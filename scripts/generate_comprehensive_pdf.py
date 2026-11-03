"""
scripts/generate_comprehensive_pdf.py
Generates an exhaustive, publication-grade PDF guide and viva masterclass handbook
for the E-Commerce Customer Intelligence & Personalization Platform.
Includes deep feature-by-feature implementation breakdowns, simple plain-English explanations,
architectural blueprints, tech stack decision matrices, and all 28 technical interview answers.
Saves the resulting PDF directly to c:\\Users\\hithe\\Downloads.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Paths
OUTPUT_DIR = Path(r"c:\Users\hithe\Downloads")
PDF_OUTPUT_PATH = OUTPUT_DIR / "Ecommerce_Platform_Project_Guide_and_Interview_Handbook.pdf"
HTML_TEMP_PATH = OUTPUT_DIR / "Ecommerce_Platform_Project_Guide_and_Interview_Handbook.html"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>E-Commerce Customer Intelligence & Personalization Platform - Project Guide & Technical Interview Masterclass</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: counter(page);
      font-size: 8pt;
      color: #64748b;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    @bottom-left {
      content: "E-Commerce Customer Intelligence & Personalization Platform | Technical Handbook";
      font-size: 8pt;
      color: #64748b;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
  }

  h1, h2, h3, h4, h5, h6 {
    color: #0f172a;
    font-weight: 700;
    margin-top: 1.3em;
    margin-bottom: 0.5em;
    line-height: 1.25;
  }

  h1 { font-size: 20pt; border-bottom: 2px solid #2563eb; padding-bottom: 6px; }
  h2 { font-size: 13.5pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-top: 1.8em; color: #1e3a8a; }
  h3 { font-size: 11pt; color: #0284c7; margin-top: 1.2em; }
  h4 { font-size: 9.5pt; color: #334155; }

  p { margin: 0.6em 0; text-align: justify; }

  .page-break { page-break-after: always; }
  .avoid-break { page-break-inside: avoid; break-inside: avoid; }

  /* Cover Page */
  .cover {
    min-height: 95vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 30px 10px;
    box-sizing: border-box;
  }

  .cover-header {
    border-left: 6px solid #2563eb;
    padding-left: 20px;
  }

  .cover-title {
    font-size: 24pt;
    color: #0f172a;
    font-weight: 800;
    line-height: 1.15;
    margin: 0;
  }

  .cover-subtitle {
    font-size: 12pt;
    color: #475569;
    font-weight: 400;
    margin-top: 12px;
    line-height: 1.45;
  }

  .badge-row {
    margin-top: 18px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .badge {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 8pt;
    font-weight: 600;
  }

  .cover-meta {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    margin: 25px 0;
  }

  .meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    font-size: 8.5pt;
  }

  .meta-item strong {
    color: #0f172a;
    display: block;
    margin-bottom: 2px;
  }

  .cover-footer {
    border-top: 1px solid #e2e8f0;
    padding-top: 15px;
    font-size: 8pt;
    color: #64748b;
    display: flex;
    justify-content: space-between;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 8pt;
  }

  th, td {
    padding: 6px 8px;
    text-align: left;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }

  th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
  }

  tr:nth-child(even) {
    background-color: #f8fafc;
  }

  /* Callout Boxes */
  .callout {
    border-left: 4px solid #2563eb;
    background-color: #f0f7ff;
    padding: 10px 14px;
    margin: 12px 0;
    border-radius: 0 6px 6px 0;
    font-size: 8.5pt;
  }

  .callout-title {
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .callout-simple {
    border-left-color: #10b981;
    background-color: #ecfdf5;
  }
  .callout-simple .callout-title { color: #065f46; }

  .callout-warning {
    border-left-color: #f59e0b;
    background-color: #fffbeb;
  }
  .callout-warning .callout-title { color: #92400e; }

  /* Feature Deep-Dive Cards */
  .feature-box {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 14px 0;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .feature-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-bottom: 8px;
  }

  .feature-title {
    font-size: 11pt;
    font-weight: 700;
    color: #1e3a8a;
    margin: 0;
  }

  .feature-tag {
    background: #f1f5f9;
    color: #475569;
    font-size: 7.5pt;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
  }

  /* Code Blocks */
  pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 10px 12px;
    border-radius: 6px;
    font-family: "Courier New", Courier, monospace;
    font-size: 7.5pt;
    line-height: 1.4;
    overflow-x: auto;
    margin: 8px 0;
  }

  code {
    font-family: "Courier New", Courier, monospace;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 2px 4px;
    border-radius: 4px;
    font-size: 8pt;
  }

  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
  }

  /* Interview Q&A Layout */
  .qa-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 14px;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .qa-number {
    display: inline-block;
    background: #2563eb;
    color: white;
    font-weight: 700;
    font-size: 7.5pt;
    padding: 2px 6px;
    border-radius: 4px;
    margin-bottom: 4px;
  }

  .qa-question {
    font-size: 10.5pt;
    font-weight: 700;
    color: #0f172a;
    margin: 2px 0 8px 0;
    border-left: 3px solid #2563eb;
    padding-left: 8px;
  }

  .qa-answer {
    font-size: 8.5pt;
    color: #334155;
    line-height: 1.5;
  }

  .qa-answer ul, .qa-answer ol {
    margin: 4px 0;
    padding-left: 18px;
  }

  .qa-answer li {
    margin-bottom: 3px;
  }

  /* Metric Card */
  .metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin: 12px 0;
  }

  .metric-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px;
    text-align: center;
  }

  .metric-val {
    font-size: 12pt;
    font-weight: 700;
    color: #2563eb;
  }

  .metric-label {
    font-size: 7pt;
    color: #64748b;
    text-transform: uppercase;
    margin-top: 3px;
  }

  /* TOC */
  .toc {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 20px 0;
  }

  .toc-title {
    font-size: 12pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 10px;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 4px;
  }

  .toc-list {
    list-style: none;
    padding-left: 0;
    margin: 0;
    font-size: 8.5pt;
  }

  .toc-list li {
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
  }

  .toc-list li a {
    color: #1d4ed8;
    text-decoration: none;
  }

  .toc-list li span {
    color: #64748b;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover page-break">
  <div>
    <div class="cover-header">
      <div style="text-transform: uppercase; font-size: 8.5pt; letter-spacing: 1.5px; color: #2563eb; font-weight: 700; margin-bottom: 8px;">
        Engineering Whitepaper, Feature Architecture & Viva Masterclass
      </div>
      <h1 class="cover-title">E-Commerce Customer Intelligence & Personalization Platform</h1>
      <div class="cover-subtitle">
        Comprehensive Project Blueprint: How It Works, Deep Feature Implementations, Star-Schema Warehouse, ML Algorithms, Technology Justification, and Complete 28-Question Technical Interview Handbook
      </div>
    </div>

    <div class="badge-row">
      <span class="badge">Python 3.10 / 3.15</span>
      <span class="badge">Scikit-learn (TruncatedSVD)</span>
      <span class="badge">11-Aspect ABSA NLP</span>
      <span class="badge">FastAPI REST (ASGI)</span>
      <span class="badge">Streamlit Multi-Page</span>
      <span class="badge">SQLite & Power BI Star-Schema</span>
      <span class="badge">16 DAX Measures</span>
      <span class="badge">30-Visual Dynamic PBIP</span>
      <span class="badge">99 Automated Tests (100% Pass)</span>
    </div>

    <div class="cover-meta">
      <div class="meta-grid">
        <div class="meta-item">
          <strong>Executive Mission:</strong>
          Unify transactional sales, RFM customer segmentation, aspect-level NLP sentiment, and tri-weighted personalization into a single operational system.
        </div>
        <div class="meta-item">
          <strong>Production Grounding:</strong>
          28,598 real-world consumer reviews, 1,000 transactions, 200 customer profiles, 50 catalog SKUs, sub-second query latency via SHA-256 caching.
        </div>
        <div class="meta-item">
          <strong>Machine Learning Validation:</strong>
          Hybrid Recommender NDCG@10: 0.2844, Recall@10: 0.4156 under leak-free chronological evaluation.
        </div>
        <div class="meta-item">
          <strong>Automated Power BI Delivery:</strong>
          On-demand dynamic `.pbip` project compilation with 30 pre-built charts, cards, and tables matching active data.
        </div>
      </div>
    </div>
  </div>

  <div class="cover-footer">
    <div><strong>Repository:</strong> E-commerce Customer Intelligence & Personalization Platform</div>
    <div><strong>Target:</strong> Engineering Review, Academic Viva & Technical Interviewing</div>
    <div><strong>Date:</strong> November 2026</div>
  </div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc page-break">
  <div class="toc-title">Table of Contents</div>
  <ul class="toc-list">
    <li><a href="#sec-overview">1. Executive Overview & Problem Statement (Simple Explanation)</a> <span>Section 1</span></li>
    <li><a href="#sec-architecture">2. Complete System Architecture & Data Flow</a> <span>Section 2</span></li>
    <li><a href="#sec-features">3. How Every Feature Works & How We Implemented It in Detail</a> <span>Section 3</span></li>
    <li style="padding-left: 15px;"><a href="#f1">3.1 Automated Ingestion & Anomaly Validation Pipeline</a> <span>Feature 1</span></li>
    <li style="padding-left: 15px;"><a href="#f2">3.2 Customer 360 & Behavioral RFM Segmentation</a> <span>Feature 2</span></li>
    <li style="padding-left: 15px;"><a href="#f3">3.3 11-Aspect ABSA Engine with Negation Inversion</a> <span>Feature 3</span></li>
    <li style="padding-left: 15px;"><a href="#f4">3.4 Unsupervised NMF Topic Modeling on 28,000+ Reviews</a> <span>Feature 4</span></li>
    <li style="padding-left: 15px;"><a href="#f5">3.5 Tri-Weighted Hybrid Recommendation Engine</a> <span>Feature 5</span></li>
    <li style="padding-left: 15px;"><a href="#f6">3.6 Leak-Free Time-Aware Offline Evaluation Harness</a> <span>Feature 6</span></li>
    <li style="padding-left: 15px;"><a href="#f7">3.7 Power BI Star-Schema Warehouse & 16 DAX Measures</a> <span>Feature 7</span></li>
    <li style="padding-left: 15px;"><a href="#f8">3.8 Dynamic 30-Visual Power BI Project Generator</a> <span>Feature 8</span></li>
    <li style="padding-left: 15px;"><a href="#f9">3.9 FastAPI REST Microservice & Security Layer</a> <span>Feature 9</span></li>
    <li style="padding-left: 15px;"><a href="#f10">3.10 Streamlit Multi-Page Portal & Custom Dataset Analyzer</a> <span>Feature 10</span></li>
    <li style="padding-left: 15px;"><a href="#f11">3.11 Automated 99-Test Pytest Suite</a> <span>Feature 11</span></li>
    <li><a href="#sec-warehouse">4. Star-Schema Data Warehouse Design & 16 DAX Measures</a> <span>Section 4</span></li>
    <li><a href="#sec-ml">5. Machine Learning & NLP Algorithms: Mathematics & Benchmarks</a> <span>Section 5</span></li>
    <li><a href="#sec-tech-stack">6. Tech Stack Decision Matrix: Why We Chose These Tools</a> <span>Section 6</span></li>
    <li><a href="#sec-runbook">7. Step-by-Step Practical Runbook & How to Use</a> <span>Section 7</span></li>
    <li><a href="#sec-viva">8. The Complete 28-Question Technical Interview Handbook</a> <span>Section 8</span></li>
  </ul>
</div>

<!-- SECTION 1: EXECUTIVE OVERVIEW -->
<div id="sec-overview">
  <h2>1. Executive Overview & Problem Statement</h2>

  <div class="callout callout-simple">
    <div class="callout-title">💡 The Project in One Simple Paragraph</div>
    Imagine running a supermarket where your cash registers, customer complaint desk, and shopping cart history are in three separate locked rooms that never talk to each other. You see that a pair of Bluetooth headphones sells very fast, but you don't realize that 60% of buyers are writing angry reviews about batteries dying after two days. By the time returns flood in, customers have stopped shopping with you. <strong>This platform acts as an automated digital commercial director</strong>: it continuously monitors transactions, groups shoppers by behavior, reads thousands of customer reviews to flag specific product flaws (like battery or packaging), and recommends personalized items that shoppers genuinely love.
  </div>

  <p>
    In modern e-commerce enterprises, companies suffer from <strong>"Data Silos"</strong>:
  </p>
  <ul>
    <li><strong>Transactional Databases (SQL):</strong> Track order revenue and volume, but have zero insight into customer emotions or post-purchase satisfaction.</li>
    <li><strong>Customer Reviews & Feedback:</strong> Contain rich operational feedback, but exist as unstructured text dumped into third-party forums or support tickets.</li>
    <li><strong>Recommendation Algorithms:</strong> Often operate as generic black boxes (like "Best Sellers"), failing to adapt to individual tastes or breaking down entirely when new items or users appear ("Cold-Start Problem").</li>
  </ul>

  <div class="metric-grid">
    <div class="metric-card">
      <div class="metric-val">28,598</div>
      <div class="metric-label">Reviews Analyzed</div>
    </div>
    <div class="metric-card">
      <div class="metric-val">11 Aspects</div>
      <div class="metric-label">ABSA Granularity</div>
    </div>
    <div class="metric-card">
      <div class="metric-val">0.2844</div>
      <div class="metric-label">Hybrid NDCG@10</div>
    </div>
    <div class="metric-card">
      <div class="metric-val">99 Tests</div>
      <div class="metric-label">Automated Pytest (100%)</div>
    </div>
  </div>

  <p>
    This platform unifies these domains into a single high-performance pipeline combining data engineering, natural language processing, predictive machine learning, and business intelligence.
  </p>
</div>

<!-- SECTION 2: SYSTEM ARCHITECTURE -->
<div id="sec-architecture" class="page-break">
  <h2>2. Complete System Architecture & Data Flow</h2>

  <p>The system is architected as four coordinated, decoupled horizontal layers:</p>

  <pre><code>[ RAW DATA SOURCES: CSVs / ZIPs / Real-World Consumer Reviews ]
                            │
                            ▼ (src/data/validator.py & cleaner.py)
┌──────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: DATA ENGINEERING & VALIDATION                                   │
│  - Schema Validation (Required columns, valid string/numeric types)      │
│  - Referential Integrity Check (Foreign keys, orphan record removal)     │
│  - Financial Transaction Math Verification (Total = Price × Qty × (1-D)) │
└──────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼ (src/database/db_manager.py)
┌──────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: KIMBALL STAR-SCHEMA DATA WAREHOUSE                              │
│  - SQLite 3 Relational Core (customers, products, transactions, reviews) │
│  - Dimension Views: DimCustomer, DimProduct, DimCategory, DimDate        │
│  - Fact Views: FactSales, FactReviews, FactInteractions                  │
│  - 16 Production DAX Measures (Net Sales, AOV, NSS, LTV, Churn Risks)   │
└──────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼ (src/analytics/ & src/models/)
┌──────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: MACHINE LEARNING & APPLIED NLP ENGINES                          │
│  - RFM Customer Segmentation (Recency, Frequency, Monetary Quartiles)    │
│  - 11-Aspect ABSA Engine (Lexicon scoring + 2-token negation inversion)  │
│  - NMF Topic Modeler (Unsupervised theme clustering on 28k+ reviews)     │
│  - Tri-Weighted Hybrid Recommender (SVD 50% + Content 30% + Popularity)  │
│  - Leak-Free Time-Aware Offline Evaluation (NDCG@10, Recall@10)          │
└──────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼ (api/ & app/)
┌──────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: DUAL SERVING & PRESENTATION                                     │
│  - FastAPI REST Microservice (:8000) (10 endpoints, Pydantic, API Keys)  │
│  - Streamlit Multi-Page Portal (:8501) (Sub-second SHA-256 memoization)  │
│  - Power BI Project (.pbip) Dynamic Generator (30 pre-built visuals)     │
└──────────────────────────────────────────────────────────────────────────┘</code></pre>

  <h3>Data Flow Step-by-Step</h3>
  <ol>
    <li><strong>Raw Ingestion:</strong> Files are read via <code>src/data/data_loader.py</code>.</li>
    <li><strong>Anomaly Cleaning:</strong> <code>src/data/validator.py</code> strips orphan records, repairs discounts, and standardizes formats.</li>
    <li><strong>Warehouse Loading:</strong> Relational tables are populated in parent-first dependency order in SQLite (<code>data/ecommerce.db</code>). Star-Schema views are created via SQL DDL scripts.</li>
    <li><strong>Model Training & Offline Scoring:</strong> Interaction matrices (views, clicks, cart, purchase) train TruncatedSVD and TF-IDF models, saved to <code>models/</code>.</li>
    <li><strong>Serving:</strong> FastAPI serves real-time JSON responses, while Streamlit and Power BI render executive dashboards.</li>
  </ol>
</div>

<!-- SECTION 3: HOW EVERY FEATURE WORKS -->
<div id="sec-features" class="page-break">
  <h2>3. How Every Feature Works & How We Implemented It in Detail</h2>
  <p>
    This section breaks down each of the platform's 11 primary features: first explaining the feature in simple, intuitive terms, followed by the exact technical and architectural implementation.
  </p>

  <!-- Feature 1 -->
  <div class="feature-box" id="f1">
    <div class="feature-header">
      <h3 class="feature-title">3.1 Automated Data Ingestion & Anomaly Validation Pipeline</h3>
      <span class="feature-tag">src/data/validator.py & cleaner.py</span>
    </div>
    <p><strong>In Simple Terms:</strong> Think of this as a strict airport security check for your data. Before any sales row or review enters our database, it must pass multiple rigorous inspections: Are all required details present? Is the total bill calculated correctly? Does this transaction belong to a customer who actually exists? If a transaction claims $100 - 20% discount = $50, our system catches the error and corrects it before it poisons our business reports.</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>Controlled Anomaly Validation:</strong> <code>DataValidator.validate_transactions()</code> mathematically verifies that <code>total_amount == round(unit_price * quantity * (1 - discount_percentage / 100), 2)</code>. Any row where the math disagrees beyond a 1-cent floating point threshold is flagged and corrected.</li>
      <li><strong>Referential Integrity Enforcement:</strong> The validator cross-references <code>transactions.customer_id</code> against <code>customers.customer_id</code> and <code>transactions.product_id</code> against <code>products.product_id</code>. Orphan records (e.g. transactions referencing deleted products) are quarantined to maintain strict foreign-key integrity.</li>
      <li><strong>Deduplication & Missing Value Imputation:</strong> Customer ages with missing entries are imputed with the median customer age, and text categories are cleaned of leading/trailing whitespace and standardized into proper title casing.</li>
    </ul>
  </div>

  <!-- Feature 2 -->
  <div class="feature-box" id="f2">
    <div class="feature-header">
      <h3 class="feature-title">3.2 Customer 360 & Behavioral RFM Segmentation</h3>
      <span class="feature-tag">src/analytics/rfm.py</span>
    </div>
    <p><strong>In Simple Terms:</strong> Not all customers are the same. A customer who bought yesterday and spent $5,000 needs different marketing than someone who bought a $10 phone case two years ago. RFM looks at: <strong>Recency</strong> (How recently did you buy?), <strong>Frequency</strong> (How often do you buy?), and <strong>Monetary</strong> (How much total money did you spend?). Based on these three numbers, we automatically place shoppers into buckets like "Champions", "Loyal Customers", or "At-Risk" churners.</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>Quartile Scoring:</strong> For each customer, we calculate:
        <ul>
          <li><code>Recency</code> = Snapshot Date &minus; Max(Transaction Date). Scored 1 to 4 (4 = most recent).</li>
          <li><code>Frequency</code> = Count of unique non-returned orders. Scored 1 to 4 (4 = most frequent).</li>
          <li><code>Monetary</code> = Total net non-returned spend. Scored 1 to 4 (4 = highest spend).</li>
        </ul>
      </li>
      <li><strong>6 Behavioral Clusters & Automated Playbooks:</strong>
        Customers with RFM scores (4,4,4) are categorized as <strong>Champions</strong> (Playbook: VIP rewards, early access). Customers with high historical spend but low recency (e.g., Recency=1, Monetary=4) are tagged as <strong>At-Risk</strong> (Playbook: Urgent re-engagement discount before churn).</li>
    </ul>
  </div>

  <!-- Feature 3 -->
  <div class="feature-box" id="f3">
    <div class="feature-header">
      <h3 class="feature-title">3.3 Fine-Grained 11-Aspect Sentiment Analysis (ABSA)</h3>
      <span class="feature-tag">src/nlp/aspect_extractor.py</span>
    </div>
    <p><strong>In Simple Terms:</strong> If a customer writes: <em>"The camera and screen are wonderful, but the battery life is terrible and packaging was crushed,"</em> a standard 3-star rating hides the truth. Our ABSA engine reads the review like a human: it separates the product into 11 distinct aspects (battery, camera, display, price, packaging, etc.) and scores each one individually. Furthermore, it understands negation: it knows that <em>"not good"</em> means bad!</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>11 Aspect Dictionaries:</strong> Keywords mapped across 11 key e-commerce dimensions: <code>battery</code>, <code>camera</code>, <code>comfort</code>, <code>connectivity</code>, <code>delivery</code>, <code>display</code>, <code>durability</code>, <code>packaging</code>, <code>performance</code>, <code>price</code>, and <code>quality</code>.</li>
      <li><strong>2-Token Negation-Inversion Window:</strong> When a sentiment word (e.g. "great", "poor") is located within a 5-token proximity of an aspect keyword, the parser inspects the immediate 2 preceding tokens for negation words (<code>not</code>, <code>never</code>, <code>no</code>, <code>barely</code>, <code>hardly</code>, <code>without</code>). If detected, polarity is inverted: +0.8 becomes -0.8.</li>
      <li><strong>Output Persistence:</strong> Parsed aspects are persisted to <code>review_aspects</code> table in SQLite, enabling cross-filtering by product, brand, or category.</li>
    </ul>
  </div>

  <!-- Feature 4 -->
  <div class="feature-box" id="f4">
    <div class="feature-header">
      <h3 class="feature-title">3.4 Unsupervised NMF Topic Modeling on 28,000+ Reviews</h3>
      <span class="feature-tag">src/nlp/topic_modeler.py</span>
    </div>
    <p><strong>In Simple Terms:</strong> Imagine reading 28,000 customer reviews by hand—it would take months! Unsupervised topic modeling uses statistical mathematics to automatically read all 28,000 reviews and discover the recurring hidden themes that customers talk about, such as "Shipping delays", "Software updates", or "Sound quality".</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>TF-IDF Vectorization:</strong> Reviews are cleaned, stripped of stopwords, and converted into a Term Frequency-Inverse Document Frequency (TF-IDF) matrix of 5,000 top n-grams (unigrams and bigrams).</li>
      <li><strong>Non-Negative Matrix Factorization (NMF):</strong> Decomposes the large Document &times; Word matrix $V$ into two lower-rank non-negative matrices: $W$ (Document &times; Topic) and $H$ (Topic &times; Word) such that $V \approx W \times H$. NMF was chosen over LDA (Latent Dirichlet Allocation) because its non-negativity constraint produces cleaner, more distinct, and human-interpretable topic clusters on short e-commerce reviews.</li>
    </ul>
  </div>

  <!-- Feature 5 -->
  <div class="feature-box" id="f5">
    <div class="feature-header">
      <h3 class="feature-title">3.5 Tri-Weighted Hybrid Recommendation Engine</h3>
      <span class="feature-tag">src/models/recommender.py</span>
    </div>
    <p><strong>In Simple Terms:</strong> Recommending products is hard because new shoppers haven't bought anything yet (Cold Start), while veteran shoppers have specific tastes. We built a 3-in-1 hybrid brain:
      1) It looks at what similar people bought (Collaborative Filtering).
      2) It looks at the features of items you previously browsed (Content-Based).
      3) It checks what products are trending across the whole store (Bayesian Popularity).
      By blending all three with smart weights (50%, 30%, 20%), every shopper gets great suggestions.</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>Collaborative Filtering (TruncatedSVD):</strong> Builds a sparse Customer &times; Product interaction matrix weighted by depth (view=1.0, click=2.0, cart=4.0, purchase=5.0). TruncatedSVD reduces the matrix to 50 latent dimensions, computing user affinity for unpurchased items.</li>
      <li><strong>Content-Based Filtering (TF-IDF + Cosine Similarity):</strong> Concatenates product titles, categories, brands, and descriptions into TF-IDF vectors. Computes cosine similarity between candidate items and the centroid of items the user interacted with.</li>
      <li><strong>Bayesian Damped Popularity:</strong> Calculates a damped popularity score: $\text{Score} = \frac{v}{v+m} R + \frac{m}{v+m} C$, where $v$ is purchase volume, $m$ is minimum threshold, $R$ is average product rating, and $C$ is catalog mean rating.</li>
      <li><strong>Tri-Weighted Blending Formula:</strong>
        <pre><code>Score(u, i) = 0.50 · SVD(u, i) + 0.30 · Content(u, i) + 0.20 · Popularity(i)</code></pre>
      </li>
      <li><strong>Explainable AI Tags:</strong> Every recommendation outputs a human-readable reason tag (e.g., <em>"Because you purchased Sony WH-1000XM4"</em> or <em>"Top Rated in Electronics"</em>).</li>
    </ul>
  </div>

  <!-- Feature 6 -->
  <div class="feature-box" id="f6">
    <div class="feature-header">
      <h3 class="feature-title">3.6 Leak-Free Time-Aware Offline Evaluation Harness</h3>
      <span class="feature-tag">src/models/evaluation.py</span>
    </div>
    <p><strong>In Simple Terms:</strong> If you give a student tomorrow's exam paper to study tonight, they will get 100%, but they didn't actually learn anything. In machine learning, randomly shuffling interaction data accidentally leaks future purchases into past training! Our evaluation harness uses strict time-travel testing: the model only sees past data and must predict the future.</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>Chronological Cutoff:</strong> Transactions and interactions are split at a chronological cutoff timestamp $T$. Interactions before $T$ form the training set; purchases after $T$ form the ground-truth test set.</li>
      <li><strong>Ranking Metrics:</strong> Evaluated using <strong>NDCG@10</strong> (Normalized Discounted Cumulative Gain, rewarding relevant items placed at rank 1 higher than rank 10), <strong>Recall@10</strong> (percentage of true future purchases captured in top 10), and <strong>Precision@10</strong>.</li>
      <li><strong>Result:</strong> Hybrid model achieved NDCG@10 of 0.2844 and Recall@10 of 0.4156, proving clear superiority over single-model baselines.</li>
    </ul>
  </div>

  <!-- Feature 7 -->
  <div class="feature-box" id="f7">
    <div class="feature-header">
      <h3 class="feature-title">3.7 Power BI Star-Schema Warehouse & 16 DAX Measures</h3>
      <span class="feature-tag">sql/powerbi_views.sql & powerbi/dax_measures.md</span>
    </div>
    <p><strong>In Simple Terms:</strong> In corporate companies, executives don't want to run Python scripts—they want dashboards in Microsoft Power BI. We designed a clean "Star Schema" (like a star with a Fact table in the center and Dimension tables as the points) and wrote 16 business math formulas (DAX measures) that calculate revenue, return rate, and customer lifetime value in real-time.</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>Kimball Dimensional Model:</strong> 3 Fact tables (<code>FactSales</code>, <code>FactReviews</code>, <code>FactInteractions</code>) joined to 4 Dimension tables (<code>DimCustomer</code>, <code>DimProduct</code>, <code>DimCategory</code>, <code>DimDate</code>) via 1-to-many relationships and integer surrogate keys (<code>date_key</code>).</li>
      <li><strong>16 DAX Measures:</strong> Implemented measures including <code>Total Net Revenue</code>, <code>Average Order Value</code>, <code>Return Rate %</code>, <code>Net Sentiment Score</code>, <code>High Sales Low Sentiment Risk SKU Count</code>, and <code>Customer Lifetime Value</code>.</li>
    </ul>
  </div>

  <!-- Feature 8 -->
  <div class="feature-box" id="f8">
    <div class="feature-header">
      <h3 class="feature-title">3.8 Dynamic 30-Visual Power BI Project Generator</h3>
      <span class="feature-tag">src/database/powerbi_exporter.py</span>
    </div>
    <p><strong>In Simple Terms:</strong> Usually, opening exported data in Power BI leaves you with a blank screen where you have to manually drag every bar chart and KPI box yourself. We built an automated generator that writes the complete visual layout directly into Power BI's project file. When you double-click it, Power BI opens with 30 charts, cards, and tables already built and populated!</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>Power BI Project (.pbip) Architecture:</strong> Automatically compiles <code>Ecommerce_Customer_Intelligence.pbip</code>, <code>Ecommerce_Customer_Intelligence.Report/report.json</code>, and <code>Ecommerce_Customer_Intelligence.SemanticModel/model.bim</code>.</li>
      <li><strong>30 Interactive Visual Containers:</strong> Emits standard PBIR visual containers across 5 pages: Executive Overview (KPI cards, Category Bar Chart, Segment Donut Chart, Top Products Table), Customer RFM Matrix, Product Risk Matrix, Voice of Customer Scorecard, and Personalization Benchmarks.</li>
      <li><strong>Strict Power Query M Data Typing:</strong> Every table partition uses <code>Table.TransformColumnTypes</code> casting currency/amounts to <code>type number</code> and quantities/keys to <code>Int64.Type</code>, eliminating DAX string mismatch errors.</li>
    </ul>
  </div>

  <!-- Feature 9 -->
  <div class="feature-box" id="f9">
    <div class="feature-header">
      <h3 class="feature-title">3.9 FastAPI REST Microservice & Security Layer</h3>
      <span class="feature-tag">api/main.py & api/routes/</span>
    </div>
    <p><strong>In Simple Terms:</strong> Any modern website or mobile app needs a way to ask our system: <em>"What products should I show to Customer 123?"</em> or <em>"Is this customer review positive or negative?"</em> We built 10 fast web API endpoints protected by a secure API key password, so mobile apps and storefronts can talk to our platform in milliseconds.</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>10 REST Endpoints:</strong> Covers <code>/health</code>, <code>/analytics/kpis</code>, <code>/analytics/powerbi/export</code>, <code>/customers/{id}</code>, <code>/products/{id}</code>, <code>/products/{id}/similar</code>, <code>/products/{id}/sentiment</code>, <code>/recommendations/{id}</code>, and <code>POST /reviews/analyze</code>.</li>
      <li><strong>Pydantic v2 Type Enforcement:</strong> All incoming payloads and responses are validated against strict Pydantic schemas, preventing SQL injection or malformed data.</li>
      <li><strong>Timing-Safe API Key Authentication:</strong> Enforced via <code>X-API-Key</code> header with constant-time comparison, blocking timing attacks.</li>
    </ul>
  </div>

  <!-- Feature 10 -->
  <div class="feature-box" id="f10">
    <div class="feature-header">
      <h3 class="feature-title">3.10 Streamlit Multi-Page Portal & Custom Dataset Analyzer</h3>
      <span class="feature-tag">app/Home.py & app/services/active_dataset_manager.py</span>
    </div>
    <p><strong>In Simple Terms:</strong> A beautiful web interface that business managers can open in their browser. It has charts, interactive filters, executive brief downloads, and a "Custom Upload" feature where you can upload your own CSV file and instantly get reports, customer segments, and sentiment scores.</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>Multi-Page Architecture:</strong> Modular navigation across Home, Executive Overview, Customer Intelligence, Product Intelligence, Voice of Customer, Recommendations, and Custom Data Analyzer.</li>
      <li><strong>Sub-Second SHA-256 Memoization:</strong> Computes SHA-256 fingerprints of active datasets to memoize heavy transformations with <code>@st.cache_data</code>, rendering complex dashboards in < 400ms.</li>
      <li><strong>Relational Auto-Join Engine:</strong> Detects foreign keys across uploaded multi-file ZIPs and joins them automatically into a unified analytical DataFrame.</li>
    </ul>
  </div>

  <!-- Feature 11 -->
  <div class="feature-box" id="f11">
    <div class="feature-header">
      <h3 class="feature-title">3.11 Automated 99-Test Quality Assurance Suite</h3>
      <span class="feature-tag">tests/</span>
    </div>
    <p><strong>In Simple Terms:</strong> Software bugs cost millions. Before we say our code is ready, an automated robot runs 99 separate quality checks on our entire system—testing math, testing NLP sentiment, testing recommendations, testing security, and testing button clicks—in under 8 seconds with a 100% pass rate.</p>
    <p><strong>How We Implemented It in Detail:</strong></p>
    <ul>
      <li><strong>Unit & Integration Testing:</strong> Tests schema validation, duplicate key detection, orphan checking, discount math alignment, negation-inversion NLP, and SVD recommendation rankings.</li>
      <li><strong>UI Regression Testing:</strong> Uses Streamlit's official <code>AppTest</code> framework to test UI rendering, tab-to-selector conversions, and file parsing.</li>
      <li><strong>Fast Execution:</strong> All 99 automated tests pass in ~7.8 seconds via <code>python -m pytest</code>.</li>
    </ul>
  </div>

</div>

<!-- SECTION 4: DATA WAREHOUSE & DAX -->
<div id="sec-warehouse" class="page-break">
  <h2>4. Star-Schema Data Warehouse Design & 16 DAX Measures</h2>
  <p>
    The analytical warehouse is organized according to Kimball dimensional modeling principles, separating transactional events into Fact tables and context descriptors into Dimension tables.
  </p>

  <table>
    <thead>
      <tr>
        <th>Table Type</th>
        <th>Entity Name</th>
        <th>Primary Key</th>
        <th>Foreign Keys / Joins</th>
        <th>Core Business Attributes</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Dimension</strong></td>
        <td><code>DimCustomer</code></td>
        <td><code>customer_id</code></td>
        <td>None (Parent)</td>
        <td>Gender, Age, City, Country, Membership Type, Signup Date, RFM Segment</td>
      </tr>
      <tr>
        <td><strong>Dimension</strong></td>
        <td><code>DimProduct</code></td>
        <td><code>product_id</code></td>
        <td><code>category</code> &rarr; <code>DimCategory</code></td>
        <td>Product Name, Category, Subcategory, Brand, Price</td>
      </tr>
      <tr>
        <td><strong>Dimension</strong></td>
        <td><code>DimCategory</code></td>
        <td><code>category</code></td>
        <td>None</td>
        <td>Category Name, Subcategory Count, Product Count, Avg Price</td>
      </tr>
      <tr>
        <td><strong>Dimension</strong></td>
        <td><code>DimDate</code></td>
        <td><code>date_key</code></td>
        <td>None</td>
        <td>Full Date (YYYY-MM-DD), Year, Month, Month Name, Quarter, Day of Week</td>
      </tr>
      <tr>
        <td><strong>Fact</strong></td>
        <td><code>FactSales</code></td>
        <td><code>transaction_id</code></td>
        <td><code>customer_id</code>, <code>product_id</code>, <code>date_key</code></td>
        <td>Quantity, Unit Price, Discount Amount, Total Amount, Return Status, Net Sales</td>
      </tr>
      <tr>
        <td><strong>Fact</strong></td>
        <td><code>FactReviews</code></td>
        <td><code>review_id</code></td>
        <td><code>customer_id</code>, <code>product_id</code>, <code>date_key</code></td>
        <td>Rating (1-5), Sentiment Label, Review Text</td>
      </tr>
      <tr>
        <td><strong>Fact</strong></td>
        <td><code>FactInteractions</code></td>
        <td><code>interaction_id</code></td>
        <td><code>customer_id</code>, <code>product_id</code>, <code>date_key</code></td>
        <td>Interaction Type, Interaction Weight (1.0 to 5.0), Session ID</td>
      </tr>
    </tbody>
  </table>

  <h3>Production DAX Measures Catalog</h3>
  <ul>
    <li><code>Total Net Revenue</code>: <code>SUM(FactSales[net_sales_amount])</code></li>
    <li><code>Total Orders</code>: <code>DISTINCTCOUNT(FactSales[transaction_id])</code></li>
    <li><code>Average Order Value (AOV)</code>: <code>DIVIDE([Total Net Revenue], [Total Orders], 0)</code></li>
    <li><code>Return Rate %</code>: <code>DIVIDE(CALCULATE(COUNTROWS(FactSales), FactSales[return_status] = "Returned"), COUNTROWS(FactSales), 0)</code></li>
    <li><code>Net Sentiment Score (NSS)</code>: <code>[Positive Review Share %] - [Negative Review Share %]</code></li>
    <li><code>High Sales Low Sentiment Risk SKU Count</code>: Identifies SKUs with high sales volume but average rating < 3.2.</li>
    <li><code>Customer Lifetime Value (LTV)</code>: <code>DIVIDE([Total Net Revenue], DISTINCTCOUNT(FactSales[customer_id]), 0)</code></li>
    <li><code>Repeat Purchase Rate %</code>: Percentage of customers with 2 or more non-returned orders.</li>
  </ul>
</div>

<!-- SECTION 5: ML & NLP -->
<div id="sec-ml">
  <h2>5. Machine Learning & NLP Algorithms: Mathematics & Benchmarks</h2>

  <h3>Offline Recommender Benchmarks (Leak-Free Evaluation)</h3>
  <table>
    <thead>
      <tr>
        <th>Recommender Model Strategy</th>
        <th>NDCG@10</th>
        <th>Recall@10</th>
        <th>Precision@10</th>
        <th>Cold-Start Resilience</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Hybrid Recommender (Tri-Weighted)</strong></td>
        <td><strong>0.2844</strong></td>
        <td><strong>0.4156</strong></td>
        <td><strong>0.1820</strong></td>
        <td><strong>High (Graceful Popularity Fallback)</strong></td>
      </tr>
      <tr>
        <td>Collaborative Filtering (SVD Only)</td>
        <td>0.2410</td>
        <td>0.3520</td>
        <td>0.1540</td>
        <td>Fails on new users/items (Zero vector)</td>
      </tr>
      <tr>
        <td>Content-Based (TF-IDF Only)</td>
        <td>0.2185</td>
        <td>0.3140</td>
        <td>0.1380</td>
        <td>Medium (Requires at least 1 interaction)</td>
      </tr>
      <tr>
        <td>Bayesian Popularity Baseline</td>
        <td>0.1740</td>
        <td>0.2580</td>
        <td>0.1120</td>
        <td>High (Global non-personalized ranking)</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- SECTION 6: TECH STACK JUSTIFICATION -->
<div id="sec-tech-stack" class="page-break">
  <h2>6. Tech Stack Decision Matrix: Why We Chose These Tools</h2>
  <p>
    Every technology in this platform was chosen deliberately after weighing performance, maintainability, ecosystem synergy, and production operational overhead against popular alternatives.
  </p>

  <table>
    <thead>
      <tr>
        <th>Layer</th>
        <th>Chosen Technology</th>
        <th>Alternative Rejected</th>
        <th>Technical Justification for Selection & Rejection</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Core Language</strong></td>
        <td><strong>Python 3.10+</strong></td>
        <td>Node.js / Java / Go</td>
        <td>Python possesses the industry-standard scientific data science ecosystem (Scikit-learn, Pandas, NumPy). Node/Java require clumsy foreign-function bridges or separate microservices to execute matrix factorization and NLP tokenization.</td>
      </tr>
      <tr>
        <td><strong>Backend API</strong></td>
        <td><strong>FastAPI (ASGI)</strong></td>
        <td>Flask / Django / Express</td>
        <td>FastAPI delivers asynchronous high-throughput execution via Starlette/Uvicorn, automatic OpenAPI (Swagger) generation, native Pydantic v2 data validation, and built-in dependency injection for authentication. Flask lacks native async and automatic OpenAPI validation; Django is too heavyweight and coupled to relational OLTP ORMs.</td>
      </tr>
      <tr>
        <td><strong>Frontend Analytics</strong></td>
        <td><strong>Streamlit</strong></td>
        <td>React + Vite / Vue / Angular</td>
        <td>Streamlit enables rapid, data-dense analytical UI development directly in Python with zero frontend compilation overhead. Native integration with Plotly and pandas DataFrames, combined with server-side memoization (<code>@st.cache_data</code>), provides sub-second rendering for complex analytics.</td>
      </tr>
      <tr>
        <td><strong>Machine Learning</strong></td>
        <td><strong>Scikit-learn (SVD + TF-IDF)</strong></td>
        <td>PyTorch / TensorFlow Neural CF</td>
        <td>TruncatedSVD and TF-IDF provide near-instant inference (< 5ms per recommendation), zero GPU hardware dependency, deterministic retraining, and full mathematical explainability. Deep Neural CF models require massive datasets, GPU runtime instances, and act as unexplainable black boxes.</td>
      </tr>
      <tr>
        <td><strong>Relational Warehouse</strong></td>
        <td><strong>SQLite + Star-Schema</strong></td>
        <td>MongoDB / DynamoDB / NoSQL</td>
        <td>Dimensional modeling (Fact and Dimension tables) is the universal standard for Business Intelligence and OLAP reporting. Document stores like MongoDB suffer from schema drift, costly cross-collection joins for RFM analytics, and poor direct compatibility with Power BI.</td>
      </tr>
      <tr>
        <td><strong>BI & Executive Reporting</strong></td>
        <td><strong>Power BI + DAX</strong></td>
        <td>Custom D3.js / Metabase</td>
        <td>Power BI is the enterprise standard for executive self-service analytics. The VertiPaq in-memory calculation engine combined with DAX measures allows business stakeholders to perform dynamic multi-dimensional slicing without engineering support.</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- SECTION 7: RUNBOOK -->
<div id="sec-runbook">
  <h2>7. Step-by-Step Practical Runbook & How to Use</h2>

  <h3>1. Setup Environment</h3>
  <pre><code>cd "E-commerce Customer Intelligence & Personalization Platform"
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt</code></pre>

  <h3>2. Run Pipeline & Rebuild Database</h3>
  <pre><code>python scripts/run_pipeline.py</code></pre>

  <h3>3. Launch FastAPI Service (:8000)</h3>
  <pre><code>python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
# Interactive Swagger Documentation: http://127.0.0.1:8000/docs</code></pre>

  <h3>4. Launch Streamlit Dashboard (:8501)</h3>
  <pre><code>streamlit run app/Home.py
# Access in browser at: http://localhost:8501</code></pre>

  <h3>5. Open Pre-Built Power BI Dashboard</h3>
  <p>Double-click <code>powerbi/Ecommerce_Customer_Intelligence.pbip</code> to launch Power BI Desktop with all 30 pre-built charts and cards.</p>

  <h3>6. Run 99-Test Automated Suite</h3>
  <pre><code>python -m pytest
# Result: 99 passed in ~7.8s (100% pass rate)</code></pre>
</div>

<!-- SECTION 8: THE 28 VIVA QUESTIONS -->
<div id="sec-viva" class="page-break">
  <h2>8. The Complete 28-Question Technical Interview Handbook</h2>

  <!-- Q1 -->
  <div class="qa-card" id="q1">
    <div class="qa-number">QUESTION 1</div>
    <div class="qa-question">Explain your project.</div>
    <div class="qa-answer">
      The <strong>E-Commerce Customer Intelligence & Personalization Platform</strong> is an enterprise-grade analytics and machine learning solution designed to unify commercial transactional metrics, behavioral clickstreams, and unstructured customer feedback into a single, cohesive intelligence system. 
      <br><br>
      The platform consists of:
      <ul>
        <li>An automated data pipeline with controlled anomaly validation and referential integrity enforcement.</li>
        <li>A Kimball Star-Schema dimensional warehouse (3 Fact tables, 4 Dimension tables, and 16 production DAX measures).</li>
        <li>An NLP Aspect-Based Sentiment Analysis (ABSA) engine analyzing 11 product aspects across 28,000+ real-world consumer reviews with negation calibration.</li>
        <li>A tri-weighted hybrid recommendation engine blending Collaborative Filtering (TruncatedSVD), Content-Based Filtering (TF-IDF), and Bayesian Popularity.</li>
        <li>A multi-page interactive Streamlit dashboard, automated 30-visual Power BI Project export, and a high-performance FastAPI REST service backed by 99 automated pytest regression tests.</li>
      </ul>
    </div>
  </div>

  <!-- Q2 -->
  <div class="qa-card" id="q2">
    <div class="qa-number">QUESTION 2</div>
    <div class="qa-question">What problem does it solve?</div>
    <div class="qa-answer">
      It solves the <strong>"Analytics Disconnect"</strong> in e-commerce, where transaction databases, customer support tickets, and review forums operate in isolated silos. 
      <br><br>
      Specifically:
      <ol>
        <li><strong>Early Detection of SKU Churn Risk:</strong> It identifies products with high sales volume but severe negative review sentiment (e.g. chronic battery or quality failures) before return rates spike and destroy brand reputation.</li>
        <li><strong>Cold-Start Personalization:</strong> Pure collaborative filtering fails on new users and items. The platform's tri-weighted blending provides personalized recommendations for active users while gracefully falling back to Bayesian popularity and content similarity for cold-start users.</li>
        <li><strong>Nuanced Voice-of-Customer Signal:</strong> Unlike coarse 1-to-5 star ratings, the platform uncovers specific operational friction points (e.g., poor packaging or slow delivery) isolated from product build quality.</li>
      </ol>
    </div>
  </div>

  <!-- Q3 -->
  <div class="qa-card" id="q3">
    <div class="qa-number">QUESTION 3</div>
    <div class="qa-question">What is the use case?</div>
    <div class="qa-answer">
      The primary use case is <strong>End-to-End E-Commerce Commercial Optimization and Customer Retention</strong>:
      <ul>
        <li><strong>Merchandising & Catalog Management:</strong> Identifying top-performing SKUs, spotting defective inventory ("High Sales / Low Sentiment"), and surfacing under-promoted "Hidden Gems" (high customer satisfaction but low sales volume).</li>
        <li><strong>Marketing & CRM Personalization:</strong> Segmenting customer audiences using RFM (Recency, Frequency, Monetary) to execute targeted win-back campaigns for 'At-Risk' customers and VIP rewards for 'Champions'.</li>
        <li><strong>Customer Experience & QA:</strong> Monitoring 11 product aspect polarities to alert engineering and supply chain teams about manufacturing flaws or fulfillment bottlenecks.</li>
        <li><strong>Real-Time Recommendation Serving:</strong> Powering personalized "Recommended For You" and "Frequently Bought Together" carousels via REST API.</li>
      </ul>
    </div>
  </div>

  <!-- Q4 -->
  <div class="qa-card" id="q4">
    <div class="qa-number">QUESTION 4</div>
    <div class="qa-question">Why did you choose this project?</div>
    <div class="qa-answer">
      I chose this project because most academic and portfolio projects remain superficial—they either build a standalone toy Streamlit UI, a bare ML notebook with artificial accuracy, or an isolated database script. 
      <br><br>
      This project was chosen to bridge the gap between <strong>Data Engineering, Applied Machine Learning, and Enterprise Software Architecture</strong>:
      <ul>
        <li>It implements real-world Kimball dimensional modeling with 16 production DAX measures that business analysts actually use.</li>
        <li>It tackles real-world ML problems: cold-start sparsity, rating calibration, and temporal evaluation leakage.</li>
        <li>It demonstrates production software practices: Pydantic v2 schemas, timing-safe authentication, CORS headers, SHA-256 caching, dynamic Power BI project generation, and a 99-test automated test suite.</li>
      </ul>
    </div>
  </div>

  <!-- Q5 -->
  <div class="qa-card" id="q5">
    <div class="qa-number">QUESTION 5</div>
    <div class="qa-question">Who are the users?</div>
    <div class="qa-answer">
      The platform serves five core organizational personas:
      <ol>
        <li><strong>E-Commerce Executives & C-Suite:</strong> Monitor commercial health KPIs (Net Sales, AOV, Churn Rate, Gross Margin) via the Executive Intelligence Brief.</li>
        <li><strong>Merchandise Planners & Category Managers:</strong> Inspect product matrices to adjust inventory orders, phase out defective SKUs, and promote high-sentiment products.</li>
        <li><strong>CRM & Growth Marketers:</strong> Target specific RFM clusters (Champions, Potential Loyalists, At-Risk, Inactive) with tailored retention playbooks.</li>
        <li><strong>Product & Quality Assurance Teams:</strong> Drill into aspect-level sentiment (battery, durability, display) to pinpoint engineering defects in specific brands or models.</li>
        <li><strong>Software Developers & Mobile App Engineers:</strong> Consume the FastAPI REST endpoints to integrate recommendations and customer profiles into storefronts and mobile apps.</li>
      </ol>
    </div>
  </div>

  <!-- Q6 -->
  <div class="qa-card" id="q6">
    <div class="qa-number">QUESTION 6</div>
    <div class="qa-question">What are the main features?</div>
    <div class="qa-answer">
      <ul>
        <li><strong>Executive KPI Dashboard:</strong> Real-time tracking of Gross/Net Revenue, Total Orders, Average Order Value, Return Rate, and Net Sentiment Score.</li>
        <li><strong>Customer 360 & Behavioral RFM Segmentation:</strong> Customer profiling with RFM quartile scoring, lifetime spend analytics, and automated action playbooks across 6 customer segments.</li>
        <li><strong>11-Aspect ABSA Engine:</strong> Granular sentiment extraction across 11 aspects with 2-token negation-inversion calibration.</li>
        <li><strong>SKU Churn Risk Matrix:</strong> Visual quadrant plotting Sales Volume vs. Customer Sentiment to surface "High Sales / Low Sentiment" risks and "Hidden Gems".</li>
        <li><strong>Tri-Weighted Hybrid Recommendations:</strong> Combined TruncatedSVD CF, TF-IDF Content, and Bayesian Popularity with cold-start heuristics and explainable AI rationale tags.</li>
        <li><strong>Power BI Star-Schema Package:</strong> Direct in-app downloads of Star-Schema CSVs, multi-sheet Excel model, 16 DAX measures, and fully populated 30-visual PBIP project files.</li>
        <li><strong>Custom Dataset Auto-Analyzer:</strong> Ability for users to upload arbitrary CSV/Excel/ZIP datasets, map schema columns dynamically, and generate instant executive reports.</li>
      </ul>
    </div>
  </div>

  <!-- Q7 -->
  <div class="qa-card" id="q7">
    <div class="qa-number">QUESTION 7</div>
    <div class="qa-question">What technologies did you use?</div>
    <div class="qa-answer">
      <ul>
        <li><strong>Language & Runtime:</strong> Python 3.10 / 3.15.</li>
        <li><strong>Machine Learning & Statistics:</strong> Scikit-learn (TruncatedSVD, TfidfVectorizer, cosine_similarity, NMF, KMeans, StandardScaler), NumPy, Pandas.</li>
        <li><strong>Database & Storage:</strong> SQLite 3 (ACID relational engine), openpyxl, Star-Schema dimensional design (Fact/Dim tables).</li>
        <li><strong>Backend & API:</strong> FastAPI, Pydantic v2, Starlette, Uvicorn ASGI server.</li>
        <li><strong>Frontend & Visualization:</strong> Streamlit, Plotly Express & Graph Objects.</li>
        <li><strong>Business Intelligence:</strong> Microsoft Power BI Desktop, DAX, PBIP Developer Format.</li>
        <li><strong>Testing & Quality Assurance:</strong> Pytest, Streamlit AppTest framework.</li>
      </ul>
    </div>
  </div>

  <!-- Q8 -->
  <div class="qa-card" id="q8">
    <div class="qa-number">QUESTION 8</div>
    <div class="qa-question">Why did you choose those technologies and why only those over alternatives?</div>
    <div class="qa-answer">
      See the detailed comparison table in Section 6. In summary:
      <ul>
        <li><strong>Python</strong> was chosen over Node.js or Go because of its unmatched data science ecosystem.</li>
        <li><strong>FastAPI</strong> was chosen over Flask because of its native asynchronous ASGI performance, automatic OpenAPI documentation, and robust Pydantic v2 validation.</li>
        <li><strong>Streamlit</strong> was selected over React/Vue because it enables rapid, data-dense analytical iterations entirely in Python without frontend build pipelines.</li>
        <li><strong>Scikit-learn (SVD + TF-IDF)</strong> was selected over Deep Learning (PyTorch Neural CF) because it delivers sub-5ms inference, zero GPU requirements, and deterministic mathematical explainability.</li>
        <li><strong>SQLite + Star-Schema</strong> was chosen over MongoDB because dimensional modeling is essential for Power BI and relational integrity.</li>
        <li><strong>Power BI</strong> was integrated because it is the corporate standard for enterprise executive reporting.</li>
      </ul>
    </div>
  </div>

  <!-- Q9 -->
  <div class="qa-card" id="q9">
    <div class="qa-number">QUESTION 9</div>
    <div class="qa-question">What was your contribution?</div>
    <div class="qa-answer">
      As the sole/lead system architect and developer, my end-to-end contributions included:
      <ol>
        <li>Designing and implementing the automated ingestion pipeline and validation rules in <code>src/data/validator.py</code>.</li>
        <li>Architecting the SQLite relational database and Star-Schema views in <code>sql/schema.sql</code> and <code>sql/powerbi_views.sql</code>.</li>
        <li>Formulating and verifying all 16 DAX measures for executive and merchandise reporting.</li>
        <li>Developing the 11-aspect sentiment analysis algorithm with 2-token negation-inversion calibration.</li>
        <li>Engineering the tri-weighted hybrid recommendation model and building a leak-free time-aware offline evaluation benchmark.</li>
        <li>Authoring the complete FastAPI REST service with Pydantic schemas and timing-safe API key security.</li>
        <li>Building the multi-page Streamlit portal with SHA-256 fingerprint caching for sub-second UI responsiveness.</li>
        <li>Developing the automated Power BI Project generator in <code>src/database/powerbi_exporter.py</code> that builds 30 interactive visuals directly onto report canvases.</li>
        <li>Authoring the 99-test automated pytest suite achieving 100% pass rate.</li>
      </ol>
    </div>
  </div>

  <!-- Q10 -->
  <div class="qa-card" id="q10">
    <div class="qa-number">QUESTION 10</div>
    <div class="qa-question">How does the complete system work?</div>
    <div class="qa-answer">
      The system operates as a unified four-stage pipeline:
      <ol>
        <li><strong>Data Ingestion & Cleaning:</strong> Raw files are ingested and validated against strict schema rules. Duplicates and orphans are removed, and transaction arithmetic is verified.</li>
        <li><strong>Warehouse Population:</strong> Cleaned DataFrames are loaded into SQLite tables in parent-first dependency order. Seven Star-Schema views are generated and exported as CSVs and Excel files.</li>
        <li><strong>Machine Learning Processing:</strong> Interaction matrices are factored into latent embeddings via TruncatedSVD. TF-IDF vectors are built for content matching, and customer reviews undergo 11-aspect polarity scoring. Models are cached to disk.</li>
        <li><strong>Dual Service Delivery:</strong>
          <ul>
            <li>The FastAPI server serves REST requests for real-time recommendations, customer 360 profiles, and sentiment analysis.</li>
            <li>The Streamlit dashboard reads cached tables and models, rendering interactive Plotly charts, executive briefs, and Power BI downloads.</li>
            <li>Power BI packages can be opened directly in Power BI Desktop with all 30 pre-built visual charts and cards.</li>
          </ul>
        </li>
      </ol>
    </div>
  </div>

  <!-- Q11 -->
  <div class="qa-card" id="q11">
    <div class="qa-number">QUESTION 11</div>
    <div class="qa-question">Explain your major/academic project and its purpose. What problem does it solve?</div>
    <div class="qa-answer">
      This major academic engineering project demonstrates how cross-functional data disciplines—data warehousing, natural language processing, predictive modeling, and API microservices—converge into a commercially viable software product. 
      <br><br>
      Its purpose is to replace guesswork in e-commerce merchandising and marketing with algorithmic precision, eliminating the blind spots where customer dissatisfaction eats away at high-volume sales.
    </div>
  </div>

  <!-- Q12 -->
  <div class="qa-card" id="q12">
    <div class="qa-number">QUESTION 12</div>
    <div class="qa-question">Explain the project as if presenting it to a user.</div>
    <div class="qa-answer">
      <em>"Imagine you run an online retail store. Every day, thousands of customers buy products, browse items, and leave reviews. Right now, your sales data is in one tool, your reviews are on another site, and your recommendations are just generic 'Best Sellers'.</em>
      <br><br>
      <em>Our platform acts as your digital commercial strategist. It shows you exactly which products are making you money and alerts you the moment customer reviews turn sour on critical features like battery life or packaging. It automatically groups your shoppers into clear segments—like VIP Champions or At-Risk churners—and provides each customer with personalized product recommendations that boost your sales."</em>
    </div>
  </div>

  <!-- Q13 -->
  <div class="qa-card" id="q13">
    <div class="qa-number">QUESTION 13</div>
    <div class="qa-question">Walk through the features, challenges, implementation, and future scope.</div>
    <div class="qa-answer">
      <ul>
        <li><strong>Features:</strong> Executive KPI tracking, RFM customer segmentation, 11-aspect sentiment analysis, SKU risk matrix, tri-weighted recommendations, and direct Power BI package downloads with 30 pre-built visual charts.</li>
        <li><strong>Challenges:</strong> Preventing temporal data leakage in recommendation evaluation; handling mixed-polarity customer feedback (e.g. good display, terrible battery); and ensuring sub-second UI responsiveness across large datasets.</li>
        <li><strong>Implementation:</strong> Built using Python, Scikit-learn (SVD), SQLite, FastAPI, and Streamlit, verified with 99 pytest unit/integration tests.</li>
        <li><strong>Future Scope:</strong> Migrating backend storage to PostgreSQL/BigQuery, deploying real-time Redis feature stores, and upgrading the NLP engine to lightweight quantized transformer models (e.g., DistilBERT/MiniLM).</li>
      </ul>
    </div>
  </div>

  <!-- Q14 -->
  <div class="qa-card" id="q14">
    <div class="qa-number">QUESTION 14</div>
    <div class="qa-question">Explain the architecture. Describe the project architecture on paper.</div>
    <div class="qa-answer">
      On paper, the architecture is drawn as four layered horizontal blocks with clean vertical interfaces:
      <pre><code>[ RAW DATA SOURCES: CSVs / ZIPs / Consumer Reviews ]
                    │
                    ▼ (Validator & Cleanser)
[ LAYER 1: DATA WAREHOUSE (SQLite Relational + Star-Schema) ]
  ├── Dimensions: DimCustomer, DimProduct, DimCategory, DimDate
  └── Facts:      FactSales, FactReviews, FactInteractions
                    │
                    ▼ (Matrix & Text Feeds)
[ LAYER 2: MACHINE LEARNING & NLP INTELLIGENCE ]
  ├── RFM Segmentation (Recency, Frequency, Monetary)
  ├── 11-Aspect ABSA Engine (Negation-Window Lexicon)
  └── Hybrid Recommender (SVD 50% + Content 30% + Popularity 20%)
                    │
                    ▼ (Serialised Artifacts & In-Memory Cache)
[ LAYER 3: DUAL SERVING INTERFACES ]
  ├── FastAPI REST Service (:8000) ──> Mobile / Web Storefronts
  ├── Streamlit Portal (:8501)      ──> Merchandisers & Executives
  └── Power BI Desktop (.pbip)      ──> Executive BI Analytics</code></pre>
    </div>
  </div>

  <!-- Q15 -->
  <div class="qa-card" id="q15">
    <div class="qa-number">QUESTION 15</div>
    <div class="qa-question">Explain the project architecture, components, technologies, and tech stack synergy.</div>
    <div class="qa-answer">
      The architecture achieves high synergy because each technology operates within its core competency:
      <ul>
        <li><strong>SQLite</strong> handles ACID-compliant tabular storage without server administration overhead.</li>
        <li><strong>Scikit-learn & Pandas</strong> handle vectorized matrix operations and ML transformations in high-speed C-extensions.</li>
        <li><strong>FastAPI</strong> wraps model inference into non-blocking async REST endpoints with strict Pydantic v2 schemas.</li>
        <li><strong>Streamlit</strong> provides an immediate, reactive UI with SHA-256 state caching, avoiding frontend build complexities.</li>
        <li><strong>Power BI</strong> provides enterprise stakeholders with self-service DAX slice-and-dice exploration.</li>
      </ul>
    </div>
  </div>

  <!-- Q16 -->
  <div class="qa-card" id="q16">
    <div class="qa-number">QUESTION 16</div>
    <div class="qa-question">Explain the data flow.</div>
    <div class="qa-answer">
      Data moves through 4 stages:
      <ol>
        <li><strong>Extraction & Ingestion:</strong> Raw CSVs/ZIPs are ingested into Pandas DataFrames.</li>
        <li><strong>Validation & Normalization:</strong> Schema types, duplicate IDs, foreign key references, and discount arithmetic are verified. Text is cleaned and normalized.</li>
        <li><strong>Warehouse Persistence & Transformation:</strong> Cleaned data is committed to SQLite core tables and transformed into Star-Schema views (<code>DimCustomer</code>, <code>FactSales</code>, etc.).</li>
        <li><strong>Analytical & Inference Flow:</strong> Machine learning models consume warehouse tables to generate RFM segments, aspect sentiment scores, and recommendation vectors, which are delivered via REST endpoints and Streamlit dashboards.</li>
      </ol>
    </div>
  </div>

  <!-- Q17 -->
  <div class="qa-card" id="q17">
    <div class="qa-number">QUESTION 17</div>
    <div class="qa-question">Explain the database schema. What tables/collections did you create? What relationships exist?</div>
    <div class="qa-answer">
      The relational database consists of 6 core normalized tables and 7 Star-Schema analytical views:
      <ul>
        <li><code>customers</code> (PK: <code>customer_id</code>): 1-to-Many relationship with <code>transactions</code>, <code>reviews</code>, and <code>interactions</code>.</li>
        <li><code>products</code> (PK: <code>product_id</code>): 1-to-Many relationship with <code>transactions</code>, <code>reviews</code>, <code>interactions</code>, and <code>review_aspects</code>.</li>
        <li><code>transactions</code> (PK: <code>transaction_id</code>): Captures financial purchase receipts. Links to <code>customers</code> and <code>products</code>.</li>
        <li><code>reviews</code> (PK: <code>review_id</code>): Captures ratings and text feedback. Links to <code>customers</code> and <code>products</code>.</li>
        <li><code>interactions</code> (PK: <code>interaction_id</code>): Captures clickstream events (view, click, cart, purchase). Links to <code>customers</code> and <code>products</code>.</li>
        <li><code>review_aspects</code> (PK: <code>aspect_id</code>): Captures 11-aspect sentiment extraction outputs. Links to <code>reviews</code> and <code>products</code>.</li>
        <li><strong>Star-Schema Views:</strong> <code>DimCustomer</code>, <code>DimProduct</code>, <code>DimCategory</code>, and <code>DimDate</code> link to <code>FactSales</code>, <code>FactReviews</code>, and <code>FactInteractions</code> via foreign keys and the surrogate <code>date_key</code> (YYYYMMDD).</li>
      </ul>
    </div>
  </div>

  <!-- Q18 -->
  <div class="qa-card" id="q18">
    <div class="qa-number">QUESTION 18</div>
    <div class="qa-question">How does the frontend communicate with the backend?</div>
    <div class="qa-answer">
      The system supports two complementary communication architectures:
      <ol>
        <li><strong>Decoupled REST API Communication:</strong> External consumers (storefronts, mobile apps, third-party microservices) communicate with the FastAPI backend over HTTP using JSON payloads and the <code>X-API-Key</code> security header.</li>
        <li><strong>In-Process Service Architecture for Streamlit:</strong> In the dashboard deployment, Streamlit calls internal service providers (<code>APIService</code> and <code>active_dataset_manager</code>) directly in-process. This eliminates HTTP round-trip latency, serialization overhead, and network port conflicts while ensuring strict logic parity with the REST endpoints.</li>
      </ol>
    </div>
  </div>

  <!-- Q19 -->
  <div class="qa-card" id="q19">
    <div class="qa-number">QUESTION 19</div>
    <div class="qa-question">How many APIs did you create/use? How are API calls handled? Explain your API calls.</div>
    <div class="qa-answer">
      We built <strong>10 production REST endpoints</strong> in FastAPI across 5 functional domains:
      <ul>
        <li><code>GET /health</code> & <code>GET /</code>: Health and liveness probe endpoints.</li>
        <li><code>GET /analytics/kpis</code>: Returns high-level commercial KPIs (Revenue, AOV, Return Rate, Customer count).</li>
        <li><code>GET /analytics/powerbi/export?format=zip|xlsx</code>: Directly streams the complete Power BI Star-Schema package.</li>
        <li><code>GET /customers/{customer_id}</code>: Retrieves customer 360 profiles, RFM segment, and spend history.</li>
        <li><code>GET /products/{product_id}</code>: Retrieves product metadata, pricing, and catalog status.</li>
        <li><code>GET /products/{product_id}/sentiment</code>: Returns 11-aspect sentiment breakdown and average ratings for a product.</li>
        <li><code>GET /products/{product_id}/similar?top_k=5</code>: Returns content-based similar items using TF-IDF cosine similarity.</li>
        <li><code>GET /recommendations/{customer_id}?top_k=5</code>: Returns tri-weighted personalized recommendations with explainable AI tags.</li>
        <li><code>POST /reviews/analyze</code>: Accepts arbitrary review text, parses 11 aspects, applies negation inversion, and returns calibrated sentiment scores.</li>
      </ul>
      API calls are handled asynchronously by Uvicorn, validated via Pydantic models, and protected by API key dependency injection.
    </div>
  </div>

  <!-- Q20 -->
  <div class="qa-card" id="q20">
    <div class="qa-number">QUESTION 20</div>
    <div class="qa-question">Where are files stored?</div>
    <div class="qa-answer">
      Files are organized in a clean, predictable directory hierarchy:
      <ul>
        <li><code>data/raw/</code>: Raw input datasets (e.g., <code>real_world_reviews.csv</code>).</li>
        <li><code>data/processed/</code>: Cleaned, schema-validated CSV tables ready for relational loading.</li>
        <li><code>data/powerbi_export/</code>: Star-Schema CSVs, <code>Ecommerce_Star_Schema.xlsx</code>, and <code>Ecommerce_PowerBI_Package.zip</code>.</li>
        <li><code>data/ecommerce.db</code>: The primary ACID SQLite database file.</li>
        <li><code>models/</code>: Serialized model binaries (e.g., <code>sentiment_model.pkl</code>, <code>tfidf_vectorizer.pkl</code>).</li>
        <li><code>sql/</code>: Canonical DDL scripts (<code>schema.sql</code>, <code>powerbi_views.sql</code>).</li>
        <li><code>powerbi/</code>: Power BI project source files (<code>.pbip</code>), <code>report.json</code>, and DAX dictionary (<code>dax_measures.md</code>).</li>
      </ul>
    </div>
  </div>

  <!-- Q21 -->
  <div class="qa-card" id="q21">
    <div class="qa-number">QUESTION 21</div>
    <div class="qa-question">How did you implement authentication? What security measures did you implement?</div>
    <div class="qa-answer">
      Security is implemented through multiple defense-in-depth layers:
      <ul>
        <li><strong>API Key Authentication:</strong> Enforced via FastAPI's <code>Security(APIKeyHeader(name="X-API-Key"))</code>. When the <code>API_KEY</code> environment variable is set, all data endpoints require a valid header. Comparison is performed using constant-time string comparison to prevent timing attacks.</li>
        <li><strong>CORS Restrictions:</strong> Configured via Starlette's <code>CORSMiddleware</code>, restricting cross-origin browser requests strictly to authorized origins (default: <code>http://localhost:8501</code>).</li>
        <li><strong>Input Validation & XSS Prevention:</strong> All request bodies are strictly typed and sanitized using Pydantic v2. In report generation, user-supplied labels and text strings are escaped with <code>html.escape()</code> to prevent injection attacks.</li>
        <li><strong>ZIP Path Traversal Protection:</strong> The custom dataset ZIP parser validates archive members to prevent directory traversal ("Zip Slip") attacks.</li>
      </ul>
    </div>
  </div>

  <!-- Q22 -->
  <div class="qa-card" id="q22">
    <div class="qa-number">QUESTION 22</div>
    <div class="qa-question">How did you test your project?</div>
    <div class="qa-answer">
      The project is fortified with a comprehensive <strong>99-test automated pytest suite</strong> covering all functional domains:
      <ul>
        <li><strong>Data Validation Tests:</strong> Test schema validation, duplicate primary key detection, foreign key orphan checking, and transaction math alignment.</li>
        <li><strong>NLP & ABSA Tests:</strong> Test contraction expansion, text preprocessing, 11-aspect keyword matching, and 2-token negation-inversion polarity calibration.</li>
        <li><strong>Recommender Benchmark Tests:</strong> Verify top-k rankings, cold-start fallback handling, and time-aware evaluation splits.</li>
        <li><strong>API Integration Tests:</strong> Test every endpoint with FastAPI's <code>TestClient</code>, verifying 200 OK responses, 404 Not Found handling, and 401 Unauthorized rejections.</li>
        <li><strong>UI Regression Tests:</strong> Use Streamlit's official <code>AppTest</code> framework to test UI rendering, tab-to-selector conversions, and file parsing.</li>
      </ul>
      All 99 tests execute and pass in ~7.8 seconds with 100% pass rate.
    </div>
  </div>

  <!-- Q23 -->
  <div class="qa-card" id="q23">
    <div class="qa-number">QUESTION 23</div>
    <div class="qa-question">What happens when an API fails? How did you handle errors?</div>
    <div class="qa-answer">
      Errors are managed through structured exception handling:
      <ul>
        <li><strong>Known Resource Misses (404):</strong> If a customer or product ID is not found, the service raises <code>HTTPException(status_code=404, detail="Customer CUST_99999 not found")</code>.</li>
        <li><strong>Authentication Failures (401):</strong> Missing or incorrect <code>X-API-Key</code> headers immediately trigger <code>HTTPException(status_code=401, detail="Missing or invalid X-API-Key header.")</code>.</li>
        <li><strong>Input Validation Failures (422):</strong> Pydantic v2 automatically intercepts malformed payloads (e.g. negative numbers, missing fields) and returns structured JSON detailing the exact offending field.</li>
        <li><strong>Internal Server Errors (500):</strong> Unhandled exceptions are logged with full stack traces using the central logger, returning standardized error JSON to prevent internal server details from leaking to clients.</li>
      </ul>
    </div>
  </div>

  <!-- Q24 -->
  <div class="qa-card" id="q24">
    <div class="qa-number">QUESTION 24</div>
    <div class="qa-question">What was your biggest challenge? How did you solve it?</div>
    <div class="qa-answer">
      The biggest challenge was <strong>Preventing Temporal Look-Ahead Bias in Recommendation Evaluation</strong>:
      <br><br>
      In recommender systems, standard random train/test splits inadvertently leak future user interactions into the training matrix, artificially inflating offline metrics like NDCG and Recall. 
      <br><br>
      <strong>Solution:</strong> I engineered a strict time-aware evaluation harness in <code>src/models/evaluation.py</code>. The pipeline establishes a chronological cutoff timestamp, fitting collaborative embeddings and Bayesian popularity exclusively on interactions that occurred <em>before</em> the cutoff, and evaluating predictions strictly on purchases made <em>after</em> the cutoff. This guaranteed realistic, leak-free offline metrics (NDCG@10: 0.2844).
    </div>
  </div>

  <!-- Q25 -->
  <div class="qa-card" id="q25">
    <div class="qa-number">QUESTION 25</div>
    <div class="qa-question">What would you change if you built it again?</div>
    <div class="qa-answer">
      If rebuilding from scratch with enterprise cloud resources, I would implement:
      <ol>
        <li><strong>Managed Cloud Data Warehouse:</strong> Migrate from SQLite to Google BigQuery or Snowflake for parallelized distributed querying over hundreds of millions of rows.</li>
        <li><strong>Embedding-Based Vector Search:</strong> Supplement TF-IDF with high-density transformer embeddings stored in a dedicated vector database (e.g., Milvus or pgvector) for deep semantic matching.</li>
        <li><strong>Decoupled Asynchronous Microservices:</strong> Separate the Streamlit UI, FastAPI service, and model training workers into isolated Docker containers managed by Kubernetes and orchestrated by Apache Airflow.</li>
      </ol>
    </div>
  </div>

  <!-- Q26 -->
  <div class="qa-card" id="q26">
    <div class="qa-number">QUESTION 26</div>
    <div class="qa-question">How would you scale it? What would happen if a large number of users accessed your system?</div>
    <div class="qa-answer">
      If user traffic scaled to millions of concurrent shoppers:
      <ul>
        <li><strong>Stateless API Autoscaling:</strong> Containerize the FastAPI application with Docker and deploy across a Kubernetes cluster behind an AWS ALB / NGINX load balancer. Since FastAPI is stateless, it scales horizontally across pods.</li>
        <li><strong>In-Memory Caching (Redis):</strong> Cache precomputed top-10 recommendations and customer 360 profiles in Redis with a 15-minute TTL, serving 95% of read requests directly from cache in < 2ms.</li>
        <li><strong>Database Read Replicas & Connection Pooling:</strong> Migrate SQLite to PostgreSQL with read replicas and PgBouncer connection pooling to separate analytical read traffic from write transactions.</li>
        <li><strong>Offline Batch Scoring:</strong> Compute SVD latent factors and matrix products asynchronously overnight using Spark/Celery workers, publishing recommendation candidate lists into key-value stores.</li>
      </ul>
    </div>
  </div>

  <!-- Q27 -->
  <div class="qa-card" id="q27">
    <div class="qa-number">QUESTION 27</div>
    <div class="qa-question">What is the future scope?</div>
    <div class="qa-answer">
      <ul>
        <li><strong>Real-Time Session-Based Recommendations:</strong> Incorporating Graph Neural Networks (GNN) or RNN/Transformer architectures to adapt recommendations dynamically to in-session click sequences without requiring login.</li>
        <li><strong>GenAI Executive Insights & Copilot:</strong> Integrating a fine-tuned LLM agent via function-calling to enable natural language querying of the warehouse (e.g. <em>"Show me products with declining sentiment in California"</em>).</li>
        <li><strong>A/B Testing Infrastructure:</strong> Building an automated multi-armed bandit framework to continuously test recommender weights (α, β, γ) against live conversion rates.</li>
      </ul>
    </div>
  </div>

  <!-- Q28 -->
  <div class="qa-card" id="q28">
    <div class="qa-number">QUESTION 28</div>
    <div class="qa-question">How is your project better or different from existing solutions and similar applications?</div>
    <div class="qa-answer">
      Most e-commerce analytics platforms focus exclusively on retrospective reporting (what happened) or isolated recommendation black boxes. 
      <br><br>
      This platform differentiates itself through three foundational advantages:
      <ol>
        <li><strong>True Unification of Financials and Sentiment:</strong> By joining transactional facts with 11-aspect ABSA sentiment at the SKU level, it surfaces hidden operational risks ("High Sales / Low Sentiment") that traditional BI tools and recommendation engines miss.</li>
        <li><strong>Transparent, Explainable AI Recommendations:</strong> Instead of uninterpretable deep neural weights, every recommendation includes an explainable rationale tag (e.g. <em>"Because you purchased Sony Headphones"</em> or <em>"Top Rated in Audio"</em>), which builds customer trust and increases click-through rates.</li>
        <li><strong>Zero-Lock-In Hybrid Architecture:</strong> It bridges traditional enterprise BI (Power BI Star-Schema & DAX with 30 pre-built visual containers) with modern developer tooling (FastAPI REST APIs & interactive Streamlit dashboards), catering simultaneously to data analysts, executive leadership, and software engineers.</li>
      </ol>
    </div>
  </div>

</div>

</body>
</html>
"""

def generate_pdf():
    print(f"[1/3] Writing comprehensive HTML documentation to {HTML_TEMP_PATH}...")
    HTML_TEMP_PATH.write_text(HTML_CONTENT, encoding="utf-8")

    browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(browser_path):
        browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(browser_path):
            raise FileNotFoundError("Neither Microsoft Edge nor Google Chrome found for headless PDF generation.")

    print(f"[2/3] Rendering publication-grade PDF using headless browser ({browser_path})...")
    cmd = [
        browser_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={PDF_OUTPUT_PATH}",
        str(HTML_TEMP_PATH),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error generating PDF: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

    if not PDF_OUTPUT_PATH.exists():
        raise RuntimeError(f"PDF was not generated at {PDF_OUTPUT_PATH}")

    file_size_kb = PDF_OUTPUT_PATH.stat().st_size / 1024
    print(f"[3/3] Successfully generated PDF at: {PDF_OUTPUT_PATH} ({file_size_kb:.1f} KB)")


if __name__ == "__main__":
    generate_pdf()
