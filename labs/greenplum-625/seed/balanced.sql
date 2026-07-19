TRUNCATE TABLE lesson01.fact_sales_bad;
TRUNCATE TABLE lesson01.fact_sales_good;

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
    ((sale_id * 41) % 2000) + 1 AS customer_id,
    ((sale_id * 19) % 200) + 1 AS product_id,
    CASE sale_id % 4
        WHEN 0 THEN 'paid'
        WHEN 1 THEN 'cancelled'
        WHEN 2 THEN 'returned'
        ELSE 'fraud_review'
    END AS status,
    DATE '2026-01-01' + (sale_id % 90) AS sale_date,
    round((20 + random() * 180)::numeric, 2) AS amount,
    current_timestamp AS loaded_at
FROM generate_series(1, 50000) AS gs(sale_id);

INSERT INTO lesson01.fact_sales_good
SELECT *
FROM lesson01.fact_sales_bad;

ANALYZE lesson01.fact_sales_bad;
ANALYZE lesson01.fact_sales_good;

