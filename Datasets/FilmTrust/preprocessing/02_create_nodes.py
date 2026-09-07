import pandas as pd

ratings = pd.read_csv(
    "data/ratings.txt",
    sep=" ",
    header=None,
    names=["user_id","movie_id","rating"]
)

trust = pd.read_csv(
    "data/trust.txt",
    sep=" ",
    header=None,
    names=["trustor","trustee","trust"]
)

# ----------------------------
# User Nodes
# ----------------------------

rating_users = set(ratings["user_id"])

trust_users = set(trust["trustor"]).union(
    set(trust["trustee"])
)

all_users = sorted(rating_users.union(trust_users))

user_nodes = pd.DataFrame({
    "Id": ["U"+str(i) for i in all_users],
    "Label": ["User_"+str(i) for i in all_users],
    "Type": "User"
})

# ----------------------------
# Movie Nodes
# ----------------------------

movies = sorted(ratings["movie_id"].unique())

movie_nodes = pd.DataFrame({
    "Id": ["M"+str(i) for i in movies],
    "Label": ["Movie_"+str(i) for i in movies],
    "Type": "Movie"
})

nodes = pd.concat([user_nodes, movie_nodes],
                  ignore_index=True)

nodes.to_csv("output/nodes.csv",
             index=False)

print(nodes.head())

print()

print("Users :",len(user_nodes))
print("Movies:",len(movie_nodes))
print("Total :",len(nodes))