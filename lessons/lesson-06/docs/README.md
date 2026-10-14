# Lesson 06 — цели и карта занятия

## Сквозная схема

```text
orders JSON
  → Kafka topic / partitions / offsets
  → Flink KafkaSource + event-time timestamps/watermarks
  → keyed/window state + network shuffle
  → checkpoint barrier n: source positions + operator state + sink committables
  → Iceberg writer files/manifests
  → Lakekeeper conditional metadata commit after completed checkpoint
  → Iceberg snapshot for SQL/Spark/Trino readers
```

## Цели обучения

К концу лабораторной ученик умеет:

1. Отличить Kafka partition offset, Flink checkpoint position, payload event time и processing time.
2. Объяснить SourceEnumerator/SourceReader, partition assignment, `keyBy` shuffle и state ownership.
3. Построить bounded-out-of-orderness watermark, объяснить idle partitions, late event и оконную политику.
4. Объяснить keyed/operator state, key-groups, checkpoint/savepoint и восстановление при другой parallelism.
5. Разобрать aligned/unaligned barrier snapshot и найти alignment/start-delay/async-duration в Flink UI.
6. Запустить Kafka→Flink SQL→Iceberg, проследить commit по checkpoint и увидеть snapshot/rows в Lakekeeper.
7. Сопоставить Java DataStream API, Table/SQL и PyFlink, понимая что connectors работают через JVM JARs.
8. Разделить exactly-once state semantics, transactional sink guarantee и бизнес-дедупликацию.
9. Спроектировать alerting по source lag, watermark lag, failed checkpoints и Iceberg commit delay.
10. Обсудить эксплуатационные последствия small files, compaction, snapshot retention, checkpoint retention и Kafka retention.

## Расписание на 4 часа

| Время | Блок | Evidence |
| ---: | --- | --- |
| 0–20 мин | Flink stream-first model и историческое сравнение с Spark micro-batch | схема runtime и отличие trigger/continuous execution |
| 20–55 мин | Kafka partitions, Source API, offsets и replay | offset table до/после checkpoint |
| 55–85 мин | Event time, watermark, idle inputs, late events | вывод окон и поведение out-of-order строки |
| 85–110 мин | Поднять стенд, создать topic и таблицу | Compose health + job graph |
| 110–155 мин | Lab A: Kafka→Flink→Iceberg SQL | Iceberg rows + snapshot IDs + checkpoint IDs |
| 155–190 мин | Internals: checkpoint barriers и sink commit lifecycle | sequence diagram + UI checkpoint metrics |
| 190–220 мин | Fault drill: остановить TaskManager / сбой catalog | restore checkpoint и анализ visible snapshot |
| 220–235 мин | Java API / PyFlink comparison | короткий pipeline design на двух API |
| 235–240 мин | Debrief и homework | production checklist |

## Deep dives

- [Runtime, state backend и checkpoints](deep-dives/flink-runtime-and-checkpoint-internals.md)
- [Kafka Source, offsets, event time и watermarks](deep-dives/kafka-source-event-time-internals.md)
- [Exactly-once от Kafka до Iceberg](deep-dives/kafka-to-iceberg-exactly-once.md)

Deep dive читать по цепочке **идея → исторический контекст → публичный API → внутренний путь → код → failure modes → сравнение альтернатив → evidence**. В примерах versions согласованы со стендом: Flink 2.2.1, Iceberg 1.12.0, Kafka connector 5.0.0-2.2.

## Вопросы Senior-level

- Что гарантирует completed checkpoint, если S3 commit ещё не виден?
- Почему Kafka consumer group offset не является checkpoint source of truth?
- Какой watermark держит окна при нескольких Kafka partitions и что произойдёт при idle timeout?
- Каким образом unaligned checkpoint влияет на bytes written и restore time?
- Почему append-only Iceberg таблица может иметь дублирующиеся логические window results, даже если sink exactly-once?
- Что надо удерживать дольше: Kafka records, Flink snapshots или Iceberg snapshots? Выведите из требуемого recovery/time-travel SLA.

## Официальная документация

- [Flink 2.2 fault tolerance](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/learn-flink/fault_tolerance/)
- [Flink 2.2 Kafka connector](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/datastream/kafka/)
- [Stateful stream processing](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/concepts/stateful-stream-processing/)
- [Iceberg Flink writes](https://iceberg.apache.org/docs/latest/flink-writes/)
