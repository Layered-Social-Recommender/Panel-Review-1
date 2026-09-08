import pandas as pd
import networkx as nx

# Load our 1,003 target users
users_df = pd.read_csv("mastodon_users_1000.csv", dtype={"id": str})
target_users = set(users_df["id"])

# Load relationships
edges_df = pd.read_csv("mastodon_edges_1000.csv", dtype=str)

# Build directed graph
G = nx.from_pandas_edgelist(
    edges_df,
    source="source_id",
    target="target_id",
    create_using=nx.DiGraph()
)

# Basic statistics
all_nodes = set(G.nodes())

internal_nodes = all_nodes & target_users
external_nodes = all_nodes - target_users

print("\n==============================")
print("MASTODON GRAPH")
print("==============================")

print("Target users:", len(target_users))
print("Total nodes in graph:", G.number_of_nodes())
print("Internal target nodes:", len(internal_nodes))
print("External nodes:", len(external_nodes))
print("Total edges:", G.number_of_edges())

print("\nGraph density:")
print(nx.density(G))

print("\nStrongly connected components:",
      nx.number_strongly_connected_components(G))

print("Weakly connected components:",
      nx.number_weakly_connected_components(G))