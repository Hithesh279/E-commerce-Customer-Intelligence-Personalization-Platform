"""
app/components/cards.py
Reusable KPI scorecards, recommendation cards and quote blocks.
Any text that may come from an uploaded file is HTML-escaped before it is rendered.
"""
import html
from typing import Any, Dict, Optional

import streamlit as st

from src.utils.formatting import is_missing


def _esc(value: Any) -> str:
    return "" if is_missing(value) else html.escape(str(value))


def render_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: bool = True,
    card_type: str = "default",
):
    """Render a styled KPI metric scorecard."""
    type_class = card_type if card_type in ("success", "warning", "danger") else ""
    delta_html = ""
    if delta:
        delta_class = "positive" if delta_positive else "negative"
        delta_icon = "▲" if delta_positive else "▼"
        delta_html = f'<div class="metric-delta {delta_class}">{delta_icon} {_esc(delta)}</div>'
    st.markdown(
        f'<div class="metric-card {type_class}">'
        f'<div class="metric-title">{_esc(title)}</div>'
        f'<div class="metric-value">{_esc(value)}</div>'
        f"{delta_html}</div>",
        unsafe_allow_html=True,
    )


def render_quote(text: Any, tone: str = "positive"):
    """Render a customer quote. The text is escaped, so review content cannot inject markup."""
    palette = {
        "positive": ("#f0fdf4", "#16a34a", "#14532d"),
        "negative": ("#fef2f2", "#ef4444", "#7f1d1d"),
    }
    background, border, color = palette.get(tone, palette["positive"])
    st.markdown(
        f'<div style="background:{background}; border-left:4px solid {border}; border-radius:4px; '
        f'padding:8px 12px; margin-bottom:8px; font-size:0.83rem; color:{color};">'
        f"&ldquo;{_esc(text)}&rdquo;</div>",
        unsafe_allow_html=True,
    )


def render_recommendation_card(product: Dict[str, Any], rank: int = 1):
    """Render an individual recommended product card with its rationale."""
    score = product.get("score")
    price = product.get("price")
    score_text = "N/A" if is_missing(score) else f"{float(score):.3f}"
    price_text = "N/A" if is_missing(price) else f"${float(price):.2f}"
    st.markdown(
        f'<div class="rec-card">'
        f'<div><span class="rec-score-badge">#{rank} Ranked</span> '
        f'<span class="rec-score-badge" style="background:#e0f2fe; color:#0369a1;">Score: {score_text}</span> '
        f'<span style="font-size:0.8rem; color:#64748b;">({_esc(product.get("product_id", ""))})</span>'
        f'<div class="rec-title" style="margin-top:6px;">{_esc(product.get("product_name", "Unknown Product"))}</div>'
        f'<div class="rec-meta">Category: <strong>{_esc(product.get("category", "General"))}</strong> | '
        f"Price: <strong>{price_text}</strong></div></div>"
        f'<div class="rec-reason">💡 <strong>Why this was recommended:</strong> '
        f'{_esc(product.get("reason", "Recommended for you"))}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
