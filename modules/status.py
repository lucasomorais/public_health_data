import json
import os
from datetime import datetime

STATUS_FILE = "_tabnet_info/status.json"

DEFAULT_SCRIPTS = [
    "casos_dengue_municipio",
]

def load_status_log():
    if not os.path.exists(STATUS_FILE):
        return []
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_status_log(log_data):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

def append_status_entry(changed_years):
    timestamp = datetime.now().isoformat()
    changed = bool(changed_years)

    entry = {
        "timestamp": timestamp,
        "changed": changed,
        "changed_years": changed_years,
        "scripts": {key: changed for key in DEFAULT_SCRIPTS}
    }

    log = load_status_log()
    log.append(entry)
    save_status_log(log)

def get_latest_status():
    log = load_status_log()
    if log:
        return log[-1]
    return None
