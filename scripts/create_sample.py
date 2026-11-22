
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Load cleaned data
df = pd.read_csv(
    ROOT / "cleaned_data" / "steam_cleaned.csv",
    low_memory=False
)

# Select different types of games
reviewed = df[df["total_reviews"] > 0].sample(50, random_state=42)
no_reviews = df[df["total_reviews"] == 0].sample(30, random_state=42)
no_genres = df[df["genres"].isna()].sample(10, random_state=42)

# Combine samples and remove duplicates
sample = pd.concat([reviewed, no_reviews, no_genres])
sample = sample.drop_duplicates(subset="app_id")

# Keep the columns needed by the team
columns = [
    "app_id", "name", "release_date", "release_year",
    "price", "genres", "positive_reviews", "negative_reviews",
    "total_reviews", "satisfaction_pct",
    "estimated_owners_range", "peak_ccu",
    "average_playtime_minutes"
]

sample = sample[columns]

# Save shared sample
sample.to_csv(
    ROOT / "samples" / "steam_sample.csv",
    index=False
)

print("Sample created successfully!")
print("Total games:", len(sample))
print("Games with reviews:", (sample["total_reviews"] > 0).sum())
print("Games without reviews:", (sample["total_reviews"] == 0).sum())
