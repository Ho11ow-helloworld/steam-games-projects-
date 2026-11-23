"""
Member 4 — Dash Dashboard

Reads the output files produced by the pipeline and displays them
in an interactive dashboard for business analysis.

Input files (all in outputs/):
    - ml_clusters.csv        (from ml_clustering.py)
    - hidden_gems.csv        (from Member 2)
    - genre_price_summary.csv (from genre_pricing.py)

Run:
    pip install dash plotly pandas
    python scripts/dashboard.py

Then open http://127.0.0.1:8050 in your browser.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, dash_table, Input, Output

# ── paths ────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"
SAMPLES = ROOT / "samples"


# ── data loading ─────────────────────────────────────────────────────
def load_csv(name, fallback_dir=None):
    """Load from outputs/, falling back to samples/ for development."""
    path = OUTPUTS / name
    if path.exists():
        return pd.read_csv(path)
    if fallback_dir:
        alt = fallback_dir / name
        if alt.exists():
            return pd.read_csv(alt)
    print(f"Warning: {name} not found, using empty DataFrame.")
    return pd.DataFrame()


def load_all_data():
    """Load all datasets needed by the dashboard."""
    # ML clusters — also used as the main games table
    ml = load_csv("ml_clusters.csv")
    if ml.empty:
        # Fall back to sample data for development
        sample_path = SAMPLES / "steam_sample.csv"
        if sample_path.exists():
            ml = pd.read_csv(sample_path)
            ml["ml_cluster"] = None
            print("Using steam_sample.csv as fallback (no ml_clusters.csv yet).")

    # Hidden gems
    gems = load_csv("hidden_gems.csv")

    # Genre & pricing summary
    genre_price = load_csv("genre_price_summary.csv")

    return ml, gems, genre_price


ml_df, gems_df, gp_df = load_all_data()

# ── derived values for filters ───────────────────────────────────────
all_genres = set()
if "genres" in ml_df.columns:
    for g in ml_df["genres"].dropna():
        for genre in str(g).split(","):
            genre = genre.strip()
            if genre:
                all_genres.add(genre)
all_genres = sorted(all_genres)

# ── app ──────────────────────────────────────────────────────────────
app = Dash(__name__)
app.title = "Steam Hidden Gems Dashboard"

# ── layout ───────────────────────────────────────────────────────────
app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "margin": "20px", "maxWidth": "1200px", "marginLeft": "auto", "marginRight": "auto"},
    children=[
        # Header
        html.H1("🎮 Steam Hidden Gems Dashboard", style={"textAlign": "center", "color": "#1b2838"}),
        html.P(
            "Interactive analysis of Steam games: hidden gems, genre & pricing insights, and ML segmentation.",
            style={"textAlign": "center", "color": "#666", "marginBottom": "30px"},
        ),

        # ── Filters ──────────────────────────────────────────────
        html.Div(
            style={"backgroundColor": "#f0f0f0", "padding": "15px", "borderRadius": "8px", "marginBottom": "25px"},
            children=[
                html.H3("Filters", style={"marginTop": "0"}),
                html.Div(
                    style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
                    children=[
                        html.Div([
                            html.Label("Genre:"),
                            dcc.Dropdown(
                                id="filter-genre",
                                options=[{"label": "All", "value": "All"}] + [{"label": g, "value": g} for g in all_genres],
                                value="All",
                                clearable=False,
                                style={"width": "200px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Price category:"),
                            dcc.Dropdown(
                                id="filter-price",
                                options=[
                                    {"label": "All", "value": "All"},
                                    {"label": "Free", "value": "Free"},
                                    {"label": "Budget (< $5)", "value": "Budget"},
                                    {"label": "Mid-range ($5–$15)", "value": "Mid-range"},
                                    {"label": "Premium (> $15)", "value": "Premium"},
                                ],
                                value="All",
                                clearable=False,
                                style={"width": "200px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Min reviews:"),
                            dcc.Input(
                                id="filter-min-reviews",
                                type="number",
                                value=0,
                                min=0,
                                style={"width": "100px"},
                            ),
                        ]),
                    ],
                ),
            ],
        ),

        # ── Tab layout ───────────────────────────────────────────
        dcc.Tabs(
            id="tabs",
            value="tab-gems",
            children=[
                dcc.Tab(label="🏆 Hidden Gems", value="tab-gems"),
                dcc.Tab(label="📊 Genre & Pricing", value="tab-genre"),
                dcc.Tab(label="🤖 ML Segmentation", value="tab-ml"),
                dcc.Tab(label="📈 Overview", value="tab-overview"),
            ],
        ),

        html.Div(id="tab-content", style={"marginTop": "20px"}),
    ],
)


# ── helpers ──────────────────────────────────────────────────────────
PRICE_BINS = [-0.01, 0, 4.99, 14.99, float("inf")]
PRICE_LABELS = ["Free", "Budget", "Mid-range", "Premium"]


def add_price_category(df):
    if "price" in df.columns and "price_category" not in df.columns:
        df = df.copy()
        df["price_category"] = pd.cut(df["price"], bins=PRICE_BINS, labels=PRICE_LABELS).astype(str)
    return df


def apply_filters(df, genre, price_cat, min_reviews):
    df = add_price_category(df)
    if genre != "All" and "genres" in df.columns:
        df = df[df["genres"].fillna("").str.contains(genre, case=False)]
    if price_cat != "All" and "price_category" in df.columns:
        df = df[df["price_category"] == price_cat]
    if "total_reviews" in df.columns:
        df = df[df["total_reviews"] >= (min_reviews or 0)]
    return df


# ── callbacks ────────────────────────────────────────────────────────
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("filter-genre", "value"),
    Input("filter-price", "value"),
    Input("filter-min-reviews", "value"),
)
def render_tab(tab, genre, price_cat, min_reviews):
    if tab == "tab-gems":
        return render_gems_tab(genre, price_cat, min_reviews)
    elif tab == "tab-genre":
        return render_genre_tab()
    elif tab == "tab-ml":
        return render_ml_tab(genre, price_cat, min_reviews)
    elif tab == "tab-overview":
        return render_overview_tab(genre, price_cat, min_reviews)
    return html.P("Select a tab.")


def render_gems_tab(genre, price_cat, min_reviews):
    if gems_df.empty:
        return html.Div([
            html.H3("Hidden Gems Ranking"),
            html.P("⏳ Waiting for hidden_gems.csv from Member 2. "
                    "Place it in the outputs/ folder and refresh."),
        ])

    df = apply_filters(gems_df, genre, price_cat, min_reviews)
    display_cols = [c for c in ["name", "hidden_gem_score", "satisfaction_pct",
                                "total_reviews", "price", "genres"] if c in df.columns]

    return html.Div([
        html.H3(f"Hidden Gems Ranking ({len(df)} games)"),
        dash_table.DataTable(
            data=df[display_cols].head(20).to_dict("records"),
             columns=[
                {
                    "name": c,
                    "id": c,
                    "type": "numeric",
                    "format": {"specifier": ".2f"},
                }
                if c == "hidden_gem_score"
                else {"name": c, "id": c}
                for c in display_cols
            ],
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px", "fontSize": "13px"},
            style_header={"backgroundColor": "#1b2838", "color": "white", "fontWeight": "bold"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
            ],
        ),
    ])


PRICE_ORDER = ["Free", "Budget", "Mid-range", "Premium"]
PRICE_DISPLAY = {
    "Free": "Free ($0)",
    "Budget": "Budget (< $5)",
    "Mid-range": "Mid-range ($5–14.99)",
    "Premium": "Premium (≥ $15)",
}
MIN_RATED_GAMES = 30  # same rule as genre_pricing.py: fewer rated games = not reliable


def render_genre_tab():
    import math

    if gp_df.empty:
        return html.Div([
            html.H3("Genre & Pricing Analysis"),
            html.P("⏳ Waiting for genre_price_summary.csv. "
                    "Run genre_pricing.py and refresh."),
        ])

    gp = gp_df.copy()
    overall = gp[(gp["genre"] == "All") & (gp["price_category"] == "All")]
    market = float(overall["median_satisfaction_pct"].iloc[0]) if not overall.empty \
        else float(gp["median_satisfaction_pct"].median())

    # 1. Satisfaction by genre (axis zoomed on the real range, market line)
    by_genre = gp[(gp["genre"] != "All") & (gp["price_category"] == "All")].copy()
    by_genre = by_genre.sort_values("median_satisfaction_pct", ascending=True)
    low = min(by_genre["median_satisfaction_pct"].min(), market) - 3
    high = max(by_genre["median_satisfaction_pct"].max(), market) + 4

    fig_genre = px.bar(
        by_genre, x="median_satisfaction_pct", y="genre",
        orientation="h",
        title="Median Satisfaction by Genre",
        labels={"median_satisfaction_pct": "Median satisfaction (%)", "genre": ""},
        color="satisfaction_gap",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        text="median_satisfaction_pct",
    )
    fig_genre.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_genre.add_vline(x=market, line_dash="dash", line_color="grey",
                        annotation_text=f"Market {market:.1f}%", annotation_position="top")
    fig_genre.update_layout(xaxis_range=[low, high], coloraxis_showscale=False, height=420,
                            margin=dict(t=80))

    # 2. Satisfaction by price category, cheapest to most expensive
    by_price = gp[(gp["genre"] == "All") & (gp["price_category"].isin(PRICE_ORDER))].copy()
    by_price["order"] = by_price["price_category"].map(PRICE_ORDER.index)
    by_price = by_price.sort_values("order")
    by_price["price_label"] = by_price["price_category"].map(PRICE_DISPLAY)
    low = min(by_price["median_satisfaction_pct"].min(), market) - 3
    high = max(by_price["median_satisfaction_pct"].max(), market) + 3

    fig_price = px.bar(
        by_price, x="price_label", y="median_satisfaction_pct",
        title="Median Satisfaction by Price Category",
        labels={"median_satisfaction_pct": "Median satisfaction (%)", "price_label": ""},
        color="price_category",
        color_discrete_map={"Free": "#2ecc71", "Budget": "#3498db", "Mid-range": "#f39c12", "Premium": "#e74c3c"},
        text="median_satisfaction_pct",
    )
    fig_price.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_price.add_hline(y=market, line_dash="dash", line_color="grey",
                        annotation_text=f"Market {market:.1f}%", annotation_position="top left")
    fig_price.update_layout(yaxis_range=[low, high], showlegend=False, height=420,
                            margin=dict(t=80))

    # 3. Satisfaction vs competition: one dot per genre x price segment
    seg = gp[(gp["genre"] != "All") & (gp["price_category"] != "All")].copy()
    seg = seg.dropna(subset=["median_satisfaction_pct"])
    seg = seg[seg["n_games"] > 0]
    seg["segment"] = seg["genre"] + " – " + seg["price_category"]
    reliable = seg["n_rated_games"] >= MIN_RATED_GAMES
    promising = seg["is_promising"].astype(str).str.lower() == "true" if "is_promising" in seg.columns \
        else pd.Series(False, index=seg.index)
    seg["status"] = "Other segments"
    seg.loc[~reliable, "status"] = f"Fewer than {MIN_RATED_GAMES} rated games (not reliable)"
    seg.loc[promising, "status"] = "Promising"
    competition_median = seg.loc[reliable, "n_games"].median()

    fig_quad = go.Figure()
    styles = {
        f"Fewer than {MIN_RATED_GAMES} rated games (not reliable)": ("#cccccc", 9, "markers"),
        "Other segments": ("#5b7db1", 10, "markers"),
        "Promising": ("#e67e22", 15, "markers+text"),
    }
    label_position = {
        "Adventure – Premium": "top left",
        "Casual – Premium": "bottom center",
        "Racing – Mid-range": "bottom center",
    }
    for status, (color, size, mode) in styles.items():
        part = seg[seg["status"] == status]
        if part.empty:
            continue
        fig_quad.add_trace(go.Scatter(
            x=part["n_games"], y=part["median_satisfaction_pct"],
            mode=mode, name=status,
            text=part["segment"],
            textposition=[label_position.get(name, "top center") for name in part["segment"]],
            marker=dict(color=color, size=size, line=dict(width=1, color="white")),
            customdata=part[["n_rated_games", "satisfaction_gap"]],
            hovertemplate="<b>%{text}</b><br>Games competing: %{x:,}"
                          "<br>Satisfaction: %{y:.1f}%<br>vs market: %{customdata[1]:+.1f} pts"
                          "<br>Rated games: %{customdata[0]}<extra></extra>",
        ))
    fig_quad.add_hline(y=market, line_dash="dash", line_color="grey",
                       annotation_text=f"Market satisfaction {market:.1f}%",
                       annotation_position="bottom right")
    if pd.notna(competition_median):
        fig_quad.add_vline(x=competition_median, line_dash="dash", line_color="grey")
        fig_quad.add_annotation(
            x=math.log10(competition_median), y=0.01, xref="x", yref="paper", showarrow=False,
            text=f"Median competition: {competition_median:,.0f} games",
            font=dict(color="grey"), xanchor="left", yanchor="bottom",
        )
    fig_quad.add_annotation(
        x=0.01, y=0.01, xref="paper", yref="paper", showarrow=False,
        text="<b>Opportunity zone = top-left</b><br>more satisfied players, fewer competitors",
        align="left", font=dict(color="#e67e22"), xanchor="left", yanchor="bottom",
    )
    fig_quad.update_layout(
        title="Satisfaction vs Competition by Segment (genre × price)",
        xaxis=dict(title="Number of competing games (log scale)", type="log"),
        yaxis=dict(title="Median satisfaction (%)"),
        legend=dict(orientation="h", y=-0.2),
        height=520,
    )

    children = [
        html.H3("Genre & Pricing Analysis"),
        html.Div(style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}, children=[
            html.Div(dcc.Graph(figure=fig_genre), style={"flex": "1", "minWidth": "400px"}),
            html.Div(dcc.Graph(figure=fig_price), style={"flex": "1", "minWidth": "400px"}),
        ]),
        dcc.Graph(figure=fig_quad),
    ]

    # 4. Promising segments table: readable names, best first
    top = seg[seg["status"] == "Promising"].sort_values("satisfaction_gap", ascending=False)
    if not top.empty:
        table = pd.DataFrame({
            "Segment": top["segment"],
            "Satisfaction (%)": top["median_satisfaction_pct"].round(1),
            "vs market (pts)": top["satisfaction_gap"].map(lambda v: f"{v:+.1f}"),
            "Games competing": top["n_games"].map(lambda v: f"{int(v):,}"),
            f"Games with ≥ {MIN_RATED_GAMES} reviews": top["n_rated_games"].astype(int),
            "Median reviews": top["median_total_reviews"].round(0).astype(int),
        })
        children.append(html.H4("🌟 Promising Segments (more satisfied players, fewer competitors)"))
        children.append(
            dash_table.DataTable(
                data=table.to_dict("records"),
                columns=[{"name": c, "id": c} for c in table.columns],
                style_cell={"textAlign": "left", "padding": "8px", "fontSize": "13px"},
                style_header={"backgroundColor": "#1b2838", "color": "white", "fontWeight": "bold"},
            )
        )

    return html.Div(children)


def render_ml_tab(genre, price_cat, min_reviews):
    if ml_df.empty or "ml_cluster" not in ml_df.columns:
        return html.Div([
            html.H3("ML Segmentation"),
            html.P("⏳ Run ml_clustering.py first to generate clusters."),
        ])

    df = apply_filters(ml_df, genre, price_cat, min_reviews)
    clustered = df.dropna(subset=["ml_cluster"]).copy()
    clustered["ml_cluster"] = clustered["ml_cluster"].astype(int).astype(str)

    if clustered.empty:
        return html.Div([
            html.H3("ML Segmentation"),
            html.P("No clustered games match the current filters."),
        ])

    # Scatter: price vs satisfaction, colored by cluster
    fig_scatter = px.scatter(
        clustered, x="price", y="satisfaction_pct",
        color="ml_cluster",
        size="total_reviews",
        hover_name="name" if "name" in clustered.columns else None,
        title="Game Segments: Price vs Satisfaction",
        labels={
            "price": "Price ($)",
            "satisfaction_pct": "Satisfaction (%)",
            "ml_cluster": "Cluster",
            "total_reviews": "Total Reviews",
        },
    )
    fig_scatter.update_layout(height=500)

    # Cluster profile table
    profile_cols = ["price", "total_reviews", "satisfaction_pct", "peak_ccu"]
    available = [c for c in profile_cols if c in clustered.columns]
    profile = clustered.groupby("ml_cluster")[available].median().round(2).reset_index()
    profile.columns = ["Cluster"] + [f"Median {c}" for c in available]

    # Cluster size bar chart
    sizes = clustered["ml_cluster"].value_counts().reset_index()
    sizes.columns = ["Cluster", "Games"]
    fig_sizes = px.bar(
        sizes, x="Cluster", y="Games",
        title="Games per Cluster",
        color="Cluster",
    )
    fig_sizes.update_layout(showlegend=False, height=300)

    return html.Div([
        html.H3(f"ML Segmentation ({len(clustered)} clustered games)"),
        dcc.Graph(figure=fig_scatter),
        html.Div(style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}, children=[
            html.Div([
                html.H4("Cluster Profiles (Medians)"),
                dash_table.DataTable(
                    data=profile.to_dict("records"),
                    columns=[{"name": c, "id": c} for c in profile.columns],
                    style_cell={"textAlign": "center", "padding": "8px", "fontSize": "13px"},
                    style_header={"backgroundColor": "#1b2838", "color": "white", "fontWeight": "bold"},
                ),
            ], style={"flex": "1", "minWidth": "350px"}),
            html.Div(dcc.Graph(figure=fig_sizes), style={"flex": "1", "minWidth": "350px"}),
        ]),
    ])


def render_overview_tab(genre, price_cat, min_reviews):
    df = apply_filters(ml_df, genre, price_cat, min_reviews) if not ml_df.empty else pd.DataFrame()

    if df.empty:
        return html.P("No data available.")

    total = len(df)
    with_reviews = (df["total_reviews"] > 0).sum() if "total_reviews" in df.columns else 0
    avg_price = df["price"].mean() if "price" in df.columns else 0
    avg_sat = df.loc[df["total_reviews"] > 0, "satisfaction_pct"].mean() if "satisfaction_pct" in df.columns else 0

    # KPI cards
    kpis = html.Div(
        style={"display": "flex", "gap": "15px", "flexWrap": "wrap", "marginBottom": "20px"},
        children=[
            _kpi_card("Total Games", f"{total:,}"),
            _kpi_card("With Reviews", f"{with_reviews:,}"),
            _kpi_card("Avg Price", f"${avg_price:.2f}"),
            _kpi_card("Avg Satisfaction", f"{avg_sat:.1f}%"),
        ],
    )

    # Review distribution
    reviewed = df[df["total_reviews"] > 0].copy() if "total_reviews" in df.columns else pd.DataFrame()
    charts = []
    if not reviewed.empty:
        import numpy as np
        reviewed["log_reviews"] = np.log1p(reviewed["total_reviews"])
        fig_hist = px.histogram(
            reviewed, x="log_reviews", nbins=30,
            title="Distribution of Reviews (log scale)",
            labels={"log_reviews": "log(1 + total_reviews)"},
        )
        fig_hist.update_layout(height=350)
        charts.append(dcc.Graph(figure=fig_hist))

    # Satisfaction distribution
    if "satisfaction_pct" in reviewed.columns:
        fig_sat = px.histogram(
            reviewed, x="satisfaction_pct", nbins=20,
            title="Satisfaction Distribution (games with reviews)",
            labels={"satisfaction_pct": "Satisfaction (%)"},
        )
        fig_sat.update_layout(height=350)
        charts.append(dcc.Graph(figure=fig_sat))

    return html.Div([
        html.H3("Dataset Overview"),
        kpis,
        html.Div(style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
                 children=[html.Div(c, style={"flex": "1", "minWidth": "400px"}) for c in charts]),
    ])


def _kpi_card(title, value):
    return html.Div(
        style={
            "backgroundColor": "#1b2838", "color": "white", "padding": "20px",
            "borderRadius": "8px", "textAlign": "center", "flex": "1", "minWidth": "150px",
        },
        children=[
            html.H4(title, style={"margin": "0", "color": "#aaa", "fontSize": "14px"}),
            html.P(value, style={"margin": "5px 0 0", "fontSize": "24px", "fontWeight": "bold"}),
        ],
    )


# ── run ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Starting dashboard at http://127.0.0.1:8050")
    print("Press Ctrl+C to stop.\n")
    app.run(debug=True, host="127.0.0.1", port=8050)
