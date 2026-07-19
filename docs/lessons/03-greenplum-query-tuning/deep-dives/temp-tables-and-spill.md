# Deep-Dive: Временные Таблицы, `pg_temp` и Spill

## Зачем TEMP В Тяжёлом OLAP

`TEMP` — это способ создать *новый physical stage* с:

- собственной кардинальностью;
- собственным `DISTRIBUTED BY`;
- собственным `ANALYZE`;
- явным lifecycle в сессии.

CTE этого контракта не даёт надёжно: оптимизатор может инлайнить или материализовать CTE иначе, чем вы думаете.

## Где Живёт TEMP

1. **Namespace:** `pg_temp_NNN` (session-local). Другие сессии объекты не видят.
2. **Каталог:** обычные `pg_class` записи во временном namespace.
3. **Файлы:** relation files на сегментах (временные relfilenode в data directory). В GPDB TEMP распределённая: данные лежат на QE, QD координирует.
4. **Lifecycle:** до конца сессии или по `ON COMMIT` правилу.

## Spill ≠ TEMP TABLE

Важно разделять два механизма:

| Механизм | Что это |
| --- | --- |
| `TEMP TABLE` | Явно созданная relation |
| temporary files / spill | Файлы hash/sort при нехватке `work_mem` |

Даже без `CREATE TEMP TABLE` исполнитель может писать spill files. Поэтому «у меня не было TEMP, значит не было диска» — ложь.

Диагностические ориентиры:

- рост temporary files на сегментах;
- node'ы Hash/Sort в `EXPLAIN ANALYZE` с дисковыми признаками;
- неадекватный `work_mem` на широком join.

## Паттерн Безопасной Декомпозиции

```sql
CREATE TEMP TABLE tmp_stage AS
SELECT ... -- обязательно сужающий фильтр
DISTRIBUTED BY (join_key);

ANALYZE tmp_stage;
```

Красные флаги:

- TEMP = полный факт без фильтра;
- забыли `ANALYZE`;
- distribution случайный, а следующий join идёт по другому ключу;
- много мелких TEMP без необходимости (overhead каталога/планирования).

## Связь С Планом

Хороший TEMP уменьшает:

- bytes в Redistribute/Broadcast;
- ширину промежуточного row;
- ошибку estimate на следующем join (после `ANALYZE`).

Плохой TEMP добавляет лишний materialize + double scan.
