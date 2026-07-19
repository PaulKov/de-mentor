# Deep-dive: Secrets #41 — `gp_autostats_mode` не срабатывает на INSERT в parent

> Стенд: [`lesson03-secret41-autostats-partitions.sql`](../../../../labs/greenplum-625/examples/lesson03-secret41-autostats-partitions.sql)  
> Метрики: [`lessons/lesson-03/artifacts/case/secret41-autostats-partitions-metrics.md`](../../artifacts/case/secret41-autostats-partitions-metrics.md)

---

## 1. Что — на пальцах

Вы уверены в ETL:

```sql
SET gp_autostats_mode = on_no_stats;
INSERT INTO sales_partitioned SELECT …;  -- в PARENT
-- «стата должна появиться сама»
```

На Greenplum 6 для **партицированных** таблиц это часто **ложь**.  
Autostats **не** триггерится при вставке через top-level parent.  
Триггерится при вставке **напрямую в leaf** (где физически лежат строки).

Отсюда ложные выводы в бенчмарках «со статой / без статы» (история Secrets #41).

---

## 2. Как проверить

После `INSERT` в parent смотрите на **leaf**-relations:

- `pg_stat_all_tables.last_analyze` / `last_autoanalyze`
- наличие строк в `pg_statistic` для attnum колонок leaf
- `gp_toolkit.gp_stats_missing` (если доступен в сборке)

Ожидание лаборатории:

| Шаг | Leaf stats |
| --- | --- |
| A INSERT → parent | часто MISSING / без fresh analyze |
| B INSERT → leaf | autostats обновляет этот leaf |
| C `ANALYZE` parent | политика ETL: явный сбор |

Имена leaf на GP6 RANGE: обычно `relname_1_prt_*` — смотрите `pg_class` в скрипте.

---

## 3. Почему — документация, не баг

Цитата поведения (Greenplum 6 / Secrets):

> For partitioned tables, automatic statistics collection is **not** triggered if data is inserted from the **top-level parent** table of a partitioned table.  
> But automatic statistics collection **is** triggered if data is inserted directly in a **leaf** table…

Код якоря (точка входа ANALYZE / autostats):

- [`analyze.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/commands/analyze.c)
- GUC объявления: [`guc.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/utils/misc/guc.c) (`gp_autostats_mode`, `gp_autostats_mode_in_functions`, `gp_autostats_on_change_threshold`)

Связанные ловушки (не этот секрет, но рядом):

- `gp_autostats_mode_in_functions` должен быть выставлен **внутри** функции
- `on_change` + высокий `gp_autostats_on_change_threshold` → «тихий» пропуск ANALYZE

---

## 4. Как исправлять

1. После load в parent — **явный** `ANALYZE` parent (или batch `ANALYZE` по leaves).
2. Не полагаться на `on_no_stats` как гарантию для partition tree.
3. В CI/ETL gate: проверка `gp_stats_missing` / `last_analyze` по leaves.
4. Для fair CE-сравнений before/after — одинаковая политика ANALYZE на обеих ветках.

---

## 5. Checklist

- [ ] Load шёл в parent или в leaf?
- [ ] `SHOW gp_autostats_mode` на сессии load?
- [ ] Есть evidence `last_analyze` на leaves?
- [ ] Явный `ANALYZE` в runbook ETL?
