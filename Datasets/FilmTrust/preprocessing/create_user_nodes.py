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

user_nodes.to_csv(
    "output/user_nodes.csv",
    index=False
)

print(user_nodes.head())
print()

print("Total Users:",len(user_nodes))