import os
import requests
import datetime
import threading
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Reporter:
    def __init__(self):
        self.candidates = [
            "http://homeassistant.local:8123",
            "https://homeassistant.local:8123"
        ]
        self.webhook_path = "/api/webhook/subsro_sync_webhook"
        self.secret = os.getenv("WEBHOOK_SECRET")
        
        self.current_activity = "Booting"
        self.current_item = "-"
        self.current_action = "Booting"
        self.current_result = "-"
        
        self.log_buffer = []
        
        self.lock = threading.Lock()
        self.working_url = None
        
        self.last_send_time = 0
        self.min_interval = 2.0 
        
        self.debug_enabled = os.getenv("DEBUG_LOG", "false").lower() == "true"

    def log(self, message):
        if "[DEBUG" in message and not self.debug_enabled:
            return
        
        print(message)
        should_send = False
        with self.lock:
            ts = datetime.datetime.now().strftime('%H:%M:%S')
            self.log_buffer.append(f"[{ts}] {message}")
            if len(self.log_buffer) > 50:
                self.log_buffer.pop(0)
            
            now = time.time()
            if now - self.last_send_time > self.min_interval:
                should_send = True
                self.last_send_time = now

        if should_send:
            self._trigger_send()

    def set_item(self, item_name):
        with self.lock:
            self.current_item = item_name

    def set_action(self, action_name):
        with self.lock:
            self.current_action = action_name
        self._trigger_send()

    def set_result(self, result_status):
        with self.lock:
            self.current_result = result_status

    def clear_log(self):
        with self.lock:
            self.log_buffer.clear()
            self.last_send_time = time.time()
            
        self._trigger_send()

    def report(self, activity, item=None, force=True):
        with self.lock:
            self.current_activity = activity
            if item:
                self.current_item = item
            if force:
                self.last_send_time = time.time()

        self._trigger_send()

    def _trigger_send(self):
        if not self.secret:
            return

        with self.lock:
            payload = {
                "secret": self.secret,
                "activity": self.current_activity,
                "item": self.current_item,
                "action": self.current_action,
                "result": self.current_result,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "log": "\n".join(self.log_buffer)
            }

        threading.Thread(target=self._send_request, args=(payload,), daemon=True).start()

    def _send_request(self, payload):
        if self.working_url:
            if self._try_post(self.working_url, payload): return
            self.working_url = None

        for base_url in self.candidates:
            if self._try_post(base_url, payload):
                self.working_url = base_url
                return
        
    def _try_post(self, base_url, payload):
        try:
            r = requests.post(f"{base_url}{self.webhook_path}", json=payload, timeout=5, verify=False)
            r.raise_for_status()
            return True
        except:
            return False