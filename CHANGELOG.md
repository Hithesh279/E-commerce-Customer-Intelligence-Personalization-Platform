# Changelog

## Platform Enhancement & Audit Release

### Bug Fixes & Analytical Accuracy
- **Default Demo Store Export Category & Product Mapping (`app/services/active_dataset_manager.py`):** Fixed a bug where generating HTML, Excel, or Markdown exports for the Default Demo Store mapped `category_col="product_id"`, causing the *Category Revenue Distribution* table to list raw SKU IDs (`PROD_0005`, `PROD_0008`) instead of product categories (`Electronics`, `Sports`, `Home & Kitchen`). Default Demo Store exports now merge `products.csv` metadata (`product_name`, `category`) prior to transaction aggregation.
- **HTML Report RFM Subtitle Accuracy (`src/analytics/report_generator.py`):** Fixed the *Champions Count* and *At-Risk Count* KPI cards in the HTML executive report, which previously displayed `"Needs recency data"` unconditionally even when recency dates were present.
- **Post-Deduplication Filter Reporting (`src/data/cleaning.py`):** Fixed `empty_reviews_filtered` in `clean_reviews()` and `invalid_types_filtered` in `clean_interactions()` so they subtract from the post-deduplication row count rather than `initial_count`, preventing duplicate rows from being double-counted as empty reviews or invalid interaction types. Also prevented `RuntimeWarning: Mean of empty slice` when imputing customer ages across segments with all-null ages.
- **Negation-Window Aspect Sentiment Analysis (`src/nlp/aspect_extraction.py`):** Pre-compiled all aspect keyword regular expressions for ~4x faster extraction and added 2-token negation-window polarity inversion (`not`, `no`, `never`, `without`, `*n't`) so negated positive clues (e.g. *"battery is not good"*) score as `Negative` and negated negative clues (e.g. *"no lag"*) score as `Positive`.
- **Eliminated Duplicate ABSA Calls (`api/services/api_service.py`, `app/services/inference_service.py`):** Reused aspect extractions already computed inside `SentimentPredictor.predict()` instead of invoking `extract_aspect_sentiment_from_text()` twice per review analysis request.

### New Features & Improvements
- **Expanded FastAPI REST Endpoints (`api/main.py`, `api/routes/products.py`, `api/services/api_service.py`):**
  - Added `GET /analytics/kpis` to expose executive commercial and sentiment scorecards via the REST API.
  - Added `GET /products/{product_id}` (`ProductProfileResponse`) to return 360-degree SKU performance metrics, net/gross revenue, returned units, return rate, and sentiment discrepancy flags.
  - Added cross-version FastAPI `Query` `pattern`/`regex` compatibility in `api/routes/recommendations.py`.
- **Streamlit UI Polish & Security Hardening (`app/main.py`, `app/pages/*.py`, `app/services/active_dataset_manager.py`):**
  - Displayed all 8 platform modules on the Main Landing Portal (`app/main.py`), adding cards for `✍️ Live Review NLP Analyzer` and `📊 Offline ML Benchmarks`.
  - Fixed corrupted UTF-8 replacement characters (`\ufffd`) in `app/pages/product_intelligence.py` (`Average Rating (1-5★)`) and `app/pages/custom_data_analyzer.py` (`🏆 Top Ranked Products / Items`).
  - Added `html.escape()` around active dataset names in `render_global_active_dataset_banner()`, similar-product cards in `app/pages/product_intelligence.py`, and aspect cards in `app/pages/live_analyzer.py`.
- **Filesystem-Safe SQLite & Consolidated Power BI Workbook (`src/database/db_manager.py`):**
  - Configured SQLite connections with `PRAGMA journal_mode = MEMORY; PRAGMA synchronous = OFF;` for reliable execution across local disks, Docker mounts, WSL2, and virtualized filesystems without `disk I/O error` lock failures.
  - Automated generation of `data/powerbi_export/Ecommerce_Star_Schema.xlsx` alongside the 7 Star-Schema CSV tables.
- **Synchronized Interactive Power BI HTML Mockup (`powerbi/powerbi_report_mockup.html`):**
  - Updated all 6 pages and interactive slicers (`Category`, `Customer Segment`, `Year`) to reflect the exact metrics from `data/processed/*.csv`, `models/evaluation_metrics.json`, and `models/topic/topic_summaries.json`.
- **Enriched Markdown Executive Briefings (`src/analytics/report_generator.py`):**
  - Enhanced `generate_markdown_report()` with structured Markdown tables for Category Revenue Distribution, Aspect Satisfaction Scorecard, and Behavioral RFM Clusters, plus threshold-driven Strategic Recommendations.
- **Workspace & Export Hygiene:**
  - Prevented automated `pytest` runs from polluting `exports/` with temporary test files and cleaned out stale test artifacts and hardcoded local paths in `pyproject.toml` and `pyrightconfig.json`.
  - Expanded the automated test suite from 79 to **97 passing tests** across 10 test modules.

---

## Previous Review Fixes

The project was reviewed end to end. The pipeline was re-run, so every model, metric and database
file in this release was regenerated from the current code.

### Correctness
- The interaction log now contains exactly `num_interactions` events. It previously held 4,000 against a configured 3,000.
- Recommendation evaluation no longer leaks test-period data. Popularity statistics and product ratings are fit only on history before the test-window cut-off. The winner changed from the popularity baseline to the hybrid model, by a small margin. The rationale text is now generated from the computed numbers.
- Topic labels are derived from each topic's top words. Previously they were fixed to topic indices and did not match the words. No review is attributed to `PROD_0001` any more; attribution is reported as unavailable when no product ID exists.
- A 1-star rating given as text (`"1"`) is classified Negative. It was classified Positive.
- Custom review inference applies the same text cleaning used in training.
- RFM recency is no longer random. Without a date column, recency metrics are reported as N/A.
- SQL Query 2 no longer multiplies units sold by the number of reviews. Query 1 guards against division by zero.
- The PostgreSQL loader runs its DDL through SQLAlchemy `text()`. The SQLite rebuild keeps primary keys and indexes, and checks row counts after loading.
- `returned_units` in product analytics counts units, not orders.

### No invented values
- Uploaded datasets: sentiment, revenue, return-rate, customer, product, timeline, category and aspect values the dataset does not contain are shown as N/A or left out.
- The executive dashboard's hard-coded "+14.2% MoM" is replaced by growth computed from the monthly trend. It shows N/A when there are fewer than two months.
- The model benchmark's "+3.06% vs baseline" label is computed from the metrics.
- The banner and sidebar counts are read from the processed files. The system status shows real file checks.
- Report recommendations cite only thresholds the data actually breaches.

### Security
- Every value from an uploaded file is HTML-escaped on the pages, in the cards and in the HTML report.
- Scan Local Directory reads only the project `data/` folder and folders listed in `LOCAL_SCAN_ROOTS`.
- ZIP uploads are limited to 100 tabular files and 200 MB extracted. Files with the same name in different folders are both kept.
- The API's CORS origins are configurable and no longer allow credentials. An optional `X-API-Key` check is enabled by setting `API_KEY`.
