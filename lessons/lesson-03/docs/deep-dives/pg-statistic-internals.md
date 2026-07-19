# Deep-Dive: Статистика, гистограммы, selectivity и cardinality (GP 6.25)

## Зачем Это Senior/Principal

Если вы не понимаете, *какие числа* видит optimizer, любой rewrite SQL остаётся гаданием.
В Greenplum/PostgreSQL lineage selectivity строится на слотах `pg_statistic`, а не на «средней кардинальности таблицы».

Статистика влияет на: **join order**, **Broadcast vs Redistribute**, **число групп GROUP BY**, **memory/spill**.

Два оптимизатора читают одни и те же catalog-slots, но **комбинируют** их по-разному:

| | Legacy (`optimizer=off`) | GPORCA (`optimizer=on`) |
|---|---|---|
| Единица оценки | `Selectivity ∈ (0,1]` | `scale_factor ≈ 1/selectivity` |
| Комбинация AND | `∏ sᵢ` (независимость) | сортировка SF + **damping** `0.75ⁿ` |
| Комбинация OR | `s1+s2−s1·s2` | накопление rows с damping |
| Структуры | MCV + equi-depth bounds | `CHistogram` / `CBucket(freq, NDV)` |
| GROUP BY | `estimate_num_groups` | `GetCumulativeNDVs` + damping |

---

## Путь Данных

```text
ANALYZE
  → sample rows (≈ 300 × statistics_target)
  → compute n_distinct / MCV / equi-depth histogram / correlation
  → запись в pg_statistic (catalog heap, возможен TOAST)
  → Legacy selfuncs / GPORCA metadata читают slots при costing
```

### Код (рабочие ссылки)

Greenplum 6.x lineage (архив / Cloudberry fork — тот же PostgreSQL/GPORCA tree):

| Что | Ссылка |
|---|---|
| `ANALYZE` | [analyze.c](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/commands/analyze.c) |
| Legacy selectivity | [selfuncs.c](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/utils/adt/selfuncs.c) |
| AND/OR clause list | [clausesel.c](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/optimizer/path/clausesel.c) |
| Defaults `DEFAULT_EQ_SEL`… | [selfuncs.h](https://github.com/greenplum-db/gpdb-archive/blob/main/src/include/utils/selfuncs.h) |
| Catalog slots | [pg_statistic.h](https://github.com/greenplum-db/gpdb-archive/blob/main/src/include/catalog/pg_statistic.h) |
| ORCA bucket | [CBucket.h](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libnaucrates/include/naucrates/statistics/CBucket.h) |
| ORCA histogram | [CHistogram.h](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libnaucrates/include/naucrates/statistics/CHistogram.h) |
| ORCA filter AND/OR | [CFilterStatsProcessor.cpp](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libnaucrates/src/statistics/CFilterStatsProcessor.cpp) |
| ORCA scale/damping | [CScaleFactorUtils.cpp](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libnaucrates/src/statistics/CScaleFactorUtils.cpp) |
| ORCA GROUP BY | [CStatisticsUtils.cpp](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libnaucrates/src/statistics/CStatisticsUtils.cpp) (`GetCumulativeNDVs`) |
| Damping defaults | [CStatisticsConfig.h](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/include/gpopt/engine/CStatisticsConfig.h) |

Демо-SQL: [`lesson03-cardinality-histogram-demo.sql`](../../../../labs/greenplum-625/examples/lesson03-cardinality-histogram-demo.sql).

---

## Состав Статистики Колонки

| Поле `pg_stats` | Смысл |
|---|---|
| `null_frac` | Доля NULL |
| `n_distinct` | NDV: `>0` абсолют; `<0` доля от rows (`-1` ≈ unique) |
| `most_common_vals` / `most_common_freqs` | MCV + **вектор частот** |
| `histogram_bounds` | Границы equi-depth корзин |
| `correlation` | Физ. порядок vs logical |

### Слоты `stakind` в `pg_statistic`

| stakind | Смысл | Где данные |
|---|---|---|
| 1 | MCV | `stavalues` = values, `stanumbers` = freqs |
| 2 | Histogram bounds | `stavalues` = sorted bounds |
| 3 | Correlation | `stanumbers` |
| 4+ | MCELEM / расширенные (если тип поддерживает) | |

Физически: обычный heap-tuple каталога; большие arrays → TOAST.  
Полная цепочка `filepath → 8KB page → TOAST` — в разделе «Физическая цепочка» ниже.

---

## Гистограмма: Как Выглядит, Как Обновляется, На Что Влияет

Это **не** «график для BI», а массив границ корзин **равной плотности строк** (equi-depth / equi-height).

### Параметры построения

- GUC `default_statistics_target` (на стенде `greenplum-625`: **100**).
- `ANALYZE` строит до ~`target` MCV и ~`target` buckets.
- `array_length(histogram_bounds) ≈ target + 1` (на стенде **101** для `amount`, `customer_id`, …).
- Значения из MCV **исключаются** из построения histogram.
- Если NDV мал и всё помещается в MCV → `histogram_bounds` = NULL (пример: `sale_date`, `segment`).

### Как выглядит (схема)

```text
sorted non-MCV sample values
  │
  ▼
bounds[0] = min_sample
bounds[1] = quantile 1/target
…
bounds[target] = max_sample

bucket i:  [bounds[i], bounds[i+1]]
доля строк в каждом bucket ≈ (1 − Σ mcf − null_frac) / target
```

Пример со стенда (`amount`):

```text
histogram_bounds ≈ {1.67, 4.33, 6.67, 9.00, … }   -- 101 граница
```

Артефакты: `lessons/lesson-03/artifacts/plan-screens/stats-*.png`, `lessons/lesson-03/artifacts/stats/`.

### Как обновляется (кратко)

| Событие | Что делать |
|---|---|
| Bulk load / INSERT…SELECT | `ANALYZE` на затронутых таблицах/партициях |
| Partition exchange | `ANALYZE` root (для ORCA критично) + leaf |
| `ALTER … SET STATISTICS N` | Меняет target колонки → нужен повторный `ANALYZE` |
| `CREATE TEMP … AS` | `ANALYZE` сразу — иначе следующий plan врёт |
| Автоматика GP6 | см. раздел **«Ручной и автоматический ANALYZE»** ниже |

```sql
ANALYZE lesson03.fact_sales;
ALTER TABLE lesson03.fact_sales ALTER COLUMN amount SET STATISTICS 200;
ANALYZE lesson03.fact_sales;   -- пересобирает MCV + hist с новым target
```

### На что влияет

1. **Range-предикаты** (`<`, `<=`, `>`, `>=`, `BETWEEN`) — основная зона histogram.
2. **Join cardinality** косвенно (через оценки промежуточных rows после фильтров).
3. **Memory/spill** — `statement_mem` планируется от estimate.
4. **Не** заменяет MCV для equality по частым значениям.
5. **Не** спасает от коррелированных AND/OR и функций на колонках.

---

## Вектор Плотности в Greenplum

В разговоре про GP «вектор плотности» — это не отдельный тип в каталоге, а **две связанные структуры**:

### 1) MCV frequency vector (`stanumbers`)

Для колонки с MCV:

```text
density_vec_MCV[i] = most_common_freqs[i]     -- P(col = mcv[i])
Σ density_vec_MCV + residual + null_frac ≈ 1
```

Пример `dim_customer.segment`:

```text
vals  = {enterprise, mid, smb, test}
freqs ≈ {0.314, 0.314, 0.314, 0.059}   ← вектор плотности частых значений
```

### 2) Per-bucket density в GPORCA (`CBucket`)

ORCA хранит гистограмму как массив `CBucket` с полями:

```text
CBucket {
  lower, upper,          -- границы
  frequency,             -- доля строк bucket ∈ [0,1]
  distinct               -- NDV внутри bucket
}
```

**Плотность одного distinct-значения внутри bucket** (uniform assumption):

```text
density_bucket = frequency / max(1, distinct)
```

Это прямо видно в `CBucket::MakeBucketSingleton`: при сужении bucket до singleton

```text
ratio          = 1 / max(1, m_distinct)
distinct_new   = m_distinct * ratio      -- → ≤ 1
frequency_new  = m_frequency * ratio     -- = density_bucket
```

Код: [CBucket.cpp — MakeBucketSingleton](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libnaucrates/src/statistics/CBucket.cpp).

Итого:

```text
rows_matching_one_value_in_bucket ≈ rows_table × (frequency / NDV_bucket)
```

Legacy делает то же качественно через `(1−Σmcf−null)/otherdistinct` вне MCV.

---

## Legacy: Формулы Selectivity (из кода)

Константы ([selfuncs.h](https://github.com/greenplum-db/gpdb-archive/blob/main/src/include/utils/selfuncs.h)):

```text
DEFAULT_EQ_SEL     = 0.005
DEFAULT_INEQ_SEL   ≈ 0.3333333333333333
DEFAULT_RANGE_INEQ_SEL = 0.005
DEFAULT_UNK_SEL    = 0.005
DEFAULT_NUM_DISTINCT = 200
```

### Equality: `col = const` (`var_eq_const` / `eqsel`)

```text
если const IS NULL:
    sel = 0

если isunique:
    sel = 1 / tuples

если const ∈ MCV:
    sel = most_common_freqs[i]

иначе (не MCV):
    selec = 1 − Σmcf − null_frac
    otherdistinct = NDV − |MCV|
    если otherdistinct > 1:
        selec = selec / otherdistinct
    clamp: selec ≤ min(MCV freqs)   -- не чаще самого редкого MCV

если нет stats:
    sel = 1 / NDV_est   (или DEFAULT через get_variable_numdistinct)

для <> (negate):
    sel = 1 − sel − null_frac
```

### Range / inequality: histogram (`ineq_histogram_selectivity`)

Бинарный поиск границы → доля `histfrac` популяции **без MCV и NULL**:

```text
если const < bounds[0]:  histfrac = 0
если const > bounds[n]:  histfrac = 1
иначе:                   линейная интерполяция внутри bucket

binfrac = (scalar(const) − scalar(lo)) / (scalar(hi) − scalar(lo))
```

Caller (`scalarineqsel`) домножает на residual `(1−Σmcf−null)` и учитывает MCV, попавшие в предикат.

### Conjunctive AND (`clauselist_selectivity`)

Независимость:

```text
s_AND = ∏ sᵢ
```

(в коде: `s1 = s1 * s2` по списку clause).

### Disjunctive OR (`clauselist_selectivity_or`)

```text
s_OR = s1 + s2 − s1·s2     -- inclusion–exclusion для независимых событий
```

(в коде: `s1 = s1 + s2 - s1 * s2`).

### NOT

```text
sel(NOT P) ≈ 1 − sel(P) − (поправка на NULL для strict ops)
```

Для `<>` это ветка `negate` в `var_eq_const`.

### IN / `= ANY(array)` (`scalararraysel`)

- Разворачивается в OR по элементам (useOr) или в AND для `ALL`.
- Для equality часто суммируется через ту же OR-формулу / специальный containment path.
- Практическое следствие: `IN (много значений)` ≈ сумма sel с поправкой на пересечения; при значениях из MCV — суммируются freqs.

### NOT IN

Семантически близко к `AND (col <> vᵢ)` с осторожностью про NULL:

```text
NOT IN (NULLs…) → часто unknown/empty semantics
```

Оценщик обычно идёт через negator equality + AND; на практике лучше `NOT EXISTS` / anti-join — и для плана, и для оценок.

### GROUP BY Legacy: `estimate_num_groups`

Эвристика (комментарий в `selfuncs.c`):

1. Boolean expr → ×2 групп.
2. Свести выражения к уникальным Vars (`GROUP BY a, a+b` ≈ `a,b`).
3. Эквивалентные Vars разных rel → оставить меньший NDV.
4. Внутри rel: `∏ NDV`, clamp к `rows/10` при >1 Var, × restriction selectivity.
5. Между rel: перемножить результаты шага 4.
6. Clamp к `input_rows`; никогда не возвращать 0.

Упрощённо для одного rel:

```text
groups ≈ min( ∏ NDV(colᵢ)  [с clamp],  input_rows )
```

---

## GPORCA: Вероятностные Структуры и Формулы

### Структуры

```text
CStatistics
  ├── rows
  ├── UlongToHistogramMap  (colid → CHistogram)
  └── widths / NDV remain / …

CHistogram
  ├── CBucket[]            (freq, distinct, bounds, closedness)
  ├── NDVRemain / freqRemain   -- хвост вне buckets
  └── null frequency

CStatsPredConj / CStatsPredDisj / CStatsPredPoint / CStatsPredArrayCmp
```

ORCA работает в терминах **scale factor**:

```text
rows_out ≈ rows_in / scale_factor
scale_factor ≈ 1 / selectivity
```

### Equality / point filter

Bucket → singleton: `frequency_new = frequency / max(1, NDV)`.
Normalize histogram → `scale_factor = 1 / selectivity_after_filter`.

### Conjunctive AND (`CalcScaleFactorCumulativeConj`)

Default damping filter = **0.75** ([CStatisticsConfig](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/include/gpopt/engine/CStatisticsConfig.h)):

```text
DampedFilter(n) = 0.75ⁿ     (для n≥2 колонок; для 1 → 1.0)

1. Отсортировать scale_factors по убыванию (самый селективный первый)
2. SF_AND = ∏ max(MinRows, SFᵢ · DampedFilter(i))   -- i = 1..n
```

Это **не** чистое `∏ sᵢ`: damping ослабляет последующие фильтры (ORCA менее агрессивно «убивает» rows при многих AND, чем Legacy independence).

### Disjunctive OR (`CalcScaleFactorCumulativeDisj`)

Комментарий в коде:

```text
rows ≈ rows0 + rows1·0.75 + rows2·(0.75)² + …
где rowsᵢ = total_rows / SFᵢ
```

Затем кумулятивный SF = `total_rows / rows_acc`.

### NOT / inequality join defaults

```text
DefaultInequalityJoinPredScaleFactor = 3.0
DefaultJoinPredScaleFactor           = 100.0
DDefaultScaleFactorLike              = 150.0
```

### Equi-join (bucket)

```text
|R ⋈ S| ≈ |R| · |S| / max(NDV(R.a), NDV(S.b))
```

(см. комментарий equi-join в `CBucket.cpp`).

### GROUP BY ORCA: `GetCumulativeNDVs`

```text
DampedGroupBy(i) = 0.75^(i+1)

отсортировать NDV по убыванию
cumulative = NDV[0]
для i = 1..n-1:
    cumulative *= max(MinDistinct, NDV[i] * DampedGroupBy(i))

groups = min(cumulative, input_rows [, upper_bound_ndvs])
```

Код: `CStatisticsUtils::GetCumulativeNDVs` + `CGroupByStatsProcessor::CalcGroupByStats`.

---

## ORCA vs Legacy: Сводка по Предикатам

| Предикат | Legacy | ORCA |
|---|---|---|
| `=` MCV | freq | singleton / MCV hist merge |
| `=` non-MCV | residual/otherNDV | density = freq/NDV в bucket |
| `<` / `BETWEEN` | histfrac + MCV | overlap % bucket + normalize |
| `AND` | `∏ s` | SF product + **0.75 damping** |
| `OR` | `s1+s2−s1s2` | damped row accumulation |
| `NOT` / `<>` | `1−s−null` | inequality SF / complement hist |
| `IN` | OR/array sel | `CStatsPredArrayCmp` / disj |
| `NOT IN` | AND of ≠ (+ NULL traps) | anti-semi join stats path |
| `GROUP BY` | `estimate_num_groups` | damped ∏ NDV |
| Нет stats | `DEFAULT_EQ_SEL=0.005` и т.п. | `DefaultSelectivity` / dummy hist |

---

## Примеры: Хорошая vs Плохая Оценка

### Хорошие (обычно близко к actual)

```sql
-- MCV equality
SELECT count(*) FROM lesson03.dim_customer WHERE segment = 'enterprise';
-- sel ≈ 0.314

-- NDV equality
SELECT count(*) FROM lesson03.fact_sales WHERE product_id = 1;
-- sel ≈ 1/NDV(product_id)

-- Range по hist
SELECT count(*) FROM lesson03.fact_sales
WHERE amount BETWEEN 10 AND 20;

-- Одноколоночный GROUP BY
SELECT region, count(*) FROM lesson03.dim_customer GROUP BY region;
-- groups ≈ 4
```

### Плохие (модель независимости / expr / skew)

```sql
-- Коррелированные AND: Legacy ≈ s1*s2, actual часто выше
SELECT count(*)
FROM lesson03.dim_customer
WHERE region = 'us' AND segment = 'enterprise';

-- Функция на колонке — stats колонки не применяются
SELECT count(*)
FROM lesson03.fact_sales
WHERE date_trunc('month', sale_date) = DATE '2026-02-01';

-- Многоколоночный GROUP BY с корреляцией ключей
SELECT region, segment, count(*)
FROM lesson03.dim_customer
GROUP BY region, segment;
-- estimate может ≈ NDV(r)*NDV(s), actual << product

-- IN с редкими + частыми без учёта корреляции join выше по стеку
SELECT count(*)
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
WHERE c.segment IN ('enterprise','test')
  AND f.sale_date >= DATE '2026-02-01';
```

Полный сценарий с `EXPLAIN ANALYZE` и сравнением ORCA/Legacy:
[`lesson03-cardinality-histogram-demo.sql`](../../../../labs/greenplum-625/examples/lesson03-cardinality-histogram-demo.sql).

---

## Путь Решения (Market Practice)

```text
1. EXPLAIN ANALYZE → найти узел с rows ≪/≫ actual
2. Прочитать pg_stats (MCV / hist_n / n_distinct / null_frac)
3. ANALYZE (и после каждого существенного load)
4. ALTER COLUMN … SET STATISTICS N; ANALYZE
5. Упростить предикат (убрать expr / лишние AND)
6. TEMP stage: сузить → ANALYZE → join  (главный рычаг на GP6)
7. Сравнить SET optimizer = on/off — разные комбинаторы!
8. На GP7/PG10+: CREATE STATISTICS (ndistinct/mcv/dependencies)
```

## Ручной и Автоматический ANALYZE (GP 6.25)

### Коротко

Статистика — это «снимок» распределения данных, который optimizer читает при построении плана.  
Данные поменялись → снимок устарел → план врёт.  
Обновить снимок = выполнить **`ANALYZE`** (или дождаться автоматики, если она сработала).

### 1) Вручную (основной способ в DWH)

```sql
-- одна таблица
ANALYZE lesson03.fact_sales;

-- схема / несколько объектов
ANALYZE lesson03.dim_customer;
ANALYZE lesson03.dim_product;

-- после смены target колонки
ALTER TABLE lesson03.fact_sales ALTER COLUMN amount SET STATISTICS 200;
ANALYZE lesson03.fact_sales;

-- partitioned (ORCA): убедитесь, что root тоже покрыт
-- (GUC optimizer_analyze_root_partition влияет на поведение)
ANALYZE lesson03.fact_sales;
```

Контракт ETL: **после существенного load / exchange → явный `ANALYZE` в пайплайне**, не «надеемся на автомат».

### 2) Автоматически: что за «сервис» в Greenplum 6

В GP6 для пользовательских БД **нельзя полагаться на классический PostgreSQL autovacuum/autoanalyze** как на основной механизм обновления stats в DWH (autovacuum для user DB по сути не является рабочим путём academy/production Greenplum 6).

Главный автомат Greenplum — **встроенный Automatic Statistics Collection**, управляемый GUC:

| GUC | Роль |
|---|---|
| **`gp_autostats_mode`** | Когда planner сам дописывает шаг `ANALYZE` после DML |
| **`gp_autostats_on_change_threshold`** | Порог строк для режима `on_change` (default огромный) |
| **`gp_autostats_mode_in_functions`** | То же внутри PL-функций (default часто `none`) |
| **`gp_autostats_allow_nonowner`** | Разрешить авто-ANALYZE не-владельцу таблицы |

Значения `gp_autostats_mode`:

| Режим | Когда срабатывает |
|---|---|
| **`on_no_stats`** (default) | После `CTAS` / `INSERT` / `COPY` **владельцем**, если у таблицы **ещё нет** статистики |
| **`on_change`** | После `CTAS`/`INSERT`/`UPDATE`/`DELETE`/`COPY`, если затронуто строк **больше** `gp_autostats_on_change_threshold` |
| **`none`** | Автоматика выключена |

Механика: это **не отдельный daemon «как cron»**, а поведение QD/planner — к команде изменения данных **добавляется шаг ANALYZE**.  
Документация: [Updating Statistics with ANALYZE](https://techdocs.broadcom.com/us/en/vmware-tanzu/data-solutions/tanzu-greenplum/6/greenplum-database/best_practices-analyze.html).

Проверить настройки на стенде:

```sql
SHOW gp_autostats_mode;
SHOW gp_autostats_on_change_threshold;
SHOW gp_autostats_mode_in_functions;
SHOW gp_autostats_allow_nonowner;
```

Практический вывод для урока:

- Default `on_no_stats` помогает **первый** раз после создания пустой таблицы.
- После регулярных bulk load в уже «статистичную» fact-таблицу автомат **часто молчит** → нужен ручной `ANALYZE` в ETL.
- Для TEMP после `CREATE TEMP … AS` всегда делайте явный `ANALYZE` (не гадайте на autostats).

### 3) Где смотреть, когда статистика обновлялась последний раз

Каталог/views статистики активности:

```sql
SELECT
    schemaname,
    relname,
    last_analyze,          -- последний РУЧНОЙ ANALYZE
    last_autoanalyze,      -- последний авто-ANALYZE (если был)
    analyze_count,
    autoanalyze_count,
    n_mod_since_analyze,   -- сколько изменений с последнего analyze (оценка)
    n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'lesson03'
ORDER BY COALESCE(last_analyze, last_autoanalyze) NULLS FIRST, relname;
```

| Колонка | Смысл |
|---|---|
| `last_analyze` | Время **ручного** `ANALYZE` |
| `last_autoanalyze` | Время **автоматического** analyze (autostats / autoanalyze path) |
| `analyze_count` / `autoanalyze_count` | Сколько раз обновляли |
| `n_mod_since_analyze` | Насколько «устарела» картина (чем больше — тем сильнее нужен ANALYZE) |

Дополнительно (наличие/полнота slots, не timestamp):

```sql
-- gp_toolkit: таблицы без статистики
SELECT * FROM gp_toolkit.gp_stats_missing
WHERE smischema = 'lesson03';

-- человекочитаемые слоты
SELECT attname, n_distinct,
       array_length(histogram_bounds, 1) AS hist_n,
       most_common_vals IS NOT NULL AS has_mcv
FROM pg_stats
WHERE schemaname = 'lesson03' AND tablename = 'fact_sales';
```

На MPP иногда смотрят агрегат с сегментов через `gp_dist_random('pg_stat_all_tables')` (см. docs `pg_stat_all_tables`) — для академии достаточно `pg_stat_user_tables` на QD.

### Физическая цепочка (не «stats files»)

В Greenplum/PostgreSQL **нет** отдельного файла-гистограммы на колонку. Статистика — tuples каталога `pg_statistic`:

```text
pg_statistic
  → pg_relation_filepath() → base/<db_oid>/<relfilenode>
  → 8 KB heap pages
  → PageHeaderData → ItemIdData → HeapTupleHeaderData
  → stavalues / stanumbers (varlena arrays)
  → TOAST relation при больших arrays
```

На стенде `mentor` (наблюдение):

```sql
SELECT pg_relation_filepath('pg_statistic'::regclass);
-- ≈ base/16587/12537
SELECT pg_size_pretty(pg_relation_size('pg_statistic'::regclass));      -- ~928 kB
SELECT pg_size_pretty(pg_relation_size(
  (SELECT reltoastrelid FROM pg_class WHERE oid = 'pg_statistic'::regclass)
));  -- ~96 kB toast
```

Расширение `pageinspect` на учебном образе может отсутствовать — тогда достаточно filepath + sizes + понимание page/tuple/TOAST.

Демо-SQL: [`lesson03-stats-analyze-lifecycle.sql`](../../../../labs/greenplum-625/examples/lesson03-stats-analyze-lifecycle.sql).

## Операционный Контракт

```sql
ANALYZE lesson03.fact_sales;
ALTER TABLE lesson03.fact_sales ALTER COLUMN sale_date SET STATISTICS 200;
ANALYZE lesson03.fact_sales;
SHOW default_statistics_target;
SHOW gp_autostats_mode;

SELECT relname, last_analyze, last_autoanalyze, n_mod_since_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson03';
```

- После ETL / exchange → `ANALYZE` обязателен.
- После `CREATE TEMP … AS` → `ANALYZE` сразу.
- Не поднимайте `default_statistics_target` глобально «в максимум» без нужды: дороже `ANALYZE` и больше catalog.
- **GP 6.25:** нет `CREATE STATISTICS` / `pg_statistic_ext`.
- Не путайте «есть autostats» с «stats всегда свежие» — в DWH это разные вещи.
