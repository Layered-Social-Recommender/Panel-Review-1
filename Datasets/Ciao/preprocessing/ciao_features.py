import pandas as pd
import networkx as nx
import time

print("======================================")
print("CIAO BEHAVIOUR FEATURE COMPUTATION")
print("======================================")

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

FILE = "ciao_trust_edgelist.csv"

print("\n[1/7] Loading CIAO dataset...")

df = pd.read_csv(FILE)

print("Columns found:", list(df.columns))
print("Rows:", len(df))

# Automatically use first two columns
df = df.iloc[:, :2]
df.columns = ["source", "target"]

# Remove missing values
df = df.dropna()

# Remove duplicate relationships
df = df.drop_duplicates()

print("Edges after cleaning:", len(df))


# --------------------------------------------------
# 2. CREATE DIRECTED TRUST GRAPH
# --------------------------------------------------

print("\n[2/7] Creating directed trust graph...")

G = nx.from_pandas_edgelist(
    df,
    source="source",
    target="target",
    create_using=nx.DiGraph()
)

print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())


# --------------------------------------------------
# 3. ACTIVITY
# --------------------------------------------------

print("\n[3/7] Computing activity and popularity...")

out_degree = dict(G.out_degree())
in_degree = dict(G.in_degree())

features = pd.DataFrame({
    "user": list(G.nodes()),

    # Activity = number of users this person trusts
    "activity_out_degree": [
        out_degree[node] for node in G.nodes()
    ],

    # Popularity = number of users who trust this person
    "popularity_in_degree": [
        in_degree[node] for node in G.nodes()
    ]
})


# --------------------------------------------------
# 4. PAGERANK
# --------------------------------------------------

print("\n[4/7] Computing PageRank...")

start = time.time()

pagerank = nx.pagerank(G)

features["influence_pagerank"] = [
    pagerank[node] for node in G.nodes()
]

print("PageRank completed in %.2f seconds"
      % (time.time() - start))


# --------------------------------------------------
# 5. BETWEENNESS
# --------------------------------------------------

print("\nComputing Betweenness Centrality...")

start = time.time()

# Approximation for speed
betweenness = nx.betweenness_centrality(
    G,
    k=min(1000, G.number_of_nodes()),
    normalized=True,
    seed=42
)

features["bridge_betweenness"] = [
    betweenness[node] for node in G.nodes()
]

print("Betweenness completed in %.2f seconds"
      % (time.time() - start))


# --------------------------------------------------
# 6. RECIPROCITY
# --------------------------------------------------

print("\nComputing reciprocity...")

reciprocity = {}

for node in G.nodes():

    outgoing = set(G.successors(node))

    if len(outgoing) == 0:
        reciprocity[node] = 0

    else:

        mutual = sum(
            G.has_edge(neighbor, node)
            for neighbor in outgoing
        )

        reciprocity[node] = (
            mutual / len(outgoing)
        )

features["reciprocity"] = [
    reciprocity[node] for node in G.nodes()
]


# --------------------------------------------------
# 7. COMMUNITY DETECTION
# --------------------------------------------------

print("\n[5/7] Detecting communities...")

start = time.time()

# Use undirected version for community detection
G_undirected = G.to_undirected()

communities = nx.community.louvain_communities(
    G_undirected,
    seed=42
)

community_map = {}

for community_id, community in enumerate(communities):

    for node in community:
        community_map[node] = community_id

features["community_id"] = [
    community_map[node] for node in G.nodes()
]

print("Number of communities:", len(communities))

print("Community detection completed in %.2f seconds"
      % (time.time() - start))


# --------------------------------------------------
# 8. COMMUNITY PARTICIPATION
# --------------------------------------------------

print("\nComputing community participation ratio...")

community_ratio = {}

for node in G.nodes():

    neighbors = list(G_undirected.neighbors(node))

    if len(neighbors) == 0:
        community_ratio[node] = 0

    else:

        same_community = sum(
            community_map[n] == community_map[node]
            for n in neighbors
        )

        community_ratio[node] = (
            same_community / len(neighbors)
        )

features["community_participation"] = [
    community_ratio[node] for node in G.nodes()
]


# --------------------------------------------------
# 9. CLUSTERING COEFFICIENT
# --------------------------------------------------

print("\nComputing clustering coefficient...")

start = time.time()

clustering = nx.clustering(G_undirected)

features["clustering_coefficient"] = [
    clustering[node] for node in G.nodes()
]

print("Clustering completed in %.2f seconds"
      % (time.time() - start))


# --------------------------------------------------
# 10. SAVE
# --------------------------------------------------

print("\n[7/7] Saving results...")

OUTPUT = "CIAO_behaviour_features.csv"

features.to_csv(
    OUTPUT,
    index=False
)

print("\n======================================")
print("DONE!")
print("======================================")

print("\nOutput file:")
print(OUTPUT)

print("\nFeatures generated:")
print(list(features.columns))

print("\nNumber of users:", len(features))

print("\nFirst 5 rows:")
print(features.head())