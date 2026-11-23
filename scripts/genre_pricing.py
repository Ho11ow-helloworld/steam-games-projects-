"""
Member 3 - Genre & Pricing Analysis

Question 2: How do game genres and pricing relate to player satisfaction,
and which market segments appear most promising?

Input : cleaned_data/steam_consolidated.csv (pipeline)
        or cleaned_data/steam_cleaned.csv (full local run)
        or samples/steam_sample.csv (development)
Output: outputs/genre_price_summary.csv
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "outputs" / "genre_price_summary.csv"

INPUT_CANDIDATES = [
    ROOT / "cleaned_data" / "steam_consolidated.csv",
    ROOT / "cleaned_data" / "steam_cleaned.csv",
    ROOT / "samples" / "steam_sample.csv",
]

# A game needs at least this many reviews before its satisfaction_pct is
# trusted (a game with 3 positive reviews would otherwise show 100%).
# Must be the same value as the one used for the Hidden Gems analysis.
MIN_REVIEWS = 30

# A segment needs at least this many rated games before we call it promising.
MIN_RATED_GAMES = 30

# Price categories (USD). Upper bounds follow common Steam price points.
PRICE_BINS = [-0.01, 0, 4.99, 14.99, float("inf")]
PRICE_LABELS = ["Free", "Budget", "Mid-range", "Premium"]

# Only real game genres are kept. Steam's "Genres" field also contains
# business-model labels (Early Access, Free To Play), content warnings
# (Violent, Gore, ...) and software categories (Utilities, Education, ...).
GAME_GENRES = [
    "Action", "Adventure", "Casual", "Indie", "Massively Multiplayer",
    "Racing", "RPG", "Simulation", "Sports", "Strategy",
]


def load_data():
    """Use the file given on the command line, else the first one that exists."""
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = next(p for p in INPUT_CANDIDATES if p.exists())
    print("Input file:", path)
    return pd.read_csv(path, low_memory=False)


def add_price_category(df):
    """Add the shared column price_category (Free / Budget / Mid-range / Premium)."""
    df = df.copy()
    df["price_category"] = pd.cut(df["price"], bins=PRICE_BINS, labels=PRICE_LABELS)
    df["price_category"] = df["price_category"].astype(str)
    return df


def explode_genres(df):
    """One row per (game, genre), keeping only real game genres."""
    df = df.dropna(subset=["genres"]).copy()
    df["genre"] = df["genres"].str.split(",")
    df = df.explode("genre")
    df["genre"] = df["genre"].str.strip()
    return df[df["genre"].isin(GAME_GENRES)]


def summarize_segments(df, keys, min_reviews=MIN_REVIEWS):
    """Indicators for each segment defined by the columns in keys."""
    df = df.copy()
    rated = df["total_reviews"] >= min_reviews
    df["rated_satisfaction"] = df["satisfaction_pct"].where(rated)
    df["rated_reviews"] = df["total_reviews"].where(rated)

    return df.groupby(keys).agg(
        # Competition: every game in the segment competes for players,
        # including games with few or no reviews.
        n_games=("app_id", "size"),
        n_rated_games=("rated_satisfaction", "count"),
        # Median, not total positive / total reviews: the ratio of totals
        # would be dominated by a few blockbusters.
        median_satisfaction_pct=("rated_satisfaction", "median"),
        # Audience size proxy among rated games.
        median_total_reviews=("rated_reviews", "median"),
    ).reset_index()


def build_genre_price_summary(df, min_reviews=MIN_REVIEWS):
    """Long table: one row per genre x price_category, plus 'All' rows."""
    df = add_price_category(df)
    df["genre"] = "All"
    genres = explode_genres(df.drop(columns="genre"))

    by_both = summarize_segments(genres, ["genre", "price_category"], min_reviews)

    by_genre = summarize_segments(genres, ["genre"], min_reviews)
    by_genre["price_category"] = "All"

    # Price-only and overall rows use the games table (not exploded),
    # so each game is counted once.
    by_price = summarize_segments(df, ["genre", "price_category"], min_reviews)

    overall = summarize_segments(df, ["genre"], min_reviews)
    overall["price_category"] = "All"

    summary = pd.concat([by_both, by_genre, by_price, overall], ignore_index=True)

    # Satisfaction compared with the whole market, in percentage points.
    baseline = overall["median_satisfaction_pct"].iloc[0]
    summary["satisfaction_gap"] = (summary["median_satisfaction_pct"] - baseline).round(2)
    summary["median_satisfaction_pct"] = summary["median_satisfaction_pct"].round(2)

    columns = [
        "genre", "price_category", "n_games", "n_rated_games",
        "median_satisfaction_pct", "satisfaction_gap", "median_total_reviews",
    ]
    return summary[columns]


def flag_promising(summary, min_rated_games=MIN_RATED_GAMES):
    """
    A genre x price segment is promising when:
      - players are more satisfied than in the market overall (gap > 0)
      - competition is below the median of comparable segments
      - it has enough rated games for the result to be reliable
    """
    summary = summary.copy()
    segments = (
        (summary["genre"] != "All")
        & (summary["price_category"] != "All")
        & (summary["n_rated_games"] >= min_rated_games)
    )
    competition_median = summary.loc[segments, "n_games"].median()

    summary["is_promising"] = (
        segments
        & (summary["satisfaction_gap"] > 0)
        & (summary["n_games"] < competition_median)
    )
    return summary


if __name__ == "__main__":
    data = load_data()
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT_FILE
    print("Games loaded:", len(data))

    summary = build_genre_price_summary(data)
    summary = flag_promising(summary)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_file, index=False)

    print("\nSatisfaction by price category:")
    print(summary[summary["genre"] == "All"].to_string(index=False))

    print("\nPromising segments:")
    promising = summary[summary["is_promising"]]
    if promising.empty:
        print("None yet (not enough rated games in this data).")
    else:
        print(promising.sort_values("satisfaction_gap", ascending=False).to_string(index=False))

    print("\nSaved:", output_file)
    print("Genre & pricing analysis completed!")
