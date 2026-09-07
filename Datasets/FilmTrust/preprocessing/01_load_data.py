import pandas as pd

ratings = pd.read_csv(
    "data/ratings.txt",
    sep=" ",
    header=None,
    names=["user_id", "movie_id", "rating"]
)

trust = pd.read_csv(
    "data/trust.txt",
    sep=" ",
    header=None,
    names=["trustor", "trustee", "trust"]
)

print("="*50)

print("Ratings")
print(ratings.shape)
print(ratings.head())

print()

print("Trust")
print(trust.shape)
print(trust.head())