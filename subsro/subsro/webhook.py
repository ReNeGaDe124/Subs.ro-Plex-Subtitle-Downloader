import json
import os
from flask import Flask, request
import threading
import logging

try:
    from waitress import serve
except ImportError:
    serve = None

def start_webhook(single_handler, download_handler, cleanup_handler, download_latest_handler, search_download_handler, search_delete_handler):
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app = Flask(__name__)

    @app.before_request
    def check_auth():
        protected_endpoints = [
            "download_call",
            "cleanup_call",
            "download_latest_call",
            "search_download_call",
            "search_delete_call"
        ]

        if request.endpoint in protected_endpoints:
            secret = os.getenv("WEBHOOK_SECRET")
            
            if secret:
                token_primit = request.headers.get("X-Auth-Token")
                
                if not token_primit or token_primit != secret:
                    print(f"SECURITY: Acces neautorizat blocat de la {request.remote_addr}")
                    return {"error": "Unauthorized"}, 401

    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "online"}, 200

    @app.route("/plex", methods=["POST"])
    def plex_webhook():
        payload = request.form.get("payload")
        if not payload:
            try:
                payload = request.data.decode("utf-8")
                data = json.loads(payload)
            except:
                return "No payload found", 400
        else:
            data = json.loads(payload)
            
        event = data.get("event")
        if event == "library.new":
            rating_key = data.get("Metadata", {}).get("ratingKey")
            if rating_key:
                print(f"WEBHOOK: Element nou detectat în Plex.")
                threading.Thread(target=single_handler, args=(rating_key,)).start()
        
        return "OK", 200

    @app.route("/download_missing_subtitles", methods=["POST"])
    def download_call():
        print("API: Apel manual 'Descărcare subtitrări lipsă'.")
        threading.Thread(target=download_handler).start()
        return {"status": "Descărcare subtitrări lipsă pornită"}, 200

    @app.route("/cleanup_orphaned_subtitles", methods=["POST"])
    def cleanup_call():
        print("API: Apel manual 'Curățare subtitrări orfane'.")
        threading.Thread(target=cleanup_handler).start()
        return {"status": "Curățare subtitrări orfane pornită"}, 200

    @app.route("/download_subtitle_for_latest_video", methods=["POST"])
    def download_latest_call():
        print("API: Apel manual 'Descărcare subtitrare pentru cel mai recent video'.")
        threading.Thread(target=download_latest_handler).start()
        return {"status": "Descărcare subtitrare pentru cel mai recent video pornită"}, 200

    @app.route("/search_and_download_subtitles", methods=["POST"])
    def search_download_call():
        data = request.get_json(silent=True) or request.form
        keywords = data.get("keywords")
        
        if not keywords:
            return {"error": "Missing 'keywords' parameter"}, 400

        print(f"API: Apel manual 'Caută și descarcă subtitrari' pentru: {keywords}")
        threading.Thread(target=search_download_handler, args=(keywords,)).start()
        return {"status": f"Căutare și descărcare subtitrări pornită pentru '{keywords}'"}, 200

    @app.route("/search_and_delete_subtitles", methods=["POST"])
    def search_delete_call():
        data = request.get_json(silent=True) or request.form
        keywords = data.get("keywords")
        
        if not keywords:
            return {"error": "Missing 'keywords' parameter"}, 400

        print(f"API: Apel manual 'Caută și șterge subtitrari' pentru: {keywords}")
        threading.Thread(target=search_delete_handler, args=(keywords,)).start()
        return {"status": f"Căutare și ștergere subtitrări pornită pentru '{keywords}'"}, 200

    if serve:
        print("Portul de conectare 8999 este activ.")
        serve(app, host='0.0.0.0', port=8999)
    else:
        print("Portul de conectare 8999 este activ.")
        app.run(host='0.0.0.0', port=8999)