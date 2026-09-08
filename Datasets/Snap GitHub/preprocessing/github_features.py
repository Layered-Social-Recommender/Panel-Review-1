import pandas as pd
import networkx as nx
import time

print("======================================")
print("SNAP GITHUB BEHAVIOUR FEATURE COMPUTATION")
print("======================================")

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

FILE = "musae_git_edges.csv"

print("\n[1/6] Loading GitHub dataset...")

df = pd.read_csv(FILE)

print("Columns found:", list(df.columns))
print("Rows:", len(df))

# Automatically use first two columns as source and target
df = df.iloc[:, :2]
df.columns = ["source", "target"]

# Remove missing values
df = df.dropna()

# Remove duplicate edges
df = df.drop_duplicates()

print("Edges after cleaning:", len(df))


# --------------------------------------------------
# 2. CREATE GRAPH
# --------------------------------------------------

print("\n[2/6] Creating undirected graph...")

G = nx.from_pandas_edgelist(
    df,
    source="source",
    target="target",
    create_using=nx.Graph()
)

print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())


# --------------------------------------------------
# 3. ACTIVITY / CONNECTIVITY
# --------------------------------------------------

print("\n[3/6] Computing activity (Degree)...")

degree = dict(G.degree())

features = pd.DataFrame({
    "user": list(G.nodes()),
    "activity_degree": [
        degree[node] for node in G.nodes()
    ]
})


# --------------------------------------------------
# 4. PAGERANK
# --------------------------------------------------

print("\n[4/6] Computing PageRank...")

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

# Approximation makes it practical for this large graph
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
# 6. COMMUNITY DETECTION
# --------------------------------------------------

print("\n[5/6] Detecting communities using Louvain...")

start = time.time()

communities = nx.community.louvain_communities(
    G,
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
# 7. COMMUNITY PARTICIPATION
# --------------------------------------------------

print("\nComputing community participation ratio...")

community_ratio = {}

for node in G.nodes():

    neighbors = list(G.neighbors(node))

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
# 8. CLUSTERING COEFFICIENT
# --------------------------------------------------

print("\nComputing clustering coefficient...")

start = time.time()

clustering = nx.clustering(G)

features["clustering_coefficient"] = [
    clustering[node] for node in G.nodes()
]

print("Clustering completed in %.2f seconds"
      % (time.time() - start))


# --------------------------------------------------
# 9. SAVE RESULTS
# --------------------------------------------------

print("\n[6/6] Saving results...")

OUTPUT = "GitHub_behaviour_features.csv"

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