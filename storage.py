import json
import os
from models import Bin, CollectionRequest

DATA_DIR = "data"
BINS_FILE = os.path.join(DATA_DIR, "bins.json")
REQUESTS_FILE = os.path.join(DATA_DIR, "requests.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_bins():
    _ensure_data_dir()
    if not os.path.exists(BINS_FILE):
        return []
    with open(BINS_FILE, "r") as f:
        data = json.load(f)
        return [Bin.from_dict(item) for item in data]

def save_bins(bins):
    _ensure_data_dir()
    with open(BINS_FILE, "w") as f:
        json.dump([b.to_dict() for b in bins], f, indent=2)

def load_requests():
    _ensure_data_dir()
    if not os.path.exists(REQUESTS_FILE):
        return []
    with open(REQUESTS_FILE, "r") as f:
        data = json.load(f)
        return [CollectionRequest.from_dict(item) for item in data]

def save_requests(requests):
    _ensure_data_dir()
    with open(REQUESTS_FILE, "w") as f:
        json.dump([r.to_dict() for r in requests], f, indent=2)

def load_history():
    _ensure_data_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    _ensure_data_dir()
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

FACILITIES_FILE = os.path.join(DATA_DIR, "facilities.json")

def load_facilities():
    _ensure_data_dir()
    if not os.path.exists(FACILITIES_FILE):
        return []
    with open(FACILITIES_FILE, "r") as f:
        data = json.load(f)
        # Import inside function to avoid circular imports if any, though top level is fine usually
        from models.facility import Facility
        return [Facility.from_dict(item) for item in data]

def save_facilities(facilities):
    _ensure_data_dir()
    with open(FACILITIES_FILE, "w") as f:
        json.dump([f.to_dict() for f in facilities], f, indent=2)
