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
    900000 + sale_id,
    ((sale_id * 41) % 2000) + 1,
    ((sale_id * 19) % 200) + 1,
    'paid',
    DATE '2025-12-15' + (sale_id % 10),
    round((25 + random() * 300)::numeric, 2),
    current_timestamp
FROM generate_series(1, 1000) AS gs(sale_id);

ANALYZE lesson01.fact_sales_bad;
