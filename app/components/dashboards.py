"""
app/components/dashboards.py
Executive dashboards shared by the Main and Overview pages, so both always show the same numbers.
Every figure is taken from the active dataset's bundles. A metric the dataset cannot support is shown
as "N/A" and its chart is skipped.
"""
import pandas as pd
import streamlit as st

from app.components.cards import render_metric_card, render_quote
from app.components.charts import (
    plot_aspect_radar,
    plot_category_sales,
    plot_revenue_trend,
    plot_segment_distribution,
    plot_sentiment_donut,
)
from src.analytics.business_metrics import calculate_mom_growth
from src.utils.formatting import fmt_money, fmt_num, fmt_pct, fmt_rating, fmt_signed, is_missing


def _table_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Replace missing cells with N/A so tables show the gap instead of blanks or nan."""
    return df.astype(object).where(df.notna(), "N/A")


def _mom_delta(monthly_trend: pd.DataFrame):
    growth = calculate_mom_growth(monthly_trend)
    if growth is None:
        return "Month-over-month: not enough months", True, "default"
    positive = growth["change_pct"] >= 0
    text = f"{growth['change_pct']:+.1f}% MoM ({growth['latest_month']} vs {growth['previous_month']})"
    return text, positive, "success" if positive else "danger"


def _voc_summary(bundles: dict):
    """Sentiment counts and aspect table for the VoC view, or None when no review data exists."""
    reviews_data = bundles.get("reviews_data")
    aspects_df = bundles.get("aspects_df", pd.DataFrame())
    if reviews_data is not None and not reviews_data.get("aspect_summary", pd.DataFrame()).empty:
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
    return reviews_data, asp_summary


def _render_voc(bundles: dict, kpis: dict, key_prefix: str):
    st.markdown("### 📊 Executive Voice of Customer & Sentiment Intelligence")
    st.caption("Sentiment polarity, aspect satisfaction drivers and customer feedback across all records.")
    reviews_data, asp_summary = _voc_summary(bundles)

    col1, col2, col3, col4, col5 = st.columns(5)
    avg_rating = kpis.get("average_rating")
    pos = kpis.get("positive_sentiment_pct")
    neg = kpis.get("negative_sentiment_pct")
    net = kpis.get("net_sentiment_score")
    with col1:
        render_metric_card("Feedback Volume", fmt_num(kpis.get("total_orders") or (reviews_data or {}).get("total_reviews")),
                           delta="Customer reviews", card_type="default")
    with col2:
        render_metric_card("Customer Satisfaction", fmt_rating(avg_rating), delta="Average rating",
                           delta_positive=(avg_rating or 0) >= 3.8, card_type="success" if (avg_rating or 0) >= 3.8 else "warning")
    with col3:
        render_metric_card("Positive Sentiment", fmt_pct(pos), delta="Share of labelled reviews",
                           delta_positive=True, card_type="success")
    with col4:
        render_metric_card("Negative Friction", fmt_pct(neg), delta="Share of labelled reviews",
                           delta_positive=(neg is None or neg < 15.0),
                           card_type="danger" if (neg or 0) > 20 else ("warning" if (neg or 0) > 10 else "default"))
    with col5:
        render_metric_card("Net Sentiment Score", fmt_signed(net, 1), delta="Positive % minus negative %",
                           delta_positive=(net or 0) > 0, card_type="success" if (net or 0) > 0 else "danger")

    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        if reviews_data is not None:
            donut = plot_sentiment_donut(reviews_data["sentiment_counts"])
        elif pos is not None and neg is not None:
            neu = kpis.get("neutral_sentiment_pct") or 0.0
            donut = plot_sentiment_donut({"Positive": pos, "Neutral": neu, "Negative": neg})
        else:
            donut = None
        if donut is not None:
            st.plotly_chart(donut, width="stretch", key=f"{key_prefix}_voc_donut")
        else:
            st.info("No sentiment data is available for this dataset.")
    with c_right:
        if not asp_summary.empty:
            st.plotly_chart(plot_aspect_radar(asp_summary), width="stretch", key=f"{key_prefix}_voc_radar")
        else:
            st.info("No product aspects were detected in the review text.")

    s_left, s_right = st.columns(2)
    with s_left:
        st.markdown("##### 📋 Aspect Sentiment Polarity Summary")
        if not asp_summary.empty:
            rename_cols = {
                "aspect": "Product Aspect", "mentions": "Mentions", "total_mentions": "Mentions",
                "avg_sentiment_score": "Score (-1 to +1)", "positive_pct": "Pos %", "negative_pct": "Neg %",
                "positive_mentions": "Positive Mentions", "negative_mentions": "Negative Mentions",
            }
            disp_df = asp_summary.rename(columns={k: v for k, v in rename_cols.items() if k in asp_summary.columns})
            sort_col = "Score (-1 to +1)" if "Score (-1 to +1)" in disp_df.columns else disp_df.columns[1]
            st.dataframe(_table_for_display(disp_df.sort_values(sort_col, ascending=False)),
                         width="stretch", hide_index=True)
        else:
            st.info("No aspect breakdown available.")
    with s_right:
        st.markdown("##### 💬 Voice of Customer (VoC) Highlights")
        pos_q = (reviews_data or {}).get("positive_quotes", [])
        neg_q = (reviews_data or {}).get("negative_quotes", [])
        if pos_q:
            st.markdown("**🟢 Top Customer Praises:**")
            for q in pos_q[:2]:
                render_quote(q, tone="positive")
        if neg_q:
            st.markdown("**🚨 Critical Customer Friction Alerts:**")
            for q in neg_q[:2]:
                render_quote(q, tone="negative")
        if not pos_q and not neg_q:
            st.info("Customer quotes appear here when textual reviews are provided.")


def _render_commercial(bundles: dict, kpis: dict, key_prefix: str):
    st.markdown("### 📊 Executive Commercial Health & Performance")
    st.caption("High-level business scorecards, sales trajectory, customer segments and top products.")
    monthly = bundles["monthly_trend"]
    mom_text, mom_positive, mom_card = _mom_delta(monthly)
    rate = kpis.get("overall_return_rate_pct")
    rating = kpis.get("average_rating")
    pos = kpis.get("positive_sentiment_pct")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card("Total Net Revenue", fmt_money(kpis.get("total_net_revenue")),
                           delta=mom_text, delta_positive=mom_positive, card_type=mom_card)
    with col2:
        render_metric_card("Total Orders", fmt_num(kpis.get("total_orders")), delta="Completed transactions",
                           card_type="default")
    with col3:
        render_metric_card("Average Order Value", fmt_money(kpis.get("average_order_value")),
                           delta="Per order", card_type="default")
    with col4:
        render_metric_card("Overall Return Rate", fmt_pct(rate),
                           delta="Benchmark: below 8%" if rate is not None else "Return status not in dataset",
                           delta_positive=(rate is None or rate < 8.0),
                           card_type="warning" if (rate or 0) > 8.0 else "success")
    with col5:
        render_metric_card("Customer Satisfaction", fmt_rating(rating),
                           delta=f"{fmt_pct(pos)} positive" if pos is not None else "No ratings in dataset",
                           delta_positive=True, card_type="success" if rating is not None else "default")

    st.markdown("---")
    left, right = st.columns(2)
    with left:
        if not monthly.empty:
            st.plotly_chart(plot_revenue_trend(monthly), width="stretch", key=f"{key_prefix}_rev_trend")
        else:
            st.info("A monthly revenue trend needs a date column and a revenue column.")
    with right:
        cat = bundles["cat_perf"]
        if not cat.empty:
            st.plotly_chart(plot_category_sales(cat), width="stretch", key=f"{key_prefix}_category_sales")
        else:
            st.info("A category breakdown needs a category column and a revenue column.")

    seg_left, seg_right = st.columns(2)
    with seg_left:
        seg = bundles["seg_summary"]
        if not seg.empty:
            st.plotly_chart(plot_segment_distribution(seg), width="stretch", key=f"{key_prefix}_segments")
        else:
            st.info("Customer segments need a customer column (and dates for recency scoring).")
    with seg_right:
        st.markdown("##### 🏆 Top Revenue-Generating Products")
        prod = bundles["prod_perf"]
        if not prod.empty and prod["net_revenue"].notna().any():
            top = prod.sort_values("net_revenue", ascending=False).head(5)
            cols = ["product_id", "product_name", "category", "units_sold", "net_revenue", "average_rating", "return_rate"]
            cols = [c for c in cols if c in top.columns]
            renamed = top[cols].rename(columns={
                "product_id": "SKU", "product_name": "Product Name", "category": "Category",
                "units_sold": "Units Sold", "net_revenue": "Net Revenue ($)", "average_rating": "Rating",
                "return_rate": "Return %",
            })
            st.dataframe(_table_for_display(renamed), width="stretch", hide_index=True)
        else:
            st.info("No product revenue is available for this dataset.")


def render_executive_dashboard(bundles: dict, key_prefix: str = "exec"):
    """Render the commercial dashboard, or the VoC dashboard when the dataset has no transactions."""
    kpis = bundles["exec_kpis"]
    has_txns = bool(bundles.get("has_transactions")) and not is_missing(kpis.get("total_net_revenue"))
    has_revs = bool(bundles.get("has_reviews")) and (
        bundles.get("reviews_data") is not None or not is_missing(kpis.get("positive_sentiment_pct"))
    )
    if has_txns:
        _render_commercial(bundles, kpis, key_prefix)
    elif has_revs:
        _render_voc(bundles, kpis, key_prefix)
    else:
        st.info(
            "This dataset has no revenue, rating or review columns that the executive dashboard can use. "
            "Map the columns in **Custom Data Analyzer**, or use one of the business templates."
        )
