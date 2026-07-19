# Workbook Ученика: Урок 03 (Greenplum 6.25)

## Подготовка

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py psql greenplum-625
```

## Блок A — Стадии и Optimizer

```sql
SHOW optimizer;
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
```

Ответь:

1. Какие стадии проходит запрос до execute?
2. Где ORCA выиграл/проиграл относительно Legacy на `v_star_join_orca_case`?
3. Какие плюсы/минусы каждого оптимизатора зафиксируешь для production policy?

## Блок B — Layered EXPLAIN

```sql
SET optimizer = on;
EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;
```

Запиши: optimizer marker, Motion, join shape, estimates, scan/pruning.

## Блок C — Статистика

```sql
SELECT attname, null_frac, n_distinct, most_common_vals, histogram_bounds
FROM pg_stats
WHERE schemaname = 'lesson03' AND tablename = 'fact_sales'
ORDER BY attname;
```

## Блок D — TEMP Rewrite

Сравни план монолита с планом через `tmp_lesson03_sales_shaped` при **том же** `SET optimizer`.

## Evidence Checklist

- [ ] before/after при фиксированном optimizer
- [ ] ORCA vs Legacy snippet
- [ ] pg_stats / pg_statistic
- [ ] storage rationale (appendonly AOCO vs Heap)
- [ ] residual risk
