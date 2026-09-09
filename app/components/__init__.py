"""
app/components package.
"""
from app.components.cards import render_metric_card, render_recommendation_card
from app.components.charts import (
    plot_aspect_radar,
    plot_category_sales,
    plot_revenue_trend,
    plot_segment_distribution,
)
from app.components.styles import apply_custom_css

__all__ = [
    "apply_custom_css",
    "render_metric_card",
    "render_recommendation_card",
    "plot_revenue_trend",
    "plot_category_sales",
    "plot_aspect_radar",
    "plot_segment_distribution",
]
