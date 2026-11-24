
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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


# 2 & 3. Genre & Pricing Analysis
# Same rules and visualizations as the final dashboard

PRICE_ORDER = ["Free", "Budget", "Mid-range", "Premium"]
PRICE_DISPLAY = {
    "Free": "Free ($0)",
    "Budget": "Budget (< $5)",
    "Mid-range": "Mid-range ($5-14.99)",
    "Premium": "Premium (>= $15)"
}
MIN_RATED_GAMES = 30

gp = genres.copy()
overall = gp[
    (gp["genre"] == "All") &
    (gp["price_category"] == "All")
]

market = float(overall["median_satisfaction_pct"].iloc[0])

# A. Median satisfaction by genre
by_genre = gp[
    (gp["genre"] != "All") &
    (gp["price_category"] == "All")
].dropna(subset=["median_satisfaction_pct"]).copy()

by_genre = by_genre.sort_values("median_satisfaction_pct")

fig_genre = px.bar(
    by_genre,
    x="median_satisfaction_pct",
    y="genre",
    orientation="h",
    title="Median Satisfaction by Genre",
    color="satisfaction_gap",
    color_continuous_scale="RdYlGn",
    color_continuous_midpoint=0,
    text="median_satisfaction_pct",
    labels={
        "median_satisfaction_pct": "Median satisfaction (%)",
        "genre": ""
    }
)

fig_genre.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig_genre.add_vline(
    x=market,
    line_dash="dash",
    line_color="grey",
    annotation_text=f"Market {market:.1f}%"
)

if not by_genre.empty:
    fig_genre.update_xaxes(
        range=[
            min(by_genre["median_satisfaction_pct"].min(), market) - 3,
            max(by_genre["median_satisfaction_pct"].max(), market) + 4
        ]
    )

fig_genre.update_layout(
    height=450,
    coloraxis_showscale=False,
    margin=dict(t=80)
)

# B. Median satisfaction by price category
by_price = gp[
    (gp["genre"] == "All") &
    (gp["price_category"].isin(PRICE_ORDER))
].dropna(subset=["median_satisfaction_pct"]).copy()

by_price["order"] = by_price["price_category"].map(
    {name: i for i, name in enumerate(PRICE_ORDER)}
)

by_price = by_price.sort_values("order")
by_price["price_label"] = by_price["price_category"].map(PRICE_DISPLAY)

fig_price = px.bar(
    by_price,
    x="price_label",
    y="median_satisfaction_pct",
    color="price_category",
    category_orders={"price_label": [
        PRICE_DISPLAY[p] for p in PRICE_ORDER
    ]},
    color_discrete_map={
        "Free": "#2ecc71",
        "Budget": "#3498db",
        "Mid-range": "#f39c12",
        "Premium": "#e74c3c"
    },
    text="median_satisfaction_pct",
    title="Median Satisfaction by Price Category",
    labels={
        "median_satisfaction_pct": "Median satisfaction (%)",
        "price_label": ""
    }
)

fig_price.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig_price.add_hline(
    y=market,
    line_dash="dash",
    line_color="grey",
    annotation_text=f"Market {market:.1f}%"
)

if not by_price.empty:
    fig_price.update_yaxes(
        range=[
            min(by_price["median_satisfaction_pct"].min(), market) - 3,
            max(by_price["median_satisfaction_pct"].max(), market) + 3
        ]
    )

fig_price.update_layout(
    showlegend=False,
    height=450,
    margin=dict(t=80)
)

# C. Satisfaction vs competition
seg = gp[
    (gp["genre"] != "All") &
    (gp["price_category"] != "All")
].dropna(subset=["median_satisfaction_pct"]).copy()

seg = seg[seg["n_games"] > 0].copy()
seg["segment"] = seg["genre"] + " - " + seg["price_category"]

reliable = seg["n_rated_games"] >= MIN_RATED_GAMES

promising = (
    seg["is_promising"].astype(str).str.lower().eq("true")
    & reliable
)

seg["status"] = "Other segments"
seg.loc[~reliable, "status"] = "Insufficient rated games"
seg.loc[promising, "status"] = "Promising"

competition_median = seg.loc[reliable, "n_games"].median()

fig_comp = go.Figure()

styles = {
    "Insufficient rated games": ("#cccccc", 8),
    "Other segments": ("#5b7db1", 10),
    "Promising": ("#e67e22", 14)
}

for status, (color, size) in styles.items():
    part = seg[seg["status"] == status]

    if part.empty:
        continue

    fig_comp.add_trace(go.Scatter(
        x=part["n_games"],
        y=part["median_satisfaction_pct"],
        mode="markers+text" if status == "Promising" else "markers",
        name=status,
        text=part["segment"],
        textposition="top center",
        marker=dict(
            color=color,
            size=size
        ),
        customdata=part[["n_rated_games", "satisfaction_gap"]],
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Competing games: %{x:,}<br>"
            "Satisfaction: %{y:.1f}%<br>"
            "vs market: %{customdata[1]:+.1f} pts<br>"
            "Rated games: %{customdata[0]}"
            "<extra></extra>"
        )
    ))

fig_comp.add_hline(
    y=market,
    line_dash="dash",
    line_color="grey",
    annotation_text=f"Market satisfaction {market:.1f}%"
)

if pd.notna(competition_median) and competition_median > 0:
    fig_comp.add_vline(
        x=competition_median,
        line_dash="dash",
        line_color="grey"
    )

fig_comp.update_layout(
    title="Satisfaction vs Competition by Segment (Genre x Price)",
    xaxis=dict(
        title="Number of competing games (log scale)",
        type="log"
    ),
    yaxis=dict(title="Median satisfaction (%)"),
    legend=dict(orientation="h", y=-0.2),
    height=520
)

# D. Promising segments table
top = seg[
    seg["status"] == "Promising"
].sort_values("satisfaction_gap", ascending=False)

if not top.empty:
    table = pd.DataFrame({
        "Segment": top["segment"],
        "Satisfaction (%)": top["median_satisfaction_pct"].round(1),
        "vs market (pts)": top["satisfaction_gap"].map(
            lambda v: f"{v:+.1f}"
        ),
        "Competing games": top["n_games"].astype(int),
        "Rated games": top["n_rated_games"].astype(int),
        "Median reviews": top["median_total_reviews"].round(0)
    })

    promising_table_html = (
        "<h2>Promising Segments</h2>"
        + table.to_html(index=False, border=0, classes="results-table")
    )
else:
    promising_table_html = (
        "<h2>Promising Segments</h2>"
        "<p>No segments meet the reliability and opportunity "
        "criteria in the current batch dataset.</p>"
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
figures = [fig_gems, fig_genre, fig_price, fig_comp, fig_ml]

charts = ""

for i, fig in enumerate(figures):
    charts += fig.to_html(
        full_html=False,
        include_plotlyjs=(i == 0)
    )

    if i == 3:
        charts += promising_table_html


# 5. Data Quality and Automated Insights

total_games = len(games)

quality_checks = {
    "Duplicate game IDs": int(games["app_id"].duplicated().sum()),
    "Missing game names": int(games["name"].isna().sum()),
    "Missing genres": int(games["genres"].isna().sum()),
    "Missing release dates": int(games["release_date"].isna().sum()),
    "Games without reviews": int((games["total_reviews"] == 0).sum())
}

quality_rows = ""

for name, count in quality_checks.items():
    percentage = (count / total_games * 100) if total_games else 0

    quality_rows += (
        f"<tr><td>{name}</td>"
        f"<td>{count:,}</td>"
        f"<td>{percentage:.1f}%</td></tr>"
    )

quality_html = f"""
<h2>Data Quality Summary</h2>
<p>Quality checks on {total_games:,} consolidated batch games.</p>
<table class="results-table">
    <tr>
        <th>Quality Indicator</th>
        <th>Count</th>
        <th>Percentage</th>
    </tr>
    {quality_rows}
</table>
"""

# Automatically summarize the current analysis results
insights = [
    f"{total_games:,} games have been consolidated from processed batches.",
    f"{len(gems):,} Hidden Gem candidates were identified.",
    f"{len(clustered):,} games were assigned to K-Means clusters.",
]

if pd.notna(market):
    insights.append(
        f"Overall median player satisfaction is {market:.1f}% "
        "among games with at least 30 reviews."
    )

if top.empty:
    insights.append(
        "No genre-price segments currently satisfy both the "
        "reliability and opportunity criteria."
    )
else:
    insights.append(
        f"{len(top)} promising genre-price segments were identified."
    )

# Detect outdated clustering results
outdated_ml = int((clustered["total_reviews"] < 30).sum())

if outdated_ml > 0:
    insights.append(
        f"WARNING: {outdated_ml} clustered games have fewer "
        "than 30 reviews. Regenerate the ML results."
    )

insights.append(
    "These findings describe the consolidated batch dataset, "
    "not the complete Steam dataset."
)

insights_html = (
    "<h2>Automated Insights</h2><ul>"
    + "".join(f"<li>{item}</li>" for item in insights)
    + "</ul>"
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

        .results-table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}

        .results-table th,
        .results-table td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}

        .results-table th {{
            background: #1b2838;
            color: white;
        }}
    </style>

</head>
<body>
    <h1>Steam Hidden Gems - Automated Report</h1>
    <div class="summary">
        <p>Total games: {len(games):,}</p>
        <p>Hidden Gem candidates: {len(gems):,}</p>
        <p>ML clustered games: {len(clustered):,}</p>
   
    </div>

    {quality_html}

    {charts}

    {insights_html}
</body>

</html>
"""

report_path = OUTPUTS / "steam_report.html"
report_path.write_text(html, encoding="utf-8")

print("HTML report created:", report_path)
print("Games included:", len(games))
