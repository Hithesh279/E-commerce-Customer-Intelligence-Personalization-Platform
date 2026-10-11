"""
src/analytics/report_generator.py
Automated report generation service for user-uploaded datasets.
Produces print-ready Executive HTML/PDF reports, multi-sheet Excel analytical workbooks,
and structured Markdown briefings.
"""
from datetime import datetime
import io
from typing import Any, Dict, Optional
import pandas as pd


def generate_executive_html_report(
    df: pd.DataFrame,
    data_source_label: str,
    schema_info: Dict[str, Any],
    txn_data: Dict[str, Any],
    reviews_data: Optional[Dict[str, Any]] = None,
    rfm_metrics: Optional[Dict[str, Any]] = None,
    rfm_df: Optional[pd.DataFrame] = None,
) -> str:
    """
    Generate a polished, self-contained, print-ready HTML executive report.
    Includes print media styling so users can export directly to PDF via browser print (Ctrl+P).
    """
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M")
    total_records = len(df)
    modalities = schema_info.get("modalities", {})

    # Generate Commercial Section
    commercial_html = ""
    if txn_data.get("total_revenue", 0) > 0 or txn_data.get("total_orders", 0) > 0:
        commercial_html = f"""
        <div class="section">
            <h3>📈 Commercial Health & Sales Analytics</h3>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total Revenue</div>
                    <div class="kpi-val">${txn_data.get('total_revenue', 0):,.2f}</div>
                    <div class="kpi-sub">Net Transaction Total</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Total Orders</div>
                    <div class="kpi-val">{txn_data.get('total_orders', 0):,}</div>
                    <div class="kpi-sub">Processed Volume</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Average Order Value</div>
                    <div class="kpi-val">${txn_data.get('aov', 0):.2f}</div>
                    <div class="kpi-sub">Spend Per Basket</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Exception / Return Rate</div>
                    <div class="kpi-val">{txn_data.get('return_rate', 0):.1f}%</div>
                    <div class="kpi-sub">Return / Churn Share</div>
                </div>
            </div>
        """
        # Category breakdown table if available
        cat_df = txn_data.get("category_df", pd.DataFrame())
        if not cat_df.empty:
            rows_html = "".join([
                f"<tr><td>{row.get(cat_df.columns[0], '')}</td><td>${row.get('revenue', 0):,.2f}</td><td>{row.get('share_pct', 0):.1f}%</td><td>{row.get('orders', 0):,}</td></tr>"
                for _, row in cat_df.head(6).iterrows()
            ])
            commercial_html += f"""
            <h4>Category Revenue Distribution</h4>
            <table>
                <thead>
                    <tr><th>Category / Vertical</th><th>Revenue ($)</th><th>Share (%)</th><th>Order Volume</th></tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """
        commercial_html += "</div>"

    # Generate NLP Sentiment Section
    nlp_html = ""
    if reviews_data is not None:
        nlp_html = f"""
        <div class="section">
            <h3>🧠 Voice of Customer & NLP Aspect Sentiment</h3>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total Reviews Analyzed</div>
                    <div class="kpi-val">{reviews_data.get('total_reviews', 0):,}</div>
                    <div class="kpi-sub">Batch Classified</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Positive Sentiment</div>
                    <div class="kpi-val" style="color: #16a34a;">{reviews_data.get('positive_pct', 0):.1f}%</div>
                    <div class="kpi-sub">Brand Advocates</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Negative Sentiment</div>
                    <div class="kpi-val" style="color: #dc2626;">{reviews_data.get('negative_pct', 0):.1f}%</div>
                    <div class="kpi-sub">Dissatisfied Friction</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Polarity Score</div>
                    <div class="kpi-val">{reviews_data.get('avg_polarity', 0):+.2f}</div>
                    <div class="kpi-sub">Scale: -1.0 to +1.0</div>
                </div>
            </div>
        """
        aspect_df = reviews_data.get("aspect_summary", pd.DataFrame())
        if not aspect_df.empty:
            a_rows = "".join([
                f"<tr><td><strong>{row['aspect']}</strong></td><td>{row['mentions']}</td><td style='color: {'#16a34a' if row['avg_sentiment_score'] > 0 else '#dc2626'}; font-weight:600;'>{row['avg_sentiment_score']:+.2f}</td><td>{row['positive_mentions']}</td><td>{row['negative_mentions']}</td></tr>"
                for _, row in aspect_df.head(8).iterrows()
            ])
            nlp_html += f"""
            <h4>11-Aspect Satisfaction Scorecard</h4>
            <table>
                <thead>
                    <tr><th>Product Aspect</th><th>Mentions</th><th>Polarity (-1 to +1)</th><th>Positive</th><th>Negative</th></tr>
                </thead>
                <tbody>{a_rows}</tbody>
            </table>
            """
        nlp_html += "</div>"

    # Generate RFM Section
    rfm_html = ""
    if rfm_metrics is not None and rfm_df is not None:
        seg_summary = rfm_metrics.get("segment_summary", pd.DataFrame())
        seg_rows = "".join([
            f"<tr><td><strong>{row['segment']}</strong></td><td>{row['count']:,}</td><td>{row.get('share_pct', 0):.1f}%</td></tr>"
            for _, row in seg_summary.iterrows()
        ])
        rfm_html = f"""
        <div class="section">
            <h3>👥 Customer Behavioral & RFM Segmentation</h3>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total Customers</div>
                    <div class="kpi-val">{rfm_metrics.get('total_customers', 0):,}</div>
                    <div class="kpi-sub">Audience Size</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Champions Count</div>
                    <div class="kpi-val" style="color: #16a34a;">{rfm_metrics.get('champions_count', 0):,}</div>
                    <div class="kpi-sub">High-Value Loyals</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">At-Risk Count</div>
                    <div class="kpi-val" style="color: #dc2626;">{rfm_metrics.get('at_risk_count', 0):,}</div>
                    <div class="kpi-sub">Retention Focus</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Avg Customer Spend</div>
                    <div class="kpi-val">${rfm_metrics.get('avg_monetary', 0):,.2f}</div>
                    <div class="kpi-sub">Lifetime Monetary</div>
                </div>
            </div>
            <h4>Behavioral Cluster Breakdown</h4>
            <table>
                <thead>
                    <tr><th>RFM Segment</th><th>Customer Count</th><th>Audience Share</th></tr>
                </thead>
                <tbody>{seg_rows}</tbody>
            </table>
        </div>
        """

    # Executive Recommendations
    recs_list = []
    if reviews_data and reviews_data.get("negative_pct", 0) > 20:
        recs_list.append("🔴 <strong>Address Feedback Friction:</strong> Negative reviews exceed 20%. Prioritize resolving the lowest-scoring aspects in customer service and product quality.")
    if rfm_metrics and rfm_metrics.get("at_risk_count", 0) > 0:
        recs_list.append(f"⚠️ <strong>Win-Back Campaign:</strong> Launch automated email re-engagement for the {rfm_metrics.get('at_risk_count'):,} At-Risk customer accounts before churn occurs.")
    if txn_data.get("return_rate", 0) > 8:
        recs_list.append("📦 <strong>Audit Return Logistics:</strong> Exception rate is above benchmark (8%). Inspect defective SKUs and update product descriptions to mitigate mismatches.")
    if not recs_list:
        recs_list.append("🟢 <strong>Sustain Momentum:</strong> High satisfaction and healthy commercial conversion observed. Expand loyalty rewards for Champions.")

    recs_html = "".join([f"<li>{r}</li>" for r in recs_list])

    # Complete HTML Template with Modern Enterprise Print Styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Intelligence Brief - {data_source_label}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            background-color: #f8fafc;
            margin: 0;
            padding: 30px;
            line-height: 1.5;
        }}
        .report-container {{
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .header {{
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .header h1 {{
            margin: 0 0 6px 0;
            font-size: 26px;
            color: #0f172a;
        }}
        .header .meta {{
            color: #64748b;
            font-size: 14px;
        }}
        .badge {{
            display: inline-block;
            background: #eff6ff;
            color: #2563eb;
            font-weight: 600;
            font-size: 12px;
            padding: 3px 10px;
            border-radius: 20px;
            margin-top: 8px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h3 {{
            color: #0f172a;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 8px;
            margin-bottom: 16px;
            font-size: 18px;
        }}
        .section h4 {{
            color: #334155;
            margin: 20px 0 10px 0;
            font-size: 15px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            border-radius: 6px;
            padding: 14px;
        }}
        .kpi-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #64748b;
            letter-spacing: 0.05em;
        }}
        .kpi-val {{
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            margin: 4px 0;
        }}
        .kpi-sub {{
            font-size: 12px;
            color: #64748b;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-bottom: 16px;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: #f1f5f9;
            color: #475569;
            font-weight: 600;
        }}
        ul.recs {{
            background: #f8fafc;
            border-left: 4px solid #10b981;
            padding: 16px 20px 16px 36px;
            border-radius: 4px;
            margin: 0;
        }}
        ul.recs li {{
            margin-bottom: 8px;
            font-size: 14px;
            color: #334155;
        }}
        .footer {{
            border-top: 1px solid #e2e8f0;
            margin-top: 40px;
            padding-top: 16px;
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
        }}
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .report-container {{
                box-shadow: none;
                border: none;
                padding: 0;
            }}
            @page {{
                margin: 1.5cm;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>📊 Executive Intelligence & Analytics Brief</h1>
            <div class="meta">
                <strong>Source:</strong> {data_source_label} | 
                <strong>Generated:</strong> {now_str} | 
                <strong>Dataset Scope:</strong> {total_records:,} records
            </div>
            <div class="badge">E-Commerce Customer Intelligence & Personalization Platform</div>
        </div>

        {commercial_html}
        {nlp_html}
        {rfm_html}

        <div class="section">
            <h3>🎯 Strategic Recommendations & Next Steps</h3>
            <ul class="recs">
                {recs_html}
            </ul>
        </div>

        <div class="footer">
            Generated autonomously by E-Commerce Customer Intelligence & Personalization Platform • Automated Star-Schema & NLP Engine
        </div>
    </div>
</body>
</html>"""

    return html_content


def generate_excel_analytical_workbook(
    enriched_df: pd.DataFrame,
    data_source_label: str,
    txn_data: Dict[str, Any],
    reviews_data: Optional[Dict[str, Any]] = None,
    rfm_df: Optional[pd.DataFrame] = None,
    rfm_metrics: Optional[Dict[str, Any]] = None,
) -> bytes:
    """
    Generate an enterprise multi-tab Excel workbook (.xlsx) with styled sheets:
    - Sheet 1: Executive Summary & KPIs
    - Sheet 2: Enriched Dataset (ML Predictions & Aspect Tags)
    - Sheet 3: Commercial Trends (if available)
    - Sheet 4: Aspect Sentiment Scorecard (if available)
    - Sheet 5: RFM Behavioral Clusters (if available)
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Sheet 1: Executive Summary
        kpi_rows = [
            {"Metric": "Dataset Source", "Value": str(data_source_label)},
            {"Metric": "Total Records Analyzed", "Value": len(enriched_df)},
            {"Metric": "Total Columns", "Value": len(enriched_df.columns)},
            {"Metric": "Generated Timestamp", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        ]
        if txn_data.get("total_revenue", 0) > 0:
            kpi_rows.extend([
                {"Metric": "Total Net Revenue ($)", "Value": f"${txn_data.get('total_revenue', 0):,.2f}"},
                {"Metric": "Total Orders", "Value": f"{txn_data.get('total_orders', 0):,}"},
                {"Metric": "Average Order Value ($)", "Value": f"${txn_data.get('aov', 0):.2f}"},
                {"Metric": "Exception / Return Rate (%)", "Value": f"{txn_data.get('return_rate', 0):.1f}%"},
            ])
        if reviews_data is not None:
            kpi_rows.extend([
                {"Metric": "Positive Sentiment Share (%)", "Value": f"{reviews_data.get('positive_pct', 0):.1f}%"},
                {"Metric": "Negative Sentiment Share (%)", "Value": f"{reviews_data.get('negative_pct', 0):.1f}%"},
                {"Metric": "Mean Polarity Index (-1 to +1)", "Value": f"{reviews_data.get('avg_polarity', 0):+.2f}"},
            ])
        if rfm_metrics is not None:
            kpi_rows.extend([
                {"Metric": "Total Unique Customers", "Value": f"{rfm_metrics.get('total_customers', 0):,}"},
                {"Metric": "High-Value Champions", "Value": f"{rfm_metrics.get('champions_count', 0):,}"},
                {"Metric": "At-Risk Customers", "Value": f"{rfm_metrics.get('at_risk_count', 0):,}"},
            ])

        summary_df = pd.DataFrame(kpi_rows)
        summary_df.to_excel(writer, sheet_name="Executive_Summary", index=False)

        # Sheet 2: Enriched Dataset (truncated to 50,000 for Excel safety)
        enriched_df.head(50000).to_excel(writer, sheet_name="Enriched_Dataset", index=False)

        # Sheet 3: Commercial Trends & Categories
        if not txn_data.get("timeline_df", pd.DataFrame()).empty:
            txn_data["timeline_df"].to_excel(writer, sheet_name="Monthly_Revenue_Trends", index=False)
        if not txn_data.get("category_df", pd.DataFrame()).empty:
            txn_data["category_df"].to_excel(writer, sheet_name="Category_Sales", index=False)
        if not txn_data.get("top_products_df", pd.DataFrame()).empty:
            txn_data["top_products_df"].to_excel(writer, sheet_name="Top_Products", index=False)

        # Sheet 4: Aspect Sentiment Scorecard
        if reviews_data is not None and not reviews_data.get("aspect_summary", pd.DataFrame()).empty:
            reviews_data["aspect_summary"].to_excel(writer, sheet_name="Aspect_Sentiment", index=False)

        # Sheet 5: RFM Clusters
        if rfm_df is not None:
            rfm_df.head(25000).to_excel(writer, sheet_name="RFM_Customer_Segments", index=False)
        if rfm_metrics is not None and not rfm_metrics.get("segment_summary", pd.DataFrame()).empty:
            rfm_metrics["segment_summary"].to_excel(writer, sheet_name="RFM_Segment_Totals", index=False)

    return output.getvalue()


def generate_markdown_report(
    df: pd.DataFrame,
    data_source_label: str,
    txn_data: Dict[str, Any],
    reviews_data: Optional[Dict[str, Any]] = None,
    rfm_metrics: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate structured markdown briefing."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = [
        f"# Executive Analytics Briefing",
        f"**Source:** {data_source_label}  ",
        f"**Generated:** {now_str}  ",
        f"**Dataset Rows:** {len(df):,}  ",
        f"\n---\n",
    ]

    if txn_data.get("total_revenue", 0) > 0 or txn_data.get("total_orders", 0) > 0:
        md.append("## 📈 Commercial Health KPIs\n")
        md.append(f"- **Total Revenue:** ${txn_data.get('total_revenue', 0):,.2f}")
        md.append(f"- **Total Orders:** {txn_data.get('total_orders', 0):,}")
        md.append(f"- **Average Order Value (AOV):** ${txn_data.get('aov', 0):.2f}")
        md.append(f"- **Exception Rate:** {txn_data.get('return_rate', 0):.1f}%\n")

    if reviews_data is not None:
        md.append("## 🧠 NLP Sentiment & Aspect Intelligence\n")
        md.append(f"- **Total Reviews:** {reviews_data.get('total_reviews', 0):,}")
        md.append(f"- **Positive Sentiment:** {reviews_data.get('positive_pct', 0):.1f}%")
        md.append(f"- **Negative Sentiment:** {reviews_data.get('negative_pct', 0):.1f}%")
        md.append(f"- **Polarity Index:** {reviews_data.get('avg_polarity', 0):+.2f}\n")

    if rfm_metrics is not None:
        md.append("## 👥 Customer RFM Behavioral Segmentation\n")
        md.append(f"- **Total Customers:** {rfm_metrics.get('total_customers', 0):,}")
        md.append(f"- **Champions (VIP):** {rfm_metrics.get('champions_count', 0):,}")
        md.append(f"- **At-Risk Accounts:** {rfm_metrics.get('at_risk_count', 0):,}")
        md.append(f"- **Average Customer Spend:** ${rfm_metrics.get('avg_monetary', 0):,.2f}\n")

    return "\n".join(md)
