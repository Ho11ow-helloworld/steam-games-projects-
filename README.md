# Steam Hidden Gems — Data Science Toolbox

**QM505E — Data Science Toolbox | Group Project**

## 1. Project Overview

**Steam Hidden Gems: Why Do Great Games Go Unnoticed?**

Steam offers thousands of video games, but not all receive the same level of attention. Some games achieve excellent player satisfaction despite having relatively few reviews.

This project uses data analytics and machine learning to identify potentially overlooked games and explore how game genres and pricing relate to player satisfaction.

The objective is to provide useful insights for independent game developers, small studios, and market research teams through an interactive dashboard and an automated data processing pipeline.

### Research Questions

1. **Hidden Gems:** Which games have exceptionally high player satisfaction despite receiving relatively few reviews?
2. **Genre & Pricing:** How do game genres and pricing relate to player satisfaction, and which market segments appear most promising?

## 2. Dataset

The project uses a Kaggle dataset containing **93,182 Steam games**.

It includes:

- Game names and unique identifiers
- Release dates and prices
- Genres
- Positive and negative player reviews
- Estimated ownership ranges
- Concurrent player counts and playtime

The dataset is a historical snapshot from September 2024.

After cleaning the complete dataset locally, **93,179 games** were retained.

### Data Storage Strategy

Due to the large size of the dataset, uploading the entire raw or cleaned CSV file to GitHub is impractical.

As discussed with and accepted by the professor, the project instead demonstrates automated data processing through a batch-based workflow.

Our approach separates data into three categories:

- **Original dataset:** Stored locally and used as the source for batch generation and full-dataset analyses.
- **Full-dataset analysis outputs:** Stored in the repository's `outputs/` directory for the interactive dashboard.
- **Automated batch outputs:** Generated progressively through GitHub Actions and provided as downloadable workflow artifacts.

A smaller cleaned sample is also included in the repository for development and testing.

This organization allows us to demonstrate both complete-dataset analytics and automated incremental processing without storing the entire original dataset on GitHub.

## 3. Project Architecture

The project combines five main components:

1. Data examination and cleaning with Python and pandas.
2. Analytical indicators for Hidden Gems and Genre & Pricing.
3. Machine learning using K-Means clustering.
4. Interactive data visualization with Dash and Plotly.
5. Automated batch processing using GitHub Actions.

### Automated Data Pipeline

```text
Original Steam Dataset (Local)
             |
             v
     BatchSimulator
    (100 games per batch)
             |
             v
          batch.csv
             |
             v
       GitHub Push
             |
             v
       GitHub Actions
             |
             v
       Data Cleaning
             |
             v
     Data Consolidation
    (remove duplicate IDs)
             |
             v
     Indicator Generation
       /      |       \
      v       v        v
 Hidden Gems Genre &   K-Means
             Pricing   Clustering
      \       |        /
       \      |       /
             v
      HTML Report
             |
             v
    GitHub Actions Artifact
```

Each new batch triggers the pipeline, which cleans the incoming data, consolidates it with previously processed data, recalculates the analyses, and generates updated results.

## 4. Data Preparation

**Main scripts:** `scripts/data_exam.py`, `scripts/cleaning.py`

The data preparation stage examines the dataset structure, missing values, duplicates, and numerical distributions.

The cleaning process includes:

- Standardizing column names.
- Removing records with missing game identifiers or names.
- Removing duplicate game identifiers.
- Converting prices and review counts into numerical values.
- Removing invalid or negative numerical values.
- Standardizing release dates.
- Generating analytical indicators.

Two important indicators are calculated:

**Total Reviews**

```python
total_reviews = positive_reviews + negative_reviews
```

**Player Satisfaction**

```python
satisfaction_pct = (
    100 * positive_reviews / total_reviews
)
```

Games without reviews have no calculated satisfaction percentage.

The cleaned dataset is saved separately from the original data.

Further information is available in [data_dictionary.md](data_dictionary.md).

## 5. Data Analytics

### 5.1 Hidden Gems Analysis

**Script:** `scripts/hidden_gems.py`

The first analysis identifies games combining high satisfaction with relatively low review counts.

Our default selection criteria are:

- Between 30 and 500 reviews.
- At least 90% positive reviews.

Eligible games are ranked using the **Wilson Score lower bound**, which considers both satisfaction and the number of reviews.

This approach avoids treating games with very few positive reviews as equally reliable as games with hundreds of positive reviews.

The full cleaned dataset analysis identified **1,071 Hidden Gem candidates**.

The script generates a ranked dataset, an indicator dataset, a sensitivity analysis, and interactive Plotly charts.

See [Hidden Gems documentation](documentation/hidden_gems.md).

### 5.2 Genre & Pricing Analysis

**Script:** `scripts/genre_pricing.py`

The second analysis studies the relationship between genres, pricing, player satisfaction, and market competition.

Games are classified into four price categories:

| Category | Price |
|---|---|
| Free | $0 |
| Budget | Below $5 |
| Mid-range | $5–$14.99 |
| Premium | $15 and above |

The analysis calculates indicators including median satisfaction, number of games, number of rated games, and median review counts.

A market segment is considered promising when it has:

- Above-market player satisfaction.
- Below-median competition.
- At least 30 sufficiently reviewed games.

Median satisfaction is used instead of an overall review-weighted satisfaction score to avoid allowing a few highly popular games to dominate the results.

See [Genre & Pricing documentation](documentation/genre_pricing.md).

## 6. Machine Learning

**Script:** `scripts/ml_clustering.py`

We use **K-Means clustering**, an unsupervised machine learning algorithm, to segment Steam games according to their characteristics.

The model uses four features:

- Price
- Total reviews
- Satisfaction percentage
- Peak concurrent players

Review counts and concurrent player counts are log-transformed, and the features are standardized using `StandardScaler`.

The number of clusters is selected by comparing silhouette scores for candidate values of K between 2 and 6.

The resulting cluster labels provide an additional analytical dimension for identifying different game profiles, such as niche, popular, budget, or premium games.

The clustering output is used for interactive visual comparison.

## 7. Interactive Dashboard

**Script:** `scripts/dashboard.py`

The dashboard is built with Dash and Plotly and is designed to present the results of the full-dataset analysis.

It contains four sections:

| Section | Content |
|---|---|
| Hidden Gems | Ranking of highly rated, less-reviewed games |
| Genre & Pricing | Satisfaction comparisons and promising market segments |
| ML Segmentation | Interactive visualization of game clusters |
| Overview | Key statistics and dataset distributions |

Users can explore results through interactive filters, including genre, price category, and minimum review count.

### Dashboard Data Architecture

The project intentionally maintains two separate sets of analytical outputs:

**1. Full-dataset outputs — `outputs/`**

These files contain analytical results generated from the complete cleaned dataset through local execution.

They are used by the interactive Dash dashboard.

The dashboard reads:

- `outputs/hidden_gems.csv`
- `outputs/genre_price_summary.csv`
- `outputs/ml_clusters.csv`

**2. Automated batch outputs — `outputs/batch/`**

These files are generated separately by the GitHub Actions pipeline after each incoming batch.

They demonstrate how the analytical results are automatically recalculated as the processed dataset grows.

This separation is intentional: the dashboard presents full-dataset analytical results, while the batch workflow demonstrates automated incremental processing.

The two components serve complementary purposes within the project.

## 8. Automated Batch Processing

**Main scripts:**

- `scripts/batch_sim.py`
- `scripts/send_batch.py`
- `scripts/auto_batches.py`
- `scripts/process_batch.py`
- `scripts/consolidate_batches.py`
- `scripts/batch_report.py`
- `scripts/generate_html_report.py`

**GitHub Actions workflow:** `.github/workflows/batch_pipeline.yml`

The purpose of the batch-processing system is to simulate the progressive arrival of new Steam game data.

### 8.1 Batch Generation

The BatchSimulator reads the original dataset locally and generates batches of up to **100 games**.

Each batch is saved as `batch.csv`.

Two local progress files are used:

- `batch_progress.txt`: last confirmed processing position.
- `pending_batch.txt`: position awaiting successful processing.

The simulator does not confirm a batch until its processing has been completed successfully.

### 8.2 GitHub Actions Workflow

The workflow runs automatically when `batch.csv`, the processing scripts, or the workflow configuration are pushed to the `main` branch.

It can also be triggered manually from GitHub Actions.

The workflow performs the following operations:

1. Install the required Python dependencies.
2. Restore the consolidated dataset and batch log from the previous successful workflow artifact, if available.
3. Clean the incoming batch.
4. Consolidate the batch with existing data.
5. Remove duplicate games using `app_id`.
6. Generate data quality indicators and the processing log.
7. Recalculate Hidden Gems, Genre & Pricing, and K-Means results.
8. Generate an interactive HTML report.
9. Upload the updated results as a GitHub Actions artifact.

### 8.3 Automated Batch Execution

The `auto_batches.py` script coordinates the batch process.

It automatically:

1. Creates a new batch.
2. Pushes the batch to GitHub.
3. Waits for the GitHub Actions workflow to complete.
4. Verifies whether the workflow succeeded.
5. Confirms the batch only after successful execution.
6. Repeats the process for the configured number of batches.

The current script is configured to process **three batches per execution**, with a maximum of 100 games per batch.

### 8.4 Validation

During our batch-processing tests, eight successive batches representing 800 source rows were processed.

The tests confirmed that:

- New batches could be sent to GitHub.
- GitHub Actions executed the processing workflow.
- Previously processed results could be consolidated with new data.
- Duplicate game identifiers were removed.
- Analysis results and HTML reports were generated.
- Progress was confirmed after successful workflow execution.

These tests validate the incremental processing mechanism.

The objective is to demonstrate a functioning automated workflow, rather than to upload and process the entire dataset through GitHub at once.

This approach follows the batch-processing requirement accepted by the professor.

## 9. Installation and Execution

### Requirements

- Python 3.11 (the version used by GitHub Actions)
- Git
- Python packages listed in `requirements.txt`

### Installation

Clone the repository:

```bash
git clone https://github.com/Ho11ow-helloworld/steam-games-projects-.git
cd steam-games-projects-
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Run the Analyses Using the Shared Sample

The repository contains `samples/steam_sample.csv`, allowing users to test the analysis scripts without downloading the full dataset.

```bash
python scripts/hidden_gems.py samples/steam_sample.csv --output-dir outputs/sample_test
```

```bash
python scripts/genre_pricing.py samples/steam_sample.csv outputs/sample_test/genre_price_summary.csv
```

```bash
python scripts/ml_clustering.py samples/steam_sample.csv outputs/sample_test/ml_clusters.csv
```

These commands generate sample analysis outputs without replacing the full-dataset results.

### Run the Full Local Analysis

Download the original Kaggle CSV and place it at:

```text
raw_data/93182_steam_games.csv
```

Then execute:

```bash
python scripts/data_exam.py
python scripts/cleaning.py
```

Generate the analytical outputs:

```bash
python scripts/hidden_gems.py cleaned_data/steam_cleaned.csv
python scripts/genre_pricing.py cleaned_data/steam_cleaned.csv
python scripts/ml_clustering.py cleaned_data/steam_cleaned.csv
```

These commands update the corresponding files in `outputs/`.

Start the dashboard:

```bash
python scripts/dashboard.py
```

Open:

`http://127.0.0.1:8050`

### Run the Automated Batch Pipeline

The automated batch script requires the original local CSV, a configured Git remote with push access, the `main` branch checked out, and no previously pending batch.

Run:

```bash
python scripts/auto_batches.py
```

**Important:** This command pushes batches to the remote repository and triggers GitHub Actions. It should only be run when intending to submit new batch data.

The number of batches per execution can be configured using `NUMBER_OF_BATCHES` inside `scripts/auto_batches.py`.

## 10. Generated Outputs

The project produces two complementary types of results.

### 10.1 Full-Dataset Analysis Outputs

The root-level `outputs/` directory contains the results generated through local analysis of the complete cleaned dataset.

These files support the interactive Dash dashboard.

| File | Description |
|---|---|
| `hidden_gems.csv` | Hidden Gems ranking from the full analysis |
| `genre_price_summary.csv` | Genre and pricing indicators |
| `ml_clusters.csv` | K-Means clustering results used by the dashboard |

### 10.2 Automated Batch Outputs

The GitHub Actions workflow generates updated results after each processed batch and uploads an artifact named:

**`steam-batch-results`**

Its contents include:

| File | Description |
|---|---|
| `cleaned_data/steam_batch_cleaned.csv` | Cleaned version of the latest batch |
| `cleaned_data/steam_consolidated.csv` | Consolidated data from processed batches |
| `outputs/data_quality_report.json` | Data quality statistics |
| `outputs/batch_log.csv` | Batch processing history |
| `outputs/batch/hidden_gems.csv` | Updated Hidden Gems ranking |
| `outputs/batch/genre_price_summary.csv` | Updated genre and pricing indicators |
| `outputs/batch/ml_clusters.csv` | Updated K-Means segmentation |
| `outputs/batch/steam_report.html` | Automatically generated interactive HTML report |

To access the automated results:

1. Open the repository's **Actions** tab.
2. Select a successful *Steam Batch Pipeline* run.
3. Download the `steam-batch-results` artifact.

The HTML report can be opened locally in a browser.

The separate output directories allow full-dataset dashboard results and incremental batch-processing results to coexist without overwriting one another.

## 11. Repository Structure

```text
steam-games-projects-/
|
|-- .github/
|   `-- workflows/
|       `-- batch_pipeline.yml
|
|-- raw_data/
|-- cleaned_data/
|-- samples/
|   `-- steam_sample.csv
|
|-- scripts/
|   |-- data_exam.py
|   |-- cleaning.py
|   |-- batch_sim.py
|   |-- send_batch.py
|   |-- auto_batches.py
|   |-- process_batch.py
|   |-- consolidate_batches.py
|   |-- batch_report.py
|   |-- hidden_gems.py
|   |-- genre_pricing.py
|   |-- ml_clustering.py
|   |-- generate_html_report.py
|   `-- dashboard.py
|
|-- outputs/
|   |-- full/
|   `-- [full-dataset analysis files]
|
|-- documentation/
|-- batch.csv
|-- requirements.txt
|-- data_dictionary.md
|-- schema.md
`-- README.md
```

## 12. Limitations

- **Historical dataset:** Findings describe Steam data collected in September 2024, not current market conditions.
- **Review bias:** Player reviews are voluntary and may not represent all customers.
- **Visibility proxy:** A low number of reviews does not necessarily mean a game is commercially unsuccessful or unknown.
- **Market segment interpretation:** Satisfaction and competition indicators highlight potential opportunities but do not establish profitability.
- **Machine learning:** K-Means identifies similarities between games; it does not predict future success.
- **Batch validation:** Eight batches were successfully tested. The complete 93,182-game dataset was not processed through the automated GitHub Actions workflow.
- **Artifact retention:** The automated pipeline depends on previously saved GitHub Actions artifacts. Their availability is subject to GitHub's artifact retention settings.

The separation between full-dataset results and automated batch results is an intentional architectural decision, not a limitation of the project.

## 13. Additional Documentation

More detailed information is available in:

- [Data Dictionary](data_dictionary.md)
- [Project Schema](schema.md)
- [Hidden Gems Analysis](documentation/hidden_gems.md)
- [Genre & Pricing Analysis](documentation/genre_pricing.md)

---

**Rennes School of Business — Master in Business Data Analytics**

*QM505E — Data Science Toolbox Group Project, Academic Year 2026–2027*

**Dataset:** https://www.kaggle.com/datasets/joebeachcapital/top-1000-steam-games
