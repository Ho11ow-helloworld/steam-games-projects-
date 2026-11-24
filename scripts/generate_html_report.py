
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

if clustered.empty:
    fig_ml = px.scatter(
        title="ML Segmentation: Popularity vs Satisfaction"
    )
    fig_ml.add_annotation(
        text="Not enough eligible games for clustering yet.",
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False
    )

else:
    clustered["ml_cluster"] = clustered["ml_cluster"].astype(int)

    # Describe each cluster using its median characteristics
    profiles = clustered.groupby("ml_cluster")[
        ["price", "total_reviews", "satisfaction_pct"]
    ].median()

    sizes = clustered["ml_cluster"].value_counts()

    def cluster_name(row):
        if row["price"] == 0:
            price = "Free"
        elif row["price"] < 5:
            price = "Budget"
        elif row["price"] < 15:
            price = "Mid-range"
        else:
            price = "Premium"

        popularity = (
            "Popular" if row["total_reviews"] >= 100
            else "Niche"
        )

        if row["satisfaction_pct"] >= 80:
            rating = "High-rated"
        elif row["satisfaction_pct"] >= 60:
            rating = "Mixed"
        else:
            rating = "Low-rated"

        return f"{price} · {popularity} · {rating}"

    names = {
        cid: f"{cluster_name(row)} ({sizes[cid]:,} games)"
        for cid, row in profiles.iterrows()
    }

    clustered["Segment"] = clustered["ml_cluster"].map(names)

    order = [
        names[cid]
        for cid in profiles.sort_values(
            "total_reviews", ascending=False
        ).index
    ]

    palette = [
        "#e67e22", "#5b7db1", "#2ecc71",
        "#9b59b6", "#e74c3c", "#95a5a6"
    ]

    colors = {
        name: palette[i % len(palette)]
        for i, name in enumerate(order)
    }

    # Popularity vs satisfaction
    fig_ml = px.scatter(
        clustered,
        x="total_reviews",
        y="satisfaction_pct",
        color="Segment",
        category_orders={"Segment": order},
        color_discrete_map=colors,
        log_x=True,
        opacity=0.45,
        render_mode="webgl",
        hover_name="name",
        hover_data={
            "price": ":$.2f",
            "total_reviews": ":,",
            "satisfaction_pct": ":.1f",
            "Segment": False
        },
        title="Game Segments found by K-Means: Popularity vs Satisfaction",
        labels={
            "total_reviews": "Number of reviews (log scale)",
            "satisfaction_pct": "Satisfaction (%)",
            "price": "Price"
        }
    )

    fig_ml.update_traces(marker=dict(size=6))
    fig_ml.update_layout(
        height=520,
        legend=dict(title="", orientation="h", y=-0.18)
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
