import requests
import base64
import os
import json

def load_secrets():
    # Get absolute path to the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up two levels to reach zero_fulfillment/
    secrets_path = os.path.join(current_dir, '..', '..', 'secrets.json')
    secrets_path = os.path.abspath(secrets_path)  # resolve to full path

    with open(secrets_path, 'r') as f:
        secrets = json.load(f)

    return secrets

# Load the secrets
secrets = load_secrets()

APP_KEY = secrets["SCHWAB_APP_KEY"]
APP_SECRRET = secrets["SCHWAB_APP_SECRET"]


auth_url = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={APP_KEY}&redirect_uri=https://127.0.0.1'

print(f"Click to authenticate: {auth_url}")

returned_link = input("Parse the redirect URL here: ")

code =  f"{returned_link[returned_link.index('code=')+5:returned_link.index('%40')]}@"

headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{APP_KEY}:{APP_SECRRET}", "utf-8")).decode("utf-8")}', 'Content-Type': 'application/x-www-form-urlencoded'}

data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': 'https://127.0.0.1'}

response = requests.post(url= 'https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)

tD = response.json()
access_token = tD['access_token']
refresh_token = tD['refresh_token']

base_url = "https://api.schwabapi.com/trader/v1"

response =  requests.get(f'{base_url}/accounts/accountNumbers', headers={'Authorization': f'Bearer {access_token}'})
print(response.json())