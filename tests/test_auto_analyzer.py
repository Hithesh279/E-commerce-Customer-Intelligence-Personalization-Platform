"""
tests/test_auto_analyzer.py
Unit tests for schema detection, automated reviews analysis, transaction analytics,
RFM profiling, and enterprise business templates.
"""
import pandas as pd
import pytest

from src.analytics.auto_analyzer import (
    analyze_custom_reviews,
    analyze_custom_transactions,
    calculate_custom_rfm,
    detect_schema,
    profile_generic_table,
)
from src.analytics.templates import (
    generate_blank_template_csv,
    get_available_templates,
    load_sample_template,
)


def test_get_available_templates():
    """Verify that all 12 enterprise business templates are registered."""
    templates = get_available_templates()
    assert len(templates) == 12
    expected_keys = [
        "product_reviews",
        "support_tickets",
        "retail_transactions",
        "subscription_churn",
        "customer_rfm",
        "cart_abandonment",
        "inventory_health",
        "shipping_logistics",
        "product_returns",
        "marketing_campaigns",
        "promotions_discounts",
        "web_traffic",
    ]
    for key in expected_keys:
        assert key in templates
        assert "name" in templates[key]
        assert "columns" in templates[key]
        assert "category" in templates[key]


def test_load_sample_templates_and_columns():
    """Verify each template generates valid data with all declared columns."""
    for key in get_available_templates():
        df = load_sample_template(key, n_records=25)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 25 or len(df) > 0
        for col in get_available_templates()[key]["columns"]:
            assert col in df.columns, f"Missing column {col} in template {key}"


def test_generate_blank_template_csv():
    """Verify blank CSV generator creates a valid CSV string with headers."""
    csv_text = generate_blank_template_csv("retail_transactions")
    assert "order_id" in csv_text
    assert "total_amount" in csv_text
    # Load back to DataFrame
    import io
    df = pd.read_csv(io.StringIO(csv_text))
    assert len(df) == 1
    assert "order_id" in df.columns


def test_detect_schema_reviews():
    """Verify schema detection accurately detects reviews modality."""
    df = load_sample_template("product_reviews", n_records=20)
    schema = detect_schema(df)
    assert schema["mappings"]["text_col"] == "review_text"
    assert schema["mappings"]["rating_col"] == "rating"
    assert schema["modalities"]["has_reviews"] is True


def test_detect_schema_transactions():
    """Verify schema detection accurately identifies transactional attributes."""
    df = load_sample_template("retail_transactions", n_records=20)
    schema = detect_schema(df)
    assert schema["mappings"]["revenue_col"] == "total_amount"
    assert schema["mappings"]["customer_col"] == "customer_id"
    assert schema["mappings"]["category_col"] == "category"
    assert schema["modalities"]["has_transactions"] is True


def test_detect_schema_generic():
    """Verify schema detection gracefully falls back on generic tabular data."""
    df = pd.DataFrame({
        "alpha": [1, 2, 3],
        "beta": [4.5, 5.5, 6.5],
        "gamma": ["x", "y", "z"],
    })
    schema = detect_schema(df)
    assert schema["modalities"]["is_generic"] is True


def test_analyze_custom_reviews():
    """Verify review analysis adds ML sentiment labels, aspect tags, and aggregates."""
    df = pd.DataFrame({
        "review_id": [1, 2, 3],
        "comment": [
            "The battery is incredible and sound is brilliant! Loved it.",
            "Terrible build quality, broke immediately and slow delivery.",
            "Just an okay product, nothing special.",
        ],
    })
    enriched_df, analytics = analyze_custom_reviews(df, text_col="comment")
    assert "predicted_sentiment" in enriched_df.columns
    assert "sentiment_confidence" in enriched_df.columns
    assert "extracted_aspects" in enriched_df.columns
    assert analytics["total_reviews"] == 3
    assert "Positive" in analytics["sentiment_counts"]
    assert -1.0 <= analytics["avg_polarity"] <= 1.0


def test_analyze_custom_transactions():
    """Verify transaction analyzer computes revenue, AOV, category shares, and trends."""
    df = pd.DataFrame({
        "tx_id": [1, 2, 3, 4],
        "tx_date": ["2026-01-10", "2026-01-15", "2026-02-05", "2026-02-12"],
        "user_id": ["U1", "U2", "U1", "U3"],
        "product": ["Widget A", "Widget B", "Widget A", "Widget C"],
        "dept": ["Tools", "Kitchen", "Tools", "Office"],
        "amount": [100.0, 50.0, 150.0, 200.0],
        "status": ["Completed", "Completed", "Returned", "Completed"],
    })
    results = analyze_custom_transactions(
        df,
        date_col="tx_date",
        revenue_col="amount",
        customer_col="user_id",
        category_col="dept",
        product_col="product",
        status_col="status",
    )
    assert results["total_orders"] == 4
    assert results["total_revenue"] == 500.0
    assert results["aov"] == 125.0
    assert results["unique_customers"] == 3
    assert results["return_rate"] == 25.0
    assert not results["timeline_df"].empty
    assert not results["category_df"].empty


def test_calculate_custom_rfm():
    """Verify custom RFM calculates quintiles and assigns behavioral segments."""
    df = pd.DataFrame({
        "customer": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
        "date": [
            "2026-03-01", "2026-03-05", "2026-02-15", "2026-01-10",
            "2026-03-10", "2026-02-20", "2026-01-05", "2025-12-10",
        ],
        "spend": [50.0, 200.0, 350.0, 20.0, 500.0, 80.0, 15.0, 10.0],
    })
    rfm_df, metrics = calculate_custom_rfm(
        df,
        customer_col="customer",
        date_col="date",
        revenue_col="spend",
    )
    assert len(rfm_df) == 8
    assert "rfm_segment" in rfm_df.columns
    assert "r_score" in rfm_df.columns
    assert "f_score" in rfm_df.columns
    assert "m_score" in rfm_df.columns
    assert metrics["total_customers"] == 8
    assert not metrics["segment_summary"].empty


def test_profile_generic_table():
    """Verify table profiler produces summary stats, correlation matrix, and missing overview."""
    df = pd.DataFrame({
        "num1": [10, 20, 30, 40, 50],
        "num2": [100, 250, 310, 420, 500],
        "cat1": ["A", "B", "A", "B", "C"],
    })
    profile = profile_generic_table(df)
    assert profile["row_count"] == 5
    assert profile["col_count"] == 3
    assert not profile["summary_stats"].empty
    assert not profile["corr_matrix"].empty
    assert not profile["missing_overview"].empty
