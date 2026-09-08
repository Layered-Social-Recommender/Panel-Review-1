import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")

url = "https://mastodon.social/api/v1/accounts/verify_credentials"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    user = response.json()
    print("Connection successful!")
    print("Username:", user["username"])
    print("Display name:", user["display_name"])
else:
    print("Connection failed")
    print("Status code:", response.status_code)
    print(response.text)