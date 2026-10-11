"""
app/main.py
Main entry point for the Streamlit E-commerce Customer Intelligence Platform.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

# Configure wide responsive page
st.set_page_config(
    page_title="E-commerce Customer Intelligence & Personalization Platform",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.components.cards import render_metric_card
from app.components.charts import (
    plot_category_sales,
    plot_revenue_trend,
    plot_segment_distribution,
)
from app.components.styles import apply_custom_css, render_sidebar_status
from app.services.data_loader import get_cached_analytics_bundles


def main():
    """Main application landing portal and executive dashboard."""
    apply_custom_css()
    render_sidebar_status()

    # Hero Banner
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 28px; border-radius: 10px; margin-bottom: 24px; border: 1px solid #334155;">
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #f8fafc;">🛍️ E-Commerce Customer Intelligence & Personalization Platform</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.0rem; color: #cbd5e1; line-height: 1.6;">
                Enterprise-grade Data Science & ML Engineering platform combining <strong>11-Aspect Review Sentiment Analysis (ABSA)</strong>, 
                <strong>NMF Unsupervised Topic Modeling</strong>, <strong>Multi-Strategy Recommender Systems (Hybrid, SVD Collaborative, Content-Based, Popularity)</strong>, 
                and <strong>Star-Schema BI Analytics</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # Platform Capabilities Grid
    st.markdown("##### 🚀 Platform Architecture & Specialized Modules:")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #3b82f6; border-radius:8px; padding:14px; margin-bottom:12px;">
                <strong style="font-size:0.95rem; color:#1e293b;">📈 Executive Overview</strong>
                <p style="font-size:0.8rem; color:#64748b; margin:6px 0 0 0;">Commercial health KPIs, revenue trajectories, category performance, and customer segment share.</p>
            </div>
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #10b981; border-radius:8px; padding:14px; margin-bottom:12px;">
                <strong style="font-size:0.95rem; color:#1e293b;">👥 Customer Intelligence</strong>
                <p style="font-size:0.8rem; color:#64748b; margin:6px 0 0 0;">Quantile-based RFM behavioral segmentation and interactive 360-degree customer profile lookup.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #f59e0b; border-radius:8px; padding:14px; margin-bottom:12px;">
                <strong style="font-size:0.95rem; color:#1e293b;">📦 Product Intelligence</strong>
                <p style="font-size:0.8rem; color:#64748b; margin:6px 0 0 0;">Catalog SKU matrix, sentiment-sales discrepancy discovery, and TF-IDF content similarity matching.</p>
            </div>
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #8b5cf6; border-radius:8px; padding:14px; margin-bottom:12px;">
                <strong style="font-size:0.95rem; color:#1e293b;">🧠 NLP Review Voice</strong>
                <p style="font-size:0.8rem; color:#64748b; margin:6px 0 0 0;">Radar chart of 11 product aspects, sentiment polarities, and NMF recurring complaint discovery.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #ec4899; border-radius:8px; padding:14px; margin-bottom:12px;">
                <strong style="font-size:0.95rem; color:#1e293b;">🎯 Recommendation Engine</strong>
                <p style="font-size:0.8rem; color:#64748b; margin:6px 0 0 0;">Multi-strategy engine (Hybrid, TruncatedSVD CF, Content-Based, Popularity) with explainable AI rationale.</p>
            </div>
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #06b6d4; border-radius:8px; padding:14px; margin-bottom:12px;">
                <strong style="font-size:0.95rem; color:#1e293b;">📁 Upload & Auto-Dashboard</strong>
                <p style="font-size:0.8rem; color:#64748b; margin:6px 0 0 0;">Upload any CSV/Excel or load 6 enterprise templates for instant ML auto-dashboards and enriched exports.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Callout Banner for Custom Analyzer
    st.markdown(
        """
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; border-radius: 8px; padding: 14px 18px; margin-bottom: 22px;">
            <strong style="color: #166534; font-size: 0.95rem;">✨ New Feature: Upload Custom Data & Auto-Generate Dashboards!</strong>
            <p style="font-size: 0.85rem; color: #15803d; margin: 4px 0 0 0;">
                Navigate to <strong>Custom Data Analyzer</strong> in the left sidebar to upload any CSV or Excel file — or test one of our 
                <strong>6 enterprise business templates</strong> (Product Reviews, Retail Sales, RFM Profiles, Inventory, Support Tickets, Churn).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    from app.services.active_dataset_manager import render_global_active_dataset_banner
    render_global_active_dataset_banner()

    # Executive Overview Dashboard embedded on Home
    st.markdown("### 📊 Executive Commercial Health & Performance")
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

    # Charts Row
    c_left, c_right = st.columns(2)
    with c_left:
        st.plotly_chart(plot_revenue_trend(bundles["monthly_trend"]), use_container_width=True)
    with c_right:
        st.plotly_chart(plot_category_sales(bundles["cat_perf"]), use_container_width=True)

    # Segment and Top SKUs Row
    s_left, s_right = st.columns(2)
    with s_left:
        st.plotly_chart(plot_segment_distribution(bundles["seg_summary"]), use_container_width=True)
    with s_right:
        st.markdown("##### 🏆 Top Revenue-Generating Products")
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


if __name__ == "__main__":
    main()

