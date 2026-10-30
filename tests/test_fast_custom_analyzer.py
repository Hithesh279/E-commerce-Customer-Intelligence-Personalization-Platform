"""
tests/test_fast_custom_analyzer.py
Regression tests for Custom Data Analyzer performance optimizations:
1. Parser caching (CSV, Excel, ZIP, folder scan) without re-parsing on reruns.
2. Lazy report exports (HTML, Excel, Markdown, CSV) not built on dataset load.
3. Export cache key invalidation on column mapping changes.
4. clean_text_series vectorization output equivalence to clean_text.
5. Replacement of st.tabs with single-selection control using AppTest.
"""
import io
from pathlib import Path
import zipfile
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.analytics.multi_file_loader import (
    parse_tabular_file_cached,
    load_zip_archive_cached,
    scan_local_directory_cached,
    get_parser_call_count,
    reset_parser_call_count,
    compute_bytes_hash,
    compute_directory_signature,
)
from src.analytics.report_generator import (
    get_export_builder_call_counts,
    reset_export_builder_call_counts,
)
from app.services.active_dataset_manager import (
    set_active_custom_dataset,
    reset_to_default_demo_dataset,
    get_active_dataset_state,
    get_active_export_filename,
    get_active_export_data,
    compute_active_export_cache_key,
)
import threading
from src.nlp.preprocessing import clean_text, clean_text_series


def test_parser_caching_tabular_csv_and_excel():
    """Verify parse_tabular_file_cached parses bytes only once and reuses cache."""
    reset_parser_call_count()
    csv_bytes = b"customer_id,revenue\nC1,100\nC2,200\nC3,300\n"
    h = compute_bytes_hash(csv_bytes)

    # First call - cache miss
    df1 = parse_tabular_file_cached(
        _file_bytes=csv_bytes,
        filename="customers.csv",
        file_size=len(csv_bytes),
        file_hash=h,
    )
    assert len(df1) == 3
    assert get_parser_call_count() == 1

    # Second call with same signature - cache hit, parser count should NOT increment
    df2 = parse_tabular_file_cached(
        _file_bytes=csv_bytes,
        filename="customers.csv",
        file_size=len(csv_bytes),
        file_hash=h,
    )
    assert len(df2) == 3
    assert get_parser_call_count() == 1
    pd.testing.assert_frame_equal(df1, df2)

    # Different content - new parse
    csv_bytes_2 = b"customer_id,revenue\nC1,500\n"
    h2 = compute_bytes_hash(csv_bytes_2)
    df3 = parse_tabular_file_cached(
        _file_bytes=csv_bytes_2,
        filename="customers.csv",
        file_size=len(csv_bytes_2),
        file_hash=h2,
    )
    assert len(df3) == 1
    assert get_parser_call_count() == 2


def test_parser_caching_zip_archive():
    """Verify load_zip_archive_cached parses archive once and reuses cache on identical bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("orders.csv", "order_id,amount\n101,50.0\n102,75.0\n")
    zip_bytes = buf.getvalue()
    zh = compute_bytes_hash(zip_bytes)

    reset_parser_call_count()
    res1 = load_zip_archive_cached(
        _zip_bytes=zip_bytes,
        filename="test_orders.zip",
        file_size=len(zip_bytes),
        file_hash=zh,
    )
    assert len(res1) == 1
    count_after_first = get_parser_call_count()
    assert count_after_first >= 1

    # Second call - identical zip archive should be served completely from cache
    res2 = load_zip_archive_cached(
        _zip_bytes=zip_bytes,
        filename="test_orders.zip",
        file_size=len(zip_bytes),
        file_hash=zh,
    )
    assert len(res2) == 1
    assert get_parser_call_count() == count_after_first


def test_parser_caching_local_scan():
    """Verify scan_local_directory_cached does not re-read files if directory signature is unchanged."""
    reset_parser_call_count()
    dir_sig = compute_directory_signature("data/raw")
    scan1 = scan_local_directory_cached("data/raw", dir_sig)
    count_after_first = get_parser_call_count()
    assert len(scan1) > 0

    scan2 = scan_local_directory_cached("data/raw", dir_sig)
    assert len(scan2) == len(scan1)
    assert get_parser_call_count() == count_after_first


def test_lazy_exports_on_dataset_load():
    """Verify exports (HTML, Excel, Markdown) are NOT generated when dataset is set, only on demand."""
    reset_export_builder_call_counts()
    sample_df = pd.DataFrame({
        "order_id": ["O1", "O2", "O3"],
        "customer_id": ["C1", "C2", "C3"],
        "order_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "total_amount": [100.0, 200.0, 300.0],
        "review_text": ["Great product!", "Poor battery life.", "Fast shipping."],
    })

    # Setting active dataset must NOT build any exports eagerly
    set_active_custom_dataset(sample_df, source_label="Test Lazy Dataset")
    counts = get_export_builder_call_counts()
    assert counts["html"] == 0
    assert counts["excel"] == 0
    assert counts["markdown"] == 0

    # Demand HTML export only
    html_data = get_active_export_data("html")
    assert html_data is not None
    assert "<html" in str(html_data).lower()
    counts = get_export_builder_call_counts()
    assert counts["html"] == 1
    assert counts["excel"] == 0
    assert counts["markdown"] == 0

    # Second request for HTML should be cached
    html_data_cached = get_active_export_data("html")
    assert html_data_cached == html_data
    assert get_export_builder_call_counts()["html"] == 1

    # Demand Excel export
    excel_bytes = get_active_export_data("excel")
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0
    assert get_export_builder_call_counts()["excel"] == 1


def test_export_cache_key_invalidation_on_mapping_change():
    """Verify changing column mappings invalidates the cached exports and regenerates them."""
    sample_df = pd.DataFrame({
        "order_id": ["O1", "O2"],
        "customer_id": ["C1", "C2"],
        "gross_rev": [100.0, 200.0],
        "net_rev": [80.0, 160.0],
    })

    reset_export_builder_call_counts()

    # Initial mapping with gross_rev
    schema_1 = {
        "mappings": {
            "revenue_col": "gross_rev",
            "customer_col": "customer_id",
        }
    }
    sig_1 = ("Test DS", 2, tuple(sample_df.columns), "gross_rev", "customer_id")
    set_active_custom_dataset(
        sample_df,
        source_label="Test DS",
        schema_info=schema_1,
        analysis_sig=sig_1,
    )
    key_1 = compute_active_export_cache_key()

    # Generate HTML
    html_1 = get_active_export_data("html")
    assert get_export_builder_call_counts()["html"] == 1

    # User changes mapping to net_rev
    schema_2 = {
        "mappings": {
            "revenue_col": "net_rev",
            "customer_col": "customer_id",
        }
    }
    sig_2 = ("Test DS", 2, tuple(sample_df.columns), "net_rev", "customer_id")
    set_active_custom_dataset(
        sample_df,
        source_label="Test DS",
        schema_info=schema_2,
        analysis_sig=sig_2,
    )
    key_2 = compute_active_export_cache_key()

    # Keys must differ because column mappings changed
    assert key_1 != key_2

    # Requesting HTML export now must rebuild (cache miss)
    html_2 = get_active_export_data("html")
    assert get_export_builder_call_counts()["html"] == 2


def test_clean_text_series_equivalence_and_behavior():
    """Verify clean_text_series produces 100% equivalent outputs to clean_text on diverse inputs."""
    samples = [
        "I love this product! It won't break and can't fail http://example.com/test",
        "Terrible service, didn't arrive on time. Very bad quality 123! #fail",
        "Great battery life & amazing screen! Would definitely recommend to anyone.",
        "It's okay, but they're not very helpful with support.",
        "Fast delivery, 10/10 stars! www.shop.com/deal",
        "   Leading and trailing whitespace with multiple    spaces   ",
        "",
        "SingleWord",
        "12345 67890 !@#$%^&*()",
    ]
    series = pd.Series(samples)

    # Without stopword removal
    res_loop = series.apply(lambda t: clean_text(t, remove_stopwords=False))
    res_vec = clean_text_series(series, remove_stopwords=False)
    pd.testing.assert_series_equal(res_loop, res_vec)

    # With stopword removal
    res_loop_stop = series.apply(lambda t: clean_text(t, remove_stopwords=True))
    res_vec_stop = clean_text_series(series, remove_stopwords=True)
    pd.testing.assert_series_equal(res_loop_stop, res_vec_stop)


def test_apptest_tab_to_selector_replacement():
    """Verify with AppTest that st.tabs is replaced and single-selection control exists."""
    target_path = Path(__file__).resolve().parent.parent / "app" / "pages" / "custom_data_analyzer.py"
    at = AppTest.from_file(str(target_path), default_timeout=30)
    at.run()
    assert len(at.exception) == 0

    # Ensure no st.tabs elements are created on initial load
    assert len(at.tabs) == 0

    # Click Load & Analyze for the default template
    assert len(at.button) > 0
    at.button[0].click().run()
    assert len(at.exception) == 0

    # After loading the dataset, tabs must still be 0 (replaced by segmented control or radio)
    assert len(at.tabs) == 0
    # Single-selection control present
    has_segmented_or_radio = len(at.button_group) > 0 or len(at.radio) > 0
    assert has_segmented_or_radio


def test_active_dataset_export_contains_uploaded_data():
    """Verify downloaded exports contain the user's uploaded data rather than default demo data."""
    uploaded_df = pd.DataFrame({
        "order_id": ["CUSTOM_ORD_101", "CUSTOM_ORD_102"],
        "customer_id": ["SPECIAL_CUST_999", "SPECIAL_CUST_888"],
        "order_date": ["2026-03-01", "2026-03-02"],
        "product_id": ["UNIQUE_PROD_A", "UNIQUE_PROD_B"],
        "total_amount": [777.50, 888.50],
        "review_text": ["Super unique custom review!", "Another custom feedback."],
    })

    set_active_custom_dataset(uploaded_df, source_label="My Custom User Upload")

    # CSV export must contain the uploaded data markers
    csv_bytes = get_active_export_data("csv")
    csv_str = csv_bytes.decode("utf-8") if isinstance(csv_bytes, bytes) else csv_bytes
    assert "SPECIAL_CUST_999" in csv_str
    assert "UNIQUE_PROD_A" in csv_str
    assert "777.5" in csv_str
    # Must NOT be the bundled demo transactions
    assert "CUST-0001" not in csv_str

    # Filename must reflect uploaded dataset name
    csv_filename = get_active_export_filename("csv")
    assert "my_custom_user_upload" in csv_filename.lower()

    # Markdown export must reference custom dataset
    md_bytes = get_active_export_data("md")
    md_str = md_bytes.decode("utf-8") if isinstance(md_bytes, bytes) else md_bytes
    assert "My Custom User Upload" in md_str

    # Clean up back to default
    reset_to_default_demo_dataset()


def test_download_in_worker_thread_without_script_context_retains_uploaded_data():
    """
    Simulate Tornado's worker thread handling st.download_button click callback.
    When executed in a separate thread without Streamlit ScriptRunContext,
    download callbacks must still return the uploaded user data.
    """
    uploaded_df = pd.DataFrame({
        "order_id": ["THREAD_ORD_1", "THREAD_ORD_2"],
        "customer_id": ["THREAD_CUST_777", "THREAD_CUST_888"],
        "order_date": ["2026-04-01", "2026-04-02"],
        "product_id": ["THREAD_PROD_X", "THREAD_PROD_Y"],
        "total_amount": [1234.56, 6543.21],
    })

    state = set_active_custom_dataset(uploaded_df, source_label="Thread Test Upload")

    # Capture closure lambda like render_download_panel does
    download_lambda = lambda s=state: get_active_export_data("csv", state=s)

    results = {}

    def worker():
        # This thread has no Streamlit ScriptRunContext
        results["via_closure"] = download_lambda()
        results["via_direct_call"] = get_active_export_data("csv")

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    # Check that closure execution in thread returned uploaded data
    csv_closure = results["via_closure"].decode("utf-8")
    assert "THREAD_CUST_777" in csv_closure
    assert "1234.56" in csv_closure

    # Check that direct call in thread also returned uploaded data via module fallback
    csv_direct = results["via_direct_call"].decode("utf-8")
    assert "THREAD_CUST_777" in csv_direct
    assert "1234.56" in csv_direct

    # Clean up
    reset_to_default_demo_dataset()
    assert get_active_dataset_state() is None
