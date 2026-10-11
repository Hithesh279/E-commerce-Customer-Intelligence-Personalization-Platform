"""
app/components/styles.py
Modern enterprise UI styling and custom CSS for Streamlit dashboard.
"""
import streamlit as st


def apply_custom_css():
    """Inject custom CSS for polished styling, typography, and card layouts."""
    st.markdown(
        """
        <style>
        /* Modern Clean Base */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Metric Card Container */
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            transition: transform 0.15s ease-in-out;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .metric-card.success { border-left-color: #10b981; }
        .metric-card.warning { border-left-color: #f59e0b; }
        .metric-card.danger { border-left-color: #ef4444; }

        .metric-title {
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0f172a;
            margin: 4px 0;
        }
        .metric-delta {
            font-size: 0.85rem;
            font-weight: 500;
        }
        .metric-delta.positive { color: #10b981; }
        .metric-delta.negative { color: #ef4444; }

        /* Recommendation Product Card */
        .rec-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 14px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .rec-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: #1e293b;
        }
        .rec-meta {
            font-size: 0.85rem;
            color: #64748b;
            margin: 4px 0 8px 0;
        }
        .rec-score-badge {
            display: inline-block;
            background: #eff6ff;
            color: #2563eb;
            font-weight: 600;
            font-size: 0.8rem;
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 6px;
        }
        .rec-reason {
            font-size: 0.85rem;
            color: #334155;
            background: #f8fafc;
            padding: 8px 12px;
            border-left: 3px solid #3b82f6;
            border-radius: 4px;
            margin-top: 8px;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] select {
            color: #0f172a !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_status():
    """Render unified platform sidebar branding, global dataset manager, and system status."""
    st.sidebar.markdown("## 🛍️ Customer Intelligence")
    st.sidebar.caption("Portfolio Platform • v2.0.0")
    st.sidebar.markdown("---")

    from app.services.active_dataset_manager import (
        generate_active_dashboard_reports,
        get_active_dataset_state,
        load_template_as_active_dataset,
        reset_to_default_demo_dataset,
    )
    from src.analytics.templates import TEMPLATES_CONFIG

    state = get_active_dataset_state()
    is_custom = state is not None

    st.sidebar.markdown("### 📊 Active Platform Dataset")
    if is_custom:
        d_name = state["dataset_name"]
        rows = state["row_count"]
        cols = state["col_count"]
        st.sidebar.markdown(
            f"""
            <div style="background: #064e3b; border: 1px solid #059669; border-radius: 6px; padding: 10px; margin-bottom: 10px;">
                <div style="font-size: 0.78rem; color: #a7f3d0; font-weight: 600;">🟢 CUSTOM DATA ACTIVE</div>
                <div style="font-size: 0.88rem; color: #ffffff; font-weight: 700; margin-top: 2px; word-break: break-word;">{d_name}</div>
                <div style="font-size: 0.74rem; color: #d1fae5; margin-top: 4px;">{rows:,} rows × {cols} cols • Synced across all pages</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            """
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 10px; margin-bottom: 10px;">
                <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 600;">📦 DEMO STORE DATA</div>
                <div style="font-size: 0.88rem; color: #f8fafc; font-weight: 700; margin-top: 2px;">E-commerce Default Baseline</div>
                <div style="font-size: 0.74rem; color: #cbd5e1; margin-top: 4px;">1,000 txns • 200 customers • 50 products</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Quick Dataset Switcher
    st.sidebar.markdown("##### 🔄 Switch Platform Dataset:")
    template_options = ["(Current Active Dataset)", "📦 Default Demo Store Data"] + [
        f"{cfg['icon']} {cfg['name']}" for cfg in TEMPLATES_CONFIG.values()
    ]

    def _on_sidebar_template_change():
        chosen = st.session_state.get("_sb_template_pick")
        if not chosen or chosen == "(Current Active Dataset)":
            return
        if "Default Demo Store Data" in chosen:
            reset_to_default_demo_dataset()
        else:
            for tid, cfg in TEMPLATES_CONFIG.items():
                if cfg["name"] in chosen:
                    load_template_as_active_dataset(tid)
                    break
        # Reset selection key so it never retains the trigger item
        st.session_state["_sb_template_pick"] = "(Current Active Dataset)"

    st.sidebar.selectbox(
        "Choose a template or data source:",
        options=template_options,
        index=0,
        key="_sb_template_pick",
        on_change=_on_sidebar_template_change,
        label_visibility="collapsed",
    )

    if is_custom:
        if st.sidebar.button("↺ Reset to Demo Store Data", key="sidebar_btn_reset_default", use_container_width=True):
            reset_to_default_demo_dataset()
            st.session_state["_sb_template_pick"] = "(Current Active Dataset)"
            st.rerun()

    # 1-Click Download Entire Dashboard
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Download Entire Dashboard")
    st.sidebar.caption("Export the complete findings for the active dataset:")

    with st.sidebar.expander("📄 Export Reports & Data", expanded=False):
        rep = generate_active_dashboard_reports()
        st.download_button(
            label="📄 Executive Report (HTML/PDF)",
            data=rep["html_report"].encode("utf-8"),
            file_name=rep["html_filename"],
            mime="text/html",
            type="primary",
            key="sb_dl_html",
            use_container_width=True,
        )
        st.download_button(
            label="📊 Analytical Excel (.xlsx)",
            data=rep["excel_bytes"],
            file_name=rep["excel_filename"],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="sb_dl_excel",
            use_container_width=True,
        )
        st.download_button(
            label="📝 Executive Briefing (.md)",
            data=rep["md_report"].encode("utf-8"),
            file_name=rep["md_filename"],
            mime="text/markdown",
            key="sb_dl_md",
            use_container_width=True,
        )
        st.download_button(
            label="📁 Enriched Data (.csv)",
            data=rep["csv_bytes"],
            file_name=rep["csv_filename"],
            mime="text/csv",
            key="sb_dl_csv",
            use_container_width=True,
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        **System Status:**
        - 🟢 SQLite Database: Connected
        - 🟢 ML Artifacts: Loaded
        - 🟢 Offline Split: Time-Aware
        """
    )
    st.sidebar.caption("Designed for Data Science & ML Engineering Portfolio")


