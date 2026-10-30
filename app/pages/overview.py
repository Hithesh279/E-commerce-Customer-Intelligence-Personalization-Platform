import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="Executive Overview • Customer Intelligence",
    page_icon="📈",
    layout="wide",
)

from app.components.dashboards import render_executive_dashboard  # noqa: E402
from app.components.styles import apply_custom_css, render_sidebar_status  # noqa: E402
from app.services.active_dataset_manager import render_global_active_dataset_banner  # noqa: E402
from app.services.data_loader import get_cached_analytics_bundles  # noqa: E402


def render_overview_page():
    """Executive Overview page: the same dashboard as the Main page."""
    render_global_active_dataset_banner(page_id="overview")
    render_executive_dashboard(get_cached_analytics_bundles(), key_prefix="overview")


apply_custom_css()
render_sidebar_status()
render_overview_page()
