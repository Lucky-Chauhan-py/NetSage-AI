"""
dashboard.py – Plotly chart builders for the NetSage AI Dashboard.

All chart functions take a pandas DataFrame and return a plotly Figure.
Charts use a consistent dark/navy colour palette matching the app theme.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Theme configuration
# ---------------------------------------------------------------------------

CHART_BG = "#0F1117"
PAPER_BG = "#161B22"
FONT_COLOR = "#E6EDF3"
GRID_COLOR = "#30363D"

PALETTE = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#06B6D4", "#F97316", "#EC4899",
    "#84CC16", "#14B8A6",
]

STATUS_COLORS = {
    "Accepted": "#10B981",
    "Edited": "#F59E0B",
    "Rejected": "#EF4444",
}

SEVERITY_COLORS = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#CA8A04",
    "Low": "#16A34A",
    "Info": "#3B82F6",
}


def _base_layout(title: str) -> dict:
    """Return common layout settings for all charts."""
    return dict(
        title=dict(text=title, font=dict(color=FONT_COLOR, size=16)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=FONT_COLOR, family="Inter, sans-serif"),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=GRID_COLOR,
            font=dict(color=FONT_COLOR),
        ),
    )


# ---------------------------------------------------------------------------
# Chart 1: Issue Type Distribution
# ---------------------------------------------------------------------------

def chart_issue_type_distribution(cases_df: pd.DataFrame) -> go.Figure:
    """Bar chart of networking concept tags in the dataset."""
    if cases_df.empty or "concept_tag" not in cases_df.columns:
        return _empty_chart("Issue Type Distribution")

    counts = (
        cases_df["concept_tag"]
        .value_counts()
        .reset_index()
        .rename(columns={"concept_tag": "Tag", "count": "Count"})
    )

    fig = px.bar(
        counts,
        x="Count",
        y="Tag",
        orientation="h",
        color="Count",
        color_continuous_scale=["#1E3A5F", "#3B82F6", "#93C5FD"],
        text="Count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        **_base_layout("Issue Type Distribution"),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title=""),
        yaxis=dict(showgrid=False, title="", autorange="reversed"),
        coloraxis_showscale=False,
        height=450,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 2: OSI Layer Distribution
# ---------------------------------------------------------------------------

def chart_osi_layer_distribution(cases_df: pd.DataFrame) -> go.Figure:
    """Donut chart of OSI layer breakdown."""
    if cases_df.empty or "osi_layer" not in cases_df.columns:
        return _empty_chart("OSI Layer Distribution")

    counts = cases_df["osi_layer"].value_counts()

    fig = go.Figure(
        go.Pie(
            labels=counts.index.tolist(),
            values=counts.values.tolist(),
            hole=0.55,
            marker=dict(colors=PALETTE, line=dict(color=CHART_BG, width=2)),
            textfont=dict(color=FONT_COLOR),
        )
    )
    fig.update_layout(
        **_base_layout("OSI Layer Distribution"),
        height=380,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 3: Severity Distribution
# ---------------------------------------------------------------------------

def chart_severity_distribution(cases_df: pd.DataFrame) -> go.Figure:
    """Pie chart of severity levels in dataset."""
    if cases_df.empty or "severity" not in cases_df.columns:
        return _empty_chart("Severity Distribution")

    counts = cases_df["severity"].value_counts()
    colors = [SEVERITY_COLORS.get(s, "#6B7280") for s in counts.index]

    fig = go.Figure(
        go.Pie(
            labels=counts.index.tolist(),
            values=counts.values.tolist(),
            hole=0.45,
            marker=dict(colors=colors, line=dict(color=CHART_BG, width=2)),
            textfont=dict(color=FONT_COLOR),
        )
    )
    fig.update_layout(
        **_base_layout("Severity Distribution"),
        height=360,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 4: Accepted vs Edited vs Rejected
# ---------------------------------------------------------------------------

def chart_review_status(reviews_df: pd.DataFrame) -> go.Figure:
    """Bar chart of human review outcomes."""
    if reviews_df.empty or "status" not in reviews_df.columns:
        statuses = ["Accepted", "Edited", "Rejected"]
        values = [0, 0, 0]
    else:
        counts = reviews_df["status"].value_counts()
        statuses = list(counts.index)
        values = list(counts.values)

    colors = [STATUS_COLORS.get(s, "#6B7280") for s in statuses]

    fig = go.Figure(
        go.Bar(
            x=statuses,
            y=values,
            marker=dict(color=colors, line=dict(color=CHART_BG, width=1)),
            text=values,
            textposition="outside",
            textfont=dict(color=FONT_COLOR),
        )
    )
    fig.update_layout(
        **_base_layout("Human Review Outcomes"),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title="Count"),
        height=350,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 5: AI Confidence Histogram
# ---------------------------------------------------------------------------

def chart_confidence_histogram(reviews_df: pd.DataFrame) -> go.Figure:
    """Histogram of AI confidence scores from reviewed cases."""
    if reviews_df.empty or "ai_confidence" not in reviews_df.columns:
        return _empty_chart("AI Confidence Distribution")

    conf_values = pd.to_numeric(reviews_df["ai_confidence"], errors="coerce").dropna()

    fig = go.Figure(
        go.Histogram(
            x=conf_values,
            nbinsx=10,
            marker=dict(
                color="#3B82F6",
                line=dict(color=CHART_BG, width=1),
            ),
        )
    )
    fig.update_layout(
        **_base_layout("AI Confidence Score Distribution"),
        xaxis=dict(
            title="Confidence Score (0-100)",
            showgrid=True, gridcolor=GRID_COLOR,
            range=[0, 100],
        ),
        yaxis=dict(title="Count", showgrid=True, gridcolor=GRID_COLOR),
        height=340,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 6: Top Network Problems
# ---------------------------------------------------------------------------

def chart_top_problems(cases_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar of top N concept tags / issues."""
    if cases_df.empty or "concept_tag" not in cases_df.columns:
        return _empty_chart("Top Network Problems")

    top = (
        cases_df["concept_tag"]
        .value_counts()
        .head(10)
        .reset_index()
        .rename(columns={"concept_tag": "Problem", "count": "Frequency"})
    )

    fig = px.bar(
        top,
        x="Frequency",
        y="Problem",
        orientation="h",
        color="Frequency",
        color_continuous_scale=["#1A1F2E", "#6366F1", "#A5B4FC"],
        text="Frequency",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        **_base_layout("Top 10 Network Problems"),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title=""),
        yaxis=dict(showgrid=False, title="", autorange="reversed"),
        coloraxis_showscale=False,
        height=420,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 7: Rule Checker Findings Breakdown
# ---------------------------------------------------------------------------

def chart_rule_findings(findings_list: list[dict]) -> go.Figure:
    """Bar chart of rule checker trigger frequency."""
    if not findings_list:
        return _empty_chart("Rule Checker Findings")

    from collections import Counter
    rule_counts = Counter(f.get("rule_name", "UNKNOWN") for f in findings_list)
    names = list(rule_counts.keys())
    values = list(rule_counts.values())
    colors = [SEVERITY_COLORS.get(
        next((f["severity"] for f in findings_list if f.get("rule_name") == n), "Low"),
        "#6B7280",
    ) for n in names]

    fig = go.Figure(
        go.Bar(
            x=names,
            y=values,
            marker=dict(color=colors, line=dict(color=CHART_BG, width=1)),
            text=values,
            textposition="outside",
            textfont=dict(color=FONT_COLOR),
        )
    )
    fig.update_layout(
        **_base_layout("Rule Checker Findings by Type"),
        xaxis=dict(showgrid=False, title="", tickangle=-35),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title="Triggers"),
        height=380,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 8: Review Timeline (line chart)
# ---------------------------------------------------------------------------

def chart_review_timeline(reviews_df: pd.DataFrame) -> go.Figure:
    """Line chart of review volume over time."""
    if reviews_df.empty or "timestamp" not in reviews_df.columns:
        return _empty_chart("Review Activity Over Time")

    df = reviews_df.copy()
    df["date"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.date
    df = df.dropna(subset=["date"])
    if df.empty:
        return _empty_chart("Review Activity Over Time")

    daily = df.groupby("date").size().reset_index(name="reviews")

    fig = go.Figure(
        go.Scatter(
            x=daily["date"],
            y=daily["reviews"],
            mode="lines+markers",
            line=dict(color="#3B82F6", width=2),
            marker=dict(size=8, color="#60A5FA"),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.15)",
        )
    )
    fig.update_layout(
        **_base_layout("Review Activity Over Time"),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title=""),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, title="Reviews"),
        height=320,
    )
    return fig


# ---------------------------------------------------------------------------
# Gauge chart for AI accuracy
# ---------------------------------------------------------------------------

def chart_ai_accuracy_gauge(accuracy_pct: float) -> go.Figure:
    """Gauge chart showing AI acceptance rate (accuracy)."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=accuracy_pct,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "AI Acceptance Rate", "font": {"color": FONT_COLOR, "size": 14}},
            delta={"reference": 70, "increasing": {"color": "#10B981"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": FONT_COLOR, "tickfont": {"color": FONT_COLOR}},
                "bar": {"color": "#3B82F6"},
                "bgcolor": CHART_BG,
                "steps": [
                    {"range": [0, 40], "color": "#7F1D1D"},
                    {"range": [40, 70], "color": "#92400E"},
                    {"range": [70, 100], "color": "#14532D"},
                ],
                "threshold": {
                    "line": {"color": "#F59E0B", "width": 3},
                    "thickness": 0.8,
                    "value": 70,
                },
            },
            number={"suffix": "%", "font": {"color": FONT_COLOR, "size": 36}},
        )
    )
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


# ---------------------------------------------------------------------------
# Helper: empty placeholder chart
# ---------------------------------------------------------------------------

def _empty_chart(title: str) -> go.Figure:
    """Return a styled empty chart with a 'No data' annotation."""
    fig = go.Figure()
    fig.update_layout(
        **_base_layout(title),
        annotations=[
            dict(
                text="No data available yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(color="#6B7280", size=14),
            )
        ],
        height=300,
    )
    return fig
