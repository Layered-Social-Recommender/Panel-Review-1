import pandas as pd

# -----------------------------
# Load data
# -----------------------------
nodes = pd.read_csv("output/nodes.csv")

rating_edges = pd.read_csv("output/rating_edges.csv")

trust_edges = pd.read_csv("output/trust_edges.csv")

# -----------------------------
# Node ID set
# -----------------------------
node_ids = set(nodes["Id"])

# -----------------------------
# Rating Graph Validation
# -----------------------------
rating_valid = (
    rating_edges["Source"].isin(node_ids)
    &
    rating_edges["Target"].isin(node_ids)
)

print("Rating Graph")

print("Total:", len(rating_edges))
print("Valid:", rating_valid.sum())
print("Invalid:", len(rating_edges)-rating_valid.sum())

print()

# -----------------------------
# Trust Graph Validation
# -----------------------------
trust_valid = (
    trust_edges["Source"].isin(node_ids)
    &
    trust_edges["Target"].isin(node_ids)
)

print("Trust Graph")

print("Total:", len(trust_edges))
print("Valid:", trust_valid.sum())
print("Invalid:", len(trust_edges)-trust_valid.sum())