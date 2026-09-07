import pandas as pd

behavior = pd.read_csv("Twitter_behavioral_features.csv")
pairwise = pd.read_csv("Twitter_pairwise_features.csv")

combined = behavior.merge(
    pairwise,
    on=["Source", "Target"],
    how="inner"
)

combined.to_csv(
    "Twitter_combined_features.csv",
    index=False
)

print("Done!")
print("Rows:", len(combined))
print()
print(combined.head())