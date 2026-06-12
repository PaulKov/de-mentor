INSERT INTO lesson01.dim_customers (
    customer_id,
    customer_name,
    region,
    segment,
    registered_at
)
SELECT
    customer_id,
    'customer_' || customer_id AS customer_name,
    CASE customer_id % 5
        WHEN 0 THEN 'Moscow'
        WHEN 1 THEN 'Saint Petersburg'
        WHEN 2 THEN 'Kazan'
        WHEN 3 THEN 'Novosibirsk'
        ELSE 'Yekaterinburg'
    END AS region,
    CASE customer_id % 4
        WHEN 0 THEN 'enterprise'
        WHEN 1 THEN 'midmarket'
        WHEN 2 THEN 'small_business'
        ELSE 'individual'
    END AS segment,
    DATE '2025-01-01' + (customer_id % 365) AS registered_at
FROM generate_series(1, 2000) AS gs(customer_id);

INSERT INTO lesson01.dim_products (
    product_id,
    product_name,
    category,
    price
)
SELECT
    product_id,
    'product_' || product_id AS product_name,
    CASE product_id % 6
        WHEN 0 THEN 'books'
        WHEN 1 THEN 'electronics'
        WHEN 2 THEN 'home'
        WHEN 3 THEN 'sport'
        WHEN 4 THEN 'beauty'
        ELSE 'games'
    END AS category,
    round((50 + random() * 950)::numeric, 2) AS price
FROM generate_series(1, 200) AS gs(product_id);

INSERT INTO lesson01.fact_sales_bad (
    sale_id,
    customer_id,
    product_id,
    status,
    sale_date,
    amount,
    loaded_at
)
SELECT
    sale_id,
    ((sale_id * 37) % 2000) + 1 AS customer_id,
    ((sale_id * 17) % 200) + 1 AS product_id,
    CASE
        WHEN sale_id % 100 < 90 THEN 'paid'
        WHEN sale_id % 100 < 97 THEN 'cancelled'
        WHEN sale_id % 100 < 99 THEN 'returned'
        ELSE 'fraud_review'
    END AS status,
    DATE '2026-01-01' + (sale_id % 90) AS sale_date,
    round((10 + random() * 490)::numeric, 2) AS amount,
    current_timestamp AS loaded_at
FROM generate_series(1, 50000) AS gs(sale_id);

INSERT INTO lesson01.fact_sales_good
SELECT *
FROM lesson01.fact_sales_bad;

ANALYZE lesson01.dim_customers;
ANALYZE lesson01.dim_products;
ANALYZE lesson01.fact_sales_bad;
ANALYZE lesson01.fact_sales_good;

