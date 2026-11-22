
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "raw_data" / "93182_steam_games.csv"
BATCH_FILE = ROOT / "batch.csv"
PROGRESS_FILE = ROOT / "raw_data" / "batch_progress.txt"

BATCH_SIZE = 100

# Load the original dataset
df = pd.read_csv(DATA_FILE, low_memory=False)

# Find where the previous batch stopped
if PROGRESS_FILE.exists():
    start = int(PROGRESS_FILE.read_text())
else:
    start = 0

# Generate the next batch
if start >= len(df):
    print("All games have been processed!")
else:
    end = min(start + BATCH_SIZE, len(df))

    batch = df.iloc[start:end]

    # Save only the current batch
    batch.to_csv(BATCH_FILE, index=False)

    # Remember progress locally
    PROGRESS_FILE.write_text(str(end))

    print("Batch created successfully!")
    print("Games in batch:", len(batch))
    print("Rows processed:", start, "to", end)
    print("Remaining games:", len(df) - end)
