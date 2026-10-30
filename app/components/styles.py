"""
app/components/styles.py
Modern enterprise UI styling and custom CSS for Streamlit dashboard.
"""
import base64
import html

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
    from app.services.active_dataset_manager import (
        get_active_dataset_state,
        get_active_export_data,
        get_active_export_filename,
        get_cached_export,
        get_default_demo_summary,
        get_system_status,
        load_template_as_active_dataset,
        platform_version,
        reset_to_default_demo_dataset,
    )
    from src.analytics.templates import TEMPLATES_CONFIG

    st.sidebar.markdown("## 🛍️ Customer Intelligence")
    st.sidebar.caption(f"Customer Intelligence Platform • v{platform_version()}")
    st.sidebar.markdown("---")

    state = get_active_dataset_state()
    is_custom = state is not None
    counts = get_default_demo_summary()

    st.sidebar.markdown("### 📊 Active Platform Dataset")
    if is_custom:
        d_name = html.escape(str(state["dataset_name"]))
        st.sidebar.markdown(
            f"""
            <div style="background: #064e3b; border: 1px solid #059669; border-radius: 6px; padding: 10px; margin-bottom: 10px;">
                <div style="font-size: 0.78rem; color: #a7f3d0; font-weight: 600;">🟢 CUSTOM DATA ACTIVE</div>
                <div style="font-size: 0.88rem; color: #ffffff; font-weight: 700; margin-top: 2px; word-break: break-word;">{d_name}</div>
                <div style="font-size: 0.74rem; color: #d1fae5; margin-top: 4px;">{state['row_count']:,} rows × {state['col_count']} cols • Synced across all pages</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 10px; margin-bottom: 10px;">
                <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 600;">📦 DEMO STORE DATA</div>
                <div style="font-size: 0.88rem; color: #f8fafc; font-weight: 700; margin-top: 2px;">E-commerce Default Baseline</div>
                <div style="font-size: 0.74rem; color: #cbd5e1; margin-top: 4px;">{counts['transactions']:,} txns • {counts['customers']:,} customers • {counts['products']:,} products</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
        if st.sidebar.button("↺ Reset to Demo Store Data", key="sidebar_btn_reset_default", width="stretch"):
            reset_to_default_demo_dataset()
            st.session_state["_sb_template_pick"] = "(Current Active Dataset)"
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Download Entire Dashboard")
    st.sidebar.caption("Export the complete findings for the active dataset:")

    with st.sidebar.expander("📄 Export Reports & Data", expanded=False):
        sb_state = get_active_dataset_state()
        html_fn = get_active_export_filename("html", state=sb_state)
        st.download_button(
            label="📄 Executive Report (HTML/PDF)",
            data=lambda s=sb_state: get_active_export_data("html", state=s),
            file_name=html_fn,
            mime="text/html",
            type="primary",
            key="sb_dl_html",
            use_container_width=True,
        )
        cached_h = get_cached_export("html", state=sb_state)
        if cached_h:
            raw_b = cached_h if isinstance(cached_h, bytes) else cached_h.encode("utf-8")
            b64_h = base64.b64encode(raw_b).decode("utf-8")
            st.markdown(
                f'<div style="text-align:center; margin-bottom:6px;"><a href="data:text/html;charset=utf-8;base64,{b64_h}" download="{html_fn}" style="font-size:0.75rem; color:#3b82f6; text-decoration:underline;">⬇️ Direct Browser Download</a></div>',
                unsafe_allow_html=True,
            )

        excel_fn = get_active_export_filename("excel", state=sb_state)
        st.download_button(
            label="📊 Analytical Excel (.xlsx)",
            data=lambda s=sb_state: get_active_export_data("excel", state=s),
            file_name=excel_fn,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="sb_dl_excel",
            use_container_width=True,
        )
        cached_x = get_cached_export("excel", state=sb_state)
        if cached_x:
            raw_b = cached_x if isinstance(cached_x, bytes) else cached_x.encode("utf-8")
            b64_x = base64.b64encode(raw_b).decode("utf-8")
            st.markdown(
                f'<div style="text-align:center; margin-bottom:6px;"><a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_x}" download="{excel_fn}" style="font-size:0.75rem; color:#3b82f6; text-decoration:underline;">⬇️ Direct Browser Download</a></div>',
                unsafe_allow_html=True,
            )

        md_fn = get_active_export_filename("md", state=sb_state)
        st.download_button(
            label="📝 Executive Briefing (.md)",
            data=lambda s=sb_state: get_active_export_data("md", state=s),
            file_name=md_fn,
            mime="text/markdown",
            key="sb_dl_md",
            use_container_width=True,
        )
        csv_fn = get_active_export_filename("csv", state=sb_state)
        st.download_button(
            label="📁 Enriched Data (.csv)",
            data=lambda s=sb_state: get_active_export_data("csv", state=s),
            file_name=csv_fn,
            mime="text/csv",
            key="sb_dl_csv",
            use_container_width=True,
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**System Status:**")
    for label, ok in get_system_status():
        st.sidebar.markdown(f"- {'🟢' if ok else '🔴'} {label}: {'ready' if ok else 'missing, run the pipeline'}")
    st.sidebar.caption("Built for data science and ML engineering portfolio review")
