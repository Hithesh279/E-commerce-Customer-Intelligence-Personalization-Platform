"""
src/analytics/report_generator.py
Automated report generation for user-uploaded datasets: a printable HTML executive brief,
a multi-sheet Excel workbook and a Markdown briefing.

Safety rules applied throughout:
  * Every value that originated in the uploaded file is HTML-escaped before it reaches the page.
  * A metric the dataset cannot support is written as "N/A", never as a guessed number.
  * Cells are stripped of characters that Excel rejects.
"""
import html
import io
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from src.utils.formatting import NA_TEXT, fmt_money, fmt_num, fmt_pct, fmt_rating, fmt_signed, is_missing

_EXPORT_BUILDER_CALL_COUNTS = {
    "html": 0,
    "excel": 0,
    "markdown": 0,
    "total": 0,
}


def get_export_builder_call_counts() -> Dict[str, int]:
    """Return dictionary of call counts for export builders."""
    return dict(_EXPORT_BUILDER_CALL_COUNTS)


def reset_export_builder_call_counts() -> None:
    """Reset call counts for export builders to zero."""
    global _EXPORT_BUILDER_CALL_COUNTS
    _EXPORT_BUILDER_CALL_COUNTS = {
        "html": 0,
        "excel": 0,
        "markdown": 0,
        "total": 0,
    }


def _e(value: Any) -> str:
    """Escape any value for safe inclusion in HTML."""
    return "" if is_missing(value) else html.escape(str(value))


def _excel_safe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy whose text cells contain no characters that openpyxl refuses to write."""
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].map(lambda v: ILLEGAL_CHARACTERS_RE.sub("", v) if isinstance(v, str) else v)
    return out


def _recommendations(reviews_data, txn_data, rfm_metrics) -> List[str]:
    """Recommendations driven only by metrics that are present and breach a stated threshold."""
    items: List[str] = []
    neg_pct = reviews_data.get("negative_pct") if reviews_data else None
    if neg_pct is not None and neg_pct > 20:
        items.append("🔴 <strong>Address Feedback Friction:</strong> Negative reviews exceed 20%. "
                     "Prioritize the lowest-scoring aspects in product quality and customer service.")
    at_risk = rfm_metrics.get("at_risk_count") if rfm_metrics else None
    if at_risk:
        items.append(f"⚠️ <strong>Win-Back Campaign:</strong> Launch re-engagement for the {fmt_num(at_risk)} "
                     "At-Risk customer accounts before churn occurs.")
    return_rate = txn_data.get("return_rate")
    if return_rate is not None and return_rate > 8:
        items.append("📦 <strong>Audit Return Logistics:</strong> The return rate is above the 8% benchmark. "
                     "Inspect defective SKUs and check product descriptions for mismatches.")
    if not items:
        measured = any(v is not None for v in (neg_pct, return_rate, at_risk))
        if measured:
            items.append("🟢 <strong>No threshold breached:</strong> The metrics available in this dataset are "
                         "within the stated thresholds (negative reviews ≤ 20%, return rate ≤ 8%, no At-Risk accounts).")
        else:
            items.append("ℹ️ <strong>Add more data:</strong> Revenue, ratings, return status or customer history "
                         "are needed before recommendations can be generated.")
    return items


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
    Generate a self-contained, print-ready HTML executive report.
    Use the browser's print dialog (Ctrl+P) to save it as PDF.
    """
    global _EXPORT_BUILDER_CALL_COUNTS
    _EXPORT_BUILDER_CALL_COUNTS["html"] += 1
    _EXPORT_BUILDER_CALL_COUNTS["total"] += 1
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M")
    total_records = len(df)
    source = _e(data_source_label)

    commercial_html = ""
    if txn_data.get("total_revenue") is not None:
        cat_df = txn_data.get("category_df", pd.DataFrame())
        commercial_html = f"""
        <div class="section">
            <h3>📈 Commercial Health & Sales Analytics</h3>
            <div class="kpi-grid">
                <div class="kpi-card"><div class="kpi-title">Total Revenue</div>
                    <div class="kpi-val">{fmt_money(txn_data.get('total_revenue'))}</div>
                    <div class="kpi-sub">Transaction total</div></div>
                <div class="kpi-card"><div class="kpi-title">Total Orders</div>
                    <div class="kpi-val">{fmt_num(txn_data.get('total_orders'))}</div>
                    <div class="kpi-sub">Rows with a revenue value</div></div>
                <div class="kpi-card"><div class="kpi-title">Average Order Value</div>
                    <div class="kpi-val">{fmt_money(txn_data.get('aov'))}</div>
                    <div class="kpi-sub">Revenue per order</div></div>
                <div class="kpi-card"><div class="kpi-title">Return / Churn Rate</div>
                    <div class="kpi-val">{fmt_pct(txn_data.get('return_rate'))}</div>
                    <div class="kpi-sub">Share of returned or churned rows</div></div>
            </div>
        """
        if not cat_df.empty:
            cat_col = cat_df.columns[0]
            rows_html = "".join(
                f"<tr><td>{_e(row[cat_col])}</td><td>{fmt_money(row.get('revenue'))}</td>"
                f"<td>{fmt_pct(row.get('share_pct'))}</td><td>{fmt_num(row.get('orders'))}</td></tr>"
                for _, row in cat_df.head(6).iterrows()
            )
            commercial_html += f"""
            <h4>Category Revenue Distribution</h4>
            <table>
                <thead><tr><th>Category / Vertical</th><th>Revenue ($)</th><th>Share (%)</th><th>Order Volume</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            """
        commercial_html += "</div>"

    nlp_html = ""
    if reviews_data is not None:
        nlp_html = f"""
        <div class="section">
            <h3>🧠 Voice of Customer & NLP Aspect Sentiment</h3>
            <div class="kpi-grid">
                <div class="kpi-card"><div class="kpi-title">Total Reviews Analyzed</div>
                    <div class="kpi-val">{fmt_num(reviews_data.get('total_reviews'))}</div>
                    <div class="kpi-sub">{fmt_num(reviews_data.get('labeled_reviews'))} with a sentiment label</div></div>
                <div class="kpi-card"><div class="kpi-title">Positive Sentiment</div>
                    <div class="kpi-val" style="color: #16a34a;">{fmt_pct(reviews_data.get('positive_pct'))}</div>
                    <div class="kpi-sub">Share of labelled reviews</div></div>
                <div class="kpi-card"><div class="kpi-title">Negative Sentiment</div>
                    <div class="kpi-val" style="color: #dc2626;">{fmt_pct(reviews_data.get('negative_pct'))}</div>
                    <div class="kpi-sub">Share of labelled reviews</div></div>
                <div class="kpi-card"><div class="kpi-title">Polarity Score</div>
                    <div class="kpi-val">{fmt_signed(reviews_data.get('avg_polarity'))}</div>
                    <div class="kpi-sub">Scale: -1.0 to +1.0</div></div>
            </div>
        """
        aspect_df = reviews_data.get("aspect_summary", pd.DataFrame())
        if not aspect_df.empty:
            a_rows = []
            for _, row in aspect_df.head(8).iterrows():
                score = row.get("avg_sentiment_score")
                color = "#64748b" if is_missing(score) else ("#16a34a" if score > 0 else "#dc2626")
                a_rows.append(
                    f"<tr><td><strong>{_e(row['aspect'])}</strong></td><td>{fmt_num(row.get('mentions'))}</td>"
                    f"<td style='color: {color}; font-weight:600;'>{fmt_signed(score)}</td>"
                    f"<td>{fmt_num(row.get('positive_mentions'))}</td><td>{fmt_num(row.get('negative_mentions'))}</td></tr>"
                )
            nlp_html += f"""
            <h4>Aspect Satisfaction Scorecard</h4>
            <table>
                <thead><tr><th>Product Aspect</th><th>Mentions</th><th>Polarity (-1 to +1)</th><th>Positive</th><th>Negative</th></tr></thead>
                <tbody>{''.join(a_rows)}</tbody>
            </table>
            """
        nlp_html += "</div>"

    rfm_html = ""
    if rfm_metrics is not None and rfm_df is not None:
        seg_summary = rfm_metrics.get("segment_summary", pd.DataFrame())
        seg_rows = "".join(
            f"<tr><td><strong>{_e(row['segment'])}</strong></td><td>{fmt_num(row['count'])}</td>"
            f"<td>{fmt_pct(row.get('share_pct'))}</td></tr>"
            for _, row in seg_summary.iterrows()
        )
        rec_avail = bool(rfm_metrics.get("recency_available", True))
        champ_sub = "High-value VIP accounts" if rec_avail else "Needs recency data"
        risk_sub = "Retention priority accounts" if rec_avail else "Needs recency data"
        rfm_html = f"""
        <div class="section">
            <h3>👥 Customer Behavioral & RFM Segmentation</h3>
            <div class="kpi-grid">
                <div class="kpi-card"><div class="kpi-title">Total Customers</div>
                    <div class="kpi-val">{fmt_num(rfm_metrics.get('total_customers'))}</div>
                    <div class="kpi-sub">Audience size</div></div>
                <div class="kpi-card"><div class="kpi-title">Champions Count</div>
                    <div class="kpi-val" style="color: #16a34a;">{fmt_num(rfm_metrics.get('champions_count'))}</div>
                    <div class="kpi-sub">{champ_sub}</div></div>
                <div class="kpi-card"><div class="kpi-title">At-Risk Count</div>
                    <div class="kpi-val" style="color: #dc2626;">{fmt_num(rfm_metrics.get('at_risk_count'))}</div>
                    <div class="kpi-sub">{risk_sub}</div></div>
                <div class="kpi-card"><div class="kpi-title">Avg Customer Spend</div>
                    <div class="kpi-val">{fmt_money(rfm_metrics.get('avg_monetary'))}</div>
                    <div class="kpi-sub">Monetary value</div></div>
            </div>
            <h4>Behavioral Cluster Breakdown</h4>
            <table>
                <thead><tr><th>RFM Segment</th><th>Customer Count</th><th>Audience Share</th></tr></thead>
                <tbody>{seg_rows}</tbody>
            </table>
        </div>
        """

    recs_html = "".join(f"<li>{r}</li>" for r in _recommendations(reviews_data, txn_data, rfm_metrics))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Intelligence Brief - {source}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b; background-color: #f8fafc; margin: 0; padding: 30px; line-height: 1.5; }}
        .report-container {{ max-width: 960px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0;
            border-radius: 10px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
        .header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 20px; margin-bottom: 25px; }}
        .header h1 {{ margin: 0 0 6px 0; font-size: 26px; color: #0f172a; }}
        .header .meta {{ color: #64748b; font-size: 14px; }}
        .badge {{ display: inline-block; background: #eff6ff; color: #2563eb; font-weight: 600; font-size: 12px;
            padding: 3px 10px; border-radius: 20px; margin-top: 8px; }}
        .section {{ margin-bottom: 30px; }}
        .section h3 {{ color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 16px; font-size: 18px; }}
        .section h4 {{ color: #334155; margin: 20px 0 10px 0; font-size: 15px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 20px; }}
        .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; border-radius: 6px; padding: 14px; }}
        .kpi-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em; }}
        .kpi-val {{ font-size: 24px; font-weight: 800; color: #0f172a; margin: 4px 0; }}
        .kpi-sub {{ font-size: 12px; color: #64748b; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 16px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; color: #475569; font-weight: 600; }}
        ul.recs {{ background: #f8fafc; border-left: 4px solid #10b981; padding: 16px 20px 16px 36px; border-radius: 4px; margin: 0; }}
        ul.recs li {{ margin-bottom: 8px; font-size: 14px; color: #334155; }}
        .footer {{ border-top: 1px solid #e2e8f0; margin-top: 40px; padding-top: 16px; text-align: center; font-size: 12px; color: #94a3b8; }}
        @media print {{
            body {{ background: #ffffff; padding: 0; }}
            .report-container {{ box-shadow: none; border: none; padding: 0; }}
            .no-print {{ display: none !important; }}
            @page {{ margin: 1.5cm; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <div class="no-print" style="float: right;">
                <button onclick="window.print()" style="background: #2563eb; color: #ffffff; border: none; padding: 9px 18px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">🖨️ Save as PDF / Print</button>
            </div>
            <h1>📊 Executive Intelligence & Analytics Brief</h1>
            <div class="meta"><strong>Source:</strong> {source} |
                <strong>Generated:</strong> {now_str} |
                <strong>Dataset Scope:</strong> {total_records:,} records</div>
            <div class="badge">E-Commerce Customer Intelligence & Personalization Platform</div>
        </div>
        {commercial_html}
        {nlp_html}
        {rfm_html}
        <div class="section">
            <h3>🎯 Strategic Recommendations & Next Steps</h3>
            <ul class="recs">{recs_html}</ul>
        </div>
        <div class="footer">Generated by the E-Commerce Customer Intelligence & Personalization Platform</div>
    </div>
</body>
</html>"""


def generate_excel_analytical_workbook(
    enriched_df: pd.DataFrame,
    data_source_label: str,
    txn_data: Dict[str, Any],
    reviews_data: Optional[Dict[str, Any]] = None,
    rfm_df: Optional[pd.DataFrame] = None,
    rfm_metrics: Optional[Dict[str, Any]] = None,
) -> bytes:
    """
    Generate a multi-sheet Excel workbook (.xlsx). Sheets are added only when they have data:
    Executive_Summary, Enriched_Dataset, Monthly_Revenue_Trends, Category_Sales, Top_Products,
    Aspect_Sentiment, RFM_Customer_Segments, RFM_Segment_Totals.
    """
    global _EXPORT_BUILDER_CALL_COUNTS
    _EXPORT_BUILDER_CALL_COUNTS["excel"] += 1
    _EXPORT_BUILDER_CALL_COUNTS["total"] += 1
    output = io.BytesIO()
    kpi_rows = [
        {"Metric": "Dataset Source", "Value": str(data_source_label)},
        {"Metric": "Total Records Analyzed", "Value": len(enriched_df)},
        {"Metric": "Total Columns", "Value": len(enriched_df.columns)},
        {"Metric": "Generated Timestamp", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    ]
    if txn_data.get("total_revenue") is not None:
        kpi_rows.extend([
            {"Metric": "Total Revenue ($)", "Value": fmt_money(txn_data.get("total_revenue"))},
            {"Metric": "Total Orders", "Value": fmt_num(txn_data.get("total_orders"))},
            {"Metric": "Average Order Value ($)", "Value": fmt_money(txn_data.get("aov"))},
            {"Metric": "Return / Churn Rate (%)", "Value": fmt_pct(txn_data.get("return_rate"))},
        ])
    if reviews_data is not None:
        kpi_rows.extend([
            {"Metric": "Positive Sentiment Share (%)", "Value": fmt_pct(reviews_data.get("positive_pct"))},
            {"Metric": "Negative Sentiment Share (%)", "Value": fmt_pct(reviews_data.get("negative_pct"))},
            {"Metric": "Mean Polarity Index (-1 to +1)", "Value": fmt_signed(reviews_data.get("avg_polarity"))},
            {"Metric": "Average Star Rating", "Value": fmt_rating(reviews_data.get("avg_rating"))},
        ])
    if rfm_metrics is not None:
        kpi_rows.extend([
            {"Metric": "Total Unique Customers", "Value": fmt_num(rfm_metrics.get("total_customers"))},
            {"Metric": "High-Value Champions", "Value": fmt_num(rfm_metrics.get("champions_count")) if rfm_metrics.get("recency_available", True) else NA_TEXT},
            {"Metric": "At-Risk Customers", "Value": fmt_num(rfm_metrics.get("at_risk_count")) if rfm_metrics.get("recency_available", True) else NA_TEXT},
        ])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(kpi_rows).to_excel(writer, sheet_name="Executive_Summary", index=False)
        _excel_safe(enriched_df.head(2500)).to_excel(writer, sheet_name="Enriched_Dataset", index=False)

        for key, sheet in [("timeline_df", "Monthly_Revenue_Trends"), ("category_df", "Category_Sales"),
                           ("top_products_df", "Top_Products")]:
            table = txn_data.get(key, pd.DataFrame())
            if isinstance(table, pd.DataFrame) and not table.empty:
                _excel_safe(table).to_excel(writer, sheet_name=sheet, index=False)

        if reviews_data is not None and not reviews_data.get("aspect_summary", pd.DataFrame()).empty:
            _excel_safe(reviews_data["aspect_summary"]).to_excel(writer, sheet_name="Aspect_Sentiment", index=False)

        if rfm_df is not None:
            _excel_safe(rfm_df.head(2500)).to_excel(writer, sheet_name="RFM_Customer_Segments", index=False)
        if rfm_metrics is not None and not rfm_metrics.get("segment_summary", pd.DataFrame()).empty:
            _excel_safe(rfm_metrics["segment_summary"]).to_excel(writer, sheet_name="RFM_Segment_Totals", index=False)

    return output.getvalue()


def generate_markdown_report(
    df: pd.DataFrame,
    data_source_label: str,
    txn_data: Dict[str, Any],
    reviews_data: Optional[Dict[str, Any]] = None,
    rfm_metrics: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a structured Markdown briefing. Unavailable metrics are written as N/A."""
    global _EXPORT_BUILDER_CALL_COUNTS
    _EXPORT_BUILDER_CALL_COUNTS["markdown"] += 1
    _EXPORT_BUILDER_CALL_COUNTS["total"] += 1
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = [
        "# Executive Analytics Briefing",
        f"**Source:** {data_source_label}  ",
        f"**Generated:** {now_str}  ",
        f"**Dataset Rows:** {len(df):,}  ",
        "\n---\n",
    ]
    if txn_data.get("total_revenue") is not None:
        md.append("## 📈 Commercial Health KPIs\n")
        md.append(f"- **Total Revenue:** {fmt_money(txn_data.get('total_revenue'))}")
        md.append(f"- **Total Orders:** {fmt_num(txn_data.get('total_orders'))}")
        md.append(f"- **Average Order Value (AOV):** {fmt_money(txn_data.get('aov'))}")
        md.append(f"- **Return / Churn Rate:** {fmt_pct(txn_data.get('return_rate'))}\n")

        cat_df = txn_data.get("category_df", pd.DataFrame())
        if isinstance(cat_df, pd.DataFrame) and not cat_df.empty:
            cat_col = cat_df.columns[0]
            md.append("### Category Revenue Distribution\n")
            md.append("| Category / Vertical | Revenue ($) | Share (%) | Order Volume |")
            md.append("|:---|---:|---:|---:|")
            for _, row in cat_df.head(6).iterrows():
                md.append(
                    f"| {row[cat_col]} | {fmt_money(row.get('revenue'))} | "
                    f"{fmt_pct(row.get('share_pct'))} | {fmt_num(row.get('orders'))} |"
                )
            md.append("")

    if reviews_data is not None:
        md.append("## 🧠 NLP Sentiment & Aspect Intelligence\n")
        md.append(f"- **Total Reviews:** {fmt_num(reviews_data.get('total_reviews'))}")
        md.append(f"- **Positive Sentiment:** {fmt_pct(reviews_data.get('positive_pct'))}")
        md.append(f"- **Negative Sentiment:** {fmt_pct(reviews_data.get('negative_pct'))}")
        md.append(f"- **Polarity Index:** {fmt_signed(reviews_data.get('avg_polarity'))}\n")

        aspect_df = reviews_data.get("aspect_summary", pd.DataFrame())
        if isinstance(aspect_df, pd.DataFrame) and not aspect_df.empty:
            md.append("### Aspect Satisfaction Scorecard\n")
            md.append("| Product Aspect | Mentions | Polarity (-1 to +1) | Positive | Negative |")
            md.append("|:---|---:|---:|---:|---:|")
            for _, row in aspect_df.head(8).iterrows():
                md.append(
                    f"| {row['aspect']} | {fmt_num(row.get('mentions'))} | "
                    f"{fmt_signed(row.get('avg_sentiment_score'))} | {fmt_num(row.get('positive_mentions'))} | "
                    f"{fmt_num(row.get('negative_mentions'))} |"
                )
            md.append("")

    if rfm_metrics is not None:
        md.append("## 👥 Customer RFM Behavioral Segmentation\n")
        md.append(f"- **Total Customers:** {fmt_num(rfm_metrics.get('total_customers'))}")
        md.append(f"- **Champions (VIP):** {fmt_num(rfm_metrics.get('champions_count'))}")
        md.append(f"- **At-Risk Accounts:** {fmt_num(rfm_metrics.get('at_risk_count'))}")
        md.append(f"- **Average Customer Spend:** {fmt_money(rfm_metrics.get('avg_monetary'))}\n")

        seg_summary = rfm_metrics.get("segment_summary", pd.DataFrame())
        if isinstance(seg_summary, pd.DataFrame) and not seg_summary.empty:
            md.append("### Behavioral Cluster Breakdown\n")
            md.append("| RFM Segment | Customer Count | Audience Share |")
            md.append("|:---|---:|---:|")
            for _, row in seg_summary.iterrows():
                md.append(f"| {row['segment']} | {fmt_num(row['count'])} | {fmt_pct(row.get('share_pct'))} |")
            md.append("")

    recs = _recommendations(reviews_data, txn_data, rfm_metrics)
    if recs:
        md.append("## 🎯 Strategic Recommendations\n")
        for r in recs:
            clean_r = re.sub(r"</?strong>", "**", r)
            md.append(f"- {clean_r}")
        md.append("")

    return "\n".join(md)
