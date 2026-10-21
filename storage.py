"""Simple persistent JSON storage for saved cities and activity notes."""
import json
import os
import threading

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "planner.json")
_lock = threading.Lock()
DEFAULT_DATA = {"saved_cities": [], "notes": []}


def load_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    with _lock:
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Stored data must be an object")
            return {
                "saved_cities": data.get("saved_cities", []) if isinstance(data.get("saved_cities", []), list) else [],
                "notes": data.get("notes", []) if isinstance(data.get("notes", []), list) else []
            }
        except FileNotFoundError:
            return {"saved_cities": [], "notes": []}
        except (json.JSONDecodeError, OSError, ValueError):
            # Avoid crashing the web app if the data file is damaged.
            return {"saved_cities": [], "notes": []}


def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    safe_data = {
        "saved_cities": data.get("saved_cities", [])[:100],
        "notes": data.get("notes", [])[:100]
    }
    temp_file = DATA_FILE + ".tmp"
    with _lock:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(safe_data, file, ensure_ascii=False, indent=2)
        os.replace(temp_file, DATA_FILE)
