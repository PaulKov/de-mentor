# Lesson 02: Partitioning, statistics and incremental loads in MPP

Второй урок продолжает Greenplum Academy после базового урока про MPP, `DISTRIBUTED BY`, `Motion`, `gp_segment_id`, Heap/AO/AOCO и первый `EXPLAIN`.

Главная идея: partitioning не заменяет distribution. Partitioning помогает `partition pruning`, retention и управляемости больших фактов. Distribution отвечает за размещение строк по segments, locality join и баланс параллельной работы.

## Результат Урока

После урока ученик должен уметь:

- выбрать partition key под реальные фильтры, retention и SLA загрузки;
- объяснить, почему partition key и distribution key решают разные задачи;
- проверить partitions через `pg_partition_tree` и `gp_toolkit.gp_partitions`;
- показать `EXPLAIN`, где виден эффект `partition pruning`;
- включить AOCO для append-heavy fact и понимать ограничения maintenance;
- описать incremental load: stage, publish, late-arriving facts, idempotency, `ANALYZE`, validation;
- принести evidence, а не только “правильный DDL”.

## Маршруты

| Маршрут | Когда Использовать | Команда |
| --- | --- | --- |
| Упрощенный 60 минут | основной урок после Lesson 01 | `python3 mentor-lab.py runbook greenplum-partitioning simple` |
| Deep-dive 90-120 минут | сильный ученик или отдельная appendix-сессия | `python3 mentor-lab.py runbook greenplum-partitioning deep` |
| Домашка 60-90 минут | самостоятельная работа ученика | `python3 mentor-lab.py runbook greenplum-partitioning homework` |

Физический стенд остается тем же:

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py psql greenplum
```

Учебный маршрут отдельный:

```bash
python3 mentor-lab.py academy greenplum-partitioning start --student Иван --dry-run
python3 mentor-lab.py student greenplum-partitioning bootstrap --platform macos
python3 mentor-lab.py student greenplum-partitioning homework
```

## Практический SQL-Lab

Основной runnable-файл:

[lesson02-partitioning-statistics-loads.sql](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql)

Что он создает:

- schema `lesson02`;
- bad table `lesson02.fact_sales_bad_partition_key`, где `PARTITION BY RANGE (loaded_at)` не помогает типичному фильтру по `sale_date`;
- good table `lesson02.fact_sales_partitioned` с `PARTITION BY RANGE (sale_date)`;
- AOCO storage через `WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)`;
- stage table `lesson02.fact_sales_stage`;
- late-arriving facts;
- `ANALYZE` после load;
- проверки через `gp_segment_id`, `tableoid`, `pg_partition_tree`, `gp_toolkit.gp_partitions`;
- `EXPLAIN` для сравнения pruning.

Запуск в psql:

```sql
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
```

Безопасный smoke-check:

```sql
BEGIN;
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
ROLLBACK;
```

## Материалы

- [План ментора](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/mentor-guide.md)
- [Workbook ученика](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/student-workbook.md)
- [Домашка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md)
- [Матрица оценки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/rubric.md)
- [Шпаргалка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/cheat-sheet.md)
- [Упрощенный маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/simple-path.md)
- [Deep-dive маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/deep-dive-path.md)
- [План домашки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/homework-plan.md)

## Следующий Урок

Lesson 03: Query tuning, workload management and production diagnostics.

Фокус: читать production-планы глубже, связывать `Motion`, joins, statistics, skew и workload management с конкретным RCA.
