-- ====================================================================
-- E-commerce Customer Intelligence Platform - Analytical SQL Queries
-- Demonstrating JOINs, CTEs, Window Functions, and Business Aggregations
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Top 10 Revenue-Generating Products with Return Rates & Ranks
-- --------------------------------------------------------------------
WITH product_sales AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        COUNT(t.transaction_id) AS total_orders,
        SUM(t.quantity) AS units_sold,
        ROUND(SUM(CASE WHEN t.return_status != 'Returned' THEN t.total_amount ELSE 0 END), 2) AS net_revenue,
        ROUND(SUM(CASE WHEN t.return_status = 'Returned' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(t.transaction_id), 2) AS return_rate_pct
    FROM products p
    LEFT JOIN transactions t ON p.product_id = t.product_id
    GROUP BY p.product_id, p.product_name, p.category, p.price
)
SELECT
    product_id,
    product_name,
    category,
    price,
    total_orders,
    units_sold,
    net_revenue,
    return_rate_pct,
    DENSE_RANK() OVER (ORDER BY net_revenue DESC) AS revenue_rank
FROM product_sales
ORDER BY revenue_rank ASC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 2: Product Discrepancy Discovery: High Sales + Low Customer Sentiment
-- Products in Top 25% of Sales Volume but Bottom 25% of Average Rating
-- --------------------------------------------------------------------
WITH product_metrics AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        SUM(t.quantity) AS total_units_sold,
        ROUND(AVG(r.rating), 2) AS avg_rating,
        COUNT(DISTINCT r.review_id) AS review_count
    FROM products p
    INNER JOIN transactions t ON p.product_id = t.product_id
    INNER JOIN reviews r ON p.product_id = r.product_id
    GROUP BY p.product_id, p.product_name, p.category
    HAVING COUNT(DISTINCT r.review_id) >= 5
),
quartiles AS (
    SELECT
        product_id,
        product_name,
        category,
        total_units_sold,
        avg_rating,
        review_count,
        NTILE(4) OVER (ORDER BY total_units_sold ASC) AS sales_quartile,
        NTILE(4) OVER (ORDER BY avg_rating ASC) AS rating_quartile
    FROM product_metrics
)
SELECT
    product_id,
    product_name,
    category,
    total_units_sold,
    avg_rating,
    review_count,
    'High Sales + Poor Sentiment (Risk Product)' AS anomaly_flag
FROM quartiles
WHERE sales_quartile = 4 AND rating_quartile = 1
ORDER BY total_units_sold DESC;


-- --------------------------------------------------------------------
-- QUERY 3: Monthly Category Revenue & MoM Growth using Window LAG()
-- --------------------------------------------------------------------
WITH monthly_cat_revenue AS (
    SELECT
        p.category,
        SUBSTR(t.transaction_date, 1, 7) AS year_month,
        ROUND(SUM(t.total_amount), 2) AS monthly_revenue
    FROM transactions t
    INNER JOIN products p ON t.product_id = p.product_id
    WHERE t.return_status != 'Returned'
    GROUP BY p.category, SUBSTR(t.transaction_date, 1, 7)
),
mom_calc AS (
    SELECT
        category,
        year_month,
        monthly_revenue,
        LAG(monthly_revenue, 1) OVER (PARTITION BY category ORDER BY year_month ASC) AS prev_month_revenue
    FROM monthly_cat_revenue
)
SELECT
    category,
    year_month,
    monthly_revenue,
    COALESCE(prev_month_revenue, 0.0) AS prev_month_revenue,
    ROUND(
        CASE
            WHEN prev_month_revenue IS NOT NULL AND prev_month_revenue > 0
            THEN ((monthly_revenue - prev_month_revenue) / prev_month_revenue) * 100.0
            ELSE 0.0
        END,
        2
    ) AS mom_growth_pct
FROM mom_calc
ORDER BY category, year_month;


-- --------------------------------------------------------------------
-- QUERY 4: Customer RFM Segmentation & Monetary Value Distribution
-- --------------------------------------------------------------------
WITH customer_orders AS (
    SELECT
        c.customer_id,
        c.customer_segment,
        COUNT(t.transaction_id) AS order_frequency,
        ROUND(SUM(t.total_amount), 2) AS total_spend,
        MAX(t.transaction_date) AS last_order_date
    FROM customers c
    INNER JOIN transactions t ON c.customer_id = t.customer_id
    WHERE t.return_status != 'Returned'
    GROUP BY c.customer_id, c.customer_segment
),
customer_ranks AS (
    SELECT
        customer_id,
        customer_segment,
        order_frequency,
        total_spend,
        last_order_date,
        NTILE(5) OVER (ORDER BY total_spend DESC) AS monetary_quintile
    FROM customer_orders
)
SELECT
    monetary_quintile,
    COUNT(customer_id) AS customer_count,
    ROUND(SUM(total_spend), 2) AS quintile_revenue,
    ROUND(AVG(total_spend), 2) AS avg_customer_spend,
    ROUND(AVG(order_frequency), 1) AS avg_orders_per_customer
FROM customer_ranks
GROUP BY monetary_quintile
ORDER BY monetary_quintile ASC;


-- --------------------------------------------------------------------
-- QUERY 5: Aspect-Based Sentiment Breakdown per Product Category
-- --------------------------------------------------------------------
SELECT
    p.category,
    ra.aspect,
    COUNT(ra.review_id) AS total_aspect_mentions,
    ROUND(AVG(ra.sentiment_score), 3) AS avg_sentiment_score,
    ROUND(SUM(CASE WHEN ra.sentiment = 'Positive' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(ra.review_id), 1) AS positive_pct,
    ROUND(SUM(CASE WHEN ra.sentiment = 'Negative' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(ra.review_id), 1) AS negative_pct
FROM review_aspects ra
INNER JOIN products p ON ra.product_id = p.product_id
GROUP BY p.category, ra.aspect
HAVING COUNT(ra.review_id) >= 10
ORDER BY p.category, total_aspect_mentions DESC;
