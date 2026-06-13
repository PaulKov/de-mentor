CREATE TABLE lesson01.fact_student_solution (
    sale_id bigint,
    customer_id bigint,
    sale_date date,
    amount numeric(12, 2)
)
WITH (
    appendoptimized=true,
    orientation=column,
    compresstype=zstd,
    compresslevel=1
)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date)
(
    START (DATE '2026-01-01') END (DATE '2026-04-01') EVERY (INTERVAL '1 month')
);

INSERT INTO lesson01.fact_student_solution
SELECT
    sale_id,
    ((sale_id * 37) % 2000) + 1 AS customer_id,
    DATE '2026-01-01' + (sale_id % 90) AS sale_date,
    round((10 + random() * 490)::numeric, 2) AS amount
FROM generate_series(1, 5000) AS gs(sale_id);

ANALYZE lesson01.fact_student_solution;

EXPLAIN ANALYZE
SELECT customer_id, sum(amount)
FROM lesson01.fact_student_solution
GROUP BY customer_id;

SELECT gp_segment_id, count(*) AS rows_on_segment
FROM lesson01.fact_student_solution
GROUP BY gp_segment_id
ORDER BY gp_segment_id;

-- validation before/after: compare EXPLAIN ANALYZE plan shape and gp_segment_id spread.
