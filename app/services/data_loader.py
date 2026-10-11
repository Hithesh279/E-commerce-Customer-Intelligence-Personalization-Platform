"""
app/services/data_loader.py
Cached data access layer for Streamlit dashboard.
"""
from typing import Dict, Tuple
import pandas as pd
import streamlit as st

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
from src.utils.config import PROCESSED_DATA_DIR


@st.cache_data(show_spinner=False)
def load_all_processed_data() -> Dict[str, pd.DataFrame]:
    """Load core processed tables with caching."""
    tables = ["customers", "products", "transactions", "reviews", "interactions"]
    data = {}
    for t in tables:
        path = PROCESSED_DATA_DIR / f"{t}.csv"
        data[t] = pd.read_csv(path)
    return data


@st.cache_data(show_spinner=False)
def _load_default_aspects_data() -> pd.DataFrame:
    """Load default extracted aspect-sentiment observations from disk."""
    path = PROCESSED_DATA_DIR / "review_aspects.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_aspects_data() -> pd.DataFrame:
    """
    Load extracted aspect-sentiment observations.
    Dynamically returns the active custom dataset's aspects if loaded,
    otherwise falls back to default processed review aspects.
    """
    from app.services.active_dataset_manager import get_active_aspects_df
    return get_active_aspects_df()


@st.cache_data(show_spinner=False)
def _get_default_cached_analytics_bundles():
    """Compute and cache default business KPIs, customer profiles, and product performance tables."""
    raw = load_all_processed_data()
    cust_df = raw["customers"]
    prod_df = raw["products"]
    txns_df = raw["transactions"]
    rev_df = raw["reviews"]

    exec_kpis = calculate_executive_kpis(cust_df, txns_df, rev_df)
    monthly_trend = calculate_monthly_revenue_trend(txns_df)
    cat_perf = calculate_category_performance(prod_df, txns_df, rev_df)
    cust_profiles = generate_customer_profile_metrics(cust_df, txns_df, rev_df)
    seg_summary = get_segment_summary(cust_profiles)
    prod_perf = generate_product_performance_metrics(prod_df, txns_df, rev_df)

    return {
        "exec_kpis": exec_kpis,
        "monthly_trend": monthly_trend,
        "cat_perf": cat_perf,
        "cust_profiles": cust_profiles,
        "seg_summary": seg_summary,
        "prod_perf": prod_perf,
    }


def get_cached_analytics_bundles():
    """
    Compute and provide all business KPIs, customer profiles, and product performance tables.
    Seamlessly synchronizes with the active dataset (custom uploaded data or selected template)
    across all dashboard pages (Main, Overview, Customer Intelligence, Product Intelligence, etc.).
    """
    from app.services.active_dataset_manager import get_active_bundles
    return get_active_bundles()

