DROP TABLE IF EXISTS lesson01.fact_daily_sales_bad_partition;

CREATE TABLE lesson01.fact_daily_sales_bad_partition (
    sale_date date NOT NULL,
    load_date date NOT NULL,
    region text NOT NULL,
    revenue numeric(14, 2) NOT NULL
)
DISTRIBUTED BY (region);

INSERT INTO lesson01.fact_daily_sales_bad_partition
SELECT
    DATE '2026-01-01' + (day_id % 90) AS sale_date,
    DATE '2026-04-01' AS load_date,
    CASE day_id % 5
        WHEN 0 THEN 'Moscow'
        WHEN 1 THEN 'Saint Petersburg'
        WHEN 2 THEN 'Kazan'
        WHEN 3 THEN 'Novosibirsk'
        ELSE 'Yekaterinburg'
    END AS region,
    round((1000 + random() * 20000)::numeric, 2) AS revenue
FROM generate_series(1, 1000) AS gs(day_id);

ANALYZE lesson01.fact_daily_sales_bad_partition;
