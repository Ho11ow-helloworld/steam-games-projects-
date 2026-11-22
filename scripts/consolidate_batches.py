
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BATCH_FILE = ROOT / "cleaned_data" / "steam_batch_cleaned.csv"
OUTPUT_FILE = ROOT / "cleaned_data" / "steam_consolidated.csv"

# Load the cleaned batch
batch = pd.read_csv(BATCH_FILE, low_memory=False)

# Load existing data if available
if OUTPUT_FILE.exists():
    existing = pd.read_csv(OUTPUT_FILE, low_memory=False)
else:
    existing = pd.DataFrame()

# Combine existing data with the new batch
combined = pd.concat([existing, batch], ignore_index=True)

# Remove duplicate games using app_id
combined = combined.drop_duplicates(
    subset="app_id",
    keep="last"
)

# Save consolidated data
combined.to_csv(OUTPUT_FILE, index=False)

print("Batch games:", len(batch))
print("New games added:", len(combined) - len(existing))
print("Total consolidated games:", len(combined))
print("Consolidation completed!")
