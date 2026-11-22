# Data Dictionary

Source: [93,182 Steam Games (Kaggle)](https://www.kaggle.com/datasets/joebeachcapital/top-1000-steam-games), file `93182_steam_games.csv`, scraped from Steam and SteamSpy on 15 September 2024.

All column names use `snake_case`. Files are UTF-8 CSV with comma separators. Dates use `YYYY-MM-DD`. `app_id` identifies a unique game.

## 1. Standardized columns (renamed from the original dataset)

Created by `scripts/cleaning.py`. Examples come from one game in `samples/steam_sample.csv` (Shadow Empire).

| Column | Original column | Type | Description | Example |
|---|---|---|---|---|
| `app_id` | AppID | integer | Unique Steam identifier of the game | `1154840` |
| `name` | Name | text | Game title | `Shadow Empire` |
| `release_date` | Release date | date (`YYYY-MM-DD`) | Release date on Steam | `2020-12-03` |
| `price` | Price | number (USD) | Price at scraping time; `0` = free | `39.99` |
| `positive_reviews` | Positive | integer | Number of positive player reviews | `1145` |
| `negative_reviews` | Negative | integer | Number of negative player reviews | `168` |
| `genres` | Genres | text, comma-separated | Steam genres, several per game, no spaces | `RPG,Simulation,Strategy` |
| `estimated_owners_range` | Estimated owners | text range | SteamSpy owner estimate, as a range | `50000 - 100000` |
| `peak_ccu` | Peak CCU | integer | Peak concurrent players (SteamSpy) | `83` |
| `average_playtime_minutes` | Average playtime forever | integer (minutes) | Average total playtime per owner | `0` |

## 2. Calculated indicators

| Column | Type | Created by | Description |
|---|---|---|---|
| `total_reviews` | integer | `cleaning.py` | `positive_reviews + negative_reviews` |
| `satisfaction_pct` | number (0–100) | `cleaning.py` | `100 × positive_reviews / total_reviews`; empty when the game has no reviews |
| `release_year` | integer | `cleaning.py` | Year of `release_date` |
| `price_category` | text | `genre_pricing.py` (`add_price_category`) | `Free` ($0), `Budget` (< $5), `Mid-range` ($5–14.99), `Premium` (≥ $15) |
| `hidden_gem_score` | number | Hidden Gems analysis | Score used to rank hidden gems *(definition to be added by Member 2)* |
| `is_hidden_gem` | boolean | Hidden Gems analysis | Whether a game meets the hidden gem criteria *(to be added by Member 2)* |
| `ml_cluster` | integer | ML analysis | Game segment identified by ML *(to be added by Member 4)* |

## 3. Cleaning rules (`scripts/cleaning.py`)

- Rows without `app_id` or `name` are removed.
- Duplicate `app_id` are removed (first kept).
- `price`, `positive_reviews`, `negative_reviews` are converted to numbers; rows where they are missing or negative are removed.
- `release_date` is parsed from mixed formats and written as `YYYY-MM-DD`.

## 4. Known data limitations

- Only 12,895 of the 93,179 cleaned games have at least one review; 80,284 have 0 positive and 0 negative reviews. `satisfaction_pct` is empty for these games.
- The `genres` field also contains labels that are not genres: business models (`Early Access`, `Free To Play`), content warnings (`Violent`, `Gore`, `Nudity`, `Sexual Content`) and software categories (`Utilities`, `Education`, …).
- 4,799 games have no `genres`.
- `estimated_owners_range` is a range, not an exact number.
- The data is a snapshot from September 2024: prices and review counts may have changed since.
