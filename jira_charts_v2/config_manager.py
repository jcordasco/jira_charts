import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULT_MAPPING_FALLBACK = "field_mappings.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_default_mapping():
    config = load_config()
    return config.get("default_field_mapping", DEFAULT_MAPPING_FALLBACK)

def set_default_mapping(file):
    config = load_config()
    if file == "default":
        config.pop("default_field_mapping", None)
    else:
        config["default_field_mapping"] = file
    save_config(config)
