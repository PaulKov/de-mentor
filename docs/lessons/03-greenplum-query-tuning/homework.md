# Домашка Principal: Урок 03 — Optimization Deep Dive

Стенд: `greenplum-625` (Greenplum 6.25).  
База: **`mentor`** (как в Уроках 01–02). Схема: **`lesson03`**.

Время: **90 минут** (жёсткий тайминг в [homework-plan.md](runbooks/homework-plan.md)).

Уровень: **Principal** — не «переписать SQL красивее», а доказать физическую стратегию тюнинга evidence-паком уровня production RFC.

## Цель

Построить и защитить **многостадийный rewrite** тяжёлого OLAP из `lesson03.v_heavy_olap_monolith` так, чтобы:

1. декомпозиция шла через **≥2 TEMP-стадии** (не один «свал» TEMP);
2. у каждой стадии был осмысленный `DISTRIBUTED BY` под следующий join/agg;
3. после каждого наполнения TEMP выполнялся `ANALYZE`;
4. before/after снимались при **фиксированном** `SET optimizer` (один выбранный движок для rewrite-доказательства);
5. отдельно — **матрица ORCA vs Legacy** на `v_star_join_orca_case` и на твоём final query (planning + shape + Motion);
6. был **stats-driven** аргумент: какие слоты `pg_stats` / `pg_statistic` объясняют estimate fail монолита;
7. был **spill/TEMP FS** аргумент (хотя бы один constrained `statement_mem` / filepath TEMP);
8. бизнес-результат (grain, фильтры, агрегаты) **бит-в-бит** совпал с монолитом на контрольном окне.

## Подготовка

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py runbook greenplum-query-tuning homework
python3 mentor-lab.py psql greenplum-625
```

В psql убедись, что ты в `mentor`:

```sql
\conninfo
\i /mentor-lab/examples/lesson03-olap-decomposition-tuning.sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
```

## Запрещено (авто-reject)

- CTE-only rewrite **без** доказательства materialize/TEMP (CTE как «магический кеш» не принимается).
- `DISTRIBUTED RANDOMLY` на join-стадии без обоснования «следующий шаг не co-locate».
- Смена `optimizer` между before и after при сравнении rewrite.
- «AOCO быстрее» / «ORCA всегда лучше» без access pattern / plan evidence.
- Изменение бизнес-grain (другие GROUP BY / фильтры / окна) без явного residual risk и reconciliation.
- Работа в БД `postgres` вместо `mentor`.

## Обязательные Deliverables

Создай каталог `submissions/lesson03-query-tuning/` (или один markdown + SQL):

### 1. `rewrite.sql`

Многостадийный pipeline:

- stage A TEMP (filter/shape fact window);
- stage B TEMP (join dims / partial agg);
- final SELECT (window/rank или аналог монолита);
- все `DISTRIBUTED BY` + `ANALYZE` после INSERT/CTAS;
- в шапке файла: `SET optimizer = on|off;` и комментарий почему.

### 2. `evidence.md` (Principal pack)

Структура обязательна:

| Секция | Что должно быть |
| --- | --- |
| A. Workload contract | grain, predicates, SLA freshness, что считается «тем же ответом» |
| B. Before plan | полный layered readout: optimizer marker, Motions, join shape, estimates alarm |
| C. Stats autopsy | `pg_stats` + хотя бы один `pg_statistic` slot; selectivity гипотеза → почему план плохой |
| D. Stage design | таблица стадий: цель / distribution key / почему / что убираем из Motion |
| E. After plan | тот же optimizer; сравнение Motion/rows/join shape с before |
| F. ORCA vs Legacy matrix | 2×2: case view + final query; где кто выигрывает и **почему** |
| G. Spill / TEMP FS | filepath TEMP (`t_*`) и/или spill при constrained `statement_mem` |
| H. Reconciliation | SQL, доказывающий равенство агрегатов vs monolith на окне |
| I. Residual risk | когда rewrite врёт (late facts, NDV drift, ORCA fallback, skew) |
| J. Question → Lesson 04 | один sharp вопрос про WLM / resource groups / production kill-switch |

### 3. Контрольные запросы (в evidence)

Минимум:

```sql
-- Fixed optimizer for rewrite proof
SET optimizer = /* on|off */;

EXPLAIN
SELECT * FROM lesson03.v_heavy_olap_monolith;

-- your stages + EXPLAIN final

-- Reconciliation (пример формы; адаптируй под свой grain)
-- SELECT ... FROM monolith_window
-- EXCEPT
-- SELECT ... FROM rewrite_window;

-- Stats
SELECT attname, null_frac, n_distinct, most_common_vals,
       array_length(histogram_bounds, 1) AS hist_n
FROM pg_stats
WHERE schemaname = 'lesson03' AND tablename = 'fact_sales'
ORDER BY attname;

-- ORCA vs Legacy on star-join case
SET optimizer = on;
EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;
SET optimizer = off;
EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;
```

## Principal Challenges (обязательно закрыть все)

### Challenge 1 — Estimate Failure Narrative

Покажи **конкретный** predicate/join, где rows estimate расходится с reality (`EXPLAIN ANALYZE`), и свяжи это с MCV / histogram / `n_distinct`. Без «статистика устарела» общими словами.

### Challenge 2 — Co-location Proof

Для одной TEMP-стадии докажи, что выбранный `DISTRIBUTED BY` уменьшает Redistribute на следующем join (before/after куски плана, не весь dump без комментария).

### Challenge 3 — Optimizer Policy RFC

Напиши 8–12 строк production policy:

- когда default `optimizer=on`;
- когда session `SET optimizer=off` допустим;
- какой evidence нужен перед merge rewrite в ETL/BI;
- что мониторить после выкладки (plan flip, spill, skew).

### Challenge 4 — Adversarial Self-Review

Сам найди **два** способа, как твой rewrite может дать другой бизнес-результат при том же SQL «на глаз», и закрой их reconciliation или residual risk.

## Самопроверка

```bash
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py student greenplum-query-tuning homework
python3 mentor-lab.py runbook greenplum-query-tuning homework
```

## Критерий Приёмки

См. [rubric.md](rubric.md). Без before/after при фиксированном optimizer, без reconciliation и без ORCA/Legacy matrix домашка **не принимается**.
