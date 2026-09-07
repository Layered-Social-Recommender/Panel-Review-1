import pandas as pd

trust = pd.read_csv(
    "data/trust.txt",
    sep=" ",
    header=None,
    names=["trustor","trustee","trust"]
)

edges = pd.DataFrame({

    "Source":
    "U"+trust["trustor"].astype(str),

    "Target":
    "U"+trust["trustee"].astype(str),

    "Type":
    "Directed",

    "EdgeType":
    "Trust",

    "Weight":
    trust["trust"]

})

edges.to_csv(
    "output/trust_edges.csv",
    index=False
)

print(edges.head())

print()

print("Trust edges:",len(edges))