# План домашки Lesson 04

## Prep — вне таймера

```bash
python3 mentor-lab.py up spark
python3 mentor-lab.py seed spark --profile lesson04
python3 mentor-lab.py check spark
```

## 00–20 — Input contract и baseline

- описать schemas;
- зафиксировать input counts;
- вывести partitions;
- получить исходный `explain("formatted")`.

## 20–55 — Pipeline

- quality filters;
- derived `event_date`;
- customer join;
- aggregation по `event_date, country, device`;
- idempotent Parquet output.

## 55–80 — Execution evidence

- physical plan;
- `Exchange` и причина;
- Spark UI job/stages/tasks;
- shuffle read/write;
- возможный broadcast decision.

## 80–105 — Correctness

- counts before/after;
- null/invalid rows;
- total revenue;
- persisted roundtrip;
- business grain.

## 105–120 — Production decision

- что внедряем;
- что не оптимизируем без данных;
- residual risks;
- monitoring/rollback note.

## Self-check

```bash
python3 mentor-lab.py homework spark check \
  --submission lessons/lesson-04/submissions
```
