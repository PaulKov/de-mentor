# Deep-Dive: Статистика до `pg_statistic` и кода Greenplum

## Зачем Это Senior/Principal

Если вы не понимаете, *какие числа* видит optimizer, любой rewrite SQL остаётся гаданием. В Greenplum/PostgreSQL lineage selectivity строится на слотах статистики, а не на «средней кардинальности таблицы».

## Путь Данных

```text
ANALYZE
  → sample rows на сегментах
  → compute MCV / histogram / correlation
  → запись в pg_statistic (catalog heap)
  → planner читает slots при costing
```

Ключевые места в коде upstream PostgreSQL / GPDB lineage:

- `src/backend/commands/analyze.c` — sampling и расчёт статистики;
- `src/backend/utils/adt/selfuncs.c` — selectivity functions;
- `src/include/catalog/pg_statistic.h` — форма слотов.

В GPDB планирование выполняется на QD, но данные и локальные отношения живут на QE/segments; поэтому stale stats после partial load особенно опасны.

## Каталожный Контракт

Человекочитаемый слой:

```sql
SELECT * FROM pg_stats WHERE schemaname = 'lesson03' AND tablename = 'fact_sales';
```

Сырой слой:

```sql
SELECT starelid::regclass, staattnum, stainherit,
       stanullfrac, stawidth, stadistinct,
       stakind1, stanumbers1, stavalues1,
       stakind2, stanumbers2, stavalues2
FROM pg_statistic
WHERE starelid = 'lesson03.fact_sales'::regclass;
```

### Слоты `stakind`

Типичные значения (lineage PostgreSQL):

| stakind | Смысл |
| --- | --- |
| 1 | MCV values + frequencies |
| 2 | histogram bounds |
| 3 | correlation |
| 4 | MCELEM для arrays |
| 5+ | expression / расширенные виды stats |

`stavaluesN` — anyarray значений; `stanumbersN` — float4[] частот/доп. чисел. Большие массивы могут быть TOAST-нуты: на диске это уже toast relation системного каталога, а не «отдельный JSON-файл статистики».

## Как Это Выглядит На Диске

`pg_statistic` — обычная heap-таблица каталога. Физически:

1. tuple в heap page catalog relation;
2. varlena-данные slots inline или в TOAST;
3. visibility через обычный MVCC каталога.

Отдельного «бинарного stats file per column» в стиле некоторых proprietary engine у PostgreSQL/GPDB нет: источник истины — catalog tuples после `ANALYZE`.

Для пользовательских таблиц данные лежат в `base/<dboid>/<relfilenode>` (и AOCO segfiles), а статистика *о* них — в catalog.

## Практический Диагностический Цикл

1. Найти predicate, где estimate врёт.
2. Посмотреть `n_distinct` / MCV / histogram для колонок predicate.
3. Проверить `last_analyze` и объём изменений с прошлого анализа.
4. Сделать targeted `ANALYZE` и сравнить plan rows.
5. Только потом менять SQL/DDL.

## Связь С Уроком

В SQL-lab смотрите `fact_sales.sale_date` (range/histogram) и `dim_customer.segment` (MCV для `<> 'test'`).
