"""
Member 4 — Machine Learning: Game Segmentation (K-Means Clustering)

Objective: segment Steam games into meaningful groups based on their
numerical characteristics so that the dashboard can highlight different
market profiles (e.g. niche vs. mainstream, premium vs. free).

Input : cleaned_data/steam_consolidated.csv  (pipeline / GitHub Actions)
        or cleaned_data/steam_cleaned.csv    (full local run)
        or samples/steam_sample.csv          (development)
Output: outputs/ml_clusters.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# paths
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "outputs" / "ml_clusters.csv"

INPUT_CANDIDATES = [
    ROOT / "cleaned_data" / "steam_consolidated.csv",
    ROOT / "cleaned_data" / "steam_cleaned.csv",
    ROOT / "samples" / "steam_sample.csv",
]

FEATURES = ["price", "total_reviews", "satisfaction_pct", "peak_ccu"]
MIN_REVIEWS_FOR_ML = 30  # same minimum as hidden_gems.py and genre_pricing.py
K_MIN = 2
K_MAX = 6
RANDOM_STATE = 42


def load_data():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = next(p for p in INPUT_CANDIDATES if p.exists())
    print("Input file:", path)
    return pd.read_csv(path, low_memory=False)


def prepare_features(df):
    eligible = df[df["total_reviews"] >= MIN_REVIEWS_FOR_ML].copy()
    print(f"Eligible games (>= {MIN_REVIEWS_FOR_ML} reviews): {len(eligible)} / {len(df)}")
    X = eligible[FEATURES].copy()
    X = X.fillna(0)
    X["total_reviews"] = np.log1p(X["total_reviews"])
    X["peak_ccu"] = np.log1p(X["peak_ccu"])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return eligible, X_scaled, scaler


def find_best_k(X_scaled, k_min=K_MIN, k_max=K_MAX):
    results = []
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE)
        labels = km.fit_predict(X_scaled)
        inertia = km.inertia_
        sil = silhouette_score(X_scaled, labels) if k > 1 else 0
        results.append({"k": k, "inertia": inertia, "silhouette": sil})
        print(f"  k={k}  inertia={inertia:,.0f}  silhouette={sil:.3f}")
    results_df = pd.DataFrame(results)
    best_k = int(results_df.loc[results_df["silhouette"].idxmax(), "k"])
    print(f"\nBest k by silhouette score: {best_k}")
    return best_k, results_df


def interpret_clusters(df, features=FEATURES):
    print("\nCluster profiles (median values):")
    profile = df.groupby("ml_cluster")[features].median().round(2)
    print(profile.to_string())
    print()
    labels = {}
    for cluster_id in profile.index:
        row = profile.loc[cluster_id]
        parts = []
        # Same 4 price categories as genre_pricing.py and the dashboard
        if row["price"] == 0:
            parts.append("Free")
        elif row["price"] < 5:
            parts.append("Budget")
        elif row["price"] < 15:
            parts.append("Mid-range")
        else:
            parts.append("Premium")
        if row["total_reviews"] >= 100:
            parts.append("Popular")
        else:
            parts.append("Niche")
        if row.get("satisfaction_pct", 0) >= 80:
            parts.append("High-rated")
        elif row.get("satisfaction_pct", 0) >= 60:
            parts.append("Mixed")
        else:
            parts.append("Low-rated")
        labels[cluster_id] = " / ".join(parts)
    print("Cluster labels:")
    for cid, label in sorted(labels.items()):
        count = (df["ml_cluster"] == cid).sum()
        print(f"  Cluster {cid}: {label} ({count} games)")
    return labels


def run_clustering(df):
    eligible, X_scaled, scaler = prepare_features(df)
    if len(eligible) < K_MAX:
        print(f"Not enough eligible games ({len(eligible)}) for clustering. Skipping.")
        df["ml_cluster"] = np.nan
        return df
    print("\nEvaluating cluster counts:")
    best_k, eval_results = find_best_k(X_scaled)
    final_model = KMeans(n_clusters=best_k, n_init=10, random_state=RANDOM_STATE)
    eligible["ml_cluster"] = final_model.fit_predict(X_scaled)
    cluster_labels = interpret_clusters(eligible)
    df = df.merge(eligible[["app_id", "ml_cluster"]], on="app_id", how="left")
    return df



if __name__ == "__main__":
    data = load_data()
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT_FILE

    print(f"Games loaded: {len(data)}")
    result = run_clustering(data)

    output_cols = [
        "app_id", "name", "price", "genres", "total_reviews",
        "satisfaction_pct", "peak_ccu", "release_year", "ml_cluster",
    ]

    output = result[[c for c in output_cols if c in result.columns]]

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_file, index=False)

    print(f"\nSaved: {output_file}")
    print(f"Games with cluster: {output['ml_cluster'].notna().sum()}")
    print(f"Games without cluster: {output['ml_cluster'].isna().sum()}")
    print("ML clustering completed!")

