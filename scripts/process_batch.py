
from pathlib import Path
from cleaning import clean_data

ROOT = Path(__file__).resolve().parent.parent

# Input: current batch
input_file = ROOT / "batch.csv"

# Output: cleaned batch
output_file = ROOT / "cleaned_data" / "steam_batch_cleaned.csv"

# Clean the batch
clean_data(input_file, output_file)

print("Batch processing completed!")
