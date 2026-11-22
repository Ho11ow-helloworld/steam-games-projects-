
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def clean_data(input_file, output_file):
    df = pd.read_csv(input_file, low_memory=False)

    # Rename columns
    df = df.rename(columns={
        "AppID": "app_id",
        "Name": "name",
        "Release date": "release_date",
        "Price": "price",
        "Positive": "positive_reviews",
        "Negative": "negative_reviews",
        "Genres": "genres",
        "Estimated owners": "estimated_owners_range",
        "Peak CCU": "peak_ccu",
        "Average playtime forever": "average_playtime_minutes"
    })

    # Remove missing game names and duplicate IDs
    df = df.dropna(subset=["app_id", "name"])
    df = df.drop_duplicates(subset="app_id")

    # Clean numerical values
    for col in ["price", "positive_reviews", "negative_reviews"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["price", "positive_reviews", "negative_reviews"])

    df = df[
        (df["price"] >= 0) &
        (df["positive_reviews"] >= 0) &
        (df["negative_reviews"] >= 0)
    ].copy()

    # Standardize dates
    df["release_date"] = pd.to_datetime(
        df["release_date"], errors="coerce", format="mixed"
    )

    df["release_year"] = df["release_date"].dt.year
    df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")

    # Calculate shared indicators
    df["total_reviews"] = df["positive_reviews"] + df["negative_reviews"]

    df["satisfaction_pct"] = (
        100 * df["positive_reviews"] /
        df["total_reviews"].replace(0, float("nan"))
    ).round(2)

    # Save cleaned data
    df.to_csv(output_file, index=False)

    print("Original rows:", len(pd.read_csv(input_file)))
    print("Cleaned rows:", len(df))
    print("Missing release dates:", df["release_date"].isna().sum())
    print("Games with no reviews:", (df["total_reviews"] == 0).sum())
    print("Cleaning completed!")


if __name__ == "__main__":
    clean_data(
        ROOT / "raw_data" / "93182_steam_games.csv",
        ROOT / "cleaned_data" / "steam_cleaned.csv"
    )
