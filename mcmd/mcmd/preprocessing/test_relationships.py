import os
import requests
from dotenv import load_dotenv

# To prove we can successfully retrieve the follower/following relationships needed to construct the Mastodon social graph.
load_dotenv()

ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# One of the users we discovered
user_id = "109333656193118788"   # seanbala

# Test followers endpoint
followers_url = f"https://mastodon.social/api/v1/accounts/{user_id}/followers"

response = requests.get(
    followers_url,
    headers=headers,
    params={"limit": 5}
)

print("FOLLOWERS")
print("Status code:", response.status_code)

if response.status_code == 200:

    followers = response.json()

    print("Number returned:", len(followers))

    for user in followers:
        print(
            user["id"],
            "|",
            user["username"]
        )

else:
    print(response.text)


# Test following endpoint
following_url = f"https://mastodon.social/api/v1/accounts/{user_id}/following"

response = requests.get(
    following_url,
    headers=headers,
    params={"limit": 5}
)

print("\nFOLLOWING")
print("Status code:", response.status_code)

if response.status_code == 200:

    following = response.json()

    print("Number returned:", len(following))

    for user in following:
        print(
            user["id"],
            "|",
            user["username"]
        )

else:
    print(response.text)