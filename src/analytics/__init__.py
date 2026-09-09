"""
src/analytics package.
"""
from src.analytics.business_metrics import (
    calculate_category_performance,
    calculate_executive_kpis,
    calculate_monthly_revenue_trend,
    calculate_simulated_recommendation_business_kpis,
)
from src.analytics.customer_analytics import (
    generate_customer_profile_metrics,
    get_segment_summary,
)
from src.analytics.product_analytics import generate_product_performance_metrics

__all__ = [
    "generate_customer_profile_metrics",
    "get_segment_summary",
    "generate_product_performance_metrics",
    "calculate_executive_kpis",
    "calculate_monthly_revenue_trend",
    "calculate_category_performance",
    "calculate_simulated_recommendation_business_kpis",
]
