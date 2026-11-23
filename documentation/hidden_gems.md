# Hidden Gems Analysis

## Objective

We identify games that combine high player satisfaction with relatively few reviews.

## Input and execution

For the final analysis, we use the shared full cleaned dataset containing 93,179 games.

Run from the repository root:

```bash
python scripts/hidden_gems.py cleaned_data/steam_cleaned.csv
```

For development, we use the 90-game sample and save its outputs separately:

```bash
python scripts/hidden_gems.py samples/steam_sample.csv --output-dir outputs/sample_test
```

The script prints the input path and number of games analyzed. It does not modify the input dataset.

## Selection criteria

We select games that meet all three conditions:

- At least 30 total reviews.
- At most 500 total reviews, inclusive.
- At least 90% positive reviews, using the unrounded ratio.

The minimum review count matches the genre and pricing analysis. It reduces reliance on very small review counts but does not guarantee statistical reliability.

These thresholds are project choices, not official Steam criteria. Low review volume is our proxy for limited visibility.

Games without reviews remain in the indicators table but cannot qualify for the ranking.

## Ranking method

We calculate hidden_gem_score using the lower bound of the 95% Wilson score interval, multiplied by 100, with z = 1.96.

For n total reviews and p = positive_reviews / n:

```text
score = 100 * (p + z²/(2n) - z*sqrt((p*(1-p) + z²/(4n))/n)) / (1 + z²/n)
```

The score considers both the positive-review proportion and the number of reviews supporting it.

We rank candidates by unrounded score in descending order. Ties are resolved by total reviews descending, then app_id ascending.

## Full dataset results

We analyzed 93,179 games and identified 1,071 candidates.

Moss: Book II ranked first, with 495 reviews, 99.39% positive reviews and a Hidden Gem Score of 98.23.

## Sensitivity analysis

We kept the minimum at 30 reviews and compared nine combinations of review caps and satisfaction thresholds.

| Maximum reviews | Candidates at 85% | Candidates at 90% | Candidates at 95% |
|---|---:|---:|---:|
| 200 | 1,261 | 812 | 352 |
| 500 | 1,664 | 1,071 | 446 |
| 1,000 | 1,889 | 1,202 | 487 |

We also compared each alternative Top 10 with the default Top 10.

| Maximum reviews | Shared games with the default Top 10, at each tested satisfaction threshold |
|---|---:|
| 200 | 0 of 10 |
| 500 | 10 of 10 |
| 1,000 | 7 of 10 |

The default Top 10 membership is unchanged across the tested satisfaction thresholds when the cap remains 500. Changing the review cap changes its membership.

These comparisons describe sensitivity to our choices; they do not establish optimal thresholds.

## Output files

CSV files use UTF-8 encoding, comma separators and no exported index. Original input columns are retained.

| File in outputs/ | Contents |
|---|---|
| hidden_gems.csv | All eligible candidates, ordered by score, with rank and game information |
| hidden_gems_indicators.csv | All input games with hidden_gem_score and is_hidden_gem |
| hidden_gems_sensitivity.csv | Candidate counts for the nine threshold combinations |
| hidden_gems_scatter.html | Satisfaction versus review count for games with at least the selected minimum reviews |
| hidden_gems_top10.html | The ten highest-ranked candidates |

## Dashboard integration

We use hidden_gems.csv for the ranking table and hidden_gems_indicators.csv for filtering and joins on app_id.

The HTML files are standalone interactive charts. The dashboard can recreate these figures using the CSV files or the plotting logic in scripts/hidden_gems.py.

Final analyses should use the same shared cleaned dataset.

## Validation

- The script ran successfully on the 90-game sample and identified 5 candidates.
- The script ran successfully on the full cleaned dataset and identified 1,071 candidates.
- The script checks identifiers, review counts, review totals and satisfaction percentages before scoring.
- We compared candidate counts and Top 10 membership across nine threshold combinations.

## Limitations

- Low review volume does not prove low awareness or explain its causes.
- Recent releases have had less time to accumulate reviews. Release age is not an eligibility criterion in this analysis.
- Reviews are voluntary and may not represent all players. Wilson scoring does not remove review bias.
- Wilson's interval interpretation assumes binomial review outcomes.
- The dataset is a historical snapshot from September 2024.
- Results do not establish profitability, future success or a probability of commercial success.