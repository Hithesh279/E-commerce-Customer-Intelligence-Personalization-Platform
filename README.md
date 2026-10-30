# E-commerce Customer Intelligence & Personalization Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0%2B-003B57.svg)](https://www.sqlite.org/)
[![Power BI Ready](https://img.shields.io/badge/Power_BI-Star_Schema-F2C811.svg)](https://powerbi.microsoft.com/)
[![Pytest](https://img.shields.io/badge/pytest-97%20passed%20(100%25)-brightgreen.svg)](https://docs.pytest.org/)

An enterprise-grade, end-to-end Data Science, Machine Learning, and Business Intelligence platform combining **Review NLP**, **11-Aspect-Based Sentiment Analysis (ABSA) with Negation-Window Polarity Inversion**, **NMF Unsupervised Topic Modeling**, **4-Strategy Personalized Recommendations (Popularity, Content-Based, Collaborative Filtering, Hybrid)**, **Time-Aware Offline Recommender Evaluation**, **Star-Schema BI Analytics**, a **Universal Ingestion & Auto-Dashboard Engine with 12 Enterprise Templates**, **Platform-Wide Dynamic Dataset Reactivity**, **1-Click Multi-Format Executive Report Downloads**, and a high-performance **FastAPI REST API Layer**.

---

## ⚡ Quick Start (Run in 3 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full data science pipeline (data generation, NLP & recommender training, SQLite & Power BI setup)
python run_pipeline.py

# 3. Launch the Streamlit Web Application
python -m streamlit run app/main.py
```
> Open **[http://localhost:8501](http://localhost:8501)** in your browser to access the interactive dashboard.
> To run the FastAPI backend: `python -m uvicorn api.main:app --port 8000` (docs at **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**).

---

## 📑 Table of Contents

1. [Executive Summary & Business Impact](#1-executive-summary--business-impact)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
3. [Key Features & Capabilities](#3-key-features--capabilities)
4. [Universal Ingestion Engine & Auto-Dashboard](#4-universal-ingestion-engine--auto-dashboard)
5. [12 Pre-Built Enterprise Business Templates](#5-12-pre-built-enterprise-business-templates)
6. [Platform-Wide Reactivity & Modality Adaptation](#6-platform-wide-reactivity--modality-adaptation)
7. [Universal 1-Click Dashboard Downloads](#7-universal-1-click-dashboard-downloads)
8. [High-Performance Caching & Sub-Second Optimization](#8-high-performance-caching--sub-second-optimization)
9. [Project Directory Structure](#9-project-directory-structure)
10. [Dataset & Data Dictionary](#10-dataset--data-dictionary)
11. [Data Cleaning & Quality Pipeline](#11-data-cleaning--quality-pipeline)
12. [NLP & 11-Aspect Sentiment Extraction (ABSA)](#12-nlp--11-aspect-sentiment-extraction-absa)
13. [NMF Topic & Complaint Modeling](#13-nmf-topic--complaint-modeling)
14. [Personalized Recommendation Engines](#14-personalized-recommendation-engines)
15. [Offline Evaluation & Mathematical Benchmarks](#15-offline-evaluation--mathematical-benchmarks)
16. [SQL Database & Complex Analytical Queries](#16-sql-database--complex-analytical-queries)
17. [Power BI Star-Schema & DAX Measures](#17-power-bi-star-schema--dax-measures)
18. [Interactive Web Applications & Pages](#18-interactive-web-applications--pages)
19. [FastAPI REST API Layer](#19-fastapi-rest-api-layer)
20. [Installation & How to Run](#20-installation--how-to-run)
21. [Automated Testing Suite (97 Tests)](#21-automated-testing-suite-97-tests)
22. [Engineering Decisions & Design Rationale](#22-engineering-decisions--design-rationale)

---

## 1. Executive Summary & Business Impact

Modern e-commerce enterprises face four core operational challenges:
1. **Understanding the Voice of Customer (VoC):** Coarse 1–5 star ratings hide actionable reasons for returns. Enterprises need to extract *which specific hardware or service aspects* (`battery`, `camera`, `display`, `performance`, `quality`, `price`, `comfort`, `durability`, `delivery`, `packaging`, `design`) drive dissatisfaction.
2. **Personalization & Retention:** Recommending the right product to the right customer at the right lifecycle stage with transparent explainability, while gracefully resolving cold-start customers.
3. **Commercial Discrepancy Discovery:** Pinpointing high-risk products (*High Sales Volume + Poor Customer Sentiment*, which inflate returns and churn) and capitalizing on hidden growth opportunities (*Low Sales + Stellar Sentiment*).
4. **Universal Data Adaptability:** Allowing executive stakeholders, analysts, and operators to drag-and-drop any external CSV, Excel workbook, ZIP archive, or directory of relational files, and immediately auto-generate full ML diagnostics and executive briefing suites without inventing placeholder numbers.

---

## 2. End-to-End System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATA INGESTION & DISCOVERY                                    │
├────────────────────────────────────────┬────────────────────────────────────────────────────────┤
│ Default E-Commerce Demo Store          │ Custom Data Ingestion Hub                              │
│ • Customers (200)     • Products (50)  │ • Single CSV / Excel (.xlsx, .xls)                     │
│ • Orders (1,000)      • Reviews (200)  │ • Multi-File Simultaneous Upload & Inventory Tracker   │
│ • Interactions (3,000)                 │ • ZIP Archive Auto-Extraction (Size/Member Guarded)    │
│ • Real-World NLP Corpus (28,598)       │ • Local Folder Directory Scanner (Allowlist Guarded)   │
│   (Scale configurable in config.yaml)  │ • Auto-Join Relational Tables on Unique Shared Keys    │
│                                        │ • 12 Enterprise Industry Templates across 5 Verticals  │
└────────────────────────────────────────┴────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           SCHEMA DETECTION & DATA CLEANING ENGINE                               │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Automated Modality Detection: Reviews/VoC, Commercial Transactions, Customer RFM, Tabular     │
│ • Controlled Anomaly Cleansing: Segment-median age imputation, primary-key deduplication        │
│ • Transaction Math Validation: total_amount = (quantity * unit_price) - discount_amount         │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                 ┌──────────────────────────┴──────────────────────────┐
                 ▼                                                     ▼
┌──────────────────────────────────────────────┐     ┌──────────────────────────────────────────────┐
│          NLP & TOPIC INTELLIGENCE            │     │          RECOMMENDATION SYSTEMS              │
├──────────────────────────────────────────────┤     ├──────────────────────────────────────────────┤
│ • Vectorized TF-IDF Soft-Voting Ensemble     │     │ • Strategy 1: Popularity (Bayesian Prior)    │
│   (LogReg + MultinomialNB + ComplementNB)    │     │ • Strategy 2: Content-Based (TF-IDF Cosine)  │
│ • 11-Aspect Sentiment Extraction (ABSA)      │     │ • Strategy 3: SVD Collaborative Filtering    │
│   with Pre-Compiled Regex & Negation Window  │     │ • Strategy 4: Hybrid Ensembling (Weighted)   │
│ • NMF Unsupervised Complaint Topic Modeling  │     │ • Dynamic Cold-Start Transition Logic        │
│ • Positive Praises & Friction Quotes Sieve   │     │ • Explainable AI Rationale Generation        │
└──────────────────────────────────────────────┘     └──────────────────────────────────────────────┘
                 │                                                     │
                 └──────────────────────────┬──────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              ACTIVE DATASET MANAGER & CACHING LAYER                             │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Global State Synchronization across all pages (Main, Overview, Customers, SKUs, NLP, Recs)    │
│ • Strict Groundedness: Missing columns display as "N/A" (zero invented fallback metrics)        │
│ • File & Archive Parser Caching (@st.cache_data keyed by SHA-256 content/directory signature)   │
│ • Lazy On-Demand Report Generation (_GLOBAL_EXPORT_CACHE + session_state invalidation)          │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                 ┌──────────────────────────┴──────────────────────────┐
                 ▼                                                     ▼
┌──────────────────────────────────────────────┐     ┌──────────────────────────────────────────────┐
│            PRESENTATION & EXPORT             │     │               API & DATABASE                 │
├──────────────────────────────────────────────┤     ├──────────────────────────────────────────────┤
│ • Streamlit Multi-Page Application (8 Pages) │     │ • FastAPI High-Performance REST API (8 Routes│
│ • Plotly Interactive Dashboards              │     │ • Optional X-API-Key Security & CORS Control │
│ • 1-Click Downloads (HTML/PDF, Excel, MD, CSV│     │ • SQLite Database (`data/ecommerce.db`)      │
│ • 6-Page Interactive Power BI HTML Mockup    │     │ • PostgreSQL Schema & Star-Schema Views/XLSX │
└──────────────────────────────────────────────┘     └──────────────────────────────────────────────┘
```

---

## 3. Key Features & Capabilities

### 🧠 Natural Language Processing & 11-Aspect ABSA
- **Vectorized ML Classification:** TF-IDF (1–2 n-grams, sublinear TF scaling) + Soft-Voting Ensemble (`LogisticRegression`, `MultinomialNB`, `ComplementNB`) classifying sentiment polarities (*Positive*, *Neutral*, *Negative*), combined with vectorized `clean_text_series` preprocessing.
- **11-Aspect Review Extraction with Negation-Window Polarity Inversion:** Evaluates `battery`, `camera`, `display`, `performance`, `quality`, `price`, `comfort`, `durability`, `delivery`, `packaging`, and `design` using pre-compiled regular expressions and a 2-token negation window (accurately flipping phrases like *"battery is not good"* to Negative and *"no lag"* to Positive).
- **Aspect-Calibrated Sentiment Prediction:** Single-review inference (`SentimentPredictor.predict`) calibrates class probabilities using extracted aspect polarities to handle compound multi-aspect reviews.
- **Voice of Customer Extraction:** Automatically surfaces verbatim positive praises and critical customer friction complaints.

### 🎯 Multi-Strategy Recommender Systems
- **4 Models:** Popularity Baseline (Bayesian rating adjustment excluding returned orders), Content-Based (TF-IDF cosine similarity over catalog metadata), Collaborative Filtering (`TruncatedSVD` matrix factorization with `TfidfTransformer` scaling), and Hybrid Ensemble.
- **Explainable AI:** Every recommendation includes a transparent human-readable reason derived from the dominant model signal.
- **Cold-Start Fallback:** Handles new users and sparse interaction profiles gracefully by transitioning weights toward category-aware popularity and content similarity.

### 👥 360-Degree Customer Intelligence & RFM
- **Behavioral RFM Clusters:** Quantile-based Recency, Frequency, and Monetary scoring assigning customers to segments (*Champions / High Value*, *Loyal Customers*, *Promising / New*, *Regular*, *At Risk / Needs Attention*, *Hibernating / Inactive*).
- **Customer 360 Explorer:** Detailed drill-down for each customer including lifetime net spend, AOV, order frequency, return rate, loyalty tier, and preferred catalog category.

### 📦 Commercial Product Intelligence & Anomaly Sieve
- **SKU Catalog Matrix:** Real-time visibility into units sold, total orders, net revenue, average ratings, returned units, and return rates.
- **Anomaly Detection:** Identifies **High Sales Volume + Poor Sentiment** (top quartile sales volume + bottom quartile ratings with $\ge 5$ reviews) and **Low Sales Volume + Stellar Sentiment** (below-median sales + top quartile ratings with $\ge 3$ reviews).

---

## 4. Universal Ingestion Engine & Auto-Dashboard

The platform features a **Custom Data Analyzer & Ingestion Hub** (`app/pages/custom_data_analyzer.py`) that accepts any external tabular data through 4 flexible ingestion pathways:

1. **📋 Enterprise Business Templates:** Load any of 12 pre-configured industry schemas with 1-click synthetic sample data or download blank CSV templates.
2. **📄 Single File Upload:** Upload any `.csv`, `.xlsx`, or `.xls` file. The engine caches parsed tables by SHA-256 content hash, auto-detects column schemas, and generates the dashboard.
3. **🗂️ Multi-File Batch & ZIP Archive Ingestion:** Upload multiple CSV/Excel files simultaneously or a compressed `.zip` archive (guarded against zip bombs with a 100-file and 200 MB uncompressed limit). Presents a file inventory table and lets you concatenate homogeneous files (tracking provenance via `_source_file`) or auto-join relational tables.
4. **📁 Local Directory Scanner:** Scan any folder inside `data/` (or directories explicitly permitted in `LOCAL_SCAN_ROOTS`). Keyed by directory metadata signature (`name`, `size`, `mtime`) for zero-overhead cache hits.

### Relational Table Auto-Joining
When multiple relational tables are loaded, `auto_join_relational_tables()` automatically checks for shared keys (`customer_id`, `order_id`, `transaction_id`, `product_id`, `sku`, `review_id`) and left-joins lookup tables onto the largest fact table **only when the join key is unique in the lookup table**, preventing accidental row multiplication.

---

## 5. 12 Pre-Built Enterprise Business Templates

The platform bundles **12 enterprise industry datasets** (`src/analytics/templates.py`) across 5 business domains, ready for 1-click loading from the left sidebar or the Custom Data Analyzer:

| # | Template ID | Template Name | Domain Category | Standard Schema Columns |
|:---:|:---|:---|:---|:---|
| **1** | `product_reviews` | **Customer Product Reviews & VoC** | Voice of Customer & NLP | `review_id`, `product_name`, `rating`, `review_text`, `verified_purchase`, `review_date` |
| **2** | `support_tickets` | **Customer Support Tickets & Helpdesk** | Voice of Customer & NLP | `ticket_id`, `ticket_date`, `customer_id`, `channel`, `priority`, `resolution_time_hrs`, `customer_feedback`, `satisfaction_score` |
| **3** | `retail_transactions` | **Retail Sales & Order Transactions** | Commerce & Sales | `order_id`, `order_date`, `customer_id`, `product_name`, `category`, `quantity`, `unit_price`, `total_amount`, `return_status` |
| **4** | `subscription_churn` | **Subscription & Recurring SaaS Churn** | Commerce & Sales | `subscription_id`, `customer_id`, `plan_tier`, `mrr_amount`, `signup_date`, `tenure_months`, `churn_status`, `exit_feedback` |
| **5** | `customer_rfm` | **Customer RFM & Loyalty Profiles** | Customer Intelligence | `customer_id`, `customer_name`, `signup_date`, `total_orders`, `lifetime_spend`, `last_order_date`, `loyalty_tier` |
| **6** | `cart_abandonment` | **Shopping Cart Abandonment & Funnel** | Customer Intelligence | `session_id`, `customer_id`, `cart_value`, `items_in_cart`, `dropoff_stage`, `abandon_reason`, `device`, `session_date` |
| **7** | `inventory_health` | **Product Catalog & Inventory Intelligence** | Supply Chain & Logistics | `sku`, `product_name`, `category`, `cost_price`, `selling_price`, `stock_quantity`, `units_sold_30d`, `return_rate_pct` |
| **8** | `shipping_logistics` | **Shipping Logistics & Carrier SLA** | Supply Chain & Logistics | `tracking_id`, `order_id`, `carrier`, `origin_warehouse`, `destination_city`, `shipping_cost`, `transit_days`, `delivery_status`, `dispatch_date` |
| **9** | `product_returns` | **Product Returns & Reverse Logistics** | Supply Chain & Logistics | `return_id`, `order_id`, `sku`, `product_name`, `category`, `return_reason`, `refund_amount`, `restockable`, `return_date` |
| **10** | `marketing_campaigns` | **Marketing & Ad Campaign Performance** | Marketing & Growth | `campaign_id`, `campaign_name`, `channel`, `ad_spend`, `impressions`, `clicks`, `conversions`, `roas`, `campaign_date` |
| **11** | `promotions_discounts` | **Discounts & Promotion Effectiveness** | Marketing & Growth | `promo_code`, `discount_type`, `discount_value`, `redemptions_count`, `gross_revenue_driven`, `discount_cost`, `net_margin_pct`, `promo_month` |
| **12** | `web_traffic` | **Web Traffic & Digital Clickstream** | Marketing & Growth | `session_id`, `visitor_id`, `traffic_source`, `landing_page`, `pages_viewed`, `session_duration_sec`, `device_type`, `converted`, `session_date` |

---

## 6. Platform-Wide Reactivity & Modality Adaptation

### 🌐 Platform-Wide Synchronization
When you upload a dataset or select an enterprise template, the **entire application synchronizes**:
- **Main Executive Portal (`app/main.py`) & Executive Overview (`app/pages/overview.py`):** Share a unified dashboard component (`app/components/dashboards.py`) that switches between commercial scorecards and Voice-of-Customer (VoC) intelligence based on active dataset modalities.
- **Customer Intelligence (`app/pages/customer_intelligence.py`):** Adapts customer profiles and RFM value scatter matrices.
- **Product Intelligence (`app/pages/product_intelligence.py`):** Reflects catalog SKUs, sales-vs-rating matrices, and discrepancy flags of the active dataset.
- **NLP Review Voice (`app/pages/nlp_insights.py`):** Calculates 11-aspect satisfaction bars and extracts verbatim positive praises and critical friction quotes from the active dataset.
- **Personalized Recommendations (`app/pages/recommendations.py`):** Uses behavioral history from the demo store and clearly informs the user when a custom dataset without interaction history is active.

### 🎯 Intelligent Modality Adaptation & Strict Groundedness
The platform inspects the active dataset's mapped columns and adapts presentation without ever inventing numbers:

| Detected Modality | Displayed Scorecards | Primary Visualizations |
|---|---|---|
| **Voice of Customer (VoC)** *(e.g. Reviews)* | Feedback Volume, Customer Satisfaction (★), Positive %, Negative Friction %, Net Sentiment Score (NSS) | Sentiment Donut, 11-Aspect Satisfaction Bar Chart, Aspect Polarity Table, Praises & Friction Quotes |
| **Commercial Transactions** *(e.g. Sales)* | Total Net Revenue (with computed MoM delta), Total Orders, Average Order Value, Overall Return Rate %, Customer Satisfaction | Revenue Trend Over Time, Category Sales Bar Chart, Segment Distribution Donut, Top Revenue Products Table |
| **Hybrid / Full Store** *(e.g. Default Demo)* | Combined Commercial Health + Customer Voice KPIs | Revenue Trends, Category Performance, Aspect Satisfaction, Customer RFM |

> [!NOTE]
> Metrics not supported by the active dataset (such as Net Revenue on a review-only dataset, or Recency when no date column is present) are rendered as `N/A` via `src/utils/formatting.py`.

---

## 7. Universal 1-Click Dashboard Downloads

Every page on the platform features a **1-Click Download Suite** in both the top active-dataset banner and the left sidebar, building exports lazily on demand in 4 enterprise formats:

1. **📄 Executive Intelligence Report (`.html` / Printable PDF):** Self-contained, responsive briefing document styled with `@media print` CSS and full HTML escaping (`html.escape`) for security. Includes commercial KPIs, category revenue distribution, NLP aspect scorecards, RFM segment breakdowns, and threshold-driven strategic recommendations.
2. **📊 Multi-Tab Analytical Workbook (`.xlsx`):** Sanitized against illegal OpenXML control characters (`ILLEGAL_CHARACTERS_RE`), containing:
   - `Executive_Summary`: High-level business scorecards, record counts, and timestamps.
   - `Enriched_Dataset`: First 2,500 rows with ML sentiment predictions, confidence scores, and aspect tags.
   - `Monthly_Revenue_Trends`: Time-series revenue and order counts (when date and revenue are present).
   - `Category_Sales` & `Top_Products`: Category breakdowns and top SKU rankings.
   - `Aspect_Sentiment`: 11-Aspect polarity scores and mention counts.
   - `RFM_Customer_Segments` & `RFM_Segment_Totals`: Customer-level RFM scores and segment summaries.
3. **📝 Executive Briefing (`.md`):** Clean Markdown briefing document with KPI bullets, Markdown tables for Category Revenue, Aspect Satisfaction, and RFM Segments, plus strategic recommendations.
4. **📁 Enriched Dataset (`.csv`):** Complete 100% source dataset augmented with `predicted_sentiment`, `sentiment_confidence`, `sentiment_source`, and `extracted_aspects`.

---

## 8. High-Performance Caching & Sub-Second Optimization

1. **File & Archive Parser Caching (`src/analytics/multi_file_loader.py`):** `parse_tabular_file_cached`, `load_zip_archive_cached`, and `scan_local_directory_cached` use `@st.cache_data` keyed by SHA-256 content hashes or directory mtime/size signatures so Streamlit reruns never re-parse unchanged files.
2. **Vectorized Text Preprocessing (`src/nlp/preprocessing.py`):** `clean_text_series()` performs vectorized Pandas string transformations equivalent to `clean_text()`, accelerating batch review preprocessing by ~3x.
3. **Pre-Compiled Regex ABSA (`src/nlp/aspect_extraction.py`):** Aspect keyword boundaries and clause tokenizers are pre-compiled at module import time.
4. **Signature Memoization (`_analyzer_cache_sig`):** The Custom Data Analyzer reuses computed ML enrichments and RFM aggregations whenever the dataset signature and column mappings are unchanged, and replaces multi-tab rendering (`st.tabs`) with a single-selection segmented control so only the visible view is rendered.
5. **Lazy On-Demand Export Generation (`get_active_export_data`):** Export formats (`html`, `excel`, `md`, `csv`) are generated only when requested and cached in `_GLOBAL_EXPORT_CACHE` (keyed by dataset + column mapping hash, ensuring thread-safe downloads and automatic invalidation when column mappings change).

---

## 9. Project Directory Structure

```text
ecommerce-customer-intelligence/
│
├── config/
│   └── config.yaml               # Central configuration (scale, seed, weights, paths, 11 aspects)
│
├── data/
│   ├── raw/                      # Raw synthetic datasets + real_world_reviews.csv (28,598 rows)
│   ├── processed/                # Cleaned analytical tables + review_aspects.csv
│   ├── powerbi_export/           # Star-schema CSV exports + Ecommerce_Star_Schema.xlsx
│   └── ecommerce.db              # SQLite relational database
│
├── exports/                      # Auto-saved executive HTML, Excel, Markdown, and CSV reports
│
├── notebooks/
│   ├── 01_eda_and_data_cleaning.ipynb
│   ├── 02_nlp_sentiment_aspects.ipynb
│   └── 03_recommendation_and_evaluation.ipynb
│
├── src/
│   ├── utils/                    # Config parser, display formatters (fmt_money, fmt_pct), logging
│   ├── data/                     # Ingestion, schema/FK/math validation, and cleaning pipelines
│   ├── features/                 # RFM scoring and sparse CSR interaction matrix builders
│   ├── nlp/                      # Preprocessing, sentiment training/prediction, ABSA, NMF topics
│   ├── recommendation/           # Popularity, Content, Collaborative, Hybrid, and Evaluation
│   ├── analytics/                # Customer RFM, product performance, auto-analyzer, templates
│   │   ├── auto_analyzer.py      # Schema detection, batch NLP, custom RFM, table profiling
│   │   ├── business_metrics.py   # Executive KPIs, monthly trends, MoM growth, category stats
│   │   ├── customer_analytics.py # Customer 360 profiling, RFM segment aggregation
│   │   ├── multi_file_loader.py  # Cached CSV/Excel/ZIP/folder ingestion & relational auto-join
│   │   ├── product_analytics.py  # SKU matrix & discrepancy discovery (High Sales / Low Rating)
│   │   ├── report_generator.py   # Multi-tab Excel, HTML/PDF, and Markdown report builders
│   │   └── templates.py          # 12 pre-built enterprise business templates across 5 domains
│   └── database/                 # SQLite manager (memory journal pragma) & star-schema exporter
│
├── models/
│   ├── sentiment/                # Soft-Voting Ensemble model, TF-IDF vectorizer & metrics JSON
│   ├── recommendation/           # SVD collaborative, content similarity, and popularity models
│   ├── topic/                    # NMF topic model, vectorizer, and topic_summaries.json
│   └── evaluation_metrics.json   # Time-aware offline evaluation benchmark results
│
├── sql/
│   ├── schema.sql                # SQLite relational DDL with foreign keys and indexes
│   ├── postgres_schema.sql       # PostgreSQL DDL with foreign key cascades
│   ├── analytical_queries.sql    # 5 complex analytical SQL queries (CTEs, Window functions)
│   ├── powerbi_views.sql         # Star-schema Fact and Dimension view definitions
│   └── load_to_postgres.py       # PostgreSQL one-command loader script
│
├── powerbi/
│   ├── README.md                 # Power BI data model guide and page layout specifications
│   ├── dax_measures.md           # 16 production-grade enterprise DAX measures
│   └── powerbi_report_mockup.html# Standalone interactive 6-page Power BI web application
│
├── app/
│   ├── main.py                   # Streamlit multi-page orchestrator & 8-module Executive Landing
│   ├── components/               # Custom CSS styles, HTML-escaped KPI cards, Plotly charts, dashboards
│   ├── services/                 # Active dataset manager, cached data loaders, model inference
│   └── pages/                    # 8 modular Streamlit pages
│       ├── overview.py           # Executive Overview & MoM growth trends
│       ├── customer_intelligence.py # Customer RFM segmentation & 360 profiling
│       ├── product_intelligence.py  # SKU catalog, discrepancy discovery, TF-IDF similar items
│       ├── nlp_insights.py       # 11-aspect radar, sentiment breakdown, NMF topics
│       ├── recommendations.py    # Multi-strategy recommendations with explainability
│       ├── custom_data_analyzer.py  # Universal Ingestion Hub & 4-View Auto-Dashboard
│       ├── live_analyzer.py      # Interactive real-time review sentiment & aspect analyzer
│       └── model_benchmarks.py   # Offline recommendation benchmarks & NLP classification metrics
│
├── api/
│   ├── main.py                   # FastAPI application with X-API-Key security & CORS control
│   ├── dependencies.py           # Dependency injection
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── routes/                   # Route controllers (customers, products, recs, reviews)
│   └── services/                 # Singleton APIService decoupling business & ML logic
│
├── tests/                        # 97 automated test cases across 10 test modules (100% pass rate)
├── run_pipeline.py               # Single command to execute full end-to-end pipeline
├── requirements.txt
├── requirements.lock.txt
├── pyproject.toml
├── pyrightconfig.json
├── CHANGELOG.md
└── README.md
```

---

## 10. Dataset & Data Dictionary

### Default Demo Store Tables (`config/config.yaml`)
The bundled demo store is configured for rapid execution (`200` customers, `50` products, `1,000` transactions, `200` store reviews, `3,000` interactions), paired with `28,598` real-world reviews in `data/raw/real_world_reviews.csv` for NLP model training. You can scale the synthetic store to any size by adjusting `data_generation` in `config/config.yaml` and running `python run_pipeline.py`.

#### Customers (`data/processed/customers.csv` — 200 records)
| Column | Type | Description |
|:---|:---|:---|
| `customer_id` | String (PK) | Unique customer ID (e.g. `CUST_00001`) |
| `gender` | String | Demographic gender (`Female`, `Male`, `Non-Binary`) |
| `age` | Integer | Customer age (18 to 75; missing values imputed by segment median) |
| `city` / `country` | String | Residence location across 10 global cities |
| `membership_type` | String | Loyalty tier (`Bronze`, `Silver`, `Gold`, `Platinum`) |
| `signup_date` | Date | Account creation date |
| `customer_segment` | String | Behavioral cohort (`High Value`, `Regular`, `Occasional`, `Discount Sensitive`, `At Risk`, `New Customer`) |
| `preferred_category` | String | Historical product category preference |

#### Products (`data/processed/products.csv` — 50 records)
| Column | Type | Description |
|:---|:---|:---|
| `product_id` | String (PK) | Unique product SKU (e.g. `PROD_0001`) |
| `product_name` | String | Branded product title |
| `category` / `subcategory` | String | Catalog taxonomy across 7 categories (`Electronics`, `Sports`, `Home & Kitchen`, `Clothing`, `Accessories`, `Beauty`, `Books`) |
| `brand` | String | Manufacturing brand |
| `price` | Float | Unit price in USD ($12.99 to $1,199.99) |
| `product_description` | Text | Descriptive metadata used for TF-IDF content similarity |

#### Transactions (`data/processed/transactions.csv` — 1,000 records)
| Column | Type | Description |
|:---|:---|:---|
| `transaction_id` | String (PK) | Order transaction identifier (`TXN_000001` to `TXN_001000`) |
| `customer_id` | String (FK) | Linkage to customer |
| `product_id` | String (FK) | Linkage to product SKU |
| `transaction_date` | Timestamp | Completion timestamp (`2023-01-01` to `2024-12-31`) |
| `quantity` | Integer | Units ordered (1 to 4) |
| `unit_price` | Float | Price per unit at purchase |
| `discount_percentage` | Float | Applied promotional discount (0% to 20%) |
| `discount_amount` | Float | Calculated promotional savings |
| `total_amount` | Float | Net realized transaction amount |
| `payment_method` | String | `Credit Card`, `PayPal`, `Debit Card`, `Apple Pay`, `Gift Card` |
| `return_status` | String | `Completed`, `Returned`, `Pending` |

#### Reviews (`data/processed/reviews.csv` — 200 records & `data/raw/real_world_reviews.csv` — 28,598 records)
| Column | Type | Description |
|:---|:---|:---|
| `review_id` | String (PK) | Review identifier |
| `customer_id` / `product_id`| String (FK) | Review author and target item |
| `review_date` | Timestamp | Review submission timestamp |
| `rating` | Integer | Star rating (1 to 5) |
| `review_text` | Text | Natural language customer review text |

#### Interactions (`data/processed/interactions.csv` — 3,000 records)
| Column | Type | Description |
|:---|:---|:---|
| `interaction_id` | String (PK) | Event stream key |
| `customer_id` / `product_id`| String (FK) | User and item linkage |
| `interaction_type` | String | `view` (1.0), `click` (2.0), `wishlist` (3.0), `cart` (4.0), `purchase` (5.0) |
| `timestamp` | Timestamp | Chronological event time used for temporal train/test split |
| `session_id` | String | Browsing session identifier |

---

## 11. Data Cleaning & Quality Pipeline

The data cleaning and validation pipeline (`src/data/cleaning.py`, `src/data/validation.py`) enforces production-grade quality rules:
1. **Missing Age Imputation:** Imputes missing customer ages using the non-null median age within that customer's behavioral segment (with global median fallback).
2. **Primary Key Deduplication & Accurate Audit Reporting:** Eliminates duplicate primary keys across all tables and tracks post-deduplication filter counts (`empty_reviews_filtered`, `invalid_types_filtered`) without double-counting removed duplicates.
3. **Taxonomy Normalization:** Strips irregular casing and whitespace to enforce canonical category taxonomies.
4. **Referential Integrity & Mathematical Enforcement:** Validates foreign keys across `transactions`, `reviews`, and `interactions` against `customers` and `products`, and enforces exact transaction arithmetic:
   $$\text{discount\_amount} = \text{round}\left(\text{quantity} \times \text{unit\_price} \times \frac{\text{discount\_percentage}}{100}, 2\right)$$
   $$\text{total\_amount} = \text{round}\left(\text{quantity} \times \text{unit\_price} - \text{discount\_amount}, 2\right)$$

---

## 12. NLP & 11-Aspect Sentiment Extraction (ABSA)

### Review Sentiment Classification (`src/nlp/sentiment_train.py`, `src/nlp/sentiment_predict.py`)
- **Partitioning:** Stratified 80/20 train/test split.
- **Model:** Soft-voting ensemble of Logistic Regression (`C=3.5`), Multinomial Naive Bayes (`alpha=0.3`), and Complement Naive Bayes (`alpha=0.4`) with weights `1 : 2 : 1`.
- **Vectorizer:** Sublinear TF-IDF (1–2 n-grams, up to 12,000 features), fit strictly on the training partition to prevent data leakage.
- **Training Data:** Authentic e-commerce reviews in `data/raw/real_world_reviews.csv` (28,598 reviews: 22,878 train, 5,720 test). Star ratings map to labels: 1–2 `Negative`, 3 `Neutral`, 4–5 `Positive`.
- **Held-Out Test Performance (`models/sentiment/sentiment_metrics.json`):** **83.53% test accuracy** for both the Soft-Voting Ensemble and Logistic Regression (`82.33%` for Multinomial Naive Bayes baseline, `80.10%` for Complement Naive Bayes). Per-class F1: Positive `0.926`, Negative `0.680`, Neutral `0.405`.

### 11-Aspect ABSA Extraction (`src/nlp/aspect_extraction.py`)
Extracts fine-grained sentiment across **11 core product dimensions** (`config/config.yaml`):
`battery`, `camera`, `display`, `performance`, `quality`, `price`, `comfort`, `durability`, `delivery`, `packaging`, `design`.

- **Negation-Window Polarity Inversion:** Clauses are tokenized and scored with a 2-token lookbehind window for negation cues (`not`, `no`, `never`, `neither`, `barely`, `hardly`, `without`, `*n't`), flipping negated positive clues (e.g. *"not good"*, *"never bright"*) to negative and negated negative clues (e.g. *"no lag"*) to positive.
- **Observations Schema (`data/processed/review_aspects.csv` — 294 observations):**
  `review_id`, `product_id`, `aspect`, `sentiment` (`Positive`/`Neutral`/`Negative`), `sentiment_score` (`-1.0` to `+1.0`).

---

## 13. NMF Topic & Complaint Modeling

Non-Negative Matrix Factorization (`src/nlp/topic_modeling.py`) groups the 28,598 real-world reviews into 5 latent topics using TF-IDF (1–2 n-grams, stopword-filtered). Each topic is automatically labelled by its strongest words from the fitted model (`models/topic/topic_summaries.json`):

| Topic ID | Auto-Generated Topic Label | Top Keywords | Review Volume | Share (%) | Avg Rating |
|:---:|:---|:---|---:|---:|:---:|
| **0** | `top, size, small` | `top, size, small, like, fit, ordered, large, just` | 7,957 | 27.82% | 3.70★ |
| **1** | `dress, beautiful, love dress` | `dress, beautiful, love dress, flattering, beautiful dress, perfect` | 4,595 | 16.07% | 4.19★ |
| **2** | `love, love love, love top` | `love, love love, love top, love dress, top, absolutely` | 2,648 | 9.26% | 4.58★ |
| **3** | `good, product, quality` | `good, product, quality, use, works, great, easy, echo` | 5,731 | 20.04% | 3.43★ |
| **4** | `great, perfect, soft` | `great, perfect, soft, sweater, jeans, comfortable, wear, pants` | 7,667 | 26.81% | 4.55★ |

---

## 14. Personalized Recommendation Engines

The platform implements 4 recommendation strategies (`src/recommendation/`):

1. **Popularity Baseline (`popularity.py`):** Composite score = 70% normalized units sold (excluding returned transactions) + 30% Bayesian-smoothed average rating ($m = 5$ prior weight).
2. **Content-Based (`content_based.py`):** TF-IDF feature embeddings (1–2 n-grams, sublinear TF) on product category, subcategory, brand, title, and description with cosine similarity.
3. **Collaborative Filtering (`collaborative.py`):** `TruncatedSVD` Matrix Factorization ($k = 25$ latent factors) over the `TfidfTransformer`-scaled implicit user-item interaction matrix (`view=1.0`, `click=2.0`, `wishlist=3.0`, `cart=4.0`, `purchase=5.0`).
4. **Hybrid Ensemble (`hybrid.py`):** Weighted ensemble of Popularity ($0.45$), Collaborative ($0.35$), and Content ($0.20$) with Min-Max score normalization and automatic cold-start fallback.

### Recommendation Explainability (`explainability.py`)
Every recommendation is paired with a transparent rationale derived from the highest contributing signal:
- *"Customers with similar shopping and browsing behavior frequently chose this"* (Collaborative dominant)
- *"Matches your affinity for {Category} features based on your interaction history"* (Content dominant)
- *"Top-rated best-seller in {Category} with verified customer satisfaction"* (Popularity dominant)
- *"Trending top seller in {Category} popular among new members"* (Cold-Start fallback)

---

## 15. Offline Evaluation & Mathematical Benchmarks

To eliminate temporal data leakage (`src/recommendation/evaluation.py`), the interaction stream is split chronologically:
- **Train Window:** Earliest 80% of interaction events (`2,400` interactions prior to cut-off `2024-08-17 06:14:28`). Transactions and reviews are strictly filtered to dates before `2024-08-17 06:14:28` before fitting any model.
- **Test Window:** Most recent 20% of events (`600` interactions, evaluated across `79` held-out customers with high-intent `purchase`, `cart`, or `wishlist` conversions).

### Benchmark Comparison (`models/evaluation_metrics.json`)

| Model Strategy | Precision@5 | Precision@10 | Recall@5 | Recall@10 | MAP@10 | NDCG@10 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Hybrid Model** | **0.0785** | 0.0532 | **0.3165** | 0.4156 | **0.2296** | **0.2844** |
| **Popularity Baseline** | 0.0734 | **0.0544** | 0.2954 | **0.4177** | 0.2220 | 0.2784 |
| **Content-Based** | 0.0203 | 0.0228 | 0.0802 | 0.1793 | 0.0695 | 0.0999 |
| **Collaborative Filtering** | 0.0203 | 0.0190 | 0.0759 | 0.1456 | 0.0517 | 0.0778 |

---

## 16. SQL Database & Complex Analytical Queries

Stored in SQLite (`data/ecommerce.db`) with a PostgreSQL schema and loader (`sql/load_to_postgres.py`). `DatabaseManager` (`src/database/db_manager.py`) rebuilds the database from `sql/schema.sql` on every pipeline run using filesystem-safe SQLite pragmas (`PRAGMA journal_mode = MEMORY; PRAGMA synchronous = OFF;`), verifying exact row counts against the processed CSVs.

### Key Analytical Queries (`sql/analytical_queries.sql`):
1. **Top Revenue Products & Return Rates:** Computes gross orders, units sold, net revenue, and return rate % using `DENSE_RANK() OVER (ORDER BY net_revenue DESC)` and `NULLIF` zero-division guards.
2. **Commercial Discrepancy Discovery:** Aggregates unit sales and review stats in separate CTEs (preventing join fan-out) and identifies products in the Top 25% of sales volume (`NTILE(4) = 4`) and Bottom 25% of ratings (`NTILE(4) = 1`).
3. **Monthly Category Revenue & MoM Growth:** Calculates month-over-month revenue growth per category using `LAG(monthly_revenue, 1) OVER (PARTITION BY category ORDER BY year_month ASC)`.
4. **Customer Spend Quintiles:** Uses `NTILE(5) OVER (ORDER BY total_spend DESC)` to quantify revenue concentration across customer tiers.
5. **Aspect Sentiment Satisfaction by Category:** Aggregates aspect occurrences by category to compute positive vs. negative complaint shares.

---

## 17. Power BI Star-Schema & DAX Measures

### Star Schema Architecture (`sql/powerbi_views.sql`)
- **Fact Tables:** `FactSales` (1,000 rows), `FactReviews` (200 rows), `FactInteractions` (3,000 rows).
- **Dimension Tables:** `DimCustomer` (200 rows), `DimProduct` (50 rows), `DimCategory` (7 rows), `DimDate` (731 rows covering 2023–2024).
- Automatically exported on every pipeline run as individual CSV files (`data/powerbi_export/*.csv`) AND as a consolidated multi-sheet Excel workbook (`data/powerbi_export/Ecommerce_Star_Schema.xlsx`).

### Interactive Mockup (`powerbi/powerbi_report_mockup.html`)
Open `powerbi/powerbi_report_mockup.html` in any browser to explore the 6-page interactive Power BI dashboard featuring dynamic Category, Customer Segment, and Year slicers grounded in the processed star-schema numbers.

---

## 18. Interactive Web Applications & Pages

Launch the multi-page Streamlit portal:
```bash
python -m streamlit run app/main.py
```

### 8 Modular Application Pages:
1. **🛍️ Main Landing Portal (`app/main.py`):** 8-module overview grid, active dataset banner, and shared executive dashboard.
2. **📈 Executive Overview (`app/pages/overview.py`):** Modality-aware business scorecards, MoM revenue trajectory, category performance, and segment share.
3. **👥 Customer Intelligence (`app/pages/customer_intelligence.py`):** Behavioral RFM segmentation table, customer value scatter matrix, and Customer 360 profile lookup.
4. **📦 Product Intelligence (`app/pages/product_intelligence.py`):** SKU catalog explorer, anomaly discrepancy discovery (High Sales/Low Sentiment & Hidden Gems), and TF-IDF similar product retrieval.
5. **🧠 NLP Customer Voice (`app/pages/nlp_insights.py`):** 11-aspect satisfaction chart, polarity leaderboard, NMF topic cards, and real customer praises and friction quotes.
6. **🎯 Personalized Recommendations (`app/pages/recommendations.py`):** Customer selector, strategy dropdown, and top-K recommendation cards with explainable AI rationale.
7. **📁 Custom Data Analyzer (`app/pages/custom_data_analyzer.py`):** Universal Ingestion Hub (12 templates, single/multi-file CSV/Excel, ZIP archives, local directory scanner) and 4-view auto-dashboard.
8. **✍️ Live Review NLP Analyzer (`app/pages/live_analyzer.py`):** Interactive real-time review sentiment classification, class probability breakdown, and 11-aspect extraction with quick presets.
9. **📊 Model Benchmarks (`app/pages/model_benchmarks.py`):** Offline recommender evaluation comparison table and NLP classification report.

---

## 19. FastAPI REST API Layer

Set `API_KEY` to require an `X-API-Key` header on every data endpoint. Set `CORS_ALLOW_ORIGINS` to configure allowed browser origins (default: `http://localhost:8501,http://127.0.0.1:8501`). Health and root checks stay open for liveness probes.

Start the FastAPI application:
```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger documentation is available at **`http://127.0.0.1:8000/docs`**.

### All 8 REST API Endpoints:
| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/` | Root service metadata and documentation link |
| `GET` | `/health` | Liveness health check (`{"status": "healthy"}`) |
| `GET` | `/analytics/kpis` | Executive commercial & sentiment KPI scorecards (`total_net_revenue`, `total_orders`, `average_order_value`, `overall_return_rate_pct`, `average_rating`, etc.) |
| `GET` | `/customers/{customer_id}` | Customer 360 profile, lifetime spend, AOV, return rate, and RFM segmentation |
| `GET` | `/products/{product_id}` | Product 360 performance profile, units sold, net revenue, return rate, and discrepancy flags |
| `GET` | `/products/{product_id}/similar?top_k=5` | Content-based semantically similar catalog products via TF-IDF cosine similarity |
| `GET` | `/products/{product_id}/sentiment` | Product sentiment distribution, review count, average rating, and top extracted aspect polarities |
| `GET` | `/recommendations/{customer_id}?strategy=hybrid&top_k=10` | Personalized Top-K recommendations (`hybrid`, `collaborative`, `content`, `popularity`) with explainable AI reasons |
| `POST` | `/reviews/analyze` | Real-time review sentiment classification, class probabilities, and 11-aspect sentiment extraction |

---

## 20. Installation & How to Run

### 📋 Prerequisites
- **Python**: Version 3.10 or higher (`python --version`)
- **Package Manager**: `pip`
- **Operating System**: Windows, macOS, or Linux (including Docker and WSL2)

### 🚀 Step-by-Step Installation

#### 1. Clone or Extract the Project & Navigate to Workspace
```bash
cd "E-commerce Customer Intelligence & Personalization Platform-1"
```

#### 2. Create and Activate a Virtual Environment (Recommended)
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux (Bash / Zsh):**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Full End-to-End Pipeline
Executes all 8 data science stages sequentially:
1. **Synthetic Data Generation**: Creates customer, product, transaction, review, and interaction datasets with controlled anomalies.
2. **Data Cleaning**: Imputes missing customer ages by segment median, eliminates duplicates, and verifies transaction math.
3. **Review Sentiment Modeling**: Trains the Soft-Voting Ensemble (`LogisticRegression` + `MultinomialNB` + `ComplementNB`) with TF-IDF on `real_world_reviews.csv`.
4. **Aspect-Based Sentiment Extraction (ABSA)**: Extracts granular polarities across 11 product dimensions with negation-window handling.
5. **NMF Topic Modeling**: Discovers latent discussion themes and customer friction clusters.
6. **Recommender Model Training**: Fits Popularity, TF-IDF Content, and TruncatedSVD Collaborative Filtering models.
7. **Offline Time-Aware Evaluation**: Computes chronological `Precision@K`, `Recall@K`, `MAP@K`, and `NDCG@K` without data leakage.
8. **Relational Database & Power BI Export**: Builds `data/ecommerce.db` and exports Star-Schema CSVs and `Ecommerce_Star_Schema.xlsx` in `data/powerbi_export/`.

```bash
python run_pipeline.py
```

---

## 21. Automated Testing Suite (97 Tests)

Run the full automated pytest suite:
```bash
python -m pytest -v
```

**Results: 97 passed (100% pass rate).**

### Test Coverage Breakdown:
| Test File | Tests | Functional Verification Area |
|:---|:---:|:---|
| `tests/test_active_dataset_manager.py` | 6 | Global state sync, bundle synthesis, VoC modality, report generation |
| `tests/test_analytics.py` | 2 | Executive KPIs, RFM quintile scoring, segment mapping |
| `tests/test_api.py` | 11 | FastAPI REST endpoints (`/analytics/kpis`, `/customers`, `/products`, `/recommendations`, `/reviews/analyze`), 404 handling |
| `tests/test_aspects.py` | 4 | Compound 11-aspect extraction, pricing/delivery clauses, 2-token negation-window polarity inversion |
| `tests/test_auto_analyzer.py` | 13 | 12 enterprise templates, schema detection, batch NLP, custom RFM, ZIP extraction, relational auto-join |
| `tests/test_cleaning.py` | 4 | Missing age imputation, duplicate removal, arithmetic alignment, post-dedup filter reporting |
| `tests/test_data.py` | 6 | Schema validation, duplicate PKs, foreign-key orphan detection, transaction math, full collection checks |
| `tests/test_fast_custom_analyzer.py` | 9 | SHA-256 parser caching, lazy on-demand exports, cache key invalidation, `clean_text_series` equivalence, `AppTest` UI verification, worker-thread download safety |
| `tests/test_nlp.py` | 4 | Contraction expansion, URL/special-character text cleaning, TF-IDF sentiment inference |
| `tests/test_recommendation.py` | 3 | Popularity top-K ordering, content-based similarity exclusion, hybrid cold-start fallback |
| `tests/test_regressions.py` | 35 | Zero invented values, leak-free chronological evaluation, Default Demo Store category export accuracy, HTML escaping, RFM subtitle accuracy, upload/folder security limits, API key auth, SQLite rebuild integrity |

---

## 22. Engineering Decisions & Design Rationale

1. **Why Vectorized TF-IDF + Soft-Voting Ensemble for Sentiment Analysis?** Provides sub-millisecond inference latency, zero GPU dependencies, and high interpretability, enabling 25,000+ reviews to be classified in under a second on standard CPU hardware while calibrating single-review predictions with localized 11-aspect polarities.
2. **Why a Hybrid Recommendation Architecture?** Collaborative Filtering (`TruncatedSVD`) captures latent behavioral co-occurrence, Content-Based (`TF-IDF` cosine similarity) resolves item-to-item catalog similarity, and Bayesian Popularity resolves cold-start users. Weighted ensembling delivers the highest held-out `NDCG@10` (`0.2844`).
3. **Why Time-Aware Recommender Evaluation?** Random cross-validation leaks future interactions into training. Splitting chronologically at `2024-08-17 06:14:28` and restricting transactions, reviews, and interactions to pre-cutoff history guarantees leak-free offline evaluation.
4. **Why Strict Groundedness (`N/A` over Invented Fallbacks)?** Executive analytics platforms must never fabricate numbers when a user uploads partial data. Any metric not supported by the uploaded schema is returned as `None` and rendered as `N/A`.
5. **Why Lazy On-Demand Exports & Signature Caching?** Streamlit re-executes scripts on widget interaction. Caching file parsing by SHA-256 hash, memoizing analysis by dataset/mapping signature, and generating export files (`HTML`, `XLSX`, `MD`, `CSV`) lazily on demand guarantees instantaneous UI responsiveness.
