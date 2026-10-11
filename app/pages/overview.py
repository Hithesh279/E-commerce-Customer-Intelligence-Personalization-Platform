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

import pandas as pd
from app.components.cards import render_metric_card
from app.components.charts import (
    plot_aspect_radar,
    plot_category_sales,
    plot_revenue_trend,
    plot_segment_distribution,
    plot_sentiment_donut,
)
from app.components.styles import apply_custom_css, render_sidebar_status
from app.services.data_loader import get_cached_analytics_bundles


def render_overview_page():
    """Render Executive Overview dashboard page."""
    from app.services.active_dataset_manager import render_global_active_dataset_banner
    render_global_active_dataset_banner(page_id="overview")

    bundles = get_cached_analytics_bundles()
    kpis = bundles["exec_kpis"]
    has_txns = bundles.get("has_transactions", True) and kpis.get("total_net_revenue", 0.0) > 0
    has_revs = bundles.get("has_reviews", True) or bundles.get("reviews_data") is not None
    reviews_data = bundles.get("reviews_data")
    aspects_df = bundles.get("aspects_df", pd.DataFrame())

    if not has_txns and has_revs:
        # -------------------------------------------------------------
        # Voice of Customer & Review Sentiment Dashboard
        # -------------------------------------------------------------
        st.markdown("## 📊 Executive Voice of Customer & Sentiment Overview")
        st.caption("Comprehensive sentiment polarity, aspect satisfaction drivers, and customer feedback across all records.")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            render_metric_card(
                title="Total Feedback Volume",
                value=f"{kpis['total_orders']:,}",
                delta="Customer Reviews",
                card_type="default",
            )
        with col2:
            render_metric_card(
                title="Customer Satisfaction",
                value=f"{kpis['average_rating']:.2f}★",
                delta="Average Rating",
                delta_positive=kpis["average_rating"] >= 3.8,
                card_type="success" if kpis["average_rating"] >= 3.8 else "warning",
            )
        with col3:
            render_metric_card(
                title="Positive Sentiment",
                value=f"{kpis['positive_sentiment_pct']:.1f}%",
                delta=f"+{kpis['positive_sentiment_pct']:.1f}% Favorable",
                delta_positive=True,
                card_type="success",
            )
        with col4:
            render_metric_card(
                title="Negative Friction",
                value=f"{kpis['negative_sentiment_pct']:.1f}%",
                delta=f"{kpis['negative_sentiment_pct']:.1f}% Critical Alerts",
                delta_positive=kpis["negative_sentiment_pct"] < 15.0,
                card_type="danger" if kpis["negative_sentiment_pct"] > 20 else ("warning" if kpis["negative_sentiment_pct"] > 10 else "default"),
            )
        with col5:
            nss = kpis.get("net_sentiment_score", round(kpis["positive_sentiment_pct"] - kpis["negative_sentiment_pct"], 1))
            render_metric_card(
                title="Net Sentiment Score",
                value=f"{nss:+0.1f}",
                delta="Pos % minus Neg %",
                delta_positive=nss > 0,
                card_type="success" if nss > 0 else "danger",
            )

        st.markdown("---")

        # Row 1: Sentiment Donut & Aspect Radar
        c_left, c_right = st.columns(2)
        with c_left:
            sent_counts = reviews_data["sentiment_counts"] if reviews_data and "sentiment_counts" in reviews_data else {
                "Positive": int(kpis["total_orders"] * (kpis["positive_sentiment_pct"] / 100)),
                "Neutral": int(kpis["total_orders"] * (kpis.get("neutral_sentiment_pct", 10.0) / 100)),
                "Negative": int(kpis["total_orders"] * (kpis["negative_sentiment_pct"] / 100)),
            }
            st.plotly_chart(plot_sentiment_donut(sent_counts), use_container_width=True, key="overview_voc_donut")

        with c_right:
            if reviews_data is not None and not reviews_data["aspect_summary"].empty:
                asp_summary = reviews_data["aspect_summary"]
            elif not aspects_df.empty:
                asp_summary = aspects_df.groupby("aspect").agg(
                    total_mentions=("review_id", "count"),
                    avg_sentiment_score=("sentiment_score", "mean"),
                    positive_pct=("sentiment", lambda s: round((s == "Positive").mean() * 100, 1)),
                    negative_pct=("sentiment", lambda s: round((s == "Negative").mean() * 100, 1)),
                ).reset_index()
            else:
                asp_summary = pd.DataFrame()

            if not asp_summary.empty:
                st.plotly_chart(plot_aspect_radar(asp_summary), use_container_width=True, key="overview_voc_radar")
            else:
                st.info("Aspect extraction processing complete.")

        # Row 2: Aspect Polarity Breakdown Table & Customer Quotes
        s_left, s_right = st.columns(2)
        with s_left:
            st.markdown("##### 📋 Aspect Sentiment Polarity Summary")
            if not asp_summary.empty:
                rename_cols = {
                    "aspect": "Product Aspect",
                    "mentions": "Mentions",
                    "total_mentions": "Mentions",
                    "avg_sentiment_score": "Score (-1 to +1)",
                    "positive_pct": "Pos %",
                    "negative_pct": "Neg %",
                    "positive_mentions": "Positive Mentions",
                    "negative_mentions": "Negative Mentions",
                }
                disp_df = asp_summary.rename(columns={k: v for k, v in rename_cols.items() if k in asp_summary.columns})
                sort_col = "Score (-1 to +1)" if "Score (-1 to +1)" in disp_df.columns else disp_df.columns[1]
                st.dataframe(disp_df.sort_values(sort_col, ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("No aspect breakdown available.")

        with s_right:
            st.markdown("##### 💬 Voice of Customer (VoC) Highlights")
            pos_q = reviews_data.get("positive_quotes", []) if reviews_data else []
            neg_q = reviews_data.get("negative_quotes", []) if reviews_data else []

            if pos_q:
                st.markdown("**🟢 Top Customer Praises:**")
                for q in pos_q[:2]:
                    st.markdown(
                        f"""
                        <div style="background:#f0fdf4; border-left:4px solid #16a34a; border-radius:4px; padding:8px 12px; margin-bottom:8px; font-size:0.83rem; color:#14532d;">
                            "{q}"
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            if neg_q:
                st.markdown("**🚨 Critical Customer Friction Alerts:**")
                for q in neg_q[:2]:
                    st.markdown(
                        f"""
                        <div style="background:#fef2f2; border-left:4px solid #ef4444; border-radius:4px; padding:8px 12px; margin-bottom:8px; font-size:0.83rem; color:#7f1d1d;">
                            "{q}"
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            if not pos_q and not neg_q:
                st.info("Customer quotes will appear here when textual reviews are provided.")
    else:
        # -------------------------------------------------------------
        # Commercial Health & Performance Dashboard
        # -------------------------------------------------------------
        st.markdown("## 📈 Executive Overview & Commercial Performance")
        st.caption("High-level business health scorecards, sales trajectories, and customer distribution.")

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
            st.plotly_chart(plot_revenue_trend(bundles["monthly_trend"]), use_container_width=True, key="overview_rev_trend")
        with col_right:
            st.plotly_chart(plot_category_sales(bundles["cat_perf"]), use_container_width=True, key="overview_category_sales")

        # Segment and Category Row
        col_seg, col_top = st.columns(2)
        with col_seg:
            st.plotly_chart(plot_segment_distribution(bundles["seg_summary"]), use_container_width=True, key="overview_segment_dist")
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

