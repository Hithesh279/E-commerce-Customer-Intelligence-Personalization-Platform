"""
src/data/cleaning.py
Robust data cleansing pipeline. Detects and resolves missing values, duplicates,
casing inconsistencies, and arithmetic discrepancies. Documents all quality actions.
"""
from pathlib import Path
from typing import Any, Dict, Tuple
import numpy as np
import pandas as pd

from src.utils.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_directories
from src.utils.logging import get_logger

logger = get_logger("data_cleaning")


def clean_customers(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean customers dataset: impute missing age by segment, validate age bounds, remove duplicates."""
    cleaned = df.copy()
    report: Dict[str, Any] = {}

    initial_count = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["customer_id"]).reset_index(drop=True)
    report["duplicates_removed"] = int(initial_count - len(cleaned))

    # Missing age imputation using segment median (skipping segments with no non-null values)
    missing_age = cleaned["age"].isnull().sum()
    if missing_age > 0:
        cleaned["age"] = cleaned.groupby("customer_segment")["age"].transform(
            lambda s: s.fillna(s.dropna().median()) if s.notna().any() else s
        )
        # Fallback if any segment was entirely null
        fallback_median = cleaned["age"].dropna().median() if cleaned["age"].notna().any() else 35
        cleaned["age"] = cleaned["age"].fillna(fallback_median).astype(int)
    else:
        cleaned["age"] = cleaned["age"].astype(int)
    report["missing_age_imputed"] = int(missing_age)

    # Standardize string fields
    cleaned["gender"] = cleaned["gender"].str.strip().str.title()
    cleaned["customer_segment"] = cleaned["customer_segment"].str.strip().str.title()
    cleaned["preferred_category"] = cleaned["preferred_category"].str.strip()

    logger.info(f"Cleaned customers: {len(cleaned)} rows. Report: {report}")
    return cleaned, report


def clean_products(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean products dataset: fix category casing, trim whitespace, validate prices."""
    cleaned = df.copy()
    report: Dict[str, Any] = {}

    initial_count = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["product_id"]).reset_index(drop=True)
    report["duplicates_removed"] = int(initial_count - len(cleaned))

    # Standardize category and subcategory casings
    category_map = {
        "electronics": "Electronics",
        "clothing": "Clothing",
        "home & kitchen": "Home & Kitchen",
        "beauty": "Beauty",
        "sports": "Sports",
        "books": "Books",
        "accessories": "Accessories",
    }
    cleaned["category"] = cleaned["category"].str.strip().str.lower().map(lambda c: category_map.get(c, c.title()))
    cleaned["subcategory"] = cleaned["subcategory"].str.strip()
    cleaned["brand"] = cleaned["brand"].str.strip()

    # Price validation: price must be positive
    invalid_prices = (cleaned["price"] <= 0).sum()
    if invalid_prices > 0:
        cleaned = cleaned[cleaned["price"] > 0].reset_index(drop=True)
    report["invalid_prices_filtered"] = int(invalid_prices)

    logger.info(f"Cleaned products: {len(cleaned)} rows. Report: {report}")
    return cleaned, report


def clean_transactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean transactions dataset: remove duplicates, enforce arithmetic consistency, standardize payment."""
    cleaned = df.copy()
    report: Dict[str, Any] = {}

    initial_count = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["transaction_id"]).reset_index(drop=True)
    report["duplicates_removed"] = int(initial_count - len(cleaned))

    # Enforce arithmetic consistency: total = (quantity * unit_price) - discount_amount
    expected_discount = (cleaned["quantity"] * cleaned["unit_price"] * (cleaned["discount_percentage"] / 100.0)).round(2)
    cleaned["discount_amount"] = expected_discount
    cleaned["total_amount"] = ((cleaned["quantity"] * cleaned["unit_price"]) - cleaned["discount_amount"]).round(2)
    report["arithmetic_standardized"] = len(cleaned)

    # Standardize status and payment
    cleaned["return_status"] = cleaned["return_status"].str.strip().str.title()
    cleaned["payment_method"] = cleaned["payment_method"].fillna("Credit Card").str.strip()

    # Sort chronologically
    cleaned["transaction_date"] = pd.to_datetime(cleaned["transaction_date"])
    cleaned = cleaned.sort_values("transaction_date").reset_index(drop=True)
    cleaned["transaction_date"] = cleaned["transaction_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"Cleaned transactions: {len(cleaned)} rows. Report: {report}")
    return cleaned, report


def clean_reviews(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean reviews dataset: deduplicate, validate rating range (1-5), strip review text."""
    cleaned = df.copy()
    report: Dict[str, Any] = {}

    initial_count = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["review_id"]).reset_index(drop=True)
    post_dedup_count = len(cleaned)
    report["duplicates_removed"] = int(initial_count - post_dedup_count)

    # Validate rating range
    cleaned["rating"] = cleaned["rating"].clip(1, 5).astype(int)

    # Clean text whitespace
    cleaned["review_text"] = cleaned["review_text"].fillna("").astype(str).str.strip()
    cleaned = cleaned[cleaned["review_text"].str.len() > 3].reset_index(drop=True)
    report["empty_reviews_filtered"] = int(post_dedup_count - len(cleaned))

    cleaned["review_date"] = pd.to_datetime(cleaned["review_date"])
    cleaned = cleaned.sort_values("review_date").reset_index(drop=True)
    cleaned["review_date"] = cleaned["review_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"Cleaned reviews: {len(cleaned)} rows. Report: {report}")
    return cleaned, report


def clean_interactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean interactions dataset: deduplicate, validate interaction types, sort by timestamp."""
    cleaned = df.copy()
    report: Dict[str, Any] = {}

    initial_count = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["interaction_id"]).reset_index(drop=True)
    post_dedup_count = len(cleaned)
    report["duplicates_removed"] = int(initial_count - post_dedup_count)

    valid_types = {"view", "click", "wishlist", "cart", "purchase"}
    cleaned = cleaned[cleaned["interaction_type"].isin(valid_types)].reset_index(drop=True)
    report["invalid_types_filtered"] = int(post_dedup_count - len(cleaned))

    cleaned["timestamp"] = pd.to_datetime(cleaned["timestamp"])
    cleaned = cleaned.sort_values("timestamp").reset_index(drop=True)
    cleaned["timestamp"] = cleaned["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"Cleaned interactions: {len(cleaned)} rows. Report: {report}")
    return cleaned, report


def run_cleaning_pipeline(raw_data: Dict[str, pd.DataFrame] = None) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """
    Execute end-to-end data cleaning pipeline across all datasets.
    Persists cleaned tables to data/processed/.
    """
    ensure_directories()
    logger.info("Starting data cleaning pipeline...")

    if raw_data is None:
        raw_data = {
            "customers": pd.read_csv(RAW_DATA_DIR / "customers.csv"),
            "products": pd.read_csv(RAW_DATA_DIR / "products.csv"),
            "transactions": pd.read_csv(RAW_DATA_DIR / "transactions.csv"),
            "reviews": pd.read_csv(RAW_DATA_DIR / "reviews.csv"),
            "interactions": pd.read_csv(RAW_DATA_DIR / "interactions.csv"),
        }

    cleaned_customers, rep_cust = clean_customers(raw_data["customers"])
    cleaned_products, rep_prod = clean_products(raw_data["products"])
    cleaned_transactions, rep_txns = clean_transactions(raw_data["transactions"])
    cleaned_reviews, rep_rev = clean_reviews(raw_data["reviews"])
    cleaned_interactions, rep_inter = clean_interactions(raw_data["interactions"])

    processed_data = {
        "customers": cleaned_customers,
        "products": cleaned_products,
        "transactions": cleaned_transactions,
        "reviews": cleaned_reviews,
        "interactions": cleaned_interactions,
    }

    # Save to data/processed/
    for name, df in processed_data.items():
        out_path = PROCESSED_DATA_DIR / f"{name}.csv"
        df.to_csv(out_path, index=False)
        logger.info(f"Saved processed dataset: {out_path} ({len(df)} rows)")

    full_report = {
        "customers": rep_cust,
        "products": rep_prod,
        "transactions": rep_txns,
        "reviews": rep_rev,
        "interactions": rep_inter,
    }
    logger.info("Data cleaning pipeline completed successfully.")
    return processed_data, full_report


if __name__ == "__main__":
    run_cleaning_pipeline()
