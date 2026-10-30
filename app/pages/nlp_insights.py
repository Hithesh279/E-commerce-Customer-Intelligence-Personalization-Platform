import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import html  # noqa: E402
import json  # noqa: E402

import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="NLP Customer Voice • Aspect Sentiment",
    page_icon="🧠",
    layout="wide",
)

from app.components.cards import render_quote  # noqa: E402
from app.components.charts import plot_aspect_radar  # noqa: E402
from app.components.styles import apply_custom_css, render_sidebar_status  # noqa: E402
from app.services.data_loader import load_aspects_data  # noqa: E402
from src.utils.config import MODELS_TOPIC_DIR  # noqa: E402
from src.utils.formatting import fmt_num, is_missing  # noqa: E402


def render_nlp_insights_page():
    """Render NLP Review Intelligence & ABSA page."""
    st.markdown("## 🧠 NLP Customer Voice & Aspect-Based Sentiment")
    st.caption("Fine-grained review intelligence, 11-aspect sentiment polarity, and recurring complaint discovery.")

    from app.services.active_dataset_manager import get_active_dataset_state, render_global_active_dataset_banner
    render_global_active_dataset_banner(page_id="nlp_insights")

    aspects_df = load_aspects_data()
    if aspects_df.empty:
        st.warning("No aspect sentiment data is available. Upload review text, or run the data pipeline for the demo store.")
        return

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
            aspect_summary.rename(columns={
                "aspect": "Product Aspect",
                "total_mentions": "Mentions",
                "avg_sentiment_score": "Sentiment Score (-1 to +1)",
                "positive_pct": "Positive %",
                "negative_pct": "Negative %",
            }).sort_values("Sentiment Score (-1 to +1)", ascending=False),
            width="stretch",
            hide_index=True,
        )

    st.markdown("---")
    state = get_active_dataset_state()
    revs = state.get("reviews_data") if state else None

    if state is not None and revs:
        st.markdown(f"##### 📌 Voice of Customer Feedback Themes & Quotes ({html.escape(str(state['dataset_name']))})")
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown("**🟢 Positive Customer Highlights & Praises:**")
            pos_quotes = revs.get("positive_quotes", [])
            if pos_quotes:
                for q in pos_quotes[:3]:
                    render_quote(q, tone="positive")
            else:
                st.info("No positive quotes available.")
        with col_q2:
            st.markdown("**🚨 Critical Friction & Recurring Complaints:**")
            neg_quotes = revs.get("negative_quotes", [])
            if neg_quotes:
                for q in neg_quotes[:3]:
                    render_quote(q, tone="negative")
            else:
                st.info("No negative friction complaints detected.")
    else:
        st.markdown("##### 📌 Topic & Recurring Complaint Discovery (NMF)")
        st.caption("Topics are labelled by their most characteristic words. Product attribution is shown only when "
                   "the source data contains product IDs.")
        topic_summary_file = MODELS_TOPIC_DIR / "topic_summaries.json"
        if topic_summary_file.exists():
            with open(topic_summary_file, "r", encoding="utf-8") as f:
                topics = json.load(f)
            topic_cols = st.columns(len(topics))
            for idx, t in enumerate(topics):
                rating = t.get("avg_rating")
                rating_color = "#64748b" if is_missing(rating) else ("#ef4444" if rating < 3.5 else "#10b981")
                rating_text = "N/A" if is_missing(rating) else f"{rating}★"
                with topic_cols[idx]:
                    st.markdown(
                        f"""
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #3b82f6; border-radius:6px; padding:14px; min-height:180px;">
                            <strong style="font-size:0.9rem; color:#1e293b;">{html.escape(t['topic_name'])}</strong><br>
                            <span style="font-size:0.75rem; color:#64748b;">Volume: {fmt_num(t['review_count'])} ({t['percentage_of_reviews']}%)</span><br>
                            <span style="font-size:0.8rem; font-weight:600; color:{rating_color};">Avg Rating: {rating_text}</span>
                            <hr style="margin:8px 0;">
                            <span style="font-size:0.75rem; color:#334155;"><strong>Keywords:</strong> {html.escape(', '.join(t['top_words'][:6]))}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Topic summaries have not been generated yet. Run the data pipeline to create them.")


apply_custom_css()
render_sidebar_status()
render_nlp_insights_page()
