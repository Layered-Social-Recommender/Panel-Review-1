import csv

INPUT_FILE = "higgs-activity_time.txt"

# Number of interactions to read
LIMIT = 100000      # Change this later if needed

nodes = set()
edges = []

count = 0

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:

        if count >= LIMIT:
            break

        parts = line.strip().split()

        if len(parts) != 4:
            continue

        source = parts[0]
        target = parts[1]
        timestamp = parts[2]
        interaction = parts[3]

        nodes.add(source)
        nodes.add(target)

        edges.append([
            source,
            target,
            "Directed",
            1,
            interaction,
            timestamp
        ])

        count += 1


# -----------------------------
# Write Nodes.csv
# -----------------------------

with open("nodes.csv", "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow(["Id", "Label"])

    for node in sorted(nodes):
        writer.writerow([node, node])


# -----------------------------
# Write Edges.csv
# -----------------------------

with open("edges.csv", "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Source",
        "Target",
        "Type",
        "Weight",
        "Interaction",
        "Timestamp"
    ])

    writer.writerows(edges)


print("Done!")
print("Nodes :", len(nodes))
print("Edges :", len(edges))