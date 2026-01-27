import os
import tempfile
import shutil
import subprocess
import re
import charset_normalizer

SOURCE_TAGS = [
    'bluray', 'blu-ray', 'bdrip', 'brrip', 
    'web-dl', 'webdl', 'webrip', 'web', 
    'hdtv', 'tvrip', 
    'dvdrip', 'dvd', 'remux'
]

def extract_tags(text):
    found = set()
    if not text: return found
    text = text.lower()
    for tag in SOURCE_TAGS:
        if tag in text:
            if 'web' in tag: found.add('web')
            elif 'bluray' in tag or 'bdrip' in tag: found.add('bluray')
            else: found.add(tag)
    return found

def ensure_utf8(file_path):
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(4096)

        if not chunk:
            return 'error'

        if chunk.startswith(b'\xef\xbb\xbf'):
            return 'already_utf8'

        try:
            chunk.decode("utf-8")
            return 'already_utf8'
        except UnicodeDecodeError as e:
            if e.start >= len(chunk) - 4:
                return 'already_utf8'
            
            pass
        
        with open(file_path, "rb") as f:
            full_data = f.read()

        results = charset_normalizer.from_bytes(full_data)
        best_match = results.best()
        
        if not best_match:
            return 'error'
            
        content = str(best_match)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return 'converted'

    except Exception:
        return 'error'

def extract_srt(archive_bytes, target_path, target_season=None, target_episode=None, video_filename=None):
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = os.path.join(tmp_dir, "subs.rar")
        with open(archive_path, "wb") as f:
            f.write(archive_bytes)
        
        try:
            subprocess.run(["7z", "x", archive_path, f"-o{tmp_dir}", "-y"], check=True, capture_output=True)
            
            all_srt_files = []
            for root, _, files in os.walk(tmp_dir):
                if "__MACOSX" in root: continue
                for file in files:
                    if file.lower().endswith(".srt"):
                        all_srt_files.append(os.path.join(root, file))
            
            if not all_srt_files: return False

            chosen_srt = None
            
            if target_season is not None and target_episode is not None:
                for srt_path in all_srt_files:
                    srt_name = os.path.basename(srt_path).upper()
                    
                    s_match = re.search(r'(?i)S(\d+).{0,6}E(\d+)|(\d+)X(\d+)', srt_name)
                    
                    found_s, found_e = None, None
                    if s_match:
                        found_s = int(s_match.group(1) or s_match.group(3))
                        found_e = int(s_match.group(2) or s_match.group(4))
                    else:
                        e_only_match = re.search(r'(?i)[^a-z]E(\d+)[^a-z]', srt_name)
                        if e_only_match:
                            found_s = target_season 
                            found_e = int(e_only_match.group(1))

                    if found_s == target_season and found_e == target_episode:
                        chosen_srt = srt_path
                        break
                
                if chosen_srt is None:
                    return False
                    
            else:
                if video_filename:
                    video_tags = extract_tags(video_filename)
                    
                    def get_score(srt_path):
                        srt_name = os.path.basename(srt_path)
                        srt_tags = extract_tags(srt_name)
                        
                        common_count = len(video_tags.intersection(srt_tags))
                        
                        return (common_count, os.path.getsize(srt_path))
                    
                    all_srt_files.sort(key=get_score, reverse=True)
                    chosen_srt = all_srt_files[0]
                else:
                    all_srt_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
                    chosen_srt = all_srt_files[0]

            if chosen_srt:
                ensure_utf8(chosen_srt)
                
                if os.path.exists(target_path):
                    try: os.remove(target_path)
                    except: pass
                
                shutil.copyfile(chosen_srt, target_path)

                try:
                    subprocess.run(["touch", target_path], check=False)
                except:
                    try:
                        os.utime(target_path, None)
                    except:
                        pass

                return True
            
            return False

        except Exception:
            return False