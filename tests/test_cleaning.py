"""
tests/test_cleaning.py
Tests for data cleaning, duplicate removal, and imputation pipelines.
"""
from src.data.cleaning import clean_customers, clean_products, clean_transactions


def test_clean_customers_imputes_missing_age(sample_customers):
    cleaned, report = clean_customers(sample_customers)
    assert cleaned["age"].isnull().sum() == 0
    assert report["missing_age_imputed"] == 1


def test_clean_products_standardizes_category_casing(sample_products):
    cleaned, report = clean_products(sample_products)
    assert cleaned.loc[0, "category"] == "Electronics"


def test_clean_transactions_removes_duplicates_and_aligns_math(sample_transactions):
    cleaned, report = clean_transactions(sample_transactions)
    # Deduplication
    assert len(cleaned) == 1
    assert report["duplicates_removed"] == 1
    # Arithmetic: 2 * 699.99 * 0.10 = 140.00 discount -> total = 1259.98
    assert cleaned.loc[0, "discount_amount"] == 140.0
    assert cleaned.loc[0, "total_amount"] == 1259.98
