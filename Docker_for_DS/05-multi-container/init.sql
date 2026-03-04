-- ============================================================
-- Database initialization script.
-- Runs automatically on first PostgreSQL container start.
-- Creates sample tables with data for learning and exploration.
-- ============================================================

-- Sample sales table
CREATE TABLE IF NOT EXISTS sample_sales (
    id          SERIAL PRIMARY KEY,
    sale_date   DATE NOT NULL,
    product     VARCHAR(100) NOT NULL,
    category    VARCHAR(50) NOT NULL,
    region      VARCHAR(50) NOT NULL,
    units_sold  INTEGER NOT NULL,
    unit_price  NUMERIC(10, 2) NOT NULL,
    revenue     NUMERIC(12, 2) GENERATED ALWAYS AS (units_sold * unit_price) STORED
);

-- Insert sample data
INSERT INTO sample_sales (sale_date, product, category, region, units_sold, unit_price)
VALUES
    ('2024-01-15', 'Laptop Pro 15',   'Electronics', 'North',  12, 1299.99),
    ('2024-01-15', 'Wireless Mouse',  'Electronics', 'South',  45,   29.99),
    ('2024-01-16', 'Standing Desk',   'Furniture',   'East',    8,  449.00),
    ('2024-01-16', 'Ergonomic Chair', 'Furniture',   'West',   15,  299.00),
    ('2024-01-17', 'USB Hub',         'Electronics', 'North',  60,   34.99),
    ('2024-01-18', 'Monitor 27"',     'Electronics', 'East',   20,  399.00),
    ('2024-01-19', 'Laptop Pro 15',   'Electronics', 'West',    9, 1299.99),
    ('2024-01-20', 'Webcam HD',       'Electronics', 'South',  33,   79.99),
    ('2024-01-21', 'Standing Desk',   'Furniture',   'North',   4,  449.00),
    ('2024-01-22', 'Mechanical KB',   'Electronics', 'East',   28,  139.99),
    ('2024-02-01', 'Laptop Pro 15',   'Electronics', 'South',  18, 1299.99),
    ('2024-02-03', 'Wireless Mouse',  'Electronics', 'North',  70,   29.99),
    ('2024-02-05', 'Standing Desk',   'Furniture',   'West',   11,  449.00),
    ('2024-02-07', 'USB Hub',         'Electronics', 'South',  44,   34.99),
    ('2024-02-10', 'Monitor 27"',     'Electronics', 'North',  16,  399.00),
    ('2024-03-01', 'Ergonomic Chair', 'Furniture',   'East',   25,  299.00),
    ('2024-03-05', 'Webcam HD',       'Electronics', 'West',   50,   79.99),
    ('2024-03-10', 'Mechanical KB',   'Electronics', 'South',  19,  139.99),
    ('2024-03-15', 'Laptop Pro 15',   'Electronics', 'North',  22, 1299.99),
    ('2024-03-20', 'Wireless Mouse',  'Electronics', 'East',   85,   29.99);

-- Sample ML experiments tracking table
CREATE TABLE IF NOT EXISTS ml_experiments (
    id              SERIAL PRIMARY KEY,
    experiment_name VARCHAR(200) NOT NULL,
    model_type      VARCHAR(100) NOT NULL,
    hyperparameters JSONB,
    train_accuracy  NUMERIC(6, 4),
    test_accuracy   NUMERIC(6, 4),
    cv_mean         NUMERIC(6, 4),
    cv_std          NUMERIC(6, 4),
    features_used   TEXT[],
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Insert some sample experiment records
INSERT INTO ml_experiments (
    experiment_name, model_type, hyperparameters,
    train_accuracy, test_accuracy, cv_mean, cv_std,
    features_used, notes
)
VALUES
    (
        'iris-baseline-rf',
        'RandomForestClassifier',
        '{"n_estimators": 100, "max_depth": 5, "random_state": 42}',
        0.9917, 0.9667, 0.9533, 0.0245,
        ARRAY['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)'],
        'Baseline run with default hyperparameters'
    ),
    (
        'iris-deep-rf',
        'RandomForestClassifier',
        '{"n_estimators": 200, "max_depth": 10, "random_state": 42}',
        1.0000, 0.9667, 0.9600, 0.0200,
        ARRAY['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)'],
        'Deeper trees -- slight overfit on training set'
    ),
    (
        'iris-logistic',
        'LogisticRegression',
        '{"C": 1.0, "max_iter": 200, "random_state": 42}',
        0.9750, 0.9333, 0.9400, 0.0316,
        ARRAY['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)'],
        'Linear model baseline for comparison'
    );

-- Useful views
CREATE OR REPLACE VIEW sales_by_category_month AS
SELECT
    DATE_TRUNC('month', sale_date) AS month,
    category,
    SUM(revenue)                   AS total_revenue,
    SUM(units_sold)                AS total_units
FROM sample_sales
GROUP BY 1, 2
ORDER BY 1, 2;

CREATE OR REPLACE VIEW top_products AS
SELECT
    product,
    category,
    SUM(revenue)                            AS total_revenue,
    SUM(units_sold)                         AS total_units,
    ROUND(AVG(unit_price), 2)               AS avg_price,
    COUNT(*)                                AS num_transactions
FROM sample_sales
GROUP BY product, category
ORDER BY total_revenue DESC;
