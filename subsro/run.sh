#!/usr/bin/env bash
export PLEX_URL=$(jq -r .plex_url /data/options.json)
export PLEX_TOKEN=$(jq -r .plex_token /data/options.json)
export SUBSRO_API_KEY=$(jq -r .subsro_api_key /data/options.json)
export WEBHOOK_SECRET=$(jq -r .webhook_secret /data/options.json)
export SCHEDULED_DOWNLOAD=$(jq -r .scheduled_download /data/options.json)
export SCHEDULED_CLEANUP=$(jq -r .scheduled_cleanup /data/options.json)
export SCAN_TIME=$(jq -r .scan_time /data/options.json)
export DEBUG_LOG=$(jq -r .debug_log /data/options.json)
export SUPERVISOR_TOKEN=$SUPERVISOR_TOKEN
export PYTHONPATH=$PYTHONPATH:/app

python3 -u /app/main.py