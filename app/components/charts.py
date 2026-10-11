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
    x_col = "year_month" if "year_month" in monthly_df.columns else monthly_df.columns[0]
    y_col = "total_revenue" if "total_revenue" in monthly_df.columns else (
        "revenue" if "revenue" in monthly_df.columns else monthly_df.columns[1]
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_df[x_col],
        y=monthly_df[y_col],
        name="Monthly Revenue ($)",
        marker_color="#3b82f6",
        opacity=0.85,
    ))
    fig.update_layout(
        title="Revenue Trend Over Time",
        xaxis_title=x_col.replace("_", " ").title(),
        yaxis_title="Revenue ($)",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig


def plot_category_sales(cat_df: pd.DataFrame) -> go.Figure:
    """Plot category sales horizontal bar chart supporting dynamic category and revenue column names."""
    df_copy = cat_df.copy()
    cat_cols = [c for c in df_copy.columns if c not in ["revenue", "orders", "share_pct"]]
    cat_col = cat_cols[0] if cat_cols else "category"
    if cat_col not in df_copy.columns:
        df_copy["category"] = df_copy.iloc[:, 0].astype(str)
        cat_col = "category"

    rev_col = "revenue" if "revenue" in df_copy.columns else df_copy.columns[1]

    fig = px.bar(
        df_copy.sort_values(rev_col, ascending=True),
        x=rev_col,
        y=cat_col,
        orientation="h",
        title=f"Revenue by {cat_col.replace('_', ' ').title()} ($)",
        labels={rev_col: "Revenue ($)", cat_col: cat_col.replace('_', ' ').title()},
        color=rev_col,
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
    col_name = "customer_segment" if "customer_segment" in segment_df.columns else "segment"
    val_name = "customer_count" if "customer_count" in segment_df.columns else "count"
    fig = px.pie(
        segment_df,
        names=col_name,
        values=val_name,
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


def plot_sentiment_donut(sentiment_dict: Dict[str, int]) -> go.Figure:
    """Plot donut chart of sentiment distribution (Positive, Neutral, Negative)."""
    color_map = {"Positive": "#10b981", "Neutral": "#64748b", "Negative": "#ef4444"}
    labels = list(sentiment_dict.keys())
    values = list(sentiment_dict.values())
    colors = [color_map.get(lbl, "#3b82f6") for lbl in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    )])
    fig.update_layout(
        title="Overall Sentiment Distribution",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        showlegend=True,
    )
    return fig


def plot_rfm_scatter(rfm_df: pd.DataFrame) -> go.Figure:
    """Plot 2D/3D behavioral scatter plot: Recency vs Monetary sized by Frequency."""
    fig = px.scatter(
        rfm_df,
        x="recency_days",
        y="monetary_total",
        size="frequency",
        color="rfm_segment",
        hover_data=["customer_id", "frequency", "monetary_total", "recency_days"],
        title="Customer RFM Matrix: Recency vs Monetary Value",
        labels={
            "recency_days": "Recency (Days Since Last Order)",
            "monetary_total": "Monetary Value ($)",
            "rfm_segment": "Segment",
            "frequency": "Order Frequency",
        },
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=380,
    )
    return fig


def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Plot Pearson correlation heatmap for numerical features."""
    fig = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Numerical Features Pearson Correlation Matrix",
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=380,
    )
    return fig


def plot_metric_timeline(timeline_df: pd.DataFrame, x_col: str, y_col: str, title: str) -> go.Figure:
    """Plot line/bar trend chart for any time series metric."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline_df[x_col],
        y=timeline_df[y_col],
        mode="lines+markers",
        name=y_col.replace("_", " ").title(),
        line=dict(color="#3b82f6", width=3),
        marker=dict(size=6, color="#1d4ed8"),
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_col.replace("_", " ").title(),
        yaxis_title=y_col.replace("_", " ").title(),
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig

