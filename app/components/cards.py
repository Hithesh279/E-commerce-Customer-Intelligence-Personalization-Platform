"""
app/components/cards.py
Reusable UI metric scorecards and recommendation display cards.
"""
from typing import Dict, Optional
import streamlit as st


def render_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: bool = True,
    card_type: str = "default",
):
    """Render a styled KPI metric scorecard."""
    type_class = ""
    if card_type == "success":
        type_class = "success"
    elif card_type == "warning":
        type_class = "warning"
    elif card_type == "danger":
        type_class = "danger"

    delta_html = ""
    if delta:
        delta_class = "positive" if delta_positive else "negative"
        delta_icon = "▲" if delta_positive else "▼"
        delta_html = f'<div class="metric-delta {delta_class}">{delta_icon} {delta}</div>'

    html = f"""
    <div class="metric-card {type_class}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_recommendation_card(product: Dict[str, any], rank: int = 1):
    """Render an individual recommended product card with transparent rationale."""
    p_name = product.get("product_name", "Unknown Product")
    cat = product.get("category", "General")
    price = product.get("price", 0.0)
    score = product.get("score", 0.0)
    reason = product.get("reason", "Recommended for you")
    pid = product.get("product_id", "")

    html = f"""
    <div class="rec-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <span class="rec-score-badge">#{rank} Ranked</span>
                <span class="rec-score-badge" style="background:#e0f2fe; color:#0369a1;">Score: {score:.3f}</span>
                <span style="font-size:0.8rem; color:#64748b;">({pid})</span>
                <div class="rec-title" style="margin-top:6px;">{p_name}</div>
                <div class="rec-meta">Category: <strong>{cat}</strong> | Price: <strong>${price:.2f}</strong></div>
            </div>
        </div>
        <div class="rec-reason">
            💡 <strong>Why this was recommended:</strong> {reason}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
