"""
src/analytics/business_metrics.py
High-level executive KPIs, financial metrics, time trends, category distributions,
and simulated recommendation business attribution metrics.
"""
from typing import Any, Dict, Optional
import pandas as pd

from src.utils.logging import get_logger

logger = get_logger("business_metrics")


def calculate_executive_kpis(
    customers_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Calculate high-level executive business scorecards.
    All metrics computed directly from data without hardcoding.
    """
    completed_txns = transactions_df[transactions_df["return_status"] != "Returned"]
    all_txns = transactions_df.copy()

    total_gross_revenue = float(all_txns["total_amount"].sum())
    total_net_revenue = float(completed_txns["total_amount"].sum())
    total_orders = int(len(all_txns))
    total_customers = int(len(customers_df))

    aov = round(total_net_revenue / max(len(completed_txns), 1), 2)
    overall_return_rate = round(((all_txns["return_status"] == "Returned").mean()) * 100, 2)

    # Customer repeat rate
    orders_per_cust = all_txns.groupby("customer_id")["transaction_id"].count()
    repeat_customers = (orders_per_cust > 1).sum()
    repeat_rate = round((repeat_customers / max(len(orders_per_cust), 1)) * 100, 2)

    # Reviews & Sentiment KPIs
    avg_rating = round(float(reviews_df["rating"].mean()), 2)
    pos_sentiment_pct = round(float((reviews_df["rating"] >= 4).mean() * 100), 2)
    neg_sentiment_pct = round(float((reviews_df["rating"] <= 2).mean() * 100), 2)
    neu_sentiment_pct = round(100.0 - pos_sentiment_pct - neg_sentiment_pct, 2)

    kpis = {
        "total_gross_revenue": round(total_gross_revenue, 2),
        "total_net_revenue": round(total_net_revenue, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "average_order_value": aov,
        "overall_return_rate_pct": overall_return_rate,
        "repeat_customer_rate_pct": repeat_rate,
        "average_rating": avg_rating,
        "positive_sentiment_pct": pos_sentiment_pct,
        "neutral_sentiment_pct": neu_sentiment_pct,
        "negative_sentiment_pct": neg_sentiment_pct,
    }
    logger.info(f"Executive KPIs calculated: Net Rev = ${total_net_revenue:,.2f}, Orders = {total_orders:,}")
    return kpis


def calculate_monthly_revenue_trend(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly revenue and order volume trends."""
    df = transactions_df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["year_month"] = df["transaction_date"].dt.to_period("M").astype(str)

    monthly = df.groupby("year_month").agg(
        total_revenue=("total_amount", "sum"),
        order_count=("transaction_id", "count"),
        returned_orders=("return_status", lambda s: (s == "Returned").sum()),
    ).reset_index()

    monthly["total_revenue"] = monthly["total_revenue"].round(2)
    monthly["return_rate_pct"] = ((monthly["returned_orders"] / monthly["order_count"]) * 100).round(1)
    return monthly.sort_values("year_month").reset_index(drop=True)


def calculate_category_performance(
    products_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate sales, order volume, return rate, and average rating by category."""
    merged_txns = transactions_df.merge(products_df[["product_id", "category"]], on="product_id", how="left")
    merged_revs = reviews_df.merge(products_df[["product_id", "category"]], on="product_id", how="left")

    cat_txns = merged_txns.groupby("category").agg(
        revenue=("total_amount", "sum"),
        orders=("transaction_id", "count"),
        units_sold=("quantity", "sum"),
        returns=("return_status", lambda s: (s == "Returned").sum()),
    ).reset_index()

    cat_revs = merged_revs.groupby("category").agg(
        avg_rating=("rating", "mean"),
        reviews_count=("review_id", "count"),
        pos_pct=("rating", lambda r: round((r >= 4).mean() * 100, 1)),
    ).reset_index()

    cat_perf = cat_txns.merge(cat_revs, on="category", how="left")
    cat_perf["revenue"] = cat_perf["revenue"].round(2)
    cat_perf["return_rate"] = ((cat_perf["returns"] / cat_perf["orders"]) * 100).round(1)
    cat_perf["avg_rating"] = cat_perf["avg_rating"].round(2)

    return cat_perf.sort_values("revenue", ascending=False).reset_index(drop=True)


def calculate_mom_growth(monthly_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Month-over-month revenue change between the last two months in a monthly trend table.
    Returns None when fewer than two months of data exist, so no growth figure is ever invented.
    """
    if monthly_df is None or monthly_df.empty or len(monthly_df) < 2:
        return None
    ordered = monthly_df.sort_values("year_month").reset_index(drop=True)
    latest, previous = ordered.iloc[-1], ordered.iloc[-2]
    prev_rev = float(previous["total_revenue"])
    if prev_rev <= 0:
        return None
    change_pct = (float(latest["total_revenue"]) - prev_rev) / prev_rev * 100
    return {
        "latest_month": str(latest["year_month"]),
        "previous_month": str(previous["year_month"]),
        "change_pct": round(change_pct, 1),
    }


