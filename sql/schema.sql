-- ====================================================================
-- E-commerce Customer Intelligence Platform - SQLite Relational Schema
-- ====================================================================

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
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
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    price REAL NOT NULL,
    product_description TEXT
);

-- 3. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_percentage REAL NOT NULL,
    discount_amount REAL NOT NULL,
    total_amount REAL NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    return_status VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 4. Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    review_date TIMESTAMP NOT NULL,
    rating INTEGER NOT NULL,
    review_text TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 5. Interactions Table
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 6. Review Aspects Table (ABSA Outputs)
CREATE TABLE IF NOT EXISTS review_aspects (
    aspect_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    aspect VARCHAR(50) NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    sentiment_score REAL NOT NULL,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indexes for Query Performance
CREATE INDEX IF NOT EXISTS idx_txns_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_txns_product ON transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_txns_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_inter_customer ON interactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_inter_type ON interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_aspects_aspect ON review_aspects(aspect);
