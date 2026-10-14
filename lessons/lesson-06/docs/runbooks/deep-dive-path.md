# Deep dive path — 3–4 часа

1. Выполнить [simple path](simple-path.md).
2. Пройти [Kafka source internals](../deep-dives/kafka-source-event-time-internals.md): split, offsets, `keyBy`, event time, per-partition watermarks и late events.
3. По [runtime deep dive](../deep-dives/flink-runtime-and-checkpoint-internals.md) проследить `StreamGraph → tasks → key-groups → barriers → checkpoint storage`.
4. Снять checkpoint subtask metrics; сформулировать hypothesis о start delay, alignment и async duration.
5. Составить sequence diagram [Kafka → Iceberg exactly-once](../deep-dives/kafka-to-iceberg-exactly-once.md).
6. Выполнить [recovery drill](recovery-drill.md), сравнить restore checkpoint, source offsets и table snapshots.
7. Сравнить DataStream Java, Table/SQL и PyFlink; отметить Java connector JAR boundary и Python UDF process boundary.
8. Рассчитать checkpoint interval, max recovery time, Kafka retention, Iceberg snapshot retention и orphan cleanup grace period для SLA кейса.
9. Пройти fault matrix: Kafka source unavailable, TaskManager killed, Lakekeeper unavailable before commit, SeaweedFS unavailable mid-write.
10. Подготовить design review, используя [homework assignment](../../homework/assignment.md).
