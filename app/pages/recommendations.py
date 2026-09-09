import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

st.set_page_config(
    page_title="Personalized Recommendations • RecEngine",
    page_icon="🎯",
    layout="wide",
)

from app.components.cards import render_recommendation_card
from app.components.styles import apply_custom_css, render_sidebar_status
from app.services.data_loader import get_cached_analytics_bundles
from app.services.inference_service import load_recommendation_system


def render_recommendations_page():
    """Render Personalized Recommendations page."""
    st.markdown("## 🎯 Personalized Product Recommendation Engine")
    st.caption("Multi-strategy recommendation engine delivering explainable recommendations across all customer lifecycle stages.")

    bundles = get_cached_analytics_bundles()
    cust_profiles = bundles["cust_profiles"]
    recs_sys = load_recommendation_system()

    # Controls
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 1])
    with col_ctrl1:
        customer_options = cust_profiles["customer_id"].tolist()[:150]
        selected_cid = st.selectbox("Select Customer ID:", options=customer_options, index=0)
    with col_ctrl2:
        model_choice = st.selectbox(
            "Recommendation Strategy:",
            options=["Hybrid Recommender (Recommended)", "Collaborative Filtering", "Content-Based", "Popularity Baseline"],
            index=0,
        )
    with col_ctrl3:
        top_k = st.slider("Top K Items:", min_value=3, max_value=12, value=5)

    # Customer Summary Strip
    cust_row = cust_profiles[cust_profiles["customer_id"] == selected_cid].iloc[0]
    st.info(
        f"👤 **Customer Profile:** {cust_row['customer_id']} ({cust_row['customer_segment']}) • "
        f"Preferred: **{cust_row['preferred_category']}** • "
        f"Lifetime Spend: **${cust_row['net_spend']:,.2f}** ({cust_row['total_orders']} orders)"
    )

    # Generate recommendations based on strategy
    if "Hybrid" in model_choice:
        engine = recs_sys["hybrid"]
        recommendations = engine.recommend(
            customer_id=selected_cid,
            top_k=top_k,
            preferred_category=cust_row["preferred_category"],
        )
    elif "Collaborative" in model_choice:
        engine = recs_sys["collaborative"]
        recommendations = engine.recommend(customer_id=selected_cid, top_k=top_k)
        if not recommendations:
            st.warning("⚠️ Cold-start customer for collaborative filtering. Falling back to category popularity.")
            recommendations = recs_sys["popularity"].recommend(
                customer_id=selected_cid, category=cust_row["preferred_category"], top_k=top_k
            )
    elif "Content" in model_choice:
        engine = recs_sys["content"]
        user_history = recs_sys["hybrid"].user_history.get(selected_cid, [])
        recommendations = engine.recommend_for_user(user_interacted_products=user_history, top_k=top_k)
        if not recommendations:
            st.warning("⚠️ No interaction history found for content matching. Showing popular items.")
            recommendations = recs_sys["popularity"].recommend(customer_id=selected_cid, top_k=top_k)
    else:
        engine = recs_sys["popularity"]
        recommendations = engine.recommend(customer_id=selected_cid, top_k=top_k)

    # Render Results
    st.markdown(f"##### Recommended Products for `{selected_cid}` ({model_choice}):")
    for idx, product in enumerate(recommendations, 1):
        render_recommendation_card(product, rank=idx)


apply_custom_css()
render_sidebar_status()
render_recommendations_page()

