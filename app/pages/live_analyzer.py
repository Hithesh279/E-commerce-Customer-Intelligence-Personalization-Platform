import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

st.set_page_config(
    page_title="Live Review NLP Analyzer • Customer Intelligence",
    page_icon="✍️",
    layout="wide",
)

from app.components.styles import apply_custom_css, render_sidebar_status
from app.services.inference_service import analyze_review_text


def render_live_analyzer_page():
    """Render Live Review Analyzer page."""
    st.markdown("## ✍️ Live Review NLP Analyzer")
    st.caption("Test the trained sentiment classification and aspect extraction pipeline on any custom text.")

    # Preset Sample Buttons
    st.markdown("##### Quick Presets:")
    p_col1, p_col2, p_col3 = st.columns(3)
    sample_text = "The battery lasts all day and performance is blazing fast, but the camera quality is disappointing."

    if p_col1.button("🔋 Battery (+) & Camera (-)"):
        st.session_state["review_input"] = "The battery lasts all day and performance is blazing fast, but the camera quality is disappointing."
    if p_col2.button("📦 Delivery (+) & Price (-)"):
        st.session_state["review_input"] = "Super fast delivery and elegant packaging, however the price is way too expensive for what you get."
    if p_col3.button("💔 Durability (-) & Display (-)"):
        st.session_state["review_input"] = "Terrible build quality and dim screen display. Lacks durability and broke after three days."

    review_text = st.text_area(
        "Enter customer review text to analyze:",
        value=st.session_state.get("review_input", sample_text),
        height=100,
    )

    if st.button("🚀 Analyze Customer Review", type="primary"):
        if not review_text.strip():
            st.warning("Please enter some text to analyze.")
            return

        with st.spinner("Analyzing review semantics and aspects..."):
            res = analyze_review_text(review_text)

        # Sentiment Result Card
        sentiment = res["sentiment"]
        confidence = res["confidence"] * 100.0

        if sentiment == "Positive":
            color = "#10b981"
            badge = "🟢 POSITIVE SENTIMENT"
        elif sentiment == "Negative":
            color = "#ef4444"
            badge = "🔴 NEGATIVE SENTIMENT"
        else:
            color = "#f59e0b"
            badge = "🟡 NEUTRAL SENTIMENT"

        st.markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:5px solid {color}; border-radius:8px; padding:18px; margin:16px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.1rem; font-weight:700; color:{color};">{badge}</span>
                    <span style="font-size:0.95rem; font-weight:600; color:#475569;">Confidence: {confidence:.1f}%</span>
                </div>
                <div style="margin-top:12px; font-size:0.85rem; color:#64748b;">
                    Class Probabilities — 
                    Negative: <strong>{res['probabilities']['Negative']*100:.1f}%</strong> | 
                    Neutral: <strong>{res['probabilities']['Neutral']*100:.1f}%</strong> | 
                    Positive: <strong>{res['probabilities']['Positive']*100:.1f}%</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Extracted Aspects
        st.markdown("##### 🔍 Detected Product Aspects & Sentiment Breakdown:")
        aspects = res["aspects"]
        if aspects:
            cols = st.columns(len(aspects))
            for i, asp in enumerate(aspects):
                asp_color = "#10b981" if asp["sentiment"] == "Positive" else ("#ef4444" if asp["sentiment"] == "Negative" else "#f59e0b")
                with cols[i]:
                    st.markdown(
                        f"""
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:3px solid {asp_color}; border-radius:6px; padding:12px; height:120px;">
                            <strong style="text-transform:capitalize; font-size:0.95rem;">{asp['aspect']}</strong><br>
                            <span style="font-size:0.85rem; font-weight:600; color:{asp_color};">{asp['sentiment']}</span><br>
                            <span style="font-size:0.75rem; color:#64748b;">Score: {asp['sentiment_score']:+.2f}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No specific domain product aspects explicitly detected in this text sample.")


apply_custom_css()
render_sidebar_status()
render_live_analyzer_page()

