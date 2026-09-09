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
    """Render unified platform sidebar branding and system status."""
    st.sidebar.markdown("## 🛍️ Customer Intelligence")
    st.sidebar.caption("Portfolio Platform • v1.0.0")
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

