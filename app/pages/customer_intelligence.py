import sys
from pathlib import Path

# Ensure project root is in sys.path for direct Streamlit page execution
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="Customer Intelligence • RFM Segmentation",
    page_icon="👥",
    layout="wide",
)

from app.components.cards import render_metric_card  # noqa: E402
from app.components.styles import apply_custom_css, render_sidebar_status  # noqa: E402
from app.services.data_loader import get_cached_analytics_bundles  # noqa: E402
from src.utils.formatting import fmt_money, fmt_num, fmt_pct, is_missing  # noqa: E402


def _value(row, column):
    """Return a column from a row, or None when the active dataset does not provide it."""
    return row[column] if column in row.index else None


def _table_for_display(df):
    return df.astype(object).where(df.notna(), "N/A")


def render_customer_intelligence_page():
    """Render Customer Intelligence & RFM page."""
    st.markdown("## 👥 Customer Intelligence & Behavioral Segmentation")
    st.caption("Recency, Frequency, and Monetary (RFM) analytics and customer profiling.")

    from app.services.active_dataset_manager import render_global_active_dataset_banner
    render_global_active_dataset_banner(page_id="cust_intel")

    bundles = get_cached_analytics_bundles()
    cust_profiles = bundles["cust_profiles"]
    seg_summary = bundles["seg_summary"]

    if cust_profiles.empty:
        st.info(
            "This dataset has no customer-level records. Map a **Customer ID** column, together with a "
            "**Date** and **Revenue** column, in the Custom Data Analyzer to enable RFM segmentation."
        )
        return

    st.markdown("##### 📊 Segment Financial & Retention Matrix")
    st.dataframe(
        _table_for_display(seg_summary.rename(columns={
            "customer_segment": "Customer Segment",
            "customer_count": "Customers",
            "total_revenue": "Total Spend ($)",
            "avg_revenue_per_customer": "Spend/Customer ($)",
            "avg_orders": "Avg Orders",
            "avg_aov": "AOV ($)",
            "avg_return_rate": "Return Rate %",
        })),
        width="stretch",
        hide_index=True,
    )

    st.markdown("---")
    st.markdown("##### 🎯 Customer Value Mapping (Monetary Spend vs Order Frequency)")
    plot_df = cust_profiles.dropna(subset=["total_orders", "net_spend"])
    hover = [c for c in ["customer_id", "customer_segment", "city", "return_rate"] if c in plot_df.columns]
    fig = px.scatter(
        plot_df.sample(min(len(plot_df), 800), random_state=42),
        x="total_orders",
        y="net_spend",
        color="rfm_segment",
        size="average_order_value" if "average_order_value" in plot_df.columns else None,
        hover_data=hover,
        labels={"total_orders": "Total Orders Placed", "net_spend": "Net Lifetime Spend ($)"},
        template="plotly_white",
        height=380,
    )
    st.plotly_chart(fig, width="stretch", key="cust_intel_rfm_scatter")

    st.markdown("---")
    st.markdown("##### 🔍 Customer 360 Profile Drill-Down")
    selected_cid = st.selectbox(
        "Select or search Customer ID:",
        options=cust_profiles["customer_id"].tolist()[:100],
        index=0,
    )
    row = cust_profiles[cust_profiles["customer_id"] == selected_cid].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    membership = _value(row, "membership_type")
    with c1:
        render_metric_card("Customer", str(row["customer_id"]),
                           f"{membership} Member" if not is_missing(membership) else "Membership not in dataset")
    with c2:
        render_metric_card("Segment", str(row["customer_segment"]),
                           f"RFM: {row['rfm_score']}" if not is_missing(_value(row, "rfm_score")) else None)
    with c3:
        render_metric_card("Net Spend", fmt_money(row["net_spend"]), f"{fmt_num(row['total_orders'])} Orders")
    with c4:
        rate = _value(row, "return_rate")
        render_metric_card("Return Rate", fmt_pct(rate),
                           f"{fmt_num(_value(row, 'returned_orders'))} Returns" if rate is not None else "Return status not in dataset",
                           delta_positive=(rate is None or rate < 10))

    demo_bits = []
    for label, column in [("Age", "age"), ("Gender", "gender"), ("Location", "city"), ("Country", "country"),
                          ("Preferred Category", "preferred_category")]:
        value = _value(row, column)
        if not is_missing(value):
            demo_bits.append(f"{label}: **{value}**")
    if demo_bits:
        st.markdown("**Profile:** " + " • ".join(demo_bits))
    recency = _value(row, "recency_days")
    if not is_missing(recency):
        st.markdown(f"**Days since last order:** {fmt_num(recency)}")


apply_custom_css()
render_sidebar_status()
render_customer_intelligence_page()
