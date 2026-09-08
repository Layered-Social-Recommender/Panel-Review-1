import argparse
import random
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score

RANDOM_STATE = 42
random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)


def load_edges(path):
    df = pd.read_csv(path)
    if df.shape[1] < 2:
        raise ValueError("The edge file must have at least two columns.")
    df = df.iloc[:, :2].copy()
    df.columns = ["source", "target"]
    df = df.dropna().drop_duplicates()
    return df


def compute_node_features(G):
    print("Computing node features...")
    degree = dict(G.degree())
    pagerank = nx.pagerank(G)

    # Approximation: much faster than exact betweenness on 37k nodes.
    betweenness = nx.betweenness_centrality(
        G, k=min(1000, G.number_of_nodes()), normalized=True, seed=RANDOM_STATE
    )

    clustering = nx.clustering(G)

    print("Detecting communities with Louvain...")
    communities = nx.community.louvain_communities(G, seed=RANDOM_STATE)

    community = {}
    for cid, members in enumerate(communities):
        for n in members:
            community[n] = cid

    community_participation = {}
    for n in G.nodes():
        nbrs = list(G.neighbors(n))
        if not nbrs:
            community_participation[n] = 0.0
        else:
            community_participation[n] = sum(
                community[x] == community[n] for x in nbrs
            ) / len(nbrs)

    return {
        n: {
            "degree": degree[n],
            "pagerank": pagerank[n],
            "betweenness": betweenness[n],
            "clustering": clustering[n],
            "community": community[n],
            "community_participation": community_participation[n],
        }
        for n in G.nodes()
    }


def sample_negative_pairs(G, n):
    nodes = list(G.nodes())
    existing = {tuple(sorted(e)) for e in G.edges()}
    negatives = set()

    while len(negatives) < n:
        a, b = random.sample(nodes, 2)
        pair = tuple(sorted((a, b)))
        if pair in existing:
            continue
        negatives.add(pair)

    return list(negatives)


def make_pair_features(G, node_features, pairs):
    rows = []

    for a, b in pairs:
        fa, fb = node_features[a], node_features[b]

        na = set(G.neighbors(a))
        nb = set(G.neighbors(b))
        common = len(na & nb)
        union = len(na | nb)
        jaccard = common / union if union else 0.0

        rows.append({
            "a": a,
            "b": b,

            "a_degree": fa["degree"],
            "b_degree": fb["degree"],
            "a_pagerank": fa["pagerank"],
            "b_pagerank": fb["pagerank"],
            "a_betweenness": fa["betweenness"],
            "b_betweenness": fb["betweenness"],
            "a_clustering": fa["clustering"],
            "b_clustering": fb["clustering"],
            "a_community_participation": fa["community_participation"],
            "b_community_participation": fb["community_participation"],

            "same_community": int(fa["community"] == fb["community"]),
            "common_neighbors": common,
            "jaccard_neighbors": jaccard,
            "preferential_attachment": len(na) * len(nb),
        })

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="SNAP GitHub edge CSV file")
    args = parser.parse_args()

    print("=" * 60)
    print("SNAP GITHUB SOCIAL RELATIONSHIP MODEL")
    print("=" * 60)

    df = load_edges(args.file)
    print(f"Edges: {len(df):,}")

    G = nx.from_pandas_edgelist(
        df, source="source", target="target", create_using=nx.Graph()
    )
    print(f"Nodes: {G.number_of_nodes():,}")
    print(f"Edges: {G.number_of_edges():,}")

    node_features = compute_node_features(G)

    positive = list(G.edges())
    negative = sample_negative_pairs(G, len(positive))
    print(f"Positive connection pairs: {len(positive):,}")
    print(f"Negative sampled pairs: {len(negative):,}")

    print("Building pairwise features...")
    pos_df = make_pair_features(G, node_features, positive)
    neg_df = make_pair_features(G, node_features, negative)

    pos_df["connection_label"] = 1
    neg_df["connection_label"] = 0

    data = pd.concat([pos_df, neg_df], ignore_index=True)
    data = data.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    feature_cols = [
        c for c in data.columns
        if c not in ["a", "b", "connection_label"]
    ]

    X = data[feature_cols]
    y = data["connection_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    print("Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]

    print("\nMODEL RESULTS")
    print("-" * 60)
    print(f"Accuracy : {accuracy_score(y_test, pred):.4f}")
    print(f"ROC-AUC  : {roc_auc_score(y_test, prob):.4f}")
    print(classification_report(y_test, pred))

    importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    importance.to_csv("GitHub_feature_importance.csv", index=False)

    all_prob = model.predict_proba(X)[:, 1]
    output = data[["a", "b", "connection_label"]].copy()
    output["predicted_connection_probability"] = all_prob
    output["predicted_connection"] = (all_prob >= 0.5).astype(int)
    output.to_csv("GitHub_relationship_predictions.csv", index=False)

    print("\nSaved:")
    print("  GitHub_feature_importance.csv")
    print("  GitHub_relationship_predictions.csv")
    print("\nTop features:")
    print(importance.head(10).to_string(index=False))


if __name__ == "__main__":
    main()