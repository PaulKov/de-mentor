# План домашки Lesson 03

База: **`mentor`**. Схема: **`lesson03`**. Стенд: **`greenplum-625`**.

Graded view: **`lesson03.v_homework_brand_region`**.  
Class demo `v_heavy_olap_monolith` — не baseline homework.

Таймер **Senior core** стартует после зелёного `check`, не с установки Docker.  
Ориентир: **90–120 минут** на Tasks 1–4. Principal extension — отдельно.

Канон: [assignment.md](assignment.md) · [rubric.md](rubric.md) · [templates/](templates/).

## Prep (вне таймера): стенд

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03 --scale small
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py psql greenplum-625
```

```sql
\conninfo
\i /mentor-lab/examples/lesson03-homework-seed.sql
-- optional: SELECT * FROM lesson03.seed_meta;
```

Не запускай `lesson03-class-demo.sql` как «решение homework».

## Senior core

### Task 1 — Baseline (~20–25 мин)

```sql
SET optimizer = on;  -- или off; дальше не менять для rewrite proof
EXPLAIN ANALYZE
SELECT * FROM lesson03.v_homework_brand_region;

SELECT attname, null_frac, n_distinct, most_common_vals,
       array_length(histogram_bounds, 1) AS hist_n
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename IN ('fact_sales', 'dim_customer', 'dim_product')
ORDER BY tablename, attname;

-- Skew smell (hot customers in seed)
SELECT customer_id, count(*) AS cnt
FROM lesson03.fact_sales
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;
```

Deliverable: секции A–C evidence (contract на brand×region, before, stats causality).

### Task 2 — A/B physical design (~30–40 мин)

Исследуй **Candidate A** (≤1 stage / no-TEMP) и **Candidate B** (multi-stage).  
В `rewrite.sql` оставь production winner; оба — в секции D.

```sql
-- optional stages; DROP for idempotency
DROP TABLE IF EXISTS tmp_l03_b;
DROP TABLE IF EXISTS tmp_l03_a;

-- CREATE TEMP TABLE tmp_l03_a AS ... DISTRIBUTED BY (...);
-- ANALYZE tmp_l03_a;
-- CREATE TEMP TABLE tmp_l03_b AS ... DISTRIBUTED BY (...);
-- ANALYZE tmp_l03_b;
```

Заполни stage table для winner. Storage выбирай сам — scaffold AOCO **не** требуется.

### Task 3 — End-to-end metrics (~20 мин)

Измерь monolith (`v_homework_brand_region`) vs A vs B (включая CTAS + ANALYZE + final).  
Заполни таблицу E. Прими decision: merge / do not merge / needs larger-scale validation.

### Task 4 — Correctness (~15–20 мин)

Скопируй и адаптируй [templates/reconcile.sql](templates/reconcile.sql):

- baseline = `v_homework_brand_region`;
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

- `--scale principal` и повтор e2e decision;
- ORCA/Legacy: явный контракт frozen-input **или** e2e;
- TEMP filepath / constrained spill;
- Optimizer Policy RFC;
- вопрос к WLM (секция J).

Не оценивай extension как обязательный 90-минутный чек-лист.
