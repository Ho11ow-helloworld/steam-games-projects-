import pandas as pd

# Load the cleaned sample shared by Alec
df = pd.read_csv("samples/steam_sample.csv")

# Select the columns needed for the initial exploration
columns = [
    "name",
    "positive_reviews",
    "negative_reviews",
    "total_reviews",
    "satisfaction_pct",
]

# Display the first five games
print("\nFirst five games:")
print(df[columns].head().to_string(index=False))

# Apply the minimum review threshold shared with Yanghe
has_enough_reviews = df["total_reviews"] >= 30

# Display the number of games in each group
print("\nGames in the sample:", len(df))
print("Games with at least 30 reviews:", has_enough_reviews.sum())
print("Games with fewer than 30 reviews:", (~has_enough_reviews).sum())