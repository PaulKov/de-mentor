# План домашки Lesson 03

База: **`mentor`**. Схема: **`lesson03`**. Стенд: **`greenplum-625`**.

Таймер **Senior core** стартует после зелёного `check`, не с установки Docker.  
Ориентир: **90–120 минут** на Tasks 1–4. Principal extension — отдельно.

Канон: [assignment.md](assignment.md) · [rubric.md](rubric.md) · [templates/](templates/).

## Prep (вне таймера): стенд

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py psql greenplum-625
```

```sql
\conninfo
\i /mentor-lab/examples/lesson03-homework-seed.sql
```

Не запускай `lesson03-class-demo.sql` как «решение homework».

## Senior core

### Task 1 — Baseline (~20–25 мин)

```sql
SET optimizer = on;  -- или off; дальше не менять для rewrite proof
EXPLAIN ANALYZE
SELECT * FROM lesson03.v_heavy_olap_monolith;

SELECT attname, null_frac, n_distinct, most_common_vals,
       array_length(histogram_bounds, 1) AS hist_n
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename IN ('fact_sales', 'dim_customer')
ORDER BY tablename, attname;
```

Deliverable: секции A–C evidence (contract, before, stats causality).

### Task 2 — Physical design (~30–40 мин)

Спроектируй 0–3 стадии. Пример формы (ключи — твои):

```sql
-- optional stages; DROP for idempotency
DROP TABLE IF EXISTS tmp_l03_b;
DROP TABLE IF EXISTS tmp_l03_a;

-- CREATE TEMP TABLE tmp_l03_a AS ... DISTRIBUTED BY (...);
-- ANALYZE tmp_l03_a;
-- CREATE TEMP TABLE tmp_l03_b AS ... DISTRIBUTED BY (...);
-- ANALYZE tmp_l03_b;
```

Заполни stage table (секция D). Storage выбирай сам — scaffold AOCO **не** требуется.

### Task 3 — End-to-end metrics (~20 мин)

Измерь monolith total vs candidate total (включая CTAS + ANALYZE + final).  
Заполни таблицу E. Прими decision: merge / do not merge / needs larger-scale validation.

### Task 4 — Correctness (~15–20 мин)

Скопируй и адаптируй [templates/reconcile.sql](templates/reconcile.sql):

- `EXCEPT ALL` в обе стороны → 0/0;
- counts;
- residual risks (секция I) **и** adversarial (два способа).

## Финальная самопроверка

```bash
python3 mentor-lab.py homework greenplum-625 check \
  --submission lessons/lesson-03/submissions
python3 mentor-lab.py student greenplum-query-tuning homework
```

## Principal extension (после core)

- ORCA/Legacy: явный контракт frozen-input **или** e2e;
- TEMP filepath / constrained spill;
- Optimizer Policy RFC;
- вопрос к WLM (секция J).

Не оценивай extension как обязательный 90-минутный чек-лист.
