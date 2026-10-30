"""
src/data/validation.py
Data validation checks for schema conformance, null rates, duplicates,
referential integrity, and business rule validity.
"""
from typing import Any, Dict, List
import pandas as pd
from src.utils.logging import get_logger

logger = get_logger("data_validation")

REQUIRED_COLUMNS: Dict[str, List[str]] = {
    "customers": [
        "customer_id", "gender", "age", "city", "country",
        "membership_type", "signup_date", "customer_segment", "preferred_category"
    ],
    "products": [
        "product_id", "product_name", "category", "subcategory",
        "brand", "price", "product_description"
    ],
    "transactions": [
        "transaction_id", "customer_id", "product_id", "transaction_date",
        "quantity", "unit_price", "discount_percentage", "discount_amount",
        "total_amount", "payment_method", "return_status"
    ],
    "reviews": [
        "review_id", "customer_id", "product_id", "review_date",
        "rating", "review_text"
    ],
    "interactions": [
        "interaction_id", "customer_id", "product_id",
        "interaction_type", "timestamp", "session_id"
    ],
}


def validate_schema(table_name: str, df: pd.DataFrame) -> bool:
    """Validate that required columns are present in DataFrame."""
    expected = REQUIRED_COLUMNS.get(table_name, [])
    missing = [col for col in expected if col not in df.columns]
    if missing:
        logger.error(f"Table '{table_name}' is missing required columns: {missing}")
        raise ValueError(f"Table '{table_name}' missing columns: {missing}")
    return True


def check_duplicates(table_name: str, df: pd.DataFrame, id_col: str) -> int:
    """Count duplicate primary keys."""
    duplicates = df[id_col].duplicated().sum()
    if duplicates > 0:
        logger.warning(f"Table '{table_name}' contains {duplicates} duplicate IDs in column '{id_col}'.")
    return int(duplicates)


def check_foreign_keys(
    child_df: pd.DataFrame,
    parent_df: pd.DataFrame,
    child_fk: str,
    parent_pk: str,
    child_table: str,
    parent_table: str,
) -> int:
    """Check for orphaned records violating foreign key constraints."""
    valid_ids = set(parent_df[parent_pk].dropna().unique())
    child_ids = child_df[child_fk].dropna()
    orphans = (~child_ids.isin(valid_ids)).sum()
    if orphans > 0:
        logger.warning(f"{child_table}.{child_fk} has {orphans} orphaned records referencing missing {parent_table}.{parent_pk}.")
    return int(orphans)


def validate_transaction_math(transactions_df: pd.DataFrame, tolerance: float = 0.02) -> int:
    """Validate that total_amount matches (quantity * unit_price - discount_amount)."""
    expected_total = (transactions_df["quantity"] * transactions_df["unit_price"]) - transactions_df["discount_amount"]
    discrepancies = (transactions_df["total_amount"] - expected_total).abs() > tolerance
    mismatch_count = int(discrepancies.sum())
    if mismatch_count > 0:
        logger.warning(f"Found {mismatch_count} transactions with arithmetic mismatches in total_amount.")
    return mismatch_count


def validate_dataset_collection(dataset: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Run full validation suite across all tables in dataset."""
    results: Dict[str, Any] = {}
    for table_name, df in dataset.items():
        validate_schema(table_name, df)
        id_col = f"{table_name[:-1]}_id" if table_name.endswith("s") else f"{table_name}_id"
        if id_col not in df.columns:
            id_col = df.columns[0]
        dups = check_duplicates(table_name, df, id_col)
        results[table_name] = {
            "row_count": len(df),
            "columns": list(df.columns),
            "duplicate_ids": dups,
            "null_counts": {k: int(v) for k, v in df.isnull().sum().to_dict().items()},
        }

    # Foreign key checks
    if "transactions" in dataset and "customers" in dataset:
        results["fk_txns_customers_orphans"] = check_foreign_keys(
            dataset["transactions"], dataset["customers"], "customer_id", "customer_id", "transactions", "customers"
        )
    if "transactions" in dataset and "products" in dataset:
        results["fk_txns_products_orphans"] = check_foreign_keys(
            dataset["transactions"], dataset["products"], "product_id", "product_id", "transactions", "products"
        )
    if "reviews" in dataset and "products" in dataset:
        results["fk_reviews_products_orphans"] = check_foreign_keys(
            dataset["reviews"], dataset["products"], "product_id", "product_id", "reviews", "products"
        )
    if "reviews" in dataset and "customers" in dataset:
        results["fk_reviews_customers_orphans"] = check_foreign_keys(
            dataset["reviews"], dataset["customers"], "customer_id", "customer_id", "reviews", "customers"
        )
    if "interactions" in dataset and "customers" in dataset:
        results["fk_interactions_customers_orphans"] = check_foreign_keys(
            dataset["interactions"], dataset["customers"], "customer_id", "customer_id", "interactions", "customers"
        )
    if "interactions" in dataset and "products" in dataset:
        results["fk_interactions_products_orphans"] = check_foreign_keys(
            dataset["interactions"], dataset["products"], "product_id", "product_id", "interactions", "products"
        )
    if "transactions" in dataset:
        results["transaction_math_mismatches"] = validate_transaction_math(dataset["transactions"])

    logger.info("Dataset validation checks completed successfully.")
    return results
