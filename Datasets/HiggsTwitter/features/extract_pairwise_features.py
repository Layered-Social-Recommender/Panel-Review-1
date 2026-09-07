import csv
import math
from collections import defaultdict

EDGE_FILE = "edges.csv"
BEHAVIOR_FILE = "Twitter_behavioral_features.csv"
NODE_FILE = "Twitter_node_features.csv"
OUTPUT_FILE = "Twitter_pairwise_features.csv"


# --------------------------------------------------
# 1. Build user neighborhoods from edges.csv
# --------------------------------------------------

neighbors = defaultdict(set)

with open(EDGE_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        source = row["Source"]
        target = row["Target"]

        if source == target:
            continue

        # For neighborhood similarity, treat connection as adjacency
        neighbors[source].add(target)
        neighbors[target].add(source)


# --------------------------------------------------
# 2. Read modularity/community information
# --------------------------------------------------

community = {}

with open(NODE_FILE, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:
        node = row["Id"]
        community[node] = row["modularity_class"]


# --------------------------------------------------
# 3. Calculate pairwise features
# --------------------------------------------------

output_rows = []

with open(BEHAVIOR_FILE, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:

        source = row["Source"]
        target = row["Target"]

        if source == target:
            continue

        source_neighbors = neighbors[source]
        target_neighbors = neighbors[target]

        # ---------- Common Neighbors ----------

        common = source_neighbors.intersection(target_neighbors)
        common_neighbors = len(common)

        # ---------- Jaccard Coefficient ----------

        union = source_neighbors.union(target_neighbors)

        if len(union) > 0:
            jaccard = common_neighbors / len(union)
        else:
            jaccard = 0

        # ---------- Preferential Attachment ----------

        source_degree = len(source_neighbors)
        target_degree = len(target_neighbors)

        preferential_attachment = source_degree * target_degree

        # ---------- Adamic-Adar ----------

        adamic_adar = 0

        for common_node in common:

            degree = len(neighbors[common_node])

            if degree > 1:
                adamic_adar += 1 / math.log(degree)

        # ---------- Same Community ----------

        source_community = community.get(source)
        target_community = community.get(target)

        if (
            source_community is not None
            and target_community is not None
            and source_community == target_community
        ):
            same_community = 1
        else:
            same_community = 0

        output_rows.append([
            source,
            target,
            common_neighbors,
            jaccard,
            preferential_attachment,
            adamic_adar,
            same_community
        ])


# --------------------------------------------------
# 4. Save
# --------------------------------------------------

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Source",
        "Target",
        "Common_Neighbors",
        "Jaccard",
        "Preferential_Attachment",
        "Adamic_Adar",
        "Same_Community"
    ])

    writer.writerows(output_rows)


print("Done!")
print("Pairs processed:", len(output_rows))
print("Output:", OUTPUT_FILE)