# Genre & Pricing Analysis (Member 3)

**Question 2:** How do game genres and pricing relate to player satisfaction, and which market segments appear most promising?

Script: `scripts/genre_pricing.py`
Output: `outputs/genre_price_summary.csv`

## How to run

```
python scripts/genre_pricing.py                              # uses the first file found below
python scripts/genre_pricing.py samples/steam_sample.csv     # any cleaned file
```

Input, in order of priority: `cleaned_data/steam_consolidated.csv` (pipeline), `cleaned_data/steam_cleaned.csv` (full local run), `samples/steam_sample.csv` (development).

## Output columns (`genre_price_summary.csv`)

One row per segment. `All` in `genre` or `price_category` means "all genres" or "all prices".

| Column | Meaning | Unit |
|---|---|---|
| `genre` | Game genre, or `All` | – |
| `price_category` | Free / Budget / Mid-range / Premium, or `All` | – |
| `n_games` | Number of games in the segment = **competition** | games |
| `n_rated_games` | Games with at least `MIN_REVIEWS` reviews | games |
| `median_satisfaction_pct` | Median share of positive reviews among rated games | % (0–100) |
| `satisfaction_gap` | Difference from the whole market's median | percentage points |
| `median_total_reviews` | Median number of reviews among rated games = **audience size** proxy | reviews |
| `is_promising` | Segment more satisfying than the market **and** less crowded than the median segment | True/False |

For the dashboard: rows with `price_category == "All"` give the genre comparison, rows with `genre == "All"` give the price comparison, the other rows give the genre × price heatmap and the satisfaction-vs-competition chart.

## Design decisions

1. **Minimum reviews (`MIN_REVIEWS = 30`).** A game with 3 reviews, all positive, would show 100% satisfaction. Only games with at least 30 reviews count for satisfaction. On the full data this keeps 6,071 games. *Must be the same value as in the Hidden Gems analysis.*
2. **Median instead of total positive / total reviews.** Summing reviews would let a few blockbusters with hundreds of thousands of reviews decide a whole genre's score. The median describes the typical game.
3. **Competition counts every game**, including games with few or no reviews: they are still on the store competing for players.
4. **Price categories:** Free = $0, Budget < $5, Mid-range $5–14.99, Premium ≥ $15. Based on the price distribution (median $3.99, 75th percentile $9.99, 90th percentile $15.99) and common Steam price points.
5. **Only real game genres.** Steam's genre field also contains business-model labels (Early Access, Free To Play), content warnings (Violent, Gore, Nudity, Sexual Content) and software categories (Utilities, Education, Photo Editing, …). These are excluded. Kept: Action, Adventure, Casual, Indie, Massively Multiplayer, Racing, RPG, Simulation, Sports, Strategy.
6. **A game with several genres counts in each of them.** For price-only and overall rows, each game counts once.
7. **Promising segments need at least 30 rated games** (`MIN_RATED_GAMES`), so the result is not based on a handful of games.

## Data note

Only 12,895 of the 93,179 cleaned games have any review count (80,284 have 0 positive and 0 negative reviews in the dataset). Satisfaction results describe these reviewed games.

## First results (full dataset, 93,179 games)

- **Price:** Mid-range ($5–14.99) games have the highest median satisfaction (83.7%), Free games the lowest (79.0%). Overall median: 81.8%.
- **Genre:** Casual (83.4%), Indie (82.3%) and Adventure (82.0%) are above the market; Massively Multiplayer is far below (67.0%).
- **Promising segments** (above-market satisfaction, below-median competition): Racing–Premium (85.1%, 484 games), Adventure–Premium, Casual–Premium, Racing–Mid-range.

These results come from a historical snapshot (September 2024): they describe patterns, not future success.
