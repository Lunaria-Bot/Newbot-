import os
import json

DATA_FILE = "data/botdata.json"


def load_data():
    """Load JSON data from file or return defaults."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"cooldowns": {}, "settings": {}}


def save_data(data):
    """Save JSON data to file."""
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
