-- Example student solution sketch for Lesson 01 homework (Greenplum 6.25).
-- Database: mentor.

CREATE TABLE lesson01.fact_sales_student_good (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    status text NOT NULL,
    sale_date date NOT NULL,
    amount numeric(12, 2) NOT NULL,
    loaded_at timestamp NOT NULL
)
WITH (
    appendonly=true,
    orientation=column,
    compresstype=zstd,
    compresslevel=1
)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date)
(
    START (DATE '2026-01-01') INCLUSIVE END (DATE '2026-04-01') EXCLUSIVE
    EVERY (INTERVAL '1 month'),
    DEFAULT PARTITION extra
);

INSERT INTO lesson01.fact_sales_student_good
SELECT *
FROM lesson01.fact_sales_bad
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-04-01';

ANALYZE lesson01.fact_sales_student_good;

-- Validation before/after: compare plan shape, runtime and segment row spread
-- against lesson01.fact_sales_bad before accepting the storage redesign.
EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_student_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;

SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_student_good
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
