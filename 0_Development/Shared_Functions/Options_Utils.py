import os
import json

def load_secrets():
    secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.json')
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(f"Secrets file not found at {secrets_path}")

    with open(secrets_path, 'r') as f:
        return json.load(f)

