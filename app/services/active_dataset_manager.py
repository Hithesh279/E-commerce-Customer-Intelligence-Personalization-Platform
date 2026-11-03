"""
app/services/active_dataset_manager.py
Global active dataset management and state orchestration for Streamlit.
Ensures that once a dataset is uploaded or a template is selected, the entire
application (Main, Overview, Customer Intelligence, Product Intelligence,
NLP Voice, Recommendations) updates synchronously to display everything related
to that data, and enables 1-click downloads of the entire dashboard across all pages.
"""
import base64
from datetime import datetime
import hashlib
import html
import io
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import streamlit as st

from src.analytics.customer_analytics import get_segment_summary
from src.analytics.auto_analyzer import (
    analyze_custom_reviews,
    analyze_custom_transactions,
    calculate_custom_rfm,
    detect_schema,
    profile_generic_table,
)
from src.analytics.report_generator import (
    generate_excel_analytical_workbook,
    generate_executive_html_report,
    generate_markdown_report,
)
from src.analytics.templates import (
    TEMPLATES_CONFIG,
    load_sample_template,
)
from src import __version__ as PLATFORM_VERSION
from src.utils.config import (
    DATABASE_PATH,
    METRICS_FILE,
    MODELS_RECOMMENDATION_DIR,
    MODELS_SENTIMENT_DIR,
    POWERBI_DATA_DIR,
    PROJECT_ROOT,
    PROCESSED_DATA_DIR,
)
from src.utils.logging import get_logger

logger = get_logger("active_dataset_manager")


def _should_persist_exports_to_disk() -> bool:
    """Skip writing temporary export files to disk during automated test runs."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    return True


def get_default_demo_summary() -> Dict[str, int]:
    """Row counts of the bundled demo store, read from the processed files."""
    summary = {}
    for name in ["customers", "products", "transactions", "reviews"]:
        path = PROCESSED_DATA_DIR / f"{name}.csv"
        summary[name] = len(pd.read_csv(path, usecols=[0])) if path.exists() else 0
    return summary


def get_system_status() -> List[Tuple[str, bool]]:
    """Real file-existence checks for the sidebar status panel."""
    return [
        ("Relational database", DATABASE_PATH.exists()),
        ("Sentiment model", (MODELS_SENTIMENT_DIR / "model.joblib").exists()),
        ("Recommendation models", (MODELS_RECOMMENDATION_DIR / "collaborative_model.joblib").exists()),
        ("Evaluation metrics", METRICS_FILE.exists()),
    ]


def platform_version() -> str:
    return PLATFORM_VERSION


def _is_streamlit_running() -> bool:
    """Check if code is running inside an active Streamlit runtime context."""
    try:
        return hasattr(st, "session_state") and st.session_state is not None
    except Exception:
        return False


_DEFAULT_DEMO_BUNDLES_CACHE: Optional[Dict[str, Any]] = None
_MODULE_ACTIVE_DATASET: Optional[Dict[str, Any]] = None
_GLOBAL_EXPORT_CACHE: Dict[Tuple[str, str], Union[bytes, str]] = {}


def get_default_demo_bundles() -> Dict[str, Any]:
    """Compute and cache analytics bundles from default processed demo dataset."""
    global _DEFAULT_DEMO_BUNDLES_CACHE
    if _DEFAULT_DEMO_BUNDLES_CACHE is not None:
        return _DEFAULT_DEMO_BUNDLES_CACHE

    from src.analytics.business_metrics import (
        calculate_category_performance,
        calculate_executive_kpis,
        calculate_monthly_revenue_trend,
    )
    from src.analytics.customer_analytics import (
        generate_customer_profile_metrics,
        get_segment_summary,
    )
    from src.analytics.product_analytics import generate_product_performance_metrics

    cust_df = pd.read_csv(PROCESSED_DATA_DIR / "customers.csv")
    prod_df = pd.read_csv(PROCESSED_DATA_DIR / "products.csv")
    txns_df = pd.read_csv(PROCESSED_DATA_DIR / "transactions.csv")
    rev_df = pd.read_csv(PROCESSED_DATA_DIR / "reviews.csv")

    exec_kpis = calculate_executive_kpis(cust_df, txns_df, rev_df)
    monthly_trend = calculate_monthly_revenue_trend(txns_df)
    cat_perf = calculate_category_performance(prod_df, txns_df, rev_df)
    cust_profiles = generate_customer_profile_metrics(cust_df, txns_df, rev_df)
    seg_summary = get_segment_summary(cust_profiles)
    prod_perf = generate_product_performance_metrics(prod_df, txns_df, rev_df)

    res = {
        "exec_kpis": exec_kpis,
        "monthly_trend": monthly_trend,
        "cat_perf": cat_perf,
        "cust_profiles": cust_profiles,
        "seg_summary": seg_summary,
        "prod_perf": prod_perf,
        "reviews_data": None,
        "aspects_df": pd.DataFrame(),
        "has_transactions": True,
        "has_reviews": True,
    }
    _DEFAULT_DEMO_BUNDLES_CACHE = res
    return res


PRODUCT_COLUMNS = [
    "product_id", "product_name", "category", "price", "units_sold", "total_orders", "net_revenue",
    "gross_revenue", "returned_units", "return_rate", "review_count", "average_rating",
    "positive_sentiment_pct", "negative_sentiment_pct", "is_high_sales_low_sentiment",
    "is_low_sales_high_sentiment", "product_description",
]
PROFILE_COLUMNS = [
    "customer_id", "customer_segment", "rfm_segment", "rfm_score", "recency_days",
    "total_orders", "net_spend", "average_order_value",
]
ASPECT_COLUMNS = ["aspect", "review_id", "sentiment", "sentiment_score", "snippet"]


def build_custom_analytics_bundles(
    df: pd.DataFrame,
    schema_info: Dict[str, Any],
    txn_data: Dict[str, Any],
    reviews_data: Optional[Dict[str, Any]],
    rfm_df: Optional[pd.DataFrame],
    rfm_metrics: Optional[Dict[str, Any]],
    table_profile: Dict[str, Any],
    enriched_df: pd.DataFrame,
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Build the bundles every dashboard page reads for an uploaded dataset.

    Only values derived from the uploaded data are used. A metric whose source column is missing is
    None (shown as "N/A"), and a chart without data is an empty DataFrame with the expected columns.
    Nothing is generated to fill a gap.
    """
    mappings = schema_info.get("detected_mappings") or schema_info.get("mappings") or {}
    customer_col = mappings.get("customer_col")
    has_txns = txn_data.get("total_revenue") is not None
    has_revs = reviews_data is not None

    # 1. Executive KPIs (None where the dataset does not provide the input)
    total_rev = txn_data.get("total_revenue")
    total_orders = txn_data.get("total_orders")
    aov = txn_data.get("aov")
    return_rate = txn_data.get("return_rate")

    avg_rating = pos_pct = neg_pct = neu_pct = None
    if reviews_data is not None:
        avg_rating = reviews_data.get("avg_rating")
        pos_pct = reviews_data.get("positive_pct")
        neg_pct = reviews_data.get("negative_pct")
        neu_pct = reviews_data.get("neutral_pct")

    repeat_rate = None
    if rfm_df is not None and not rfm_df.empty and "frequency" in rfm_df.columns:
        repeat_rate = round(float((rfm_df["frequency"] > 1).mean() * 100), 1)

    total_cust = None
    if rfm_metrics is not None:
        total_cust = rfm_metrics.get("total_customers")
    elif customer_col and customer_col in df.columns:
        total_cust = int(df[customer_col].nunique())

    net_sentiment = round(pos_pct - neg_pct, 1) if pos_pct is not None and neg_pct is not None else None
    exec_kpis = {
        "total_gross_revenue": None,  # no separate gross column in an uploaded file
        "total_net_revenue": total_rev,
        "total_orders": total_orders,
        "total_customers": total_cust,
        "average_order_value": aov,
        "overall_return_rate_pct": return_rate,
        "repeat_customer_rate_pct": repeat_rate,
        "average_rating": avg_rating,
        "positive_sentiment_pct": pos_pct,
        "neutral_sentiment_pct": neu_pct,
        "negative_sentiment_pct": neg_pct,
        "net_sentiment_score": net_sentiment,
        "has_transactions": has_txns,
        "has_reviews": has_revs,
    }

    # 2. Monthly trend: only from a real date column with a revenue column
    timeline_df = txn_data.get("timeline_df")
    if isinstance(timeline_df, pd.DataFrame) and not timeline_df.empty:
        monthly_trend = timeline_df.rename(
            columns={"period": "year_month", "revenue": "total_revenue", "orders": "order_count"}
        )
    else:
        monthly_trend = pd.DataFrame(columns=["year_month", "total_revenue", "order_count"])

    # 3. Category performance: only from a real category column with a revenue column
    cat_df = txn_data.get("category_df")
    if isinstance(cat_df, pd.DataFrame) and not cat_df.empty:
        cat_perf = cat_df.rename(columns={cat_df.columns[0]: "category"}).copy()
    else:
        cat_perf = pd.DataFrame(columns=["category", "revenue", "orders", "share_pct"])

    # 4. Customer profiles and segments: only from computed RFM output
    if rfm_df is not None and not rfm_df.empty and customer_col and customer_col in rfm_df.columns:
        spend = pd.to_numeric(rfm_df["monetary_total"], errors="coerce")
        orders = pd.to_numeric(rfm_df["frequency"], errors="coerce")
        cust_profiles = pd.DataFrame({
            "customer_id": rfm_df[customer_col].astype(str),
            "customer_segment": rfm_df["rfm_segment"],
            "rfm_segment": rfm_df["rfm_segment"],
            "rfm_score": rfm_df["rfm_score"],
            "recency_days": rfm_df["recency_days"],
            "total_orders": orders,
            "net_spend": spend,
            "average_order_value": (spend / orders.clip(lower=1)).round(2),
        })
    else:
        cust_profiles = pd.DataFrame(columns=PROFILE_COLUMNS)
    seg_summary = get_segment_summary(cust_profiles)

    # 5. Product performance: only from a real product column in the transactions
    top_p = txn_data.get("top_products_df")
    if isinstance(top_p, pd.DataFrame) and not top_p.empty:
        names = top_p[top_p.columns[0]].astype(str)
        prod_perf = pd.DataFrame({
            "product_id": names,
            "product_name": names,
            "category": None,
            "price": None,
            "units_sold": None,
            "total_orders": top_p["orders"] if "orders" in top_p.columns else None,
            "net_revenue": top_p["revenue"] if "revenue" in top_p.columns else None,
            "gross_revenue": None,
            "returned_units": None,
            "return_rate": None,
            "review_count": None,
            "average_rating": None,
            "positive_sentiment_pct": None,
            "negative_sentiment_pct": None,
            "is_high_sales_low_sentiment": False,
            "is_low_sales_high_sentiment": False,
            "product_description": None,
        })
    else:
        prod_perf = pd.DataFrame(columns=PRODUCT_COLUMNS)

    # 6. Aspect observations: the real extracted mentions, nothing else
    aspect_records = (reviews_data or {}).get("aspect_records", [])
    if aspect_records:
        aspects_df = pd.DataFrame(aspect_records)
        aspects_df["review_id"] = aspects_df["review_row"].map(lambda i: f"ROW-{int(i) + 1}")
        aspects_df = aspects_df[ASPECT_COLUMNS]
    else:
        aspects_df = pd.DataFrame(columns=ASPECT_COLUMNS)

    bundles = {
        "exec_kpis": exec_kpis,
        "monthly_trend": monthly_trend,
        "cat_perf": cat_perf,
        "cust_profiles": cust_profiles,
        "seg_summary": seg_summary,
        "prod_perf": prod_perf,
        "reviews_data": reviews_data,
        "aspects_df": aspects_df,
        "has_transactions": has_txns,
        "has_reviews": has_revs,
    }
    return bundles, aspects_df


def set_active_custom_dataset(
    df: pd.DataFrame,
    source_label: str,
    schema_info: Optional[Dict[str, Any]] = None,
    txn_data: Optional[Dict[str, Any]] = None,
    reviews_data: Optional[Dict[str, Any]] = None,
    rfm_df: Optional[pd.DataFrame] = None,
    rfm_metrics: Optional[Dict[str, Any]] = None,
    table_profile: Optional[Dict[str, Any]] = None,
    enriched_df: Optional[Dict[str, Any]] = None,
    analysis_sig: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Set and store the active dataset across the entire application.
    Automatically executes ML inference and aggregates bundles if not pre-computed.
    """
    if schema_info is None:
        schema_info = detect_schema(df)

    mappings = schema_info.get("detected_mappings") or schema_info.get("mappings") or {}

    if enriched_df is None:
        enriched_df = df.copy()
        text_col = mappings.get("text_col")
        rating_col = mappings.get("rating_col")
        sentiment_col = mappings.get("sentiment_col")
        if (text_col and text_col in df.columns) or (sentiment_col and sentiment_col in df.columns) or (rating_col and rating_col in df.columns):
            enriched_df, reviews_data = analyze_custom_reviews(
                df,
                text_col=text_col,
                rating_col=rating_col,
                sentiment_col=sentiment_col,
            )

    assert enriched_df is not None

    if txn_data is None:
        txn_data = analyze_custom_transactions(
            enriched_df,
            date_col=mappings.get("date_col"),
            revenue_col=mappings.get("revenue_col"),
            customer_col=mappings.get("customer_col"),
            category_col=mappings.get("category_col"),
            product_col=mappings.get("product_col"),
            status_col=mappings.get("status_col"),
        )

    if rfm_df is None and mappings.get("customer_col"):
        try:
            rfm_df, rfm_metrics = calculate_custom_rfm(
                enriched_df,
                customer_col=mappings.get("customer_col"),
                date_col=mappings.get("date_col"),
                revenue_col=mappings.get("revenue_col"),
            )
        except Exception as e:
            logger.warning(f"RFM calculation skipped: {e}")
            rfm_df, rfm_metrics = None, None

    if table_profile is None:
        table_profile = profile_generic_table(enriched_df)

    bundles, aspects_df = build_custom_analytics_bundles(
        df=df,
        schema_info=schema_info,
        txn_data=txn_data,
        reviews_data=reviews_data,
        rfm_df=rfm_df,
        rfm_metrics=rfm_metrics,
        table_profile=table_profile,
        enriched_df=enriched_df,
    )

    dataset_state = {
        "is_custom_active": True,
        "dataset_name": source_label,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "raw_df": df,
        "enriched_df": enriched_df,
        "schema_info": schema_info,
        "txn_data": txn_data,
        "reviews_data": reviews_data,
        "rfm_df": rfm_df,
        "rfm_metrics": rfm_metrics,
        "table_profile": table_profile,
        "bundles": bundles,
        "aspects_df": aspects_df,
        "row_count": len(df),
        "col_count": len(df.columns),
        "analysis_sig": analysis_sig,
    }

    global _MODULE_ACTIVE_DATASET, _GLOBAL_EXPORT_CACHE
    _MODULE_ACTIVE_DATASET = dataset_state
    _GLOBAL_EXPORT_CACHE.clear()

    if _is_streamlit_running():
        try:
            cache_key = compute_active_export_cache_key_for_state(dataset_state)
            old_key = st.session_state.get("_cached_active_reports_key")
            if old_key != cache_key:
                st.session_state.pop("_cached_active_reports", None)
                st.session_state.pop("_cached_active_reports_key", None)
                for fmt in ["html", "excel", "md", "csv"]:
                    st.session_state.pop(f"_cached_export_{fmt}", None)
                    st.session_state.pop(f"_cached_export_{fmt}_key", None)
            st.session_state["active_dataset"] = dataset_state
            st.session_state["is_custom_active"] = True
            st.session_state["active_dataset_name"] = source_label
        except Exception:
            pass

    logger.info(f"Active platform dataset set to: '{source_label}' with {len(df):,} rows.")
    return dataset_state


def load_template_as_active_dataset(template_id: str) -> Dict[str, Any]:
    """Generate and activate one of the 12 pre-built enterprise templates."""
    cfg = TEMPLATES_CONFIG.get(template_id)
    if not cfg:
        raise ValueError(f"Unknown template: {template_id}")

    sample_df = load_sample_template(template_id)
    label = f"Template: {cfg['name']}"
    return set_active_custom_dataset(sample_df, source_label=label)


def reset_to_default_demo_dataset():
    """Reset the platform back to the default e-commerce store dataset."""
    global _MODULE_ACTIVE_DATASET, _GLOBAL_EXPORT_CACHE
    _MODULE_ACTIVE_DATASET = None
    _GLOBAL_EXPORT_CACHE.clear()
    if _is_streamlit_running():
        try:
            if "active_dataset" in st.session_state:
                del st.session_state["active_dataset"]
            st.session_state["is_custom_active"] = False
            st.session_state["active_dataset_name"] = "Default Demo Store Data"
            st.session_state.pop("_cached_active_reports", None)
            st.session_state.pop("_cached_active_reports_key", None)
            st.session_state.pop("_analyzer_cache_sig", None)
            for fmt in ["html", "excel", "md", "csv"]:
                st.session_state.pop(f"_cached_export_{fmt}", None)
                st.session_state.pop(f"_cached_export_{fmt}_key", None)
        except Exception:
            pass
    logger.info("Platform dataset reset to default processed demo dataset.")


def get_active_dataset_state() -> Optional[Dict[str, Any]]:
    """Retrieve the current active dataset state dict, or None if default."""
    if _is_streamlit_running():
        try:
            if st.session_state.get("is_custom_active", False) and "active_dataset" in st.session_state:
                return st.session_state["active_dataset"]
        except Exception:
            pass
    global _MODULE_ACTIVE_DATASET
    return _MODULE_ACTIVE_DATASET


def get_active_bundles() -> Dict[str, Any]:
    """
    Central provider of analytics bundles for all platform pages.
    Seamlessly returns active custom dataset bundles if loaded, or defaults to demo data.
    """
    state = get_active_dataset_state()
    if state is not None and "bundles" in state:
        return state["bundles"]
    return get_default_demo_bundles()


_DEFAULT_ASPECTS_CACHE: Optional[pd.DataFrame] = None


def get_active_aspects_df() -> pd.DataFrame:
    """
    Central provider of aspect sentiment observations for NLP Insights page.
    Returns custom extracted aspects if active, or default review_aspects.csv.
    """
    global _DEFAULT_ASPECTS_CACHE
    state = get_active_dataset_state()
    if state is not None and "aspects_df" in state and not state["aspects_df"].empty:
        return state["aspects_df"]

    if _DEFAULT_ASPECTS_CACHE is not None:
        return _DEFAULT_ASPECTS_CACHE

    path = PROCESSED_DATA_DIR / "review_aspects.csv"
    if path.exists():
        _DEFAULT_ASPECTS_CACHE = pd.read_csv(path)
        return _DEFAULT_ASPECTS_CACHE
    return pd.DataFrame()


_DEFAULT_DEMO_REPORTS_CACHE: Optional[Dict[str, Any]] = None


def compute_active_export_cache_key_for_state(state: Optional[Dict[str, Any]]) -> str:
    """Compute an invalidated-on-change cache key for active dataset exports."""
    if state is None:
        return "default_demo"

    dataset_name = state.get("dataset_name", "")
    row_count = state.get("row_count", 0)
    col_count = state.get("col_count", 0)

    schema_info = state.get("schema_info") or {}
    mappings = schema_info.get("detected_mappings") or schema_info.get("mappings") or {}

    sig_parts = [
        str(dataset_name),
        str(row_count),
        str(col_count),
        repr(sorted((k, str(v)) for k, v in mappings.items())),
    ]
    if "analysis_sig" in state and state["analysis_sig"] is not None:
        sig_parts.append(repr(state["analysis_sig"]))

    sig_hash = hashlib.sha256("::".join(sig_parts).encode("utf-8")).hexdigest()[:16]
    return f"{dataset_name}_{row_count}_{col_count}_{sig_hash}"


def compute_active_export_cache_key(state: Optional[Dict[str, Any]] = None) -> str:
    """Compute the current export cache key based on the active dataset state."""
    if state is None:
        state = get_active_dataset_state()
    return compute_active_export_cache_key_for_state(state)


def get_active_export_filename(
    export_format: str,
    state: Optional[Dict[str, Any]] = None,
) -> str:
    """Get the standard output filename for a given export format."""
    if state is None:
        state = get_active_dataset_state()
    label = state["dataset_name"] if state else "Default Demo Store Data"
    ts = datetime.now().strftime("%Y%m%d")
    clean_prefix = "".join(c if c.isalnum() else "_" for c in label.lower()).strip("_")
    if export_format == "html":
        return f"executive_analytics_report_{clean_prefix}_{ts}.html"
    elif export_format == "excel":
        return f"analytical_workbook_{clean_prefix}_{ts}.xlsx"
    elif export_format == "md":
        return f"executive_briefing_{clean_prefix}_{ts}.md"
    elif export_format == "csv":
        return f"dataset_{clean_prefix}_{ts}.csv"
    return f"export_{clean_prefix}_{ts}.dat"


def get_cached_export(
    export_format: str,
    state: Optional[Dict[str, Any]] = None,
) -> Optional[Union[bytes, str]]:
    """Retrieve pre-built export content from session_state or memory cache if available."""
    if state is None:
        state = get_active_dataset_state()
    cache_key = compute_active_export_cache_key_for_state(state)
    global _GLOBAL_EXPORT_CACHE
    if (export_format, cache_key) in _GLOBAL_EXPORT_CACHE:
        return _GLOBAL_EXPORT_CACHE[(export_format, cache_key)]
    if _is_streamlit_running():
        try:
            session_k = f"_cached_export_{export_format}"
            session_key_k = f"_cached_export_{export_format}_key"
            if st.session_state.get(session_key_k) == cache_key:
                return st.session_state.get(session_k)
        except Exception:
            pass
    return None


def _prepare_default_demo_export_inputs():
    """Prepare enriched transaction, review, and RFM structures for the Default Demo Store."""
    label = "Default Demo Store Data"
    txns_df = pd.read_csv(PROCESSED_DATA_DIR / "transactions.csv")
    rev_df = pd.read_csv(PROCESSED_DATA_DIR / "reviews.csv")
    prod_df = pd.read_csv(PROCESSED_DATA_DIR / "products.csv")

    df = txns_df.merge(
        prod_df[["product_id", "product_name", "category"]],
        on="product_id",
        how="left",
    )
    schema_info = detect_schema(df)
    txn_data = analyze_custom_transactions(
        df,
        date_col="transaction_date",
        revenue_col="total_amount",
        customer_col="customer_id",
        category_col="category",
        product_col="product_name",
        status_col="return_status",
    )
    _, reviews_data = analyze_custom_reviews(rev_df, text_col="review_text", rating_col="rating")
    rfm_df, rfm_metrics = calculate_custom_rfm(
        df,
        customer_col="customer_id",
        date_col="transaction_date",
        revenue_col="total_amount",
    )
    return df, label, schema_info, txn_data, reviews_data, rfm_df, rfm_metrics


def get_active_export_data(
    export_format: str,
    state: Optional[Dict[str, Any]] = None,
) -> Union[bytes, str]:
    """
    Lazily build and return data for a single export format ('html', 'excel', 'md', 'csv').
    Does NOT build other formats. Auto-saves to exports/ on generation (when not running pytest) and caches results.
    """
    if state is None:
        state = get_active_dataset_state()

    cache_key = compute_active_export_cache_key_for_state(state)
    session_k = f"_cached_export_{export_format}"
    session_key_k = f"_cached_export_{export_format}_key"

    global _GLOBAL_EXPORT_CACHE
    if (export_format, cache_key) in _GLOBAL_EXPORT_CACHE:
        return _GLOBAL_EXPORT_CACHE[(export_format, cache_key)]

    if _is_streamlit_running():
        try:
            cached_val = st.session_state.get(session_k)
            if cached_val is not None and st.session_state.get(session_key_k) == cache_key:
                _GLOBAL_EXPORT_CACHE[(export_format, cache_key)] = cached_val
                return cached_val
        except Exception:
            pass

    if state is not None:
        df = state["enriched_df"]
        label = state["dataset_name"]
        schema_info = state["schema_info"]
        txn_data = state["txn_data"]
        reviews_data = state["reviews_data"]
        rfm_metrics = state["rfm_metrics"]
        rfm_df = state["rfm_df"]
    else:
        df, label, schema_info, txn_data, reviews_data, rfm_df, rfm_metrics = _prepare_default_demo_export_inputs()

    exports_dir = Path(__file__).resolve().parent.parent.parent / "exports"
    filename = get_active_export_filename(export_format, state=state)
    file_path = exports_dir / filename
    persist = _should_persist_exports_to_disk()
    if persist:
        exports_dir.mkdir(exist_ok=True, parents=True)

    if export_format == "html":
        content = generate_executive_html_report(
            df=df,
            data_source_label=label,
            schema_info=schema_info,
            txn_data=txn_data,
            reviews_data=reviews_data,
            rfm_metrics=rfm_metrics,
            rfm_df=rfm_df,
        )
        if persist:
            try:
                file_path.write_text(content, encoding="utf-8")
            except Exception as e:
                logger.warning(f"Could not auto-save {filename}: {e}")
        res = content.encode("utf-8")
    elif export_format == "excel":
        content = generate_excel_analytical_workbook(
            enriched_df=df,
            data_source_label=label,
            txn_data=txn_data,
            reviews_data=reviews_data,
            rfm_df=rfm_df,
            rfm_metrics=rfm_metrics,
        )
        if persist:
            try:
                file_path.write_bytes(content)
            except Exception as e:
                logger.warning(f"Could not auto-save {filename}: {e}")
        res = content
    elif export_format == "md":
        content = generate_markdown_report(
            df=df,
            data_source_label=label,
            txn_data=txn_data,
            reviews_data=reviews_data,
            rfm_metrics=rfm_metrics,
        )
        if persist:
            try:
                file_path.write_text(content, encoding="utf-8")
            except Exception as e:
                logger.warning(f"Could not auto-save {filename}: {e}")
        res = content.encode("utf-8")
    elif export_format == "csv":
        content = df.to_csv(index=False).encode("utf-8")
        if persist:
            try:
                file_path.write_bytes(content)
            except Exception as e:
                logger.warning(f"Could not auto-save {filename}: {e}")
        res = content
    else:
        raise ValueError(f"Unknown export format: {export_format}")

    _GLOBAL_EXPORT_CACHE[(export_format, cache_key)] = res
    if _is_streamlit_running():
        try:
            st.session_state[session_k] = res
            st.session_state[session_key_k] = cache_key
        except Exception:
            pass

    return res


def generate_active_dashboard_reports(state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate complete export suite for the active platform dataset:
    HTML/PDF executive report, multi-sheet Excel workbook, Markdown briefing, and CSV.
    Caches results in session_state and memory to ensure instant UI rendering.
    """
    global _DEFAULT_DEMO_REPORTS_CACHE, _GLOBAL_EXPORT_CACHE
    if state is None:
        state = get_active_dataset_state()

    # For default demo dataset, return instant module-level cache if available
    if state is None and _DEFAULT_DEMO_REPORTS_CACHE is not None:
        return _DEFAULT_DEMO_REPORTS_CACHE

    cache_key = compute_active_export_cache_key_for_state(state)

    if _is_streamlit_running():
        try:
            cached = st.session_state.get("_cached_active_reports")
            cached_key = st.session_state.get("_cached_active_reports_key")
            if cached is not None and cached_key == cache_key:
                return cached
        except Exception:
            pass

    if state is not None:
        df = state["enriched_df"]
        label = state["dataset_name"]
        schema_info = state["schema_info"]
        txn_data = state["txn_data"]
        reviews_data = state["reviews_data"]
        rfm_metrics = state["rfm_metrics"]
        rfm_df = state["rfm_df"]
    else:
        df, label, schema_info, txn_data, reviews_data, rfm_df, rfm_metrics = _prepare_default_demo_export_inputs()

    html_report = generate_executive_html_report(
        df=df,
        data_source_label=label,
        schema_info=schema_info,
        txn_data=txn_data,
        reviews_data=reviews_data,
        rfm_metrics=rfm_metrics,
        rfm_df=rfm_df,
    )

    excel_bytes = generate_excel_analytical_workbook(
        enriched_df=df,
        data_source_label=label,
        txn_data=txn_data,
        reviews_data=reviews_data,
        rfm_df=rfm_df,
        rfm_metrics=rfm_metrics,
    )

    md_report = generate_markdown_report(
        df=df,
        data_source_label=label,
        txn_data=txn_data,
        reviews_data=reviews_data,
        rfm_metrics=rfm_metrics,
    )

    csv_bytes = df.to_csv(index=False).encode("utf-8")

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    clean_prefix = "".join(c if c.isalnum() else "_" for c in label.lower()).strip("_")

    exports_dir = Path(__file__).resolve().parent.parent.parent / "exports"
    html_filename = f"executive_analytics_report_{clean_prefix}_{ts}.html"
    excel_filename = f"analytical_workbook_{clean_prefix}_{ts}.xlsx"
    md_filename = f"executive_briefing_{clean_prefix}_{ts}.md"
    csv_filename = f"dataset_{clean_prefix}_{ts}.csv"

    html_path = exports_dir / html_filename
    excel_path = exports_dir / excel_filename
    md_path = exports_dir / md_filename
    csv_path = exports_dir / csv_filename

    if _should_persist_exports_to_disk():
        exports_dir.mkdir(exist_ok=True, parents=True)
        try:
            html_path.write_text(html_report, encoding="utf-8")
            excel_path.write_bytes(excel_bytes)
            md_path.write_text(md_report, encoding="utf-8")
            csv_path.write_bytes(csv_bytes)
        except Exception as e:
            logger.warning(f"Could not auto-save export files to disk: {e}")

    html_bytes = html_report.encode("utf-8")
    md_bytes = md_report.encode("utf-8")

    _GLOBAL_EXPORT_CACHE[("html", cache_key)] = html_bytes
    _GLOBAL_EXPORT_CACHE[("excel", cache_key)] = excel_bytes
    _GLOBAL_EXPORT_CACHE[("md", cache_key)] = md_bytes
    _GLOBAL_EXPORT_CACHE[("csv", cache_key)] = csv_bytes

    reports_suite = {
        "html_report": html_report,
        "excel_bytes": excel_bytes,
        "md_report": md_report,
        "csv_bytes": csv_bytes,
        "html_filename": html_filename,
        "excel_filename": excel_filename,
        "md_filename": md_filename,
        "csv_filename": csv_filename,
        "html_path": str(html_path),
        "excel_path": str(excel_path),
        "md_path": str(md_path),
        "csv_path": str(csv_path),
        "b64_html": base64.b64encode(html_bytes).decode("utf-8"),
        "b64_excel": base64.b64encode(excel_bytes).decode("utf-8"),
        "b64_md": base64.b64encode(md_bytes).decode("utf-8"),
        "b64_csv": base64.b64encode(csv_bytes).decode("utf-8"),
    }

    if state is None:
        _DEFAULT_DEMO_REPORTS_CACHE = reports_suite

    if _is_streamlit_running():
        try:
            st.session_state["_cached_active_reports"] = reports_suite
            st.session_state["_cached_active_reports_key"] = cache_key
            st.session_state["_cached_export_html"] = html_bytes
            st.session_state["_cached_export_html_key"] = cache_key
            st.session_state["_cached_export_excel"] = excel_bytes
            st.session_state["_cached_export_excel_key"] = cache_key
            st.session_state["_cached_export_md"] = md_bytes
            st.session_state["_cached_export_md_key"] = cache_key
            st.session_state["_cached_export_csv"] = csv_bytes
            st.session_state["_cached_export_csv_key"] = cache_key
        except Exception:
            pass

    return reports_suite


def get_powerbi_model_data() -> bytes:
    """Return bytes of data/powerbi_export/Ecommerce_Star_Schema.xlsx."""
    xlsx_path = POWERBI_DATA_DIR / "Ecommerce_Star_Schema.xlsx"
    if not xlsx_path.exists():
        try:
            from src.database.db_manager import DatabaseManager
            DatabaseManager().export_powerbi_star_schema()
        except Exception as e:
            logger.warning(f"Could not auto-generate Power BI star schema: {e}")
    return xlsx_path.read_bytes() if xlsx_path.exists() else b""


def get_powerbi_package_data() -> bytes:
    """Return bytes of data/powerbi_export/Ecommerce_PowerBI_Package.zip."""
    zip_path = POWERBI_DATA_DIR / "Ecommerce_PowerBI_Package.zip"
    if not zip_path.exists():
        try:
            from src.database.db_manager import build_powerbi_package_zip
            build_powerbi_package_zip(zip_path)
        except Exception as e:
            logger.warning(f"Could not auto-bundle Power BI zip package: {e}")
    return zip_path.read_bytes() if zip_path.exists() else b""


def get_powerbi_mockup_data() -> bytes:
    """Return bytes of powerbi/powerbi_report_mockup.html."""
    html_path = PROJECT_ROOT / "powerbi" / "powerbi_report_mockup.html"
    return html_path.read_bytes() if html_path.exists() else b""


def render_download_panel(
    reports: Optional[Dict[str, Any]] = None,
    key_prefix: str = "dl",
    show_header: bool = True,
):
    """
    Render a 4-column export suite providing both Streamlit download buttons
    AND direct base64 download links, plus the auto-saved disk file path.
    Builds exports lazily on demand when reports is None.
    """
    active_state = get_active_dataset_state()

    if show_header:
        st.markdown("### 📥 Download Generated Dashboard & Reports")
        st.caption("Export the complete findings in 4 enterprise formats. Instant on-demand generation:")

    col1, col2, col3, col4 = st.columns(4)

    # HTML Executive Report
    with col1:
        html_fn = (
            reports["html_filename"]
            if reports and "html_filename" in reports
            else get_active_export_filename("html", state=active_state)
        )
        html_data = (
            (reports["html_report"].encode("utf-8") if isinstance(reports["html_report"], str) else reports["html_report"])
            if reports and "html_report" in reports
            else (lambda s=active_state: get_active_export_data("html", state=s))
        )
        st.download_button(
            label="📄 Executive Report (HTML/PDF)",
            data=html_data,
            file_name=html_fn,
            mime="text/html",
            type="primary",
            key=f"{key_prefix}_btn_html",
            width="stretch",
        )
        cached_h = reports.get("b64_html") if reports else None
        if not cached_h:
            raw_c = get_cached_export("html", state=active_state)
            if raw_c:
                raw_bytes = raw_c if isinstance(raw_c, bytes) else raw_c.encode("utf-8")
                cached_h = base64.b64encode(raw_bytes).decode("utf-8")
        if cached_h:
            st.markdown(
                f'<div style="text-align:center; margin-top:4px;"><a href="data:text/html;charset=utf-8;base64,{cached_h}" download="{html_fn}" style="font-size:0.75rem; color:#2563eb; text-decoration:underline;">⬇️ Direct Browser Download</a></div>',
                unsafe_allow_html=True,
            )
        st.caption("🖨️ *Printable: Ctrl+P to save as PDF.*")

    # Excel Analytical Workbook
    with col2:
        excel_fn = (
            reports["excel_filename"]
            if reports and "excel_filename" in reports
            else get_active_export_filename("excel", state=active_state)
        )
        excel_data = (
            reports["excel_bytes"]
            if reports and "excel_bytes" in reports
            else (lambda s=active_state: get_active_export_data("excel", state=s))
        )
        st.download_button(
            label="📊 Multi-Tab Excel (.xlsx)",
            data=excel_data,
            file_name=excel_fn,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"{key_prefix}_btn_excel",
            width="stretch",
        )
        cached_x = reports.get("b64_excel") if reports else None
        if not cached_x:
            raw_c = get_cached_export("excel", state=active_state)
            if raw_c:
                raw_bytes = raw_c if isinstance(raw_c, bytes) else raw_c.encode("utf-8")
                cached_x = base64.b64encode(raw_bytes).decode("utf-8")
        if cached_x:
            st.markdown(
                f'<div style="text-align:center; margin-top:4px;"><a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{cached_x}" download="{excel_fn}" style="font-size:0.75rem; color:#2563eb; text-decoration:underline;">⬇️ Direct Browser Download</a></div>',
                unsafe_allow_html=True,
            )
        st.caption("📈 *Multi-sheet workbook: Summary, Trends, RFM, etc.*")

    # Markdown Briefing
    with col3:
        md_fn = (
            reports["md_filename"]
            if reports and "md_filename" in reports
            else get_active_export_filename("md", state=active_state)
        )
        md_data = (
            (reports["md_report"].encode("utf-8") if isinstance(reports["md_report"], str) else reports["md_report"])
            if reports and "md_report" in reports
            else (lambda s=active_state: get_active_export_data("md", state=s))
        )
        st.download_button(
            label="📝 Executive Briefing (.md)",
            data=md_data,
            file_name=md_fn,
            mime="text/markdown",
            key=f"{key_prefix}_btn_md",
            width="stretch",
        )
        cached_m = reports.get("b64_md") if reports else None
        if not cached_m:
            raw_c = get_cached_export("md", state=active_state)
            if raw_c:
                raw_bytes = raw_c if isinstance(raw_c, bytes) else raw_c.encode("utf-8")
                cached_m = base64.b64encode(raw_bytes).decode("utf-8")
        if cached_m:
            st.markdown(
                f'<div style="text-align:center; margin-top:4px;"><a href="data:text/markdown;charset=utf-8;base64,{cached_m}" download="{md_fn}" style="font-size:0.75rem; color:#2563eb; text-decoration:underline;">⬇️ Direct Browser Download</a></div>',
                unsafe_allow_html=True,
            )
        st.caption("📋 *Formatted KPI markdown tables.*")

    # CSV Dataset
    with col4:
        csv_fn = (
            reports["csv_filename"]
            if reports and "csv_filename" in reports
            else get_active_export_filename("csv", state=active_state)
        )
        csv_data = (
            reports["csv_bytes"]
            if reports and "csv_bytes" in reports
            else (lambda s=active_state: get_active_export_data("csv", state=s))
        )
        st.download_button(
            label="📁 Dataset (.csv)",
            data=csv_data,
            file_name=csv_fn,
            mime="text/csv",
            key=f"{key_prefix}_btn_csv",
            width="stretch",
        )
        cached_c = reports.get("b64_csv") if reports else None
        if not cached_c:
            raw_c = get_cached_export("csv", state=active_state)
            if raw_c:
                raw_bytes = raw_c if isinstance(raw_c, bytes) else raw_c.encode("utf-8")
                cached_c = base64.b64encode(raw_bytes).decode("utf-8")
        if cached_c:
            st.markdown(
                f'<div style="text-align:center; margin-top:4px;"><a href="data:text/csv;charset=utf-8;base64,{cached_c}" download="{csv_fn}" style="font-size:0.75rem; color:#2563eb; text-decoration:underline;">⬇️ Direct Browser Download</a></div>',
                unsafe_allow_html=True,
            )
        st.caption("💾 *Complete analytical table.*")

    st.markdown("---")
    st.markdown("##### 📈 Direct Power BI Star-Schema & Data Warehouse Downloads")
    pbi_c1, pbi_c2, pbi_c3 = st.columns(3)

    with pbi_c1:
        st.download_button(
            label="📊 Power BI Star Schema (.xlsx)",
            data=get_powerbi_model_data(),
            file_name="Ecommerce_Star_Schema.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"{key_prefix}_btn_pbi_xlsx",
            width="stretch",
        )
        st.caption("⚡ *Full 7-table Star Schema: Dimensions & Facts in 1 workbook.*")

    with pbi_c2:
        st.download_button(
            label="📦 Power BI Full Package (.zip)",
            data=get_powerbi_package_data(),
            file_name="Ecommerce_PowerBI_Package.zip",
            mime="application/zip",
            key=f"{key_prefix}_btn_pbi_zip",
            width="stretch",
        )
        st.caption("📦 *Includes 7 CSVs, Excel model, 16 DAX measures & PBIP project.*")

    with pbi_c3:
        st.download_button(
            label="🖥️ Interactive Report (.html)",
            data=get_powerbi_mockup_data(),
            file_name="PowerBI_Interactive_Dashboard.html",
            mime="text/html",
            key=f"{key_prefix}_btn_pbi_html",
            width="stretch",
        )
        st.caption("🌐 *Open interactive dashboard in browser without desktop app.*")

    if reports and reports.get("html_path") and "html_filename" in reports:
        st.info(f"💾 **Auto-Saved to Project Disk:** Reports are automatically saved to `exports/{reports['html_filename']}` — open directly in any browser or Excel.")


def _demo_counts_text() -> str:
    c = get_default_demo_summary()
    return (f"<strong>{c['transactions']:,}</strong> transactions • <strong>{c['customers']:,}</strong> customers • "
            f"<strong>{c['products']:,}</strong> products • <strong>{c['reviews']:,}</strong> reviews")


def render_global_active_dataset_banner(page_id: str = "banner"):
    """
    Render a clean, responsive active dataset status bar and 1-click download suite
    at the top of dashboard pages.
    """
    state = get_active_dataset_state()

    if state is not None:
        d_name = html.escape(str(state["dataset_name"]))
        rows = int(state["row_count"])
        cols = int(state["col_count"])
        ts = html.escape(str(state["timestamp"]))

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border: 1px solid #a7f3d0; border-left: 5px solid #10b981; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                    <div>
                        <strong style="color: #065f46; font-size: 0.95rem;">🟢 Active Platform Dataset: {d_name}</strong>
                        <div style="color: #047857; font-size: 0.8rem; margin-top: 3px;">
                            <span>📊 <strong>{rows:,}</strong> rows × <strong>{cols}</strong> columns</span> • 
                            <span>🕒 Loaded: {ts}</span> • 
                            <span>⚡ All pages dynamically synchronized</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #cbd5e1; border-left: 5px solid #3b82f6; border-radius: 8px; padding: 10px 16px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                    <div>
                        <strong style="color: #1e293b; font-size: 0.92rem;">🏬 Active Platform Dataset: Default E-Commerce Demo Store</strong>
                        <div style="color: #64748b; font-size: 0.78rem; margin-top: 2px;">
                            <span>📊 {_demo_counts_text()}</span> • 
                            <span>⚡ All analytical models synchronized</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("📥 1-Click Download Entire Dashboard Report & Data", expanded=False):
        st.caption("Export the complete executive intelligence findings for the currently active dataset in 4 enterprise formats:")
        render_download_panel(key_prefix=f"{page_id}_banner", show_header=False)

        if state is not None:
            c_btn1, c_btn2 = st.columns([1, 1])
            with c_btn1:
                if st.button("↺ Reset to Default Demo Store Data", key=f"{page_id}_btn_reset"):
                    reset_to_default_demo_dataset()
                    st.rerun()
            with c_btn2:
                st.caption("💡 *To upload new data or switch templates, use the sidebar or Custom Data Analyzer.*")
