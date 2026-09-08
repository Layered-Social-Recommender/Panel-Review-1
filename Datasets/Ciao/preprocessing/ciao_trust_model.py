import argparse
import time
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
    degree_out = dict(G.out_degree())
    degree_in = dict(G.in_degree())
    pagerank = nx.pagerank(G)
    betweenness = nx.betweenness_centrality(
        G, k=min(1000, G.number_of_nodes()), normalized=True, seed=RANDOM_STATE
    )
    UG = G.to_undirected()
    clustering = nx.clustering(UG)

    print("Detecting communities with Louvain...")
    communities = nx.community.louvain_communities(UG, seed=RANDOM_STATE)
    community = {}
    for cid, members in enumerate(communities):
        for n in members:
            community[n] = cid

    # Fraction of neighbours belonging to the same community.
    community_participation = {}
    for n in UG.nodes():
        nbrs = list(UG.neighbors(n))
        if not nbrs:
            community_participation[n] = 0.0
        else:
            community_participation[n] = sum(
                community[x] == community[n] for x in nbrs
            ) / len(nbrs)

    # Per-node reciprocity.
    reciprocity = {}
    for n in G.nodes():
        out_nbrs = list(G.successors(n))
        if not out_nbrs:
            reciprocity[n] = 0.0
        else:
            mutual = sum(G.has_edge(x, n) for x in out_nbrs)
            reciprocity[n] = mutual / len(out_nbrs)

    return {
        n: {
            "out_degree": degree_out[n],
            "in_degree": degree_in[n],
            "pagerank": pagerank[n],
            "betweenness": betweenness[n],
            "clustering": clustering[n],
            "community": community[n],
            "community_participation": community_participation[n],
            "reciprocity": reciprocity[n],
        }
        for n in G.nodes()
    }


def sample_negative_pairs(G, n):
    nodes = list(G.nodes())
    existing = set(G.edges())
    negatives = set()

    while len(negatives) < n:
        a = random.choice(nodes)
        b = random.choice(nodes)
        if a == b or (a, b) in existing:
            continue
        negatives.add((a, b))

    return list(negatives)


def make_pair_features(G, node_features, pairs, directed=True):
    UG = G.to_undirected()
    rows = []

    for idx, (a, b) in enumerate(pairs):
        fa, fb = node_features[a], node_features[b]

        na = set(UG.neighbors(a))
        nb = set(UG.neighbors(b))
        common = len(na & nb)
        union = len(na | nb)
        jaccard = common / union if union else 0.0

        # Local "network path" signal without running an expensive
        # all-pairs shortest-path calculation:
        # direct edge / common neighbour / within 3 hops.
        direct = int(G.has_edge(a, b))
        reverse = int(G.has_edge(b, a)) if directed else direct
        within_2 = int(common > 0)

        # Preferential attachment is a classic graph link-prediction feature.
        pref_attach = len(na) * len(nb)

        rows.append({
            "a": a,
            "b": b,

            "a_out_degree": fa["out_degree"],
            "b_out_degree": fb["out_degree"],
            "a_in_degree": fa["in_degree"],
            "b_in_degree": fb["in_degree"],

            "a_pagerank": fa["pagerank"],
            "b_pagerank": fb["pagerank"],
            "a_betweenness": fa["betweenness"],
            "b_betweenness": fb["betweenness"],

            "a_clustering": fa["clustering"],
            "b_clustering": fb["clustering"],

            "a_community_participation": fa["community_participation"],
            "b_community_participation": fb["community_participation"],

            "a_reciprocity": fa["reciprocity"],
            "b_reciprocity": fb["reciprocity"],

            "same_community": int(fa["community"] == fb["community"]),
            "common_neighbors": common,
            "jaccard_neighbors": jaccard,
            "preferential_attachment": pref_attach,
            "direct_connection": direct,
            "reverse_connection": reverse,
            "common_neighbor_path_signal": within_2,
        })

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="CIAO edge CSV file")
    args = parser.parse_args()

    print("=" * 60)
    print("CIAO TRUST MODEL")
    print("=" * 60)

    df = load_edges(args.file)
    print(f"Edges: {len(df):,}")

    G = nx.from_pandas_edgelist(
        df, source="source", target="target", create_using=nx.DiGraph()
    )
    print(f"Nodes: {G.number_of_nodes():,}")
    print(f"Edges: {G.number_of_edges():,}")

    node_features = compute_node_features(G)

    positive = list(G.edges())
    negative = sample_negative_pairs(G, len(positive))
    print(f"Positive trust pairs: {len(positive):,}")
    print(f"Negative sampled pairs: {len(negative):,}")

    print("Building pairwise features...")
    pos_df = make_pair_features(G, node_features, positive, directed=True)
    neg_df = make_pair_features(G, node_features, negative, directed=True)
    pos_df["trust_label"] = 1
    neg_df["trust_label"] = 0

    data = pd.concat([pos_df, neg_df], ignore_index=True)
    data = data.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    # Remove direct/reverse connection from the ML inputs because these are
    # essentially the label itself and would cause leakage.
    feature_cols = [
        c for c in data.columns
        if c not in ["a", "b", "trust_label", "direct_connection", "reverse_connection"]
    ]

    X = data[feature_cols]
    y = data["trust_label"]

    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, data.index, test_size=0.20, random_state=RANDOM_STATE, stratify=y
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

    importance.to_csv("CIAO_feature_importance.csv", index=False)

    # Predictions for every generated pair.
    all_prob = model.predict_proba(X)[:, 1]
    output = data[["a", "b", "trust_label"]].copy()
    output["predicted_trust_probability"] = all_prob
    output["predicted_trust"] = (all_prob >= 0.5).astype(int)
    output.to_csv("CIAO_trust_predictions.csv", index=False)

    print("\nSaved:")
    print("  CIAO_feature_importance.csv")
    print("  CIAO_trust_predictions.csv")
    print("\nTop features:")
    print(importance.head(10).to_string(index=False))


if __name__ == "__main__":
    main()