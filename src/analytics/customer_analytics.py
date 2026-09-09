"""
src/analytics/customer_analytics.py
Customer-level metrics, RFM segmentation, purchase frequency, and behavioral profiling.
"""
from datetime import datetime
from typing import Dict, Tuple
import pandas as pd

from src.features.rfm import calculate_rfm
from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logging import get_logger

logger = get_logger("customer_analytics")


def generate_customer_profile_metrics(
    customers_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate comprehensive customer-level 360-degree analytical profiles.
    """
    # 1. Base transactions aggregation
    completed_txns = transactions_df[transactions_df["return_status"] != "Returned"]
    all_txns = transactions_df.copy()

    txns_summary = all_txns.groupby("customer_id").agg(
        total_orders=("transaction_id", "count"),
        total_items_purchased=("quantity", "sum"),
        gross_spend=("total_amount", "sum"),
        returned_orders=("return_status", lambda s: (s == "Returned").sum()),
    ).reset_index()

    # Net spend from completed
    net_spend = completed_txns.groupby("customer_id")["total_amount"].sum().rename("net_spend").reset_index()
    txns_summary = txns_summary.merge(net_spend, on="customer_id", how="left").fillna({"net_spend": 0.0})

    txns_summary["average_order_value"] = (txns_summary["net_spend"] / txns_summary["total_orders"].clip(lower=1)).round(2)
    txns_summary["return_rate"] = ((txns_summary["returned_orders"] / txns_summary["total_orders"]) * 100).round(1)

    # 2. Reviews aggregation
    rev_summary = reviews_df.groupby("customer_id").agg(
        reviews_written=("review_id", "count"),
        avg_rating_given=("rating", "mean"),
    ).reset_index()
    rev_summary["avg_rating_given"] = rev_summary["avg_rating_given"].round(2)

    # 3. RFM Metrics
    rfm_df = calculate_rfm(transactions_df)

    # 4. Merge all together with customer master
    merged = customers_df.merge(txns_summary, on="customer_id", how="left").fillna({
        "total_orders": 0,
        "total_items_purchased": 0,
        "gross_spend": 0.0,
        "net_spend": 0.0,
        "average_order_value": 0.0,
        "returned_orders": 0,
        "return_rate": 0.0,
    })

    merged = merged.merge(rev_summary, on="customer_id", how="left").fillna({
        "reviews_written": 0,
        "avg_rating_given": 0.0,
    })

    merged = merged.merge(
        rfm_df[["customer_id", "recency_days", "r_score", "f_score", "m_score", "rfm_score", "rfm_segment"]],
        on="customer_id",
        how="left",
    ).fillna({
        "recency_days": 999,
        "r_score": 1,
        "f_score": 1,
        "m_score": 1,
        "rfm_score": "111",
        "rfm_segment": "Hibernating / Inactive",
    })

    logger.info(f"Generated 360-degree analytics for {len(merged)} customers.")
    return merged


def get_segment_summary(customer_profiles: pd.DataFrame) -> pd.DataFrame:
    """Summarize financial and engagement KPIs across customer segments."""
    summary = customer_profiles.groupby("customer_segment").agg(
        customer_count=("customer_id", "count"),
        total_revenue=("net_spend", "sum"),
        avg_revenue_per_customer=("net_spend", "mean"),
        avg_orders=("total_orders", "mean"),
        avg_aov=("average_order_value", "mean"),
        avg_return_rate=("return_rate", "mean"),
    ).reset_index()

    summary["total_revenue"] = summary["total_revenue"].round(2)
    summary["avg_revenue_per_customer"] = summary["avg_revenue_per_customer"].round(2)
    summary["avg_orders"] = summary["avg_orders"].round(1)
    summary["avg_aov"] = summary["avg_aov"].round(2)
    summary["avg_return_rate"] = summary["avg_return_rate"].round(1)

    return summary.sort_values("total_revenue", ascending=False).reset_index(drop=True)
