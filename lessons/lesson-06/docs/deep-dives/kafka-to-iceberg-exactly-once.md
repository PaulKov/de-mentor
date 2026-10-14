# Deep Dive: Exactly-once от Kafka до Iceberg snapshot

Фраза exactly-once относится к чётко ограниченному наблюдаемому результату. В этом pipeline нужно отдельно назвать: (1) Kafka source offset восстановление, (2) Flink state checkpoint, (3) Iceberg sink commit, (4) бизнес-уникальность строк. Только когда все четыре границы согласованы, читатель table видит результат, эквивалентный failure-free запуску.

## 1. Полная транзакционная линия

```text
Kafka partition p, offset o
   │ KafkaSourceReader читает запись и хранит split position
   ▼
Flink operators: parse → watermark/window → keyed state
   │ Iceberg writer создаёт data/delete files и pending committable
   ▼
Checkpoint barrier n обходит graph; offsets + state + committable snapshot-ятся
   │ all required subtasks ACK → CheckpointCoordinator завершает n
   ▼
Iceberg sink получает notifyCheckpointComplete(n)
   │ committer объединяет файлы, создаёт manifests + metadata v+1
   ▼
Catalog conditionally swaps current pointer v → v+1
   ▼
Новый Iceberg snapshot виден читателям
```

Идея двухфазная на уровне sink: task writers заранее пишут неизменяемые объекты, а commit делается только по успешному completed checkpoint. До публикации current metadata эти объекты не являются частью snapshot. После сбоя Flink восстанавливает committed checkpoint и connector защищается от повторной публикации тех же checkpoint-данных по своей metadata/snapshot summary логике. Официальная Iceberg Flink документация описывает exactly-once sink и commit в `notifyCheckpointComplete`; всё равно нужно мониторить отдельный успех Iceberg commit — checkpoint может пройти, а commit нет. [Iceberg Flink writes](https://iceberg.apache.org/docs/latest/flink-writes/) · [Flink exactly-once scope](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/learn-flink/fault_tolerance/).

## 2. Почему commit после checkpoint важен

Пусть source offset `o=100` обработан, агрегат state содержит сумму 15, а writer успел записать parquet file F:

| Момент отказа | Что известно после рестарта | Почему нет пропуска |
|---|---|---|
| до checkpoint N | Flink восстановит предыдущий checkpoint, повторно прочитает offset 100; незавершённая F не опубликована | replay + file не виден в snapshot |
| во время snapshot N, но N не completed | восстановление идёт с последнего completed checkpoint; offset 100 будет replay | неуспешный барьер не двигает recovery frontier |
| N completed, commit callback ещё не успел | checkpoint содержит позиции/state/committables; sink может повторить commit из восстановленного состояния | writer идемпотентно распознаёт уже обработанный checkpoint или корректно повторяет |
| catalog CAS вернул конфликт | Flink не делает вид, что table commit успешен; retry/rebase или fail job | другой writer не потерян, победивший pointer остаётся текущим |
| metadata pointer опубликован, ответ клиенту потерян | retry может не знать, прошёл ли commit | recovery/retry должен распознать checkpoint/snapshot summary; проверяем Iceberg commits и connector logs |
| checkpoint успешен, REST/S3 недоступны при публикации | source/state checkpoint может быть зелёным, snapshot commit отсутствует | сигнализирует sink commit metric/alert; нужен retry/failure policy |

Эта таблица объясняет, почему «Flink checkpoint completed» и «Iceberg таблица обновлена» — разные факты. Периодически проверяйте snapshot summary и метрику `elapsedSecondsSinceLastSuccessfulCommit`.

## 3. Неодинаковое exactly-once у Kafka sink, Iceberg sink и Kafka transaction

Kafka-to-Kafka Flink sink может писать Kafka transaction и commit transaction вместе с checkpoint; consumer должен читать с `isolation.level=read_committed`, а `transaction.timeout.ms` должен покрывать максимальный checkpoint + restart interval. Iceberg не использует Kafka transaction: его commit — metadata transaction каталога и table snapshot. Транзакции двух систем не образуют атомарную distributed transaction автоматически. Если один pipeline пишет и Kafka, и Iceberg sinks, Flink checkpoints координируют application state, но отдельные external commit protocols могут иметь собственные visibility windows.

Идемпотентный sink — альтернативная end-to-end стратегия: ключ/версия записи позволяет повторный эффект свернуть. Append parquet без checkpoint coordination не становится idempotent только потому, что файл имеет уникальное имя.

Сравните:

| Подход | Механизм видимости | Типовая цена/риск |
|---|---|---|
| Kafka EOS sink | producer transaction commit после checkpoint; read-committed consumers | transaction timeout, consumer isolation, fencing, задержка видимости |
| Iceberg Flink sink | files + commit по checkpoint completion, atomically published table metadata | commit/manifest/catalog latency, маленькие файлы, maintenance/retention |
| JDBC upsert sink | transaction/PK upsert или idempotency key | DB bottleneck, transaction size, schema/collision handling |
| обычный HTTP side effect | приложение должно само сделать idempotency key/outbox | без контракта возможны дубли/потери |

### Исторический контекст и границы альтернатив

Kafka transactions (начиная с Kafka 0.11) дали обработке Kafka → Kafka возможность атомарно связать прочитанные offsets, changelog/state и output records. Именно узкая Kafka boundary делает Kafka Streams EOS естественным: после commit транзакции consumer с `read_committed` видит связанный результат целиком. Flink checkpoint шире одного broker: coordinator снимает согласованный state dataflow, а source и каждый внешний sink подключают собственный протокол. Поэтому Flink может согласовать Kafka offsets + operator state + Iceberg committables, но S3 object PUT и Lakekeeper metadata CAS не становятся участниками общей Kafka transaction.

Spark Structured Streaming строит recovery вокруг query checkpoint и commit-log конкретной query/sink; детали output mode, trigger и sink connector определяют поведение при retry. Для Iceberg оценивайте реальную связку `Spark version × Iceberg runtime × catalog`, а не выводите гарантию из имени Spark. Beam описывает модель обработки и delivery semantics поверх runner; capabilities реализации sink/runner тоже часть контракта. Альтернативы полезны, когда их transaction boundary совпадает с доменом: Kafka Streams для Kafka-only processing, Flink для многосистемного stateful pipeline с координацией checkpoints, Spark для аналитического streaming, тесно связанного с Spark SQL/lakehouse batch.

Для всех вариантов отдельно задайте четыре observable properties: **replay position**, **state recovery point**, **sink visibility/commit point**, **business deduplication key**. Таблица «exactly once: да/нет» скрывает эти границы. [Kafka Streams processing guarantees](https://kafka.apache.org/documentation/streams/core-concepts/#processing-guarantees) · [Spark Structured Streaming recovery semantics](https://spark.apache.org/docs/latest/streaming/index.html#recovering-from-failures-with-checkpointing) · [Beam execution model](https://beam.apache.org/documentation/runtime/model/).

## 4. SQL путь в стенде

В [source DDL](../../../../labs/flink-iceberg/sql/04-kafka-source.sql) JSON разбирается в event time, а [sink pipeline](../../../../labs/flink-iceberg/sql/05-stream-to-iceberg.sql) задаёт `EXACTLY_ONCE`, checkpoint interval и Iceberg v2 upsert таблицу. Точка для исследования:

```sql
SET 'execution.checkpointing.interval' = '15 s';
SET 'execution.checkpointing.mode' = 'EXACTLY_ONCE';

USE CATALOG lakekeeper;
CREATE DATABASE IF NOT EXISTS lesson06;

CREATE TABLE lakekeeper.lesson06.region_minute_metrics (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  region STRING,
  order_count BIGINT,
  gross_amount DECIMAL(20, 2),
  PRIMARY KEY (window_start, window_end, region) NOT ENFORCED
) PARTITIONED BY (region) WITH (
  'format-version' = '2',
  'write.upsert.enabled' = 'true'
);

INSERT INTO lakekeeper.lesson06.region_minute_metrics
SELECT window_start, window_end, region, COUNT(*), SUM(amount)
FROM TABLE(TUMBLE(TABLE default_catalog.default_database.orders_source,
  DESCRIPTOR(event_time), INTERVAL '1' MINUTE))
GROUP BY window_start, window_end, region;
```

`PRIMARY KEY ... NOT ENFORCED` — planner/write contract, а не проверка уникальности источника на Kafka. Если window result emits updates, PK и Iceberg upsert/delete semantics должны соответствовать реальной таблице. Это соответствует [runnable source](../../../../labs/flink-iceberg/sql/04-kafka-source.sql) и [sink](../../../../labs/flink-iceberg/sql/05-stream-to-iceberg.sql); сверьте SQL syntax с закреплённой версией Flink/Iceberg при изменении образов.

## 5. Java DataStream вариант

Фрагмент показывает основные публичные API границы: source offsets/checkpointing, event-time, обработка, Iceberg writer. Он предполагает уже созданную Iceberg v2 table и `TableLoader`, configured на тот же Lakekeeper REST catalog и warehouse:

```java
KafkaSource<Order> source = KafkaSource.<Order>builder()
    .setBootstrapServers("kafka:29092")
    .setTopics("orders")
    .setGroupId("orders-iceberg-lab")
    .setStartingOffsets(OffsetsInitializer.earliest())
    .setValueOnlyDeserializer(new OrderJsonDeserializationSchema())
    .build();

WatermarkStrategy<Order> watermarks = WatermarkStrategy
    .<Order>forBoundedOutOfOrderness(Duration.ofSeconds(5))
    .withTimestampAssigner((event, kafkaTs) -> event.eventTimeMillis())
    .withIdleness(Duration.ofSeconds(30));

env.enableCheckpointing(15_000, CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setCheckpointStorage("s3://lab/checkpoints");

DataStream<RowData> normalized = env.fromSource(source, watermarks, "orders")
    .keyBy(Order::region)
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .aggregate(new OrderWindowAggregate())
    .map(new ToIcebergRowData());

FlinkSink.forRowData(normalized)
    .tableLoader(tableLoader)     // Iceberg REST catalog + Iceberg table
    .upsert(true)                 // target v2 table must have a compatible key
    .append();

env.execute("orders-kafka-to-iceberg");
```

`tableLoader` и schema conversion нельзя оставлять неявными в рабочем проекте: закрепите Iceberg runtime JAR той же версии, что и Flink integration; назначайте operator UIDs, если state должен пережить code rollout; параметризуйте offsets, bucket/warehouse, credentials; обеспечьте реальную durable checkpoint location. Для примера по API сверяйтесь с [Iceberg DataStream writes](https://iceberg.apache.org/docs/latest/flink-writes/#writing-with-datastream-api) и [KafkaSource](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/datastream/kafka/#kafka-source).

## 6. PyFlink: Python управляет графом, JAR выполняет коннекторы

PyFlink может объявить ту же Table API pipeline через `StreamTableEnvironment`; Iceberg и Kafka connectors должны быть в JVM classpath TaskManager/JobManager. Этот небольшой пример ориентирован на job submission из окружения, где `flink-sql-connector-kafka` и `iceberg-flink-runtime` уже добавлены как JARs:

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
env.enable_checkpointing(15_000)
env.get_checkpoint_config().set_checkpoint_storage("s3://lab/checkpoints")
t_env = StreamTableEnvironment.create(env)

t_env.execute_sql("""
CREATE CATALOG lakekeeper WITH (
  'type' = 'iceberg',
  'catalog-type' = 'rest',
  'uri' = 'http://lakekeeper:8181/catalog',
  'warehouse' = 'flink-demo',
  'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO'
)
""")
t_env.execute_sql("USE CATALOG default_catalog")
# The Kafka source table has the exact schema/properties from 04-kafka-source.sql.
t_env.execute_sql("""
CREATE TABLE IF NOT EXISTS default_catalog.default_database.orders_source (
  order_id STRING, region STRING, amount DECIMAL(12, 2), event_time TIMESTAMP(3),
  WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka', 'topic' = 'orders',
  'properties.bootstrap.servers' = 'kafka:29092',
  'properties.group.id' = 'lesson06-pyflink',
  'scan.startup.mode' = 'earliest-offset', 'format' = 'json',
  'json.timestamp-format.standard' = 'ISO-8601'
)
""")
t_env.execute_sql("USE CATALOG lakekeeper")
t_env.execute_sql("CREATE DATABASE IF NOT EXISTS lesson06")
t_env.execute_sql("""
CREATE TABLE IF NOT EXISTS lesson06.region_minute_metrics (
  window_start TIMESTAMP(3), window_end TIMESTAMP(3), region STRING,
  order_count BIGINT, gross_amount DECIMAL(20, 2),
  PRIMARY KEY (window_start, window_end, region) NOT ENFORCED
) PARTITIONED BY (region) WITH (
  'format-version' = '2', 'write.upsert.enabled' = 'true',
  'write.format.default' = 'parquet', 'write.distribution-mode' = 'hash'
)
""")
result = t_env.execute_sql("""
INSERT INTO lesson06.region_minute_metrics
SELECT window_start, window_end, region, COUNT(*), SUM(amount)
FROM TABLE(TUMBLE(TABLE default_catalog.default_database.orders_source,
  DESCRIPTOR(event_time), INTERVAL '1' MINUTE))
GROUP BY window_start, window_end, region
""")
result.wait()  # blocks until job result/termination in this submission style
```

The ellipses are intentional: choose catalog auth/endpoint and the exact table schema from this lab's SQL files rather than copying credentials into a notebook. A long-running streaming job submission generally returns a `TableResult`/job handle while the cluster executes the job; `wait()` behavior is client/API mode dependent. PyFlink calls JVM planner/connectors; only a Python UDF crosses a separate Python worker boundary. [PyFlink Table/SQL and DataStream integration](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/dev/table/data_stream_api/) · [Dependency management](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/dev/python/dependency_management/).

## 7. Retention, compaction и sink recovery are one design

Iceberg Flink sink uses committed checkpoint identity in snapshot summaries and may keep temporary/uncommitted data files. Expiring the most recent Flink-associated snapshot or cleaning recent orphan files can break restart/recovery. Compaction rewrites data files and publishes a new snapshot; it is not equivalent to cleanup. Snapshot expiration prunes table history according to retention; orphan cleanup deletes unreferenced objects older than a threshold. These maintenance operations must coordinate with maximum checkpoint/restart/commit duration and active jobs. [Iceberg Flink writes: maintenance notes and metrics](https://iceberg.apache.org/docs/latest/flink-writes/) · [Iceberg maintenance operations](https://iceberg.apache.org/docs/latest/maintenance/).

Production retention parameters should be derived from: checkpoint interval + timeout, max recovery time, restart backoff, commit retry envelope, concurrent writer duration, required time travel retention, object-store lifecycle and audit requirements. “Delete unreferenced objects after 1 hour” is not safe if an active writer can spend 2 hours on a checkpoint/commit.

## 8. Exactly-once evidence checklist

1. Source partition offsets in completed Flink checkpoint line up with source lag and replay test.
2. Failed checkpoint is not selected on restore; job restores a completed checkpoint ID.
3. Iceberg snapshot summary has the expected Flink job/checkpoint identity and rows.
4. Replaying identical input after a forced TaskManager failure does not add duplicate logical output.
5. Catalog logs show commit conflict/retry outcomes; no commit errors silently swallowed.
6. `elapsedSecondsSinceLastSuccessfulCommit` alerts independently of checkpoint success.
7. Maintenance retention keeps the snapshot/files required by a recent job checkpoint.
8. Business key uniqueness is checked separately from connector exactly-once semantics.

### Senior design questions

- If a Kafka record is processed twice after recovery, why might Iceberg still present one logical committed effect?
- If source/checkpoint is healthy but Iceberg commits stop, which exact metric and alerts reveal the split failure?
- If the same app writes Kafka and Iceberg, can consumers observe both outputs atomically? Why?
- What changes when input is replayed with a new job submission rather than restored from its savepoint?
- Which retention time must be longer: Kafka replay horizon, checkpoint retention, Iceberg snapshot retention, or business time-travel window? Answer with the recovery contract, not one universal ordering.
