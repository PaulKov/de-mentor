# Workbook Ученика: Lesson 03

Тема: декомпозиция тяжёлых OLAP, Legacy vs GPORCA, статистика и TEMP на Greenplum 6.25.

База: **`mentor`**. Схема: **`lesson03`**. Стенд: **`greenplum-625`**.

## Перед Стартом

Проверь окружение:

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py readiness greenplum-625 --platform macos
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
```

Windows:

```powershell
py mentor-lab.py doctor --full
py mentor-lab.py readiness greenplum-625 --platform windows
py mentor-lab.py up greenplum-625
py mentor-lab.py seed greenplum-625 --profile lesson03
py mentor-lab.py check greenplum-625
```

Linux:

```bash
python3 mentor-lab.py readiness greenplum-625 --platform linux
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
```

Ключевые ссылки:

- [Домашка Principal 90м](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/03-greenplum-query-tuning/homework.md)
- [План домашки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/03-greenplum-query-tuning/runbooks/homework-plan.md)
- [SQL-lab](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql)
- [Optimizer lab](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql)
- [Шпаргалка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/03-greenplum-query-tuning/cheat-sheet.md)

## Упражнение 1: Ты В БД mentor

```bash
python3 mentor-lab.py psql greenplum-625
```

```sql
\conninfo
SELECT current_database(), current_user;
\dn lesson03
SELECT count(*) FROM lesson03.fact_sales;
```

Ответь:

- какая БД активна (должно быть `mentor`, не `postgres`);
- зачем образ всё ещё имеет maintenance DB `postgres`;
- где живут объекты урока (`mentor.lesson03.*`).

Self-check:

- в ответе явно `mentor` + `lesson03`;
- нет работы «по привычке» в `postgres`.

## Упражнение 2: Optimizer GUC И Маркеры Плана

```sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql

SHOW optimizer;
SET optimizer = on;
EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;
SET optimizer = off;
EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;
```

Ответь:

- какие стадии проходит запрос до execute;
- где ORCA выиграл/проиграл относительно Legacy;
- почему `SET optimizer` — session-scoped и опасен в shared session.

Self-check:

- есть маркеры Pivotal Optimizer / Postgres query optimizer;
- есть вывод про join order или Motion, не только «быстрее/медленнее».

## Упражнение 3: Layered EXPLAIN Монолита

```sql
SET optimizer = on;
EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;
```

Ответь слоями:

1. optimizer marker;
2. все Motion и смысл Redistribute/Broadcast/Gather;
3. join shape;
4. estimates alarm (где rows выглядят неправдоподобно).

Self-check:

- в ответе есть все четыре слоя;
- есть ссылка на конкретный узел плана.

## Упражнение 4: Статистика До Selectivity

```sql
SHOW default_statistics_target;

SELECT attname, n_distinct, most_common_vals, most_common_freqs,
       array_length(histogram_bounds, 1) AS hist_n
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename IN ('fact_sales', 'dim_customer')
ORDER BY tablename, attname;

EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.dim_customer
WHERE segment = 'enterprise';
```

Ответь:

- чем MCV отличается от equi-depth histogram;
- какой predicate ты связал со stats slot;
- когда stats не спасают и нужен TEMP stage.

Self-check:

- есть `pg_stats` snippet;
- есть rows estimate vs actual (из ANALYZE).

## Упражнение 5: TEMP Rewrite При Фиксированном Optimizer

Сравни план монолита с планом через `tmp_lesson03_sales_shaped` (из SQL-lab) при **том же** `SET optimizer`.

Дополнительно:

```sql
CREATE TEMP TABLE tmp_wb_fs AS
SELECT customer_id, product_id, amount
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01'
DISTRIBUTED BY (customer_id);

SELECT n.nspname, c.relname, pg_relation_filepath(c.oid)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relname = 'tmp_wb_fs';
```

Ответь:

- почему выбран distribution ключ промежуточного TEMP;
- где на диске TEMP (`t_*`) vs spill Sort;
- что обязательно сделать после наполнения TEMP (`ANALYZE`).

Self-check:

- before/after при одном optimizer;
- filepath TEMP зафиксирован;
- есть residual risk одной фразой.

## Evidence Checklist К Домашке

- [ ] работа в БД `mentor`
- [ ] before/after при фиксированном optimizer
- [ ] ORCA vs Legacy matrix
- [ ] `pg_stats` / `pg_statistic`
- [ ] ≥2 TEMP стадии + `DISTRIBUTED BY` + `ANALYZE`
- [ ] reconciliation или честный residual risk
- [ ] вопрос к Уроку 04
