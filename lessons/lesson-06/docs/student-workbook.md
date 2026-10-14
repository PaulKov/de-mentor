# Workbook ученика — Kafka, Flink state и Iceberg commits

Предпосылки: Lesson 05 / SQL, JSON, Kafka topic/partition и базовый Flink. Не требуется устанавливать Java, Maven или Python на Windows host: Compose использует контейнеры. Открой [стенд](../../labs/flink-iceberg/README.md) и три deep dive по мере прохождения.

## 1. Подготовка и mental model

Запусти Docker Desktop, убедись в режиме Linux containers и выдели Docker около 5 GB RAM. Из корня `de-mentor`:

```powershell
./labs/flink-iceberg/scripts/up.ps1
./labs/flink-iceberg/scripts/create-topic.ps1
docker compose -f labs/flink-iceberg/compose.yaml ps
```

Построй таблицу из четырёх координат:

| Координата | Что она означает | Где смотреть |
|---|---|---|
| Kafka offset | позиция чтения внутри конкретной partition | Kafka CLI / KafkaSource metrics |
| Flink checkpoint ID | согласованный snapshot всех stateful subtasks | Flink UI → Checkpoints |
| event timestamp | когда событие случилось по payload | Kafka JSON / decoded source row |
| watermark | event-time frontier, которую считает safe закрывать | operator/task metrics, оконный output |

Добавь к каждой строке пример значения для одного order ID из `data/orders.jsonl`.

## 2. Lab A — от события до Iceberg snapshot

Открой Flink SQL Client:

```powershell
./labs/flink-iceberg/scripts/sql-client.ps1
```

В SQL Client уже зарегистрируются Lakekeeper и Nessie. Выполни по очереди:

```sql
-- команды из файлов
-- labs/flink-iceberg/sql/04-kafka-source.sql
-- labs/flink-iceberg/sql/05-stream-to-iceberg.sql
```

В другом PowerShell отправь фиксированный dataset:

```powershell
./labs/flink-iceberg/scripts/publish-orders.ps1
```

Job начинает читать Kafka source. Подожди event-time watermark и минимум один completed checkpoint после поступления данных. Затем в новом SQL Client выполни `01-catalogs.sql`, затем `06-query-iceberg.sql`.

Запиши в evidence:

- Kafka topic/partition/offset до и после публикации;
- Flink Job ID, parallelism, checkpoint ID и duration;
- строки результата `window_start × window_end × region`;
- Iceberg snapshot id, operation, committed timestamp;
- число data files, file sizes, snapshot summary;
- сколько времени прошло между последней записью и table visibility.

## 3. Lab B — поздние и out-of-order записи

В `data/orders.jsonl` последняя запись намеренно имеет event time раньше ранее отправленного события. Выполни лабораторию заново с чистым topic (`orders-late` и отдельный source DDL либо новый `group.id`). Не изменяй production-like table незаметно: зафиксируй порядок событий, watermark strategy и вывод окон.

Ответь:

1. Закрылось ли окно до поздней строки?
2. Появилась ли строка в таблице, обновился ли агрегат или запись стала late?
3. Что изменится при bounded out-of-orderness 5s → 30s?
4. Какой компромисс между event completeness, latency и state retention?

## 4. Lab C — наблюдение checkpoint и recovery

Запусти pipeline и дождись completed checkpoint. Зафиксируй checkpoint ID/offsets. Останови **только** TaskManager из другого PowerShell:

```powershell
docker compose -f labs/flink-iceberg/compose.yaml stop flink-taskmanager
```

Наблюдай job failure/restart. Потом:

```powershell
docker compose -f labs/flink-iceberg/compose.yaml start flink-taskmanager
```

Сравни restored checkpoint, Kafka source offsets, итоговую Iceberg таблицу и количество snapshots. Не запускай новое submission поверх того же sink без анализа job identity и topic offsets.

## 5. Lab D — bottleneck и checkpoint internals

Открой [checkpoint deep dive](deep-dives/flink-runtime-and-checkpoint-internals.md). В UI выбери checkpoint → subtask details и запиши:

- start delay;
- synchronous duration;
- asynchronous duration;
- alignment duration / buffered bytes;
- checkpoint size и state size;
- failed checkpoints и причину.

Найди самый медленный operator/subtask. Сформулируй гипотезу: backpressure, skew, state growth, checkpoint I/O или catalog commit latency. Нельзя делать вывод только по общему job status.

## 6. Java DataStream и PyFlink

Прочитай два примера в [exactly-once deep dive](deep-dives/kafka-to-iceberg-exactly-once.md). Перепиши pipeline sketch для Java и Python:

```text
KafkaSource → parse schema → event-time WatermarkStrategy → keyBy/window → Iceberg sink
```

Подпиши, какая часть выполняется JVM Table/SQL connector-ом, а где возможен Python worker boundary. Если Python job использует Kafka/Iceberg, connector JARs должны быть доступны Flink JVM classpath; `pip install pyflink` не устанавливает все Java connectors.

## 7. Cleanup и durability

После сдачи останавливай stand без удаления volumes:

```powershell
./labs/flink-iceberg/scripts/down.ps1
```

Для полного reset скрипт спросит отдельное слово `DELETE`. Это удалит Kafka, Iceberg objects, catalog metadata и checkpoints. Перед reset сохрани evidence.

## Definition of done

- [ ] Pipeline SQL исполняется без connector/classpath errors.
- [ ] Появился completed checkpoint после входных данных.
- [ ] Iceberg query возвращает ожидаемые агрегаты и snapshot.
- [ ] Recovery evidence объясняет replay и отсутствие/наличие дублей.
- [ ] Документированы ограничения single-broker/single-node/local-checkpoint стенда.
- [ ] Ответы различают exactly-once state, table commit и business key uniqueness.
