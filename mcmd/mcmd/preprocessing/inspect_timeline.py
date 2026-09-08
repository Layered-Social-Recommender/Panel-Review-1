import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")

url = "https://mastodon.social/api/v1/timelines/tag/technology"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

params = {
    "limit": 1
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:

    statuses = response.json()

    if len(statuses) == 0:
        print("No statuses returned.")
    else:
        status = statuses[0]
        account = status["account"]

        print("\n===== STATUS FIELDS =====")
        print(list(status.keys()))

        print("\n===== ACCOUNT FIELDS =====")
        print(list(account.keys()))

        print("\n===== ACCOUNT INFORMATION =====")
        print("Username:", account["username"])
        print("Followers:", account["followers_count"])
        print("Following:", account["following_count"])
        print("Total statuses:", account["statuses_count"])
        print("Account created:", account["created_at"])

        print("\n===== STATUS INFORMATION =====")
        print("Created:", status["created_at"])
        print("Replies:", status["replies_count"])
        print("Boosts:", status["reblogs_count"])
        print("Favourites:", status["favourites_count"])
        print("Visibility:", status["visibility"])
        print("Language:", status["language"])
        print("Reply to:", status["in_reply_to_id"])

else:
    print("Request failed")
    print("Status code:", response.status_code)
    print(response.text)