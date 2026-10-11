"""
tests/test_active_dataset_manager.py
Unit tests for global active dataset management, multi-page state synchronization,
synthetic bundle building, template switching, and report generation.
"""
import pandas as pd
import pytest

from app.services.active_dataset_manager import (
    generate_active_dashboard_reports,
    get_active_aspects_df,
    get_active_bundles,
    get_default_demo_bundles,
    load_template_as_active_dataset,
    reset_to_default_demo_dataset,
    set_active_custom_dataset,
)


def test_get_default_demo_bundles():
    """Verify default demo bundles contain all required dashboard keys and structures."""
    bundles = get_default_demo_bundles()
    assert "exec_kpis" in bundles
    assert "monthly_trend" in bundles
    assert "cat_perf" in bundles
    assert "cust_profiles" in bundles
    assert "seg_summary" in bundles
    assert "prod_perf" in bundles

    kpis = bundles["exec_kpis"]
    assert kpis["total_net_revenue"] > 0
    assert kpis["total_orders"] > 0
    assert kpis["average_order_value"] > 0
    assert 0 <= kpis["overall_return_rate_pct"] <= 100


def test_set_active_custom_dataset_and_bundles():
    """Verify setting a custom dataset builds all synchronized bundles across all pages."""
    sample_df = pd.DataFrame({
        "order_id": ["ORD-1", "ORD-2", "ORD-3", "ORD-4", "ORD-5"],
        "customer_id": ["CUST-1", "CUST-2", "CUST-1", "CUST-3", "CUST-2"],
        "order_date": ["2026-01-10", "2026-01-15", "2026-02-01", "2026-02-20", "2026-03-05"],
        "product_name": ["Widget A", "Widget B", "Widget A", "Widget C", "Widget B"],
        "category": ["Electronics", "Home", "Electronics", "Outdoor", "Home"],
        "total_amount": [120.0, 45.0, 150.0, 80.0, 95.0],
        "quantity": [2, 1, 3, 1, 2],
        "return_status": ["Completed", "Completed", "Returned", "Completed", "Completed"],
        "review_text": [
            "Great battery and performance!",
            "Terrible build quality and delivery was delayed.",
            "Fast shipping and nice design.",
            "Average product, acceptable for the price.",
            "Excellent camera and screen quality.",
        ],
        "rating": [5, 1, 4, 3, 5],
    })

    state = set_active_custom_dataset(sample_df, source_label="Test Custom Orders")

    assert state["is_custom_active"] is True
    assert state["dataset_name"] == "Test Custom Orders"
    assert state["row_count"] == 5

    bundles = state["bundles"]
    kpis = bundles["exec_kpis"]
    assert kpis["total_orders"] == 5
    assert kpis["total_net_revenue"] > 0
    assert "average_rating" in kpis
    assert "positive_sentiment_pct" in kpis

    # Monthly trend DataFrame
    assert not bundles["monthly_trend"].empty
    assert "year_month" in bundles["monthly_trend"].columns
    assert "total_revenue" in bundles["monthly_trend"].columns

    # Category performance DataFrame
    assert not bundles["cat_perf"].empty
    assert "category" in bundles["cat_perf"].columns
    assert "revenue" in bundles["cat_perf"].columns

    # Customer profiles DataFrame
    assert not bundles["cust_profiles"].empty
    assert "customer_id" in bundles["cust_profiles"].columns
    assert "customer_segment" in bundles["cust_profiles"].columns

    # Product performance DataFrame
    assert not bundles["prod_perf"].empty
    assert "product_name" in bundles["prod_perf"].columns
    assert "net_revenue" in bundles["prod_perf"].columns

    # Aspects DataFrame
    assert not state["aspects_df"].empty
    assert "aspect" in state["aspects_df"].columns


def test_load_template_as_active_dataset():
    """Verify loading enterprise templates seamlessly sets active dataset state."""
    state = load_template_as_active_dataset("retail_transactions")
    assert state["is_custom_active"] is True
    assert "Retail Sales" in state["dataset_name"]
    assert state["row_count"] > 0
    assert "bundles" in state
    assert state["bundles"]["exec_kpis"]["total_orders"] > 0


def test_generate_active_dashboard_reports():
    """Verify generating complete report download package for the active dataset."""
    reports = generate_active_dashboard_reports()
    assert "html_report" in reports
    assert "excel_bytes" in reports
    assert "md_report" in reports
    assert "csv_bytes" in reports

    assert "<!DOCTYPE html>" in reports["html_report"]
    assert len(reports["excel_bytes"]) > 0
    assert "# Executive Analytics Briefing" in reports["md_report"]
    assert len(reports["csv_bytes"]) > 0


def test_reset_to_default_demo_dataset():
    """Verify resetting to default dataset clears custom state."""
    reset_to_default_demo_dataset()
    bundles = get_active_bundles()
    assert "exec_kpis" in bundles
    # Verify default dataset metrics
    assert bundles["exec_kpis"]["total_orders"] == 1000


def test_sentiment_only_dataset_modality():
    """Verify sentiment-only review datasets correctly set modality and don't invent fake revenue."""
    voc_df = pd.DataFrame({
        "review_id": [f"REV-{i}" for i in range(100)],
        "review_text": ["This is great and amazing build quality!" if i % 2 == 0 else "Horrible battery life and terrible service." for i in range(100)],
        "sentiment": ["Positive" if i % 2 == 0 else "Negative" for i in range(100)],
    })

    state = set_active_custom_dataset(voc_df, source_label="Customer Sentiment VoC")
    assert state["is_custom_active"] is True
    bundles = state["bundles"]
    kpis = bundles["exec_kpis"]

    # Must reflect VoC modality without invented transaction revenue
    assert bundles["has_transactions"] is False
    assert bundles["has_reviews"] is True
    assert kpis["total_net_revenue"] == 0.0
    assert kpis["total_orders"] == 100
    assert "net_sentiment_score" in kpis
    assert kpis["positive_sentiment_pct"] == 50.0
    assert kpis["negative_sentiment_pct"] == 50.0
    assert kpis["net_sentiment_score"] == 0.0

    # Ensure required columns for other pages are present
    assert "rfm_segment" in bundles["cust_profiles"].columns
    assert "rfm_score" in bundles["cust_profiles"].columns
    assert "product_description" in bundles["prod_perf"].columns
    assert not state["aspects_df"].empty
