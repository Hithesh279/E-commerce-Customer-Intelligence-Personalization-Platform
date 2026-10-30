"""
app/pages/custom_data_analyzer.py
User Data Upload & Auto-Generated Interactive Dashboard.
Supports CSV/Excel/ZIP uploads, local folder scanning, 12 pre-built enterprise business templates,
automated schema inference, NLP batch sentiment, RFM customer profiling, and enriched exports.
"""
from datetime import datetime
import io
import sys
from pathlib import Path
from typing import Dict

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Custom Data Analyzer • Customer Intelligence",
    page_icon="📁",
    layout="wide",
)

from app.components.cards import render_metric_card, render_quote
from app.components.charts import (
    plot_aspect_radar,
    plot_category_sales,
    plot_correlation_heatmap,
    plot_metric_timeline,
    plot_revenue_trend,
    plot_rfm_scatter,
    plot_segment_distribution,
    plot_sentiment_donut,
)
from app.components.styles import apply_custom_css, render_sidebar_status
from src.analytics.auto_analyzer import (
    analyze_custom_reviews,
    analyze_custom_transactions,
    calculate_custom_rfm,
    detect_schema,
    profile_generic_table,
)
from src.utils.formatting import fmt_money, fmt_num, fmt_pct, fmt_signed
from src.analytics.templates import (
    generate_blank_template_csv,
    get_available_templates,
    load_sample_template,
)


def render_custom_analyzer_page():
    """Render the Custom Data Analyzer and Auto-Dashboard page."""
    apply_custom_css()
    render_sidebar_status()

    # Hero Header
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 22px 28px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #334155;">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #f8fafc;">📁 Custom Data Upload & Auto-Dashboard Generator</h2>
            <p style="margin: 8px 0 0 0; font-size: 0.95rem; color: #cbd5e1; line-height: 1.5;">
                Upload your company's CSV or Excel data — or choose from our comprehensive library of <strong>12 enterprise business templates</strong> 
                across Sales, Voice of Customer, RFM, Supply Chain, and Marketing. Our platform automatically inspects the schema, executes batch NLP 
                sentiment classification, computes commercial KPIs, and generates an interactive executive dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    templates = get_available_templates()

    from src.analytics.multi_file_loader import (
        auto_join_relational_tables,
        check_schema_compatibility,
        combine_homogeneous_tables,
        compute_bytes_hash,
        compute_directory_signature,
        load_zip_archive_cached,
        parse_tabular_file_cached,
        scan_local_directory_cached,
    )

    # Ingestion Source Selector
    st.markdown("##### 📥 Step 1: Select Data Ingestion Source")
    ingest_mode = st.radio(
        "Choose how you want to provide data:",
        [
            "📋 Use Enterprise Business Template (12 Ready-to-Use)",
            "📄 Upload Single File (CSV or Excel)",
            "🗂️ Upload Multiple Files / Folder ZIP",
            "📁 Scan Local Directory / Folder on Disk",
        ],
        horizontal=True,
    )

    active_df = None
    data_source_label = ""

    if ingest_mode.startswith("📋 Use Enterprise Business Template"):
        st.markdown(
            """
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                <strong style="color: #1e293b; font-size: 0.95rem;">Select from 12 Pre-Configured Enterprise Business Templates:</strong>
                <p style="font-size: 0.85rem; color: #64748b; margin: 4px 0 0 0;">
                    Each template is tailored for a specific e-commerce workflow. Test it with 1-click synthetic data generation, or download the blank CSV schema to populate with your own records.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        all_categories = ["All Categories"] + sorted(list(set(t["category"] for t in templates.values())))
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            selected_cat = st.selectbox("Filter by Domain / Vertical:", all_categories)

        filtered_keys = [
            k for k, t in templates.items()
            if selected_cat == "All Categories" or t["category"] == selected_cat
        ]

        template_display_names = [
            f"{templates[k]['icon']} {templates[k]['name']} — [{templates[k]['category']}]"
            for k in filtered_keys
        ]

        with f_col2:
            selected_idx = st.selectbox(
                "Choose Template Schema:",
                range(len(filtered_keys)),
                format_func=lambda i: template_display_names[i],
            )
        selected_key = filtered_keys[selected_idx]
        t_meta = templates[selected_key]

        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            st.markdown(f"**Description**: {t_meta['description']}")
            st.caption(f"**Standard Schema Columns**: `{', '.join(t_meta['columns'])}`")
        with col_t2:
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            blank_csv = generate_blank_template_csv(selected_key)
            st.download_button(
                label=f"📥 Download Blank Template CSV",
                data=blank_csv,
                file_name=f"{selected_key}_template.csv",
                mime="text/csv",
                width="stretch",
            )

        btn_load = st.button("⚡ Load & Analyze This Template", type="primary", width="content")
        if btn_load or f"template_{selected_key}_loaded" in st.session_state:
            st.session_state[f"template_{selected_key}_loaded"] = True
            active_df = load_sample_template(selected_key, n_records=150)
            data_source_label = f"Template: {t_meta['name']}"

    elif ingest_mode.startswith("📄 Upload Single File"):
        uploaded_file = st.file_uploader(
            "Upload your dataset (CSV or Excel file):",
            type=["csv", "xlsx", "xls"],
            help="Upload raw customer reviews, sales transactions, support tickets, or any tabular business data.",
        )
        if uploaded_file is not None:
            try:
                content = uploaded_file.getvalue()
                f_size = len(content)
                f_name = uploaded_file.name
                file_id = getattr(uploaded_file, "file_id", f"{f_name}_{f_size}")
                cached_hash_key = f"_fhash_{file_id}"
                if cached_hash_key in st.session_state:
                    f_hash = st.session_state[cached_hash_key]
                else:
                    f_hash = compute_bytes_hash(content)
                    st.session_state[cached_hash_key] = f_hash

                active_df = parse_tabular_file_cached(
                    _file_bytes=content,
                    filename=f_name,
                    file_size=f_size,
                    file_hash=f_hash,
                )
                data_source_label = f"Uploaded File: {f_name}"
            except Exception as e:
                st.error(f"Error loading uploaded file: {e}")
                return

    elif ingest_mode.startswith("🗂️ Upload Multiple Files"):
        st.markdown(
            """
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 14px;">
                <strong style="color: #1e293b; font-size: 0.95rem;">Upload Multiple Datasets or Zipped Folder:</strong>
                <p style="font-size: 0.85rem; color: #64748b; margin: 4px 0 0 0;">
                    Select multiple CSV/Excel files at once, or upload a <strong>.zip folder</strong> containing your datasets. 
                    Compatible files can be automatically unified into a single master dataset, or inspected individually.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_files = st.file_uploader(
            "Choose multiple CSV/Excel files or a .ZIP archive:",
            type=["csv", "xlsx", "xls", "zip"],
            accept_multiple_files=True,
            help="Select multiple files using Ctrl/Shift+Click, or drop a zipped folder.",
        )

        loaded_tables: Dict[str, pd.DataFrame] = {}
        if uploaded_files:
            for uf in uploaded_files:
                content = uf.getvalue()
                f_size = len(content)
                f_name = uf.name
                file_id = getattr(uf, "file_id", f"{f_name}_{f_size}")
                cached_hash_key = f"_fhash_{file_id}"
                if cached_hash_key in st.session_state:
                    f_hash = st.session_state[cached_hash_key]
                else:
                    f_hash = compute_bytes_hash(content)
                    st.session_state[cached_hash_key] = f_hash

                if f_name.lower().endswith(".zip"):
                    try:
                        extracted = load_zip_archive_cached(
                            _zip_bytes=content,
                            filename=f_name,
                            file_size=f_size,
                            file_hash=f_hash,
                        )
                        loaded_tables.update(extracted)
                    except Exception as e:
                        st.error(f"Error reading ZIP archive {f_name}: {e}")
                else:
                    try:
                        df_single = parse_tabular_file_cached(
                            _file_bytes=content,
                            filename=f_name,
                            file_size=f_size,
                            file_hash=f_hash,
                        )
                        loaded_tables[f_name] = df_single
                    except Exception as e:
                        st.error(f"Error reading file {f_name}: {e}")

        if loaded_tables:
            st.success(f"Successfully loaded {len(loaded_tables)} dataset(s): {', '.join(loaded_tables.keys())}")
            # Display multi-file inventory table
            multi_inv = pd.DataFrame([
                {"File Name": name, "Rows": len(df), "Columns": len(df.columns), "Size (KB)": round(df.memory_usage(deep=True).sum() / 1024, 1)}
                for name, df in loaded_tables.items()
            ])
            st.dataframe(multi_inv, width="stretch", hide_index=True)

            is_compat, shared = check_schema_compatibility(loaded_tables)
            if len(loaded_tables) > 1:
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    merge_opt = st.radio(
                        "How would you like to analyze these files?",
                        [
                            "🔗 Combine all files into unified master dataset" if is_compat else "🔗 Auto-Join relational tables on common ID keys",
                            "🔍 Select a specific file to analyze individually",
                        ],
                    )

                if merge_opt.startswith("🔗 Combine"):
                    active_df = combine_homogeneous_tables(loaded_tables)
                    data_source_label = f"Consolidated {len(loaded_tables)} Files ({len(active_df):,} total rows)"
                elif merge_opt.startswith("🔗 Auto-Join"):
                    active_df, msg = auto_join_relational_tables(loaded_tables)
                    st.info(msg)
                    data_source_label = f"Relational Joined Dataset ({len(active_df):,} rows)"
                else:
                    with col_act2:
                        chosen_table = st.selectbox("Select file to analyze in dashboard:", list(loaded_tables.keys()))
                    active_df = loaded_tables[chosen_table]
                    data_source_label = f"File: {chosen_table}"
            else:
                only_name = list(loaded_tables.keys())[0]
                active_df = loaded_tables[only_name]
                data_source_label = f"File: {only_name}"

    elif ingest_mode.startswith("📁 Scan Local Directory"):
        st.markdown(
            """
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 14px;">
                <strong style="color: #1e293b; font-size: 0.95rem;">Scan & Ingest from Local Machine Folder:</strong>
                <p style="font-size: 0.85rem; color: #64748b; margin: 4px 0 0 0;">
                    Enter a folder inside the project data directory (or a folder listed in the LOCAL_SCAN_ROOTS environment variable). All CSV and Excel files in it are imported.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c_p1, c_p2 = st.columns([3, 1])
        with c_p1:
            local_path_input = st.text_input(
                "Local Directory Path:",
                value="data/raw",
                help="Relative paths resolve against the project root. Folders outside the allowed locations are refused.",
            )
        with c_p2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            scan_btn = st.button("🔍 Scan & Ingest Folder", type="primary")

        if scan_btn or "scanned_local_path" in st.session_state:
            if scan_btn:
                st.session_state["scanned_local_path"] = local_path_input

            target_path = st.session_state.get("scanned_local_path", local_path_input)
            try:
                dir_sig = compute_directory_signature(target_path)
                scanned_tables = scan_local_directory_cached(str(target_path), dir_sig)
                if not scanned_tables:
                    st.warning(f"No CSV or Excel files found in directory: `{target_path}`")
                else:
                    st.success(f"Found {len(scanned_tables)} datasets in `{target_path}`: {', '.join(scanned_tables.keys())}")
                    multi_inv = pd.DataFrame([
                        {"File Name": name, "Rows": len(df), "Columns": len(df.columns), "Size (KB)": round(df.memory_usage(deep=True).sum() / 1024, 1)}
                        for name, df in scanned_tables.items()
                    ])
                    st.dataframe(multi_inv, width="stretch", hide_index=True)

                    is_compat, shared = check_schema_compatibility(scanned_tables)
                    if len(scanned_tables) > 1:
                        c_opt1, c_opt2 = st.columns(2)
                        with c_opt1:
                            folder_merge_opt = st.radio(
                                "Multi-File Strategy:",
                                [
                                    "🔗 Combine all files into unified master dataset" if is_compat else "🔗 Auto-Join relational tables on common ID keys",
                                    "🔍 Select a specific file to analyze individually",
                                ],
                                key="folder_merge_strategy",
                            )

                        if folder_merge_opt.startswith("🔗 Combine"):
                            active_df = combine_homogeneous_tables(scanned_tables)
                            data_source_label = f"Folder Ingestion: {len(scanned_tables)} Files Consolidated ({len(active_df):,} rows)"
                        elif folder_merge_opt.startswith("🔗 Auto-Join"):
                            active_df, msg = auto_join_relational_tables(scanned_tables)
                            st.info(msg)
                            data_source_label = f"Folder Relational Joined ({len(active_df):,} rows)"
                        else:
                            with c_opt2:
                                chosen_file = st.selectbox("Select file to analyze:", list(scanned_tables.keys()), key="folder_sel_file")
                            active_df = scanned_tables[chosen_file]
                            data_source_label = f"Folder File: {chosen_file}"
                    else:
                        single_k = list(scanned_tables.keys())[0]
                        active_df = scanned_tables[single_k]
                        data_source_label = f"Folder File: {single_k}"

            except Exception as e:
                st.error(f"Error scanning folder: {e}")
                return

    if active_df is None or active_df.empty:
        st.info("👆 Please select a business template and click **Load & Analyze**, or upload your own CSV/Excel file to start.")
        return

    # Auto-detection
    schema_info = detect_schema(active_df)
    mappings = schema_info["mappings"]
    modalities = schema_info["modalities"]

    # File Summary Ribbon
    st.markdown("---")
    st.markdown("##### 📊 Dataset Profile & Auto-Detected Schema")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Total Records", f"{len(active_df):,}")
    with m_col2:
        st.metric("Total Columns", f"{len(active_df.columns):,}")
    with m_col3:
        st.metric("Memory Footprint", f"{active_df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    with m_col4:
        tag_list = []
        if modalities["has_reviews"]:
            tag_list.append("💬 Reviews / VoC")
        if modalities["has_transactions"]:
            tag_list.append("🛍️ Transactions")
        if modalities["has_rfm"]:
            tag_list.append("👥 RFM Profiles")
        if not tag_list:
            tag_list.append("📊 Tabular")
        st.metric("Detected Modality", " + ".join(tag_list))

    # Column Mapping Override Expander
    with st.expander("🛠️ Review / Customize Column Mappings (Optional)", expanded=False):
        st.caption("Our smart schema detector identified the candidate columns below. You can override any mapping if needed:")
        cols_options = ["None"] + list(active_df.columns)

        def get_default_idx(col_name):
            if col_name in active_df.columns:
                return cols_options.index(col_name)
            return 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            sel_text = st.selectbox("Text / Review Column:", cols_options, index=get_default_idx(mappings.get("text_col")))
            sel_sentiment = st.selectbox("Sentiment / Polarity Column:", cols_options, index=get_default_idx(mappings.get("sentiment_col")))
            sel_rating = st.selectbox("Rating / Score Column:", cols_options, index=get_default_idx(mappings.get("rating_col")))
        with c2:
            sel_date = st.selectbox("Date / Timestamp Column:", cols_options, index=get_default_idx(mappings.get("date_col")))
            sel_revenue = st.selectbox("Revenue / Amount Column:", cols_options, index=get_default_idx(mappings.get("revenue_col")))
        with c3:
            sel_cust = st.selectbox("Customer ID Column:", cols_options, index=get_default_idx(mappings.get("customer_col")))
            sel_prod = st.selectbox("Product / SKU Column:", cols_options, index=get_default_idx(mappings.get("product_col")))
        with c4:
            sel_cat = st.selectbox("Category / Dept Column:", cols_options, index=get_default_idx(mappings.get("category_col")))
            sel_status = st.selectbox("Status / Return Column:", cols_options, index=get_default_idx(mappings.get("status_col")))

        # Apply overrides
        text_col = None if sel_text == "None" else sel_text
        sentiment_col = None if sel_sentiment == "None" else sel_sentiment
        rating_col = None if sel_rating == "None" else sel_rating
        date_col = None if sel_date == "None" else sel_date
        revenue_col = None if sel_revenue == "None" else sel_revenue
        customer_col = None if sel_cust == "None" else sel_cust
        product_col = None if sel_prod == "None" else sel_prod
        category_col = None if sel_cat == "None" else sel_cat
        status_col = None if sel_status == "None" else sel_status

        # Synchronize overrides back to schema_info mappings dictionary
        mappings.update({
            "text_col": text_col,
            "sentiment_col": sentiment_col,
            "rating_col": rating_col,
            "date_col": date_col,
            "revenue_col": revenue_col,
            "customer_col": customer_col,
            "product_col": product_col,
            "category_col": category_col,
            "status_col": status_col,
        })
        schema_info["mappings"] = mappings

    # Data Processing with Intelligent In-Memory Caching
    analysis_sig = (
        data_source_label,
        len(active_df),
        tuple(active_df.columns),
        text_col,
        sentiment_col,
        rating_col,
        date_col,
        revenue_col,
        customer_col,
        product_col,
        category_col,
        status_col,
    )

    cached_sig = st.session_state.get("_analyzer_cache_sig")
    active_ds = st.session_state.get("active_dataset")

    if cached_sig == analysis_sig and active_ds is not None and active_ds.get("enriched_df") is not None:
        # Re-use already computed ML results and aggregations instantaneously (0ms)
        enriched_df = active_ds["enriched_df"]
        reviews_data = active_ds["reviews_data"]
        txn_data = active_ds["txn_data"]
        rfm_df = active_ds["rfm_df"]
        rfm_metrics = active_ds["rfm_metrics"]
        table_profile = active_ds["table_profile"]
    else:
        with st.spinner("Executing ML inference and analytics aggregations..."):
            # Reviews analysis
            reviews_data = None
            enriched_df = active_df.copy()
            if (text_col and text_col in active_df.columns) or (sentiment_col and sentiment_col in active_df.columns) or (rating_col and rating_col in active_df.columns):
                enriched_df, reviews_data = analyze_custom_reviews(
                    active_df,
                    text_col=text_col,
                    rating_col=rating_col,
                    sentiment_col=sentiment_col,
                )

            # Transactions analysis
            txn_data = analyze_custom_transactions(
                enriched_df,
                date_col=date_col,
                revenue_col=revenue_col,
                customer_col=customer_col,
                category_col=category_col,
                product_col=product_col,
                status_col=status_col,
            )

            # RFM analysis
            rfm_df, rfm_metrics = None, None
            if customer_col and (date_col or "lifetime_spend" in [str(c).lower() for c in active_df.columns]):
                try:
                    rfm_df, rfm_metrics = calculate_custom_rfm(
                        enriched_df,
                        customer_col=customer_col,
                        date_col=date_col,
                        revenue_col=revenue_col,
                    )
                except Exception as e:
                    rfm_df, rfm_metrics = None, None

            # Generic profiling
            table_profile = profile_generic_table(enriched_df)

            # Synchronize this dataset globally across all platform pages
            from app.services.active_dataset_manager import set_active_custom_dataset
            set_active_custom_dataset(
                df=active_df,
                source_label=data_source_label,
                schema_info=schema_info,
                txn_data=txn_data,
                reviews_data=reviews_data,
                rfm_df=rfm_df,
                rfm_metrics=rfm_metrics,
                table_profile=table_profile,
                enriched_df=enriched_df,
                analysis_sig=analysis_sig,
            )
            st.session_state["_analyzer_cache_sig"] = analysis_sig

    # 4 Dynamic Dashboard Sections & Top-level Quick Report Download
    st.markdown("---")
    st.success(f"🌐 **Active Platform Dataset Synchronized:** All pages (**Main**, **Overview**, **Customer Intelligence**, **Product Intelligence**, **NLP Insights**, **Recommendations**) are now displaying this dataset!")
    st.markdown(f"### 📈 Interactive Auto-Dashboard: {data_source_label}")

    # pyrefly: ignore [missing-import]
    from app.services.active_dataset_manager import render_download_panel
    with st.expander("📥 1-Click Download Generated Dashboard & Reports", expanded=True):
        render_download_panel(key_prefix="top_auto_dl", show_header=False)

    section_options = [
        "📈 Executive KPIs & Trends",
        "🧠 NLP & Aspect Intelligence",
        "👥 Customer Behavioral & RFM",
        "📁 Data Explorer & Download Reports",
    ]
    if hasattr(st, "segmented_control"):
        active_section = st.segmented_control(
            "Dashboard View",
            section_options,
            default=section_options[0],
            key="custom_dashboard_active_tab",
            label_visibility="collapsed",
        )
    else:
        active_section = st.radio(
            "Dashboard View",
            section_options,
            index=0,
            horizontal=True,
            key="custom_dashboard_active_tab",
            label_visibility="collapsed",
        )
    if not active_section:
        active_section = section_options[0]

    # ==========================================
    # SECTION 1: EXECUTIVE KPIS & TRENDS
    # ==========================================
    if active_section.startswith("📈"):
        st.markdown("#### 🏆 High-Level Business Performance Scorecards")
        kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)

        if revenue_col and revenue_col in enriched_df.columns:
            with kpi_c1:
                render_metric_card(
                    title="Total Revenue",
                    value=fmt_money(txn_data['total_revenue']),
                    delta="Cumulative Spend",
                    delta_positive=True,
                    card_type="success",
                )
            with kpi_c2:
                render_metric_card(
                    title="Total Orders",
                    value=fmt_num(txn_data['total_orders']),
                    delta="Completed Records",
                    card_type="default",
                )
            with kpi_c3:
                render_metric_card(
                    title="Average Order Value",
                    value=fmt_money(txn_data['aov']),
                    delta="Per Transaction",
                    card_type="default",
                )
            with kpi_c4:
                render_metric_card(
                    title="Unique Customers",
                    value=fmt_num(txn_data['unique_customers']),
                    delta="Active Buyers",
                    card_type="default",
                )
            with kpi_c5:
                render_metric_card(
                    title="Return / Churn Rate",
                    value=fmt_pct(txn_data['return_rate']),
                    delta="Exception Rate",
                    delta_positive=(txn_data['return_rate'] is None or txn_data['return_rate'] < 10.0),
                    card_type="warning" if (txn_data['return_rate'] or 0) >= 10.0 else "success",
                )
        elif reviews_data is not None:
            with kpi_c1:
                render_metric_card(
                    title="Total Reviews Analyzed",
                    value=f"{reviews_data['total_reviews']:,}",
                    delta="NLP Processed",
                    card_type="default",
                )
            with kpi_c2:
                render_metric_card(
                    title="Positive Sentiment",
                    value=fmt_pct(reviews_data['positive_pct']),
                    delta="Brand Advocates",
                    delta_positive=(reviews_data['positive_pct'] or 0) > 50,
                    card_type="success",
                )
            with kpi_c3:
                render_metric_card(
                    title="Negative Sentiment",
                    value=fmt_pct(reviews_data['negative_pct']),
                    delta="Dissatisfied",
                    delta_positive=(reviews_data['negative_pct'] or 0) < 20,
                    card_type="danger" if (reviews_data['negative_pct'] or 0) > 25 else "warning",
                )
            with kpi_c4:
                render_metric_card(
                    title="Polarity Index",
                    value=fmt_signed(reviews_data['avg_polarity']),
                    delta="Scale: -1.0 to +1.0",
                    delta_positive=(reviews_data['avg_polarity'] or 0) > 0,
                    card_type="success" if (reviews_data['avg_polarity'] or 0) > 0 else "danger",
                )
            with kpi_c5:
                aspect_cnt = len(reviews_data['aspect_summary']) if not reviews_data['aspect_summary'].empty else 0
                render_metric_card(
                    title="Aspects Extracted",
                    value=f"{aspect_cnt}",
                    delta="Granular Features",
                    card_type="default",
                )
        else:
            with kpi_c1:
                render_metric_card(title="Total Rows", value=f"{table_profile['row_count']:,}", card_type="default")
            with kpi_c2:
                render_metric_card(title="Total Columns", value=f"{table_profile['col_count']:,}", card_type="default")
            with kpi_c3:
                render_metric_card(title="Duplicate Rows", value=f"{table_profile['duplicate_rows']:,}", card_type="warning" if table_profile['duplicate_rows'] > 0 else "success")
            with kpi_c4:
                render_metric_card(title="Memory Size", value=f"{table_profile['memory_mb']:.2f} MB", card_type="default")
            with kpi_c5:
                render_metric_card(title="Completeness", value=f"{100 - table_profile['missing_overview']['missing_pct'].mean():.1f}%", card_type="success")

        # Visualizations Row 1
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_v1, col_v2 = st.columns(2)

        with col_v1:
            if not txn_data["timeline_df"].empty:
                st.plotly_chart(
                    plot_revenue_trend(
                        txn_data["timeline_df"].rename(
                            columns={"period": "year_month", "revenue": "total_revenue"}
                        )
                    ),
                    width="stretch",
                    key="custom_overview_rev_trend",
                )
            elif reviews_data is not None:
                st.plotly_chart(
                    plot_sentiment_donut(reviews_data["sentiment_counts"]),
                    width="stretch",
                    key="custom_overview_sentiment_donut",
                )
            elif not table_profile["summary_stats"].empty:
                num_col = table_profile["summary_stats"]["feature"].iloc[0]
                fig_num = px.histogram(enriched_df, x=num_col, title=f"Distribution of {num_col}", template="plotly_white")
                st.plotly_chart(fig_num, width="stretch", key="custom_overview_numeric_hist")
            else:
                st.info("No time series or numeric distribution data available.")

        with col_v2:
            if not txn_data["category_df"].empty:
                st.plotly_chart(
                    plot_category_sales(txn_data["category_df"]),
                    width="stretch",
                    key="custom_overview_category_sales",
                )
            elif reviews_data is not None and not reviews_data["aspect_summary"].empty:
                st.plotly_chart(
                    plot_aspect_radar(reviews_data["aspect_summary"]),
                    width="stretch",
                    key="custom_overview_aspect_radar",
                )
            elif len(table_profile["summary_stats"]) > 1:
                num_col2 = table_profile["summary_stats"]["feature"].iloc[1]
                fig_num2 = px.box(enriched_df, y=num_col2, title=f"Boxplot of {num_col2}", template="plotly_white")
                st.plotly_chart(fig_num2, width="stretch", key="custom_overview_numeric_box")
            else:
                st.info("No category or aspect distribution data available.")

        # Top Items Leaderboard
        if not txn_data["top_products_df"].empty:
            st.markdown("##### 🏆 Top Ranked Products / Items")
            st.dataframe(txn_data["top_products_df"], width="stretch", hide_index=True)

    # ==========================================
    # SECTION 2: NLP & ASPECT INTELLIGENCE
    # ==========================================
    elif active_section.startswith("🧠"):
        if reviews_data is not None:
            st.markdown("#### 🧠 Natural Language Sentiment & 11-Aspect Extraction")
            st.caption("Batch ML classification evaluating sentiment polarities and extracting hardware/feature satisfaction drivers.")

            c_nlp1, c_nlp2 = st.columns(2)
            with c_nlp1:
                st.plotly_chart(
                    plot_sentiment_donut(reviews_data["sentiment_counts"]),
                    width="stretch",
                    key="custom_nlp_sentiment_donut",
                )

            with c_nlp2:
                if not reviews_data["aspect_summary"].empty:
                    st.plotly_chart(
                        plot_aspect_radar(reviews_data["aspect_summary"]),
                        width="stretch",
                        key="custom_nlp_aspect_radar",
                    )
                else:
                    st.info("No specific hardware aspects detected in the reviews.")

            # Aspect Details Table
            if not reviews_data["aspect_summary"].empty:
                st.markdown("##### 🔍 Aspect Polarity Leaderboard")
                st.dataframe(
                    reviews_data["aspect_summary"].rename(
                        columns={
                            "aspect": "Product Aspect",
                            "mentions": "Total Mentions",
                            "avg_sentiment_score": "Sentiment Polarity Score (-1 to +1)",
                            "positive_mentions": "Positive Mentions",
                            "negative_mentions": "Negative Mentions",
                        }
                    ),
                    width="stretch",
                    hide_index=True,
                )

            # Sample Quotes Section
            st.markdown("##### 💬 Voice of Customer Highlights:")
            q_col1, q_col2 = st.columns(2)
            with q_col1:
                st.markdown("**🟢 Positive Customer Quotes:**")
                for q in reviews_data["positive_quotes"]:
                    render_quote(q, tone="positive")
            with q_col2:
                st.markdown("**🔴 Negative Customer Quotes (Areas for Improvement):**")
                for q in reviews_data["negative_quotes"]:
                    render_quote(q, tone="negative")

        else:
            st.info("💡 To view NLP & Aspect Intelligence, select or map a text column in the mapping expander above.")

    # ==========================================
    # SECTION 3: CUSTOMER BEHAVIORAL & RFM
    # ==========================================
    elif active_section.startswith("👥"):
        if rfm_df is not None and rfm_metrics is not None:
            st.markdown("#### 👥 Customer Behavioral RFM Segmentation")
            st.caption("Quantile-based Recency, Frequency, and Monetary scoring segmenting customers into actionable behavioral clusters.")

            rfm_c1, rfm_c2, rfm_c3, rfm_c4 = st.columns(4)
            with rfm_c1:
                render_metric_card("Total Customers", f"{rfm_metrics['total_customers']:,}", card_type="default")
            with rfm_c2:
                render_metric_card("Champions Count", fmt_num(rfm_metrics['champions_count']), delta=None if rfm_metrics.get('recency_available') else "Needs dates for recency", card_type="success")
            with rfm_c3:
                render_metric_card("At-Risk Count", fmt_num(rfm_metrics['at_risk_count']), delta=None if rfm_metrics.get('recency_available') else "Needs dates for recency", card_type="danger")
            with rfm_c4:
                render_metric_card("Avg Customer Spend", fmt_money(rfm_metrics['avg_monetary']), card_type="default")

            rfm_v1, rfm_v2 = st.columns(2)
            with rfm_v1:
                st.plotly_chart(
                    plot_segment_distribution(rfm_metrics["segment_summary"]),
                    width="stretch",
                    key="custom_rfm_segment_distribution",
                )
            with rfm_v2:
                st.plotly_chart(
                    plot_rfm_scatter(rfm_df),
                    width="stretch",
                    key="custom_rfm_scatter",
                )

            st.markdown("##### 🏅 VIP Customer Leaderboard")
            top_rfm = rfm_df.sort_values("monetary_total", ascending=False).head(10)
            st.dataframe(top_rfm, width="stretch", hide_index=True)

        else:
            st.info("💡 To view RFM Segmentation, map a **Customer ID** column along with a **Date** and **Revenue** column above.")

    # ==========================================
    # SECTION 4: DATA EXPLORER & ENRICHED EXPORT
    # ==========================================
    elif active_section.startswith("📁"):
        st.markdown("#### 📁 Interactive Data Explorer & Statistical Profiling")

        # Correlation Heatmap
        if not table_profile["corr_matrix"].empty:
            st.plotly_chart(
                plot_correlation_heatmap(table_profile["corr_matrix"]),
                width="stretch",
                key="custom_corr_heatmap",
            )

        # Summary Statistics
        if not table_profile["summary_stats"].empty:
            st.markdown("##### 🔢 Numerical Feature Summary Statistics")
            st.dataframe(table_profile["summary_stats"], width="stretch", hide_index=True)

        # Enriched Data Table
        st.markdown("##### 📄 Enriched Dataset Preview (with ML Predictions & Aspect Tags)")
        st.dataframe(enriched_df.head(100), width="stretch")

        # Report and Dataset Download Suite
        st.markdown("---")
        from app.services.active_dataset_manager import render_download_panel
        render_download_panel(key_prefix="tab4_auto_dl", show_header=True)


render_custom_analyzer_page()
