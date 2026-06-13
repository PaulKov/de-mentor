# Lesson 02: Partitioning, Statistics And Incremental Loads In MPP

## Цель

Lesson 02 продолжает первый урок: ученик уже видел `DISTRIBUTED BY`, Motion, `gp_segment_id`, Heap/AO/AOCO и вводный `PARTITION BY RANGE`. Теперь задача - научиться проектировать partitioning под реальные фильтры, retention и incremental loads, а не считать partition key заменой distribution key.

## Что Ученик Должен Понять

- partitioning отвечает за pruning, retention и manageability;
- distribution отвечает за locality join, parallelism и баланс строк по segments;
- statistics после load влияют на plan quality не меньше DDL;
- incremental loads должны явно описывать late-arriving facts, idempotency и validation;
- AOCO partitions полезны для append-heavy fact, но требуют аккуратного maintenance.

## Каркас Урока

| Время | Блок | Практика |
|---:|---|---|
| 0-10 | Replay Lesson 01 | открыть replay pack и missing evidence |
| 10-25 | Partition pruning | сравнить good/bad partition key |
| 25-40 | Statistics after load | показать stale estimates и `ANALYZE` |
| 40-55 | Incremental load design | разобрать daily load, late facts и idempotency |
| 55-60 | Домашка | дать мини-проект с retention и validation |

## Команды Старта

```bash
python3 mentor-lab.py readiness greenplum --platform macos
python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md
python3 mentor-lab.py diagnostics greenplum show table-statistics
python3 mentor-lab.py scenario greenplum show partition-pruning
```

## Связь С Lesson 01

- Если ученик путает partition key и distribution key, начни с `python3 mentor-lab.py misconception greenplum diagnose --text "partition key это то же самое что distribution key"`.
- Если ученик не умеет доказывать планом, начни с `python3 mentor-lab.py coach-plan greenplum --query bad_customer_join --sample`.
- Если не хватает evidence, открой `artifacts/greenplum-replay.md` и выбери один missing marker.

## Материалы

- [Упрощенный маршрут Lesson 02](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/simple-path.md)
- [Workbook Lesson 02](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/student-workbook.md)
- [Partitioning strategies deep dive](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md)
- [Partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql)
