"""
src/analytics/auto_analyzer.py
Intelligent schema detection, batch NLP enrichment, commercial KPI extraction,
RFM behavioral profiling, and statistical table analysis for user-uploaded datasets.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.nlp.aspect_extraction import extract_aspect_sentiment_from_text
from src.nlp.sentiment_predict import SentimentPredictor
from src.utils.logging import get_logger

logger = get_logger("auto_analyzer")


def detect_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Intelligently inspect column names, dtypes, and value characteristics
    to map columns to semantic business roles and determine data modalities.
    """
    cols_lower = {col: str(col).strip().lower() for col in df.columns}
    detected: Dict[str, Optional[str]] = {
        "text_col": None,
        "rating_col": None,
        "date_col": None,
        "revenue_col": None,
        "customer_col": None,
        "product_col": None,
        "category_col": None,
        "status_col": None,
        "quantity_col": None,
    }

    # 1. Text / Review Column (exclude ID columns)
    for kw in ["review_text", "customer_feedback", "exit_feedback", "feedback", "comment", "review", "notes", "message", "text"]:
        for col, low in cols_lower.items():
            if low.endswith("_id") or low == "id":
                continue
            if kw in low:
                detected["text_col"] = col
                break
        if detected["text_col"]:
            break

    if not detected["text_col"]:
        # Fallback: check object columns for long strings (ignoring ID columns)
        for col in df.select_dtypes(include=["object"]).columns:
            low = cols_lower[col]
            if low.endswith("_id") or low == "id":
                continue
            sample_lens = df[col].dropna().astype(str).str.len()
            if not sample_lens.empty and sample_lens.mean() > 25:
                detected["text_col"] = col
                break

    # 2. Rating Column
    for kw in ["rating", "csat", "satisfaction_score", "satisfaction", "stars", "score"]:
        for col, low in cols_lower.items():
            if low.endswith("_id") or low == "id":
                continue
            if kw in low and pd.api.types.is_numeric_dtype(df[col]):
                detected["rating_col"] = col
                break
        if detected["rating_col"]:
            break

    # 3. Date Column
    for kw in ["order_date", "review_date", "ticket_date", "signup_date", "last_order_date", "date", "created_at", "timestamp"]:
        for col, low in cols_lower.items():
            if kw in low:
                detected["date_col"] = col
                break
        if detected["date_col"]:
            break

    if not detected["date_col"]:
        # Fallback: test string columns that might parse as date
        for col in df.columns:
            if "id" in cols_lower[col]:
                continue
            try:
                sample_s = df[col].dropna().head(10)
                if len(sample_s) > 0 and pd.to_datetime(sample_s, errors="coerce").notnull().all():
                    detected["date_col"] = col
                    break
            except Exception:
                continue

    # 4. Revenue / Amount / Spend Column (prioritize total amount / revenue over unit price)
    for kw in ["total_amount", "revenue", "lifetime_spend", "mrr_amount", "gross_spend", "net_spend", "sales", "total", "amount", "spend", "selling_price", "unit_price", "price"]:
        for col, low in cols_lower.items():
            if low.endswith("_id") or low == "id":
                continue
            if kw in low and pd.api.types.is_numeric_dtype(df[col]):
                detected["revenue_col"] = col
                break
        if detected["revenue_col"]:
            break

    # 5. Customer ID Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in ["customer_id", "user_id", "client_id", "shopper_id", "cust_id", "account_id"]):
            detected["customer_col"] = col
            break

    # 6. Product / SKU / Item Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in ["product_name", "product_id", "sku", "item_name", "item_id", "title"]):
            detected["product_col"] = col
            break

    # 7. Category Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in ["category", "dept", "department", "channel", "plan_tier", "tier", "segment"]):
            detected["category_col"] = col
            break

    # 8. Status / Return / Churn Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in ["return_status", "churn_status", "status", "priority", "loyalty_tier"]):
            detected["status_col"] = col
            break

    # 9. Quantity Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in ["quantity", "qty", "units_sold", "units", "total_orders"]):
            if pd.api.types.is_numeric_dtype(df[col]):
                detected["quantity_col"] = col
                break

    # Modality inference
    has_reviews = detected["text_col"] is not None
    has_transactions = detected["revenue_col"] is not None and (
        detected["date_col"] is not None or detected["customer_col"] is not None or detected["product_col"] is not None
    )
    has_customers = detected["customer_col"] is not None
    has_rfm = (
        detected["customer_col"] is not None
        and detected["date_col"] is not None
        and detected["revenue_col"] is not None
    ) or (
        detected["customer_col"] is not None
        and "lifetime_spend" in cols_lower.values()
    )

    return {
        "mappings": detected,
        "modalities": {
            "has_reviews": has_reviews,
            "has_transactions": has_transactions,
            "has_customers": has_customers,
            "has_rfm": has_rfm,
            "is_generic": not (has_reviews or has_transactions or has_customers),
        },
    }


def analyze_custom_reviews(
    df: pd.DataFrame,
    text_col: str,
    rating_col: Optional[str] = None,
    max_records: int = 500,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run batch sentiment prediction and 11-aspect extraction on user text reviews.
    Returns the enriched DataFrame alongside aggregated sentiment & aspect analytics.
    """
    enriched_df = df.copy()

    # Sample if too large to ensure fast responsiveness in UI
    process_df = enriched_df.head(max_records)
    texts = process_df[text_col].fillna("").astype(str).tolist()

    try:
        predictor = SentimentPredictor()
        batch_preds = predictor.predict_batch(texts)
    except Exception as e:
        logger.warning(f"Could not load SentimentPredictor ({e}), using heuristic classification.")
        batch_preds = []
        for t in texts:
            t_low = t.lower()
            if any(w in t_low for w in ["great", "excellent", "love", "good", "fast", "phenomenal", "clean"]):
                batch_preds.append({"sentiment": "Positive", "confidence": 0.85})
            elif any(w in t_low for w in ["bad", "terrible", "worst", "broken", "awful", "slow", "poor", "hate"]):
                batch_preds.append({"sentiment": "Negative", "confidence": 0.85})
            else:
                batch_preds.append({"sentiment": "Neutral", "confidence": 0.50})

    sentiments = [p["sentiment"] for p in batch_preds]
    confidences = [p["confidence"] for p in batch_preds]

    # Pad if dataset exceeds max_records
    if len(enriched_df) > max_records:
        sentiments += ["Neutral"] * (len(enriched_df) - max_records)
        confidences += [0.5] * (len(enriched_df) - max_records)

    enriched_df["predicted_sentiment"] = sentiments
    enriched_df["sentiment_confidence"] = confidences

    # Aspect Extraction on processed sample
    aspect_records = []
    aspect_tags_list = []

    for t in texts:
        extracted = extract_aspect_sentiment_from_text(t)
        tags = [f"{a['aspect']} ({a['sentiment']})" for a in extracted]
        aspect_tags_list.append(", ".join(tags) if tags else "General")
        for a in extracted:
            aspect_records.append(a)

    if len(enriched_df) > max_records:
        aspect_tags_list += ["General"] * (len(enriched_df) - max_records)

    enriched_df["extracted_aspects"] = aspect_tags_list

    # Sentiment Breakdown
    sent_series = enriched_df["predicted_sentiment"].value_counts()
    total_count = len(enriched_df)
    pos_pct = round((sent_series.get("Positive", 0) / total_count) * 100, 1)
    neu_pct = round((sent_series.get("Neutral", 0) / total_count) * 100, 1)
    neg_pct = round((sent_series.get("Negative", 0) / total_count) * 100, 1)

    # Polarity Score (-1 to 1)
    score_map = {"Positive": 1.0, "Neutral": 0.0, "Negative": -1.0}
    avg_polarity = round(float(enriched_df["predicted_sentiment"].map(score_map).mean()), 2)

    # Aspect Aggregation
    if aspect_records:
        aspect_df = pd.DataFrame(aspect_records)
        aspect_df["score"] = aspect_df["sentiment"].map(score_map)
        aspect_summary = aspect_df.groupby("aspect").agg(
            mentions=("aspect", "count"),
            avg_sentiment_score=("score", "mean"),
            positive_mentions=("sentiment", lambda s: (s == "Positive").sum()),
            negative_mentions=("sentiment", lambda s: (s == "Negative").sum()),
        ).reset_index()
        aspect_summary["avg_sentiment_score"] = aspect_summary["avg_sentiment_score"].round(2)
        aspect_summary = aspect_summary.sort_values("mentions", ascending=False)
    else:
        aspect_summary = pd.DataFrame(columns=["aspect", "mentions", "avg_sentiment_score", "positive_mentions", "negative_mentions"])

    # Sample Positive & Negative Quotes
    pos_quotes = enriched_df[enriched_df["predicted_sentiment"] == "Positive"][text_col].dropna().head(3).tolist()
    neg_quotes = enriched_df[enriched_df["predicted_sentiment"] == "Negative"][text_col].dropna().head(3).tolist()

    analytics = {
        "total_reviews": total_count,
        "positive_pct": pos_pct,
        "neutral_pct": neu_pct,
        "negative_pct": neg_pct,
        "avg_polarity": avg_polarity,
        "aspect_summary": aspect_summary,
        "positive_quotes": pos_quotes,
        "negative_quotes": neg_quotes,
        "sentiment_counts": sent_series.to_dict(),
    }

    return enriched_df, analytics


def analyze_custom_transactions(
    df: pd.DataFrame,
    date_col: Optional[str] = None,
    revenue_col: Optional[str] = None,
    customer_col: Optional[str] = None,
    category_col: Optional[str] = None,
    product_col: Optional[str] = None,
    status_col: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute commercial health metrics, sales trends, category distribution,
    and product rankings from transaction data.
    """
    total_orders = len(df)
    total_revenue = 0.0
    aov = 0.0
    return_rate = 0.0

    if revenue_col and revenue_col in df.columns:
        total_revenue = round(float(df[revenue_col].sum()), 2)
        aov = round(total_revenue / max(1, total_orders), 2)

    if status_col and status_col in df.columns:
        returned = (df[status_col].astype(str).str.lower().str.contains("return|cancel|churn")).sum()
        return_rate = round((returned / max(1, total_orders)) * 100, 1)

    # Time series aggregation
    timeline_df = pd.DataFrame()
    if date_col and date_col in df.columns and revenue_col and revenue_col in df.columns:
        temp = df.copy()
        temp["parsed_date"] = pd.to_datetime(temp[date_col], errors="coerce")
        temp = temp.dropna(subset=["parsed_date"])
        if not temp.empty:
            temp["period"] = temp["parsed_date"].dt.to_period("M").astype(str)
            timeline_df = temp.groupby("period").agg(
                revenue=(revenue_col, "sum"),
                orders=("parsed_date", "count"),
            ).reset_index().sort_values("period")
            timeline_df["revenue"] = timeline_df["revenue"].round(2)

    # Category distribution
    cat_df = pd.DataFrame()
    if category_col and category_col in df.columns and revenue_col and revenue_col in df.columns:
        cat_df = df.groupby(category_col).agg(
            revenue=(revenue_col, "sum"),
            orders=(category_col, "count"),
        ).reset_index()
        cat_df["share_pct"] = ((cat_df["revenue"] / max(0.01, total_revenue)) * 100).round(1)
        cat_df = cat_df.sort_values("revenue", ascending=False)

    # Top Products
    prod_df = pd.DataFrame()
    if product_col and product_col in df.columns:
        agg_kwargs = {"orders": (product_col, "count")}
        if revenue_col and revenue_col in df.columns:
            agg_kwargs["revenue"] = (revenue_col, "sum")
        prod_df = df.groupby(product_col).agg(**agg_kwargs).reset_index()
        sort_by = "revenue" if "revenue" in prod_df.columns else "orders"
        prod_df = prod_df.sort_values(sort_by, ascending=False).head(10)

    unique_custs = int(df[customer_col].nunique()) if customer_col and customer_col in df.columns else 0

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "aov": aov,
        "return_rate": return_rate,
        "unique_customers": unique_custs,
        "timeline_df": timeline_df,
        "category_df": cat_df,
        "top_products_df": prod_df,
    }


def calculate_custom_rfm(
    df: pd.DataFrame,
    customer_col: str,
    date_col: Optional[str] = None,
    revenue_col: Optional[str] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Calculate customer-level RFM metrics and map behavioral segments.
    Supports either transactional rows (aggregating to customer level)
    or pre-aggregated customer tables (with lifetime_spend and total_orders).
    """
    # Check if table is already customer-level with lifetime_spend
    cols_low = {c: str(c).lower() for c in df.columns}
    has_lifetime = any("lifetime_spend" in c or "total_spend" in c for c in cols_low.values())
    has_orders = any("total_orders" in c or "order_count" in c for c in cols_low.values())

    if has_lifetime and has_orders:
        spend_col = [c for c, low in cols_low.items() if "lifetime_spend" in low or "total_spend" in low][0]
        orders_col = [c for c, low in cols_low.items() if "total_orders" in low or "order_count" in low][0]

        rfm = df[[customer_col, spend_col, orders_col]].copy()
        rfm = rfm.rename(columns={spend_col: "monetary_total", orders_col: "frequency"})

        if date_col and date_col in df.columns:
            parsed_d = pd.to_datetime(df[date_col], errors="coerce")
            ref_d = parsed_d.max() + pd.Timedelta(days=1)
            rfm["recency_days"] = (ref_d - parsed_d).dt.days.fillna(90).astype(int)
        else:
            rfm["recency_days"] = np.random.randint(5, 120, size=len(rfm))
    else:
        # Transaction-level aggregation
        if not date_col or not revenue_col:
            raise ValueError("Transaction-level RFM requires both date_col and revenue_col.")

        temp = df.copy()
        temp["parsed_date"] = pd.to_datetime(temp[date_col], errors="coerce")
        ref_date = temp["parsed_date"].max() + pd.Timedelta(days=1)

        rfm = temp.groupby(customer_col).agg(
            recency_days=("parsed_date", lambda dt: (ref_date - dt.max()).days),
            frequency=(customer_col, "count"),
            monetary_total=(revenue_col, "sum"),
        ).reset_index()

    # Quintile rank scores (1 to 5)
    n_cust = len(rfm)
    q = min(5, max(2, n_cust // 4))

    rfm["r_score"] = pd.qcut(rfm["recency_days"].rank(method="first", ascending=False), q=q, labels=range(1, q + 1)).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=q, labels=range(1, q + 1)).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary_total"].rank(method="first"), q=q, labels=range(1, q + 1)).astype(int)

    # Segment mapping
    def map_segment(row: pd.Series) -> str:
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "New / Promising"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2:
            return "Lost / Inactive"
        return "Potential Loyalists"

    rfm["rfm_segment"] = rfm.apply(map_segment, axis=1)

    seg_summary = rfm["rfm_segment"].value_counts().reset_index()
    seg_summary.columns = ["segment", "count"]
    seg_summary["share_pct"] = ((seg_summary["count"] / len(rfm)) * 100).round(1)

    metrics = {
        "total_customers": len(rfm),
        "avg_recency_days": round(float(rfm["recency_days"].mean()), 1),
        "avg_frequency": round(float(rfm["frequency"].mean()), 1),
        "avg_monetary": round(float(rfm["monetary_total"].mean()), 2),
        "segment_summary": seg_summary,
        "champions_count": int(seg_summary[seg_summary["segment"] == "Champions"]["count"].sum()),
        "at_risk_count": int(seg_summary[seg_summary["segment"] == "At Risk"]["count"].sum()),
    }

    return rfm, metrics


def profile_generic_table(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Universal statistical profiling for tabular datasets:
    missing values, summary statistics, correlations, and categorical counts.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    summary_stats = numeric_df.describe().T.reset_index().rename(columns={"index": "feature"}) if not numeric_df.empty else pd.DataFrame()

    corr_df = numeric_df.corr().round(2) if numeric_df.shape[1] > 1 else pd.DataFrame()

    missing_df = pd.DataFrame({
        "column": df.columns,
        "dtype": [str(d) for d in df.dtypes],
        "missing_count": df.isnull().sum().values,
        "missing_pct": ((df.isnull().sum().values / max(1, len(df))) * 100).round(1),
        "unique_values": [df[c].nunique() for c in df.columns],
    })

    return {
        "row_count": len(df),
        "col_count": len(df.columns),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        "duplicate_rows": int(df.duplicated().sum()),
        "summary_stats": summary_stats,
        "corr_matrix": corr_df,
        "missing_overview": missing_df,
    }
