"""
app/main.py
Entry point for the Streamlit E-commerce Customer Intelligence Platform.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="E-commerce Customer Intelligence & Personalization Platform",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.components.dashboards import render_executive_dashboard  # noqa: E402
from app.components.styles import apply_custom_css, render_sidebar_status  # noqa: E402
from app.services.active_dataset_manager import render_global_active_dataset_banner  # noqa: E402
from app.services.data_loader import get_cached_analytics_bundles  # noqa: E402
from src.analytics.templates import get_available_templates  # noqa: E402


def main():
    """Main application landing portal and executive dashboard."""
    apply_custom_css()
    render_sidebar_status()

    n_templates = len(get_available_templates())
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 28px; border-radius: 10px; margin-bottom: 24px; border: 1px solid #334155;">
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #f8fafc;">🛍️ E-Commerce Customer Intelligence & Personalization Platform</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.0rem; color: #cbd5e1; line-height: 1.6;">
                Analytics and machine learning for e-commerce data: <strong>aspect-based review sentiment</strong>,
                <strong>NMF topic discovery</strong>, <strong>multi-strategy recommendations</strong>
                (hybrid, SVD collaborative, content-based, popularity), and <strong>star-schema BI exports</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### 🚀 Platform Modules")
    cols = st.columns(4)
    cards = [
        ("📈 Executive Overview", "#3b82f6", "Commercial KPIs, revenue trend, category performance and segment share."),
        ("👥 Customer Intelligence", "#10b981", "RFM behavioral segmentation and a customer 360 drill-down."),
        ("📦 Product Intelligence", "#f59e0b", "SKU performance, sentiment-sales discrepancy checks and similar products."),
        ("🧠 NLP Review Voice", "#8b5cf6", "Aspect sentiment radar and topic discovery from review text."),
        ("🎯 Recommendations", "#ec4899", "Hybrid, collaborative, content-based and popularity strategies with explanations."),
        ("📁 Upload & Auto-Dashboard", "#06b6d4", f"Upload CSV, Excel, or ZIP data, or load one of {n_templates} business templates."),
        ("✍️ Live Review NLP Analyzer", "#14b8a6", "Interactive real-time sentiment classification and 11-aspect polarity extraction."),
        ("📊 Offline ML Benchmarks", "#6366f1", "Time-aware held-out recommender evaluation and NLP classifier benchmarks."),
    ]
    for idx, (title, color, text) in enumerate(cards):
        with cols[idx % 4]:
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid {color}; border-radius:8px; padding:14px; margin-bottom:12px; min-height:110px;">
                    <strong style="font-size:0.95rem; color:#1e293b;">{title}</strong>
                    <p style="font-size:0.8rem; color:#64748b; margin:6px 0 0 0;">{text}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    render_global_active_dataset_banner(page_id="main")
    render_executive_dashboard(get_cached_analytics_bundles(), key_prefix="main")


if __name__ == "__main__":
    main()
