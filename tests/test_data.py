"""
tests/test_data.py
Tests for data validation and schema conformance.
"""
import pandas as pd
import pytest
from src.data.validation import (
    check_duplicates,
    check_foreign_keys,
    validate_dataset_collection,
    validate_schema,
    validate_transaction_math,
)


def test_schema_validation_passes_on_valid_data(sample_customers):
    assert validate_schema("customers", sample_customers) is True


def test_schema_validation_fails_on_missing_column():
    invalid_df = pd.DataFrame({"customer_id": ["C1"], "gender": ["Female"]})
    with pytest.raises(ValueError):
        validate_schema("customers", invalid_df)


def test_duplicate_primary_keys_detected(sample_transactions):
    dups = check_duplicates("transactions", sample_transactions, "transaction_id")
    assert dups == 1


def test_foreign_key_orphan_detection(sample_customers):
    txns = pd.DataFrame([
        {"transaction_id": "T1", "customer_id": "CUST_00001"},
        {"transaction_id": "T2", "customer_id": "CUST_99999"},  # Orphan
    ])
    orphans = check_foreign_keys(txns, sample_customers, "customer_id", "customer_id", "txns", "customers")
    assert orphans == 1


def test_transaction_math_validation():
    txns = pd.DataFrame([
        {
            "transaction_id": "T1",
            "quantity": 2,
            "unit_price": 50.0,
            "discount_amount": 10.0,
            "total_amount": 90.0,  # 2*50 - 10 = 90 (Correct)
        },
        {
            "transaction_id": "T2",
            "quantity": 1,
            "unit_price": 100.0,
            "discount_amount": 0.0,
            "total_amount": 80.0,  # 1*100 - 0 = 100 != 80 (Mismatch)
        }
    ])
    mismatches = validate_transaction_math(txns)
    assert mismatches == 1


def test_validate_dataset_collection_full_checks(sample_customers, sample_products, sample_transactions):
    dataset = {
        "customers": sample_customers,
        "products": sample_products,
        "transactions": sample_transactions,
    }
    res = validate_dataset_collection(dataset)
    assert "fk_txns_customers_orphans" in res
    assert "fk_txns_products_orphans" in res
    assert "transaction_math_mismatches" in res
    assert res["fk_txns_customers_orphans"] == 0
    assert res["fk_txns_products_orphans"] == 0
