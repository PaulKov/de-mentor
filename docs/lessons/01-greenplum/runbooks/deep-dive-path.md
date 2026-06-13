# Расширенный Маршрут: Greenplum Lesson 01

Маршрут на 90-120 минут или отдельная appendix-сессия после базового урока. Его цель - дать техническую глубину без перегруза основного маршрута: QD/QE internals, slices/gangs, Motion, physical joins, storage caveats и системную таксономию.

Связанные материалы:

- презентация: [теоретическая презентация Greenplum](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx)
- гайд ведущего: [гайд ведущего](https://github.com/PaulKov/de-mentor/blob/master/decks/greenplum-theory/facilitator-guide.md)
- подготовка ученика: [подготовка ученика](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/student-prep.md)
- рабочая тетрадь: [рабочая тетрадь ученика](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md)
- домашка: [домашка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md)
- план домашки: [план домашки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/homework-plan.md)
- SQL-примеры: [storage and partitioning SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql)
- SQL по стратегиям partitioning: [partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql)
- SQL для мониторинга кластера: [cluster monitoring SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/cluster-monitoring.sql)
- QD/QE/slices/gangs explained: [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md)
- QD/QE deep dive: [master/segment data path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md)
- deep dive по joins: [physical joins in MPP](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md)
- deep dive по partitioning: [partitioning strategies](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md)
- ladder для EXPLAIN: [EXPLAIN plan reading](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md)

## Этап 1: 00:00-15:00 - QD/QE, Gang, Slices

Слайды: 1-8, затем appendix slide 28 при готовности ученика.

Что говорит ментор:

> Простая аналогия: QD - диспетчер смены, QE - исполнители на площадках, gang - команда исполнителей на всех сегментах, slice - независимый фрагмент плана. Технически QD режет plan на slices, готовит dispatch, создает `QueryDispatchDesc`, а QE исполняют свои части.

Что показывает в Greenplum:

```sql
EXPLAIN
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;
```

Команды:

```bash
python3 mentor-lab.py lesson greenplum --step 2
python3 mentor-lab.py hint greenplum plan-reading
python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join --sample
```

Что спрашиваем:

> Почему slice часто появляется рядом с Motion?

Ожидаемый ответ:

> Motion соединяет producer и consumer части distributed plan. Эти части исполняются разными gangs/QE и логически становятся разными slices.

Как проверяем:

- Ученик объясняет `QD`, `QE`, `gang`, `slice` сначала простыми словами.
- Ученик может технически сказать: plan режется на slices, slice исполняется gang-процессами на сегментах, а `QueryDispatchDesc` создается на QD и отправляется на QE.

Ссылки: [student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md), [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md), [homework](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md), [storage and partitioning SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql), [partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql).

## Этап 2: 15:00-40:00 - Data Path Master/Coordinator И Bulk I/O

Слайды: 7-9, 28.

Что говорит ментор:

> Master/coordinator должен оставаться control plane. Обычный query result собирается через Gather Motion и возвращается клиенту через coordinator. Но bulk data path лучше строить так, чтобы segments читали или писали параллельно: `gpfdist external table`, `COPY ON SEGMENT`-паттерны, внешние источники или PXF-подходы.

Что показывает в Greenplum:

```sql
EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_good;
```

Пояснение:

- `Gather Motion` собирает финальный result на coordinator.
- `Redistribute Motion` и `Broadcast Motion` передают tuple chunks между QE через interconnect.
- Для bulk I/O строки не должны массово "ехать через master", если есть segment-parallel path.

Команды:

```bash
python3 mentor-lab.py hint greenplum motion
python3 mentor-lab.py check greenplum
```

Что спрашиваем:

> Почему `gpfdist external table` лучше для больших загрузок, чем ручной поток через client/coordinator?

Ожидаемый ответ:

> Segments читают данные параллельно как HTTP clients, а coordinator управляет планом. Так throughput масштабируется сегментами, а master не становится центральной трубой.

Как проверяем:

- Ученик отличает result gather от parallel external table read.
- Ученик не говорит, что Redistribute Motion гоняет все строки через master.

Ссылки: [student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md), [homework](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md), [storage and partitioning SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql), [cluster monitoring SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/cluster-monitoring.sql), [partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql).

## Этап 3: 40:00-65:00 - Storage Internals, Defaults И Partitioning Strategies

Слайды: 10-12, 16, 29.

Что говорит ментор:

> Heap vs AO row vs AOCO - это не косметика. Heap удобен для mutable/small tables. AO row и AOCO оптимальны для append-heavy аналитики. AOCO хранит колонки отдельно, дает column pruning и compression. Но storage не отменяет distribution, statistics и partition design.

Что показывает в Greenplum:

```sql
\i /mentor-lab/examples/storage-and-partitioning.sql
\i /mentor-lab/examples/partitioning-strategies.sql
\d+ lesson01.storage_aoco_demo

SELECT n.nspname, c.relname, am.amname AS access_method
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_am AS am ON am.oid = c.relam
WHERE n.nspname = 'lesson01'
  AND c.relname LIKE 'storage_%_demo'
ORDER BY c.relname;

SELECT *
FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson01';
```

Команды:

```bash
python3 mentor-lab.py psql greenplum
```

```sql
SHOW gp_default_storage_options;
```

Не выполняем на уроке без необходимости:

```bash
gpconfig -c gp_default_storage_options \
  -v "'appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1'"
gpconfig -s gp_default_storage_options
gpstop -u
```

Что спрашиваем:

> В каком порядке думать: storage, distribution, partitioning или grain?

Дополнительный вопрос:

> Почему partition key не равен distribution key, и когда выбрать `PARTITION BY RANGE`, `PARTITION BY LIST`, `PARTITION BY HASH`?

Ожидаемый ответ:

> Сначала grain и workload, затем distribution/join locality, затем partitioning для pruning/retention, затем storage/compression под scan pattern.

Как проверяем:

- Ученик видит `appendoptimized=true`, `orientation=column`, column `ENCODING`.
- Ученик объясняет precedence: table `WITH/ENCODING` сильнее role/database/cluster defaults.
- Ученик не путает `PARTITION BY RANGE (sale_date)` с `DISTRIBUTED BY (customer_id)`.
- Ученик выбирает RANGE / LIST / HASH по workload, понимает `DEFAULT partition`, no default partitioning и out-of-range INSERT.
- Ученик считает `leaf_partitions` через `pg_partition_tree` и знает compatibility view `gp_toolkit.gp_partitions`.
- Ученик узнает maintenance snippets: `ATTACH PARTITION`, `DETACH PARTITION`, retention `DROP TABLE`.

Ссылки: [student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md), [homework](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md), [storage and partitioning SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql), [partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql), [partitioning strategies deep dive](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md).

## Этап 4: 65:00-95:00 - EXPLAIN Ladder И Physical Joins In MPP

Слайды: 24-27.

Что говорит ментор:

> В MPP у join две оси. Первая - локальный алгоритм: Hash Join, Merge Join, Nested Loop. Вторая - data movement: co-located join, Broadcast Motion, Redistribute Motion. Нельзя сказать "там Hash Join" и считать анализ законченным.

Что показывает в Greenplum:

```sql
EXPLAIN
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;

EXPLAIN
SELECT p.category, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_products AS p USING (product_id)
GROUP BY p.category;
```

Команды:

```bash
python3 mentor-lab.py hint greenplum physical-joins
python3 mentor-lab.py hint greenplum plan-reading
```

Что спрашиваем:

> Когда Broadcast лучше Redistribute?

Ожидаемый ответ:

> Когда broadcast side мала после фильтров и дешевле разослать ее всем сегментам, чем перераскладывать большой fact. Для большой стороны Broadcast опасен.

Как проверяем:

- Ученик заполняет ladder: leaf scans, local work, join algorithm, first Motion, rows out, global work, RCA.
- Ученик отличает co-located join от Broadcast/Redistribute join.
- Ученик понимает, почему один distribution key не оптимизирует все joins.

Ссылки: [student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md), [homework](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md), [storage and partitioning SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql), [partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql).

## Этап 5: 95:00-120:00 - System Taxonomy, Caveats И Next Lesson

Слайды: 30 и summary slide 23.

Что говорит ментор:

> SMP, shared-disk, MPP, EPP/cloud elastic, lakehouse и HTAP отличаются тем, куда они переносят bottleneck. Greenplum силен в MPP-аналитике, но требует дисциплины: distribution, stats, partitioning, bulk I/O, operational maintenance.

Что показывает в Greenplum:

```sql
SELECT 'distribution' AS topic, gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_good
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

Команды:

```bash
python3 mentor-lab.py hint greenplum mpp-systems
python3 mentor-lab.py runbook greenplum homework
python3 mentor-lab.py grade greenplum --dry-run
```

Что спрашиваем:

> Что принести на Lesson 02?

Ожидаемый ответ:

> DDL модели, distribution rationale, partitioning intro checks, skew checks, EXPLAIN evidence и вопросы по statistics/incremental loads/late-arriving facts.

Как проверяем:

- Ученик классифицирует сценарии как SMP/MPP/EPP/lakehouse/HTAP.
- Ученик называет caveat: ALTER TABLE storage changes требуют понимания rewrite/maintenance и не являются бесплатной кнопкой.
- Ученик забирает [homework](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md) и [homework plan](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/homework-plan.md).

Ссылки: [student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md), [homework](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md), [storage and partitioning SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql), [partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql).
