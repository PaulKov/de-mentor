-- Greenplum lesson 02: partitioning, statistics and incremental loads.
--
-- Safe run pattern:
--   BEGIN;
--   \i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
--   ROLLBACK;
--
-- Mentor anchor:
--   partition key supports pruning and retention;
--   distribution key controls segment placement and join locality;
--   ANALYZE after load is part of the MPP load contract.

CREATE SCHEMA IF NOT EXISTS lesson02;

DROP TABLE IF EXISTS lesson02.fact_sales_stage CASCADE;
DROP TABLE IF EXISTS lesson02.fact_sales_partitioned CASCADE;
DROP TABLE IF EXISTS lesson02.fact_sales_bad_partition_key CASCADE;

\echo '01. Bad partition key: loaded_at does not help sale_date reporting filters'
CREATE TABLE lesson02.fact_sales_bad_partition_key (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    sale_date date NOT NULL,
    loaded_at timestamp NOT NULL,
    amount numeric(12, 2) NOT NULL,
    source_system text NOT NULL
)
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (loaded_at);

CREATE TABLE lesson02.fact_sales_bad_partition_key_2026_01
    PARTITION OF lesson02.fact_sales_bad_partition_key
    FOR VALUES FROM (TIMESTAMP '2026-01-01') TO (TIMESTAMP '2026-02-01');

CREATE TABLE lesson02.fact_sales_bad_partition_key_2026_02
    PARTITION OF lesson02.fact_sales_bad_partition_key
    FOR VALUES FROM (TIMESTAMP '2026-02-01') TO (TIMESTAMP '2026-03-01');

\echo '02. Good partition key: PARTITION BY RANGE (sale_date) supports pruning and retention'
CREATE TABLE lesson02.fact_sales_partitioned (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    sale_date date NOT NULL,
    loaded_at timestamp NOT NULL,
    amount numeric(12, 2) NOT NULL,
    source_system text NOT NULL,
    load_batch_id text NOT NULL
)
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date);

CREATE TABLE lesson02.fact_sales_partitioned_2026_01
    PARTITION OF lesson02.fact_sales_partitioned
    FOR VALUES FROM (DATE '2026-01-01') TO (DATE '2026-02-01');

CREATE TABLE lesson02.fact_sales_partitioned_2026_02
    PARTITION OF lesson02.fact_sales_partitioned
    FOR VALUES FROM (DATE '2026-02-01') TO (DATE '2026-03-01');

CREATE TABLE lesson02.fact_sales_partitioned_2026_03
    PARTITION OF lesson02.fact_sales_partitioned
    FOR VALUES FROM (DATE '2026-03-01') TO (DATE '2026-04-01');

CREATE TABLE lesson02.fact_sales_partitioned_default
    PARTITION OF lesson02.fact_sales_partitioned
    DEFAULT;

\echo '03. Stage table for incremental load window and late-arriving facts'
CREATE TABLE lesson02.fact_sales_stage (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    sale_date date NOT NULL,
    loaded_at timestamp NOT NULL,
    amount numeric(12, 2) NOT NULL,
    source_system text NOT NULL,
    load_batch_id text NOT NULL
)
DISTRIBUTED BY (customer_id);

INSERT INTO lesson02.fact_sales_stage
SELECT
    gs AS sale_id,
    1000 + (gs % 200) AS customer_id,
    10 + (gs % 50) AS product_id,
    DATE '2026-02-01' + ((gs % 20)::int) AS sale_date,
    TIMESTAMP '2026-02-25 10:00:00' AS loaded_at,
    round((10 + (gs % 500))::numeric, 2) AS amount,
    'crm' AS source_system,
    'batch-2026-02-25' AS load_batch_id
FROM generate_series(1, 3000) AS gs;

-- late-arriving fact: business date is January, but it arrives in February load.
INSERT INTO lesson02.fact_sales_stage
VALUES
    (900001, 1042, 17, DATE '2026-01-15', TIMESTAMP '2026-02-25 10:05:00', 199.90, 'crm', 'batch-2026-02-25'),
    (900002, 1042, 17, DATE '2026-03-05', TIMESTAMP '2026-03-06 09:00:00', 249.90, 'crm', 'batch-2026-03-06');

\echo '04. Publish stage rows into the partitioned fact'
INSERT INTO lesson02.fact_sales_partitioned
SELECT *
FROM lesson02.fact_sales_stage;

INSERT INTO lesson02.fact_sales_bad_partition_key (
    sale_id,
    customer_id,
    product_id,
    sale_date,
    loaded_at,
    amount,
    source_system
)
SELECT
    sale_id,
    customer_id,
    product_id,
    sale_date,
    loaded_at,
    amount,
    source_system
FROM lesson02.fact_sales_stage
WHERE loaded_at >= TIMESTAMP '2026-02-01'
  AND loaded_at < TIMESTAMP '2026-03-01';

\echo '05. Validation before ANALYZE: stage counts and target partition placement'
SELECT sale_date, count(*) AS rows_count, sum(amount) AS amount_sum
FROM lesson02.fact_sales_stage
GROUP BY sale_date
ORDER BY sale_date;

SELECT
    tableoid::regclass AS physical_partition,
    count(*) AS rows_count,
    min(sale_date) AS min_sale_date,
    max(sale_date) AS max_sale_date
FROM lesson02.fact_sales_partitioned
GROUP BY tableoid::regclass
ORDER BY tableoid::regclass::text;

SELECT
    gp_segment_id,
    count(*) AS rows_count
FROM lesson02.fact_sales_partitioned
GROUP BY gp_segment_id
ORDER BY gp_segment_id;

\echo '06. Statistics policy after incremental load'
ANALYZE lesson02.fact_sales_stage;
ANALYZE lesson02.fact_sales_partitioned;
ANALYZE lesson02.fact_sales_bad_partition_key;

SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson02'
ORDER BY relname;

\echo '07. Partition catalog checks: pg_partition_tree and gp_toolkit.gp_partitions'
SELECT
    tree.level,
    tree.isleaf,
    tree.relid::regclass AS relation_name,
    tree.parentrelid::regclass AS parent_relation
FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass) AS tree
ORDER BY tree.level, tree.relid::regclass::text;

SELECT
    schemaname,
    tablename,
    partitiontablename,
    partitionlevel,
    partitionrank,
    partitionboundary
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson02'
  AND tablename IN ('fact_sales_partitioned', 'fact_sales_bad_partition_key')
ORDER BY tablename, partitionlevel, partitionrank, partitiontablename;

\echo '08. EXPLAIN: bad partition key cannot prune by sale_date as well as the good table'
EXPLAIN
SELECT sum(amount)
FROM lesson02.fact_sales_bad_partition_key
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';

EXPLAIN
SELECT sum(amount)
FROM lesson02.fact_sales_partitioned
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';

\echo '09. Incremental load self-checks for idempotency discussion'
SELECT
    load_batch_id,
    count(*) AS rows_count,
    count(DISTINCT sale_id) AS distinct_sale_ids,
    sum(amount) AS amount_sum
FROM lesson02.fact_sales_partitioned
GROUP BY load_batch_id
ORDER BY load_batch_id;

SELECT customer_id, sale_date, count(*) AS duplicate_candidates
FROM lesson02.fact_sales_partitioned
GROUP BY customer_id, sale_date
HAVING count(*) > 1
ORDER BY duplicate_candidates DESC, customer_id
LIMIT 10;

\echo '10. Maintenance snippets: read in class, execute only in controlled admin practice'
-- Add next month partition:
-- CREATE TABLE lesson02.fact_sales_partitioned_2026_04
--     PARTITION OF lesson02.fact_sales_partitioned
--     FOR VALUES FROM (DATE '2026-04-01') TO (DATE '2026-05-01');
--
-- Retention through metadata boundary:
-- ALTER TABLE lesson02.fact_sales_partitioned
--     DETACH PARTITION lesson02.fact_sales_partitioned_2026_01;
-- DROP TABLE lesson02.fact_sales_partitioned_2026_01;
--
-- Production load contract checklist:
-- 1. load to stage;
-- 2. validate stage row counts and sums;
-- 3. publish touched window idempotently;
-- 4. ANALYZE touched data;
-- 5. store audit evidence for retry and rollback.
