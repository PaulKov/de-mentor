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
    CASE
        WHEN sale_id % 10 < 4 THEN ((sale_id * 7) % 20) + 1
        ELSE ((sale_id * 37) % 1980) + 21
    END AS customer_id,
    ((sale_id * 17) % 200) + 1 AS product_id,
    CASE
        WHEN sale_id % 100 < 90 THEN 'paid'
        WHEN sale_id % 100 < 97 THEN 'cancelled'
        WHEN sale_id % 100 < 99 THEN 'returned'
        ELSE 'fraud_review'
    END AS status,
    DATE '2026-01-01' + (sale_id % 90) AS sale_date,
    CASE
        WHEN sale_id % 10 < 4 THEN round((2000 + random() * 8000)::numeric, 2)
        ELSE round((20 + random() * 280)::numeric, 2)
    END AS amount,
    current_timestamp AS loaded_at
FROM generate_series(1, 50000) AS gs(sale_id);

INSERT INTO lesson01.fact_sales_good
SELECT *
FROM lesson01.fact_sales_bad;

ANALYZE lesson01.fact_sales_bad;
ANALYZE lesson01.fact_sales_good;

