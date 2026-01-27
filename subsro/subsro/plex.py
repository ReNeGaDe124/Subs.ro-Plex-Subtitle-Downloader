import os

def get_media_file(item):
    try: return item.media[0].parts[0].file
    except: return None

def get_all_media_files(item):
    files = []
    try:
        if not hasattr(item, 'media'):
            return files
        
        for media in item.media:
            for part in media.parts:
                if part.file:
                    files.append(part.file)
    except Exception:
        pass
    return files

def get_ids(item):
    target = item
    if item.type == 'episode':
        try:
            show = item.show() 
            if show: target = show
        except Exception: pass

    guids = getattr(target, 'guids', [])
    if not guids:
        guid = getattr(target, 'guid', "")
        if "imdb://" in guid: return ("imdbid", guid.split("/")[-1].replace("tt", ""))
        if "tmdb://" in guid: return ("tmdbid", guid.split("/")[-1])
        return (None, None)

    for g in guids:
        if "imdb://" in g.id: return ("imdbid", g.id.split("/")[-1].replace("tt", ""))
        if "tmdb://" in g.id: return ("tmdbid", g.id.split("/")[-1])
        
    return (None, None)

def subtitle_path(media_file):
    return os.path.splitext(media_file)[0] + ".ro.srt"