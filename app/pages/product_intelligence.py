import html
import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="Product Intelligence • SKU Analytics",
    page_icon="📦",
    layout="wide",
)

from app.components.cards import render_metric_card  # noqa: E402
from app.components.styles import apply_custom_css, render_sidebar_status  # noqa: E402
from app.services.active_dataset_manager import get_active_dataset_state, render_global_active_dataset_banner  # noqa: E402
from app.services.data_loader import get_cached_analytics_bundles  # noqa: E402
from src.utils.formatting import fmt_money, fmt_num, fmt_pct, fmt_rating, is_missing  # noqa: E402


def _table_for_display(df):
    return df.astype(object).where(df.notna(), "N/A")


def render_product_intelligence_page():
    """Render Product Intelligence page."""
    st.markdown("## 📦 Product Intelligence & Anomaly Discovery")
    st.caption("SKU performance, sentiment-sales discrepancy checks and similar product lookup.")
    render_global_active_dataset_banner(page_id="prod_intel")

    bundles = get_cached_analytics_bundles()
    prod_perf = bundles["prod_perf"].copy()
    if prod_perf.empty:
        st.info(
            "This dataset has no product-level records. Map a **Product / SKU** column together with "
            "revenue in the Custom Data Analyzer to enable product analytics."
        )
        return

    prod_perf["category"] = prod_perf["category"].fillna("Unspecified").astype(str)
    cats = ["All Categories"] + sorted(prod_perf["category"].unique().tolist())
    selected_cat = st.selectbox("Filter Catalog by Category:", options=cats, index=0)
    filtered_df = prod_perf if selected_cat == "All Categories" else prod_perf[prod_perf["category"] == selected_cat]

    st.markdown("##### ⚠️ Commercial Discrepancy Discovery")
    has_sentiment = filtered_df["average_rating"].notna().any()
    risk_products = filtered_df[filtered_df["is_high_sales_low_sentiment"] == True]  # noqa: E712
    gem_products = filtered_df[filtered_df["is_low_sales_high_sentiment"] == True]  # noqa: E712
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if has_sentiment:
            st.error(f"🚨 **High Sales + Poor Sentiment ({len(risk_products)} SKUs):** top sales volume with the lowest "
                     "customer ratings. These SKUs carry churn and return risk.")
            if not risk_products.empty:
                st.dataframe(_table_for_display(risk_products[["product_id", "product_name", "units_sold", "average_rating", "return_rate"]].head(3)),
                             width="stretch", hide_index=True)
        else:
            st.info("Discrepancy checks need product ratings, which this dataset does not contain.")
    with d_col2:
        if has_sentiment:
            st.success(f"💎 **Low Sales + Stellar Sentiment ({len(gem_products)} SKUs):** high customer ratings "
                       "with few units sold. Candidates for promotion.")
            if not gem_products.empty:
                st.dataframe(_table_for_display(gem_products[["product_id", "product_name", "units_sold", "average_rating", "return_rate"]].head(3)),
                             width="stretch", hide_index=True)

    st.markdown("---")
    st.markdown("##### 📊 Product Matrix: Sales Volume vs Customer Rating")
    plot_df = filtered_df.dropna(subset=["units_sold", "average_rating"])
    if plot_df.empty:
        st.info("The sales-versus-rating matrix needs both units sold and ratings.")
    else:
        fig = px.scatter(
            plot_df,
            x="units_sold",
            y="average_rating",
            size="net_revenue" if plot_df["net_revenue"].notna().all() else None,
            color="category",
            hover_data=["product_id", "product_name", "return_rate"],
            labels={"units_sold": "Units Sold", "average_rating": "Average Rating (1-5★)"},
            template="plotly_white",
            height=380,
        )
        fig.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Dissatisfaction Threshold (3.0★)")
        st.plotly_chart(fig, width="stretch", key="prod_intel_scatter")

    st.markdown("---")
    st.markdown("##### 🔍 SKU Deep-Dive & Similar Products")
    selected_pid = st.selectbox("Select Product to Inspect:", options=filtered_df["product_id"].tolist()[:100], index=0)
    prod_row = prod_perf[prod_perf["product_id"] == selected_pid].iloc[0]

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        render_metric_card("Product Name", str(prod_row["product_name"]), str(prod_row["category"]))
    with p2:
        render_metric_card("Revenue", fmt_money(prod_row["net_revenue"]), f"Units Sold: {fmt_num(prod_row['units_sold'])}")
    with p3:
        render_metric_card("Rating", fmt_rating(prod_row["average_rating"]), f"{fmt_num(prod_row['review_count'])} Reviews")
    with p4:
        rate = prod_row["return_rate"]
        render_metric_card("Return Rate", fmt_pct(rate),
                           delta_positive=(is_missing(rate) or rate < 10),
                           card_type="danger" if (not is_missing(rate) and rate > 15) else "success")

    description = prod_row.get("product_description")
    if not is_missing(description):
        st.markdown(f"**Description:** {description}")

    # Similar products: the content model only knows the demo catalog, so it is used only when the
    # demo dataset is active. Otherwise, products in the same category are listed without any score.
    similar = []
    if get_active_dataset_state() is None:
        try:
            from app.services.inference_service import load_recommendation_system
            content_engine = load_recommendation_system()["content"]
            if selected_pid in content_engine.prod_to_idx:
                similar = [
                    {**item, "score_label": f"Similarity {item['score']:.3f}"}
                    for item in content_engine.recommend_similar_products(selected_pid, top_k=4)
                ]
        except Exception:
            similar = []

    if not similar:
        same_cat = prod_perf[(prod_perf["product_id"] != selected_pid) & (prod_perf["category"] == prod_row["category"])]
        similar = [
            {"product_name": r["product_name"], "category": r["category"],
             "price": r["price"], "score_label": "Same category"}
            for _, r in same_cat.head(4).iterrows()
        ]

    if similar:
        st.markdown("###### Similar Catalog Products:")
        cols = st.columns(len(similar))
        for idx, item in enumerate(similar):
            with cols[idx]:
                price = item.get("price")
                p_name = html.escape(str(item.get("product_name", "")))
                p_cat = html.escape(str(item.get("category", "")))
                s_lbl = html.escape(str(item.get("score_label", "")))
                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px; min-height:120px;">
                        <strong style="font-size:0.85rem;">{p_name}</strong><br>
                        <span style="font-size:0.75rem; color:#64748b;">{p_cat} • {fmt_money(price)}</span><br>
                        <span style="font-size:0.75rem; color:#2563eb; font-weight:600;">{s_lbl}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


apply_custom_css()
render_sidebar_status()
render_product_intelligence_page()
