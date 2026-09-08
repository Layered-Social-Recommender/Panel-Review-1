import pandas as pd

users = pd.read_csv("mastodon_users_1000.csv", dtype=str)
edges = pd.read_csv("mastodon_edges_1000.csv", dtype=str)

target_ids = set(users["id"])

# Users that appear in at least one edge
connected_ids = set(edges["source_id"]) | set(edges["target_id"])

# Target users with/without relationships
connected_targets = target_ids & connected_ids
isolated_targets = target_ids - connected_ids

print("Total target users:", len(target_ids))
print("Target users with relationships:", len(connected_targets))
print("Target users with NO relationships:", len(isolated_targets))

print("\nCoverage:")
print(
    round(len(connected_targets) / len(target_ids) * 100, 2),
    "%"
)

print("\nFirst 20 users with no relationships:")
for user_id in list(isolated_targets)[:20]:
    print(user_id)