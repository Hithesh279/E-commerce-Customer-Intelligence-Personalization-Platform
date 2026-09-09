"""
tests/conftest.py
Shared pytest fixtures and test data generators.
"""
import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_customers():
    return pd.DataFrame([
        {
            "customer_id": "CUST_00001",
            "gender": "Female",
            "age": 34,
            "city": "Austin",
            "country": "United States",
            "membership_type": "Gold",
            "signup_date": "2023-01-15",
            "customer_segment": "High Value",
            "preferred_category": "Electronics",
        },
        {
            "customer_id": "CUST_00002",
            "gender": "Male",
            "age": None,  # Test missing age
            "city": "New York",
            "country": "United States",
            "membership_type": "Silver",
            "signup_date": "2023-03-20",
            "customer_segment": "Regular",
            "preferred_category": "Clothing",
        },
    ])


@pytest.fixture
def sample_products():
    return pd.DataFrame([
        {
            "product_id": "PROD_0001",
            "product_name": "ApexTech Ultra Phone 800",
            "category": "electronics",  # Test inconsistent casing
            "subcategory": "Smartphones",
            "brand": "ApexTech",
            "price": 699.99,
            "product_description": "Flagship smartphone featuring vibrant display, long battery life, and crystal camera.",
        },
        {
            "product_id": "PROD_0002",
            "product_name": "ChefCraft Air Fryer 200",
            "category": "Home & Kitchen",
            "subcategory": "Air Fryers",
            "brand": "ChefCraft",
            "price": 129.99,
            "product_description": "Modern air fryer with digital presets, sturdy build quality, and easy cleaning.",
        },
    ])


@pytest.fixture
def sample_transactions():
    return pd.DataFrame([
        {
            "transaction_id": "TXN_000001",
            "customer_id": "CUST_00001",
            "product_id": "PROD_0001",
            "transaction_date": "2023-05-10 14:30:00",
            "quantity": 2,
            "unit_price": 699.99,
            "discount_percentage": 10.0,
            "discount_amount": 139.998,  # Test arithmetic rounding
            "total_amount": 1259.98,
            "payment_method": "Credit Card",
            "return_status": "Completed",
        },
        {
            "transaction_id": "TXN_000001",  # Test duplicate ID
            "customer_id": "CUST_00001",
            "product_id": "PROD_0001",
            "transaction_date": "2023-05-10 14:30:00",
            "quantity": 2,
            "unit_price": 699.99,
            "discount_percentage": 10.0,
            "discount_amount": 140.0,
            "total_amount": 1259.98,
            "payment_method": "Credit Card",
            "return_status": "Completed",
        },
    ])
