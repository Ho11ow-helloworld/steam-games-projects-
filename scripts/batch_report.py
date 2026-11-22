
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)

# Load data
raw = pd.read_csv(ROOT / "batch.csv", low_memory=False)
cleaned = pd.read_csv(
    ROOT / "cleaned_data" / "steam_batch_cleaned.csv",
    low_memory=False
)
data = pd.read_csv(
    ROOT / "cleaned_data" / "steam_consolidated.csv",
    low_memory=False
)

# 1. Data quality report
report = {
    "total_games": len(data),
    "duplicate_app_ids": int(data["app_id"].duplicated().sum()),
    "missing_names": int(data["name"].isna().sum()),
    "missing_genres": int(data["genres"].isna().sum()),
    "missing_release_dates": int(data["release_date"].isna().sum()),
    "games_without_reviews": int((data["total_reviews"] == 0).sum())
}

report_file = OUTPUT / "data_quality_report.json"
report_file.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

# 2. Batch processing log
log_file = OUTPUT / "batch_log.csv"

batch_id = f"{raw['AppID'].iloc[0]}-{raw['AppID'].iloc[-1]}"

already_logged = False

if log_file.exists():
    logs = pd.read_csv(log_file)
    already_logged = batch_id in logs["batch_id"].astype(str).values

if not already_logged:
    log = pd.DataFrame([{
        "batch_id": batch_id,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "rows_received": len(raw),
        "rows_cleaned": len(cleaned),
        "rows_removed": len(raw) - len(cleaned),
        "total_consolidated": len(data)
    }])

    log.to_csv(
        log_file,
        mode="a",
        header=not log_file.exists(),
        index=False
    )
    print("Batch added to log!")
else:
    print("Batch already logged!")

print("Data quality report:", report)
print("Batch reporting completed!")
