
import pandas as pd
from pathlib import Path

# Load the Steam dataset
root = Path(__file__).resolve().parent.parent
file = root / "raw_data" / "93182_steam_games.csv"

df = pd.read_csv(file, low_memory=False)

# 1. Dataset overview
print("\n=== DATASET OVERVIEW ===")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# 2. Column names and data types
print("\n=== COLUMNS AND TYPES ===")
print(df.dtypes)

# 3. Missing values
print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

# 4. Duplicates
print("\n=== DUPLICATES ===")
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate AppIDs:", df["AppID"].duplicated().sum())

# 5. Price and review statistics
print("\n=== NUMERICAL STATISTICS ===")
for col in ["Price", "Positive", "Negative"]:
    print(f"\n{col}:")
    print(pd.to_numeric(df[col], errors="coerce").describe())

print("\nData exploration completed!")
