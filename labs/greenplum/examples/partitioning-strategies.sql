-- Greenplum lesson 01: partitioning strategies deep drill.
--
-- This file complements storage-and-partitioning.sql:
--   - RANGE for date pruning and retention.
--   - LIST for finite business categories.
--   - HASH for controlled bucketization when no natural range/list exists.
--   - DEFAULT partition as a safety net for unexpected values.
--   - Inspection queries: pg_partition_tree and gp_toolkit.gp_partitions.
--
-- Safe run pattern:
--   BEGIN;
--   \i /mentor-lab/examples/partitioning-strategies.sql
--   ROLLBACK;
--
-- Mentor anchor: partition key не равен distribution key.
-- Distribution decides segment placement; partitioning decides logical pruning
-- and retention boundaries inside a distributed table.

CREATE SCHEMA IF NOT EXISTS lesson01;

DROP TABLE IF EXISTS lesson01.partition_multilevel_demo CASCADE;
DROP TABLE IF EXISTS lesson01.partition_hash_demo CASCADE;
DROP TABLE IF EXISTS lesson01.partition_list_demo CASCADE;
DROP TABLE IF EXISTS lesson01.partition_range_demo CASCADE;

\echo '01. RANGE strategy: monthly sale_date partitions plus DEFAULT partition'
CREATE TABLE lesson01.partition_range_demo (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    sale_date date NOT NULL,
    region text NOT NULL,
    amount numeric(12, 2) NOT NULL
)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date);

CREATE TABLE lesson01.partition_range_demo_2026_01
    PARTITION OF lesson01.partition_range_demo
    FOR VALUES FROM (DATE '2026-01-01') TO (DATE '2026-02-01');

CREATE TABLE lesson01.partition_range_demo_2026_02
    PARTITION OF lesson01.partition_range_demo
    FOR VALUES FROM (DATE '2026-02-01') TO (DATE '2026-03-01');

CREATE TABLE lesson01.partition_range_demo_2026_03
    PARTITION OF lesson01.partition_range_demo
    FOR VALUES FROM (DATE '2026-03-01') TO (DATE '2026-04-01');

CREATE TABLE lesson01.partition_range_demo_default
    PARTITION OF lesson01.partition_range_demo
    DEFAULT;

INSERT INTO lesson01.partition_range_demo
SELECT
    sale_id,
    customer_id,
    sale_date,
    CASE customer_id % 5
        WHEN 0 THEN 'Moscow'
        WHEN 1 THEN 'Saint Petersburg'
        WHEN 2 THEN 'Kazan'
        WHEN 3 THEN 'Novosibirsk'
        ELSE 'Yekaterinburg'
    END AS region,
    amount
FROM lesson01.fact_sales_good
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-04-01'
LIMIT 12000;

-- DEFAULT partition catches unexpected values. Without DEFAULT, an
-- out-of-range INSERT would fail instead of silently landing somewhere.
INSERT INTO lesson01.partition_range_demo (
    sale_id,
    customer_id,
    sale_date,
    region,
    amount
)
VALUES (900001, 42, DATE '2030-01-01', 'unknown', 10.00);

\echo '02. LIST strategy: region partitions plus DEFAULT partition'
CREATE TABLE lesson01.partition_list_demo (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    sale_date date NOT NULL,
    region text NOT NULL,
    amount numeric(12, 2) NOT NULL
)
DISTRIBUTED BY (customer_id)
PARTITION BY LIST (region);

CREATE TABLE lesson01.partition_list_demo_capitals
    PARTITION OF lesson01.partition_list_demo
    FOR VALUES IN ('Moscow', 'Saint Petersburg');

CREATE TABLE lesson01.partition_list_demo_regions
    PARTITION OF lesson01.partition_list_demo
    FOR VALUES IN ('Kazan', 'Novosibirsk', 'Yekaterinburg');

CREATE TABLE lesson01.partition_list_demo_default
    PARTITION OF lesson01.partition_list_demo
    DEFAULT;

INSERT INTO lesson01.partition_list_demo
SELECT sale_id, customer_id, sale_date, region, amount
FROM lesson01.partition_range_demo
WHERE sale_id <> 900001
LIMIT 5000;

INSERT INTO lesson01.partition_list_demo
VALUES (900002, 77, DATE '2026-02-01', 'Other', 25.00);

\echo '03. HASH strategy: four buckets over customer_id'
CREATE TABLE lesson01.partition_hash_demo (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    sale_date date NOT NULL,
    amount numeric(12, 2) NOT NULL
)
DISTRIBUTED BY (customer_id)
PARTITION BY HASH (customer_id);

CREATE TABLE lesson01.partition_hash_demo_p0
    PARTITION OF lesson01.partition_hash_demo
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE lesson01.partition_hash_demo_p1
    PARTITION OF lesson01.partition_hash_demo
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE lesson01.partition_hash_demo_p2
    PARTITION OF lesson01.partition_hash_demo
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE lesson01.partition_hash_demo_p3
    PARTITION OF lesson01.partition_hash_demo
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

INSERT INTO lesson01.partition_hash_demo
SELECT sale_id, customer_id, sale_date, amount
FROM lesson01.fact_sales_good
LIMIT 5000;

\echo '04. Multi-level strategy: RANGE by date, then LIST by region'
CREATE TABLE lesson01.partition_multilevel_demo (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    sale_date date NOT NULL,
    region text NOT NULL,
    amount numeric(12, 2) NOT NULL
)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date);

CREATE TABLE lesson01.partition_multilevel_demo_2026_01
    PARTITION OF lesson01.partition_multilevel_demo
    FOR VALUES FROM (DATE '2026-01-01') TO (DATE '2026-02-01')
    PARTITION BY LIST (region);

CREATE TABLE lesson01.partition_multilevel_demo_2026_01_capitals
    PARTITION OF lesson01.partition_multilevel_demo_2026_01
    FOR VALUES IN ('Moscow', 'Saint Petersburg');

CREATE TABLE lesson01.partition_multilevel_demo_2026_01_regions
    PARTITION OF lesson01.partition_multilevel_demo_2026_01
    FOR VALUES IN ('Kazan', 'Novosibirsk', 'Yekaterinburg');

CREATE TABLE lesson01.partition_multilevel_demo_2026_01_default
    PARTITION OF lesson01.partition_multilevel_demo_2026_01
    DEFAULT;

INSERT INTO lesson01.partition_multilevel_demo
SELECT sale_id, customer_id, sale_date, region, amount
FROM lesson01.partition_range_demo
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01'
LIMIT 3000;

ANALYZE lesson01.partition_range_demo;
ANALYZE lesson01.partition_list_demo;
ANALYZE lesson01.partition_hash_demo;
ANALYZE lesson01.partition_multilevel_demo;

\echo '05. How many partitions does each demo table have? Count leaf_partitions'
WITH roots AS (
    SELECT
        n.nspname AS schema_name,
        c.relname AS table_name,
        c.oid AS root_oid
    FROM pg_class AS c
    JOIN pg_namespace AS n ON n.oid = c.relnamespace
    WHERE n.nspname = 'lesson01'
      AND c.relname IN (
          'partition_range_demo',
          'partition_list_demo',
          'partition_hash_demo',
          'partition_multilevel_demo'
      )
)
SELECT
    roots.schema_name,
    roots.table_name,
    COUNT(*) FILTER (WHERE tree.isleaf) AS leaf_partitions,
    COUNT(*) FILTER (WHERE NOT tree.isleaf) AS internal_partition_nodes,
    MAX(tree.level) AS max_partition_level
FROM roots
CROSS JOIN LATERAL pg_partition_tree(roots.root_oid) AS tree
GROUP BY roots.schema_name, roots.table_name
ORDER BY roots.table_name;

\echo '06. Partition tree for RANGE demo'
SELECT
    tree.level,
    tree.isleaf,
    tree.relid::regclass AS relation_name,
    tree.parentrelid::regclass AS parent_relation
FROM pg_partition_tree('lesson01.partition_range_demo'::regclass) AS tree
ORDER BY tree.level, tree.relid::regclass::text;

\echo '07. Partition tree for multi-level demo'
SELECT
    tree.level,
    tree.isleaf,
    tree.relid::regclass AS relation_name,
    tree.parentrelid::regclass AS parent_relation
FROM pg_partition_tree('lesson01.partition_multilevel_demo'::regclass) AS tree
ORDER BY tree.level, tree.relid::regclass::text;

\echo '08. Inspect partition key definitions'
SELECT
    c.oid::regclass AS partitioned_table,
    pg_get_partkeydef(c.oid) AS partition_key
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'lesson01'
  AND c.relname IN (
      'partition_range_demo',
      'partition_list_demo',
      'partition_hash_demo',
      'partition_multilevel_demo',
      'partition_multilevel_demo_2026_01'
  )
ORDER BY c.oid::regclass::text;

\echo '09. Inspect leaf partitions through gp_toolkit.gp_partitions if available'
SELECT CASE
    WHEN to_regclass('gp_toolkit.gp_partitions') IS NULL THEN
        $$SELECT 'gp_toolkit.gp_partitions is not available in this cluster version' AS note;$$
    ELSE
        $$SELECT *
          FROM gp_toolkit.gp_partitions
          WHERE schemaname = 'lesson01'
            AND tablename IN (
                'partition_range_demo',
                'partition_list_demo',
                'partition_hash_demo',
                'partition_multilevel_demo'
            )
          ORDER BY schemaname, tablename, partitionlevel, partitiontablename;$$
END AS sql_to_run
\gexec

\echo '10. Show which physical partition received DEFAULT/out-of-range rows'
SELECT
    tableoid::regclass AS physical_partition,
    sale_id,
    sale_date,
    region
FROM lesson01.partition_range_demo
WHERE sale_id = 900001
UNION ALL
SELECT
    tableoid::regclass AS physical_partition,
    sale_id,
    sale_date,
    region
FROM lesson01.partition_list_demo
WHERE sale_id = 900002
ORDER BY sale_id;

\echo '11. Pruning demo: RANGE predicate should target only matching date partitions'
EXPLAIN
SELECT sum(amount)
FROM lesson01.partition_range_demo
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';

\echo '12. LIST pruning demo: region predicate should target matching list partition'
EXPLAIN
SELECT sum(amount)
FROM lesson01.partition_list_demo
WHERE region = 'Moscow';

\echo '13. HASH demo: good for bucketization, not for date retention'
SELECT
    tableoid::regclass AS physical_partition,
    COUNT(*) AS rows_count
FROM lesson01.partition_hash_demo
GROUP BY tableoid::regclass
ORDER BY tableoid::regclass::text;

\echo '14. Maintenance snippets: read during class; run only in controlled practice'
-- ATTACH PARTITION pattern:
-- CREATE TABLE lesson01.partition_range_demo_2026_04
--     (LIKE lesson01.partition_range_demo INCLUDING DEFAULTS INCLUDING CONSTRAINTS)
--     DISTRIBUTED BY (customer_id);
-- ALTER TABLE lesson01.partition_range_demo
--     ATTACH PARTITION lesson01.partition_range_demo_2026_04
--     FOR VALUES FROM (DATE '2026-04-01') TO (DATE '2026-05-01');
--
-- DETACH PARTITION pattern:
-- ALTER TABLE lesson01.partition_range_demo
--     DETACH PARTITION lesson01.partition_range_demo_2026_01;
--
-- DROP old retention partition pattern:
-- DROP TABLE lesson01.partition_range_demo_2026_01;
--
-- Out-of-range INSERT behavior:
-- If there is no DEFAULT partition and no matching partition range/list value,
-- Greenplum rejects the row instead of guessing a target partition.
