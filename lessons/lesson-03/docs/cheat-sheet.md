# Шпаргалка: Урок 03

Стенд: `greenplum-625`. БД: **`mentor`**. Схема: **`lesson03`**.

## Словарь

| | |
|---|---|
| **GUC** | Grand Unified Configuration — параметр сервера (`SHOW`/`SET`). |
| **optimizer** | GUC выбора движка плана: `on` = GPORCA, `off` = Legacy. |
| **QD / QE** | Query Dispatcher / Query Executor. |
| **Motion** | Redistribute / Broadcast / Gather между сегментами. |
| **Star-join** | Fact в центре + несколько Dimension по FK («звезда»). |
| **Snowflake** | Dims нормализованы дальше → ещё больше joins. |

## Optimizer (GP 6.25)

```sql
SHOW optimizer;           -- GUC
SET optimizer = on;       -- GPORCA
SET optimizer = off;      -- Legacy
```

| Когда | Выбор |
| --- | --- |
| Many-join OLAP, distribution-heavy | чаще ORCA |
| Простой SQL, быстрый planning, fallback | Legacy |
| Всегда | измерять EXPLAIN, не верить |

## Чтение Плана

0. Зафиксируй optimizer on/off.
1. Найди все Motion и ключ перераспределения.
2. Найди самый большой input у join.
3. Сравни estimate rows vs actual (если `EXPLAIN ANALYZE`).
4. Проверь pruning / ширину scan.

## Статистика

```sql
SHOW default_statistics_target;  -- обычно 100 → ~100 buckets, hist_bounds≈101

SELECT attname, n_distinct, most_common_vals, most_common_freqs,
       array_length(histogram_bounds, 1) AS hist_n
FROM pg_stats
WHERE schemaname = '...' AND tablename = '...';

ANALYZE myschema.mytable;
ALTER TABLE myschema.mytable ALTER COLUMN col SET STATISTICS 200;
ANALYZE myschema.mytable;
```

| Предикат | Legacy | ORCA |
| --- | --- | --- |
| `=` | MCV freq или residual/NDV | `CBucket` density = freq/NDV |
| `<` / `BETWEEN` | `histfrac` + края | overlap bucket → SF |
| `AND` | `∏ sᵢ` | damped `∏ (SF · 0.75ⁱ)` |
| `OR` | `s1+s2−s1s2` | `Σ rows · 0.75ᵏ` |
| `IN` / `NOT IN` | array/OR / AND≠ | ArrayCmp / disj / anti-semi |
| `GROUP BY` | `estimate_num_groups` | damped `∏ NDV` |

**Вектор плотности:** `most_common_freqs[]` + в ORCA `frequency/distinct` на bucket.

Диагностика: `EXPLAIN ANALYZE` → `rows` vs `actual` → `pg_stats` → формулы → `ANALYZE` / `SET STATISTICS` / TEMP.

Демо: `labs/greenplum-625/examples/lesson03-cardinality-histogram-demo.sql`.

Помни: `ANALYZE` после load/TEMP — часть контракта, не «опция».

## TEMP Паттерн

```sql
CREATE TEMP TABLE tmp_step AS
SELECT ...          -- сужающий фильтр!
DISTRIBUTED BY (...);
ANALYZE tmp_step;
```

| Где | Путь |
| --- | --- |
| TEMP TABLE | `base/<dboid>/t_<relfilenode>` на QE (`pg_temp_NNN`) |
| Spill Sort/Hash | `<datadir>/base/pgsql_tmp/pgsql_tmp_Sort_*` |
| Маркер spill | `Sort Method: external merge Disk: …` + `statement_mem` |

### TEMP: сессия и ON COMMIT

| Режим | После COMMIT | Конец сессии (`\q`) |
| --- | --- | --- |
| `PRESERVE ROWS` (default) | таблица + строки живы | удаляется |
| `DELETE ROWS` | таблица жива, строк 0 | удаляется |
| `DROP` | таблицы нет | — |

```sql
SELECT pg_backend_pid(), pg_my_temp_schema()::regnamespace;
SELECT n.nspname, c.relname, c.relpersistence, pg_relation_filepath(c.oid)
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.oid = pg_my_temp_schema();
```

Демо: `lesson03-temp-on-commit-lifecycle.sql`.

### ANALYZE: вручную / авто / когда обновляли

```sql
ANALYZE myschema.mytable;                 -- вручную (ETL-контракт)
SHOW gp_autostats_mode;                   -- авто: on_no_stats|on_change|none

SELECT relname, last_analyze, last_autoanalyze, n_mod_since_analyze
FROM pg_stat_user_tables WHERE schemaname = 'myschema';
```

Автомат GP6 = **`gp_autostats_*`** (planner дописывает ANALYZE), не «cron autovacuum для DWH».  
Демо: `lesson03-stats-analyze-lifecycle.sql`.

## CTE vs TEMP vs Spill

| Инструмент | Когда |
| --- | --- |
| CTE | Логическая читаемость; optimizer может инлайнить |
| TEMP | Нужен physical stage, stats, distribution |
| Spill | Не хватило `statement_mem` — диск без CREATE TEMP |

## Storage

| Тип | Когда |
| --- | --- |
| Heap | dims, staging с updates |
| AO row | bulk append row-oriented |
| AOCO | scan-heavy fact, узкая projection |

## Не Путать

- Partition pruning ≠ отсутствие Motion
- AOCO ≠ лекарство от skew
- TEMP без фильтра может увеличить стоимость
