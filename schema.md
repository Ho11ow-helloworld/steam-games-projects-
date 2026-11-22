# Project Schema

How data moves through the Steam Hidden Gems pipeline, and what each file contains.
Column definitions: see `data_dictionary.md`.

## 1. Folder structure

```
steam-games-projects-/
├── .github/workflows/batch_pipeline.yml   # GitHub Actions: runs the pipeline on each new batch
├── raw_data/          # original Kaggle CSV (local only, not in Git)
├── batch.csv          # current batch of 100 raw games (pushed by batch_sim.py)
├── cleaned_data/      # cleaned and consolidated data (generated, not in Git)
├── samples/           # steam_sample.csv: small shared sample for development
├── scripts/           # all Python scripts
├── outputs/           # indicators and reports (generated, not in Git)
├── documentation/     # project documentation
├── data_dictionary.md
├── schema.md
└── requirements.txt
```

## 2. Pipeline flow

```
raw_data/93182_steam_games.csv
        │  batch_sim.py          (local: writes the next 100 games to batch.csv, which is then pushed to GitHub)
        ▼
batch.csv
        │  process_batch.py      (cleans the batch with cleaning.clean_data)
        ▼
cleaned_data/steam_batch_cleaned.csv
        │  consolidate_batches.py (adds the batch to all previous ones, removes duplicate app_id)
        ▼
cleaned_data/steam_consolidated.csv
        │
        ├─ batch_report.py       → outputs/data_quality_report.json, outputs/batch_log.csv
        ├─ Hidden Gems analysis  → outputs/hidden_gems.csv
        ├─ genre_pricing.py      → outputs/genre_price_summary.csv
        └─ ML analysis           → outputs/ml_clusters.csv
                │
                ▼
        Dash dashboard (reads the files in outputs/)
```

On GitHub, `batch_pipeline.yml` runs these steps each time `batch.csv` or a script is pushed to `main`. It restores `steam_consolidated.csv` and `batch_log.csv` from the previous successful run, so the data keeps growing batch after batch, and uploads the results as the artifact `steam-batch-results`.

For a full local run, `cleaning.py` cleans the whole raw file into `cleaned_data/steam_cleaned.csv` in one go.

## 3. Files

| File | Created by | One row = | Key | Content |
|---|---|---|---|---|
| `raw_data/93182_steam_games.csv` | Kaggle download | game | `AppID` | Original data, never modified |
| `batch.csv` | `batch_sim.py` | game | `AppID` | Current raw batch (100 games) |
| `cleaned_data/steam_cleaned.csv` | `cleaning.py` | game | `app_id` | Whole dataset, cleaned (local run) |
| `cleaned_data/steam_batch_cleaned.csv` | `process_batch.py` | game | `app_id` | Current batch, cleaned |
| `cleaned_data/steam_consolidated.csv` | `consolidate_batches.py` | game | `app_id` | All batches processed so far |
| `samples/steam_sample.csv` | `create_sample.py` | game | `app_id` | 90 games (with and without reviews / genres) for development |
| `outputs/data_quality_report.json` | `batch_report.py` | – | – | Totals, duplicates, missing values, games without reviews |
| `outputs/batch_log.csv` | `batch_report.py` | batch | `batch_id` | History of processed batches (rows received, cleaned, removed) |
| `outputs/hidden_gems.csv` | Hidden Gems analysis | game | `app_id` | Hidden Gems ranking *(Member 2)* |
| `outputs/genre_price_summary.csv` | `genre_pricing.py` | genre × price category | `genre`, `price_category` | Satisfaction, competition and promising segments (see `documentation/genre_pricing.md`) |
| `outputs/ml_clusters.csv` | ML analysis | game | `app_id` | ML segment per game *(Member 4)* |

## 4. Common rules

- UTF-8 CSV, comma separator, dates as `YYYY-MM-DD`.
- `app_id` identifies a unique game; batch processing removes duplicates on `app_id`.
- The original dataset is never modified.
- Indicators are calculated from the consolidated cleaned data.
