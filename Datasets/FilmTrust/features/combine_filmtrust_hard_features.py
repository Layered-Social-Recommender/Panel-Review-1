import pandas as pd


# --------------------------------------------------
# 1. Read the two files
# --------------------------------------------------

pairs = pd.read_csv("FilmTrust_hard_pair_features.csv")
nodes = pd.read_csv("FilmTrust_node_features.csv")


# --------------------------------------------------
# 2. Convert Gephi IDs
#
# Gephi has IDs like:
# U1, U2, U15
#
# Pair file has:
# 1, 2, 15
#
# So U15 -> 15
# --------------------------------------------------

nodes["User_ID"] = (
    nodes["Id"]
    .astype(str)
    .str.replace("U", "", regex=False)
    .astype(int)
)


# --------------------------------------------------
# 3. Select the node features we want
# --------------------------------------------------

features = nodes[
    [
        "User_ID",
        "indegree",
        "outdegree",
        "Degree",
        "pageranks",
        "clustering",
        "eigencentrality",
        "betweenesscentrality",
        "modularity_class"
    ]
].copy()


# --------------------------------------------------
# 4. Add SOURCE user's features
# --------------------------------------------------

source_features = features.rename(columns={
    "User_ID": "Source",

    "indegree": "Source_Indegree",
    "outdegree": "Source_Outdegree",
    "Degree": "Source_Degree",

    "pageranks": "Source_PageRank",
    "clustering": "Source_Clustering",
    "eigencentrality": "Source_Eigenvector",
    "betweenesscentrality": "Source_Betweenness",

    "modularity_class": "Source_Community"
})


combined = pairs.merge(
    source_features,
    on="Source",
    how="left"
)


# --------------------------------------------------
# 5. Add TARGET user's features
# --------------------------------------------------

target_features = features.rename(columns={
    "User_ID": "Target",

    "indegree": "Target_Indegree",
    "outdegree": "Target_Outdegree",
    "Degree": "Target_Degree",

    "pageranks": "Target_PageRank",
    "clustering": "Target_Clustering",
    "eigencentrality": "Target_Eigenvector",
    "betweenesscentrality": "Target_Betweenness",

    "modularity_class": "Target_Community"
})


combined = combined.merge(
    target_features,
    on="Target",
    how="left"
)


# --------------------------------------------------
# 6. Check whether both users are in same community
# --------------------------------------------------

combined["Same_Community"] = (
    combined["Source_Community"]
    == combined["Target_Community"]
).astype(int)


# --------------------------------------------------
# 7. Save
# --------------------------------------------------

combined.to_csv(
    "FilmTrust_hard_complete_features.csv",
    index=False
)


# --------------------------------------------------
# 8. Check result
# --------------------------------------------------

print("Done!")
print("Rows:", len(combined))
print("Columns:", len(combined.columns))

print()
print(combined.head())

print()
print("Missing Source features:")
print(combined["Source_Degree"].isna().sum())

print("Missing Target features:")
print(combined["Target_Degree"].isna().sum())