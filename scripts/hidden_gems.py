"""Identify and rank games with high satisfaction and limited review counts.

Run from the repository root:
    python scripts/hidden_gems.py cleaned_data/steam_cleaned.csv
"""

import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parent.parent
MIN_REVIEWS = 30  # Shared minimum across game-level and genre analyses.
MAX_REVIEWS = 500  # Provisional exploration threshold, not a Steam standard.
MIN_SATISFACTION = 90.0  # Provisional percentage of positive reviews.


def validate_data(df):
    """Validate the required columns and consistency of cleaned input data."""
    required = ["app_id", "name", "positive_reviews", "negative_reviews",
                "total_reviews", "satisfaction_pct"]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if df["app_id"].isna().any() or df["app_id"].duplicated().any():
        raise ValueError("Expected one nonmissing app_id per game.")
    df = df.copy()
    for col in ["positive_reviews", "negative_reviews", "total_reviews"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if (df[col].isna() | (df[col] < 0) | (df[col] % 1 != 0)).any():
            raise ValueError(f"{col} must contain nonnegative whole numbers.")
    if not (df["total_reviews"] == df["positive_reviews"] + df["negative_reviews"]).all():
        raise ValueError("total_reviews does not match positive + negative reviews.")
    df["satisfaction_pct"] = pd.to_numeric(df["satisfaction_pct"], errors="raise")
    reviewed = df["total_reviews"] > 0
    expected = 100 * df.loc[reviewed, "positive_reviews"] / df.loc[reviewed, "total_reviews"]
    actual = df.loc[reviewed, "satisfaction_pct"]
    if (actual.isna() | ((actual - expected).abs() > 0.011)).any():
        raise ValueError("satisfaction_pct is inconsistent with review counts.")
    if df.loc[~reviewed, "satisfaction_pct"].notna().any():
        raise ValueError("Games without reviews must have missing satisfaction_pct.")
    return df


def score_games(df, min_reviews=MIN_REVIEWS, max_reviews=MAX_REVIEWS,
                min_satisfaction=MIN_SATISFACTION):
    """Wilson lower bound ranks review evidence; review cap defines 'hidden'."""
    df = df.copy()
    n = df["total_reviews"].where(df["total_reviews"] > 0)
    p = df["positive_reviews"] / n
    z = 1.96
    lower = (p + z**2 / (2*n) - z *
             ((p*(1-p) + z**2 / (4*n)) / n)**0.5) / (1 + z**2/n)
    df["hidden_gem_score"] = (100 * lower).clip(0, 100)
    # Use the exact ratio for threshold checks, not its rounded display value.
    df["is_hidden_gem"] = (
        df["total_reviews"].between(min_reviews, max_reviews)
        & (100 * p >= min_satisfaction)
    )
    return df


def build_ranking(scored):
    ranking = scored.loc[scored["is_hidden_gem"]].copy()
    ranking = ranking.sort_values(
        ["hidden_gem_score", "total_reviews", "app_id"],
        ascending=[False, False, True]
    )
    ranking.insert(0, "rank", range(1, len(ranking) + 1))
    return ranking


def save_charts(scored, ranking, output_dir, min_reviews):
    """Generate standalone interactive Plotly charts."""
    plotted = scored[scored["total_reviews"] >= min_reviews]
    scatter = px.scatter(
        plotted, x="total_reviews", y="satisfaction_pct",
        color="is_hidden_gem", hover_name="name", log_x=True,
        title="Satisfaction and review volume in the selected input",
        labels={"total_reviews": "Total reviews (log scale)",
                "satisfaction_pct": "Positive reviews (%)",
                "is_hidden_gem": "Candidate"}
    )
    bars = px.bar(
        ranking.head(10).sort_values("rank", ascending=False),
        x="hidden_gem_score", y="name", orientation="h",
        hover_data=["total_reviews", "satisfaction_pct"],
        title="Top candidates in the selected input (empty if none qualify)",
        labels={"hidden_gem_score": "Wilson lower-bound score (0–100)", "name": "Game"}
    )
    scatter.write_html(output_dir / "hidden_gems_scatter.html", include_plotlyjs=True)
    bars.write_html(output_dir / "hidden_gems_top10.html", include_plotlyjs=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", nargs="?", type=Path)
    parser.add_argument("--min-reviews", type=int, default=MIN_REVIEWS)
    parser.add_argument("--max-reviews", type=int, default=MAX_REVIEWS)
    parser.add_argument("--min-satisfaction", type=float, default=MIN_SATISFACTION)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    if not (1 <= args.min_reviews <= args.max_reviews) or not (0 <= args.min_satisfaction <= 100):
        parser.error("Require 1 <= min-reviews <= max-reviews and satisfaction between 0 and 100.")
    path = args.input_file
    if path is None:
        candidates = [ROOT / "cleaned_data" / "steam_consolidated.csv",
                      ROOT / "cleaned_data" / "steam_cleaned.csv",
                      ROOT / "samples" / "steam_sample.csv"]
        path = next((p for p in candidates if p.exists()), None)
    if path is None or not path.is_file():
        parser.error("Provide an existing cleaned CSV or the shared sample.")
    data = validate_data(pd.read_csv(path, low_memory=False))
    scored = score_games(data, args.min_reviews, args.max_reviews, args.min_satisfaction)
    ranking = build_ranking(scored)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # All games retain a flag for filters/joins; ranking contains candidates only.
    scored.to_csv(args.output_dir / "hidden_gems_indicators.csv", index=False, encoding="utf-8")
    ranking.to_csv(args.output_dir / "hidden_gems.csv", index=False, encoding="utf-8")
    # Exploratory sensitivity: all nine combinations, without overwriting main criteria.
    sensitivity = []
    for maximum in [200, 500, 1000]:
        for satisfaction in [85, 90, 95]:
            if maximum >= args.min_reviews:
                trial = score_games(data, args.min_reviews, maximum, satisfaction)
                sensitivity.append({"min_reviews": args.min_reviews, "max_reviews": maximum,
                                    "min_satisfaction_pct": satisfaction,
                                    "n_candidates": int(trial["is_hidden_gem"].sum())})
    pd.DataFrame(sensitivity).to_csv(args.output_dir / "hidden_gems_sensitivity.csv", index=False)
    save_charts(scored, ranking, args.output_dir, args.min_reviews)
    print("Input:", path.resolve())
    print("Games analyzed:", len(data))
    print(f"Criteria: {args.min_reviews}–{args.max_reviews} reviews; >= {args.min_satisfaction}% positive")
    print("Hidden Gem candidates:", len(ranking))
    print(ranking[["rank", "name", "total_reviews", "satisfaction_pct", "hidden_gem_score"]]
          .head(10).round(2).to_string(index=False))
    print("Outputs:", args.output_dir.resolve())
    print("Analysis completed. Results describe the selected historical dataset.")


if __name__ == "__main__":
    main()

