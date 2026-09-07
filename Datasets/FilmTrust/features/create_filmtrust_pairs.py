import pandas as pd
import random

random.seed(42)

# -------------------------------------------
# 1. Read FilmTrust trust relationships
# -------------------------------------------

trust = pd.read_csv(
    "data/trust.txt",
    sep=r"\s+",
    header=None,
    names=["Source", "Target", "Trust"]
)

print("Trust edges:", len(trust))

# Remove self-loops if any
trust = trust[trust["Source"] != trust["Target"]].copy()

# Remove duplicate directed relationships
trust = trust.drop_duplicates(subset=["Source", "Target"])

print("Unique trust edges:", len(trust))


# -------------------------------------------
# 2. Positive examples
# -------------------------------------------

positive = trust[["Source", "Target"]].copy()
positive["Trust"] = 1


# -------------------------------------------
# 3. Find all users in trust network
# -------------------------------------------

users = sorted(
    set(trust["Source"]).union(set(trust["Target"]))
)

print("Users in trust network:", len(users))


# Store existing trust edges for fast lookup
trust_edges = set(
    zip(trust["Source"], trust["Target"])
)


# -------------------------------------------
# 4. Generate comparison non-edge pairs
# -------------------------------------------

negative_pairs = set()

number_needed = len(positive)

while len(negative_pairs) < number_needed:

    source = random.choice(users)
    target = random.choice(users)

    # No self-pairs
    if source == target:
        continue

    # Must NOT already be an observed trust edge
    if (source, target) in trust_edges:
        continue

    # Avoid duplicates
    if (source, target) in negative_pairs:
        continue

    negative_pairs.add((source, target))


negative = pd.DataFrame(
    list(negative_pairs),
    columns=["Source", "Target"]
)

# IMPORTANT:
# 0 means "no observed trust edge", not proven distrust.
negative["Trust"] = 0


# -------------------------------------------
# 5. Combine
# -------------------------------------------

pairs = pd.concat(
    [positive, negative],
    ignore_index=True
)

# Shuffle rows
pairs = pairs.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# -------------------------------------------
# 6. Save
# -------------------------------------------

pairs.to_csv(
    "FilmTrust_pairs.csv",
    index=False
)


print()
print("Done!")
print("Observed trust pairs:", len(positive))
print("Sampled non-edge pairs:", len(negative))
print("Total pairs:", len(pairs))

print()
print(pairs.head(10))