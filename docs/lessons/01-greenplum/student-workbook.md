# Student Workbook

Этот workbook связан с маршрутами ментора и домашкой:

- student prep: `runbooks/student-prep.md`
- simple path: `runbooks/simple-path.md`
- deep-dive path: `runbooks/deep-dive-path.md`
- homework plan: `runbooks/homework-plan.md`
- homework: `homework.md`
- QD/QE/slices/gangs deep dive: `deep-dives/qd-qe-gang-slices-explained.md`
- cluster inspection: `../../../labs/greenplum/examples/cluster-inspection.sql`
- runnable storage/partitioning examples: `../../../labs/greenplum/examples/storage-and-partitioning.sql`

## Подготовка

Перед уроком пройди `runbooks/student-prep.md`. Если стенд не стартует, принеси ментору вывод команд из секции "Что принести ментору, если не завелось".

macOS:

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py psql greenplum
```

Windows PowerShell:

```powershell
py mentor-lab.py up greenplum
py mentor-lab.py psql greenplum
```

Если нужно начать заново:

```bash
python3 mentor-lab.py reset greenplum
python3 mentor-lab.py up greenplum
```

## Задание 0: Greenplum vs Sharded PostgreSQL

Сначала сформулируй разницу своими словами.

```text
Greenplum vs sharded PostgreSQL:

Single SQL endpoint:
Who builds distributed plan:
Who dispatches work:
Where data movement is visible:
Why application-side routing is not the main model:
```

Контрольная мысль:

- sharded PostgreSQL часто требует внешнего routing/fan-out слоя или ручной логики приложения;
- Greenplum дает единый SQL endpoint, где QD строит distributed plan, QE исполняют slices, а Motion виден в плане;
- Greenplum не sharded PostgreSQL: это MPP engine с optimizer/executor/interconnect как частью СУБД.

## Задание 1: Осмотри Кластер

Сначала выполни готовый inspection script:

```sql
\i /mentor-lab/examples/cluster-inspection.sql
```

Он покажет версию Greenplum, строки `gp_segment_configuration`, memory-related настройки из `pg_settings`, размер базы и свободное место из `gp_toolkit.gp_disk_free`.

Затем отдельно повтори главный topology-запрос:

```sql
SELECT content, role, preferred_role, mode, status, hostname, port
FROM gp_segment_configuration
ORDER BY content, role;
```

Ответь:

- сколько coordinator/master instances видно в output;
- сколько сегментов участвует в хранении данных;
- сколько segment hosts используется в Docker-стенде;
- какой узел принимает пользовательские подключения;
- заданы ли CPU/RAM limits в compose или контейнер берет лимиты Docker Desktop/Engine;
- почему в MPP-базе важна равномерность работы сегментов.

## Задание 1.1: QD, QE, Gang, Slice

Перед заданием можно открыть `deep-dives/qd-qe-gang-slices-explained.md`: там есть короткая аналогия, пример `EXPLAIN` с `Redistribute Motion 48:48` и объяснение, почему slice - это часть плана, а gang - группа QE-процессов.

Заполни короткую карту компонентов:

```text
QD:
QE:
gang:
slice:
Motion boundary:
```

Expected answer:

- `QD` - query dispatcher на coordinator/master: принимает SQL, планирует, режет plan на slices и dispatch-ит работу;
- `QE` - query executor на сегментах: исполняет slice на локальных данных;
- `gang` - набор QE-процессов, обычно по одному на segment для конкретного slice;
- `slice` - фрагмент distributed plan, часто отделенный Motion boundary;
- `Motion` - оператор передачи строк между slices/QE через interconnect.

## Задание 2: Найди Skew

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_bad
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

Затем посмотри распределение по статусам:

```sql
SELECT status, count(*) AS rows_count
FROM lesson01.fact_sales_bad
GROUP BY status
ORDER BY rows_count DESC;
```

Ответь:

- почему распределение по `status` опасно;
- какой сегмент получил больше работы;
- какие поля лучше подходят для distribution key.

## Задание 3: Поймай Motion

```sql
EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;
```

Найди в плане:

- `Redistribute Motion`;
- `Gather Motion`;
- строки, где optimizer двигает данные между сегментами.

## Задание 4: Сравни С Исправленной Таблицей

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_good
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

```sql
EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;
```

Ответь:

- стало ли распределение ровнее;
- какой Motion исчез или стал дешевле;
- почему `customer_id` лучше для этого join.

## Задание 5: Heap vs AO Row vs AOCO

Запусти runnable demo из `storage-and-partitioning.sql`.

Внутри `psql`:

```sql
\i /mentor-lab/examples/storage-and-partitioning.sql
\d+ lesson01.storage_heap_demo
\d+ lesson01.storage_ao_row_demo
\d+ lesson01.storage_aoco_demo

SELECT n.nspname AS schema_name, c.relname, am.amname AS access_method
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_am AS am ON am.oid = c.relam
WHERE n.nspname = 'lesson01'
  AND c.relname LIKE 'storage_%_demo'
ORDER BY c.relname;
```

Обрати внимание на DDL:

```sql
CREATE TABLE lesson01.storage_ao_row_demo (...)
WITH (appendoptimized=true, orientation=row, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id);

CREATE TABLE lesson01.storage_aoco_demo (
    amount numeric(12, 2) ENCODING (compresstype=zstd, compresslevel=3)
)
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id);
```

Ответь:

- где heap, где AO row, где AOCO;
- почему AOCO полезен для wide analytical scans;
- почему `orientation=column` не исправляет skew;
- когда `heap` может быть лучше для маленькой mutable dimension.

## Задание 6: Как Включить Columnstore

Table-level:

```sql
CREATE TABLE lesson01.fact_sales_aoco (
    sale_id bigint,
    customer_id integer,
    sale_date date,
    amount numeric(12, 2)
)
WITH (
    appendoptimized=true,
    orientation=column,
    compresstype=zstd,
    compresslevel=1
)
DISTRIBUTED BY (customer_id);
```

Column-level:

```sql
amount numeric(12, 2) ENCODING (compresstype=zstd, compresslevel=3)
```

Database-level default:

```sql
ALTER DATABASE mentor
SET gp_default_storage_options =
'appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1';
```

Role-level default:

```sql
ALTER ROLE gpadmin
SET gp_default_storage_options =
'appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1';
```

Instance-level default, production/admin snippet:

```bash
gpconfig -c gp_default_storage_options \
  -v "'appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1'"

gpconfig -s gp_default_storage_options
gpstop -u
```

Важно:

- на уроке instance-level `gpconfig` обычно не выполняем;
- сначала учимся задавать storage явно на table/column level;
- precedence: table `WITH/ENCODING` > role/database/cluster defaults.

## Задание 7: Partitioning Intro

Partitioning в первом уроке - только intro. Глубокая практика будет в `Lesson 02: Partitioning, statistics and incremental loads in MPP`.

Сравни bad/good пример из `storage-and-partitioning.sql`:

```sql
-- bad: partition не помогает типичному фильтру по sale_date
EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_partition_bad
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01';

-- good: PARTITION BY RANGE (sale_date) помогает pruning
EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_partition_good
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01';
```

Ответь:

- почему `PARTITION BY RANGE (sale_date)` помогает отчетам по датам;
- почему partition key не равен distribution key;
- почему partitioning помогает pruning/retention, а distribution помогает сегментам и joins.

## Задание 8: Мини Design Review

Спроектируй факт `fact_daily_sales`:

- grain;
- distribution key;
- partition key;
- основные dimensions;
- 2-3 риска модели.

Формат ответа:

```text
Grain:
Distribution key:
Partition key:
Dimensions:
Risks:
```

## Advanced Track: План, Joins, Архитектура

Эти задания включай, если базовые 5 заданий идут уверенно. Их можно дать как продолжение урока или домашнюю работу.

### Advanced 1: Прочитай План По Лестнице

```sql
EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;
```

Заполни:

```text
Leaf scans:
Local work:
Join algorithm:
First Motion:
Rows out / actual row surprise:
Global work:
One-sentence RCA:
```

Подсказка:

```bash
python3 mentor-lab.py hint greenplum plan-reading
```

### Advanced 2: Физика Join В MPP

Сравни три join patterns:

```sql
-- A. Плохой distribution относительно customer_id
EXPLAIN
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;

-- B. Хороший distribution относительно customer_id
EXPLAIN
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;

-- C. Хороший для customer_id, но не для product_id
EXPLAIN
SELECT p.category, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_products AS p USING (product_id)
GROUP BY p.category;
```

Ответь:

- где join co-located;
- где нужен `Broadcast Motion`;
- где нужен `Redistribute Motion`;
- почему один distribution key не оптимизирует все joins одновременно.

Подсказка:

```bash
python3 mentor-lab.py hint greenplum physical-joins
```

### Advanced 3: Выбери Класс Системы

Для каждого сценария выбери `SMP`, `MPP`, `EPP/cloud`, `lakehouse` или `HTAP`:

1. 2 TB данных, один сильный сервер, команда маленькая, важна простота эксплуатации.
2. 200 TB фактов, стабильные nightly loads, тяжелые joins, предсказуемая BI-нагрузка.
3. Петабайтный data lake, Spark/Trino/ML, открытые форматы и много команд.
4. Operational workload с транзакциями и near-real-time аналитикой.

Формат ответа:

```text
Scenario:
System class:
Primary bottleneck:
Why not the alternatives:
```

Подсказка:

```bash
python3 mentor-lab.py hint greenplum mpp-systems
```

## Домашка И Следующий Урок

После урока открой:

- `homework.md` - что сдать;
- `runbooks/homework-plan.md` - как разложить домашку на 60-90 минут;
- `storage-and-partitioning.sql` - SQL-демо, которое можно переиспользовать в домашней модели.

На следующий урок принеси:

- DDL фактов и dimensions;
- rationale по grain, distribution, partitioning и storage;
- self-check commands;
- `EXPLAIN` evidence;
- вопросы по partition pruning, statistics after load и incremental loads.

## Что Отправить Ученику После Урока

Скопируй ученику этот handoff pack, чтобы он сам поднял Greenplum, воспроизвел тестовую среду и выполнил домашку.

Материалы:

1. `runbooks/student-prep.md` - подготовка Docker, Python и базовая диагностика для macOS, Windows и Linux.
2. `../../../labs/greenplum/README.md` - как устроен Docker-стенд Greenplum и как его запустить.
3. `student-workbook.md` - задания урока и self-check по кластеру, skew, Motion, storage и partitioning intro.
4. `homework.md` - что нужно сдать после урока.
5. `runbooks/homework-plan.md` - план самостоятельной работы на 60-90 минут.
6. `../../../labs/greenplum/examples/cluster-inspection.sql` - проверка topology, segments, memory settings и disk free.
7. `../../../labs/greenplum/examples/storage-and-partitioning.sql` - runnable demo для Heap/AO/AOCO и partitioning intro.

Команды для macOS/Linux:

```bash
python3 mentor-lab.py doctor
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py psql greenplum
```

Команды для Windows PowerShell:

```powershell
py mentor-lab.py doctor
py mentor-lab.py up greenplum
py mentor-lab.py check greenplum
py mentor-lab.py psql greenplum
```

Что ученик должен увидеть:

- `mentor-lab.py check greenplum` возвращает `PASS`;
- `\i /mentor-lab/examples/cluster-inspection.sql` показывает 1 coordinator/master и 2 primary segments;
- `\i /mentor-lab/examples/storage-and-partitioning.sql` создает demo-таблицы для heap, AO row, AOCO и partitioning;
- в домашке есть DDL/архитектурные решения, skew check, `EXPLAIN` evidence и вопросы к Lesson 02.
