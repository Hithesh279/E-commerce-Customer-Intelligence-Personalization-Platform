import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

st.set_page_config(
    page_title="Executive Overview • Customer Intelligence",
    page_icon="📈",
    layout="wide",
)

from app.components.cards import render_metric_card
from app.components.charts import (
    plot_category_sales,
    plot_revenue_trend,
    plot_segment_distribution,
)
from app.components.styles import apply_custom_css, render_sidebar_status
from app.services.data_loader import get_cached_analytics_bundles


def render_overview_page():
    """Render Executive Overview dashboard page."""
    st.markdown("## 📈 Executive Overview & Commercial Performance")
    st.caption("High-level business health scorecards, sales trajectories, and customer distribution.")

    from app.services.active_dataset_manager import render_global_active_dataset_banner
    render_global_active_dataset_banner()

    bundles = get_cached_analytics_bundles()
    kpis = bundles["exec_kpis"]

    # Top KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card(
            title="Total Net Revenue",
            value=f"${kpis['total_net_revenue']:,.2f}",
            delta="+14.2% MoM",
            delta_positive=True,
            card_type="success",
        )
    with col2:
        render_metric_card(
            title="Total Orders",
            value=f"{kpis['total_orders']:,}",
            delta="Completed Txns",
            card_type="default",
        )
    with col3:
        render_metric_card(
            title="Average Order Value",
            value=f"${kpis['average_order_value']:.2f}",
            delta="Per Basket",
            card_type="default",
        )
    with col4:
        render_metric_card(
            title="Overall Return Rate",
            value=f"{kpis['overall_return_rate_pct']:.1f}%",
            delta="Target: < 8.0%",
            delta_positive=kpis["overall_return_rate_pct"] < 8.0,
            card_type="warning" if kpis["overall_return_rate_pct"] > 8.0 else "success",
        )
    with col5:
        render_metric_card(
            title="Customer Satisfaction",
            value=f"{kpis['average_rating']:.2f}★",
            delta=f"{kpis['positive_sentiment_pct']:.1f}% Positive",
            delta_positive=True,
            card_type="success",
        )

    st.markdown("---")

    # Visuals Row
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(plot_revenue_trend(bundles["monthly_trend"]), use_container_width=True)
    with col_right:
        st.plotly_chart(plot_category_sales(bundles["cat_perf"]), use_container_width=True)

    # Segment and Category Row
    col_seg, col_top = st.columns(2)
    with col_seg:
        st.plotly_chart(plot_segment_distribution(bundles["seg_summary"]), use_container_width=True)
    with col_top:
        st.markdown("##### 🏆 Top 5 Revenue-Generating Products")
        top_prods = bundles["prod_perf"].sort_values("net_revenue", ascending=False).head(5)
        st.dataframe(
            top_prods[["product_id", "product_name", "category", "units_sold", "net_revenue", "average_rating", "return_rate"]].rename(
                columns={
                    "product_id": "SKU",
                    "product_name": "Product Name",
                    "category": "Category",
                    "units_sold": "Units Sold",
                    "net_revenue": "Net Revenue ($)",
                    "average_rating": "Rating",
                    "return_rate": "Return %",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


apply_custom_css()
render_sidebar_status()
render_overview_page()

