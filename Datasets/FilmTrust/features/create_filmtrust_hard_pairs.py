import pandas as pd
import random
from collections import defaultdict

random.seed(42)

TRUST_FILE = "data/trust.txt"
OUTPUT_FILE = "FilmTrust_hard_pairs.csv"


# --------------------------------------------------
# 1. Read trust.txt
# --------------------------------------------------

trust = pd.read_csv(
    TRUST_FILE,
    sep=r"\s+",
    header=None,
    names=["Source", "Target", "Trust"]
)

# Remove self-loops and duplicate edges
trust = trust[trust["Source"] != trust["Target"]]
trust = trust.drop_duplicates(subset=["Source", "Target"])

print("Trust edges:", len(trust))


# --------------------------------------------------
# 2. Store all existing directed trust edges
# --------------------------------------------------

trust_edges = set(
    zip(trust["Source"], trust["Target"])
)


# --------------------------------------------------
# 3. Build an undirected neighborhood
#
# If A trusts B, we treat A and B as neighbors here.
# This is only being used to find nearby candidate pairs.
# --------------------------------------------------

neighbors = defaultdict(set)

for row in trust.itertuples(index=False):

    source = row.Source
    target = row.Target

    neighbors[source].add(target)
    neighbors[target].add(source)


# --------------------------------------------------
# 4. Find hard non-edges
#
# A-X-B
#
# A and B share X, but A -> B is NOT a trust edge.
# --------------------------------------------------

hard_candidates = set()

for source in neighbors:

    # Look at Source's neighbors
    for middle in neighbors[source]:

        # Look at the neighbors of that neighbor
        for target in neighbors[middle]:

            if source == target:
                continue

            # We only want pairs where Source -> Target
            # is NOT an observed trust edge
            if (source, target) in trust_edges:
                continue

            hard_candidates.add((source, target))


print("Possible hard non-edges:", len(hard_candidates))


# --------------------------------------------------
# 5. Sample the same number as trust edges
# --------------------------------------------------

number_needed = len(trust)

if len(hard_candidates) < number_needed:
    raise ValueError(
        "Not enough hard non-edge candidates."
    )

hard_candidates = list(hard_candidates)

sampled_hard = random.sample(
    hard_candidates,
    number_needed
)


# --------------------------------------------------
# 6. Create positive examples
# --------------------------------------------------

positive = trust[
    ["Source", "Target"]
].copy()

positive["Trust"] = 1


# --------------------------------------------------
# 7. Create hard negative examples
# --------------------------------------------------

negative = pd.DataFrame(
    sampled_hard,
    columns=["Source", "Target"]
)

# 0 = no observed Source -> Target trust edge
negative["Trust"] = 0


# --------------------------------------------------
# 8. Combine them
# --------------------------------------------------

pairs = pd.concat(
    [positive, negative],
    ignore_index=True
)

pairs = pairs.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# --------------------------------------------------
# 9. Save
# --------------------------------------------------

pairs.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("Done!")
print("Observed trust pairs:", len(positive))
print("Hard non-edge pairs:", len(negative))
print("Total pairs:", len(pairs))

print()
print(pairs.head(10))