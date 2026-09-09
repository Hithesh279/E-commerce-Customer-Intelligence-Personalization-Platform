"""
src/features/rfm.py
Calculates Recency, Frequency, and Monetary (RFM) metrics for customer behavioral segmentation.
"""
from datetime import datetime
from typing import Tuple
import numpy as np
import pandas as pd

from src.utils.logging import get_logger

logger = get_logger("rfm_features")


def calculate_rfm(transactions_df: pd.DataFrame, reference_date: datetime = None) -> pd.DataFrame:
    """
    Compute RFM metrics per customer.

    Parameters
    ----------
    transactions_df : pd.DataFrame
        Cleaned transactions DataFrame.
    reference_date : datetime, optional
        Date against which recency is computed. Defaults to max(transaction_date) + 1 day.

    Returns
    -------
    pd.DataFrame
        DataFrame with customer_id, recency_days, frequency, monetary_total,
        r_score, f_score, m_score, rfm_score, and rfm_segment.
    """
    df = transactions_df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    if reference_date is None:
        reference_date = df["transaction_date"].max() + pd.Timedelta(days=1)

    # Filter out returned transactions for net monetary calculation
    completed_txns = df[df["return_status"] != "Returned"]

    rfm = completed_txns.groupby("customer_id").agg(
        recency_days=("transaction_date", lambda dt: (reference_date - dt.max()).days),
        frequency=("transaction_id", "count"),
        monetary_total=("total_amount", "sum"),
    ).reset_index()

    # Calculate Quintile Scores (1 to 5)
    # Recency: lower days = higher score (5)
    rfm["r_score"] = pd.qcut(rfm["recency_days"].rank(method="first", ascending=False), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    # Frequency: higher count = higher score (5)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    # Monetary: higher spend = higher score (5)
    rfm["m_score"] = pd.qcut(rfm["monetary_total"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)

    # Derive behavioral segment based on RFM scores
    def map_rfm_segment(row: pd.Series) -> str:
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions / High Value"
        if r >= 3 and f >= 3:
            return "Loyal Customers"
        if r >= 4 and f <= 2:
            return "Promising / New"
        if r <= 2 and f >= 3:
            return "At Risk / Needs Attention"
        if r <= 2 and f <= 2:
            return "Hibernating / Inactive"
        return "Regular"

    rfm["rfm_segment"] = rfm.apply(map_rfm_segment, axis=1)
    logger.info(f"Calculated RFM metrics for {len(rfm)} customers.")
    return rfm
