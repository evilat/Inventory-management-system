import os
import json

def load_config():
    CONFIG_PATH = os.path.join('userdata', 'config.json')
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}