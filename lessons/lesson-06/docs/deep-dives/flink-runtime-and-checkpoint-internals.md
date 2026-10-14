# Deep Dive: Flink runtime, state и distributed checkpoints

Flink важен не только как API для `map` и SQL. Его главный инженерный контракт — исполнять распределённый поток как долгоживущий dataflow, сохранять пользовательское состояние и позицию во входе в одной согласованной точке. Эта точка позволяет повторить вход после сбоя, не теряя логический результат.

## 1. Идея и история модели

MapReduce восстанавливает работу на границах завершённых batch задач; streaming движку нужно поддерживать состояние между событиями при неограниченном входе. Flink развивался как stream-first runtime с состоянием и event-time, а batch трактовался как bounded dataflow. Это отличает базовую модель от Spark Structured Streaming micro-batch: в Flink операторы обычно работают непрерывно, а checkpoint — отдельный механизм консистентного состояния, не обязательная граница мини-батча. Flink Table/SQL дает relational frontend к streaming runtime. В текущей линейке DataStream API V1 — зрелый основной путь; DataStream API V2 развивается отдельно, поэтому сверяйте capabilities до выбора.

Научная формулировка snapshotting — лёгкие асинхронные snapshots распределённых dataflows, основанные на идеях Chandy–Lamport и адаптированные к потокам и состоянию Flink. [Stateful stream processing](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/concepts/stateful-stream-processing/) · [Оригинальная статья Lightweight Asynchronous Snapshots](https://arxiv.org/abs/1506.08603).

## 2. От Java/Python программы до выполняемого графа

```text
пользовательский код / SQL
   ↓ API transformations и Table planner
StreamGraph → JobGraph (chainable operators, exchanges, slot sharing)
   ↓ JobMaster / scheduler
ExecutionGraph (конкретные parallel subtasks)
   ↓ deploy tasks
TaskManager: Task → StreamTask → operator chain → network inputs/outputs
```

`keyBy` — логическое требование перераспределить записи по hash key; runtime строит network exchange. Параллельность source/operator/sink — число subtasks, а не число thread-ов в приложении. Операторы могут быть chained в одну task, если partitioning и chaining rules позволяют; shuffle, incompatible parallelism и explicit disable chaining образуют сетевые границы. Slot — ресурсное размещение одной или нескольких tasks, а не отдельный процесс. JobManager координирует выполнение и checkpoints; TaskManagers запускают subtasks, держат state backend и network buffers.

В Python API граф всё равно компилируется и исполняется в JVM runtime. Python operators вызываются через Python worker / serialization boundary; встроенные Table/SQL expressions остаются выражениями для JVM planner. Поэтому PyFlink — не отдельный Python-native runtime и не требует переписывать Iceberg Java connector на Python: Flink connector JAR добавляется к Java classpath, а Python код задаёт граф/SQL. [PyFlink dependency management](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/dev/python/dependency_management/).

## 3. Классы состояния и масштабирование

| Состояние | Логическое владение | Пример | Масштабирование |
|---|---|---|---|
| Keyed state | `keyBy` key | `ValueState` счётчика по account | делится по key-groups и перераспределяется между subtasks |
| Operator state | одна subtask | список Kafka partitions/offsets или split assignment | connector задаёт redistribution (split/list/union) |
| Broadcast state | копия у каждой subtask | правила/справочник | каждое обновление broadcast всем replicas |
| Timers | ключ + namespace/time domain | event-time window timer | сохраняются вместе с keyed state |
| In-flight channel state | сетевые каналы | записи между операторами | часть только unaligned checkpoint |

Keyed state физически partitioned по key-groups. `maxParallelism` задаёт число групп, а текущий parallelism — сколько subtasks ими владеют. При restore с другой параллельностью key-groups перемещаются между subtasks; это не произвольный migration API. Стабильные operator UIDs и совместимая state serializer/schema критичны для обновлений. Изменить имя/топологию stateful operator без сохранения его UID — иногда значит потерять возможность восстановиться из savepoint.

Backend и checkpoint storage — разные понятия. `HashMapStateBackend` хранит объекты в heap и удобно для небольшого состояния, но heap/GC ограничивает рост. `EmbeddedRocksDBStateBackend` использует локальную RocksDB с асинхронными/incremental snapshots; удобен для большого state, платой служат сериализация, локальный disk и tuning. Checkpoint storage содержит устойчивый snapshot (локальный shared volume в нашей лаборатории, HDFS/S3/object store в production). Современный ForSt backend/disaggregated state — отдельная evolving опция; не путайте его с default production choice. [Flink state backends](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/ops/state/state_backends/).

## 4. Барьеры: согласованная точка без остановки всего графа

Coordinator запускает checkpoint `n`, источники фиксируют позицию `Sₙ` и вводят barrier `n` в поток после этой позиции. Barrier движется в порядке данных, не обгоняя записи. Каждый оператор snapshot-ит своё состояние на границе между данными до и после barrier, а затем передаёт barrier дальше. Sink ACK и snapshot handles отправляются coordinator; когда нужные subtasks подтвердили checkpoint, он становится completed.

Для оператора с несколькими входами aligned checkpoint ждёт barrier `n` на всех входах. Получив barrier на первом канале, оператор временно не читает следующий буфер этого канала, пока медленный канал не догонит. Это не stop-the-world для всей job: ограничение локально к точке alignment. Но если downstream backpressure задерживает barrier, растёт alignment duration, очередь buffers и checkpoint latency.

```text
Input A: --r1--r2--|B_n|--r3---->
Input B: --r4--------------|B_n|-->
Operator: snapshot after r1,r2,r4; buffers r3 for next epoch; emit B_n
```

Unaligned checkpoint позволяет barrier обойти накопленные buffers, но записывает overtaken in-flight records как channel state. Он уменьшает ожидание alignment при медленном канале, однако увеличивает snapshot bytes и storage I/O. Если bottleneck — именно checkpoint/object-store I/O, unaligned может усугубить нагрузку. Flink 2.2 позволяет включить unaligned только при `EXACTLY_ONCE`; aligned timeout может переключить отдельный checkpoint, если включен соответствующий режим. [Checkpoint mechanics](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/concepts/stateful-stream-processing/) · [Monitoring alignment](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/ops/monitoring/checkpoint_monitoring/).

## 5. Что именно восстанавливает Flink

```text
completed checkpoint C17
  source Kafka: partition 0 offset 581; partition 1 offset 224
  aggregate keyed state: key-group handles
  event-time timers + watermark/operator state
  Iceberg sink: pending files/committables/checkpoint identity

failure → redeploy graph → restore C17 → Kafka resumes after captured offsets
       → input after C17 is replayed → state produces logical failure-free result
```

Checkpoint не означает «физически каждый event обработан один раз»: replay может заставить код обработать запись снова. Exactly-once означает, что управляемое состояние выглядит как обработанное ровно один раз; end-to-end требует replayable source и transactional либо idempotent sink. Внешний HTTP call из `map()` не становится exactly-once автоматически.

Checkpoint часто создаётся асинхронно: оператор делает короткую synchronous фазу, фиксирует snapshot view/handles, а тяжёлая запись состояния идёт asynchronously. Для RocksDB snapshots могут быть incremental. Completed checkpoint нужен для recovery; незавершённый checkpoint не должен становиться новой точкой старта. Checkpoint interval — компромисс между replay/recovery window, commit latency downstream, размером state, storage throughput и coordinator overhead.

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

env.enableCheckpointing(15_000, CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setCheckpointTimeout(120_000);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(5_000);
env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);
env.getCheckpointConfig().setCheckpointStorage("s3://company/flink/checkpoints");

// S3 requires the Flink filesystem plugin/credentials. This local demo instead
// uses file:///opt/flink/checkpoints on a Docker named volume.
```

Для failover strategy, restart policy, HA metadata и checkpoint storage отдельно проверьте окружение: sample Compose не создаёт высокодоступный Flink cluster.

## 6. Checkpoint versus savepoint

Checkpoint — автоматически управляемая recovery-log-like точка: Flink регулярно создаёт и удаляет её по lifecycle policy. Savepoint — операторский snapshot/backup point, который сохраняют для обновления, переноса/остановки job или эксперимента. Savepoint требует версионированного пути/управляемой retention policy и совместимости state serializers/operator UIDs. Сравнение «checkpoint быстрый, savepoint всегда полный» зависит от режима и конфигурации; верная мысль — разные lifecycle и operational intent. [Checkpoint vs savepoint](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/ops/state/checkpoints_vs_savepoints/).

## 7. Что смотреть в Web UI при диагностике

| Признак | Вероятная причина | Следующий замер |
|---|---|---|
| Start delay высокий | barrier долго идёт от source до subtask: backpressure/network queue/slow upstream | task backpressure, source lag, busy/backpressured time |
| Alignment duration высокий | несколько входов/shuffle; один канал медленнее | определить skew key, slow subtask, network throughput |
| Sync duration высокий | дорогой snapshot preparation, synchronous state access / operator pause | состояние operator, timers, state size, GC |
| Async duration высокий | checkpoint storage медленный, большие bytes, network/disk contention | bytes, upload throughput, incremental/full size |
| checkpoint timeout | checkpoint не укладывается в срок / contention | end-to-end timeline, timeout, concurrent checkpoint count |
| checkpoint success, no Iceberg snapshots | sink commit path/REST catalog/storage failure; checkpoint и table commit разные стадии | sink `elapsedSecondsSinceLastSuccessfulCommit`, task logs, catalog logs |

Операционную страницу checkpoints используйте как timeline по subtask, не как один общий зелёный статус. [Checkpoint monitoring](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/ops/monitoring/checkpoint_monitoring/).

## 8. Где читать код

- [CheckpointCoordinator](https://github.com/apache/flink/blob/master/flink-runtime/src/main/java/org/apache/flink/runtime/checkpoint/CheckpointCoordinator.java) — trigger, tracking/complete, ACK handling.
- [Flink stateful stream processing source](https://github.com/apache/flink/blob/master/docs/content/docs/concepts/stateful-stream-processing.md) — барьеры и recovery объяснены рядом с реализацией.
- В source tree ищите `CheckpointBarrierHandler`, `SingleCheckpointBarrierHandler`, `CheckpointedInputGate`, `StreamTask`, `StateBackend`, `KeyGroupRangeAssignment`.
- Смотрите исходники той версии, что запущена (`release-2.2`), а не только `master`; имена и классы меняются между версиями.

## 9. Альтернативные runtime и граница ответственности

| Система | Единица выполнения | Где живёт state/recovery | Когда выбирать |
|---|---|---|---|
| Flink | непрерывные operators/tasks и network exchanges | distributed checkpoints связывают operator state с replay position источника | stateful streaming, event-time/timers, длинные jobs и несколько независимых источников/приёмников |
| Spark Structured Streaming | logical query; обычно последовательность micro-batches, плюс ограниченный Real-Time Mode в новых версиях | query checkpoint и commit protocol конкретного source/sink; гарантия зависит от пары connectors и output mode | streaming поверх Spark SQL и существующего lakehouse/ETL стека, где batch unification важнее тонкого контроля каждого record |
| Kafka Streams | embedded topology внутри приложения; tasks назначаются по Kafka partitions | локальные state stores восстанавливаются из changelog topics; EOS тесно связывает Kafka input offsets, state changelog и Kafka output transactions | сервис, где Kafka — основной транспорт и все атомарные результаты остаются в Kafka |
| Apache Beam | portability model: pipeline запускается выбранным runner-ом | checkpoint/state/watermark semantics задаются моделью Beam и реализуются runner-ом | один pipeline API на нескольких поддерживаемых execution backends или переносимость между managed runners |

Сравнение — не рейтинг throughput: это сравнение ownership и границ транзакции. Kafka Streams может атомарно коммитить input offsets, state store changelog и output topic в Kafka transaction; Iceberg REST catalog и объектное хранилище находятся вне этой транзакции. Flink, напротив, даёт runtime-level consistent checkpoint, но внешний sink обязан участвовать в recovery/commit протоколе. Spark Structured Streaming использует micro-batch по умолчанию и в актуальных версиях документирует дополнительный Real-Time Mode для поддерживаемого подмножества запросов; поэтому старое упрощение «Spark всегда micro-batch» уже не универсально. Beam отделяет API от runner: реальная latency, ограничения и state implementation требуют смотреть документацию конкретного runner.

Исторически Flink вырос из проекта Stratosphere: batch-модель была обобщена как bounded dataflow, а непрерывные потоки получили state, event time и checkpointing как базовые механизмы. Это объясняет, почему batch и streaming сходятся в одном runtime, а recovery строится через graph-wide snapshot вместо восстановления только целых микробатчей. [Flink concepts](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/concepts/overview/) · [Spark Structured Streaming modes](https://spark.apache.org/streaming/) · [Kafka Streams core concepts](https://kafka.apache.org/documentation/streams/core-concepts/) · [Beam programming guide](https://beam.apache.org/documentation/programming-guide/).

**Разбор одного incident по трём системам:** возьмите заказ `o-17`, который обновляет keyed state, после чего падает TaskManager. В Flink найдите последний completed checkpoint, его Kafka split offsets, restored operator state и повторный Iceberg commit. В Kafka Streams сравните offset/transaction markers и восстановление state store из changelog. В Spark проверьте номер завершённого batch и source/sink commit log в checkpoint directory. Одинаковый бизнес-результат может получаться из разных механизмов; нельзя переносить настройку checkpoint одной системы в другую по совпадению названия.

### Вопросы для защиты

1. Какие именно offsets и state составляют один checkpoint?
2. Почему aligned checkpoint испытывает влияние shuffle/backpressure?
3. В каком случае unaligned снижает latency и в каком добавляет вредную нагрузку?
4. Что означает key-group при scale-out с parallelism 2 → 4?
5. Как доказать, что восстановление вернулось к completed checkpoint, а не к последнему созданному?
