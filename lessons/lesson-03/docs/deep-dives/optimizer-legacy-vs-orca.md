# Deep-Dive: Legacy Postgres Planner vs GPORCA (Greenplum 6.25)

## Словарь (обязательно)

| Аббревиатура | Расшифровка |
|---|---|
| **GUC** | *Grand Unified Configuration* — параметр сервера PostgreSQL/Greenplum (`SHOW`/`SET` / `postgresql.conf`). Пример: `optimizer`. |
| **QD** | *Query Dispatcher* — процесс на master/coordinator: парсит, оптимизирует, диспатчит slices. |
| **QE** | *Query Executor* — процесс на segment: исполняет свой slice плана. |
| **MPP** | *Massively Parallel Processing* — параллельное исполнение с обменом через interconnect. |
| **GPORCA / ORCA** | *Pivotal Optimizer* — Cascades/memo optimizer (`optimizer=on`). |
| **Legacy planner** | Postgres-based planner Greenplum (`optimizer=off`). |
| **Motion** | Оператор обмена строк между сегментами: Redistribute / Broadcast / Gather. |
| **Slice / Gang** | Кусок плана и группа QE-процессов, которые его исполняют. |
| **DXL** | XML intermediate representation между GPORCA и executor (translator в `gpopt`). |
| **MCV** | *Most Common Values* в `pg_statistic` / `pg_stats.most_common_vals`. |
| **AO / AOCO** | Append-Only (row) / Append-Only Column-Oriented. |
| **Star-join** | Fact в центре + несколько Dimension по FK («звезда»). Много equi-joins от одной fact. |
| **Snowflake** | Dims нормализованы дальше (dim → sub-dim) → ещё больше joins. |

## История: от Legacy Postgres Planner к GPORCA

Краткий экскурс — зачем в одном продукте **два** оптимизатора.

| Год / этап | Что произошло |
|---|---|
| **До 2010** | Greenplum Database строится на PostgreSQL planner (OLTP-ориентированный path/cost model), адаптированном под MPP (Motion, distribution locus). Это и есть **Legacy**. |
| **Конец 2010** | Внутри Greenplum (затем Pivotal) стартует проект нового оптимизатора под аналитические MPP-нагрузки. Лидер направления — **Florian Waas**; ключевые авторы архитектуры — в т.ч. **Mohamed Soliman** и команда (см. SIGMOD’14). |
| **2014** | Статья *Orca: A Modular Query Optimizer Architecture for Big Data* (ACM SIGMOD). Cascades/memo, portable optimizer, tooling (в т.ч. AMPERE для воспроизводимости багов). |
| **≈ GP 4.3.5** | GPORCA появляется в продукте как опциональный / early optimizer (ещё не default). |
| **Greenplum 5 (2017)** | **GPORCA становится default** (`optimizer=on`). Legacy остаётся fallback и явным выбором сессии. |
| **2015–2016+** | Open-source Greenplum + дерево `gporca` в репозитории (Apache License). Сегодня удобные зеркала кода: [gpdb-archive](https://github.com/greenplum-db/gpdb-archive), [apache/cloudberry](https://github.com/apache/cloudberry). |

### Почему Legacy «не хватило»

PostgreSQL planner изначально заточен под **короткие OLTP** на одном узле: локальный join search, простые selectivity, нет first-class модели распределённого Motion.

В MPP/DWH типичны:

- star/snowflake с **множеством joins**;
- сотни/тысячи **партиций**;
- стоимость **Redistribute/Broadcast** часто доминирует над CPU scan;
- длинные analytical pipelines (agg + window + CTE).

Эвристики Legacy дают локально разумный plan, но часто проигрывают на глобальном join order и partition-aware transform. GPORCA строили как **cost-based search по memo** с Motion как гражданином первого класса.

### Почему Legacy не удалили

- Предсказуемый planning time на простом SQL.
- Fallback при feature gaps ORCA.
- Сопоставимость с PostgreSQL mental model для отладки.
- Иногда runtime Legacy лучше на узком классе запросов.

Подробные формулы selectivity/cardinality (AND/OR/IN/GROUP BY, density vector):  
[pg-statistic-internals.md](pg-statistic-internals.md).

## Pipeline Оптимизации

```text
SQL
 → Parse      (grammar → parse tree)
 → Rewrite    (views/rules → query tree)
 → Optimize   ← Legacy или GPORCA (выбор = GUC optimizer)
 → Dispatch   (QD → gangs / slices)
 → Execute    (QE + Motion + Gather на QD)
```

На Greenplum 6.25 выбор оптимизатора — это **GUC** `optimizer`:

```sql
SHOW optimizer;     -- on = GPORCA, off = Legacy
SET optimizer = on;
SET optimizer = off;
```

`SET` живёт в сессии `psql`. Новый коннект вернёт default кластера.

## Деревья плана по фазам (что видеть в EXPLAIN)

Ниже — реальные планы со стенда `greenplum-625` (GP 6.25.3).
Скрины: [`lessons/lesson-03/artifacts/plan-screens/`](../../artifacts/plan-screens/).
Текст: [`lessons/lesson-03/artifacts/plans/`](../../artifacts/plans/).

### Parse

SQL → `SelectStmt` / parse tree. Плана и Motion ещё нет.

Код: [`gram.y`](https://github.com/greenplum-db/gpdb/blob/6X_STABLE/src/backend/parser/gram.y),
[`analyze.c`](https://github.com/greenplum-db/gpdb/blob/6X_STABLE/src/backend/parser/analyze.c).

### Rewrite

View вроде `lesson03.v_star_join_orca_case` разворачивается в join graph.
Оптимизатор видит развёрнутый SQL, не имя view.

Код: [`rewriteHandler.c`](https://github.com/greenplum-db/gpdb/blob/6X_STABLE/src/backend/rewrite/rewriteHandler.c).

### Optimize → physical plan tree (пример: простой agg, GPORCA)

```text
Gather Motion 2:1  (slice2; segments: 2)
  ->  GroupAggregate
        ->  Sort
              ->  Redistribute Motion 2:2  (slice1)
                    Hash Key: region
                    ->  HashAggregate
                          ->  Seq Scan on dim_customer
Optimizer: Pivotal Optimizer (GPORCA)
```

Читаем фазы в дереве:

1. **Optimize** выбрал локальный `HashAggregate` + `Redistribute` по `region`.
2. **Dispatch** разрезал план на `slice1` / `slice2`.
3. **Execute** на QE → `Gather Motion` на QD.

### Optimize: star-join GPORCA vs Legacy

Один SQL (`v_star_join_orca_case`), два GUC:

| | GPORCA (`optimizer=on`) | Legacy (`optimizer=off`) |
|---|---|---|
| Маркер | `Optimizer: Pivotal Optimizer (GPORCA)` | `Optimizer: Postgres query optimizer` |
| Скрин | `explain-orca.png` | `explain-legacy.png` |
| Типичный фокус сравнения | join order + где стоит Redistribute | тот же SQL, другой path tree |

Сжатый readout GPORCA:

```text
Limit
  -> Gather Motion 2:1 (slice3)
       -> Sort + HashAggregate
            -> Redistribute Motion 2:2 (slice2)  -- по group keys
                 -> HashAggregate
                      -> Hash Join fact ⋈ product
                           -> Redistribute Motion 2:2 (slice1)
                                -> Hash Join fact ⋈ customer
                                     -> Seq Scan fact / dims
```

### Dispatch / Execute

- QD отправляет каждый slice на gang QE.
- Interconnect реализует Motion.
- Финальный `Gather Motion *:1` собирает результат на QD.

Код (якоря — рабочие деревья gpdb-archive / Cloudberry):

- Legacy planner: [`planner.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/optimizer/plan/planner.c)
- Motion paths: [`cdbpath.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/cdb/cdbpath.c)
- GPORCA: [`src/backend/gporca`](https://github.com/apache/cloudberry/tree/main/src/backend/gporca)
- Selectivity Legacy: [`selfuncs.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/utils/adt/selfuncs.c)
- ORCA stats: [`CFilterStatsProcessor.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libnaucrates/src/statistics/CFilterStatsProcessor.cpp)
- CDB dispatch/motion: [`src/backend/cdb`](https://github.com/greenplum-db/gpdb-archive/tree/main/src/backend/cdb)

## Legacy Postgres Planner

### Как работает

- Строит path trees в духе PostgreSQL (`joinpath`, `costsize`, `selfuncs`).
- Greenplum добавляет Motion/distribution через `cdbpath` / locus.
- Поиск join order ограничен эвристиками и локальным DP.

### Плюсы

- Предсказуем на простых/средних запросах.
- Быстрее planning time на коротком SQL.
- Надёжный fallback, когда ORCA не может построить план.
- Проще объяснить Senior’у через привычную PostgreSQL модель.

### Минусы

- Слабее на many-join star/snowflake.
- Чаще локально-оптимальный порядок joins.
- Меньше глобальных transform (agg pull-up, сложные CTE-сценарии).

### Когда эффективен

- 1–3 joins, локальные aggregates.
- Операционные/простые reporting queries.
- Когда ORCA даёт нестабильный/дорогой planning без выигрыша runtime.

## GPORCA (Pivotal Optimizer)

### Как работает

- Cascades-style: memo groups + transformation rules (xforms).
- Distribution/Motion — first-class citizens costing model.
- Исследует большее пространство эквивалентных планов.
- Translator `gpopt` переводит query tree ↔ DXL ↔ executable Plan.

### Плюсы

- Сильнее на сложных OLAP с многими joins.
- Лучше учитывает стоимость redistribute/broadcast.
- Часто находит лучший global join order.

### Минусы

- Дороже planning.
- Возможны feature gaps → fallback в Legacy.
- Сложнее debug (нужны status/minidump).
- Иногда «красивый» plan хуже на фактических stats.

### Когда эффективен

- Star/snowflake с 4+ joins.
- Сложные CTE/подзапросы, где важен reorder.
- Когда Motion cost доминирует и нужен distribution-aware search.

## Демо На Стенде `greenplum-625`

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py psql greenplum-625
```

```sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
SET optimizer = on;
EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;
SET optimizer = off;
EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;
```

Сравнивайте:

1. маркер Optimizer (GPORCA vs Postgres query optimizer);
2. порядок joins;
3. типы Motion и их положение относительно фильтров/agg;
4. `sliceK; segments: N`;
5. planning time vs runtime (через `EXPLAIN ANALYZE` на контролируемом окне).

## Практическое Правило

1. Зафиксируйте GUC `SET optimizer`.
2. Снимите before plan (и сохраните скрин/текст).
3. Исправьте stats/TEMP/distribution, если estimates врут.
4. Только потом меняйте optimizer или SQL shape.
5. After plan при том же GUC — иначе сравнение невалидно.
