"""
src/analytics/product_analytics.py
Product performance KPIs, return rates, sentiment-sales correlation, and anomaly discovery.
"""
from typing import Dict, Tuple
import numpy as np
import pandas as pd

from src.utils.logging import get_logger

logger = get_logger("product_analytics")


def generate_product_performance_metrics(
    products_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate 360-degree product performance metrics including revenue, returns,
    average rating, sentiment distribution, and business discrepancy flags.
    """
    # 1. Transaction aggregations
    all_txns = transactions_df.copy()
    completed_txns = all_txns[all_txns["return_status"] != "Returned"]

    txn_stats = all_txns.groupby("product_id").agg(
        total_orders=("transaction_id", "count"),
        units_sold=("quantity", "sum"),
        gross_revenue=("total_amount", "sum"),
        returned_units=("return_status", lambda s: (s == "Returned").sum()),
    ).reset_index()

    net_rev = completed_txns.groupby("product_id")["total_amount"].sum().rename("net_revenue").reset_index()
    txn_stats = txn_stats.merge(net_rev, on="product_id", how="left").fillna({"net_revenue": 0.0})
    txn_stats["return_rate"] = ((txn_stats["returned_units"] / txn_stats["total_orders"].clip(lower=1)) * 100).round(1)

    # 2. Review aggregations
    rev_stats = reviews_df.groupby("product_id").agg(
        review_count=("review_id", "count"),
        average_rating=("rating", "mean"),
        positive_reviews=("rating", lambda r: (r >= 4).sum()),
        negative_reviews=("rating", lambda r: (r <= 2).sum()),
    ).reset_index()

    rev_stats["average_rating"] = rev_stats["average_rating"].round(2)
    rev_stats["positive_sentiment_pct"] = ((rev_stats["positive_reviews"] / rev_stats["review_count"].clip(lower=1)) * 100).round(1)
    rev_stats["negative_sentiment_pct"] = ((rev_stats["negative_reviews"] / rev_stats["review_count"].clip(lower=1)) * 100).round(1)

    # 3. Merge with products master catalog
    merged = products_df.merge(txn_stats, on="product_id", how="left").fillna({
        "total_orders": 0,
        "units_sold": 0,
        "gross_revenue": 0.0,
        "net_revenue": 0.0,
        "returned_units": 0,
        "return_rate": 0.0,
    })

    merged = merged.merge(rev_stats, on="product_id", how="left").fillna({
        "review_count": 0,
        "average_rating": 0.0,
        "positive_reviews": 0,
        "negative_reviews": 0,
        "positive_sentiment_pct": 0.0,
        "negative_sentiment_pct": 0.0,
    })

    # 4. Identify Discrepancies:
    # High Sales + Low Sentiment
    sales_q75 = merged["units_sold"].quantile(0.75)
    rating_q25 = merged[merged["review_count"] >= 5]["average_rating"].quantile(0.25)
    rating_q75 = merged[merged["review_count"] >= 5]["average_rating"].quantile(0.75)
    sales_median = merged["units_sold"].median()

    merged["is_high_sales_low_sentiment"] = (
        (merged["units_sold"] >= sales_q75) & (merged["average_rating"] <= rating_q25) & (merged["review_count"] >= 5)
    )

    # Low Sales + High Sentiment (Hidden Gems)
    merged["is_low_sales_high_sentiment"] = (
        (merged["units_sold"] <= sales_median) & (merged["average_rating"] >= rating_q75) & (merged["review_count"] >= 3)
    )

    logger.info(f"Generated product performance metrics for {len(merged)} products.")
    logger.info(f"Identified {merged['is_high_sales_low_sentiment'].sum()} High Sales + Low Sentiment products.")
    logger.info(f"Identified {merged['is_low_sales_high_sentiment'].sum()} Low Sales + High Sentiment products.")

    return merged
