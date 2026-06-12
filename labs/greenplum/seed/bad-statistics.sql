INSERT INTO lesson01.fact_sales_good (
    sale_id,
    customer_id,
    product_id,
    status,
    sale_date,
    amount,
    loaded_at
)
SELECT
    910000 + sale_id,
    42,
    ((sale_id * 23) % 200) + 1,
    'paid',
    DATE '2026-03-01' + (sale_id % 5),
    round((100 + random() * 900)::numeric, 2),
    current_timestamp
FROM generate_series(1, 5000) AS gs(sale_id);

-- Intentionally no ANALYZE: this profile is for stale-statistics investigation.
