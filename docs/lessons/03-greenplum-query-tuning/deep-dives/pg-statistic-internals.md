# Deep-Dive: Статистика, гистограммы и оценка кардинальности (GP 6.25)

## Зачем Это Senior/Principal

Если вы не понимаете, *какие числа* видит optimizer, любой rewrite SQL остаётся гаданием.
В Greenplum/PostgreSQL lineage selectivity строится на слотах `pg_statistic`, а не на «средней кардинальности таблицы».

Статистика влияет на: **join order**, **Broadcast vs Redistribute**, **число групп GROUP BY**, **memory/spill**.

## Путь Данных

```text
ANALYZE
  → sample rows (≈ 300 × statistics_target)
  → compute n_distinct / MCV / equi-depth histogram / correlation
  → запись в pg_statistic (catalog heap, возможен TOAST)
  → Legacy selfuncs / GPORCA metadata читают slots при costing
```

Код (`6X_STABLE`):

- [`analyze.c`](https://github.com/greenplum-db/gpdb/blob/6X_STABLE/src/backend/commands/analyze.c)
- [`selfuncs.c`](https://github.com/greenplum-db/gpdb/blob/6X_STABLE/src/backend/utils/adt/selfuncs.c)
- [`pg_statistic.h`](https://github.com/greenplum-db/gpdb/blob/6X_STABLE/src/include/catalog/pg_statistic.h)

## Состав Статистики Колонки

| Поле `pg_stats` | Смысл |
|---|---|
| `null_frac` | Доля NULL |
| `n_distinct` | NDV: `>0` абсолют; `<0` доля от rows (`-1` ≈ unique) |
| `most_common_vals` / `most_common_freqs` | MCV + частоты |
| `histogram_bounds` | Границы equi-depth корзин |
| `correlation` | Физ. порядок vs logical |

### Слоты `stakind` в `pg_statistic`

| stakind | Смысл | Где данные |
|---|---|---|
| 1 | MCV | `stavalues` = values, `stanumbers` = freqs |
| 2 | Histogram bounds | `stavalues` = sorted bounds |
| 3 | Correlation | `stanumbers` |
| 4+ | MCELEM / расширенные (если тип поддерживает) | |

Физически: обычный heap-tuple каталога; большие arrays → TOAST. Отдельного proprietary stats-file per column нет.

## Гистограмма: Как Выглядит и Сколько Шагов

Это **не** «график для BI», а массив границ корзин **равной плотности строк** (equi-depth / equi-height).

- GUC `default_statistics_target` (на стенде `greenplum-625`: **100**).
- `ANALYZE` строит до ~`target` MCV и ~`target` buckets.
- `array_length(histogram_bounds) ≈ target + 1` (на стенде **101** для `amount`, `customer_id`, …).
- Значения из MCV **исключаются** из построения histogram.
- Если NDV мал и всё помещается в MCV → `histogram_bounds` = NULL (пример: `sale_date`, `segment`).

Selectivity для `BETWEEN lo AND hi`:

1. доля полных корзин внутри диапазона;
2. плюс доля края (интерполяция внутри partial bucket).

### Пример Со Стенда (`amount`)

```text
histogram_bounds ≈ {1.67, 4.33, 6.67, 9.00, … }  -- 101 граница
```

Артефакты: `artifacts/lesson-03/plan-screens/stats-*.png`, `artifacts/lesson-03/stats/`.

## MCV: Пример

`dim_customer.segment`:

```text
vals  = {enterprise, mid, smb, test}
freqs ≈ {0.314, 0.314, 0.314, 0.059}
```

`WHERE segment = 'enterprise'` → sel ≈ 0.314 (**не** 1/4).
`WHERE segment = 'test'` → sel ≈ 0.059.

## Как Оцениваются Предикаты

| Предикат | Опора на stats |
|---|---|
| `col = const` | MCV freq или `(1−Σmcf)/(NDV−\|MCV\|)` / `1/NDV` |
| `col < / BETWEEN` | Histogram bounds |
| `AND` | По умолчанию `s1·s2` (независимость) |
| `OR` | `s1+s2−s1·s2` (тоже с оговорками) |
| `f(col) = …` | Часто **нет** stats → дефолтная selectivity |

Код selectivity: `eqsel`, `scalarltsel`, … в `selfuncs.c`.

## GROUP BY / «Векторы Плотности»

Упрощённо:

```text
groups(col)   ≈ n_distinct(col)
groups(a,b)   ≈ min(NDV(a)*NDV(b), rows)   -- независимость ключей
```

На стенде `GROUP BY region` → 4 группы, estimate совпадает.

Ошибка растёт, когда ключи коррелированы или группировка по выражению.

**GP 6.25:** нет `CREATE STATISTICS` / `pg_statistic_ext` (это PG10+/GP7 market practice).
На GP6 чиним через `SET STATISTICS`, rewrite и **TEMP decomposition**.

## Хорошие Оценки (Стенд, EXPLAIN ANALYZE)

| Предикат | Estimate | Actual | Комментарий |
|---|---|---|---|
| `sale_date` Feb window | ~22400/seg | ~22896/seg | range / MCV дат |
| `product_id = 1` | 75/seg | ~78/seg | ≈ N/NDV |
| `segment = enterprise` | 785 | 788 | MCV freq |
| join `test` ∧ date≥Feb | 2068 | ~2296 | ~10% — уже независимость |

## Когда Хорошая Статистика Не Помогает

1. **Коррелированные фильтры** (`region` ∧ `segment`) — модель независимости.
2. **Many-join star** — ошибки перемножаются на цепочке joins/Motion.
3. **Функции на колонках** (`date_trunc`, `lower`) — stats колонки не применяются.
4. **Skew + значение вне MCV** — сильная недо/переоценка.
5. **Устаревший ANALYZE** после bulk load / partition exchange.

## Путь Решения (Market Practice)

```text
1. EXPLAIN ANALYZE → найти узел с rows ≪/≫ actual
2. Прочитать pg_stats по колонкам фильтра/join
3. ANALYZE (и после каждого существенного load)
4. ALTER COLUMN … SET STATISTICS N; ANALYZE  — больше buckets/MCV
5. Упростить предикат (убрать expr / лишние AND)
6. TEMP stage: сузить → ANALYZE → join  (главный рычаг на GP6)
7. На GP7/PG10+: CREATE STATISTICS (ndistinct/mcv/dependencies)
```

## Операционный Контракт

```sql
ANALYZE lesson03.fact_sales;
ALTER TABLE lesson03.fact_sales ALTER COLUMN sale_date SET STATISTICS 200;
ANALYZE lesson03.fact_sales;
SHOW default_statistics_target;
```

- После ETL / exchange → `ANALYZE` обязателен.
- После `CREATE TEMP … AS` → `ANALYZE` сразу.
- Не поднимайте `default_statistics_target` глобально «в максимум» без нужды: дороже `ANALYZE` и больше catalog.
