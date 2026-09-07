import pandas as pd

# --------------------------------------------------
# 1. Load complete FilmTrust feature dataset
# --------------------------------------------------

df = pd.read_csv("FilmTrust_complete_features.csv")

print("=" * 70)
print("FILMTRUST TRUST FEATURE ANALYSIS")
print("=" * 70)

print("Total pairs:", len(df))
print("Observed trust edges:", (df["Trust"] == 1).sum())
print("Sampled non-edges:", (df["Trust"] == 0).sum())


# --------------------------------------------------
# 2. Pair-level structural features
# --------------------------------------------------

pair_features = [
    "Common_Neighbors",
    "Jaccard",
    "Preferential_Attachment",
    "Adamic_Adar"
]

print()
print("=" * 70)
print("1. PAIR-LEVEL FEATURES")
print("=" * 70)

pair_comparison = df.groupby("Trust")[pair_features].mean()

print(pair_comparison.round(6))


# --------------------------------------------------
# 3. Source-user features
# --------------------------------------------------

source_features = [
    "Source_Indegree",
    "Source_Outdegree",
    "Source_Degree",
    "Source_PageRank",
    "Source_Clustering",
    "Source_Eigenvector",
    "Source_Betweenness"
]

print()
print("=" * 70)
print("2. SOURCE USER FEATURES")
print("=" * 70)

source_comparison = df.groupby("Trust")[source_features].mean()

print(source_comparison.round(6))


# --------------------------------------------------
# 4. Target-user features
# --------------------------------------------------

target_features = [
    "Target_Indegree",
    "Target_Outdegree",
    "Target_Degree",
    "Target_PageRank",
    "Target_Clustering",
    "Target_Eigenvector",
    "Target_Betweenness"
]

print()
print("=" * 70)
print("3. TARGET USER FEATURES")
print("=" * 70)

target_comparison = df.groupby("Trust")[target_features].mean()

print(target_comparison.round(6))


# --------------------------------------------------
# 5. Same-community analysis
# --------------------------------------------------

print()
print("=" * 70)
print("4. COMMUNITY ANALYSIS")
print("=" * 70)

community = df.groupby("Trust")["Same_Community"].mean() * 100

print("Percentage of pairs in same community:")
print(community.round(2))


# --------------------------------------------------
# 6. Correlation with trust
# --------------------------------------------------

print()
print("=" * 70)
print("5. CORRELATION WITH TRUST")
print("=" * 70)

features = (
    pair_features
    + source_features
    + target_features
    + ["Same_Community"]
)

correlations = (
    df[features + ["Trust"]]
    .corr()["Trust"]
    .drop("Trust")
    .sort_values(ascending=False)
)

print(correlations.round(4))


# --------------------------------------------------
# 7. Save comparison table
# --------------------------------------------------

comparison = pd.DataFrame({
    "Non_Edge_Mean": df[df["Trust"] == 0][features].mean(),
    "Trust_Edge_Mean": df[df["Trust"] == 1][features].mean()
})

comparison["Difference"] = (
    comparison["Trust_Edge_Mean"]
    - comparison["Non_Edge_Mean"]
)

comparison["Ratio"] = (
    comparison["Trust_Edge_Mean"]
    / comparison["Non_Edge_Mean"].replace(0, float("nan"))
)

comparison.to_csv(
    "FilmTrust_feature_comparison.csv"
)

print()
print("=" * 70)
print("DONE")
print("=" * 70)

print("Saved: FilmTrust_feature_comparison.csv")