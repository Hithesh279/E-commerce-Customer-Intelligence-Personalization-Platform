"""
tests/test_analytics.py
Tests for RFM customer segmentation and executive business KPIs.
"""
import pandas as pd
from src.analytics.business_metrics import calculate_executive_kpis
from src.features.rfm import calculate_rfm


def test_rfm_calculation():
    txns = pd.DataFrame([
        {"transaction_id": "T1", "customer_id": "C1", "transaction_date": "2024-01-01", "total_amount": 100.0, "return_status": "Completed"},
        {"transaction_id": "T2", "customer_id": "C1", "transaction_date": "2024-02-01", "total_amount": 200.0, "return_status": "Completed"},
        {"transaction_id": "T3", "customer_id": "C2", "transaction_date": "2024-01-15", "total_amount": 50.0, "return_status": "Completed"},
        {"transaction_id": "T4", "customer_id": "C3", "transaction_date": "2024-01-20", "total_amount": 80.0, "return_status": "Completed"},
        {"transaction_id": "T5", "customer_id": "C4", "transaction_date": "2024-02-10", "total_amount": 120.0, "return_status": "Completed"},
        {"transaction_id": "T6", "customer_id": "C5", "transaction_date": "2024-02-15", "total_amount": 300.0, "return_status": "Completed"},
    ])

    rfm = calculate_rfm(txns)
    assert len(rfm) == 5
    assert "r_score" in rfm.columns
    assert "f_score" in rfm.columns
    assert "m_score" in rfm.columns
    assert "rfm_segment" in rfm.columns


def test_executive_kpis_calculation():
    custs = pd.DataFrame([{"customer_id": "C1"}, {"customer_id": "C2"}])
    txns = pd.DataFrame([
        {"transaction_id": "T1", "customer_id": "C1", "total_amount": 100.0, "return_status": "Completed"},
        {"transaction_id": "T2", "customer_id": "C1", "total_amount": 50.0, "return_status": "Returned"},
    ])
    revs = pd.DataFrame([
        {"review_id": "R1", "rating": 5},
        {"review_id": "R2", "rating": 2},
    ])

    kpis = calculate_executive_kpis(custs, txns, revs)
    assert kpis["total_orders"] == 2
    assert kpis["total_net_revenue"] == 100.0
    assert kpis["total_gross_revenue"] == 150.0
    assert kpis["overall_return_rate_pct"] == 50.0
    assert kpis["average_rating"] == 3.5
