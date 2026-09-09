import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

st.set_page_config(
    page_title="Customer Intelligence • RFM Segmentation",
    page_icon="👥",
    layout="wide",
)

import plotly.express as px

from app.components.cards import render_metric_card
from app.components.styles import apply_custom_css, render_sidebar_status
from app.services.data_loader import get_cached_analytics_bundles


def render_customer_intelligence_page():
    """Render Customer Intelligence & RFM page."""
    st.markdown("## 👥 Customer Intelligence & Behavioral Segmentation")
    st.caption("Recency, Frequency, and Monetary (RFM) analytics and 360-degree customer profiling.")

    bundles = get_cached_analytics_bundles()
    cust_profiles = bundles["cust_profiles"]
    seg_summary = bundles["seg_summary"]

    # Segment KPI Summary
    st.markdown("##### 📊 Segment Financial & Retention Matrix")
    st.dataframe(
        seg_summary.rename(
            columns={
                "customer_segment": "Customer Segment",
                "customer_count": "Customers",
                "total_revenue": "Total Spend ($)",
                "avg_revenue_per_customer": "Spend/Customer ($)",
                "avg_orders": "Avg Orders",
                "avg_aov": "AOV ($)",
                "avg_return_rate": "Return Rate %",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # RFM Scatter Visualization
    st.markdown("##### 🎯 Customer Value Mapping (Monetary Spend vs Order Frequency)")
    fig = px.scatter(
        cust_profiles.sample(min(len(cust_profiles), 800), random_state=42),
        x="total_orders",
        y="net_spend",
        color="rfm_segment",
        size="average_order_value",
        hover_data=["customer_id", "customer_segment", "city", "return_rate"],
        labels={"total_orders": "Total Orders Placed", "net_spend": "Net Lifetime Spend ($)"},
        template="plotly_white",
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Customer 360 Drill-Down Search
    st.markdown("##### 🔍 Customer 360 Profile Drill-Down")
    selected_cid = st.selectbox(
        "Select or search Customer ID:",
        options=cust_profiles["customer_id"].tolist()[:100],
        index=0,
    )

    cust_row = cust_profiles[cust_profiles["customer_id"] == selected_cid].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Customer", str(cust_row["customer_id"]), f"{cust_row['membership_type']} Member")
    with c2:
        render_metric_card("Segment", str(cust_row["customer_segment"]), f"RFM: {cust_row['rfm_score']}")
    with c3:
        render_metric_card("Net Spend", f"${cust_row['net_spend']:,.2f}", f"{cust_row['total_orders']} Orders")
    with c4:
        render_metric_card("Return Rate", f"{cust_row['return_rate']:.1f}%", f"{cust_row['returned_orders']} Returns", delta_positive=cust_row['return_rate'] < 10)

    st.markdown(
        f"**Demographics:** Age {cust_row['age']} • Gender: {cust_row['gender']} • Location: {cust_row['city']}, {cust_row['country']} • Preferred Category: **{cust_row['preferred_category']}**"
    )


apply_custom_css()
render_sidebar_status()
render_customer_intelligence_page()

