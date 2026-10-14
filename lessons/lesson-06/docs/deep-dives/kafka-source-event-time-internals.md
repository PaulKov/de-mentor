# Deep Dive: Kafka source, offsets, shuffle, event time и watermarks

В этом уроке одна строка заказа проходит четыре независимых временных/позиционных модели: Kafka partition offset, Flink checkpoint position, record event timestamp и watermark progress. Ошибки часто возникают, когда эти координаты называют общим словом «offset» или считают, что watermark равен текущему времени.

## 1. Kafka задаёт журнал и локальный порядок

Kafka сохраняет записи в partitions. Внутри partition offsets упорядочены и монотонны; между partition глобального порядка нет. Key влияет на routing/partitioning producer-а, но Flink не гарантирует, что downstream `keyBy` совпадает с Kafka partition assignment. Kafka retention ограничивает окно replay: если Flink отстал дальше срока retention, checkpoint хранит желаемые offsets, но брокер уже удалил соответствующие записи.

```text
orders-0: o100 → o101 → o102 → o103
orders-1: o220 → o221 → o222
          ^ local order only; no total order between partitions
```

Для потребления современный `KafkaSource` использует Source API (enumerator + readers): coordinator обнаруживает topic partitions и раздаёт splits, SourceReader читает назначенные partitions. При rebalance/re-discovery split state участвует в checkpoint. Если partitions меньше source parallelism, часть readers простаивает; если partitions больше, reader может читать несколько partitions. [Flink Kafka connector 2.2](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/datastream/kafka/).

## 2. Kafka consumer group offsets не являются truth для Flink recovery

В `KafkaSource` выбранный `OffsetsInitializer` задаёт начальный offset при первой активации. Далее точка восстановления находится в Flink checkpoint state. Когда checkpoint завершается, connector может записать offsets в Kafka broker, чтобы мониторинг consumer group показывал прогресс. Эти broker commits **не** являются источником fault tolerance Flink: документ Flink 2.2 явно указывает, что Flink восстанавливается из checkpointed partition offsets. Без checkpoint semantics другие и зависят от auto-commit и свойств consumer.

```java
KafkaSource<String> source = KafkaSource.<String>builder()
    .setBootstrapServers("kafka:29092")
    .setTopics("orders")
    .setGroupId("de-mentor-orders")
    .setStartingOffsets(OffsetsInitializer.earliest())
    .setValueOnlyDeserializer(new SimpleStringSchema())
    .build();

DataStream<String> raw = env.fromSource(
    source,
    WatermarkStrategy.noWatermarks(),
    "orders-kafka-source");
```

`earliest` — хорошая учебная настройка для повторяемого сценария, но опасный implicit production choice: новая group может переиграть всю retention history. В реальном runbook задайте initial offset policy, savepoint/restore policy, retention, backfill cutoff и unique group identity. [Kafka starting offsets + broker commits](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/datastream/kafka/#starting-offset) · [Offset committing](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/datastream/kafka/#consumer-offset-committing).

## 3. От source split к keyed state

Partitioning Kafka и распределение Flink — два разных shuffle:

```text
Kafka topic partitions (source splits)
     ↓ SourceReaders: offsets + deserialization
DataStream records (source subtasks)
     ↓ keyBy(region): hash partitioning over Flink network channels
Keyed operators: keyed state lives with the owning key-groups
     ↓ sink parallelism / Iceberg file writers
Committed table snapshot
```

Key, использованный для Kafka routing, может обеспечить локальность до source, но `keyBy` внутри Flink создаёт собственное hash partitioning. После shuffle записи одного ключа приходят на один downstream keyed subtask, что позволяет локально держать `ValueState`/window state. Hot key остаётся serial bottleneck: простое увеличение parallelism не разделит один логический ключ. Решение может включать salting + второй aggregate, отдельный путь для heavy-hitter или approximate aggregation — каждый меняет семантику/точность.

## 4. Event time — время события, а не время обработки

**Processing time** — часы машины, на которой сейчас работает task. **Event time** — timestamp из события/источника. Если producer задержал запись на 20 минут, processing time уже поздний, но бизнес-время события прежнее. Event-time windows воспроизводимы при replay, если timestamps/входные данные детерминированы; processing-time windows привязаны к wall-clock и при replay могут дать иной временной раскрой.

Watermark `W` — утверждение runtime: «для данного потока мы больше не ожидаем обычных событий с timestamp ≤ W». Это не глобальный доказанный максимум и не таймер wall clock. Для bounded out-of-orderness `B` генератор хранит наблюдаемый максимум `M` и периодически выпускает примерно `M - B - 1ms`. Логика приложения выбирает компромисс: больше B допускает более поздние события, но увеличивает задержку окон и объём state.

```java
WatermarkStrategy<Order> strategy = WatermarkStrategy
    .<Order>forBoundedOutOfOrderness(Duration.ofSeconds(5))
    .withTimestampAssigner((order, kafkaRecordTimestamp) -> order.eventTimeMillis())
    .withIdleness(Duration.ofSeconds(30));

DataStream<Order> orders = env.fromSource(
    source, strategy, "orders-with-event-time");
```

Здесь мы предпочитаем бизнес timestamp `eventTimeMillis()` из payload Kafka timestamp. Если payload timestamp отсутствует/повреждён, нужно явно решить: reject/quarantine, fallback timestamp и quality metric. Нельзя бездумно заменить отсутствующий event time на `System.currentTimeMillis()` — это маскирует ошибку контракта данных и меняет оконную семантику.

## 5. Min-watermark, idle partitions и эффект медленного источника

При union/нескольких входах downstream watermark обычно ограничивается самым медленным активным каналом/входом: иначе можно закрыть окно, пока по другому каналу ещё идёт своевременное событие. Из этого следует неприятная операционная ситуация: одна Kafka partition молчит или сильно отстаёт — окна по всем регионам задерживаются, хотя остальные partitions обработаны.

`withIdleness(timeout)` объявляет источник idle после отсутствия записей за период и исключает его watermark из минимума. Но после возврата idle partition поздние для уже сработавших окон records могут попасть в late side output/быть отброшены согласно политике. Настройка idle timeout — решение о бизнес-корректности, а не только удобный tuning. В KafkaSource параллелизм выше числа partitions не автоматически помечает лишние readers idle; configure idleness or size parallelism intentionally. [Kafka per-partition watermarks and idleness](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/datastream/kafka/#idleness).

В Table/SQL API аналогичная сессийная настройка — `SET 'table.exec.source.idle-timeout' = '5 s'`. В нашей лаборатории topic имеет одну partition, а source parallelism равен двум, поэтому один reader закономерно не получает partition. Без idle timeout его `MIN` watermark блокирует event-time timers downstream, даже когда reader с partition уже прочёл все сообщения. Проверьте оба значения метрики `currentOutputWatermark` на source subtasks, затем включите idle timeout и сравните, когда закроются окна.

## 6. Late events, allowed lateness и state cleanup

Window trigger fires when watermark passes window end. Allowed lateness держит state некоторое дополнительное event-time время и может выпускать updates; слишком поздние элементы могут быть отброшены или отправлены в side output. Для оконного агрегата и Iceberg append-only sink важно определить, записываем ли мы:

- insert-only финальные результаты после watermark;
- changelog (insert/update-before/update-after) для предварительных результатов;
- переписываем/upsert-им один ключ окна, требуя корректную PK semantics и Iceberg v2 table.

Вторая и третья стратегии влияют на sink file/delete behavior и replay. Iceberg append может содержать версии одной window result как отдельные строки; тогда consumer должен понимать snapshot/change feed semantics или pipeline должен выпускать только окончательные results. Нельзя назвать output «exactly-once», если application сама создала дублирующие business rows.

SQL в лаборатории использует:

```sql
WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
```

Вычитание пяти секунд — ожидание bounded lateness estimate для источника, не гарантия, что Kafka всегда укладывается в 5 секунд. Попробуйте изменить последнюю запись в `data/orders.jsonl`, сравнить водяную линию, результат TUMBLE и позднюю запись. См. [Flink watermark generators](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/dev/datastream/event-time/generating_watermarks/) и [event-time concepts](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/dev/datastream/event-time/).

## 7. DataStream, Table/SQL и PyFlink: один runtime, разные frontends

- **Java DataStream** — явно описываем `KafkaSource`, serializers, `WatermarkStrategy`, `keyBy`, stateful functions, sink. Лучше контроль типов, таймеров и lifecycle.
- **Table API / SQL** — connector DDL плюс декларативные watermark/window expressions. Planner переводит их в Flink operators, но фактический changelog mode и physical plan нужно проверять `EXPLAIN`/job plan.
- **PyFlink DataStream/Table** — похожие концепции и API из Python; operator UDF могут перейти в Python worker boundary. SQL/Java connectors остаются JAR dependencies в runtime. Декларативный SQL часто лучший интерфейс для Kafka→Iceberg, Python — для orchestration, parameterization и специальных UDF.

В лаборатории основной pipeline лежит в [SQL](../../../../labs/flink-iceberg/sql/04-kafka-source.sql) и [stream-to-Iceberg](../../../../labs/flink-iceberg/sql/05-stream-to-iceberg.sql); сравните его с Java source recipe выше и PyFlink TableEnvironment рецептом в Lesson 06 README.

## 8. Отладочная матрица

| Симптом | Сначала проверьте |
|---|---|
| Source lag растёт, watermark стоит | `pendingRecords`, `currentOffsets`, partitions, idle behavior, slow split |
| watermark быстро улетает вперёд | неверный payload timestamp, часы устройства, один future timestamp |
| event time lag велик, processing throughput нормальный | upstream задержка или watermark boundedness слишком строгий |
| окно не закрывается | отстающая активная partition/input, watermark assigner не получает timestamp, idle timeout |
| результат окна дублируется | changelog interpretation, sink mode/primary key, recovery/replay, job resubmission mode |
| после restart читает старый диапазон | restored checkpoint/savepoint или новая submission/offset initializer; проверьте checkpoint ID и job UID |

Для investigation сопоставляйте Kafka offsets по partition, Flink checkpoint ID, watermark, window state и Iceberg snapshot ID — только вся последовательность позволяет найти точную границу потери/повтора.

## 9. Event time в других моделях обработки

| Runtime | Кто продвигает время | Как выражается опоздание | Важный operational trade-off |
|---|---|---|---|
| Flink | watermark strategy на source/operator; downstream обычно берёт минимум входных watermarks | allowed lateness, side output, trigger и cleanup timers | один медленный активный input может удерживать event-time timers и state целого downstream operator |
| Kafka Streams | timestamp extractor + stream-time, оконная grace period | `grace` определяет, насколько поздние записи ещё могут обновить window | stream-time привязан к наблюдаемым timestamp внутри task; idle partitions и partition routing надо анализировать в рамках topology |
| Spark Structured Streaming | event-time column и watermark внутри query; engine отслеживает прогресс для state cleanup | `withWatermark` задаёт границу задержки для stateful query | output mode и trigger влияют на то, когда результат становится наблюдаемым; проверьте выбранный execution mode |
| Apache Beam | runner propagates watermarks по PCollection; окна сочетаются с triggers и allowed lateness | trigger определяет ранние/on-time/late panes, allowed lateness — срок принятия поздних данных | runner реализует модель, поэтому сравнивать нужно и API, и ограничения конкретной среды исполнения |

Flink-код задаёт границу явно у source:

```java
WatermarkStrategy<Order> strategy = WatermarkStrategy
    .<Order>forBoundedOutOfOrderness(Duration.ofSeconds(5))
    .withTimestampAssigner((order, kafkaTimestamp) -> order.eventTimeMillis())
    .withIdleness(Duration.ofSeconds(30));

DataStream<Order> orders = env.fromSource(source, strategy, "orders");
```

`5 s` — это бизнес-допуск на перестановку, а не задержка Kafka и не таймаут checkpoint. `withIdleness` исключает временно бездействующий split из минимума watermark; он не доказывает, что в нём больше никогда не придёт старое событие. Если `region` используется как key, это самостоятельный downstream shuffle: watermark и keyed state имеют разные partitioning rules. В оконной SQL-версии аналог задаётся `WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND`, но проверьте физический план, changelog и очистку state через `EXPLAIN` и runtime metrics.

Flink's `ProcessFunction`/window API даёт управление keyed timers и side outputs; Kafka Streams удобен, если source/state/output остаются внутри Kafka и достаточно stream-time/grace semantics; Spark Structured Streaming удобен при SQL-centric lakehouse workloads и batch unification; Beam полезен, когда runner portability важнее конкретного runtime API. Нельзя свести их к одной универсальной формуле «watermark = max timestamp − N»: прогресс может агрегироваться по разным inputs, split-ам и runner-ам. [Kafka Streams windows](https://kafka.apache.org/documentation/streams/developer-guide/dsl-api.html#windowing) · [Spark event-time and watermark](https://spark.apache.org/docs/latest/streaming/apis-on-dataframes-and-datasets.html#handling-event-time-and-late-data) · [Beam watermarks, triggers and late data](https://beam.apache.org/documentation/programming-guide/#watermarks-and-late-data).

### Дизайн-упражнение: выбрать watermark по SLO

Для потока заказов зафиксируйте три измерения: p99 `event_time → ingest_time`, максимальный разрыв между активными Kafka partitions и допустимую задержку витрины. Если выбрать bounded out-of-orderness равным `5 s`, но реальные часы клиента могут отставать на сутки, watermark сам по себе не решит проблему: нормализуйте timestamp или отправьте такие события в late-data path. Затем оцените state retention и объём поздних исправлений. На защите объясните, как изменятся latency, полнота и стоимость state при `N=5 s`, `N=2 min` и отдельной side output для записей старше SLA.
