"""
app/components/charts.py
Reusable Plotly visualization components for the Streamlit dashboard.
"""
from typing import Dict, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_revenue_trend(monthly_df: pd.DataFrame) -> go.Figure:
    """Plot monthly net revenue line/bar trend chart."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_df["year_month"],
        y=monthly_df["total_revenue"],
        name="Monthly Revenue ($)",
        marker_color="#3b82f6",
        opacity=0.85,
    ))
    fig.update_layout(
        title="Monthly Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Net Revenue ($)",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig


def plot_category_sales(cat_df: pd.DataFrame) -> go.Figure:
    """Plot category sales horizontal bar chart."""
    fig = px.bar(
        cat_df.sort_values("revenue", ascending=True),
        x="revenue",
        y="category",
        orientation="h",
        title="Revenue by Category ($)",
        labels={"revenue": "Revenue ($)", "category": "Category"},
        color="revenue",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        coloraxis_showscale=False,
    )
    return fig


def plot_aspect_radar(aspects_summary: pd.DataFrame) -> go.Figure:
    """Plot radar/bar chart of aspect sentiment satisfaction scores."""
    aspect_order = aspects_summary.sort_values("avg_sentiment_score", ascending=True)
    colors = ["#ef4444" if s < 0 else "#10b981" for s in aspect_order["avg_sentiment_score"]]

    fig = go.Figure(go.Bar(
        x=aspect_order["avg_sentiment_score"],
        y=aspect_order["aspect"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title="11-Aspect Sentiment Satisfaction Score (-1.0 to +1.0)",
        xaxis_title="Mean Aspect Sentiment Polarity",
        yaxis_title="Product Aspect",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=380,
    )
    return fig


def plot_segment_distribution(segment_df: pd.DataFrame) -> go.Figure:
    """Plot customer segment donut chart."""
    fig = px.pie(
        segment_df,
        names="customer_segment",
        values="customer_count",
        hole=0.45,
        title="Customer Distribution by Segment",
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig
