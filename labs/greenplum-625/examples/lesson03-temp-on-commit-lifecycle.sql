-- Demo: TEMP lifecycle — сессия vs транзакция, ON COMMIT режимы, каталог.
-- Database: mentor. Schema lesson03 не обязателен для самих TEMP.
--
-- Запускайте целиком в ОДНОЙ сессии psql, затем откройте второй psql и
-- убедитесь, что чужие TEMP не видны.

\echo '=== 0. Что такое сессия (этот backend) ==='
SELECT
    pg_backend_pid() AS backend_pid,
    current_database() AS db,
    current_user AS usr,
    pg_my_temp_schema()::regnamespace AS my_temp_schema_before;

SELECT pid, usename, application_name, state, left(query, 40) AS q
FROM pg_stat_activity
WHERE pid = pg_backend_pid();

\echo '=== 1. ON COMMIT PRESERVE ROWS (default): живёт после COMMIT ==='
DROP TABLE IF EXISTS tmp_preserve;
BEGIN;
CREATE TEMP TABLE tmp_preserve AS
SELECT customer_id, amount
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date <  DATE '2026-03-01'
DISTRIBUTED BY (customer_id)
ON COMMIT PRESERVE ROWS;
ANALYZE tmp_preserve;
SELECT count(*) AS rows_in_txn FROM tmp_preserve;
COMMIT;

SELECT count(*) AS rows_after_commit FROM tmp_preserve;  -- должно быть > 0
SELECT to_regclass('tmp_preserve') AS still_exists;

\echo '=== 2. ON COMMIT DELETE ROWS: таблица есть, строки после COMMIT = 0 ==='
DROP TABLE IF EXISTS tmp_delete_rows;
BEGIN;
CREATE TEMP TABLE tmp_delete_rows (
    customer_id int,
    amount numeric
) DISTRIBUTED BY (customer_id)
ON COMMIT DELETE ROWS;
INSERT INTO tmp_delete_rows
SELECT customer_id, amount FROM lesson03.fact_sales LIMIT 100;
SELECT count(*) AS rows_in_txn FROM tmp_delete_rows;
COMMIT;

SELECT count(*) AS rows_after_commit FROM tmp_delete_rows;  -- 0
SELECT to_regclass('tmp_delete_rows') AS table_still_exists; -- oid

\echo '=== 3. ON COMMIT DROP: после COMMIT таблицы нет ==='
BEGIN;
CREATE TEMP TABLE tmp_drop AS
SELECT 1 AS x
DISTRIBUTED BY (x)
ON COMMIT DROP;
SELECT * FROM tmp_drop;
COMMIT;

-- Ожидаем ошибку relation does not exist — это успех демо:
SELECT to_regclass('tmp_drop') AS should_be_null;

\echo '=== 4. Каталог: где смотреть TEMP в Greenplum ==='
SELECT pg_my_temp_schema()::regnamespace AS my_temp_schema;

SELECT
    n.nspname,
    c.relname,
    c.relpersistence,
    c.relkind,
    pg_relation_filepath(c.oid) AS filepath,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.oid = pg_my_temp_schema()
ORDER BY c.relname;

\echo '=== 5. Явный DROP vs конец сессии ==='
DROP TABLE IF EXISTS tmp_delete_rows;
SELECT to_regclass('tmp_delete_rows') AS after_explicit_drop;

\echo '=== Подсказка ==='
\echo 'Откройте ВТОРОЙ psql к mentor и выполните:'
\echo '  SELECT to_regclass(''tmp_preserve'');  -- NULL в чужой сессии'
\echo '  SELECT nspname FROM pg_namespace WHERE nspname LIKE ''pg_temp%'';'
\echo 'Закройте ЭТОТ psql (\\q) — tmp_preserve исчезнет вместе с сессией.'

\echo '=== Done ==='
