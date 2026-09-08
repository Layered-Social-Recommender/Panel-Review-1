import os
import csv
import requests
import time
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

BASE_URL = "https://mastodon.social/api/v1/accounts"

USER_FILE = "mastodon_users_1000.csv"
EDGE_FILE = "mastodon_edges_1000.csv"
PROGRESS_FILE = "relationship_progress.txt"

# --------------------------------------------------
# LOAD USERS
# --------------------------------------------------

users = []

with open(USER_FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        users.append(row["id"])

print("Users loaded:", len(users))


# --------------------------------------------------
# LOAD EXISTING EDGES
# --------------------------------------------------

edges = []

if os.path.exists(EDGE_FILE):

    with open(EDGE_FILE, "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:
            edges.append(row)

    print("Existing edges loaded:", len(edges))

else:

    print("No previous edge file found.")


# --------------------------------------------------
# LOAD PROGRESS
# --------------------------------------------------

start_index = 0

if os.path.exists(PROGRESS_FILE):

    with open(PROGRESS_FILE, "r") as file:
        start_index = int(file.read().strip())

    print("Resuming from user:", start_index + 1)


# --------------------------------------------------
# REQUEST FUNCTION WITH RETRIES
# --------------------------------------------------

def get_relationships(url):

    for attempt in range(5):

        try:

            response = requests.get(
                url,
                headers=headers,
                params={"limit": 80},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()

            elif response.status_code == 429:

                print("Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)

            else:

                print(
                    "HTTP error:",
                    response.status_code
                )

                time.sleep(10)

        except requests.exceptions.RequestException as e:

            print(
                f"Connection error "
                f"(attempt {attempt + 1}/5):",
                e
            )

            time.sleep(15)

    return None


# --------------------------------------------------
# PROCESS USERS
# --------------------------------------------------

for index in range(start_index, len(users)):

    user_id = users[index]

    print(
        f"\n[{index + 1}/{len(users)}] "
        f"Processing user {user_id}"
    )


    # --------------------------------------------------
    # FOLLOWING
    # --------------------------------------------------

    url = f"{BASE_URL}/{user_id}/following"

    following = get_relationships(url)

    if following is not None:

        for account in following:

            edges.append({
                "source_id": user_id,
                "target_id": account["id"],
                "relationship": "following"
            })

        print(
            "  Following retrieved:",
            len(following)
        )

    else:

        print("  Could not retrieve following.")


    time.sleep(1)


    # --------------------------------------------------
    # FOLLOWERS
    # --------------------------------------------------

    url = f"{BASE_URL}/{user_id}/followers"

    followers = get_relationships(url)

    if followers is not None:

        for account in followers:

            edges.append({
                "source_id": account["id"],
                "target_id": user_id,
                "relationship": "following"
            })

        print(
            "  Followers retrieved:",
            len(followers)
        )

    else:

        print("  Could not retrieve followers.")


    # --------------------------------------------------
    # SAVE AFTER EVERY USER
    # --------------------------------------------------

    unique_edges = {}

    for edge in edges:

        key = (
            edge["source_id"],
            edge["target_id"]
        )

        unique_edges[key] = edge


    with open(
        EDGE_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source_id",
                "target_id",
                "relationship"
            ]
        )

        writer.writeheader()

        writer.writerows(unique_edges.values())


    # Save progress
    with open(PROGRESS_FILE, "w") as file:
        file.write(str(index + 1))


    print(
        "  Saved edges:",
        len(unique_edges)
    )


    # Small delay
    time.sleep(1)


# --------------------------------------------------
# COMPLETE
# --------------------------------------------------

print("\n==============================")
print("RELATIONSHIP COLLECTION DONE")
print("==============================")

print(
    "Total unique edges:",
    len(unique_edges)
)

print(
    "Saved as:",
    EDGE_FILE
)