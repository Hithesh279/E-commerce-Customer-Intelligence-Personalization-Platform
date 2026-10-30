"""
src/analytics/auto_analyzer.py
Intelligent schema detection, batch NLP enrichment, commercial KPI extraction,
RFM behavioral profiling, and statistical table analysis for user-uploaded datasets.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import warnings
import numpy as np
import pandas as pd

from src.nlp.aspect_extraction import extract_aspect_sentiment_from_text
from src.nlp.preprocessing import clean_text, clean_text_series
from src.nlp.sentiment_predict import SentimentPredictor
from src.utils.logging import get_logger

logger = get_logger("auto_analyzer")


POSITIVE_LABELS = {"positive", "pos", "4", "5", "good", "happy", "true", "yes"}
NEGATIVE_LABELS = {"negative", "neg", "1", "2", "0", "-1", "bad", "sad", "false", "no"}
NEUTRAL_LABELS = {"neutral", "3", "mixed", "ok", "okay"}


def _standardize_sentiment(val: Any) -> str:
    """Map a pre-labelled value to Positive/Neutral/Negative. Unknown values stay "Unlabeled"."""
    if pd.isna(val):
        return "Unlabeled"
    s = str(val).strip().lower()
    if s in POSITIVE_LABELS:
        return "Positive"
    if s in NEGATIVE_LABELS:
        return "Negative"
    if s in NEUTRAL_LABELS:
        return "Neutral"
    return "Unlabeled"


def detect_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Intelligently inspect column names, dtypes, and value characteristics
    to map columns to semantic business roles and determine data modalities.
    """
    cols_lower = {col: str(col).strip().lower() for col in df.columns}
    detected: Dict[str, Optional[str]] = {
        "text_col": None,
        "sentiment_col": None,
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
        for col in df.select_dtypes(include=["object", "string"]).columns:
            low = cols_lower[col]
            if low.endswith("_id") or low == "id":
                continue
            sample_lens = df[col].dropna().astype(str).str.len()
            if not sample_lens.empty and sample_lens.mean() > 25:
                detected["text_col"] = col
                break

    # 2. Sentiment Column (pre-labeled sentiment or polarity)
    for kw in ["sentiment", "sentiment_label", "polarity", "vibe", "label", "sentiment_class", "feedback_sentiment", "feedback_type"]:
        for col, low in cols_lower.items():
            if low.endswith("_id") or low == "id":
                continue
            if kw in low:
                detected["sentiment_col"] = col
                break
        if detected["sentiment_col"]:
            break

    # 3. Rating Column
    for kw in ["rating", "csat", "satisfaction_score", "satisfaction", "stars", "score"]:
        for col, low in cols_lower.items():
            if low.endswith("_id") or low == "id":
                continue
            if kw in low and pd.api.types.is_numeric_dtype(df[col]):
                detected["rating_col"] = col
                break
        if detected["rating_col"]:
            break

    # 4. Date Column
    for kw in ["order_date", "review_date", "ticket_date", "signup_date", "last_order_date", "dispatch_date", "return_date", "campaign_date", "session_date", "promo_month", "date", "created_at", "timestamp"]:
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
                if len(sample_s) > 0:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        if pd.to_datetime(sample_s, errors="coerce").notnull().all():
                            detected["date_col"] = col
                            break
            except Exception:
                continue

    # 5. Revenue / Amount / Spend Column (prioritize total amount / revenue over unit price)
    for kw in [
        "total_amount", "gross_revenue_driven", "revenue", "lifetime_spend", "mrr_amount",
        "gross_spend", "net_spend", "ad_spend", "refund_amount", "cart_value", "shipping_cost",
        "discount_cost", "sales", "total", "amount", "spend", "selling_price", "unit_price", "price"
    ]:
        for col, low in cols_lower.items():
            if low.endswith("_id") or low == "id":
                continue
            if kw in low and pd.api.types.is_numeric_dtype(df[col]):
                detected["revenue_col"] = col
                break
        if detected["revenue_col"]:
            break

    # 6. Customer ID Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in ["customer_id", "visitor_id", "user_id", "client_id", "shopper_id", "cust_id", "account_id"]):
            detected["customer_col"] = col
            break

    # 7. Product / SKU / Item Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in ["product_name", "campaign_name", "promo_code", "product_id", "sku", "item_name", "item_id", "title"]):
            detected["product_col"] = col
            break

    # 8. Category Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in [
            "category", "dept", "department", "channel", "carrier", "return_reason",
            "dropoff_stage", "traffic_source", "discount_type", "landing_page", "plan_tier", "tier", "segment"
        ]):
            detected["category_col"] = col
            break

    # 9. Status / Return / Churn Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in ["return_status", "churn_status", "delivery_status", "converted", "status", "priority", "loyalty_tier"]):
            detected["status_col"] = col
            break

    # 10. Quantity / Volume Column
    for col, low in cols_lower.items():
        if any(kw in low for kw in [
            "quantity", "qty", "units_sold", "units", "items_in_cart", "redemptions_count",
            "conversions", "clicks", "impressions", "total_orders", "pages_viewed"
        ]):
            if pd.api.types.is_numeric_dtype(df[col]):
                detected["quantity_col"] = col
                break

    # Modality inference
    has_reviews = (
        detected["text_col"] is not None
        or detected["sentiment_col"] is not None
        or (detected["rating_col"] is not None and "rating" in str(detected["rating_col"]).lower())
    )
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
        "detected_mappings": detected,
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
    text_col: Optional[str] = None,
    rating_col: Optional[str] = None,
    sentiment_col: Optional[str] = None,
    max_records: int = 100000,
) -> Tuple[pd.DataFrame, Optional[Dict[str, Any]]]:
    """
    Classify review sentiment and extract product aspects from a customer-feedback table.

    Sentiment source, in priority order: a pre-labelled sentiment column, then star ratings, then the
    trained text classifier. The source used for each row is recorded in ``sentiment_source``.
    Rows without a usable signal are labelled "Unlabeled" and are excluded from every percentage.

    Returns (enriched_df, analytics). analytics is None when the table has no review signal at all.
    """
    enriched_df = df.copy()
    has_sentiment_col = bool(sentiment_col) and sentiment_col in df.columns
    has_rating_col = bool(rating_col) and rating_col in df.columns
    has_text_col = bool(text_col) and text_col in df.columns
    if not (has_sentiment_col or has_rating_col or has_text_col):
        return enriched_df, None

    total_count = len(enriched_df)
    score_map = {"Positive": 1.0, "Neutral": 0.0, "Negative": -1.0}
    texts = enriched_df[text_col].fillna("").astype(str).tolist() if has_text_col else [""] * total_count

    if has_sentiment_col:
        labels = df[sentiment_col].apply(_standardize_sentiment)
        enriched_df["predicted_sentiment"] = labels
        enriched_df["sentiment_confidence"] = np.where(labels == "Unlabeled", np.nan, 0.95)
        enriched_df["sentiment_source"] = "pre-labelled column"
    elif has_rating_col:
        r = pd.to_numeric(df[rating_col], errors="coerce")
        enriched_df["predicted_sentiment"] = np.select(
            [r >= 4, r <= 2, r == 3], ["Positive", "Negative", "Neutral"], default="Unlabeled"
        )
        enriched_df["sentiment_confidence"] = np.where(r.notna(), 0.90, np.nan)
        enriched_df["sentiment_source"] = "star rating"
    else:
        cleaned = clean_text_series(pd.Series(texts), remove_stopwords=False).tolist()
        has_content = np.array([bool(c) for c in cleaned])
        try:
            predictor = SentimentPredictor()
            features = predictor.vectorizer.transform(cleaned)
            probas = predictor.model.predict_proba(features)
            classes = predictor.model.classes_
            max_idx = np.argmax(probas, axis=1)
            sentiments = np.array([classes[i] for i in max_idx], dtype=object)
            confidences = np.round(probas[np.arange(len(texts)), max_idx], 3)
            source = "trained text classifier"
        except Exception as e:  # model artifacts missing or incompatible
            logger.warning(f"Could not run SentimentPredictor ({e}); using keyword heuristic.")
            lowered = pd.Series(texts).str.lower()
            is_pos = lowered.str.contains("great|excellent|love|good|fast|phenomenal|clean|best|amazing", regex=True)
            is_neg = lowered.str.contains("bad|terrible|worst|broken|awful|slow|poor|hate|disappointed", regex=True)
            sentiments = np.where(is_pos, "Positive", np.where(is_neg, "Negative", "Neutral")).astype(object)
            confidences = np.full(len(texts), np.nan)
            source = "keyword heuristic"
        sentiments = np.where(has_content, sentiments, "Unlabeled")
        enriched_df["predicted_sentiment"] = sentiments
        enriched_df["sentiment_confidence"] = np.where(has_content, confidences, np.nan)
        enriched_df["sentiment_source"] = source

    # Aspect extraction on a representative sample (first 1,000 texts). Rows beyond the sample are
    # marked as not analysed rather than given invented aspect tags.
    sample_size = min(total_count, 1000)
    aspect_records: List[Dict[str, Any]] = []
    aspect_tags = ["Not analysed"] * total_count
    if has_text_col:
        for i in range(sample_size):
            extracted = extract_aspect_sentiment_from_text(texts[i])
            aspect_tags[i] = ", ".join(f"{a['aspect']} ({a['sentiment']})" for a in extracted) or "General"
            aspect_records.extend({**a, "review_row": i} for a in extracted)
    enriched_df["extracted_aspects"] = aspect_tags

    labels = enriched_df["predicted_sentiment"]
    labeled = labels[labels.isin(["Positive", "Neutral", "Negative"])]
    n_labeled = int(len(labeled))
    counts = labeled.value_counts()
    sentiment_counts = {
        "Positive": int(counts.get("Positive", 0)),
        "Neutral": int(counts.get("Neutral", 0)),
        "Negative": int(counts.get("Negative", 0)),
    }

    def _pct(n: int) -> Optional[float]:
        return round(n / n_labeled * 100, 1) if n_labeled else None

    avg_polarity = round(float(labeled.map(score_map).mean()), 2) if n_labeled else None
    avg_rating = None
    if has_rating_col:
        valid = pd.to_numeric(df[rating_col], errors="coerce").dropna()
        avg_rating = round(float(valid.mean()), 2) if len(valid) else None

    scale_factor = max(1.0, total_count / max(sample_size, 1))
    if aspect_records:
        aspect_df = pd.DataFrame(aspect_records)
        aspect_df["score"] = aspect_df["sentiment"].map(score_map)
        aspect_summary = aspect_df.groupby("aspect").agg(
            mentions=("aspect", lambda s: int(len(s) * scale_factor)),
            avg_sentiment_score=("score", "mean"),
            positive_mentions=("sentiment", lambda s: int((s == "Positive").sum() * scale_factor)),
            negative_mentions=("sentiment", lambda s: int((s == "Negative").sum() * scale_factor)),
        ).reset_index()
        aspect_summary["avg_sentiment_score"] = aspect_summary["avg_sentiment_score"].round(2)
        aspect_summary = aspect_summary.sort_values("mentions", ascending=False)
    else:
        aspect_summary = pd.DataFrame(
            columns=["aspect", "mentions", "avg_sentiment_score", "positive_mentions", "negative_mentions"]
        )

    pos_quotes, neg_quotes = [], []
    if has_text_col:
        labeled_text = enriched_df.loc[labels.isin(["Positive", "Negative"]) & (enriched_df[text_col].fillna("").astype(str).str.strip() != "")]
        pos_quotes = labeled_text[labeled_text["predicted_sentiment"] == "Positive"][text_col].astype(str).head(3).tolist()
        neg_quotes = labeled_text[labeled_text["predicted_sentiment"] == "Negative"][text_col].astype(str).head(3).tolist()

    sources = sorted(set(enriched_df["sentiment_source"]))
    analytics = {
        "total_reviews": total_count,
        "labeled_reviews": n_labeled,
        "positive_pct": _pct(sentiment_counts["Positive"]),
        "neutral_pct": _pct(sentiment_counts["Neutral"]),
        "negative_pct": _pct(sentiment_counts["Negative"]),
        "sentiment_counts": sentiment_counts,
        "sentiment_source": ", ".join(sources),
        "avg_rating": avg_rating,
        "avg_polarity": avg_polarity,
        "aspect_summary": aspect_summary,
        "aspect_records": aspect_records,
        "positive_quotes": pos_quotes,
        "negative_quotes": neg_quotes,
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
    Compute commercial metrics from transaction-like data.

    Metrics that the mapped columns cannot support are returned as None (for example total_revenue
    without a revenue column), never as a guessed value.
    """
    has_revenue = bool(revenue_col) and revenue_col in df.columns
    total_orders = len(df) if has_revenue else None
    total_revenue = None
    aov = None
    return_rate = None

    if has_revenue:
        revenue = pd.to_numeric(df[revenue_col], errors="coerce")
        total_revenue = round(float(revenue.sum()), 2)
        aov = round(total_revenue / max(1, total_orders), 2)

    if status_col and status_col in df.columns:
        returned = int(df[status_col].astype(str).str.lower().str.contains("return|cancel|churn").sum())
        return_rate = round((returned / max(1, len(df))) * 100, 1)

    timeline_df = pd.DataFrame()
    if date_col and date_col in df.columns and has_revenue:
        temp = df.copy()
        temp["parsed_date"] = pd.to_datetime(temp[date_col], errors="coerce")
        temp["_revenue"] = pd.to_numeric(temp[revenue_col], errors="coerce")
        temp = temp.dropna(subset=["parsed_date"])
        if not temp.empty:
            temp["period"] = temp["parsed_date"].dt.to_period("M").astype(str)
            timeline_df = temp.groupby("period").agg(
                revenue=("_revenue", "sum"),
                orders=("parsed_date", "count"),
            ).reset_index().sort_values("period")
            timeline_df["revenue"] = timeline_df["revenue"].round(2)

    cat_df = pd.DataFrame()
    if category_col and category_col in df.columns and has_revenue:
        work = df.assign(_revenue=pd.to_numeric(df[revenue_col], errors="coerce"))
        cat_df = work.groupby(category_col).agg(
            revenue=("_revenue", "sum"),
            orders=("_revenue", "count"),
        ).reset_index()
        cat_df["share_pct"] = ((cat_df["revenue"] / max(0.01, total_revenue)) * 100).round(1)
        cat_df["revenue"] = cat_df["revenue"].round(2)
        cat_df = cat_df.sort_values("revenue", ascending=False)

    prod_df = pd.DataFrame()
    if product_col and product_col in df.columns:
        work = df.assign(_revenue=pd.to_numeric(df[revenue_col], errors="coerce")) if has_revenue else df
        agg_kwargs = {"orders": (product_col, "count")}
        if has_revenue:
            agg_kwargs["revenue"] = ("_revenue", "sum")
        prod_df = work.groupby(product_col).agg(**agg_kwargs).reset_index()
        sort_by = "revenue" if "revenue" in prod_df.columns else "orders"
        prod_df = prod_df.sort_values(sort_by, ascending=False).head(10)

    unique_custs = int(df[customer_col].nunique()) if customer_col and customer_col in df.columns else None

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

    Accepts transaction rows (aggregated per customer) or a pre-aggregated customer table that has
    lifetime spend and order counts. Recency is scored only when dates are available. Without dates
    the segments use frequency and monetary value alone, and recency-based metrics are None.
    """
    cols_low = {c: str(c).lower() for c in df.columns}
    has_lifetime = any("lifetime_spend" in c or "total_spend" in c for c in cols_low.values())
    has_orders = any("total_orders" in c or "order_count" in c for c in cols_low.values())

    if has_lifetime and has_orders:
        spend_col = [c for c, low in cols_low.items() if "lifetime_spend" in low or "total_spend" in low][0]
        orders_col = [c for c, low in cols_low.items() if "total_orders" in low or "order_count" in low][0]
        rfm = df[[customer_col, spend_col, orders_col]].copy()
        rfm[spend_col] = pd.to_numeric(rfm[spend_col], errors="coerce")
        rfm[orders_col] = pd.to_numeric(rfm[orders_col], errors="coerce")
        rfm = rfm.rename(columns={spend_col: "monetary_total", orders_col: "frequency"})
        rfm = rfm.groupby(customer_col, as_index=False).agg(monetary_total=("monetary_total", "sum"), frequency=("frequency", "sum"))
        if date_col and date_col in df.columns:
            parsed = pd.to_datetime(df[date_col], errors="coerce")
            ref_date = parsed.max() + pd.Timedelta(days=1)
            last_seen = pd.DataFrame({customer_col: df[customer_col], "_d": parsed}).groupby(customer_col)["_d"].max()
            rfm["recency_days"] = (ref_date - rfm[customer_col].map(last_seen)).dt.days
        else:
            rfm["recency_days"] = np.nan
    else:
        if not date_col or not revenue_col:
            raise ValueError("Transaction-level RFM requires both date_col and revenue_col.")
        temp = df.copy()
        temp["parsed_date"] = pd.to_datetime(temp[date_col], errors="coerce")
        temp["_revenue"] = pd.to_numeric(temp[revenue_col], errors="coerce")
        temp = temp.dropna(subset=[customer_col])
        ref_date = temp["parsed_date"].max() + pd.Timedelta(days=1)
        rfm = temp.groupby(customer_col).agg(
            last_date=("parsed_date", "max"),
            frequency=(customer_col, "count"),
            monetary_total=("_revenue", "sum"),
        ).reset_index()
        rfm["recency_days"] = (ref_date - rfm["last_date"]).dt.days
        rfm = rfm.drop(columns="last_date")

    n_cust = len(rfm)
    if n_cust < 2:
        raise ValueError("RFM segmentation needs at least 2 customers.")
    recency_available = bool(rfm["recency_days"].notna().any())
    q = min(5, max(2, n_cust // 4))

    def _quintile(series: pd.Series, higher_is_better: bool) -> pd.Series:
        ranks = series.rank(method="first", ascending=higher_is_better)
        return pd.qcut(ranks, q=q, labels=range(1, q + 1)).astype(int)

    if recency_available:
        rfm["r_score"] = _quintile(rfm["recency_days"], higher_is_better=False)
    else:
        rfm["r_score"] = np.nan
    rfm["f_score"] = _quintile(rfm["frequency"], higher_is_better=True)
    rfm["m_score"] = _quintile(rfm["monetary_total"], higher_is_better=True)

    def map_segment(row: pd.Series) -> str:
        f, m = row["f_score"], row["m_score"]
        if not recency_available:
            if f >= 4 and m >= 4:
                return "High Value"
            if f >= 3 and m >= 3:
                return "Potential Loyalists"
            if f <= 2 and m <= 2:
                return "Low Value"
            return "Core"
        r = row["r_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        if f >= 3 and m >= 3:
            return "Loyal Customers"
        if r >= 4 and f <= 2:
            return "New / Promising"
        if r <= 2 and f >= 3:
            return "At Risk"
        if r <= 2 and f <= 2:
            return "Lost / Inactive"
        return "Potential Loyalists"

    rfm["rfm_segment"] = rfm.apply(map_segment, axis=1)
    if recency_available:
        rfm["rfm_score"] = rfm["r_score"].astype(int).astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)
    else:
        rfm["rfm_score"] = "-" + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)

    seg_summary = rfm["rfm_segment"].value_counts().reset_index()
    seg_summary.columns = ["segment", "count"]
    seg_summary["share_pct"] = ((seg_summary["count"] / n_cust) * 100).round(1)

    def _count(name: str) -> Optional[int]:
        if not recency_available:
            return None
        return int((rfm["rfm_segment"] == name).sum())

    metrics = {
        "total_customers": n_cust,
        "recency_available": recency_available,
        "avg_recency_days": round(float(rfm["recency_days"].mean()), 1) if recency_available else None,
        "avg_frequency": round(float(rfm["frequency"].mean()), 1),
        "avg_monetary": round(float(rfm["monetary_total"].mean()), 2),
        "segment_summary": seg_summary,
        "champions_count": _count("Champions"),
        "at_risk_count": _count("At Risk"),
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
