-- ====================================================================
-- E-commerce Customer Intelligence Platform - Power BI Star-Schema Views
-- ====================================================================

-- 1. DimDate
CREATE VIEW IF NOT EXISTS DimDate AS
WITH RECURSIVE dates(d) AS (
    SELECT '2023-01-01'
    UNION ALL
    SELECT DATE(d, '+1 day') FROM dates WHERE d < '2024-12-31'
)
SELECT
    REPLACE(d, '-', '') AS date_key,
    d AS full_date,
    CAST(SUBSTR(d, 1, 4) AS INTEGER) AS year,
    CAST(SUBSTR(d, 6, 2) AS INTEGER) AS month,
    CASE SUBSTR(d, 6, 2)
        WHEN '01' THEN 'January' WHEN '02' THEN 'February' WHEN '03' THEN 'March'
        WHEN '04' THEN 'April'   WHEN '05' THEN 'May'      WHEN '06' THEN 'June'
        WHEN '07' THEN 'July'    WHEN '08' THEN 'August'   WHEN '09' THEN 'September'
        WHEN '10' THEN 'October' WHEN '11' THEN 'November' WHEN '12' THEN 'December'
    END AS month_name,
    'Q' || CAST(((CAST(SUBSTR(d, 6, 2) AS INTEGER) - 1) / 3) + 1 AS TEXT) AS quarter,
    CASE STRFTIME('%w', d)
        WHEN '0' THEN 'Sunday'    WHEN '1' THEN 'Monday'   WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday'
        ELSE 'Saturday'
    END AS day_of_week
FROM dates;

-- 2. DimCustomer
CREATE VIEW IF NOT EXISTS DimCustomer AS
SELECT
    customer_id,
    gender,
    age,
    city,
    country,
    membership_type,
    signup_date,
    customer_segment,
    preferred_category
FROM customers;

-- 3. DimProduct
CREATE VIEW IF NOT EXISTS DimProduct AS
SELECT
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    price
FROM products;

-- 4. DimCategory
CREATE VIEW IF NOT EXISTS DimCategory AS
SELECT
    category,
    COUNT(DISTINCT subcategory) AS subcategory_count,
    COUNT(product_id) AS product_count,
    ROUND(AVG(price), 2) AS avg_category_price
FROM products
GROUP BY category;

-- 5. FactSales
CREATE VIEW IF NOT EXISTS FactSales AS
SELECT
    t.transaction_id,
    t.customer_id,
    t.product_id,
    REPLACE(SUBSTR(t.transaction_date, 1, 10), '-', '') AS date_key,
    t.transaction_date,
    t.quantity,
    t.unit_price,
    t.discount_percentage,
    t.discount_amount,
    t.total_amount,
    t.payment_method,
    t.return_status,
    CASE WHEN t.return_status = 'Returned' THEN 1 ELSE 0 END AS is_returned,
    CASE WHEN t.return_status != 'Returned' THEN t.total_amount ELSE 0.0 END AS net_sales_amount
FROM transactions t;

-- 6. FactReviews
CREATE VIEW IF NOT EXISTS FactReviews AS
SELECT
    r.review_id,
    r.customer_id,
    r.product_id,
    REPLACE(SUBSTR(r.review_date, 1, 10), '-', '') AS date_key,
    r.review_date,
    r.rating,
    CASE
        WHEN r.rating >= 4 THEN 'Positive'
        WHEN r.rating = 3 THEN 'Neutral'
        ELSE 'Negative'
    END AS sentiment,
    r.review_text
FROM reviews r;

-- 7. FactInteractions
CREATE VIEW IF NOT EXISTS FactInteractions AS
SELECT
    i.interaction_id,
    i.customer_id,
    i.product_id,
    REPLACE(SUBSTR(i.timestamp, 1, 10), '-', '') AS date_key,
    i.timestamp,
    i.interaction_type,
    CASE i.interaction_type
        WHEN 'view' THEN 1.0
        WHEN 'click' THEN 2.0
        WHEN 'wishlist' THEN 3.0
        WHEN 'cart' THEN 4.0
        WHEN 'purchase' THEN 5.0
        ELSE 1.0
    END AS interaction_weight,
    i.session_id
FROM interactions i;
