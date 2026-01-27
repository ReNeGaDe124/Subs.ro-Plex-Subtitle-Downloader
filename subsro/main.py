import os
import threading
import requests
from requests.adapters import HTTPAdapter
import datetime
import time
import re
from queue import Queue
from plexapi.server import PlexServer
from subsro.api import SubsAPI
from subsro.plex import get_media_file, get_all_media_files, get_ids, subtitle_path
from subsro.extract import extract_srt, ensure_utf8
from subsro.reporter import Reporter
from subsro.matcher import sort_best_match

plex_url = os.getenv("PLEX_URL")
plex_token = os.getenv("PLEX_TOKEN")

session = requests.Session()
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
session.mount('http://', adapter)
session.mount('https://', adapter)

plex = PlexServer(plex_url, plex_token, session=session)

reporter = Reporter()

subs = SubsAPI(os.getenv("SUBSRO_API_KEY"), logger=reporter.log)

process_queue = Queue()
api_lock = threading.Lock()
state_lock = threading.Lock()
active_workers = 0

def get_log_name(item):
    try:
        if item.type == 'episode':
            show_title = getattr(item, 'grandparentTitle', item.title)
            season_ep = getattr(item, 'seasonEpisode', '').upper()
            if not season_ep:
                s_idx = getattr(item, 'parentIndex', 0)
                e_idx = getattr(item, 'index', 0)
                season_ep = f"S{s_idx:02}E{e_idx:02}"
            return f"{show_title} {season_ep} - {item.title}"
        elif item.type == 'movie':
            return f"{item.title} ({item.year})"
        return item.title
    except Exception:
        return getattr(item, 'title', f"ID {getattr(item, 'ratingKey', '?')}")

def worker(worker_id):
    global active_workers
    
    while True:
        try:
            rating_key = process_queue.get()
            if rating_key is None: break
            
            with state_lock:
                active_workers += 1

            item_name = f"ID {rating_key}"
            try:
                item = plex.library.fetchItem(int(rating_key))
                item_name = get_log_name(item)
                
                reporter.set_item(item_name)
                
                if item.type in ['episode', 'movie']:
                    status = process(item, item_name)
                    if status == 'retry':
                        threading.Timer(30, lambda: process_queue.put(rating_key)).start()
                    elif status == 'rate_limited':
                        reporter.log(f"SUBS.RO API: Limită API atinsă pentru '{item_name}'.")
                        reporter.set_result("Nu (Eroare API)")
                
            except Exception as e:
                reporter.log(f"Eroare pentru {rating_key}: {e}")
                reporter.set_result("Nu (Eroare API)")
            
            finally:
                process_queue.task_done()
                
                with state_lock:
                    active_workers -= 1
                    should_go_idle = (active_workers == 0 and process_queue.empty())
                
                if should_go_idle:
                     try:
                        subs.clear_cache()
                     except Exception as e:
                        reporter.log(f"Eroare la golirea cache-ului: {e}")
                     reporter.report("Idle", item=item_name)
                     
        except Exception as e:
            reporter.log(f"Eroare critică worker loop: {e}")
            time.sleep(5)

def process(item, log_name):
    try:
        item.reload()
        
        all_files = get_all_media_files(item)
        if not all_files: return 'retry'

        files_to_process = []
        
        for f in all_files:
            srt = subtitle_path(f)
            if os.path.exists(srt):
                ensure_utf8(srt)
            else:
                files_to_process.append(f)
        
        if not files_to_process:
            reporter.set_result("Nu (subtitrarea există deja)")
            return 'skip'

        field, val = get_ids(item)
        if not field: return 'retry'
        
        with api_lock:
            time.sleep(1) 
            try:
                results = subs.search(field, val)
                
                if results:
                    reporter.log(f"[DEBUG API] Total rezultate găsite: {len(results)}:")
                    for i, res in enumerate(results[:100]):
                        r_title = res.get('title', 'Fără titlu')
                        r_desc = res.get('description', 'Fără descriere')
                        r_id = res.get('id', 'N/A')
                        reporter.log(f"[DEBUG API]  #{i+1}: {r_title} (ID:{r_id}) | Desc: {r_desc}")


            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429: return 'rate_limited'
                raise e
        
        if not results:
            reporter.log(f"SUBS.RO API: Nu există subtitrare pentru '{log_name}'")
            reporter.set_result("Nu (nu a fost gasită)")
            return 'done'
        
        video_season = None
        video_episode = None
        
        if item.type == 'episode':
            try:
                video_season = int(item.parentIndex)
                video_episode = int(item.index)
            except: 
                pass

        success_count = 0
        
        for video_file in files_to_process:
            video_filename = os.path.basename(video_file)
            srt_target = subtitle_path(video_file)
            
            reporter.log(f"[SEARCH] Se caută subtitrare pentru fișierul video: {video_filename}")
            
            try:
                sorted_results = sort_best_match(results, video_file, video_season, video_episode, log_func=reporter.log)
            except Exception as e:
                reporter.log(f"Eroare matcher pentru {video_filename}: {e}")
                sorted_results = results

            downloaded_for_this_file = False
            
            for sub in sorted_results:
                try:
                    reporter.log(f"[DEBUG API DOWNLOAD] Solicitare conținut cu ID {sub['id']} - '{sub.get('title')}'")
                    
                    with api_lock:
                        archive_bytes = subs.download(sub['id'])
                    
                    if extract_srt(archive_bytes, srt_target, video_season, video_episode, video_filename=video_filename):
                        reporter.log(f"SUBS.RO API: Subtitrare descărcată pentru fișierul video: '{video_filename}'")
                        downloaded_for_this_file = True
                        success_count += 1
                        break
                    else:
                        reporter.log(f"[DEBUG API DOWNLOAD] Arhiva cu ID {sub['id']} nu a conținut fișierul corect.")
                        continue

                except Exception as e: 
                    reporter.log(f"[DEBUG API ERROR] Eroare la descărcare/extragere: {e}")
                    continue
            
            if not downloaded_for_this_file:
                 reporter.log(f"SUBS.RO API: Nu s-a găsit subtitrare pentru '{video_filename}'")

        if success_count > 0:
            reporter.set_result("Da")
            return 'done'
        else:
            reporter.set_result("Nu (nu a fost gasită)")
            return 'done'
        
    except Exception as e:
        reporter.log(f"Eroare procesare {log_name}: {e}")
        reporter.set_result("Nu (Eroare API)")
        return 'retry'

def cleanup_orphans():
    reporter.clear_log()
    reporter.set_action("Curățare subtitrări orfane")
    reporter.report("Processing", item="-")
    reporter.set_result("-")
    reporter.log("=== [CLEANUP] PORNIRE CURĂȚARE SUBTITRĂRI ORFANE ===")
    
    try:
        plex_locations = set()
        try:
            for section in plex.library.sections():
                for location in section.locations:
                    if os.path.exists(location): plex_locations.add(location)
        except: pass

        for base_path in plex_locations:
            for root, dirs, files in os.walk(base_path, topdown=False):
                for file in files:
                    if file.endswith(".ro.srt"):
                        srt_path = os.path.join(root, file)
                        video_base = srt_path.replace(".ro.srt", "")
                        video_exists = any(os.path.exists(video_base + ext) for ext in ['.mkv', '.mp4', '.avi', '.ts', '.mov', '.m4v'])
                        if not video_exists:
                            reporter.log(f"  [CLEANUP] Ștergere subtitrare orfană -> {file}")
                            try: os.remove(srt_path)
                            except: pass
                if not os.listdir(root) and root not in plex_locations:
                    reporter.log(f"  [CLEANUP] Ștergere folder gol -> {root}")
                    try: os.rmdir(root)
                    except: pass
    except Exception as e:
        reporter.log(f"  [CLEANUP] Eroare: {e}")

    finally:
        reporter.log("=== [CLEANUP] FINALIZAT ===")
        reporter.report("Idle")

def process_single(rating_key, action_override="Descărcare automată subtitrare", clear_log=True):
    if clear_log:
        reporter.clear_log()
        
    reporter.set_action(action_override)
    reporter.report("Processing", item="Analyzing Request")
    reporter.set_result("-")
    
    try:
        item = plex.library.fetchItem(int(rating_key))
        added_count = 0
        if item.type in ['show', 'season']:
            for episode in item.episodes():
                process_queue.put(episode.ratingKey)
                added_count += 1
        elif item.type in ['episode', 'movie']:
            process_queue.put(rating_key)
            added_count += 1
        
    except Exception as e:
        reporter.log(f"Eroare identificare media ID {rating_key}: {e}")
        if process_queue.empty() and active_workers == 0:
            reporter.report("Idle", item="Error")

def download_latest():
    reporter.clear_log()
    reporter.set_action("Descărcare subtitrare pentru cel mai recent video")
    reporter.report("Processing", item="Checking Latest Video")
    reporter.set_result("-")
    reporter.log("=== [LATEST] VERIFICARE ULTIMUL VIDEO ADĂUGAT ===")
    
    try:
        all_items = []
        try:
            movies = plex.library.section("Movies").search(libtype='movie', sort="addedAt:desc", limit=1)
            if movies: all_items.append(movies[0])
        except Exception: pass

        try:
            episodes = plex.library.section("TV Shows").search(libtype='episode', sort="addedAt:desc", limit=1)
            if episodes: all_items.append(episodes[0])
        except Exception: pass

        if all_items:
            latest = sorted(all_items, key=lambda x: x.addedAt, reverse=True)[0]
            
            try:
                latest.reload()
                all_files = get_all_media_files(latest)
                missing_subs = False
                
                for media_file in all_files:
                    srt_path = subtitle_path(media_file)
                    if not os.path.exists(srt_path):
                        missing_subs = True
                        break
                
                if not missing_subs and all_files:
                    item_name = get_log_name(latest)
                    reporter.set_item(item_name)
                    reporter.set_result("Nu (subtitrarea există deja)")
                    reporter.log(f"SKIP: Toate versiunile pentru '{item_name}' au deja subtitrare.")
                    reporter.report("Idle", item=item_name)
                    return
            except Exception as e:
                reporter.log(f"[LATEST] Eroare: {e}")

            process_single(latest.ratingKey, action_override="Descărcare subtitrare pentru cel mai recent video", clear_log=False)
        else:
            reporter.report("Idle", item="Nu a fost găsit ultimul video")
            
    except Exception as e:
        reporter.log(f"[LATEST] Eroare: {e}")
        reporter.report("Idle", item="Eroare")

def download_missing():
    reporter.clear_log()
    reporter.set_action("Descărcare subtitrări lipsă")
    reporter.report("Processing", item="Scanning Library")
    reporter.set_result("-")
    reporter.log("=== [MISSING] PORNIRE DESCĂRCARE SUBTITRĂRI LIPSĂ ===")
    count = 0
    try:
        for m in plex.library.section("Movies").all():
            process_queue.put(m.ratingKey); count += 1
        
        for s in plex.library.section("TV Shows").all():
            for ep in s.episodes():
                 process_queue.put(ep.ratingKey); count += 1

        if count == 0:
            reporter.report("Idle", item="Library Scanned")
    except Exception as e:
        reporter.log(f"[MISSING] Eroare: {e}")
        reporter.report("Idle")

def search_and_download(keywords_input):
    reporter.clear_log()
    reporter.set_action("Caută și descarcă subtitrari")
    reporter.set_result("-")
    reporter.report("Processing", item=f"Search: {keywords_input}")
    
    if not keywords_input: 
        reporter.report("Idle", item="Câmpul de căutare este gol")
        return

    required_words = list(set(keywords_input.lower().split()))
    if not required_words: 
        reporter.report("Idle")
        return

    search_anchor = max(required_words, key=len)
    reporter.log(f"=== [SEARCH] CĂUTARE DUPĂ CUVINTELE: {required_words} ===")
    
    keys_to_process = []
    items_display_log = []

    try:
        results = plex.search(search_anchor)
        for item in results:
            if item.type in ['movie', 'show']:
                title_lower = item.title.lower()
                all_words_found = True
                for word in required_words:
                    pattern = r'\b' + re.escape(word) + r'\b'
                    if not re.search(pattern, title_lower):
                        all_words_found = False
                        break
                
                if all_words_found:
                    if item.type == 'show':
                        episodes = item.episodes()
                        if episodes:
                            items_display_log.append(f"{item.title} ({item.year}) - {len(episodes)} episoade")
                            for ep in episodes:
                                keys_to_process.append(ep.ratingKey)
                    else:
                        items_display_log.append(f"{item.title} ({item.year})")
                        keys_to_process.append(item.ratingKey)
                    
    except Exception as e:
        reporter.log(f"[SEARCH] Eroare: {e}")

    if items_display_log:
        reporter.log(f"=== [SEARCH] {len(items_display_log)} ELEMENTE CARE SE POTRIVESC CĂUTĂRII: ===")
        
        for name in items_display_log:
            reporter.log(f"  -> {name}")
        
        for key in keys_to_process:
            process_queue.put(key)
    else:
        reporter.log(f"=== [SEARCH] NICIUN REZULTAT PENTRU: {required_words} ===")
        reporter.report("Idle", item="Fără rezultate")

import os
import re

def search_and_delete(keywords_input):
    reporter.clear_log()
    reporter.set_action("Caută și șterge subtitrari")
    reporter.set_result("-")
    reporter.report("Processing", item=f"Search & Delete: {keywords_input}")
    
    if not keywords_input: 
        reporter.report("Idle", item="Câmpul de căutare este gol")
        return

    required_words = list(set(keywords_input.lower().split()))
    if not required_words: 
        reporter.report("Idle")
        return

    search_anchor = max(required_words, key=len)
    reporter.log(f"=== [DELETE] CĂUTARE PENTRU ȘTERGERE: {required_words} ===")
    
    items_found = []

    try:
        results = plex.search(search_anchor)
        for item in results:
            if item.type in ['movie', 'show']:
                title_lower = item.title.lower()
                all_words_found = True
                for word in required_words:
                    pattern = r'\b' + re.escape(word) + r'\b'
                    if not re.search(pattern, title_lower):
                        all_words_found = False
                        break
                
                if all_words_found:
                    if item.type == 'show':
                        for ep in item.episodes():
                            items_found.append(ep)
                    else:
                        items_found.append(item)
                    
    except Exception as e:
        reporter.log(f"[DELETE] Eroare căutare Plex: {e}")
        reporter.report("Idle", item="Eroare")
        return

    if not items_found:
        reporter.log(f"=== [DELETE] NICIUN REZULTAT PENTRU: {required_words} ===")
        reporter.report("Idle", item="Fără rezultate")
        return

    reporter.log(f"=== [DELETE] {len(items_found)} ELEMENTE CARE SE POTRIVESC CĂUTĂRII ===")
    
    deleted_count = 0
    
    for item in items_found:
        try:
            item.reload()
            all_media_files = get_all_media_files(item)
            if not all_media_files: continue
            
            item_base_name = get_log_name(item)
            
            for media_file in all_media_files:
                srt_path = subtitle_path(media_file)
                video_filename = os.path.basename(media_file)
                
                if os.path.exists(srt_path):
                    try:
                        os.remove(srt_path)
                        
                        deleted_info = f"{video_filename}"
                        
                        reporter.log(f"  [DELETE] A fost ștearsă subtitrarea pentru {deleted_info}")
                        deleted_count += 1
                    except Exception as e:
                        reporter.log(f"  [DELETE ERROR] {video_filename}: {e}")
                else:
                    pass
                
        except Exception as e:
            reporter.log(f"  [DELETE ERROR] {item}: {e}")

    reporter.log(f"=== [DELETE] OPERAȚIUNE COMPLETĂ. SUBTITRĂRI ȘTERSE: {deleted_count} ===")

    reporter.report("Idle", item=f"Subtitrari șterse: {deleted_count}")

def run_scheduled_tasks():
    reporter.log(f"=== ACTIVITATE PROGRAMATĂ ({datetime.datetime.now().strftime('%H:%M')}) ===")
    if os.getenv("SCHEDULED_CLEANUP") == "true":
        cleanup_orphans()
    if os.getenv("SCHEDULED_DOWNLOAD") == "true":
        download_missing()

def daily_scheduler():
    scan_time = os.getenv("SCAN_TIME", "03:00")
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now == scan_time:
            threading.Thread(target=run_scheduled_tasks, daemon=True).start()
            time.sleep(61)
        time.sleep(30)

if __name__ == "__main__":
    reporter.log("Addon Subs.ro Plex Subtitle Downloader pornit.")
    reporter.report("Booting")

    for i in range(10):
        threading.Thread(target=worker, args=(i+1,), daemon=True).start()
    
    from subsro.webhook import start_webhook
    webhook_process_single = lambda rk: process_single(rk, action_override="Descărcare automată subtitrare", clear_log=True)
    
    threading.Thread(target=start_webhook, args=(
        webhook_process_single, 
        download_missing,
        cleanup_orphans,
        download_latest,
        search_and_download,
        search_and_delete
    ), daemon=True).start()
    
    threading.Thread(target=daily_scheduler, daemon=True).start()
    
    reporter.report("Idle")
    
    while True:

        time.sleep(3600)