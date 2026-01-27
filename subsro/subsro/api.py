import requests
import threading
from collections import OrderedDict
from requests.adapters import HTTPAdapter

BASE_URL = "https://subs.ro/api/v1.0"

class SubsAPI:
    def __init__(self, api_key, logger=None):
        self.headers = {"X-Subs-Api-Key": api_key}
        self.logger = logger if logger else print
        
        self.cache = OrderedDict()
        self.cache_lock = threading.Lock()
        self.cache_limit = 100
        
        self.session = requests.Session()
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
        self.session.mount('https://', adapter)

    def search(self, field, value):
        r = self.session.get(f"{BASE_URL}/search/{field}/{value}", headers=self.headers, params={"language":"ro"})
        r.raise_for_status()
        return r.json().get("items", [])

    def download(self, subtitle_id):
        with self.cache_lock:
            if subtitle_id in self.cache:
                self.logger(f"[DEBUG API] Arhiva cu subtitrări (ID {subtitle_id}) găsită în memorie. Se livrează din cache.")
                self.cache.move_to_end(subtitle_id)
                return self.cache[subtitle_id]
        
        self.logger(f"[DEBUG API] Se descarcă arhiva cu subtitrări (ID {subtitle_id})")
        r = self.session.get(f"{BASE_URL}/subtitle/{subtitle_id}/download", headers=self.headers)
        r.raise_for_status()
        content = r.content
        
        with self.cache_lock:
            self.cache[subtitle_id] = content
            if len(self.cache) > self.cache_limit:
                self.cache.popitem(last=False)
        
        self.logger(f"[DEBUG API] Descărcare reușită. Arhivă cu subtitrări salvată în cache.")
        return content
    
    def clear_cache(self):
        with self.cache_lock:
            count = len(self.cache)
            if count > 0:
                self.cache.clear()
                self.logger(f"[DEBUG API] S-au sters {count} arhive cu subtitrări din cache.")