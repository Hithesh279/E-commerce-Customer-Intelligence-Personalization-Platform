import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json  # noqa: E402

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="Offline ML Benchmarks • Evaluation",
    page_icon="📊",
    layout="wide",
)

from app.components.styles import apply_custom_css, render_sidebar_status  # noqa: E402
from src.utils.config import METRICS_FILE, MODELS_SENTIMENT_DIR  # noqa: E402


def render_model_benchmarks_page():
    """Render Offline ML Model Benchmarks & Comparison page."""
    st.markdown("## 📊 Offline Machine Learning Benchmarks & Evaluation")
    st.caption("Offline metrics on held-out data. Recommendation models are trained only on history before the test window.")

    st.markdown("##### 🏆 Recommendation Engine Evaluation (Time-Aware Held-Out Test Split)")
    if METRICS_FILE.exists():
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            rec_metrics = json.load(f)
        comp_data = rec_metrics.get("results_comparison", {})
        df_comp = pd.DataFrame.from_dict(comp_data, orient="index")
        st.dataframe(df_comp.style.highlight_max(axis=0, color="#dcfce7"), width="stretch")
        st.caption(
            f"Customers evaluated: {rec_metrics.get('test_users_evaluated', 'N/A')} • "
            f"Training cut-off: {rec_metrics.get('training_cutoff', 'N/A')}"
        )
        winner = rec_metrics.get("winning_model", "N/A")
        st.success(f"🏅 **Best NDCG@10: {winner}** — {rec_metrics.get('rationale', '')}")
    else:
        st.warning("Recommendation evaluation metrics file not found. Run the pipeline to create it.")

    st.markdown("---")
    st.markdown("##### 📝 Review Sentiment Classifier Performance")
    sent_metrics_file = MODELS_SENTIMENT_DIR / "sentiment_metrics.json"
    if sent_metrics_file.exists():
        with open(sent_metrics_file, "r", encoding="utf-8") as f:
            sent = json.load(f)
        ensemble = sent.get("accuracy", 0.0)
        baseline = sent.get("baseline_accuracy", 0.0)
        gap_pts = (ensemble - baseline) * 100
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Production Voting Ensemble", f"{ensemble * 100:.2f}%",
                      delta=f"{gap_pts:+.2f} pts vs Naive Bayes baseline")
        with col2:
            st.metric("Naive Bayes Baseline", f"{baseline * 100:.2f}%")
        with col3:
            st.metric("Logistic Regression", f"{sent.get('logistic_regression_accuracy', 0) * 100:.2f}%")
        with col4:
            st.metric("Held-Out Test Size", f"{sent.get('test_samples', 0):,} Reviews")
        st.caption(f"Training data: {sent.get('training_data_source', 'N/A')} "
                   f"({sent.get('train_samples', 0):,} training reviews)")

        st.markdown("###### Per-Class Classification Report:")
        cls_report = sent.get("classification_report", {})
        if cls_report:
            st.dataframe(pd.DataFrame(cls_report).transpose().style.format(precision=3), width="stretch")
    else:
        st.warning("Sentiment metrics not found.")


apply_custom_css()
render_sidebar_status()
render_model_benchmarks_page()
