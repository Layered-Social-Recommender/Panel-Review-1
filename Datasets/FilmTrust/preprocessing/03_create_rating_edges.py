import pandas as pd

ratings = pd.read_csv(
    "data/ratings.txt",
    sep=" ",
    header=None,
    names=["user_id","movie_id","rating"]
)

edges = pd.DataFrame({

    "Source":
    "U"+ratings["user_id"].astype(str),

    "Target":
    "M"+ratings["movie_id"].astype(str),

    "Type":
    "Directed",

    "EdgeType":
    "Rating",

    "Weight":
    ratings["rating"]

})

edges.to_csv(
    "output/rating_edges.csv",
    index=False
)

print(edges.head())
print()

print("Rating edges:",len(edges))