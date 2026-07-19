-- Demo: ручной vs автоматический ANALYZE, где смотреть last_analyze.
-- Database: mentor. Schema: lesson03.

\echo '=== 0. Какие автоматы включены на стенде ==='
SHOW gp_autostats_mode;
SHOW gp_autostats_on_change_threshold;
SHOW gp_autostats_mode_in_functions;
SHOW gp_autostats_allow_nonowner;
SHOW default_statistics_target;

\echo '=== 1. Когда статистика обновлялась последний раз ==='
SELECT
    schemaname,
    relname,
    last_analyze,
    last_autoanalyze,
    analyze_count,
    autoanalyze_count,
    n_mod_since_analyze,
    n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'lesson03'
ORDER BY relname;

\echo '=== 2. Ручной ANALYZE + проверка timestamp ==='
ANALYZE lesson03.dim_customer;

SELECT
    relname,
    last_analyze,
    last_autoanalyze,
    analyze_count,
    n_mod_since_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson03'
  AND relname = 'dim_customer';

\echo '=== 3. Слоты pg_stats после ANALYZE ==='
SELECT
    attname,
    n_distinct,
    array_length(histogram_bounds, 1) AS hist_n,
    most_common_vals IS NOT NULL AS has_mcv
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename = 'dim_customer'
ORDER BY attname;

\echo '=== 4. Таблицы без статистики (если есть gp_toolkit) ==='
SELECT *
FROM gp_toolkit.gp_stats_missing
WHERE smischema = 'lesson03'
LIMIT 20;

\echo '=== 5. Автоматика gp_autostats (on_no_stats) — идея демо ==='
\echo 'Default on_no_stats: ANALYZE вшивается в CTAS/INSERT/COPY только если stats ещё нет.'
\echo 'На уже проанализированной fact после bulk load автомат часто НЕ срабатывает.'
\echo 'Поэтому ETL контракт: явный ANALYZE, а не надежда на gp_autostats_mode.'

-- Безопасный мини-пример: новая TEMP без stats → после CTAS часто появляется auto path
DROP TABLE IF EXISTS tmp_autostats_demo;
CREATE TEMP TABLE tmp_autostats_demo AS
SELECT customer_id, amount
FROM lesson03.fact_sales
LIMIT 1000
DISTRIBUTED BY (customer_id);

-- Даже если autostats сработал — для следующего plan всё равно проверяйте:
ANALYZE tmp_autostats_demo;

SELECT
    n.nspname,
    c.relname,
    c.reltuples
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relname = 'tmp_autostats_demo';

\echo '=== 6. SET STATISTICS меняет target; нужен повторный ANALYZE ==='
SELECT
    attname,
    array_length(histogram_bounds, 1) AS hist_n_before
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename = 'fact_sales'
  AND attname = 'amount';

ALTER TABLE lesson03.fact_sales ALTER COLUMN amount SET STATISTICS 200;
ANALYZE lesson03.fact_sales;

SELECT
    attname,
    array_length(histogram_bounds, 1) AS hist_n_after,
    (SELECT last_analyze
     FROM pg_stat_user_tables
     WHERE schemaname = 'lesson03' AND relname = 'fact_sales') AS last_analyze
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename = 'fact_sales'
  AND attname = 'amount';

-- Вернуть учебный target
ALTER TABLE lesson03.fact_sales ALTER COLUMN amount SET STATISTICS 100;
ANALYZE lesson03.fact_sales;

\echo '=== Done ==='
