-- Greenplum 6.25 lesson 01: storage models and partitioning intro.
-- Database: mentor. Stand: greenplum-625.
--
-- Safe run pattern:
--   BEGIN;
--   \i /mentor-lab/examples/storage-and-partitioning.sql
--   ROLLBACK;
--
-- Mentor question: why partition key is not the same as distribution key?
-- Expected answer: partition key helps pruning/retention, distribution key
-- decides how rows are placed across segments and whether joins are co-located.
--
-- GP6 note: use appendonly=true (not GP7 appendoptimized).

CREATE SCHEMA IF NOT EXISTS lesson01;

DROP TABLE IF EXISTS lesson01.storage_heap_demo CASCADE;
DROP TABLE IF EXISTS lesson01.storage_ao_row_demo CASCADE;
DROP TABLE IF EXISTS lesson01.storage_aoco_demo CASCADE;
DROP TABLE IF EXISTS lesson01.fact_sales_partition_bad CASCADE;
DROP TABLE IF EXISTS lesson01.fact_sales_partition_good CASCADE;

\echo '1. Heap demo: row storage, good for mutable/small tables'

CREATE TABLE lesson01.storage_heap_demo (
    sale_id bigint,
    customer_id integer,
    product_id integer,
    sale_date date,
    amount numeric(12, 2),
    status text
)
DISTRIBUTED BY (customer_id);

\echo '2. AO row demo: append-optimized row storage for append-heavy analytics'

CREATE TABLE lesson01.storage_ao_row_demo (
    sale_id bigint,
    customer_id integer,
    product_id integer,
    sale_date date,
    amount numeric(12, 2),
    status text
)
WITH (appendonly=true, orientation=row, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id);

\echo '3. AOCO demo: column-oriented append-optimized storage'

CREATE TABLE lesson01.storage_aoco_demo (
    sale_id bigint,
    customer_id integer,
    product_id integer,
    sale_date date,
    amount numeric(12, 2) ENCODING (compresstype=zstd, compresslevel=3),
    status text,
    payload text ENCODING (compresstype=zstd, compresslevel=5)
)
WITH (appendonly=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id);

INSERT INTO lesson01.storage_heap_demo
SELECT
    sale_id,
    customer_id,
    product_id,
    sale_date,
    amount,
    status
FROM lesson01.fact_sales_good
LIMIT 5000;

INSERT INTO lesson01.storage_ao_row_demo
SELECT *
FROM lesson01.storage_heap_demo;

INSERT INTO lesson01.storage_aoco_demo
SELECT
    sale_id,
    customer_id,
    product_id,
    sale_date,
    amount,
    status,
    repeat('columnar-compression-demo-', 3) AS payload
FROM lesson01.storage_heap_demo;

\echo '4. Storage catalog check (GP6): relstorage h=heap, a=AO row, c=AO column'

SELECT
    n.nspname AS schema_name,
    c.relname,
    c.relstorage,
    CASE c.relstorage
        WHEN 'h' THEN 'heap'
        WHEN 'a' THEN 'ao_row'
        WHEN 'c' THEN 'aoco'
        ELSE c.relstorage::text
    END AS storage_kind
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'lesson01'
  AND c.relname IN (
      'storage_heap_demo',
      'storage_ao_row_demo',
      'storage_aoco_demo'
  )
ORDER BY c.relname;

\echo '5. Bad partitioning example: typical filter is sale_date, but table is partitioned by loaded_at'

CREATE TABLE lesson01.fact_sales_partition_bad (
    sale_id bigint,
    customer_id integer,
    product_id integer,
    sale_date date,
    loaded_at timestamp,
    amount numeric(12, 2)
)
WITH (appendonly=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (loaded_at)
(
    START (TIMESTAMP '2026-01-01') INCLUSIVE
    END (TIMESTAMP '2027-01-01') EXCLUSIVE
    EVERY (INTERVAL '1 month')
);

INSERT INTO lesson01.fact_sales_partition_bad
SELECT
    sale_id,
    customer_id,
    product_id,
    sale_date,
    current_timestamp AS loaded_at,
    amount
FROM lesson01.fact_sales_good
LIMIT 10000;

\echo '6. Good partitioning example: PARTITION BY RANGE (sale_date) supports pruning by reporting date'

CREATE TABLE lesson01.fact_sales_partition_good (
    sale_id bigint,
    customer_id integer,
    product_id integer,
    sale_date date,
    loaded_at timestamp,
    amount numeric(12, 2)
)
WITH (appendonly=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date)
(
    START (DATE '2026-01-01') INCLUSIVE
    END (DATE '2026-04-01') EXCLUSIVE
    EVERY (INTERVAL '1 month')
);

INSERT INTO lesson01.fact_sales_partition_good
SELECT
    sale_id,
    customer_id,
    product_id,
    sale_date,
    loaded_at,
    amount
FROM lesson01.fact_sales_good
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-04-01'
LIMIT 10000;

ANALYZE lesson01.storage_heap_demo;
ANALYZE lesson01.storage_ao_row_demo;
ANALYZE lesson01.storage_aoco_demo;
ANALYZE lesson01.fact_sales_partition_bad;
ANALYZE lesson01.fact_sales_partition_good;

\echo '7. Compare EXPLAIN plans: partition_bad cannot prune by sale_date; partition_good can'

EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_partition_bad
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01';

EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_partition_good
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01';

\echo '8. Columnstore defaults snippets (GP6 appendonly); do not run gpconfig casually in class'

-- CREATE TABLE lesson01.fact_sales_aoco (...)
-- WITH (appendonly=true, orientation=column, compresstype=zstd, compresslevel=1)
-- DISTRIBUTED BY (customer_id);
--
-- ALTER DATABASE mentor
-- SET gp_default_storage_options =
-- 'appendonly=true, orientation=column, compresstype=zstd, compresslevel=1';
