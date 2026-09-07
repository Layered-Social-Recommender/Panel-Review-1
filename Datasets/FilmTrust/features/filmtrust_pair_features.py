import pandas as pd
import math
from collections import defaultdict

TRUST_FILE = "data/trust.txt"
PAIRS_FILE = "FilmTrust_pairs.csv"
OUTPUT_FILE = "FilmTrust_pair_features.csv"


# -------------------------------------------------
# 1. Read trust network
# -------------------------------------------------

trust = pd.read_csv(
    TRUST_FILE,
    sep=r"\s+",
    header=None,
    names=["Source", "Target", "TrustValue"]
)

trust = trust[trust["Source"] != trust["Target"]]
trust = trust.drop_duplicates(subset=["Source", "Target"])


# -------------------------------------------------
# 2. Build neighborhoods
#
# We use an undirected version of the trust network
# for Common Neighbors, Jaccard, etc.
# -------------------------------------------------

neighbors = defaultdict(set)

for row in trust.itertuples(index=False):

    source = row.Source
    target = row.Target

    neighbors[source].add(target)
    neighbors[target].add(source)


# -------------------------------------------------
# 3. Read pairs
# -------------------------------------------------

pairs = pd.read_csv(PAIRS_FILE)

results = []


# -------------------------------------------------
# 4. Calculate pair features
# -------------------------------------------------

for row in pairs.itertuples(index=False):

    source = row.Source
    target = row.Target
    label = row.Trust

    source_neighbors = set(neighbors[source])
    target_neighbors = set(neighbors[target])

    # Remove the direct Source-Target connection
    # while calculating the features.
    source_neighbors.discard(target)
    target_neighbors.discard(source)


    # -------------------------------------------------
    # Common Neighbors
    # -------------------------------------------------

    common = source_neighbors & target_neighbors

    common_neighbors = len(common)


    # -------------------------------------------------
    # Jaccard
    # -------------------------------------------------

    union = source_neighbors | target_neighbors

    if len(union) > 0:
        jaccard = len(common) / len(union)
    else:
        jaccard = 0


    # -------------------------------------------------
    # Preferential Attachment
    # -------------------------------------------------

    preferential_attachment = (
        len(source_neighbors) *
        len(target_neighbors)
    )


    # -------------------------------------------------
    # Adamic-Adar
    # -------------------------------------------------

    adamic_adar = 0

    for common_user in common:

        degree = len(neighbors[common_user])

        if degree > 1:
            adamic_adar += 1 / math.log(degree)


    # -------------------------------------------------
    # Save result
    # -------------------------------------------------

    results.append([
        source,
        target,
        label,
        common_neighbors,
        jaccard,
        preferential_attachment,
        adamic_adar
    ])


# -------------------------------------------------
# 5. Create dataframe
# -------------------------------------------------

result_df = pd.DataFrame(
    results,
    columns=[
        "Source",
        "Target",
        "Trust",
        "Common_Neighbors",
        "Jaccard",
        "Preferential_Attachment",
        "Adamic_Adar"
    ]
)


# -------------------------------------------------
# 6. Save CSV
# -------------------------------------------------

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# -------------------------------------------------
# 7. Display results
# -------------------------------------------------

print("Done!")
print("Pairs processed:", len(result_df))

print()
print(result_df.head(10))

print()
print("AVERAGE FEATURES")

print(
    result_df.groupby("Trust")[
        [
            "Common_Neighbors",
            "Jaccard",
            "Preferential_Attachment",
            "Adamic_Adar"
        ]
    ].mean()
)