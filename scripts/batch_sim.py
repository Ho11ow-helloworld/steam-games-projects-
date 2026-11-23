
import pandas as pd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "raw_data" / "93182_steam_games.csv"
BATCH_FILE = ROOT / "batch.csv"
PROGRESS_FILE = ROOT / "raw_data" / "batch_progress.txt"
PENDING_FILE = ROOT / "raw_data" / "pending_batch.txt"

BATCH_SIZE = 100

# Confirm a batch after successful processing
if len(sys.argv) > 1 and sys.argv[1] == "confirm":
    if PENDING_FILE.exists():
        PROGRESS_FILE.write_text(PENDING_FILE.read_text())
        PENDING_FILE.unlink()
        print("Batch confirmed! Progress saved.")
    else:
        print("No pending batch to confirm.")

# Generate a new batch
elif PENDING_FILE.exists():
    print("A batch is still pending confirmation.")

else:
    df = pd.read_csv(DATA_FILE, low_memory=False)

    start = int(PROGRESS_FILE.read_text()) if PROGRESS_FILE.exists() else 0

    if start >= len(df):
        print("All games have been processed!")
    else:
        end = min(start + BATCH_SIZE, len(df))

        batch = df.iloc[start:end]
        batch.to_csv(BATCH_FILE, index=False)

        # Save pending progress without confirming it
        PENDING_FILE.write_text(str(end))

        print("Batch created successfully!")
        print("Games in batch:", len(batch))
        print("Rows processed:", start, "to", end)
        print("Remaining games:", len(df) - end)
