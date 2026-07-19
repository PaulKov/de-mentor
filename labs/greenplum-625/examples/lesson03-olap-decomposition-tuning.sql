-- Greenplum 6.25 Lesson 03: декомпозиция OLAP + Legacy planner vs GPORCA.
--
-- Stand: labs/greenplum-625 (andruche/greenplum:6.25.3)
-- Database: mentor (как Lessons 01/02). Schema: lesson03.
-- Safe pattern:
--   BEGIN;
--   \i /mentor-lab/examples/lesson03-olap-decomposition-tuning.sql
--   ROLLBACK;
--
-- Ключевые демо:
--   SET optimizer = on;   -- GPORCA
--   SET optimizer = off;  -- legacy Postgres planner
--   EXPLAIN ...

CREATE SCHEMA IF NOT EXISTS lesson03;

DROP TABLE IF EXISTS lesson03.fact_sales CASCADE;
DROP TABLE IF EXISTS lesson03.dim_customer CASCADE;
DROP TABLE IF EXISTS lesson03.dim_product CASCADE;
DROP TABLE IF EXISTS lesson03.fact_sales_heap_demo CASCADE;
DROP TABLE IF EXISTS lesson03.fact_sales_ao_row_demo CASCADE;

\echo '01. Dimensions (Heap)'
CREATE TABLE lesson03.dim_customer (
    customer_id integer,
    region text NOT NULL,
    segment text NOT NULL,
    full_name text NOT NULL
)
DISTRIBUTED BY (customer_id);

CREATE TABLE lesson03.dim_product (
    product_id integer,
    category text NOT NULL,
    brand text NOT NULL,
    attrs text NOT NULL DEFAULT '{}'
)
DISTRIBUTED BY (product_id);

INSERT INTO lesson03.dim_customer
SELECT
    gs AS customer_id,
    (ARRAY['eu', 'us', 'apac', 'latam'])[1 + (gs % 4)] AS region,
    CASE WHEN gs % 17 = 0 THEN 'test' ELSE (ARRAY['smb', 'mid', 'enterprise'])[1 + (gs % 3)] END AS segment,
    'customer-' || gs::text AS full_name
FROM generate_series(1, 5000) AS gs;

INSERT INTO lesson03.dim_product
SELECT
    gs AS product_id,
    (ARRAY['compute', 'storage', 'network', 'security'])[1 + (gs % 4)] AS category,
    'brand-' || ((gs % 20) + 1)::text AS brand,
    '{"sku":"sku-' || gs::text || '"}' AS attrs
FROM generate_series(1, 800) AS gs;

\echo '02. Fact AOCO (GP6: appendonly=true, orientation=column)'
CREATE TABLE lesson03.fact_sales (
    sale_id bigint,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    sale_date date NOT NULL,
    amount numeric(12, 2) NOT NULL,
    payload text NOT NULL
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date)
(
    START ('2026-01-01'::date) INCLUSIVE END ('2026-02-01'::date) EXCLUSIVE,
    START ('2026-02-01'::date) INCLUSIVE END ('2026-03-01'::date) EXCLUSIVE,
    START ('2026-03-01'::date) INCLUSIVE END ('2026-04-01'::date) EXCLUSIVE,
    DEFAULT PARTITION extra
);

INSERT INTO lesson03.fact_sales
SELECT
    gs AS sale_id,
    1 + (gs % 5000) AS customer_id,
    1 + (gs % 800) AS product_id,
    DATE '2026-01-01' + ((gs % 75)::int) AS sale_date,
    round((5 + (gs % 700))::numeric / 3, 2) AS amount,
    repeat('x', 20 + (gs % 40)) AS payload
FROM generate_series(1, 120000) AS gs;

\echo '03. Storage demos'
CREATE TABLE lesson03.fact_sales_heap_demo (
    sale_id bigint,
    customer_id integer NOT NULL,
    amount numeric(12, 2) NOT NULL,
    note text NOT NULL
)
DISTRIBUTED BY (customer_id);

CREATE TABLE lesson03.fact_sales_ao_row_demo (
    sale_id bigint,
    customer_id integer NOT NULL,
    amount numeric(12, 2) NOT NULL,
    note text NOT NULL
)
WITH (appendonly = true, orientation = row)
DISTRIBUTED BY (customer_id);

INSERT INTO lesson03.fact_sales_heap_demo
SELECT sale_id, customer_id, amount, left(payload, 16)
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-02-08';

INSERT INTO lesson03.fact_sales_ao_row_demo
SELECT sale_id, customer_id, amount, left(payload, 16)
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-02-08';

\echo '04. ANALYZE + heavy view'
ANALYZE lesson03.dim_customer;
ANALYZE lesson03.dim_product;
ANALYZE lesson03.fact_sales;
ANALYZE lesson03.fact_sales_heap_demo;
ANALYZE lesson03.fact_sales_ao_row_demo;

CREATE OR REPLACE VIEW lesson03.v_heavy_olap_monolith AS
SELECT
    c.region,
    d.category,
    sum(f.amount) AS revenue,
    rank() OVER (PARTITION BY c.region ORDER BY sum(f.amount) DESC) AS category_rank
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
JOIN lesson03.dim_product d ON d.product_id = f.product_id
WHERE f.sale_date >= DATE '2026-02-01'
  AND f.sale_date < DATE '2026-03-01'
  AND c.segment <> 'test'
GROUP BY c.region, d.category;

\echo '05. Multi-join star for ORCA vs Legacy (5 joins)'
CREATE OR REPLACE VIEW lesson03.v_star_join_orca_case AS
SELECT
    c.region,
    d.category,
    d.brand,
    date_trunc('week', f.sale_date)::date AS week_start,
    count(*) AS orders_count,
    sum(f.amount) AS revenue
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
JOIN lesson03.dim_product d ON d.product_id = f.product_id
JOIN lesson03.dim_customer c2 ON c2.customer_id = f.customer_id
JOIN lesson03.dim_product d2 ON d2.product_id = f.product_id
WHERE f.sale_date >= DATE '2026-02-01'
  AND f.sale_date < DATE '2026-03-01'
  AND c.segment <> 'test'
  AND c2.segment = c.segment
  AND d2.category = d.category
GROUP BY c.region, d.category, d.brand, date_trunc('week', f.sale_date)::date;

\echo '06. TEMP decomposition'
CREATE TEMP TABLE tmp_lesson03_sales_feb
ON COMMIT PRESERVE ROWS
AS
SELECT f.customer_id, f.product_id, f.amount
FROM lesson03.fact_sales f
WHERE f.sale_date >= DATE '2026-02-01'
  AND f.sale_date < DATE '2026-03-01'
DISTRIBUTED BY (customer_id);

ANALYZE tmp_lesson03_sales_feb;

CREATE TEMP TABLE tmp_lesson03_sales_shaped
ON COMMIT PRESERVE ROWS
AS
SELECT
    c.region,
    d.category,
    sum(t.amount) AS revenue
FROM tmp_lesson03_sales_feb t
JOIN lesson03.dim_customer c ON c.customer_id = t.customer_id
JOIN lesson03.dim_product d ON d.product_id = t.product_id
WHERE c.segment <> 'test'
GROUP BY c.region, d.category
DISTRIBUTED BY (region);

ANALYZE tmp_lesson03_sales_shaped;

\echo '07. Optimizer probe helpers (run manually in class)'
-- SET optimizer = on;   -- GPORCA
-- EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case;
-- SET optimizer = off;  -- legacy planner
-- EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case;
-- SHOW optimizer;
-- SELECT name, setting FROM pg_settings WHERE name LIKE 'optimizer%' ORDER BY 1;

SELECT 'lesson03@gp6.25 ready' AS status;
SELECT version() AS gp_version;
SELECT current_setting('optimizer') AS optimizer_default;
SELECT count(*) AS fact_rows FROM lesson03.fact_sales;
