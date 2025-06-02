import json
import os

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG = {
    "jira_url": "",
    "client_id": "",
    "redirect_uri": "http://localhost:5000/callback"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, 'r') as f:
            data = f.read().strip()
            if not data:
                save_config(DEFAULT_CONFIG)
                return DEFAULT_CONFIG
            return json.loads(data)
    except (json.JSONDecodeError, IOError):
        print("Warning: config file was invalid, resetting to defaults.")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def update_config(**kwargs):
    config = load_config()
    config.update(kwargs)
    save_config(config)
