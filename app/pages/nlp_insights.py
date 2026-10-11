import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="NLP Customer Voice • Aspect Sentiment",
    page_icon="🧠",
    layout="wide",
)

from app.components.charts import plot_aspect_radar
from app.components.styles import apply_custom_css, render_sidebar_status
from app.services.data_loader import load_aspects_data
from src.utils.config import MODELS_TOPIC_DIR


def render_nlp_insights_page():
    """Render NLP Review Intelligence & ABSA page."""
    st.markdown("## 🧠 NLP Customer Voice & Aspect-Based Sentiment")
    st.caption("Fine-grained review intelligence, 11-aspect sentiment polarity, and recurring complaint discovery.")

    from app.services.active_dataset_manager import get_active_dataset_state, render_global_active_dataset_banner
    render_global_active_dataset_banner(page_id="nlp_insights")

    aspects_df = load_aspects_data()

    if aspects_df.empty:
        st.warning("Aspect sentiment data not found. Please run the data pipeline.")
        return

    # Aggregate aspect scores
    aspect_summary = aspects_df.groupby("aspect").agg(
        total_mentions=("review_id", "count"),
        avg_sentiment_score=("sentiment_score", "mean"),
        positive_pct=("sentiment", lambda s: round((s == "Positive").mean() * 100, 1)),
        negative_pct=("sentiment", lambda s: round((s == "Negative").mean() * 100, 1)),
    ).reset_index()

    aspect_summary["avg_sentiment_score"] = aspect_summary["avg_sentiment_score"].round(3)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(plot_aspect_radar(aspect_summary), width="stretch", key="nlp_insights_radar")
    with col2:
        st.markdown("##### 📋 Aspect Sentiment Polarity Summary")
        st.dataframe(
            aspect_summary.rename(
                columns={
                    "aspect": "Product Aspect",
                    "total_mentions": "Mentions",
                    "avg_sentiment_score": "Sentiment Score (-1 to +1)",
                    "positive_pct": "Positive %",
                    "negative_pct": "Negative %",
                }
            ).sort_values("Sentiment Score (-1 to +1)", ascending=False),
            width="stretch",
            hide_index=True,
        )

    st.markdown("---")

    # Feedback Themes & Recurring Complaint Section
    state = get_active_dataset_state()
    revs = state.get("reviews_data") if state else None

    if state is not None and revs:
        st.markdown(f"##### 📌 Voice of Customer Feedback Themes & Quotes ({state['dataset_name']})")
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown("**🟢 Positive Customer Highlights & Praises:**")
            pos_quotes = revs.get("positive_quotes", [])
            if pos_quotes:
                for q in pos_quotes[:3]:
                    st.markdown(
                        f"""
                        <div style="background:#f0fdf4; border-left:4px solid #16a34a; border-radius:4px; padding:8px 12px; margin-bottom:8px; font-size:0.83rem; color:#14532d;">
                            "{q}"
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No positive quotes available.")
        with col_q2:
            st.markdown("**🚨 Critical Friction & Recurring Complaints:**")
            neg_quotes = revs.get("negative_quotes", [])
            if neg_quotes:
                for q in neg_quotes[:3]:
                    st.markdown(
                        f"""
                        <div style="background:#fef2f2; border-left:4px solid #ef4444; border-radius:4px; padding:8px 12px; margin-bottom:8px; font-size:0.83rem; color:#7f1d1d;">
                            "{q}"
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No negative friction complaints detected.")
    else:
        # Topic Modeling Section for Default Demo Store
        st.markdown("##### 📌 Topic & Recurring Complaint Discovery (NMF)")
        topic_summary_file = MODELS_TOPIC_DIR / "topic_summaries.json"

        if topic_summary_file.exists():
            with open(topic_summary_file, "r", encoding="utf-8") as f:
                topics = json.load(f)

            topic_cols = st.columns(len(topics))
            for idx, t in enumerate(topics):
                with topic_cols[idx]:
                    st.markdown(
                        f"""
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #3b82f6; border-radius:6px; padding:14px; min-height:180px;">
                            <strong style="font-size:0.9rem; color:#1e293b;">{t['topic_name']}</strong><br>
                            <span style="font-size:0.75rem; color:#64748b;">Volume: {t['review_count']:,} ({t['percentage_of_reviews']}%)</span><br>
                            <span style="font-size:0.8rem; font-weight:600; color:{'#ef4444' if t['avg_rating'] < 3.5 else '#10b981'};">Avg Rating: {t['avg_rating']}★</span>
                            <hr style="margin:8px 0;">
                            <span style="font-size:0.75rem; color:#334155;"><strong>Keywords:</strong> {', '.join(t['top_words'][:4])}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


apply_custom_css()
render_sidebar_status()
render_nlp_insights_page()

