# Домашка: Lesson 04 — PySpark ETL Evidence Pack

Ориентир: **90–120 минут после зелёного `check`**. Установка Docker и pull image не входят в таймер.

## Кейс

На основе `events` и `customers` создай собственный mart:

```text
event_date × country × device
```

Показатели:

- orders;
- revenue;
- unique customers.

## Обязательные требования

1. PySpark DataFrame API; Scala не использовать.
2. Явные schemas; `inferSchema` запрещён для graded pipeline.
3. Invalid/null amount не должен попадать в revenue.
4. Использовать built-in functions, а не Python UDF.
5. Записать Parquet idempotently.
6. Объяснить output partitioning.
7. Приложить `explain("formatted")` и назвать `Exchange`.
8. Приложить Spark UI observations: jobs/stages/tasks/shuffle.
9. Проверить counts, revenue и persisted roundtrip.
10. Сформулировать production decision и residual risks.

## Что сдать

```text
lessons/lesson-04/submissions/
├── pipeline.py
└── evidence.md
```

Опционально:

```text
├── plan.txt
└── screenshots/
```

## Hard reject

- `.collect()` или `.toPandas()` на полном dataset;
- Python UDF при наличии built-in expression;
- отсутствует explicit schema;
- output не воспроизводим;
- нет physical plan;
- нет correctness checks;
- performance claim основан только на wall-clock одного запуска;
- изменён business grain без объяснения.

## Самопроверка

```bash
python3 mentor-lab.py up spark
python3 mentor-lab.py seed spark --profile lesson04
python3 mentor-lab.py check spark
python3 mentor-lab.py spark-submit spark lessons/lesson-04/submissions/pipeline.py
python3 mentor-lab.py homework spark check \
  --submission lessons/lesson-04/submissions
```

## Acceptance

Механический reviewer должен принять pack, затем ментор проверяет качество plan/UI reasoning по [rubric](rubric.md).
