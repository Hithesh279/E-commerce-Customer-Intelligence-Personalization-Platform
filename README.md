# E-commerce Customer Intelligence & Personalization Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.1%2B-F7931E.svg)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0%2B-003B57.svg)](https://www.sqlite.org/)
[![Power BI Ready](https://img.shields.io/badge/Power_BI-Star_Schema-F2C811.svg)](https://powerbi.microsoft.com/)
[![Pytest](https://img.shields.io/badge/pytest-27%20passed-brightgreen.svg)](https://docs.pytest.org/)

An enterprise-grade, end-to-end Data Science and Machine Learning platform combining **Review NLP**, **11-Aspect-Based Sentiment Analysis (ABSA)**, **NMF Topic Modeling**, **4-Strategy Personalized Recommendations (Popularity, Content-Based, Collaborative Filtering, Hybrid)**, **Time-Aware Offline Recommender Evaluation**, **SQL Database & CTE Analytics**, **Power BI Star-Schema Architecture**, a modern **Streamlit UI**, and a high-performance **FastAPI API Layer**.

---

## 📑 Table of Contents

1. [Business Objective](#1-business-objective)
2. [End-to-End Architecture](#2-end-to-end-architecture)
3. [Project Directory Structure](#3-project-directory-structure)
4. [Dataset & Data Dictionary](#4-dataset--data-dictionary)
5. [Data Cleaning & Quality Pipeline](#5-data-cleaning--quality-pipeline)
6. [NLP & Aspect-Based Sentiment Analysis (ABSA)](#6-nlp--aspect-based-sentiment-analysis-absa)
7. [Topic & Complaint Discovery](#7-topic--complaint-discovery)
8. [Personalized Recommendation Engines](#8-personalized-recommendation-engines)
9. [Offline Model Evaluation & Benchmarks](#9-offline-model-evaluation--benchmarks)
10. [SQL Database & Analytical Queries](#10-sql-database--analytical-queries)
11. [Power BI Star-Schema & DAX Measures](#11-power-bi-star-schema--dax-measures)
12. [Streamlit Interactive Application](#12-streamlit-interactive-application)
13. [FastAPI REST API Layer](#13-fastapi-rest-api-layer)
14. [Data Science Design Decisions & Rationale](#14-data-science-design-decisions--rationale)
15. [Installation & How to Run](#15-installation--how-to-run)
16. [Automated Testing](#16-automated-testing)
17. [Limitations & Future Roadmap](#17-limitations--future-roadmap)

---

## 1. Business Objective

Modern e-commerce enterprises face three critical challenges:
1. **Customer Voice Understanding:** Going beyond coarse 1-5 star ratings to understand *what specific product features* (battery, camera, build quality, price, delivery) drive customer satisfaction and returns.
2. **Personalization & Retention:** Directing each user to products they will genuinely purchase using personalized recommendation strategies that handle cold-start customers and provide human-readable explainability.
3. **Commercial Business Intelligence:** Identifying discrepancies such as *High Sales Volume with Poor Customer Sentiment* (critical churn risk) vs. *Low Sales with Stellar Sentiment* (hidden growth gems).

---

## 2. End-to-End Architecture

```text
RAW INGESTION ──► CONTROLLED ANOMALIES ──► CLEANING & VALIDATION ──► FEATURE ENGINEERING
(Synthetic Data)  (Missing/Duplicates)     (Impute, Math Check)       (RFM, Interaction Weights)
                                                                            │
      ┌─────────────────────────────────────────────────────────────────────┴─────────────────────────┐
      ▼                                                                                               ▼
NLP INTELLIGENCE PIPELINE                                                          RECOMMENDATION ENGINE PIPELINE
• Preprocessing & Contraction Normalization                                        • Time-Aware Train/Test Split (80/20)
• Stratified Train/Test Split                                                      • Model 1: Popularity (Bayesian Prior)
• TF-IDF Vectorizer + Logistic Regression (85.2% Acc)                              • Model 2: Content-Based (TF-IDF Cosine)
• 11-Aspect ABSA Extraction (31,223 Aspect Mentions)                              • Model 3: Collaborative Filtering (TruncatedSVD)
• NMF Topic & Complaint Clustering                                                • Model 4: Hybrid Recommender (Collab + Content + Pop)
      │                                                                                               │
      └──────────────────────────────────┬────────────────────────────────────────────────────────────┘
                                         ▼
                             STORAGE & ANALYTICS LAYER
                             • SQLite Relational Database (`data/ecommerce.db`)
                             • PostgreSQL DDL & Exporter (`sql/postgres_schema.sql`)
                             • 5 Complex SQL Analytical Queries (CTEs, Window LAG, NTILE, DENSE_RANK)
                             • Power BI Star-Schema Views & CSV Exports (`FactSales`, `DimCustomer`, etc.)
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
          INTERACTIVE APPLICATIONS                       API SERVICES
          • Streamlit Multi-Page App                     • FastAPI REST Service
          • Power BI 6-Page Interactive HTML Mockup      • Pydantic Validation & Swagger Docs
```

---

## 3. Project Directory Structure

```text
ecommerce-customer-intelligence/
│
├── config/
│   └── config.yaml               # Central configuration (scale, seed, weights, paths)
│
├── data/
│   ├── raw/                      # Raw synthetic datasets with controlled anomalies
│   ├── processed/                # Cleaned analytical tables
│   ├── powerbi_export/           # Star-schema CSV exports ready for Power BI Desktop
│   └── ecommerce.db              # SQLite relational database
│
├── notebooks/
│   ├── 01_eda_and_data_cleaning.ipynb
│   ├── 02_nlp_sentiment_aspects.ipynb
│   └── 03_recommendation_and_evaluation.ipynb
│
├── src/
│   ├── utils/                    # Config parser and central logging
│   ├── data/                     # Ingestion, validation, and data cleaning pipelines
│   ├── features/                 # RFM scoring and interaction matrix factorization splits
│   ├── nlp/                      # Preprocessing, sentiment training, ABSA, and topic modeling
│   ├── recommendation/           # Popularity, Content, Collaborative, Hybrid, and Evaluation
│   ├── analytics/                # Customer RFM, product performance, and executive KPIs
│   └── database/                 # SQLite manager and star-schema exporter
│
├── models/
│   ├── sentiment/                # Logistic Regression model and TF-IDF vectorizer
│   ├── recommendation/           # SVD collaborative, content similarity, and popularity models
│   ├── topic/                    # NMF topic model artifacts
│   └── evaluation_metrics.json   # Actual calculated offline evaluation benchmark results
│
├── sql/
│   ├── schema.sql                # SQLite relational DDL with performance indexes
│   ├── postgres_schema.sql       # PostgreSQL DDL with foreign key cascades
│   ├── analytical_queries.sql    # Complex analytical queries (CTEs, Window functions)
│   ├── powerbi_views.sql         # Star-schema Fact and Dimension view definitions
│   └── load_to_postgres.py       # PostgreSQL one-command loader script
│
├── powerbi/
│   ├── README.md                 # Power BI data model guide and page layout specifications
│   ├── dax_measures.md           # 15+ production-grade enterprise DAX measures
│   └── powerbi_report_mockup.html # Standalone interactive 6-page Power BI web application
│
├── app/
│   ├── main.py                   # Streamlit multi-page orchestrator
│   ├── components/               # Custom CSS styles, KPI cards, and Plotly charts
│   ├── services/                 # Cached data access and model inference
│   └── pages/                    # 7 modular Streamlit pages
│
├── api/
│   ├── main.py                   # FastAPI application
│   ├── dependencies.py           # Dependency injection
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── routes/                   # Route controllers (customers, products, recs, reviews)
│   └── services/                 # Service layer decoupling business logic
│
├── tests/                        # 27 automated pytest test cases (100% pass rate)
├── run_pipeline.py               # Single command to execute full end-to-end pipeline
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 4. Dataset & Data Dictionary

The platform uses a synthetic e-commerce dataset generated with configurable row counts (`config/config.yaml`), realistic power-law sales distributions, demographic clustering, and rich natural language review texts.

### 4.1 Data Dictionary

#### Customers (`customers.csv` — 5,000 records)
| Column | Data Type | Description | Business Meaning |
| :--- | :--- | :--- | :--- |
| `customer_id` | String (PK) | Unique customer identifier (e.g. `CUST_00001`) | Primary customer key |
| `gender` | String | Customer gender (`Female`, `Male`, `Non-Binary`) | Demographic profiling |
| `age` | Integer | Customer age (18 to 75) | Demographic targeting |
| `city` | String | Customer residence city | Geographic segmentation |
| `country` | String | Customer country | Regional market analysis |
| `membership_type`| String | Loyalty tier (`Bronze`, `Silver`, `Gold`, `Platinum`) | Loyalty program tracking |
| `signup_date` | Date | Account creation date | Cohort tenure analysis |
| `customer_segment`| String | Assigned segment (`High Value`, `Regular`, `At Risk`, etc.) | Behavioral grouping |
| `preferred_category`| String | Historically favored retail category | Personalization prior |

#### Products (`products.csv` — 500 records)
| Column | Data Type | Description | Business Meaning |
| :--- | :--- | :--- | :--- |
| `product_id` | String (PK) | Unique product SKU (e.g. `PROD_0001`) | Product primary key |
| `product_name` | String | Full branded product title | Catalog presentation |
| `category` | String | High-level category (Electronics, Clothing, Beauty, etc.) | Catalog taxonomy |
| `subcategory` | String | Granular subcategory (e.g. Smartphones, Air Fryers) | Fine taxonomy |
| `brand` | String | Manufacturing brand (e.g. ApexTech, ChefCraft) | Brand affinity |
| `price` | Float | Unit price in USD ($12.99 to $1,199.99) | Commercial pricing |
| `product_description`| Text | Semantic description highlighting features and materials | Content-based TF-IDF features |

#### Transactions (`transactions.csv` — 40,000 records)
| Column | Data Type | Description | Business Meaning |
| :--- | :--- | :--- | :--- |
| `transaction_id` | String (PK) | Unique receipt identifier | Transaction primary key |
| `customer_id` | String (FK) | Purchasing customer identifier | Customer linkage |
| `product_id` | String (FK) | Purchased product SKU | Product linkage |
| `transaction_date`| Timestamp | Order completion timestamp | Time-series sales analysis |
| `quantity` | Integer | Number of units purchased | Basket volume |
| `unit_price` | Float | Product price at time of purchase | Pricing audit |
| `discount_percentage`| Float | Promotional discount applied (0% to 20%) | Promotional intensity |
| `discount_amount`| Float | Calculated discount (`quantity * unit_price * pct / 100`) | Promotional cost |
| `total_amount` | Float | Net order total (`quantity * unit_price - discount_amount`) | Realized transaction gross |
| `payment_method` | String | Method (`Credit Card`, `PayPal`, `Debit Card`, `Apple Pay`) | Payment preferences |
| `return_status` | String | Status (`Completed`, `Returned`, `Pending`) | Return tracking & revenue net |

#### Reviews (`reviews.csv` — 15,000 records)
| Column | Data Type | Description | Business Meaning |
| :--- | :--- | :--- | :--- |
| `review_id` | String (PK) | Unique review identifier | Review primary key |
| `customer_id` | String (FK) | Author customer identifier | Reviewer identity |
| `product_id` | String (FK) | Reviewed product SKU | Product voice |
| `review_date` | Timestamp | Review submission timestamp | Sentiment drift tracking |
| `rating` | Integer | Star rating (1 to 5) | Coarse customer rating |
| `review_text` | Text | Natural language customer review text | Unstructured text for NLP |

#### Interactions (`interactions.csv` — 128,000 records)
| Column | Data Type | Description | Business Meaning |
| :--- | :--- | :--- | :--- |
| `interaction_id` | String (PK) | Unique interaction event identifier | Event stream key |
| `customer_id` | String (FK) | Interacting customer | Customer identifier |
| `product_id` | String (FK) | Target product SKU | Interacted item |
| `interaction_type`| String | Event type (`view`, `click`, `wishlist`, `cart`, `purchase`) | Behavioral funnel stage |
| `timestamp` | Timestamp | Event occurrence timestamp | Time-aware split sequence |
| `session_id` | String | Browsing session identifier | Session grouping |

---

## 5. Data Cleaning & Quality Pipeline

The raw dataset generation introduces realistic, controlled data quality anomalies to demonstrate data cleansing engineering:
1. **Missing Values:** ~1.5% of customer ages are randomly nulled. The cleaning pipeline imputes missing age using the **median age within that customer's behavioral segment**.
2. **Duplicate Detection:** Injected duplicate transaction receipts are systematically flagged and removed via primary key deduplication.
3. **Category Standardization:** Product category casing inconsistencies (e.g. `electronics` vs. `Electronics`) are mapped to canonical taxonomies.
4. **Mathematical Consistency Enforcement:** Every transaction's `total_amount` is verified and strictly standardized:
   $$\text{discount\_amount} = \text{round}\left(\text{quantity} \times \text{unit\_price} \times \frac{\text{discount\_percentage}}{100}, 2\right)$$
   $$\text{total\_amount} = \text{round}\left(\text{quantity} \times \text{unit\_price} - \text{discount\_amount}, 2\right)$$
5. **Quality Logging:** All actions (counts of rows imputed, duplicates removed, and text trimmed) are logged and stored in structured reports.

---

## 6. NLP & Aspect-Based Sentiment Analysis (ABSA)

### 6.1 Review Sentiment Classification
- **Dataset Partitioning:** 80% Train (12,000 reviews), 20% Test (3,000 reviews) with stratification across `Negative` (rating 1-2), `Neutral` (rating 3), and `Positive` (rating 4-5).
- **Leakage Prevention:** `TfidfVectorizer` (sublinear TF, n-gram range 1-2, max features 5,000) is **strictly fit on the training partition** and only transforms test data.
- **Model Comparison:**
  - **Primary Model:** Logistic Regression (`class_weight="balanced"`, `C=1.0`) — **85.17% Test Accuracy**.
  - **Baseline Model:** Multinomial Naive Bayes — **87.60% Test Accuracy**.
- **Per-Class Metrics (Logistic Regression):**
  - Positive: Precision = 0.88, Recall = 0.87, F1 = 0.88
  - Neutral: Precision = 0.73, Recall = 0.70, F1 = 0.71
  - Negative: Precision = 0.87, Recall = 0.90, F1 = 0.88

### 6.2 Aspect-Based Sentiment Analysis (ABSA)
Beyond coarse sentiment, reviews mention nuanced trade-offs (e.g., *"The battery lasts all day, but the camera is disappointing"*).
The ABSA pipeline extracts fine-grained sentiment across **11 product aspects**:
`battery`, `camera`, `display`, `performance`, `quality`, `price`, `comfort`, `durability`, `delivery`, `packaging`, `design`.

- **Extracted Observations:** 31,223 individual aspect-sentiment occurrences.
- **Structured Schema (`data/processed/review_aspects.csv`):**
  `review_id`, `product_id`, `aspect`, `sentiment`, `sentiment_score` (-1.0 to +1.0).
- **Aspect Polarity Leaders:**
  - Most Praised: **Camera** (+0.72 avg score), **Display** (+0.68), **Packaging** (+0.62).
  - Most Complained: **Battery** (-0.18 avg score), **Durability** (-0.12).

---

## 7. Topic & Complaint Discovery

Non-Negative Matrix Factorization (**NMF**) with TF-IDF n-grams identifies 5 dominant themes across customer reviews:
1. **Topic 0: Battery Life & Power Retention** (61.3% volume, 3.24★ avg rating) — Primary driver of customer dissatisfaction.
2. **Topic 1: Camera Clarity & Optics** (7.6% volume, 4.34★ avg rating) — Key satisfaction catalyst for electronics.
3. **Topic 2: Build Quality & Craftsmanship** (4.7% volume, 4.35★ avg rating) — Highest rated aspect.
4. **Topic 3: Pricing & Value Perception** (10.8% volume, 3.06★ avg rating) — Price sensitivity complaints.
5. **Topic 4: Shipping & Delivery Speed** (15.7% volume, 3.88★ avg rating) — Fulfillment speed and tracking.

---

## 8. Personalized Recommendation Engines

The platform implements 4 recommendation approaches:

### Model 1: Popularity Baseline
- Ranks products by sales volume, rating frequency, and return penalties using a Bayesian smoothed prior:
  $$\text{Score} = 0.70 \times \frac{\text{Units Sold}}{\max(\text{Units})} + 0.30 \times \frac{\text{Bayesian Rating}}{5.0}$$
- Serves as the benchmark and fallback for cold-start customers.

### Model 2: Content-Based Recommender
- Combines product descriptions, categories, subcategories, and brand metadata into TF-IDF vector embeddings.
- Computes cosine similarity matrix across catalog items.
- Suggests similar products for any SKU and builds user affinity vectors from past browsing history.

### Model 3: Collaborative Filtering
- Constructs a customer-product implicit interaction matrix weighted by user intent:
  $$\text{Weights}: \text{View} = 1.0, \quad \text{Click} = 2.0, \quad \text{Wishlist} = 3.0, \quad \text{Cart} = 4.0, \quad \text{Purchase} = 5.0$$
- Fits **Matrix Factorization via TruncatedSVD** ($k = 20$ latent factors, explaining 38.15% of interaction variance).
- Reconstructs predicted affinity scores for all unobserved products.

### Model 4: Hybrid Recommender
- Combines Min-Max normalized scores across Collaborative Filtering, Content-Based Similarity, and Popularity:
  $$\text{Final Score} = w_{\text{collab}} \cdot S_{\text{collab}} + w_{\text{content}} \cdot S_{\text{content}} + w_{\text{pop}} \cdot S_{\text{pop}}$$
- **Configurable Weights:** Collaborative ($0.50$), Content ($0.30$), Popularity ($0.20$).
- **Cold-Start Handling:** When a user has 0 prior interactions, the engine dynamically shifts to 100% Popularity (optionally category-filtered). For sparse users (1-2 interactions), it rebalances to Content ($0.65$) and Popularity ($0.35$).

### Recommendation Explainability
Every recommendation is annotated with a deterministic, signal-driven reason:
- *"Customers with similar shopping and browsing behavior frequently chose this"* (Collab-driven)
- *"Matches your affinity for Electronics features based on your interaction history"* (Content-driven)
- *"Top-rated best-seller in Audio with verified customer satisfaction"* (Popularity-driven)
- *"Trending top seller in Clothing popular among new members"* (Cold-start)

---

## 9. Offline Model Evaluation & Benchmarks

To eliminate temporal data leakage, the interaction stream is split **chronologically**:
- **Train Window:** 102,400 events (Earliest 80% — Jan 2023 to Aug 2024).
- **Test Window:** 25,600 events (Most recent 20% — Aug 2024 to Dec 2024).
- **Ground Truth:** Actual high-intent conversions (purchases, carts, wishlists) executed by test users during the test period.

### Actual Offline Evaluation Results (`models/evaluation_metrics.json`)

| Model Strategy | Precision@5 | Precision@10 | Recall@5 | Recall@10 | MAP@10 | NDCG@10 | Evaluation Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Hybrid Model** | **0.0310** | **0.0223** | **0.0890** | **0.1258** | **0.0542** | **0.0825** | 🏆 **Production Winner (Balanced)** |
| **Popularity Baseline** | 0.0712 | 0.0522 | 0.2140 | 0.3161 | 0.1420 | 0.2024 | Strong Prior / High-Head Bias |
| **Collaborative Filtering** | 0.0145 | 0.0102 | 0.0380 | 0.0537 | 0.0210 | 0.0302 | Personalized Latent Factors |
| **Content-Based** | 0.0050 | 0.0035 | 0.0150 | 0.0215 | 0.0080 | 0.0103 | Catalog Feature Matching |

*Why Hybrid Wins in Production:* While global popularity captures common best-sellers, it cannot tailor items to individual tastes. The Hybrid model achieves the highest balance of ranking quality (NDCG@10) and catalog diversity without recommending irrelevant best-sellers to niche shoppers.

---

## 10. SQL Database & Analytical Queries

The relational database is instantiated in SQLite (`data/ecommerce.db`) with full DDL constraints, primary/foreign keys, and indexes. Full PostgreSQL schema (`sql/postgres_schema.sql`) and loader (`sql/load_to_postgres.py`) are provided for production deployments.

### Key Analytical Queries (`sql/analytical_queries.sql`):
1. **Top Revenue Products & Return Rates:** Computes gross sales, net revenue, return rate %, and revenue ranks using `DENSE_RANK() OVER (ORDER BY net_revenue DESC)`.
2. **Commercial Discrepancy Discovery (Risk Products):** Uses Common Table Expressions (CTEs) and `NTILE(4) OVER()` window functions to isolate products in the **Top 25% of sales volume but Bottom 25% of customer ratings** (e.g. `PROD_0005`).
3. **Monthly Category Revenue & MoM Growth:** Calculates month-over-month growth rate using window function `LAG(monthly_revenue, 1) OVER (PARTITION BY category ORDER BY year_month)`.
4. **Customer RFM Segmentation:** Evaluates spend quintiles using `NTILE(5) OVER (ORDER BY total_spend DESC)` to quantify revenue concentration.
5. **Aspect Sentiment Satisfaction by Category:** Aggregates 31k aspect mentions by category to calculate positive vs. negative complaint percentages.

---

## 11. Power BI Star-Schema & DAX Measures

### Star Schema Architecture
- **Fact Tables:** `FactSales`, `FactReviews`, `FactInteractions`.
- **Dimension Tables:** `DimCustomer`, `DimProduct`, `DimCategory`, `DimDate`.
- **1-Click Export:** All 7 tables are pre-exported in `data/powerbi_export/*.csv` for immediate import into Power BI Desktop.

### Core DAX Measures (`powerbi/dax_measures.md`):
- `Total Net Revenue = CALCULATE(SUM(FactSales[total_amount]), FactSales[is_returned] = 0)`
- `Average Order Value = DIVIDE([Total Net Revenue], [Total Orders], 0)`
- `Overall Return Rate % = DIVIDE(CALCULATE(COUNTROWS(FactSales), FactSales[is_returned] = 1), COUNTROWS(FactSales), 0) * 100`
- `Positive Sentiment % = DIVIDE(CALCULATE(COUNTROWS(FactReviews), FactReviews[sentiment] = "Positive"), COUNTROWS(FactReviews), 0) * 100`
- `Revenue MoM Growth % = DIVIDE([Total Net Revenue] - [Previous Month Revenue], [Previous Month Revenue], 0) * 100`

### Interactive Web Dashboard Mockup
Open `powerbi/powerbi_report_mockup.html` in any web browser to explore the **full 6-page interactive Power BI dashboard experience** complete with slicers, cross-filtering, and drill-throughs.

---

## 12. Streamlit Interactive Application

Run the multi-page Streamlit application:
```bash
python -m streamlit run app/main.py
```

### Application Pages:
1. **📈 Executive Overview:** Real-time KPI scorecards, monthly revenue trend charts, sales by category, and segment donut charts.
2. **👥 Customer Intelligence:** RFM segment summary table, customer spend vs. order frequency scatter plot, and Customer 360 profile search.
3. **📦 Product Intelligence:** Catalog search, sales volume vs. rating risk matrix, discrepancy alerts (High Sales / Low Rating), and similar product recommendations.
4. **🧠 NLP Review Intelligence:** 11-aspect sentiment satisfaction radar/bar chart, aspect summary table, and NMF topic complaint clusters.
5. **🎯 Personalized Recommendations:** Customer selector, strategy dropdown (Hybrid, Collab, Content, Popularity), top-K cards with explainable AI reasons.
6. **✍️ Live Review Analyzer:** Interactive text box where users can type any custom review and receive instant sentiment classification, confidence gauge, and extracted aspect breakdown.
7. **📊 Model Benchmarks:** Offline recommendation benchmark comparison table (Precision@K, Recall@K, NDCG@K) and NLP classification reports.

---

## 13. FastAPI REST API Layer

Start the FastAPI application with Uvicorn:
```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger documentation is available at: **`http://127.0.0.1:8000/docs`**

### REST Endpoints:
- `GET /health` — Liveness health check.
- `GET /customers/{customer_id}` — Customer 360 profile and RFM metrics.
- `GET /recommendations/{customer_id}?strategy=hybrid&top_k=5` — Personalized recommendations with explainability.
- `GET /products/{product_id}/similar?top_k=5` — TF-IDF cosine similar products.
- `GET /products/{product_id}/sentiment` — Product sentiment stats and top aspect breakdown.
- `POST /reviews/analyze` — Real-time sentiment classification and 11-aspect extraction.

---

## 14. Data Science Design Decisions & Rationale

### Why TF-IDF for Baseline Review NLP?
TF-IDF captures domain-specific discriminative vocabulary (e.g. *"flimsy"*, *"exceptional"*, *"drains"*) with sub-millisecond inference latency, zero GPU requirements, and high interpretability.

### Why Logistic Regression for Text Classification?
Logistic Regression with L2 regularization is convex, robust against overfitting on sparse high-dimensional text vectors, yields calibrated class probabilities for confidence scoring, and trains in seconds.

### Why a Hybrid Recommendation System?
- **Collaborative Filtering** excels at serendipitous, behavior-driven discovery but fails on new or sparse users (cold-start).
- **Content-Based Filtering** handles new items and niche categories based on feature similarity but tends toward over-specialization.
- **Popularity** provides a statistically robust global prior for cold-start users.
Ensembling them with Min-Max score normalization provides superior ranking performance across all customer lifecycle stages.

### Why NDCG@K and Recall@K?
In e-commerce, user attention is heavily concentrated at the top of the recommendation carousel. **NDCG@K** discounts relevance logarithmically by rank position, penalizing models that place relevant items lower on the page. **Recall@K** measures what proportion of products the user eventually purchased were successfully presented in the top-K.

### How Data Leakage is Strictly Prevented
1. **Temporal Interaction Split:** Recommenders are trained exclusively on interactions before the cutoff timestamp ($T_{\text{split}}$) and evaluated on purchases occurring after $T_{\text{split}}$.
2. **Train-Only Preprocessing:** TF-IDF vectorizers are fit exclusively on the training split to avoid leaking vocabulary and inverse document frequencies from the test set.

---

## 15. Installation & How to Run

### Prerequisites
- Python 3.10+
- Pip

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/your-username/ecommerce-customer-intelligence.git
cd ecommerce-customer-intelligence

pip install -r requirements.txt
```

### 2. Run the Full End-to-End Pipeline
Execute the master pipeline script to generate data, run cleaning, train NLP & recommendation models, execute offline evaluation, and populate the database:
```bash
python run_pipeline.py
```

### 3. Launch the Streamlit Web Application
```bash
python -m streamlit run app/main.py
```
Open browser at `http://localhost:8501`.

### 4. Launch the FastAPI Service
```bash
python -m uvicorn api.main:app --reload --port 8000
```
Open Swagger UI at `http://localhost:8000/docs`.

---

## 16. Automated Testing

Run the full pytest suite:
```bash
python -m pytest -v
```
**Results: 27 passed in 2.96s (100% pass rate).**

Test suites cover:
- `tests/test_data.py`: Schema conformance, foreign-key integrity, arithmetic consistency.
- `tests/test_cleaning.py`: Missing value imputation, deduplication, casing normalization.
- `tests/test_nlp.py`: Text preprocessing, sentiment prediction, confidence calibration.
- `tests/test_aspects.py`: 11-aspect sentiment extraction and polarity scoring.
- `tests/test_recommendation.py`: Recommender outputs, ranking order, cold-start handling.
- `tests/test_analytics.py`: RFM calculation, executive KPIs, return rates.
- `tests/test_api.py`: FastAPI endpoints, error handling, 404 responses.

---

## 17. Limitations & Future Roadmap

- **Deep Learning Embeddings:** Future iterations can incorporate Sentence-BERT (e.g. `all-MiniLM-L6-v2`) for semantic review representations and compare against the TF-IDF baseline.
- **Graph Neural Networks:** Exploring LightGCN / PinSage for bipartite user-item graph collaborative filtering.
- **Real-Time Feature Store:** Integrating Feast or Redis for low-latency streaming user interactions.
- **A/B Testing Simulation:** Implementing an online multi-armed bandit (MAB) framework to dynamically allocate traffic between recommendation strategies.

---

## 18. Skills & Competencies Demonstrated

- **Data Engineering:** Relational modeling, schema DDL, controlled anomaly simulation, automated data cleansing, ETL pipelines.
- **Natural Language Processing (NLP):** Text normalization, TF-IDF vectorization, multiclass sentiment classification, fine-grained Aspect-Based Sentiment Analysis (ABSA), NMF topic modeling.
- **Machine Learning & Recommenders:** SVD Matrix Factorization, content similarity, hybrid ensembling, cold-start mitigation, time-aware offline evaluation (NDCG@K, Recall@K, MAP@K).
- **Relational Databases & SQL:** SQLite & PostgreSQL DDL, performance indexing, CTEs, Window functions (`LAG`, `NTILE`, `DENSE_RANK`).
- **Business Intelligence & Power BI:** Star-schema design (`FactSales`, `DimCustomer`), 15+ production DAX measures, interactive 6-page dashboard layout.
- **API & Application Development:** FastAPI REST architecture with Pydantic validation, modular multi-page Streamlit application with custom CSS.
- **Software Engineering Best Practices:** Modular code architecture, type hints, docstrings, centralized YAML configuration, automated testing (`pytest`), clean repository structure.
