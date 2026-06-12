# Mentor Guide

## Главная Идея

Не пытайся дать всю теорию Greenplum за час. Первый урок должен сформировать правильный рефлекс: перед созданием таблицы в MPP-базе инженер обязан подумать о grain, ключах join, cardinality и распределении нагрузки по сегментам.

## Как Вести Урок

Используй [презентацию PowerPoint](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx) вместе с поминутным presenter guide:

- deck source: [slides source](https://github.com/PaulKov/de-mentor/tree/master/decks/greenplum-theory/slides);
- facilitator guide: [facilitator guide](https://github.com/PaulKov/de-mentor/blob/master/decks/greenplum-theory/facilitator-guide.md);
- student prep: [student prep](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/student-prep.md);
- simple path: [simple path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/simple-path.md);
- deep-dive path: [deep-dive path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/deep-dive-path.md);
- homework route: [homework plan](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/homework-plan.md);
- QD/QE/slices/gangs explained: [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md);
- deep dive: [master/segment data path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md);
- partitioning deep dive: [partitioning strategies](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md);
- практика ученика: [student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md);
- домашка: [homework](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md);
- runnable SQL: [storage and partitioning SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql);
- partitioning SQL: [partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql);
- monitoring SQL: [cluster monitoring SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/cluster-monitoring.sql);
- автоматическая проверка: `python3 mentor-lab.py check greenplum`.

Презентация должна занимать не весь час, а примерно половину урока: 33 минуты на theory framing, 12 минут на hands-on diagnostics, затем incident/capstone/review. Подробный тайминг по каждому слайду находится в [facilitator guide](https://github.com/PaulKov/de-mentor/blob/master/decks/greenplum-theory/facilitator-guide.md).

Выбирай маршрут:

- [Simple path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/simple-path.md) - основной 60-минутный маршрут: MPP mental model, storage, distribution, skew, EXPLAIN, partitioning intro, homework.
- [Deep-dive path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/deep-dive-path.md) - расширенный 90-120 минут: QD/QE/gang/slices, QueryDispatchDesc, physical joins, Broadcast vs Redistribute, storage caveats.

CLI shortcuts:

```bash
python3 mentor-lab.py runbook greenplum simple
python3 mentor-lab.py runbook greenplum deep
python3 mentor-lab.py runbook greenplum homework
python3 mentor-lab.py runbook greenplum prep
```

Advanced track подключай только после базового цикла `skew -> EXPLAIN -> fix -> evidence`. Для сильного ученика используй appendix-слайды и четыре deep dive:

- [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md) - сначала простыми словами, затем технически объяснить QD, QE, slice, gang, Motion и `EXPLAIN`;
- [EXPLAIN plan reading](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md) - читать план по scan/local work/join/Motion/global work/Rows out;
- [Physical joins in MPP](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md) - отличать локальный join algorithm от MPP data movement;
- [Partitioning strategies](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md) - выбирать `PARTITION BY RANGE`, `PARTITION BY LIST`, `PARTITION BY HASH`, смотреть `DEFAULT partition`, no default partitioning, out-of-range INSERT, `leaf_partitions`, `pg_partition_tree`, `gp_toolkit.gp_partitions`, `ATTACH PARTITION`, `DETACH PARTITION`;
- [MPP system taxonomy](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md) - сравнивать SMP, MPP, EPP, lakehouse и HTAP по bottleneck.

### 0-5 Минут: Контекст

Скажи ученику:

> Сегодня мы будем смотреть не на синтаксис SQL, а на физику выполнения запроса. Один и тот же SQL может быть нормальным в PostgreSQL и дорогим в Greenplum.

Проверь, что ученик понимает разницу между transactional workload и analytical workload.

Коротко обозначь классы систем:

- `SMP`: один большой сервер, общая память/storage, проще в эксплуатации, но масштабируется в основном вертикально;
- `MPP`: shared-nothing, много сегментов с собственными ресурсами, хорошо масштабируется горизонтально, но требует distribution design;
- `EPP / cloud elastic`: compute и storage часто масштабируются независимо, удобно для эластики, но требует контроля стоимости и движения данных.

Обязательно покажи разницу между control plane и data plane:

- master/coordinator отвечает за подключение, metadata, planning, dispatch и gather;
- QE на segments исполняют slices и читают локальные данные;
- Motion передает строки между QE через interconnect;
- для больших загрузок избегай master как data pipe: показывай `gpfdist`/external tables как parallel segment path.

Коротко зафиксируй Greenplum vs sharded PostgreSQL:

- sharded PostgreSQL часто требует внешнего routing/fan-out слоя и discipline на стороне приложения;
- Greenplum дает единый SQL endpoint, optimizer/executor/interconnect внутри СУБД и видимый distributed plan;
- Greenplum не sharded PostgreSQL, а MPP engine на PostgreSQL heritage.

### 5-15 Минут: Архитектура

Объясни через три роли:

- coordinator принимает SQL и строит план;
- segments хранят данные и выполняют работу;
- interconnect передает данные между сегментами.

Контрольный вопрос:

> Если таблица распределена по `customer_id`, где физически лежит строка конкретного клиента?

### 15-25 Минут: Distribution

Дай правило первого приближения:

> Хороший distribution key часто совпадает с частым join key, имеет высокую cardinality и равномерно распределяет строки.

Попроси ученика выбрать ключ для `orders`, `payments`, `customers`.

### 25-35 Минут: EXPLAIN

Сконцентрируйся на Motion:

- `Gather Motion` собирает результат;
- `Broadcast Motion` копирует данные на сегменты;
- `Redistribute Motion` перераспределяет данные по новому ключу.

Не уходи глубоко в optimizer. Цель - научить замечать "данные поехали по сети".

### 35-42 Минут: Storage И Partitioning Intro

Выполни короткий storage demo:

```sql
\i /mentor-lab/examples/storage-and-partitioning.sql
\d+ lesson01.storage_aoco_demo

SELECT n.nspname, c.relname, am.amname AS access_method
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_am AS am ON am.oid = c.relam
WHERE n.nspname = 'lesson01'
  AND c.relname LIKE 'storage_%_demo'
ORDER BY c.relname;
```

Скажи емко:

> Heap, AO row и AOCO column решают scan/storage/compression задачи. Distribution решает placement. Partitioning intro нужен, чтобы не спутать pruning/retention с распределением по сегментам.

Покажи DDL-маркер:

```sql
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)
PARTITION BY RANGE (sale_date)
```

Если ученик готов к глубине, запусти отдельный drill:

```sql
\i /mentor-lab/examples/partitioning-strategies.sql

SELECT *
FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson01';
```

Скажи емко:

> RANGE подходит для дат и retention, LIST - для конечных категорий, HASH - для bucketization. `DEFAULT partition` полезен как safety net, но если его не мониторить, он прячет out-of-range INSERT и грязные значения. Partition key не равен distribution key.

Maintenance snippets для deep route: `ATTACH PARTITION`, `DETACH PARTITION`, retention `DROP TABLE`.

Columnstore defaults:

- table-level `WITH`;
- column-level `ENCODING`;
- database/role-level `gp_default_storage_options`;
- instance-level `gpconfig` показываем как production/admin snippet, не выполняем без необходимости.

### 42-52 Минут: Практика

Пусть ученик выполняет workbook сам. Помогай вопросами:

- "Какой сегмент получил больше строк?"
- "Почему низкая cardinality плоха для distribution?"
- "Что изменилось в плане после исправления?"

### 52-58 Минут: Design Review

Дай мини-кейс:

> У нас есть заказы, клиенты, товары и платежи. Нужно построить факт продаж для ежедневной аналитики по регионам, товарам и способам оплаты. Какой grain, distribution key и partition key ты выберешь?

Оценивай не "правильный ответ", а качество аргументации.

## Частые Ошибки Ученика

- Выбирает `status` как distribution key, потому что по нему часто фильтруют.
- Думает, что primary key автоматически решает распределение.
- Игнорирует cardinality.
- Смотрит только на SQL и не смотрит на `EXPLAIN`.
- Путает `Hash Join` как локальный алгоритм с `Redistribute Motion` как сетевой ценой.
- Думает, что хороший distribution key делает локальными все joins.
- Называет MPP "просто масштабированным PostgreSQL" и не видит network как часть плана.
- Не отличает partitioning от distribution.

## Критерии Успеха

Урок прошел хорошо, если ученик своими словами объяснил:

- почему `DISTRIBUTED BY(status)` плох для факта;
- зачем смотреть `gp_segment_id`;
- почему Motion может быть дорогим;
- чем co-located join отличается от Broadcast/Redistribute join;
- почему `Rows out` и фактические строки важнее красивой формы SQL;
- когда нужен SMP, MPP, EPP/cloud или lakehouse;
- чем ключ распределения отличается от partition key.
