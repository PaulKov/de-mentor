-- Storage lab: Heap vs AO row vs AOCO on the same sample + catalog.
-- Database: mentor.

\echo '=== 0. fact_sales storage options / appendonly catalog ==='
SELECT c.relname,
       a.blocksize,
       a.compresslevel,
       a.compresstype,
       a.columnstore,
       a.segrelid::regclass AS segrel,
       a.blkdirrelid::regclass AS blkdir,
       a.visimaprelid::regclass AS visimap
FROM pg_class c
JOIN pg_appendonly a ON a.relid = c.oid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'lesson03' AND c.relname = 'fact_sales';

\echo '=== 1. Sizes: fact (AOCO) vs dims (heap-like) ==='
SELECT c.relname,
       pg_size_pretty(pg_total_relation_size(c.oid)) AS total,
       pg_size_pretty(pg_relation_size(c.oid)) AS main
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'lesson03'
  AND c.relkind = 'r'
ORDER BY pg_total_relation_size(c.oid) DESC;

\echo '=== 2. Mini clones: same 5k rows → Heap / AO row / AOCO ==='
DROP TABLE IF EXISTS lesson03.storage_demo_heap;
DROP TABLE IF EXISTS lesson03.storage_demo_ao;
DROP TABLE IF EXISTS lesson03.storage_demo_aoco;

CREATE TABLE lesson03.storage_demo_heap AS
SELECT customer_id, product_id, amount, sale_date,
       repeat('x', 64) AS payload
FROM lesson03.fact_sales
LIMIT 5000
DISTRIBUTED BY (customer_id);

CREATE TABLE lesson03.storage_demo_ao (
  LIKE lesson03.storage_demo_heap INCLUDING DEFAULTS
)
WITH (appendoptimized=true, orientation=row, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id);
INSERT INTO lesson03.storage_demo_ao SELECT * FROM lesson03.storage_demo_heap;

CREATE TABLE lesson03.storage_demo_aoco (
  LIKE lesson03.storage_demo_heap INCLUDING DEFAULTS
)
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id);
INSERT INTO lesson03.storage_demo_aoco SELECT * FROM lesson03.storage_demo_heap;

ANALYZE lesson03.storage_demo_heap;
ANALYZE lesson03.storage_demo_ao;
ANALYZE lesson03.storage_demo_aoco;

SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) AS total
FROM pg_class
WHERE oid IN (
  'lesson03.storage_demo_heap'::regclass,
  'lesson03.storage_demo_ao'::regclass,
  'lesson03.storage_demo_aoco'::regclass
);

\echo '=== 3. Narrow vs wide scan (compare EXPLAIN ANALYZE times) ==='
EXPLAIN ANALYZE
SELECT customer_id, amount FROM lesson03.storage_demo_aoco WHERE amount > 50;

EXPLAIN ANALYZE
SELECT * FROM lesson03.storage_demo_aoco WHERE amount > 50;

EXPLAIN ANALYZE
SELECT customer_id, amount FROM lesson03.storage_demo_heap WHERE amount > 50;

EXPLAIN ANALYZE
SELECT * FROM lesson03.storage_demo_heap WHERE amount > 50;

\echo '=== Cleanup (optional) ==='
-- DROP TABLE lesson03.storage_demo_heap, lesson03.storage_demo_ao, lesson03.storage_demo_aoco;
