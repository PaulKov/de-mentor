# Simple Path: Greenplum Lesson 01

Маршрут на 60 минут. Цель - не рассказать все про Greenplum, а научить новичка видеть MPP-физику: где лежит строка, кто ее обрабатывает, когда появляется Motion и как доказать исправление.

Cross-links:

- deck: `artifacts/greenplum-theory.pptx`
- facilitator guide: `decks/greenplum-theory/facilitator-guide.md`
- student prep: `docs/lessons/01-greenplum/runbooks/student-prep.md`
- workbook: `docs/lessons/01-greenplum/student-workbook.md`
- homework: `docs/lessons/01-greenplum/homework.md`
- homework plan: `docs/lessons/01-greenplum/runbooks/homework-plan.md`
- cluster inspection SQL: `labs/greenplum/examples/cluster-inspection.sql`
- cluster monitoring SQL: `labs/greenplum/examples/cluster-monitoring.sql`
- SQL examples: `labs/greenplum/examples/storage-and-partitioning.sql`
- partitioning strategy examples: `labs/greenplum/examples/partitioning-strategies.sql`

## Stage 1: 00:00-10:00 - MPP И Роли Компонентов

Слайды: 1-6.

Что говорит ментор:

> Greenplum не sharded PostgreSQL. В sharded PostgreSQL приложение или middleware часто само решает routing и fan-out. В Greenplum есть единый SQL endpoint, QD строит distributed plan, QE на сегментах исполняют slices, а gang - это группа процессов, которые синхронно выполняют slice.

Что показывает в Greenplum:

```sql
SELECT content, role, preferred_role, mode, status, hostname, port
FROM gp_segment_configuration
ORDER BY content, role;
```

Команды:

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py psql greenplum
```

Что спрашиваем:

> Что делает master/coordinator, а что делают segments?

Expected answer:

> Master/coordinator принимает подключение, парсит SQL, планирует, делает dispatch и собирает финальный результат. Segments хранят данные, исполняют QE slices и обмениваются строками через interconnect.

Как проверяем:

- Ученик называет `QD`, `QE`, `gang`, `slice` без путаницы с "просто шардами".
- Ученик может объяснить, почему master - потенциальное узкое место для control plane и final gather.

Переход:

> Теперь посмотрим, как физическая модель хранения влияет на scan, compression и демонстрацию columnstore.

Ссылки: `student-workbook.md`, `homework.md`, `cluster-inspection.sql`, `storage-and-partitioning.sql`.

## Stage 2: 10:00-24:00 - Execution, Lab Passport, Heap И AOCO

Слайды: 7-13.

Что говорит ментор:

> Перед первой реальной SQL-демонстрацией фиксируем, какой стенд поднят: один Docker service, один coordinator/master, два primary segments, mirrors нет. CPU/RAM limits не заданы в compose, поэтому контейнер живет внутри лимитов Docker Desktop/Engine. После этого показываем storage: Heap - row storage по умолчанию, AO row и AOCO подходят для append-heavy аналитики.

Что показывает в Greenplum:

```sql
\i /mentor-lab/examples/cluster-inspection.sql
\i /mentor-lab/examples/cluster-monitoring.sql

\i /mentor-lab/examples/storage-and-partitioning.sql
\d+ lesson01.storage_heap_demo
\d+ lesson01.storage_ao_row_demo
\d+ lesson01.storage_aoco_demo

SELECT n.nspname, c.relname, am.amname AS access_method
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_am AS am ON am.oid = c.relam
WHERE n.nspname = 'lesson01'
  AND c.relname LIKE 'storage_%_demo'
ORDER BY c.relname;
```

Команды:

```bash
python3 mentor-lab.py psql greenplum
```

```sql
\i /mentor-lab/examples/cluster-inspection.sql
\i /mentor-lab/examples/cluster-monitoring.sql
\i /mentor-lab/examples/storage-and-partitioning.sql
SHOW gp_default_storage_options;
```

CLI snippets outside `psql` for mentor context: `gpstate -s`, `gpstate -m`, `gpstate -c`, `gpstate -e`.

Production/admin snippet, не выполняем без необходимости:

```bash
gpconfig -c gp_default_storage_options \
  -v "'appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1'"

gpconfig -s gp_default_storage_options
gpstop -u
```

Что спрашиваем:

> Сколько segment instances реально участвует в хранении данных на нашем Docker-стенде?

Expected answer:

> Два primary segment instances (`content 0` и `content 1`) на одном segment host `greenplum`; master/coordinator - отдельная строка `content = -1`.

Дополнительный вопрос:

> Почему AOCO не спасает плохой distribution key?

Expected answer:

> AOCO меняет формат хранения и scan/compression, но не размещение строк по сегментам. Если distribution key плохой, часть сегментов все равно простаивает.

Как проверяем:

- Ученик видит `access_method` для heap/AO/AOCO.
- Ученик может назвать table-level, column-level, database-level, role-level и instance-level способы задать columnstore defaults.
- Ученик понимает, что instance-level `gpconfig` - административный пример, а не команда для обычного урока.

Ссылки: `student-workbook.md`, `homework.md`, `cluster-inspection.sql`, `cluster-monitoring.sql`, `storage-and-partitioning.sql`, `partitioning-strategies.sql`.

## Stage 3: 24:00-42:00 - Distribution, Skew, EXPLAIN И Motion

Слайды: 14-19.

Что говорит ментор:

> Distribution key - не "индекс" и не "partition key". Он решает, на каком сегменте живет строка. `gp_segment_id` превращает архитектурный спор в измерение. Motion в EXPLAIN показывает цену сети.

Что показывает в Greenplum:

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_bad
GROUP BY gp_segment_id
ORDER BY gp_segment_id;

EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;

EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;
```

Команды:

```bash
python3 mentor-lab.py hint greenplum skew
python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join --sample
```

Что спрашиваем:

> Увидев `Redistribute Motion`, какой вопрос задаем первым?

Expected answer:

> Почему данные нужно переложить: join key не совпал с distribution key, есть skew, нужна глобальная агрегация или финальный gather?

Как проверяем:

- Ученик называет сегмент с перекосом.
- Ученик отличает `Hash Join` как локальный алгоритм от `Redistribute Motion` как сетевой цены.
- Ученик связывает улучшение `fact_sales_good` с `DISTRIBUTED BY (customer_id)`.

Ссылки: `student-workbook.md`, `homework.md`, `cluster-inspection.sql`, `storage-and-partitioning.sql`.

## Stage 4: 42:00-60:00 - Partitioning Intro, Incident И Homework

Слайды: 17, 20-24.

Что говорит ментор:

> Partitioning intro в первом уроке нужен только как граница понятий: partitioning помогает pruning и retention, distribution помогает parallel placement и join locality. Глубокий partitioning lab будет в Lesson 02.

Что показывает в Greenplum:

```sql
\i /mentor-lab/examples/partitioning-strategies.sql

EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_partition_bad
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01';

EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_partition_good
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01';
```

Команды:

```bash
python3 mentor-lab.py incident start greenplum skewed-distribution
python3 mentor-lab.py grade greenplum --dry-run
python3 mentor-lab.py runbook greenplum homework
```

Если есть 5-7 минут на partitioning drill:

```sql
SELECT *
FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson01';
```

Ключевые маркеры: `PARTITION BY RANGE`, `PARTITION BY LIST`, `PARTITION BY HASH`, `DEFAULT partition`, `leaf_partitions`, `ATTACH PARTITION`, `DETACH PARTITION`, out-of-range INSERT.

Что спрашиваем:

> Почему partition key не равен distribution key?

Expected answer:

> Partition key выбирается под фильтры времени, pruning и lifecycle/retention. Distribution key выбирается под равномерность, join locality и параллельность.

Дополнительный вопрос:

> Когда выбрать RANGE / LIST / HASH?

Expected answer:

> RANGE - для дат/числовых интервалов и retention, LIST - для конечных категорий, HASH - для bucketization. No default partitioning: partitions и `DEFAULT partition` нужно объявлять явно.

Как проверяем:

- Ученик формулирует RCA: symptom, evidence, root cause, fix, validation.
- Ученик может посчитать `leaf_partitions` через `pg_partition_tree` или посмотреть их через `gp_toolkit.gp_partitions`.
- Ученик называет домашние deliverables из `homework.md`.
- Ученик понимает, что следующий урок - `Lesson 02: Partitioning, statistics and incremental loads in MPP`.

Ссылки: `student-workbook.md`, `homework.md`, `cluster-inspection.sql`, `cluster-monitoring.sql`, `storage-and-partitioning.sql`, `partitioning-strategies.sql`.
