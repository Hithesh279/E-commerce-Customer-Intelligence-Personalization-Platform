"""
tests/test_cleaning.py
Tests for data cleaning, duplicate removal, and imputation pipelines.
"""
import pandas as pd
from src.data.cleaning import (
    clean_customers,
    clean_interactions,
    clean_products,
    clean_reviews,
    clean_transactions,
)


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


def test_clean_reviews_and_interactions_filter_counts_exclude_duplicates():
    revs = pd.DataFrame([
        {"review_id": "R1", "customer_id": "C1", "product_id": "P1", "review_date": "2024-01-01 10:00:00", "rating": 5, "review_text": "Great product!"},
        {"review_id": "R1", "customer_id": "C1", "product_id": "P1", "review_date": "2024-01-01 10:00:00", "rating": 5, "review_text": "Great product!"},
        {"review_id": "R2", "customer_id": "C2", "product_id": "P1", "review_date": "2024-01-02 10:00:00", "rating": 3, "review_text": "ok"},
    ])
    cleaned_revs, rev_report = clean_reviews(revs)
    assert len(cleaned_revs) == 1
    assert rev_report["duplicates_removed"] == 1
    assert rev_report["empty_reviews_filtered"] == 1

    inters = pd.DataFrame([
        {"interaction_id": "I1", "customer_id": "C1", "product_id": "P1", "interaction_type": "view", "timestamp": "2024-01-01 10:00:00", "session_id": "S1"},
        {"interaction_id": "I1", "customer_id": "C1", "product_id": "P1", "interaction_type": "view", "timestamp": "2024-01-01 10:00:00", "session_id": "S1"},
        {"interaction_id": "I2", "customer_id": "C1", "product_id": "P1", "interaction_type": "invalid_event", "timestamp": "2024-01-01 11:00:00", "session_id": "S1"},
    ])
    cleaned_inters, inter_report = clean_interactions(inters)
    assert len(cleaned_inters) == 1
    assert inter_report["duplicates_removed"] == 1
    assert inter_report["invalid_types_filtered"] == 1
