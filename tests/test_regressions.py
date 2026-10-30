"""
tests/test_regressions.py
Regression tests for the defects fixed in the review: invented values, leakage, data-integrity
and security problems. Each test pins a behaviour that used to be wrong.
"""
import io
import json
import random
import sqlite3
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.utils.config import ASPECT_LIST, PROCESSED_DATA_DIR, PROJECT_ROOT
from src.utils.formatting import fmt_money, fmt_num, fmt_pct, is_missing


# ---------------------------------------------------------------- formatting
def test_formatters_render_missing_as_na():
    assert fmt_money(None) == "N/A"
    assert fmt_money(float("nan")) == "N/A"
    assert fmt_pct(None) == "N/A"
    assert fmt_num(np.nan) == "N/A"
    assert fmt_money(1234.5) == "$1,234.50"
    assert fmt_pct(12.345) == "12.3%"
    assert is_missing(pd.NA)


# ---------------------------------------------------------------- data generation
def test_interactions_total_matches_configured_budget():
    from src.data.ingestion import generate_interactions

    txns = pd.DataFrame({
        "transaction_id": [f"T{i}" for i in range(100)],
        "customer_id": [f"C{i % 10}" for i in range(100)],
        "product_id": [f"P{i % 5}" for i in range(100)],
        "transaction_date": [f"2024-01-{(i % 28) + 1:02d} 10:00:00" for i in range(100)],
    })
    customers = pd.DataFrame({"customer_id": [f"C{i}" for i in range(10)]})
    products = pd.DataFrame({"product_id": [f"P{i}" for i in range(5)]})
    out = generate_interactions(txns, customers, products, n_interactions=300)
    assert len(out) == 300


# ---------------------------------------------------------------- sentiment and review analytics
def test_one_star_label_is_negative_not_positive():
    from src.analytics.auto_analyzer import _standardize_sentiment

    assert _standardize_sentiment("1") == "Negative"
    assert _standardize_sentiment(5) == "Positive"
    assert _standardize_sentiment("3") == "Neutral"
    assert _standardize_sentiment("maybe") == "Unlabeled"
    assert _standardize_sentiment(None) == "Unlabeled"


def test_missing_rating_is_unlabeled_and_excluded_from_percentages():
    from src.analytics.auto_analyzer import analyze_custom_reviews

    df = pd.DataFrame({"rating": [5, np.nan, 1, np.nan], "text": ["a", "b", "c", "d"]})
    _, analytics = analyze_custom_reviews(df, rating_col="rating")
    assert analytics["labeled_reviews"] == 2
    assert analytics["positive_pct"] == 50.0
    assert analytics["negative_pct"] == 50.0
    assert analytics["avg_rating"] == 3.0


def test_review_table_without_signal_returns_no_analytics():
    from src.analytics.auto_analyzer import analyze_custom_reviews

    df = pd.DataFrame({"x": [1, 2, 3]})
    enriched, analytics = analyze_custom_reviews(df, text_col=None, rating_col=None, sentiment_col=None)
    assert analytics is None
    assert "predicted_sentiment" not in enriched.columns


def test_custom_text_is_preprocessed_like_training(monkeypatch):
    """Inference must apply the same cleaning as training, so the two never disagree on the same text."""
    from src.analytics import auto_analyzer
    from src.nlp.sentiment_predict import SentimentPredictor

    predictor = SentimentPredictor()
    text = "I can't believe how GREAT this is!!! Won't regret it."
    expected = predictor.predict(text)["sentiment"]
    enriched, analytics = auto_analyzer.analyze_custom_reviews(pd.DataFrame({"t": [text]}), text_col="t")
    assert enriched["predicted_sentiment"].iloc[0] == expected


def test_transactions_without_revenue_report_none_not_zero():
    from src.analytics.auto_analyzer import analyze_custom_transactions

    df = pd.DataFrame({"order": [1, 2], "status": ["Returned", "Completed"]})
    res = analyze_custom_transactions(df, status_col="status")
    assert res["total_revenue"] is None
    assert res["aov"] is None
    assert res["total_orders"] is None
    assert res["return_rate"] == 50.0


def test_rfm_without_dates_does_not_invent_recency():
    from src.analytics.auto_analyzer import calculate_custom_rfm

    df = pd.DataFrame({
        "customer_id": [f"C{i}" for i in range(8)],
        "lifetime_spend": [10.0, 50.0, 300.0, 20.0, 500.0, 80.0, 15.0, 90.0],
        "total_orders": [1, 2, 9, 1, 12, 3, 1, 4],
    })
    first_rfm, first_metrics = calculate_custom_rfm(df, customer_col="customer_id")
    second_rfm, _ = calculate_custom_rfm(df, customer_col="customer_id")
    assert first_metrics["recency_available"] is False
    assert first_rfm["recency_days"].isna().all()
    assert first_metrics["champions_count"] is None and first_metrics["at_risk_count"] is None
    pd.testing.assert_frame_equal(first_rfm, second_rfm)  # deterministic, no random recency


def test_rfm_rejects_single_customer_instead_of_crashing():
    from src.analytics.auto_analyzer import calculate_custom_rfm

    df = pd.DataFrame({"c": ["A"], "d": ["2024-01-01"], "amt": [10.0]})
    with pytest.raises(ValueError):
        calculate_custom_rfm(df, customer_col="c", date_col="d", revenue_col="amt")


def test_detect_schema_handles_string_dtype_columns():
    from src.analytics.auto_analyzer import detect_schema

    df = pd.DataFrame({"notes_col": pd.array(["a long description of the product " * 3] * 3, dtype="string")})
    assert detect_schema(df)["mappings"]["text_col"] == "notes_col"


def test_load_sample_template_does_not_touch_global_random_state():
    from src.analytics.templates import load_sample_template

    random.seed(123)
    before = random.getstate()
    load_sample_template("retail_transactions", n_records=10)
    assert random.getstate() == before


def test_aspect_extraction_keeps_hyphenated_words():
    from src.nlp.aspect_extraction import extract_aspect_sentiment_from_text

    found = extract_aspect_sentiment_from_text("Eco-friendly packaging, really elegant")
    packaging = [a for a in found if a["aspect"] == "packaging"]
    assert packaging and packaging[0]["sentiment"] == "Positive"


# ---------------------------------------------------------------- dataset bundles (no invented values)
def test_custom_bundles_use_only_real_aspects():
    from app.services.active_dataset_manager import build_custom_analytics_bundles
    from src.analytics.auto_analyzer import analyze_custom_reviews, analyze_custom_transactions, detect_schema, profile_generic_table

    df = pd.DataFrame({
        "review": ["battery is great", "terrible durability", "camera is blurry"] * 5,
        "rating": [5, 1, 2] * 5,
    })
    schema = detect_schema(df)
    enriched, reviews = analyze_custom_reviews(df, text_col="review", rating_col="rating")
    txns = analyze_custom_transactions(enriched)
    bundles, aspects = build_custom_analytics_bundles(
        df, schema, txns, reviews, None, None, profile_generic_table(enriched), enriched
    )
    assert set(aspects["aspect"]).issubset(set(ASPECT_LIST))
    assert bundles["exec_kpis"]["total_net_revenue"] is None
    assert bundles["exec_kpis"]["repeat_customer_rate_pct"] is None
    assert bundles["exec_kpis"]["total_customers"] is None


def test_bundles_never_contain_random_customers_or_products():
    from app.services.active_dataset_manager import build_custom_analytics_bundles
    from src.analytics.auto_analyzer import analyze_custom_reviews, analyze_custom_transactions, detect_schema, profile_generic_table

    df = pd.DataFrame({"review": ["fine product"] * 6, "rating": [4] * 6})
    schema = detect_schema(df)
    enriched, reviews = analyze_custom_reviews(df, text_col="review", rating_col="rating")
    txns = analyze_custom_transactions(enriched)
    results = []
    for _ in range(2):
        b, _ = build_custom_analytics_bundles(df, schema, txns, reviews, None, None, profile_generic_table(enriched), enriched)
        results.append(b)
    assert results[0]["cust_profiles"].empty and results[0]["prod_perf"].empty
    pd.testing.assert_frame_equal(results[0]["cust_profiles"], results[1]["cust_profiles"])


# ---------------------------------------------------------------- analytics metrics
def test_product_returned_units_count_units_not_orders():
    from src.analytics.product_analytics import generate_product_performance_metrics

    products = pd.DataFrame({"product_id": ["P1"], "product_name": ["A"], "category": ["X"], "price": [10.0]})
    txns = pd.DataFrame({
        "transaction_id": ["T1", "T2", "T3"],
        "product_id": ["P1", "P1", "P1"],
        "quantity": [2, 3, 4],
        "total_amount": [20.0, 30.0, 40.0],
        "return_status": ["Returned", "Returned", "Completed"],
    })
    reviews = pd.DataFrame({"review_id": ["R1"], "product_id": ["P1"], "rating": [4]})
    merged = generate_product_performance_metrics(products, txns, reviews)
    assert int(merged.loc[0, "returned_units"]) == 5
    assert int(merged.loc[0, "returned_orders"]) == 2


def test_segment_summary_works_with_partial_columns():
    from src.analytics.customer_analytics import get_segment_summary

    profiles = pd.DataFrame({"customer_id": ["A", "B", "C"], "customer_segment": ["X", "X", "Y"]})
    summary = get_segment_summary(profiles)
    assert set(summary["customer_segment"]) == {"X", "Y"}
    assert list(summary["customer_count"]) == [2, 1]


def test_mom_growth_is_none_without_two_months():
    from src.analytics.business_metrics import calculate_mom_growth

    one = pd.DataFrame({"year_month": ["2024-01"], "total_revenue": [100.0]})
    two = pd.DataFrame({"year_month": ["2024-01", "2024-02"], "total_revenue": [100.0, 150.0]})
    assert calculate_mom_growth(one) is None
    growth = calculate_mom_growth(two)
    assert growth["change_pct"] == 50.0
    assert growth["latest_month"] == "2024-02"


# ---------------------------------------------------------------- reports (escaping and N/A)
def test_report_escapes_user_supplied_label():
    from src.analytics.report_generator import generate_executive_html_report

    df = pd.DataFrame({"x": [1]})
    html_text = generate_executive_html_report(
        df=df,
        data_source_label="<script>alert('x')</script>",
        schema_info={},
        txn_data={"total_revenue": None},
        reviews_data=None,
    )
    assert "<script>alert" not in html_text
    assert "&lt;script&gt;" in html_text


def test_report_shows_na_for_unavailable_sentiment_metrics():
    from src.analytics.report_generator import generate_executive_html_report, generate_markdown_report

    reviews = {"total_reviews": 4, "labeled_reviews": 0, "positive_pct": None, "negative_pct": None,
               "avg_polarity": None, "aspect_summary": pd.DataFrame(), "sentiment_counts": {}}
    html_text = generate_executive_html_report(
        df=pd.DataFrame({"x": [1, 2]}), data_source_label="t", schema_info={},
        txn_data={"total_revenue": None}, reviews_data=reviews,
    )
    md = generate_markdown_report(df=pd.DataFrame({"x": [1]}), data_source_label="t",
                                  txn_data={"total_revenue": None}, reviews_data=reviews)
    assert "N/A" in html_text and "nan" not in html_text.lower().replace("finance", "")
    assert "**Positive Sentiment:** N/A" in md


def test_recommendations_do_not_claim_success_without_data():
    from src.analytics.report_generator import _recommendations

    items = _recommendations(None, {"total_revenue": None}, None)
    assert len(items) == 1 and "Add more data" in items[0]


def test_excel_workbook_strips_illegal_characters():
    from src.analytics.report_generator import generate_excel_analytical_workbook

    df = pd.DataFrame({"review_text": ["bad\x07char in review", "fine"]})
    data = generate_excel_analytical_workbook(enriched_df=df, data_source_label="t", txn_data={"total_revenue": None})
    sheets = pd.ExcelFile(io.BytesIO(data)).sheet_names
    assert "Enriched_Dataset" in sheets


# ---------------------------------------------------------------- recommendation evaluation (no leakage)
def test_evaluation_fits_popularity_only_on_history_before_cutoff(monkeypatch, tmp_path):
    import src.recommendation.evaluation as evaluation
    from src.recommendation.popularity import PopularityRecommender

    seen = {}
    original_fit = PopularityRecommender.fit

    def spy_fit(self, transactions_df, products_df, reviews_df):
        seen["tx_max"] = pd.to_datetime(transactions_df["transaction_date"]).max()
        seen["rev_max"] = pd.to_datetime(reviews_df["review_date"]).max()
        return original_fit(self, transactions_df, products_df, reviews_df)

    monkeypatch.setattr(PopularityRecommender, "fit", spy_fit)
    monkeypatch.setattr(evaluation, "METRICS_FILE", tmp_path / "metrics.json")
    result = evaluation.evaluate_models_chronological()

    cutoff = pd.Timestamp(result["training_cutoff"])
    assert seen["tx_max"] < cutoff
    assert seen["rev_max"] < cutoff
    assert result["winning_model"] in result["results_comparison"]
    assert result["winning_model"] in result["rationale"]


def test_evaluation_rationale_matches_the_numbers():
    metrics_file = PROJECT_ROOT / "models" / "evaluation_metrics.json"
    data = json.loads(metrics_file.read_text(encoding="utf-8"))
    table = data["results_comparison"]
    best = max(table, key=lambda m: table[m]["NDCG@10"])
    assert data["winning_model"] == best
    assert f"{table[best]['NDCG@10']:.4f}" in data["rationale"]


def test_sql_query2_units_are_not_multiplied_by_review_count():
    """Query 2 must sum units from transactions alone. Lower the review threshold so rows come back."""
    import re
    sql = (PROJECT_ROOT / "sql" / "analytical_queries.sql").read_text(encoding="utf-8")
    text = re.sub(r"--[^\n]*", "", sql)
    query2 = [s.strip() for s in text.split(";") if s.strip()][1]
    query2 = query2.replace("HAVING COUNT(DISTINCT review_id) >= 5", "HAVING COUNT(DISTINCT review_id) >= 1")

    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE products (product_id TEXT, product_name TEXT, category TEXT);
        CREATE TABLE transactions (transaction_id TEXT, product_id TEXT, quantity INTEGER);
        CREATE TABLE reviews (review_id TEXT, product_id TEXT, rating INTEGER);
        INSERT INTO products VALUES ('P1','A','X'),('P2','B','X'),('P3','C','X'),('P4','D','X');
        INSERT INTO transactions VALUES ('T1','P1',10),('T2','P2',1),('T3','P3',2),('T4','P4',3);
        INSERT INTO reviews VALUES ('R1','P1',1),('R2','P1',1),('R3','P1',2),('R4','P1',1),('R5','P1',1),
                                   ('R6','P2',5),('R7','P3',5),('R8','P4',5);
    """)
    rows = conn.execute(query2).fetchall()
    assert rows, "fixture should produce a flagged product"
    assert rows[0][0] == "P1"
    assert rows[0][3] == 10  # total_units_sold for P1, not 10 x 5 reviews


# ---------------------------------------------------------------- database
def test_database_rebuild_keeps_constraints_and_counts(tmp_path):
    from src.database.db_manager import DatabaseManager, CORE_TABLES

    db = DatabaseManager(db_path=tmp_path / "test.db")
    db.initialize_schema()
    db.load_processed_tables()
    db.initialize_schema()  # rebuilding must not leave stale or duplicate tables behind
    db.load_processed_tables()
    with sqlite3.connect(tmp_path / "test.db") as conn:
        pk_cols = [r[1] for r in conn.execute("PRAGMA table_info(transactions)") if r[5]]
        assert pk_cols == ["transaction_id"]
        counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in CORE_TABLES}
    assert counts["transactions"] == 1000
    assert counts["interactions"] == 3000


# ---------------------------------------------------------------- uploads and file access
def _zip_of(files: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def test_zip_member_limit_is_enforced():
    from src.analytics.multi_file_loader import load_zip_archive

    payload = _zip_of({f"f{i}.csv": "a,b\n1,2\n" for i in range(5)})
    with pytest.raises(ValueError):
        load_zip_archive(payload, max_members=3)


def test_zip_size_limit_is_enforced():
    from src.analytics.multi_file_loader import load_zip_archive

    payload = _zip_of({"big.csv": "a,b\n" + "1,2\n" * 1000})
    with pytest.raises(ValueError):
        load_zip_archive(payload, max_uncompressed_bytes=100)


def test_zip_keeps_same_named_files_from_different_folders():
    from src.analytics.multi_file_loader import load_zip_archive

    tables = load_zip_archive(_zip_of({"jan/sales.csv": "a\n1\n", "feb/sales.csv": "a\n2\n"}))
    assert set(tables) == {"jan/sales.csv", "feb/sales.csv"}


def test_local_scan_refuses_folders_outside_allowed_roots():
    from src.analytics.multi_file_loader import scan_local_directory

    with pytest.raises(PermissionError):
        scan_local_directory("/etc")
    with pytest.raises(PermissionError):
        scan_local_directory(PROJECT_ROOT / "..")


def test_local_scan_reads_project_data_directory():
    from src.analytics.multi_file_loader import scan_local_directory

    tables = scan_local_directory("data/processed")
    assert "transactions.csv" in tables


def test_join_skips_tables_whose_key_repeats():
    from src.analytics.multi_file_loader import auto_join_relational_tables

    orders = pd.DataFrame({"order_id": [1, 2, 3, 4], "customer_id": ["A", "A", "B", "C"], "amt": [1, 2, 3, 4]})
    dup_customers = pd.DataFrame({"customer_id": ["A", "A", "B"], "tier": ["g", "g", "s"]})
    joined, summary = auto_join_relational_tables({"orders.csv": orders, "customers.csv": dup_customers})
    assert len(joined) == 4  # no row repetition
    assert "customers.csv" in summary and "Not joined" in summary


# ---------------------------------------------------------------- API access control
def test_api_requires_key_when_configured(monkeypatch):
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    monkeypatch.setenv("API_KEY", "secret-123")
    assert client.get("/customers/CUST_00001").status_code == 401
    assert client.get("/customers/CUST_00001", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/customers/CUST_00001", headers={"X-API-Key": "secret-123"}).status_code == 200
    assert client.get("/health").status_code == 200  # liveness stays open


def test_api_cors_origins_are_configurable(monkeypatch):
    from api.main import DEFAULT_CORS_ORIGINS, _cors_origins

    monkeypatch.delenv("CORS_ALLOW_ORIGINS", raising=False)
    assert _cors_origins() == DEFAULT_CORS_ORIGINS.split(",")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "https://a.example, https://b.example ")
    assert _cors_origins() == ["https://a.example", "https://b.example"]


def test_default_demo_export_uses_product_categories_not_sku_ids():
    from app.services.active_dataset_manager import reset_to_default_demo_dataset, get_active_export_data
    reset_to_default_demo_dataset()
    html_bytes = get_active_export_data("html")
    html_str = html_bytes.decode("utf-8") if isinstance(html_bytes, bytes) else html_bytes
    assert "Electronics" in html_str
    assert "<td>PROD_0005</td>" not in html_str


def test_html_report_rfm_subtitle_reflects_recency_availability():
    from src.analytics.report_generator import generate_executive_html_report
    rfm_df = pd.DataFrame({"customer_id": ["C1", "C2"], "rfm_segment": ["Champions", "At Risk"]})
    rfm_metrics_with_rec = {
        "total_customers": 2,
        "recency_available": True,
        "champions_count": 1,
        "at_risk_count": 1,
        "avg_monetary": 100.0,
        "segment_summary": pd.DataFrame({"segment": ["Champions", "At Risk"], "count": [1, 1], "share_pct": [50.0, 50.0]}),
    }
    html_with_rec = generate_executive_html_report(
        df=pd.DataFrame({"x": [1, 2]}),
        data_source_label="Test",
        schema_info={},
        txn_data={"total_revenue": None},
        rfm_metrics=rfm_metrics_with_rec,
        rfm_df=rfm_df,
    )
    assert "High-value VIP accounts" in html_with_rec
    assert "Needs recency data" not in html_with_rec
