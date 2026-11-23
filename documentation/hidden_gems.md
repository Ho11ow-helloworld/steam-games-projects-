# Hidden Gems analysis — Member 2 (Karla)

Question: Which games combine high player satisfaction with relatively few reviews?

## Run

From the repository root, with pandas and Plotly installed:

```bash
python scripts/hidden_gems.py samples/steam_sample.csv
python scripts/hidden_gems.py cleaned_data/steam_cleaned.csv
python scripts/hidden_gems.py cleaned_data/steam_consolidated.csv
```

An explicit input is recommended so a small accumulated batch is not mistaken for the full dataset. With no input argument the script follows Member 3's priority: consolidated, full cleaned, then sample. The input path and game count are printed. No original or cleaned input is modified.

## Proposed criteria — subject to team review

- At least **30 reviews**, matching Yanghe's minimum. This is a practical filter, not proof of statistical reliability.
- At most **500 reviews**, inclusive, as a provisional proxy for limited review visibility.
- At least **90% positive**, using the exact ratio from review counts rather than rounded `satisfaction_pct`.
- `is_hidden_gem` is true only when all three conditions hold. Zero-review games remain in the indicators table but cannot qualify.
- The 500/90 thresholds are illustrative starting choices, not an empirically validated optimum or official Steam definition. Inspect full-data distributions and sensitivity before finalizing. Release age is preserved as context, not an eligibility rule: recent releases have had less time to collect reviews.

## Ranking score

`hidden_gem_score` is 100 times the Wilson lower bound for the positive-review proportion, using z = 1.96. For n reviews, p = positive_reviews/n:

```text
score = 100 * (p + z²/(2n) - z*sqrt((p*(1-p) + z²/(4n))/n)) / (1 + z²/n)
```

This reduces the advantage of tiny perfect ratings. It is an evidence-adjusted review score, not a probability of commercial success or a combined measure of visibility. Limited visibility is enforced by the review cap. The interval interpretation assumes binomial review outcomes; voluntary reviews may be biased or dependent, so it is not a guarantee about all players. Ties are resolved by review count descending, then app_id ascending. Ranking uses unrounded scores.

## Files and dashboard integration

All CSVs are UTF-8, comma separated, with no index. Original input columns are retained.

| File in outputs/ | Contents |
|---|---|
| hidden_gems.csv | Candidates only, one row per app_id; rank, input columns, hidden_gem_score, is_hidden_gem. Empty output still has headers. |
| hidden_gems_indicators.csv | All input games with both added indicators; use this for dashboard filtering or joins on app_id. |
| hidden_gems_sensitivity.csv | Candidate counts for review caps 200/500/1000 and satisfaction thresholds 85/90/95, keeping the selected minimum review count. Counts alone do not validate ranking stability. |
| hidden_gems_scatter.html | Satisfaction vs review count for games with at least the selected minimum; candidate colors, log review axis. |
| hidden_gems_top10.html | Top ten candidates ordered by score. |

Susheela can recreate the two Plotly figures in Dash using the CSVs or reuse figure logic in `save_charts`. HTMLs are standalone interactive figures, not a complete Dash app. The module is not yet wired into the team's workflow. Integration order: clean, consolidate, run this module on steam_consolidated.csv, then dashboard/report generation. Include outputs in the workflow artifact if required.

CLI parameters allow exploration without editing the code:

```bash
python scripts/hidden_gems.py samples/steam_sample.csv --max-reviews 1000 --min-satisfaction 95 --output-dir outputs/hidden_gems_alternative
```

## Validation performed

- Shared sample: 90 games, 5 candidates using the proposed default criteria. This is a functionality check, not a market finding. The deliberately selected sample is not representative.
- Synthetic checks: review minimum and maximum boundaries, satisfaction boundary, zero reviews, greater review evidence, empty ranking, duplicate identifiers.
- Input validation rejects invalid review counts, duplicate or missing IDs, inconsistent totals and inconsistent satisfaction percentages.
- Full dataset and GitHub Actions execution of this module have not been verified. The sample contains rounded satisfaction; tolerance is 0.011 percentage points.

Before presentation: run on the agreed complete/consolidated input, examine distributions, compare alternative criteria and top-game overlap, manually check selected candidates, and interpret genre/price alongside Yanghe's output from the same input. A low review count does not establish low awareness or explain its cause. The snapshot cannot establish profitability, causal explanations or future success.

## What Karla should be able to explain

1. Eligibility and ranking are different: rules select candidates, score orders them.
2. Why 2 positive reviews do not provide the same evidence as 190 out of 200.
3. Why no reviews means unknown satisfaction, not zero satisfaction.
4. Why we match Yanghe's minimum while answering a game-level question rather than a segment-level question.
5. Which choices remain provisional and what was tested.

Implementation and initial thresholds were prepared with ChatGPT assistance and require Karla's understanding and team review before final adoption.
