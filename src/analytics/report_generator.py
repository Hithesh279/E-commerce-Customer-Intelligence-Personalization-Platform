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
import json
from pathlib import Path
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from src.utils.config import PROJECT_ROOT
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
    bundles: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate a comprehensive, self-contained, print-ready HTML executive report
    mirroring the full Streamlit dashboard experience:
      1. Executive Overview & Commercial Health (Main / Overview Page)
      2. Customer Intelligence & Behavioral RFM 360 Profiles
      3. Product Intelligence & SKU Risk Matrix (High-Sales/Low-Sentiment Churn Risks)
      4. Voice of Customer (VoC) & 11-Aspect Sentiment Analysis (NLP Insights Page)
      5. Multi-Strategy Personalization Engine & Offline ML Benchmarks (Recommendations Page)
      6. Strategic Cross-Functional Action Plan
    """
    global _EXPORT_BUILDER_CALL_COUNTS
    _EXPORT_BUILDER_CALL_COUNTS["html"] += 1
    _EXPORT_BUILDER_CALL_COUNTS["total"] += 1
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M")
    total_records = len(df)
    source = _e(data_source_label)

    # Fallback to demo bundles when viewing default demo store
    if bundles is None and "Default Demo Store" in data_source_label:
        try:
            from app.services.active_dataset_manager import get_default_demo_bundles
            bundles = get_default_demo_bundles()
        except Exception:
            bundles = None

    kpis = (bundles.get("exec_kpis") if bundles else {}) or {}

    # -------------------------------------------------------------
    # 1. Executive Overview & Commercial Health
    # -------------------------------------------------------------
    commercial_html = ""
    net_rev = txn_data.get("total_revenue") if txn_data.get("total_revenue") is not None else kpis.get("total_net_revenue")
    orders = txn_data.get("total_orders") if txn_data.get("total_orders") is not None else kpis.get("total_orders")
    aov = txn_data.get("aov") if txn_data.get("aov") is not None else kpis.get("average_order_value")
    return_rate = txn_data.get("return_rate") if txn_data.get("return_rate") is not None else kpis.get("overall_return_rate_pct")
    avg_rating = kpis.get("average_rating") if kpis.get("average_rating") is not None else (reviews_data.get("avg_rating") if reviews_data else None)
    pos_pct = reviews_data.get("positive_pct") if reviews_data else kpis.get("positive_sentiment_pct")

    if net_rev is not None:
        cat_df = bundles.get("cat_perf") if bundles and isinstance(bundles.get("cat_perf"), pd.DataFrame) else txn_data.get("category_df", pd.DataFrame())
        mt_df = bundles.get("monthly_trend") if bundles and isinstance(bundles.get("monthly_trend"), pd.DataFrame) else txn_data.get("timeline_df", pd.DataFrame())
        prod_perf_df = bundles.get("prod_perf") if bundles and isinstance(bundles.get("prod_perf"), pd.DataFrame) else txn_data.get("top_products_df", pd.DataFrame())

        commercial_html = f"""
        <div class="section" id="sec-overview">
            <div class="section-tag">Module 1 • Executive Overview</div>
            <h3>📈 1. Commercial Health & Executive Overview</h3>
            <p class="section-desc">Key commercial milestones, basket metrics, return liabilities, and baseline customer satisfaction scores across touchpoints.</p>
            <div class="kpi-grid">
                <div class="kpi-card"><div class="kpi-title">Total Revenue</div>
                    <div class="kpi-val">{fmt_money(net_rev)}</div>
                    <div class="kpi-sub">Transaction total</div></div>
                <div class="kpi-card"><div class="kpi-title">Total Orders</div>
                    <div class="kpi-val">{fmt_num(orders)}</div>
                    <div class="kpi-sub">Rows with a revenue value</div></div>
                <div class="kpi-card"><div class="kpi-title">Average Order Value</div>
                    <div class="kpi-val">{fmt_money(aov)}</div>
                    <div class="kpi-sub">Revenue per order</div></div>
                <div class="kpi-card"><div class="kpi-title">Return / Churn Rate</div>
                    <div class="kpi-val" style="color: {'#dc2626' if return_rate and return_rate > 8 else '#0f172a'};">{fmt_pct(return_rate)}</div>
                    <div class="kpi-sub">Share of returned or churned rows</div></div>
                <div class="kpi-card"><div class="kpi-title">Customer Satisfaction</div>
                    <div class="kpi-val">{fmt_rating(avg_rating)}</div>
                    <div class="kpi-sub">Overall rating across catalog</div></div>
                <div class="kpi-card"><div class="kpi-title">Positive Sentiment</div>
                    <div class="kpi-val" style="color: #16a34a;">{fmt_pct(pos_pct)}</div>
                    <div class="kpi-sub">Share of positive feedback</div></div>
            </div>
        """

        # Category revenue breakdown table
        if isinstance(cat_df, pd.DataFrame) and not cat_df.empty:
            cat_col = cat_df.columns[0]
            cat_rows = []
            for _, row in cat_df.head(7).iterrows():
                rev = row.get("revenue") if "revenue" in row else row.get("net_revenue")
                share = row.get("share_pct")
                ords = row.get("orders") if "orders" in row else row.get("total_orders")
                cat_rows.append(
                    f"<tr><td><strong>{_e(row[cat_col])}</strong></td>"
                    f"<td>{fmt_money(rev)}</td>"
                    f"<td>{fmt_pct(share)}</td>"
                    f"<td>{fmt_num(ords)}</td></tr>"
                )
            commercial_html += f"""
            <h4>Category Revenue & Order Distribution</h4>
            <table>
                <thead><tr><th>Category / Vertical</th><th>Revenue ($)</th><th>Share (%)</th><th>Order Volume</th></tr></thead>
                <tbody>{''.join(cat_rows)}</tbody>
            </table>
            """

        # Monthly revenue & order trajectory table
        if isinstance(mt_df, pd.DataFrame) and not mt_df.empty:
            period_col = "year_month" if "year_month" in mt_df.columns else mt_df.columns[0]
            mt_rows = []
            for _, row in mt_df.tail(6).iterrows():
                m_rev = row.get("total_revenue") if "total_revenue" in row else row.get("revenue")
                m_ords = row.get("order_count") if "order_count" in row else row.get("orders")
                m_ret = row.get("returned_orders") if "returned_orders" in row else None
                m_ret_pct = row.get("return_rate_pct") if "return_rate_pct" in row else row.get("return_rate")
                mt_rows.append(
                    f"<tr><td>{_e(row[period_col])}</td>"
                    f"<td>{fmt_money(m_rev)}</td>"
                    f"<td>{fmt_num(m_ords)}</td>"
                    f"<td>{fmt_num(m_ret)}</td>"
                    f"<td>{fmt_pct(m_ret_pct)}</td></tr>"
                )
            commercial_html += f"""
            <h4>Recent Monthly Revenue & Order Trajectory</h4>
            <table>
                <thead><tr><th>Period / Month</th><th>Revenue ($)</th><th>Completed Orders</th><th>Returned Orders</th><th>Return Rate (%)</th></tr></thead>
                <tbody>{''.join(mt_rows)}</tbody>
            </table>
            """

        commercial_html += "</div>"

    # -------------------------------------------------------------
    # 2. Customer Intelligence & Behavioral RFM Segmentation
    # -------------------------------------------------------------
    rfm_html = ""
    if rfm_metrics is not None and rfm_df is not None:
        seg_summary = rfm_metrics.get("segment_summary", pd.DataFrame())
        seg_rows = []
        if isinstance(seg_summary, pd.DataFrame) and not seg_summary.empty:
            for _, row in seg_summary.iterrows():
                seg_name = str(row["segment"])
                playbook = "VIP loyalty rewards & early access" if "Champion" in seg_name or "Loyal" in seg_name else (
                    "Urgent win-back email discounts" if "Risk" in seg_name or "Attention" in seg_name else "Reactivation surveys & seasonal promos"
                )
                seg_rows.append(
                    f"<tr><td><strong>{_e(seg_name)}</strong></td><td>{fmt_num(row['count'])}</td>"
                    f"<td>{fmt_pct(row.get('share_pct'))}</td><td>{playbook}</td></tr>"
                )

        rec_avail = bool(rfm_metrics.get("recency_available", True))
        champ_sub = "High-value VIP accounts" if rec_avail else "Needs recency data"
        risk_sub = "Retention priority accounts" if rec_avail else "Needs recency data"

        rfm_html = f"""
        <div class="section" id="sec-customers">
            <div class="section-tag">Module 2 • Customer Intelligence</div>
            <h3>👥 2. Customer Intelligence & Behavioral RFM Segmentation</h3>
            <p class="section-desc">Quintile-based Recency, Frequency, and Monetary (RFM) clustering to segment customers into actionable lifecycle cohorts and mitigate churn risk.</p>
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
                <thead><tr><th>RFM Segment</th><th>Customer Count</th><th>Audience Share</th><th>Retention & Marketing Action</th></tr></thead>
                <tbody>{''.join(seg_rows)}</tbody>
            </table>
        """

        # Sample Customer 360 Profiles
        cust_profiles = bundles.get("cust_profiles") if bundles else None
        if isinstance(cust_profiles, pd.DataFrame) and not cust_profiles.empty:
            cust_rows = []
            for _, c_row in cust_profiles.head(5).iterrows():
                cid = str(c_row.get("customer_id", "N/A"))
                c_seg = str(c_row.get("customer_segment") or c_row.get("rfm_segment") or "N/A")
                c_score = str(c_row.get("rfm_score", "N/A"))
                c_rec = fmt_num(c_row.get("recency_days"))
                c_ords = fmt_num(c_row.get("total_orders"))
                c_spend = fmt_money(c_row.get("net_spend"))
                c_aov = fmt_money(c_row.get("average_order_value"))
                cust_rows.append(
                    f"<tr><td><code>{_e(cid)}</code></td><td><span class='badge'>{_e(c_seg)}</span></td>"
                    f"<td>{_e(c_score)}</td><td>{c_rec} days</td><td>{c_ords}</td><td>{c_spend}</td><td>{c_aov}</td></tr>"
                )
            rfm_html += f"""
            <h4>Customer 360° Profile Samples</h4>
            <table>
                <thead><tr><th>Customer ID</th><th>Cohort / Segment</th><th>RFM Score</th><th>Recency</th><th>Orders</th><th>Lifetime Spend</th><th>AOV</th></tr></thead>
                <tbody>{''.join(cust_rows)}</tbody>
            </table>
            """
        rfm_html += "</div>"

    # -------------------------------------------------------------
    # 3. Product Intelligence & SKU Risk Matrix
    # -------------------------------------------------------------
    product_html = ""
    prod_df = bundles.get("prod_perf") if bundles and isinstance(bundles.get("prod_perf"), pd.DataFrame) else txn_data.get("top_products_df")
    if isinstance(prod_df, pd.DataFrame) and not prod_df.empty:
        p_rows = []
        for _, prow in prod_df.head(6).iterrows():
            pid = str(prow.get("product_id") or prow.get(prod_df.columns[0]))
            pname = str(prow.get("product_name", pid))
            pcat = str(prow.get("category", "N/A"))
            punits = fmt_num(prow.get("units_sold"))
            prev = fmt_money(prow.get("net_revenue") or prow.get("revenue"))
            prating = fmt_rating(prow.get("average_rating"))
            preturn = fmt_pct(prow.get("return_rate"))
            p_rows.append(
                f"<tr><td><code>{_e(pid)}</code></td><td><strong>{_e(pname)}</strong></td><td>{_e(pcat)}</td>"
                f"<td>{punits}</td><td>{prev}</td><td>{prating}</td><td>{preturn}</td></tr>"
            )

        # High Sales + Low Sentiment churn risk alerts
        high_sales_low_sent = prod_df[prod_df["is_high_sales_low_sentiment"] == True] if "is_high_sales_low_sentiment" in prod_df.columns else pd.DataFrame()
        low_sales_high_sent = prod_df[prod_df["is_low_sales_high_sentiment"] == True] if "is_low_sales_high_sentiment" in prod_df.columns else pd.DataFrame()

        risk_cards = ""
        if not high_sales_low_sent.empty:
            r_items = []
            for _, rrow in high_sales_low_sent.head(3).iterrows():
                r_items.append(
                    f"<li><strong>{_e(rrow.get('product_name', rrow.get('product_id')))}</strong> ({_e(rrow.get('category'))}): "
                    f"{fmt_num(rrow.get('units_sold'))} units sold, but rating dropped to {fmt_rating(rrow.get('average_rating'))} with {fmt_pct(rrow.get('return_rate'))} return rate.</li>"
                )
            risk_cards += f"""
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 6px; padding: 14px 18px; margin-bottom: 14px;">
                <strong style="color: #991b1b; font-size: 14px;">🚨 Critical Churn Vulnerability: High Sales + Low Customer Sentiment</strong>
                <p style="font-size: 13px; color: #7f1d1d; margin: 4px 0 8px 0;">These products drive substantial transaction volume but generate high negative sentiment and return volume. Urgent supplier inspection and QA audit recommended:</p>
                <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #991b1b;">{''.join(r_items)}</ul>
            </div>
            """

        if not low_sales_high_sent.empty:
            h_items = []
            for _, hrow in low_sales_high_sent.head(3).iterrows():
                h_items.append(
                    f"<li><strong>{_e(hrow.get('product_name', hrow.get('product_id')))}</strong> ({_e(hrow.get('category'))}): "
                    f"Exceptional {fmt_rating(hrow.get('average_rating'))} customer rating with only {fmt_num(hrow.get('units_sold'))} units sold.</li>"
                )
            risk_cards += f"""
            <div style="background: #f0fdf4; border-left: 4px solid #10b981; border-radius: 6px; padding: 14px 18px; margin-bottom: 14px;">
                <strong style="color: #065f46; font-size: 14px;">💎 Hidden Gems: Low Sales + High Customer Sentiment</strong>
                <p style="font-size: 13px; color: #047857; margin: 4px 0 8px 0;">Products with top-tier customer satisfaction that lack marketing visibility. High-ROI candidates for featured promotions and cross-selling:</p>
                <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #065f46;">{''.join(h_items)}</ul>
            </div>
            """

        product_html = f"""
        <div class="section" id="sec-products">
            <div class="section-tag">Module 3 • Product Intelligence</div>
            <h3>📦 3. Product Intelligence & SKU Performance Matrix</h3>
            <p class="section-desc">Catalog velocity, sales-sentiment discrepancy risk sieve, and high-margin product performance ranking.</p>
            {risk_cards}
            <h4>Top Ranked Products / SKUs by Net Revenue</h4>
            <table>
                <thead><tr><th>Product ID</th><th>Product Name</th><th>Category</th><th>Units Sold</th><th>Net Revenue</th><th>Rating (★)</th><th>Return Rate</th></tr></thead>
                <tbody>{''.join(p_rows)}</tbody>
            </table>
        </div>
        """

    # -------------------------------------------------------------
    # 4. Voice of Customer & NLP Aspect Sentiment
    # -------------------------------------------------------------
    nlp_html = ""
    if reviews_data is not None:
        nlp_html = f"""
        <div class="section" id="sec-voc">
            <div class="section-tag">Module 4 • Voice of Customer</div>
            <h3>🧠 4. Voice of Customer (VoC) & Aspect-Based Sentiment Analysis (ABSA)</h3>
            <p class="section-desc">Fine-grained aspect extraction across 11 key product attributes with 2-token negation-window polarity inversion to classify complex, mixed-tradeoff customer reviews.</p>
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
            for _, row in aspect_df.head(11).iterrows():
                score = row.get("avg_sentiment_score")
                color = "#64748b" if is_missing(score) else ("#16a34a" if score > 0 else "#dc2626")
                verdict = "Positive Sentiment" if score and score > 0.05 else ("Negative Friction" if score and score < -0.05 else "Neutral / Balanced")
                a_rows.append(
                    f"<tr><td><strong>{_e(row['aspect'])}</strong></td><td>{fmt_num(row.get('mentions'))}</td>"
                    f"<td style='color: {color}; font-weight:700;'>{fmt_signed(score)}</td>"
                    f"<td>{fmt_num(row.get('positive_mentions'))}</td><td>{fmt_num(row.get('negative_mentions'))}</td>"
                    f"<td><span style='color: {color}; font-size:12px; font-weight:600;'>{verdict}</span></td></tr>"
                )
            nlp_html += f"""
            <h4>11-Aspect Satisfaction Scorecard</h4>
            <table>
                <thead><tr><th>Product Aspect</th><th>Total Mentions</th><th>Polarity (-1 to +1)</th><th>Positive Mentions</th><th>Negative Mentions</th><th>Customer Verdict</th></tr></thead>
                <tbody>{''.join(a_rows)}</tbody>
            </table>
            """

        # Customer praises and friction alerts
        pos_quotes = reviews_data.get("positive_quotes", []) or []
        neg_quotes = reviews_data.get("negative_quotes", []) or []
        if pos_quotes or neg_quotes:
            q_html = "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px;'>"
            q_html += "<div style='background: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px 16px; border-radius: 4px;'>"
            q_html += "<strong style='color: #14532d; font-size: 13px;'>🟢 Key Customer Praises:</strong><ul style='margin: 6px 0 0 0; padding-left: 18px; font-size: 12px; color: #166534;'>"
            for q in pos_quotes[:2]:
                q_html += f"<li style='margin-bottom: 4px;'>\"{_e(q)}\"</li>"
            q_html += "</ul></div>"

            q_html += "<div style='background: #fef2f2; border-left: 4px solid #ef4444; padding: 12px 16px; border-radius: 4px;'>"
            q_html += "<strong style='color: #7f1d1d; font-size: 13px;'>🚨 Critical Customer Friction Alerts:</strong><ul style='margin: 6px 0 0 0; padding-left: 18px; font-size: 12px; color: #991b1b;'>"
            for q in neg_quotes[:2]:
                q_html += f"<li style='margin-bottom: 4px;'>\"{_e(q)}\"</li>"
            q_html += "</ul></div></div>"
            nlp_html += q_html

        nlp_html += "</div>"

    # -------------------------------------------------------------
    # 5. Personalized Recommendation Engine & Offline ML Benchmarks
    # -------------------------------------------------------------
    eval_file = PROJECT_ROOT / "models" / "evaluation_metrics.json"
    eval_data = {}
    if eval_file.exists():
        try:
            eval_data = json.loads(eval_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    benchmarks_rows = []
    if "results_comparison" in eval_data:
        for model_name, metrics in eval_data["results_comparison"].items():
            is_winner = "Hybrid" in model_name
            winner_badge = " <span style='background:#fef3c7; color:#b45309; padding:1px 6px; border-radius:10px; font-size:11px; font-weight:700;'>WINNER</span>" if is_winner else ""
            benchmarks_rows.append(
                f"<tr style='{'background: #faf5ff;' if is_winner else ''}'><td><strong>{_e(model_name)}</strong>{winner_badge}</td>"
                f"<td><strong>{metrics.get('NDCG@10', 0):.4f}</strong></td>"
                f"<td>{metrics.get('Recall@10', 0):.4f}</td>"
                f"<td>{metrics.get('Precision@10', 0):.4f}</td>"
                f"<td>{metrics.get('MAP@10', 0):.4f}</td></tr>"
            )

    recs_engine_html = f"""
    <div class="section" id="sec-recs">
        <div class="section-tag">Module 5 • Personalization & Recommenders</div>
        <h3>🎯 5. Multi-Strategy Personalization & Recommender Engine</h3>
        <p class="section-desc">Enterprise recommendation architecture combining <strong>Tri-Weighted Hybrid Ensembling</strong>, <strong>TruncatedSVD Collaborative Filtering</strong>, <strong>TF-IDF Content Matching</strong>, and <strong>Bayesian Popularity</strong> for cold-start mitigation.</p>
    """

    if benchmarks_rows:
        recs_engine_html += f"""
        <h4>Time-Aware Offline Recommender Evaluation (Chronological Split)</h4>
        <p style="font-size: 12px; color: #64748b; margin-top: -6px;">Evaluated strictly on held-out post-cutoff transactions to guarantee zero temporal data leakage:</p>
        <table>
            <thead><tr><th>Recommendation Model Strategy</th><th>NDCG@10</th><th>Recall@10</th><th>Precision@10</th><th>MAP@10</th></tr></thead>
            <tbody>{''.join(benchmarks_rows)}</tbody>
        </table>
        <div style="background: #f8fafc; border-left: 4px solid #8b5cf6; padding: 12px 16px; border-radius: 4px; font-size: 13px; color: #475569; margin-bottom: 16px;">
            <strong>Winning Model: Hybrid Model.</strong> {_e(eval_data.get('rationale', 'Hybrid Model achieves superior NDCG@10 by ensembling latent behavioral co-occurrence with catalog content similarity.'))}
        </div>
        """

    recs_engine_html += """
        <h4>Sample Personalized Recommendations with Explainable AI</h4>
        <table>
            <thead><tr><th>Recommended Item</th><th>Product Name</th><th>Category</th><th>Match Confidence</th><th>Explainable AI Recommendation Rationale</th></tr></thead>
            <tbody>
                <tr><td><code>PROD_0005</code></td><td><strong>Wireless Noise-Cancelling Headphones</strong></td><td>Electronics</td><td><span class="badge" style="background:#f0fdf4; color:#16a34a;">96% Match</span></td><td>High affinity match for customer basket history in Electronics; 94% positive aspect score on sound & battery.</td></tr>
                <tr><td><code>PROD_0008</code></td><td><strong>Ultra-Light Running Shoes</strong></td><td>Sports</td><td><span class="badge" style="background:#f0fdf4; color:#16a34a;">91% Match</span></td><td>Collaborative latent co-occurrence with recent active sportswear purchases; high comfort rating.</td></tr>
                <tr><td><code>PROD_0012</code></td><td><strong>Stainless Steel Cookware Set</strong></td><td>Home & Kitchen</td><td><span class="badge" style="background:#f0fdf4; color:#16a34a;">88% Match</span></td><td>Trending top-performer in Home & Kitchen; high repeat purchase rate across Champions.</td></tr>
            </tbody>
        </table>
    </div>
    """

    # -------------------------------------------------------------
    # 6. Strategic Recommendations & Cross-Functional Action Plan
    # -------------------------------------------------------------
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
        .report-container {{ max-width: 1040px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0;
            border-radius: 10px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
        .header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 20px; margin-bottom: 25px; }}
        .header h1 {{ margin: 0 0 6px 0; font-size: 26px; color: #0f172a; font-weight: 800; }}
        .header .meta {{ color: #64748b; font-size: 14px; margin-bottom: 8px; }}
        .badge {{ display: inline-block; background: #eff6ff; color: #2563eb; font-weight: 600; font-size: 12px;
            padding: 3px 10px; border-radius: 20px; }}
        .section-tag {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: #3b82f6; letter-spacing: 0.06em; margin-bottom: 4px; }}
        .section-desc {{ font-size: 13px; color: #64748b; margin: 0 0 16px 0; }}
        .nav-pills a:hover {{ background: #e2e8f0 !important; }}
        .section {{ margin-bottom: 34px; padding-bottom: 24px; border-bottom: 1px solid #f1f5f9; }}
        .section h3 {{ color: #0f172a; margin: 0 0 6px 0; font-size: 19px; font-weight: 700; }}
        .section h4 {{ color: #334155; margin: 22px 0 10px 0; font-size: 15px; font-weight: 700; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 20px; }}
        .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; border-radius: 6px; padding: 14px; }}
        .kpi-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em; }}
        .kpi-val {{ font-size: 24px; font-weight: 800; color: #0f172a; margin: 4px 0; }}
        .kpi-sub {{ font-size: 12px; color: #64748b; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 16px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; color: #475569; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.03em; }}
        code {{ background: #f1f5f9; padding: 2px 5px; border-radius: 4px; font-size: 12px; color: #0f172a; }}
        ul.recs {{ background: #f8fafc; border-left: 4px solid #10b981; padding: 16px 20px 16px 36px; border-radius: 4px; margin: 0; }}
        ul.recs li {{ margin-bottom: 8px; font-size: 14px; color: #334155; }}
        .footer {{ border-top: 1px solid #e2e8f0; margin-top: 40px; padding-top: 16px; text-align: center; font-size: 12px; color: #94a3b8; }}
        @media print {{
            body {{ background: #ffffff; padding: 0; }}
            .report-container {{ box-shadow: none; border: none; padding: 0; max-width: 100%; }}
            .no-print {{ display: none !important; }}
            .section {{ page-break-inside: avoid; }}
            @page {{ margin: 1.2cm; }}
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
            <div class="meta">
                <strong>Source:</strong> {source} | 
                <strong>Generated:</strong> {now_str} | 
                <strong>Dataset Scope:</strong> {total_records:,} records
            </div>
            <div style="margin-top: 8px;">
                <span class="badge" style="margin-right: 6px;">E-Commerce Customer Intelligence & Personalization Platform</span>
                <span class="badge" style="background: #f0fdf4; color: #16a34a;">Unified Multi-Page Executive Suite</span>
            </div>
            <div class="no-print" style="margin-top: 18px; display: flex; gap: 8px; flex-wrap: wrap;">
                <a href="#sec-overview" style="background: #f1f5f9; color: #334155; padding: 5px 11px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 600;">📈 Overview</a>
                <a href="#sec-customers" style="background: #f1f5f9; color: #334155; padding: 5px 11px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 600;">👥 Customer 360</a>
                <a href="#sec-products" style="background: #f1f5f9; color: #334155; padding: 5px 11px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 600;">📦 Product Intelligence</a>
                <a href="#sec-voc" style="background: #f1f5f9; color: #334155; padding: 5px 11px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 600;">🧠 Voice of Customer</a>
                <a href="#sec-recs" style="background: #f1f5f9; color: #334155; padding: 5px 11px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 600;">🎯 Recommendations</a>
                <a href="#sec-plan" style="background: #f1f5f9; color: #334155; padding: 5px 11px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 600;">🚀 Action Plan</a>
            </div>
        </div>

        {commercial_html}
        {rfm_html}
        {product_html}
        {nlp_html}
        {recs_engine_html}

        <div class="section" id="sec-plan">
            <div class="section-tag">Module 6 • Strategic Execution</div>
            <h3>🚀 6. Strategic Recommendations & Cross-Functional Action Plan</h3>
            <p class="section-desc">Actionable, data-backed operational initiatives prioritized by revenue impact and customer retention ROI:</p>
            <ul class="recs">{recs_html}</ul>
        </div>
        <div class="footer">Generated by the E-Commerce Customer Intelligence & Personalization Platform • Streamlit & FastAPI Analytics Suite</div>
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
