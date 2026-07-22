-- Greenplum 6.25 Lesson 03 — homework / class seed (NO TEMP rewrite).
--
-- Stand: labs/greenplum-625 · Database: mentor · Schema: lesson03
-- Scale via psql: -v scale=small|principal  (CLI: seed ... --scale)
--
-- Graded homework target: lesson03.v_homework_brand_region
-- Class demo monolith:     lesson03.v_heavy_olap_monolith (Feb × category)
-- Do NOT copy class-demo TEMP into graded homework.
--
-- Safe pattern:
--   BEGIN;
--   \i /mentor-lab/examples/lesson03-homework-seed.sql
--   ROLLBACK;

\set ON_ERROR_STOP on
-- Scale: mentor-lab seed passes -v scale=small|principal; default small for bare \i
\if :{?scale}
\else
\set scale small
\endif

CREATE SCHEMA IF NOT EXISTS lesson03;

DROP TABLE IF EXISTS lesson03.seed_meta CASCADE;
DROP TABLE IF EXISTS lesson03.fact_sales CASCADE;
DROP TABLE IF EXISTS lesson03.dim_customer CASCADE;
DROP TABLE IF EXISTS lesson03.dim_product CASCADE;
DROP TABLE IF EXISTS lesson03.fact_sales_heap_demo CASCADE;
DROP TABLE IF EXISTS lesson03.fact_sales_ao_row_demo CASCADE;

CREATE TABLE lesson03.seed_meta (
    key text,
    value text
)
DISTRIBUTED REPLICATED;

\echo '01. Dimensions (Heap) — region↔segment correlation for stats pathology'
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

-- Correlated dims: eu→enterprise-heavy, us→smb-heavy (breaks independence assumptions).
INSERT INTO lesson03.dim_customer
SELECT
    gs AS customer_id,
    (ARRAY['eu', 'us', 'apac', 'latam'])[1 + (gs % 4)] AS region,
    CASE
        WHEN gs % 17 = 0 THEN 'test'
        WHEN (ARRAY['eu', 'us', 'apac', 'latam'])[1 + (gs % 4)] = 'eu'
            AND gs % 5 <> 0 THEN 'enterprise'
        WHEN (ARRAY['eu', 'us', 'apac', 'latam'])[1 + (gs % 4)] = 'us'
            AND gs % 4 <> 0 THEN 'smb'
        ELSE (ARRAY['smb', 'mid', 'enterprise'])[1 + (gs % 3)]
    END AS segment,
    'customer-' || gs::text AS full_name
FROM generate_series(1, 5000) AS gs;

INSERT INTO lesson03.dim_product
SELECT
    gs AS product_id,
    (ARRAY['compute', 'storage', 'network', 'security'])[1 + (gs % 4)] AS category,
    'brand-' || ((gs % 20) + 1)::text AS brand,
    '{"sku":"sku-' || gs::text || '"}' AS attrs
FROM generate_series(1, 800) AS gs;

\echo '02. Fact AOCO — scale + deliberate hot-customer skew (~30% on ids 1..5)'
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

-- Row counts: small=120k, principal=2M (local-friendly Principal stress).
INSERT INTO lesson03.fact_sales
SELECT
    gs AS sale_id,
    CASE
        WHEN gs % 10 < 3 THEN 1 + (gs % 5)              -- hot customers ~30%
        ELSE 1 + (gs % 5000)
    END AS customer_id,
    CASE
        WHEN gs % 11 = 0 THEN 1 + (gs % 7)              -- hot products pocket
        ELSE 1 + (gs % 800)
    END AS product_id,
    DATE '2026-01-01' + ((gs % 90)::int) AS sale_date,  -- Jan–Mar for homework Mar window
    round((5 + (gs % 700))::numeric / 3, 2) AS amount,
    repeat('x', 20 + (gs % 40)) AS payload
FROM generate_series(
    1,
    CASE WHEN :'scale' = 'principal' THEN 2000000 ELSE 120000 END
) AS gs;

\echo '03. Storage demos (class / workbook)'
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

\echo '04. ANALYZE + views'
ANALYZE lesson03.dim_customer;
ANALYZE lesson03.dim_product;
ANALYZE lesson03.fact_sales;
ANALYZE lesson03.fact_sales_heap_demo;
ANALYZE lesson03.fact_sales_ao_row_demo;

-- Class / lecture monolith (Feb × category). Not the graded homework target.
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

-- GRADED homework target: March × brand × region (different grain from class demo).
CREATE OR REPLACE VIEW lesson03.v_homework_brand_region AS
SELECT
    c.region,
    d.brand,
    sum(f.amount) AS revenue,
    count(*) AS order_cnt,
    dense_rank() OVER (PARTITION BY c.region ORDER BY sum(f.amount) DESC) AS brand_rank
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
JOIN lesson03.dim_product d ON d.product_id = f.product_id
WHERE f.sale_date >= DATE '2026-03-01'
  AND f.sale_date < DATE '2026-04-01'
  AND c.segment IN ('smb', 'mid')
  AND d.category <> 'security'
GROUP BY c.region, d.brand;

-- Class/demo only for ORCA vs Legacy join-space. Not graded rewrite target.
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

INSERT INTO lesson03.seed_meta (key, value) VALUES
    ('scale', :'scale'),
    ('graded_view', 'lesson03.v_homework_brand_region'),
    ('class_view', 'lesson03.v_heavy_olap_monolith');

SELECT 'lesson03 homework seed ready (no TEMP rewrite)' AS status;
SELECT :'scale' AS seed_scale;
SELECT count(*) AS fact_rows FROM lesson03.fact_sales;
SELECT count(*) AS homework_result_rows FROM lesson03.v_homework_brand_region;
SELECT version() AS gp_version;
SELECT current_setting('optimizer') AS optimizer_default;
