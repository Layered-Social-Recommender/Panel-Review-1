import csv
from collections import defaultdict

INPUT_FILE = "higgs-activity_time.txt"
OUTPUT_FILE = "Twitter_behavioral_features.csv"

# IMPORTANT:
# Keep this the same as create_gephi_files.py so that
# behavioral features correspond to the SAME graph.
LIMIT = 100000


# --------------------------------------------------
# pair_stats[(A, B)] stores interactions from A -> B
# --------------------------------------------------

pair_stats = defaultdict(lambda: {
    "RT": 0,
    "RE": 0,
    "MT": 0,
    "total": 0
})

count = 0


# --------------------------------------------------
# Read the SAME first 100,000 valid interactions
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in f:

        if count >= LIMIT:
            break

        parts = line.strip().split()

        if len(parts) != 4:
            continue

        source = parts[0]
        target = parts[1]
        # Ignore self-interactions for pairwise relationship analysis
        if source == target:
            count += 1
            continue
        timestamp = parts[2]
        interaction = parts[3]

        # Ignore unexpected interaction types
        if interaction not in {"RT", "RE", "MT"}:
            continue

        pair = (source, target)

        pair_stats[pair][interaction] += 1
        pair_stats[pair]["total"] += 1

        count += 1


# --------------------------------------------------
# Write behavioral features for each user pair
# --------------------------------------------------

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Source",
        "Target",
        "RT_Count",
        "RE_Count",
        "MT_Count",
        "Total_Interactions",
        "Reverse_Interactions",
        "Reciprocal"
    ])

    for (source, target), stats in pair_stats.items():

        # Number of interactions in the opposite direction:
        # Target -> Source
        reverse_stats = pair_stats.get((target, source))

        if reverse_stats is not None:
            reverse_interactions = reverse_stats["total"]
        else:
            reverse_interactions = 0

        # Reciprocal = 1 if interaction exists in BOTH directions
        if reverse_interactions > 0:
            reciprocal = 1
        else:
            reciprocal = 0

        writer.writerow([
            source,
            target,
            stats["RT"],
            stats["RE"],
            stats["MT"],
            stats["total"],
            reverse_interactions,
            reciprocal
        ])


print("Done!")
print("Interactions processed:", count)
print("Unique directed user pairs:", len(pair_stats))
print("Output file:", OUTPUT_FILE)