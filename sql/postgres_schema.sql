-- ====================================================================
-- E-commerce Customer Intelligence Platform - PostgreSQL Schema
-- ====================================================================

DROP TABLE IF EXISTS review_aspects CASCADE;
DROP TABLE IF EXISTS interactions CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- 1. Customers Table
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(20) NOT NULL,
    age INTEGER,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    membership_type VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    preferred_category VARCHAR(100) NOT NULL
);

-- 2. Products Table
CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    product_description TEXT
);

-- 3. Transactions Table
CREATE TABLE transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    transaction_date TIMESTAMP NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    discount_percentage NUMERIC(5, 2) NOT NULL,
    discount_amount NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    return_status VARCHAR(50) NOT NULL
);

-- 4. Reviews Table
CREATE TABLE reviews (
    review_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    review_date TIMESTAMP NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT
);

-- 5. Interactions Table
CREATE TABLE interactions (
    interaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    session_id VARCHAR(100) NOT NULL
);

-- 6. Review Aspects Table
CREATE TABLE review_aspects (
    aspect_id SERIAL PRIMARY KEY,
    review_id VARCHAR(20) NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    aspect VARCHAR(50) NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    sentiment_score NUMERIC(4, 2) NOT NULL
);

-- PostgreSQL Performance Indexes
CREATE INDEX idx_pg_txns_cust ON transactions(customer_id);
CREATE INDEX idx_pg_txns_prod ON transactions(product_id);
CREATE INDEX idx_pg_txns_date ON transactions(transaction_date);
CREATE INDEX idx_pg_rev_prod ON reviews(product_id);
CREATE INDEX idx_pg_inter_cust ON interactions(customer_id);
CREATE INDEX idx_pg_aspect_name ON review_aspects(aspect);
