import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

st.set_page_config(
    page_title="Product Intelligence • SKU Analytics",
    page_icon="📦",
    layout="wide",
)

import plotly.express as px

from app.components.cards import render_metric_card
from app.components.styles import apply_custom_css, render_sidebar_status
from app.services.data_loader import get_cached_analytics_bundles
from app.services.inference_service import load_recommendation_system


def render_product_intelligence_page():
    """Render Product Intelligence page."""
    st.markdown("## 📦 Product Intelligence & Anomaly Discovery")
    st.caption("Commercial SKU performance, sentiment-sales discrepancy detection, and similar product retrieval.")

    from app.services.active_dataset_manager import render_global_active_dataset_banner
    render_global_active_dataset_banner(page_id="prod_intel")

    bundles = get_cached_analytics_bundles()
    prod_perf = bundles["prod_perf"]

    # Filter by category
    cats = ["All Categories"] + sorted(prod_perf["category"].unique().tolist())
    selected_cat = st.selectbox("Filter Catalog by Category:", options=cats, index=0)

    filtered_df = prod_perf if selected_cat == "All Categories" else prod_perf[prod_perf["category"] == selected_cat]

    # Discrepancy highlights
    st.markdown("##### ⚠️ Commercial Discrepancy Discovery")
    risk_products = filtered_df[filtered_df["is_high_sales_low_sentiment"]]
    gem_products = filtered_df[filtered_df["is_low_sales_high_sentiment"]]

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.error(f"🚨 **High Sales + Poor Sentiment ({len(risk_products)} SKUs):** Top sales volume but lowest customer satisfaction. At high risk of churn and elevated return rates.")
        if not risk_products.empty:
            st.dataframe(
                risk_products[["product_id", "product_name", "units_sold", "average_rating", "return_rate"]].head(3),
                width="stretch",
                hide_index=True,
            )
    with d_col2:
        st.success(f"💎 **Low Sales + Stellar Sentiment ({len(gem_products)} SKUs):** Hidden gems with high customer ratings (>4.5★) and negligible returns (<3%) that are prime candidates for marketing promotion.")
        if not gem_products.empty:
            st.dataframe(
                gem_products[["product_id", "product_name", "units_sold", "average_rating", "return_rate"]].head(3),
                width="stretch",
                hide_index=True,
            )

    st.markdown("---")

    # Risk vs Satisfaction Scatter Plot
    st.markdown("##### 📊 Product Matrix: Sales Volume vs Customer Rating")
    fig = px.scatter(
        filtered_df,
        x="units_sold",
        y="average_rating",
        size="net_revenue",
        color="category",
        hover_data=["product_id", "product_name", "return_rate"],
        labels={"units_sold": "Units Sold", "average_rating": "Average Rating (1-5★)"},
        template="plotly_white",
        height=380,
    )
    # Add horizontal threshold lines
    fig.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Dissatisfaction Threshold (3.0★)")
    st.plotly_chart(fig, width="stretch", key="prod_intel_scatter")

    st.markdown("---")

    # Product Drill-Down & Similar Items
    st.markdown("##### 🔍 SKU Deep-Dive & Similar Products (Content-Based Similarity)")
    selected_pid = st.selectbox(
        "Select Product to Inspect:",
        options=filtered_df["product_id"].tolist()[:100],
        index=0,
    )
    prod_row = prod_perf[prod_perf["product_id"] == selected_pid].iloc[0]

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        render_metric_card("Product Name", str(prod_row["product_name"]), str(prod_row["category"]))
    with p2:
        render_metric_card("Price", f"${prod_row['price']:.2f}", f"Units Sold: {prod_row['units_sold']:,}")
    with p3:
        render_metric_card("Rating", f"{prod_row['average_rating']:.2f}★", f"{prod_row['review_count']} Reviews")
    with p4:
        render_metric_card(
            "Return Rate",
            f"{prod_row['return_rate']:.1f}%",
            delta_positive=prod_row['return_rate'] < 10,
            card_type="danger" if prod_row['return_rate'] > 15 else "success",
        )

    p_desc = prod_row.get("product_description", f"High performance catalog product in category {prod_row.get('category', 'General')}.")
    st.markdown(f"**Description:** {p_desc}")

    # Similar products via Content recommender or catalog category matching
    recs_sys = load_recommendation_system()
    content_engine = recs_sys["content"]
    similar_items = []
    if selected_pid in getattr(content_engine, "product_index", getattr(content_engine, "prod_to_idx", {})):
        similar_items = content_engine.recommend_similar_products(selected_pid, top_k=4)

    if not similar_items:
        # Fallback to similar category items from active catalog
        same_cat = filtered_df[filtered_df["product_id"] != selected_pid]
        matched = same_cat[same_cat["category"] == prod_row["category"]].head(4)
        if matched.empty:
            matched = same_cat.head(4)
        if not matched.empty:
            similar_items = [
                {
                    "product_name": r["product_name"],
                    "category": r["category"],
                    "price": r["price"],
                    "score": round(float(r["average_rating"] / 5.0), 3),
                }
                for _, r in matched.iterrows()
            ]

    if similar_items:
        st.markdown("###### Top Similar Catalog Products:")
        cols = st.columns(len(similar_items))
        for idx, itm in enumerate(similar_items):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px; height:140px;">
                        <strong style="font-size:0.85rem;">{itm['product_name']}</strong><br>
                        <span style="font-size:0.75rem; color:#64748b;">{itm['category']} • ${itm['price']:.2f}</span><br>
                        <span style="font-size:0.75rem; color:#2563eb; font-weight:600;">Match Index: {itm['score']:.3f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


apply_custom_css()
render_sidebar_status()
render_product_intelligence_page()

