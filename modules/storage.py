# modules/storage.py
import os
import json
from typing import List, Dict

DATA_DIR = "data"
CHAT_FILE = os.path.join(DATA_DIR, "chat_history.json")
LOG_FILE = os.path.join(DATA_DIR, "logs.json")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "w", encoding="utf8") as f:
            json.dump([], f)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf8") as f:
            json.dump([], f)

def read_chat() -> List[Dict]:
    ensure_data_dir()
    with open(CHAT_FILE, "r", encoding="utf8") as f:
        return json.load(f)

def append_chat(entry: Dict):
    logs = read_chat()
    logs.append(entry)
    with open(CHAT_FILE, "w", encoding="utf8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def read_logs() -> List[Dict]:
    ensure_data_dir()
    with open(LOG_FILE, "r", encoding="utf8") as f:
        return json.load(f)

def append_log(entry: Dict):
    logs = read_logs()
    logs.append(entry)
    with open(LOG_FILE, "w", encoding="utf8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
