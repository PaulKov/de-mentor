# Шпаргалка: Урок 03

## Optimizer (GP 6.25)

```sql
SHOW optimizer;
SET optimizer = on;   -- GPORCA
SET optimizer = off;  -- Legacy
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
SELECT attname, n_distinct, most_common_vals, histogram_bounds
FROM pg_stats
WHERE schemaname = '...' AND tablename = '...';
```

Помни: `ANALYZE` после существенного изменения данных — часть контракта, не «опция».

## TEMP Паттерн

```sql
CREATE TEMP TABLE tmp_step AS
SELECT ...
DISTRIBUTED BY (...);
ANALYZE tmp_step;
```

## CTE vs TEMP

| Инструмент | Когда |
| --- | --- |
| CTE | Логическая читаемость, оптимизатор может инлайнить |
| TEMP | Нужен новый physical stage, stats, distribution |

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
