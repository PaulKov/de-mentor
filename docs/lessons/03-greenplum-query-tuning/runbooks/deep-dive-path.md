# Deep-Dive Path: Урок 03 (90–120 минут)

База: **`mentor`**. Схема: **`lesson03`**.

## Блоки

1. Simple-path целиком на `greenplum-625` / `mentor`.
2. ORCA memo/xforms/fallback + minidump discussion.
3. `pg-statistic-internals.md`.
4. `storage-physical-layout.md` (GP6 `appendonly`).
5. `temp-tables-and-spill.md` (TEMP `t_*` vs `pgsql_tmp_Sort_*`).
6. Design review: rewrite + optimizer policy как production RFC (мост к Principal homework).

## Команды

```bash
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py runbook greenplum-query-tuning deep
python3 mentor-lab.py psql greenplum-625
```

```sql
\conninfo
SET statement_mem = '8MB';
SET optimizer = off;
EXPLAIN ANALYZE
SELECT customer_id, amount FROM lesson03.fact_sales ORDER BY amount;
```
