-- Greenplum 6.25 lesson 01: partitioning strategies deep drill.
-- Database: mentor. Stand: greenplum-625.
--
-- Classic GP6 PARTITION BY RANGE/LIST (+ SUBPARTITION), not PG11 PARTITION OF.
-- Inspection: pg_partitions.
--
-- Safe run pattern:
--   BEGIN;
--   \i /mentor-lab/examples/partitioning-strategies.sql
--   ROLLBACK;
--
-- Mentor anchor: partition key не равен distribution key.
-- out-of-range INSERT without DEFAULT partition is rejected by Greenplum.

CREATE SCHEMA IF NOT EXISTS lesson01;

DROP TABLE IF EXISTS lesson01.partition_multilevel_demo CASCADE;
DROP TABLE IF EXISTS lesson01.partition_list_demo CASCADE;
DROP TABLE IF EXISTS lesson01.partition_range_demo CASCADE;

\echo '01. RANGE strategy: monthly sale_date partitions plus DEFAULT'
CREATE TABLE lesson01.partition_range_demo (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    sale_date date NOT NULL,
    region text NOT NULL,
    amount numeric(12, 2) NOT NULL
)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date)
(
    START (DATE '2026-01-01') INCLUSIVE END (DATE '2026-02-01') EXCLUSIVE,
    START (DATE '2026-02-01') INCLUSIVE END (DATE '2026-03-01') EXCLUSIVE,
    START (DATE '2026-03-01') INCLUSIVE END (DATE '2026-04-01') EXCLUSIVE,
    DEFAULT PARTITION extra
);

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

INSERT INTO lesson01.partition_range_demo (
    sale_id, customer_id, sale_date, region, amount
)
VALUES (900001, 42, DATE '2030-01-01', 'unknown', 10.00);

\echo '02. LIST strategy: region partitions plus DEFAULT'
CREATE TABLE lesson01.partition_list_demo (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    sale_date date NOT NULL,
    region text NOT NULL,
    amount numeric(12, 2) NOT NULL
)
DISTRIBUTED BY (customer_id)
PARTITION BY LIST (region)
(
    PARTITION capitals VALUES ('Moscow', 'Saint Petersburg'),
    PARTITION regions VALUES ('Kazan', 'Novosibirsk', 'Yekaterinburg'),
    DEFAULT PARTITION other
);

INSERT INTO lesson01.partition_list_demo
SELECT sale_id, customer_id, sale_date, region, amount
FROM lesson01.partition_range_demo
WHERE sale_id <> 900001
LIMIT 5000;

INSERT INTO lesson01.partition_list_demo
VALUES (900002, 77, DATE '2026-02-01', 'Other', 25.00);

\echo '03. Multi-level: RANGE(sale_date) + LIST(region) subpartitions'
CREATE TABLE lesson01.partition_multilevel_demo (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    sale_date date NOT NULL,
    region text NOT NULL,
    amount numeric(12, 2) NOT NULL
)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date)
SUBPARTITION BY LIST (region)
SUBPARTITION TEMPLATE (
    SUBPARTITION capitals VALUES ('Moscow', 'Saint Petersburg'),
    SUBPARTITION regions VALUES ('Kazan', 'Novosibirsk', 'Yekaterinburg'),
    DEFAULT SUBPARTITION other
)
(
    START (DATE '2026-01-01') INCLUSIVE END (DATE '2026-02-01') EXCLUSIVE,
    START (DATE '2026-02-01') INCLUSIVE END (DATE '2026-03-01') EXCLUSIVE,
    DEFAULT PARTITION extra
);

INSERT INTO lesson01.partition_multilevel_demo
SELECT sale_id, customer_id, sale_date, region, amount
FROM lesson01.partition_range_demo
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01'
LIMIT 3000;

ANALYZE lesson01.partition_range_demo;
ANALYZE lesson01.partition_list_demo;
ANALYZE lesson01.partition_multilevel_demo;

\echo '04. Inspect partitions via pg_partitions'
SELECT
    tablename,
    partitiontablename,
    partitionlevel,
    partitionrank,
    partitionboundary
FROM pg_partitions  -- GP6 classic; gp_toolkit.gp_partitions absent on some slim images
WHERE schemaname = 'lesson01'
  AND tablename IN (
      'partition_range_demo',
      'partition_list_demo',
      'partition_multilevel_demo'
  )
ORDER BY tablename, partitionlevel, partitionrank, partitiontablename;

\echo '05. Show which physical partition received DEFAULT/out-of-range rows'
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

\echo '06. Pruning demo: RANGE predicate'
EXPLAIN
SELECT sum(amount)
FROM lesson01.partition_range_demo
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';

\echo '07. LIST pruning demo'
EXPLAIN
SELECT sum(amount)
FROM lesson01.partition_list_demo
WHERE region = 'Moscow';

\echo '08. Maintenance snippets (GP6)'
-- ALTER TABLE lesson01.partition_range_demo
--   ADD PARTITION START (DATE '2026-04-01') INCLUSIVE
--   END (DATE '2026-05-01') EXCLUSIVE;
-- ALTER TABLE lesson01.partition_range_demo
--   DROP PARTITION FOR (DATE '2026-01-01');
