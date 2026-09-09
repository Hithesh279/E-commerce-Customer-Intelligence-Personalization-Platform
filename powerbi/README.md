# Power BI Architecture & Dashboard Implementation Guide

## 1. Star-Schema Data Model Architecture

The analytical layer is structured into a clean, normalized **Star Schema** to deliver sub-second query performance and eliminate circular or many-to-many ambiguity in Power BI Desktop.

```text
                           ┌──────────────────┐
                           │   DimCustomer    │
                           └────────┬─────────┘
                                    │ (1:*)
                                    │
┌──────────────┐ (1:*)     ┌────────▼─────────┐     (1:*) ┌──────────────┐
│   DimDate    ├───────────►    FactSales     ◄───────────┤  DimProduct  │
└──────┬───────┘           └────────▲─────────┘           └──────┬───────┘
       │                            │                            │
       │ (1:*)                      │ (1:*)                      │ (1:*)
       │                   ┌────────▼─────────┐                  │
       ├───────────────────►   FactReviews    ◄──────────────────┤
       │                   └────────▲─────────┘                  │
       │                            │                            │
       │ (1:*)                      │ (1:*)                      │ (1:*)
       │                   ┌────────▼─────────┐                  │
       └───────────────────► FactInteractions ◄──────────────────┘
                           └──────────────────┘
```

### Table Relationships & Cardinality

| Dimension Table | Primary Key | Related Fact Table | Foreign Key | Cardinality | Cross-Filter Direction |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DimCustomer** | `customer_id` | `FactSales` | `customer_id` | 1 to Many (1:*) | Single |
| **DimCustomer** | `customer_id` | `FactReviews` | `customer_id` | 1 to Many (1:*) | Single |
| **DimCustomer** | `customer_id` | `FactInteractions` | `customer_id` | 1 to Many (1:*) | Single |
| **DimProduct** | `product_id` | `FactSales` | `product_id` | 1 to Many (1:*) | Single |
| **DimProduct** | `product_id` | `FactReviews` | `product_id` | 1 to Many (1:*) | Single |
| **DimProduct** | `product_id` | `FactInteractions` | `product_id` | 1 to Many (1:*) | Single |
| **DimCategory** | `category` | `DimProduct` | `category` | 1 to Many (1:*) | Both |
| **DimDate** | `date_key` | `FactSales` | `date_key` | 1 to Many (1:*) | Single |
| **DimDate** | `date_key` | `FactReviews` | `date_key` | 1 to Many (1:*) | Single |
| **DimDate** | `date_key` | `FactInteractions` | `date_key` | 1 to Many (1:*) | Single |

---

## 2. Quick Setup in Power BI Desktop (1-Click Import)

All star-schema tables are exported as clean, typed CSV files in `data/powerbi_export/`:

1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Folder** (or **Text/CSV**).
3. Select the folder path:
   `...\data\powerbi_export\`
4. Load the 7 tables:
   - `DimCustomer.csv`
   - `DimProduct.csv`
   - `DimCategory.csv`
   - `DimDate.csv`
   - `FactSales.csv`
   - `FactReviews.csv`
   - `FactInteractions.csv`
5. Verify in **Model View** that relationships match the Star Schema diagram above.
6. Create a new measure table called `_Measures` and paste the DAX formulas from `dax_measures.md`.

---

## 3. Dashboard Page Architecture

### Page 1 — Executive Overview
* **Target Audience:** C-Suite, VP of E-commerce, Head of Growth.
* **Top KPI Scorecards:**
  - `Total Net Revenue` ($ formatted)
  - `Total Orders`
  - `Total Customers`
  - `Average Order Value (AOV)`
  - `Overall Return Rate %`
  - `Positive Sentiment %`
* **Visuals:**
  - **Revenue & Order Trend (Area/Line Chart):** Monthly net revenue over time with 3-month moving average.
  - **Sales by Category (Horizontal Clustered Bar):** Category revenue breakdown.
  - **Customer Segment Distribution (Donut Chart):** High Value, Regular, Occasional, Discount Sensitive, etc.
  - **Sentiment Gauge:** Positive % vs Negative % vs Neutral %.
  - **Top 5 Revenue Generating Products (Table/Card).**

### Page 2 — Customer Intelligence
* **Focus:** RFM Behavioral Segmentation, customer lifetime spend, churn risk.
* **Visuals:**
  - **RFM Scatter Plot:** Monetary Total ($) vs Order Frequency with bubble size = Recency Days.
  - **Revenue by Customer Segment (Column Chart):** Segment-level net spend and customer count.
  - **Geographic Sales Matrix:** Spend and return rates across cities/countries.
  - **Membership Value Breakdown:** Bronze, Silver, Gold, Platinum average spend per order.
* **Slicers:** Customer Segment, Membership Type, City/Country, Date Range.

### Page 3 — Product Intelligence & Drill-Through
* **Focus:** SKU performance, profit drivers, return rates, and risk detection.
* **Visuals:**
  - **Product Performance Matrix Table:** Product Name, Category, Price, Units Sold, Net Revenue, Return Rate %, Avg Rating, Sentiment Flag.
  - **Risk Matrix Scatter Plot:** Units Sold (X-axis) vs Average Rating (Y-axis).
    - Highlights **High Sales + Poor Sentiment** (Risk quadrant).
    - Highlights **Low Sales + High Sentiment** (Hidden Gem quadrant).
  - **Drill-Through Target:** Selecting any product opens the **Product Detail Drill-Through Page** displaying sales history, return status, customer reviews, and aspect breakdown.

### Page 4 — NLP & Aspect Sentiment Intelligence
* **Focus:** Customer voice, fine-grained aspect sentiment, recurring complaint discovery.
* **Visuals:**
  - **11-Aspect Satisfaction Radar/Bar Chart:** Average sentiment score across Battery, Camera, Display, Performance, Quality, Price, Comfort, Durability, Delivery, Packaging, Design.
  - **Sentiment Trend over Time (Stacked Bar):** Positive, Neutral, and Negative review volume by month.
  - **Category Aspect Matrix Heatmap:** Aspects vs Categories showing satisfaction and complaint hot spots.
  - **Complaint Topic Distribution (Treemap):** Review count and percentage across NMF topic clusters.
* **Slicers:** Product Category, Brand, Star Rating (1-5), Sentiment Polarity.

### Page 5 — Recommendation Analytics & Offline Benchmarks
* **Focus:** ML Recommender evaluation, offline benchmarking, business impact simulation.
* **Visuals:**
  - **Model Benchmark Comparison (Grouped Bar Chart):** Compares Popularity, Content-Based, Collaborative Filtering, and Hybrid models on `Precision@5`, `Precision@10`, `Recall@5`, `Recall@10`, `MAP@10`, and `NDCG@10`.
  - **Winning Model Callout Card:** Highlights the winning Hybrid Recommender.
  - **Funnel Visual:** Simulated Recommendation Impressions -> Clicks (CTR %) -> Purchases (Conversion %).
  - **Simulated Attributed Revenue ($):** Estimated commercial impact of personalized suggestions.

### Page 6 — Customer 360 Drill-Through
* **Focus:** Individual customer profile, order timeline, browsing history, and personalized suggestions.
* **Visuals:**
  - **Customer Profile Card:** Demographics, signup date, segment, RFM score, preferred category.
  - **Purchase Timeline (Table):** Historical transactions, discounts, and return status.
  - **Review History:** Submitted reviews, ratings, and extracted aspects.
  - **Personalized Recommendation Grid:** Top-5 personalized product recommendations with dynamic explainability rationale ("Because you viewed...").

---

## 4. Interactive Features

* **Slicers & Cross-Filtering:** All visuals cross-filter dynamically. Clicking a customer segment on Page 2 immediately filters all KPIs, scatter plots, and tables for that cohort.
* **Custom Tooltips:** Hovering over any product in a scatter plot displays a custom tooltip page showing unit price, total orders, return rate, and average rating.
* **Bookmarks:** Bookmarks are configured for:
  - Default View vs Filtered View.
  - Top 10 Products vs Bottom 10 Products.
  - Sales Trend (Daily vs Monthly).
* **Dynamic Titles:** Visual titles use DAX conditional formatting to display context-aware headings (e.g. `Selected Category: Electronics`).
