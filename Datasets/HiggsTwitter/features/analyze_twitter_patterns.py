import pandas as pd

df = pd.read_csv("Twitter_combined_features.csv")

print("=" * 60)
print("DATASET")
print("=" * 60)

print("Total user pairs:", len(df))
print()


# --------------------------------------------------
# 1. Reciprocal vs non-reciprocal relationships
# --------------------------------------------------

print("=" * 60)
print("1. RECIPROCAL VS NON-RECIPROCAL PAIRS")
print("=" * 60)

comparison = df.groupby("Reciprocal")[
    [
        "Total_Interactions",
        "Common_Neighbors",
        "Jaccard",
        "Adamic_Adar",
        "Preferential_Attachment"
    ]
].mean()

print(comparison)
print()


# --------------------------------------------------
# 2. Same-community analysis
# --------------------------------------------------

print("=" * 60)
print("2. SAME COMMUNITY")
print("=" * 60)

same_community_percentage = (
    df["Same_Community"].mean() * 100
)

print(
    "Percentage of interacting pairs in same community:",
    round(same_community_percentage, 2),
    "%"
)

print()


# --------------------------------------------------
# 3. Reciprocity inside vs outside communities
# --------------------------------------------------

print("=" * 60)
print("3. RECIPROCITY AND COMMUNITY")
print("=" * 60)

community_reciprocity = df.groupby(
    "Same_Community"
)["Reciprocal"].mean() * 100

print(community_reciprocity)
print()


# --------------------------------------------------
# 4. Interaction frequency vs structural similarity
# --------------------------------------------------

print("=" * 60)
print("4. CORRELATIONS")
print("=" * 60)

columns = [
    "Total_Interactions",
    "Reverse_Interactions",
    "Common_Neighbors",
    "Jaccard",
    "Preferential_Attachment",
    "Adamic_Adar",
    "Same_Community",
    "Reciprocal"
]

correlations = df[columns].corr()

print(correlations.round(3))
print()


# --------------------------------------------------
# 5. Interaction type statistics
# --------------------------------------------------

print("=" * 60)
print("5. INTERACTION TYPES")
print("=" * 60)

print("Total retweets:", df["RT_Count"].sum())
print("Total replies:", df["RE_Count"].sum())
print("Total mentions:", df["MT_Count"].sum())

print()


# --------------------------------------------------
# 6. Percentage of pairs containing each interaction
# --------------------------------------------------

print("=" * 60)
print("6. PAIRS CONTAINING EACH INTERACTION TYPE")
print("=" * 60)

rt_pairs = (df["RT_Count"] > 0).mean() * 100
re_pairs = (df["RE_Count"] > 0).mean() * 100
mt_pairs = (df["MT_Count"] > 0).mean() * 100

print("Pairs with retweets:", round(rt_pairs, 2), "%")
print("Pairs with replies:", round(re_pairs, 2), "%")
print("Pairs with mentions:", round(mt_pairs, 2), "%")

print()


# --------------------------------------------------
# 7. Structural properties by interaction type
# --------------------------------------------------

print("=" * 60)
print("7. STRUCTURE BY INTERACTION TYPE")
print("=" * 60)

features = [
    "Common_Neighbors",
    "Jaccard",
    "Adamic_Adar",
    "Same_Community",
    "Reciprocal"
]

for interaction in ["RT_Count", "RE_Count", "MT_Count"]:

    subset = df[df[interaction] > 0]

    print()
    print(interaction)
    print("Number of pairs:", len(subset))

    if len(subset) > 0:
        print(subset[features].mean().round(4))


# --------------------------------------------------
# 8. Basic counts
# --------------------------------------------------

print()
print("=" * 60)
print("8. BASIC RELATIONSHIP COUNTS")
print("=" * 60)

reciprocal_pairs = (df["Reciprocal"] == 1).sum()
non_reciprocal_pairs = (df["Reciprocal"] == 0).sum()

print("Reciprocal directed pairs:", reciprocal_pairs)
print("Non-reciprocal directed pairs:", non_reciprocal_pairs)

print(
    "Reciprocal percentage:",
    round(df["Reciprocal"].mean() * 100, 2),
    "%"
)

print(
    "Pairs with at least one common neighbor:",
    (df["Common_Neighbors"] > 0).sum()
)

print(
    "Pairs in same community:",
    (df["Same_Community"] == 1).sum()
)