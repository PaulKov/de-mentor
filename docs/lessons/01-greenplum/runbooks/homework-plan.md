# Homework Plan: Greenplum Lesson 01

План самостоятельной работы на 60-90 минут. Его задача - закрепить первый урок и подготовить следующий: `Lesson 02: Partitioning, statistics and incremental loads in MPP`.

Cross-links:

- deck: `artifacts/greenplum-theory.pptx`
- workbook: `docs/lessons/01-greenplum/student-workbook.md`
- homework: `docs/lessons/01-greenplum/homework.md`
- simple runbook: `docs/lessons/01-greenplum/runbooks/simple-path.md`
- deep-dive runbook: `docs/lessons/01-greenplum/runbooks/deep-dive-path.md`
- SQL examples: `labs/greenplum/examples/storage-and-partitioning.sql`

## Stage 1: 00:00-10:00 - Прочитать Задание И Зафиксировать Grain

Что говорит ментор перед выдачей:

> Не начинай с `DISTRIBUTED BY`. Начни с вопроса: одна строка факта что означает? За какой business event отвечает таблица?

Что показывает в Greenplum:

```sql
SELECT min(sale_date), max(sale_date), count(*)
FROM lesson01.fact_sales_good;
```

Команды:

```bash
python3 mentor-lab.py info greenplum
python3 mentor-lab.py runbook greenplum simple
```

Что спрашиваем:

> Какой факт самый большой и какой у него grain?

Expected answer:

> Например, `fact_sales` на grain `one sold item/order line per sale_id` или явно выбранный daily aggregate grain. Главное - grain сформулирован до ключей.

Как проверяем:

- В `homework.md` заполнены facts, dimensions и grain.
- Ученик не подменил grain partition key или primary key.
- Есть ссылка на `student-workbook.md` как источник базовых упражнений.

Ссылки: `student-workbook.md`, `homework.md`, `storage-and-partitioning.sql`.

## Stage 2: 10:00-35:00 - Distribution, Skew И EXPLAIN Evidence

Что говорит ментор:

> Для каждого большого fact объясни distribution key через join pattern и cardinality. Потом докажи это проверкой `gp_segment_id`.

Что показывает в Greenplum:

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_good
GROUP BY gp_segment_id
ORDER BY gp_segment_id;

EXPLAIN
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;
```

Команды:

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py hint greenplum skew
python3 mentor-lab.py hint greenplum motion
```

Что спрашиваем:

> Почему `status` плохой distribution key для большого факта?

Expected answer:

> Низкая cardinality создает skew: мало разных значений, строки концентрируются на части сегментов, параллелизм теряется.

Как проверяем:

- В домашке есть SQL self-check для skew.
- В домашке есть хотя бы один `EXPLAIN`.
- Ученик словами связывает Motion с distribution/join pattern.

Ссылки: `student-workbook.md`, `homework.md`, `storage-and-partitioning.sql`.

## Stage 3: 35:00-60:00 - Storage И Partitioning Intro

Что говорит ментор:

> Storage и partitioning не выбираются "по моде". AOCO хорош для широких append-heavy facts и аналитических scans. Partitioning нужен для pruning и retention, а не для равномерного распределения между сегментами.

Что показывает в Greenplum:

```sql
\i /mentor-lab/examples/storage-and-partitioning.sql
\d+ lesson01.storage_aoco_demo

EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_partition_good
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01';
```

Команды:

```bash
docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin greenplum \
  bash -lc '. /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor -v ON_ERROR_STOP=1 -f /mentor-lab/examples/storage-and-partitioning.sql'
```

Что спрашиваем:

> Почему partition key не равен distribution key?

Expected answer:

> Partition key выбирается под фильтр/pruning/retention, например `sale_date`. Distribution key выбирается под равномерность и co-located joins, например `customer_id`.

Как проверяем:

- В домашке есть `PARTITION BY RANGE` или явное объяснение, почему partitioning пока не нужен.
- В домашке есть storage choice: heap, AO row или AOCO.
- В домашке указано, что `gp_default_storage_options` можно задать на database/role/cluster level, но production-defaults не меняются без админского решения.

Ссылки: `student-workbook.md`, `homework.md`, `storage-and-partitioning.sql`.

## Stage 4: 60:00-90:00 - Optional Deep Tasks И Что Принести На Следующий Урок

Что говорит ментор:

> Если остается энергия, добавь deep evidence: plan-reading ladder, physical join analysis и список вопросов к Lesson 02.

Что показывает в Greenplum:

```sql
EXPLAIN ANALYZE
SELECT p.category, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_products AS p USING (product_id)
GROUP BY p.category;
```

Команды:

```bash
python3 mentor-lab.py hint greenplum plan-reading
python3 mentor-lab.py hint greenplum physical-joins
python3 mentor-lab.py runbook greenplum deep
python3 mentor-lab.py grade greenplum --dry-run
```

Что спрашиваем:

> Что нужно принести на Lesson 02: Partitioning, statistics and incremental loads in MPP?

Expected answer:

> DDL, grain/rationale, skew checks, EXPLAIN evidence, storage decision, partitioning questions, risks for late-arriving facts and statistics after load.

Как проверяем:

- Deliverables из `homework.md` заполнены.
- Есть self-check commands.
- Есть 3 риска и как они проверяются.
- Есть список вопросов на следующий урок.

Ссылки: `student-workbook.md`, `homework.md`, `storage-and-partitioning.sql`.

## Acceptance Criteria

Домашка принимается, если:

- grain описан до физического дизайна;
- distribution key выбран через cardinality и join pattern;
- partition key не смешан с distribution key;
- есть skew check через `gp_segment_id`;
- есть `EXPLAIN` с комментарием про Motion;
- есть storage choice и короткое объяснение Heap vs AO row vs AOCO;
- есть вопрос или гипотеза для Lesson 02.
