import re
import os

SOURCE_TAGS = [
    'bluray', 'blu-ray', 'bdrip', 'brrip', 
    'web-dl', 'webdl', 'webrip', 'web', 
    'hdtv', 'tvrip', 
    'dvdrip', 'dvd', 'remux'
]

def get_season_range(text):
    if not text:
        return None, None
    
    match = re.search(r'(?i)(?:sez(?:oanele|oane|onul)?|seasons?|s)\W*(\d+)\s*-\s*(\d+)', text)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))

        if start > 100 or end > 100:
            return None, None
        
        return start, end
    
    return None, None

def get_episode_number(text):
    if not text: 
        return None, None
    
    match_pair = re.search(r'(?i)(?:s|season\W?)(\d+).{0,3}(?:e|episode\W?)(\d+)', text)
    if match_pair:
        return int(match_pair.group(1)), int(match_pair.group(2))
        
    match_ro = re.search(r'(?i)sez(?:onul)?\.?\s*(\d+).*?ep(?:isodul)?\.?\s*(\d+)', text)
    if match_ro:
        return int(match_ro.group(1)), int(match_ro.group(2))
        
    return None, None

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

def calculate_score(sub, video_tags, video_season, video_episode, log_func=None):
    score = 0
    reasons = []
    
    title = sub.get('title', '')
    desc = sub.get('description', '')
    full_text = f"{title} {desc}"
    
    sub_tags = extract_tags(title) | extract_tags(desc)
    
    s_range_start, s_range_end = get_season_range(full_text)
    s_exact, e_exact = get_episode_number(full_text)
    
    if s_range_start and s_range_end:
        if video_season and (video_season >= s_range_start and video_season <= s_range_end):
            score += 100
            reasons.append(f"POTRIVIRE SEZON S{s_range_start}-{s_range_end}")
        else:
            if log_func: log_func(f"[DEBUG MATCHER]   [SKIP] Sezon greșit pentru '{title}'. Video: S{video_season}, Sub: S{s_range_start}-{s_range_end}")
            return -100

    elif s_exact and e_exact:
        if video_season == s_exact:
            if video_episode == e_exact:
                score += 100
                reasons.append(f"POTRIVIRE EPISOD E{video_episode}")
            elif video_episode < e_exact:
                score += 95
                reasons.append(f"POTRIVIRE EPISOD (Video E{video_episode} <= Sub E{e_exact})")
            else:
                if log_func: log_func(f"[DEBUG MATCHER]   [SKIP] Episod prea nou pentru '{title}'. Video: E{video_episode}, Sub: E{e_exact}")
                return -100
        else:
            if log_func: log_func(f"[DEBUG MATCHER]   [SKIP] Sezon greșit pentru '{title}'. Video: S{video_season}, Sub: S{s_exact}")
            return -100

    else:
        match_s = re.search(r'(?i)(?:sez(?:onul)?|season|s)\.?\s*(\d+)', title)
        if match_s:
            found_s = int(match_s.group(1))
            if video_season == found_s:
                score += 50
                reasons.append(f"POTRIVIRE SEZON S{found_s}")
            else:
                if log_func: log_func(f"[DEBUG MATCHER]   [SKIP] Sezon greșit pentru '{title}'. Video: S{video_season}, Sub: S{found_s}")
                return -100

    common_tags = video_tags.intersection(sub_tags)
    if common_tags:
        score += 10
        reasons.append(f"POTRIVIRE SURSA {list(common_tags)}")
    
    if "complet" in full_text.lower():
        score += 5
        reasons.append("COMPLET")

    if score > 0 and log_func:
        log_func(f"[DEBUG MATCHER]   [VALID] {sub.get('title')} - SCOR: {score} | Tag-uri: {sub_tags} | Motiv: {', '.join(reasons)}")
        
    return score

def sort_best_match(results, video_filepath, video_season, video_episode, log_func=None):
    if not video_filepath:
        return results

    try:
        filename = os.path.basename(video_filepath)
        dirname = os.path.basename(os.path.dirname(video_filepath))
        
        video_tags = extract_tags(filename) | extract_tags(dirname)
        
        if log_func:
            log_func(f"[DEBUG MATCHER] Informații detectate: Sezon {video_season}, Episod {video_episode}")
            log_func(f"[DEBUG MATCHER] Tag-uri sursă detectate: {video_tags}")
            log_func(f"[DEBUG MATCHER] Analizez {len(results)} arhive cu subtitrări...")

        scored_results = []
        for sub in results:
            score = calculate_score(sub, video_tags, video_season, video_episode, log_func)
            
            if score > -100:
                scored_results.append((score, sub))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        if log_func and scored_results:
             best = scored_results[0][1].get('title', 'Unknown')
             best_score = scored_results[0][0]
             log_func(f"[DEBUG MATCHER] Câștigător: '{best}' cu scorul {best_score}")

        return [x[1] for x in scored_results]

    except Exception as e:
        if log_func: log_func(f"[DEBUG MATCHER ERROR]: {e}")
        return results