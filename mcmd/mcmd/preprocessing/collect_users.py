import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

base_url = "https://mastodon.social/api/v1/timelines/tag/{}"

hashtags = [
    "technology",
    "science",
    "books",
    "music",
    "gaming",
    "education",
    "photography",
    "news"
]

TARGET_USERS = 1000

users = {}
total_statuses = 0


for hashtag in hashtags:

    print(f"\nCollecting #{hashtag}...")

    max_id = None
    page = 1

    while len(users) < TARGET_USERS:

        params = {
            "limit": 40
        }

        if max_id:
            params["max_id"] = max_id

        url = base_url.format(hashtag)

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            print("Error:", response.status_code)
            print(response.text)
            break

        statuses = response.json()

        if not statuses:
            print("No more statuses available.")
            break

        total_statuses += len(statuses)

        for status in statuses:

            account = status["account"]

            user_id = account["id"]

            if user_id not in users:

                users[user_id] = {
                    "id": account["id"],
                    "username": account["username"],
                    "acct": account["acct"],
                    "followers_count": account["followers_count"],
                    "following_count": account["following_count"],
                    "statuses_count": account["statuses_count"],
                    "created_at": account["created_at"],
                    "last_status_at": account["last_status_at"],
                    "bot": account["bot"]
                }

        print(
            f"  Page {page}: "
            f"{len(statuses)} statuses | "
            f"{len(users)} unique users"
        )

        # Oldest status in this page
        max_id = statuses[-1]["id"]

        page += 1

        time.sleep(1)

    if len(users) >= TARGET_USERS:
        break


print("\n==============================")
print("COLLECTION COMPLETE")
print("==============================")

print("Total statuses collected:", total_statuses)
print("Unique users collected:", len(users))

print("\nSample users:")

for user in list(users.values())[:10]:
    print(
        user["id"],
        "|",
        user["username"],
        "| followers:",
        user["followers_count"],
        "| following:",
        user["following_count"],
        "| posts:",
        user["statuses_count"],
        "| bot:",
        user["bot"]
    )

import csv

with open("mastodon_users_1000.csv", "w", newline="", encoding="utf-8") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "id",
            "username",
            "acct",
            "followers_count",
            "following_count",
            "statuses_count",
            "created_at",
            "last_status_at",
            "bot"
        ]
    )

    writer.writeheader()

    for user in users.values():
        writer.writerow(user)

print("\nSaved users to mastodon_users_1000.csv")