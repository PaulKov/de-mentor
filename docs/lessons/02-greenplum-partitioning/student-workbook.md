# Lesson 02 Student Workbook: Partitioning, Statistics And Incremental Loads

## Перед Стартом

Проверь окружение и открой replay прошлого урока:

```bash
python3 mentor-lab.py readiness greenplum --platform macos
python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md
```

На Windows используй:

```powershell
py mentor-lab.py readiness greenplum --platform windows
```

## Упражнение 1: Partition Key Не Равен Distribution Key

Запусти:

```bash
python3 mentor-lab.py scenario greenplum show partition-pruning
python3 mentor-lab.py misconception greenplum diagnose --text "partition key это то же самое что distribution key"
```

Ответь письменно:

- какой predicate должен включать partition pruning;
- какой join pattern должен определять `DISTRIBUTED BY`;
- почему один ключ не обязан совпадать с другим.

Self-check:

- в ответе есть слова `partition pruning`;
- в ответе есть слова `distribution key`;
- в ответе есть пример фильтра по date/range;
- в ответе есть пример join key.

## Упражнение 2: Statistics After Load

Запусти диагностический шаблон:

```bash
python3 mentor-lab.py diagnostics greenplum show table-statistics
python3 mentor-lab.py scenario greenplum show stale-statistics
```

Ответь:

- что изменится после `ANALYZE`;
- какие estimates нужно сравнить до и после;
- почему stale statistics могут привести к плохому Broadcast Motion или Redistribute Motion.

Self-check:

- есть before/after `EXPLAIN`;
- есть упоминание `ANALYZE`;
- есть вывод про plan quality, а не только про скорость.

## Упражнение 3: Incremental Loads

Спроектируй daily load для fact table:

- grain таблицы;
- partition strategy;
- distribution strategy;
- late-arriving facts;
- statistics policy;
- validation before/after.

Мини-шаблон:

```text
Fact grain:
Partition strategy:
Distribution strategy:
Incremental window:
Late-arriving facts:
Statistics after load:
Validation:
Residual risk:
```

## Что Сдать

Файл `submissions/lesson02-partitioning.md`:

- DDL sketch;
- `EXPLAIN` или ожидаемый plan shape;
- catalog checks для partitions;
- statistics policy после incremental loads;
- validation и residual risk.

## Что Принести На Следующий Урок

- один вопрос по partition pruning;
- один вопрос по statistics;
- один production-риск по incremental loads.
