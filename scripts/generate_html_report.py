
from pathlib import Path
import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs" / "batch"

# Load consolidated data and analysis results
games = pd.read_csv(ROOT / "cleaned_data" / "steam_consolidated.csv")
gems = pd.read_csv(OUTPUTS / "hidden_gems.csv")
genres = pd.read_csv(OUTPUTS / "genre_price_summary.csv")
ml = pd.read_csv(OUTPUTS / "ml_clusters.csv")

# 1. Hidden Gems ranking
top_gems = gems.head(10).sort_values("hidden_gem_score")
fig_gems = px.bar(
    top_gems, x="hidden_gem_score", y="name",
    orientation="h", title="Top 10 Hidden Gems"
)

# 2. Genre analysis
by_genre = genres[
    (genres["genre"] != "All") &
    (genres["price_category"] == "All")
]
fig_genre = px.bar(
    by_genre, x="genre", y="median_satisfaction_pct",
    title="Median Satisfaction by Genre"
)

# 3. Pricing analysis
by_price = genres[
    (genres["genre"] == "All") &
    (genres["price_category"] != "All")
]
fig_price = px.bar(
    by_price, x="price_category", y="median_satisfaction_pct",
    title="Median Satisfaction by Price Category"
)

# 4. Machine Learning segmentation
clustered = ml.dropna(subset=["ml_cluster"]).copy()
clustered["ml_cluster"] = clustered["ml_cluster"].astype(int).astype(str)

fig_ml = px.scatter(
    clustered, x="price", y="satisfaction_pct",
    color="ml_cluster", hover_name="name",
    title="ML Segmentation: Price vs Satisfaction"
)

# Combine interactive charts in one HTML report
figures = [fig_gems, fig_genre, fig_price, fig_ml]
charts = ""

for i, fig in enumerate(figures):
    charts += fig.to_html(
        full_html=False,
        include_plotlyjs=(i == 0)
    )

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Steam Games - Automated Report</title>
    <style>
        body {{ font-family: Arial; margin: 40px; }}
        h1 {{ color: #1b2838; }}
        .summary {{ padding: 15px; background: #eef2f7; }}
    </style>
</head>
<body>
    <h1>Steam Hidden Gems - Automated Report</h1>
    <div class="summary">
        <p>Total games: {len(games):,}</p>
        <p>Hidden Gem candidates: {len(gems):,}</p>
        <p>ML clustered games: {len(clustered):,}</p>
    </div>
    {charts}
</body>
</html>
"""

report_path = OUTPUTS / "steam_report.html"
report_path.write_text(html, encoding="utf-8")

print("HTML report created:", report_path)
print("Games included:", len(games))
