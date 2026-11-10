# Workbook ученика — Kafka, Flink state и Iceberg commits

Предпосылки: Lesson 05 / SQL, JSON, Kafka topic/partition и базовый Flink. Не требуется устанавливать Java, Maven или Python на машине с Docker: Compose использует контейнеры. Открой [стенд](../../../labs/flink-iceberg/README.md) и три deep dive по мере прохождения.

## 1. Подготовка и mental model

Для учебного стенда нужны Docker с Linux containers, Docker Compose v2 и около 6 GB RAM. Из корня `de-mentor`:

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

В SQL Client уже зарегистрированы Lakekeeper, Nessie и Hive Metastore. Выполни по очереди:

```sql
-- команды из файлов
-- labs/flink-iceberg/sql/04-kafka-source.sql
-- labs/flink-iceberg/sql/05-stream-to-iceberg.sql
```

`04-kafka-source.sql` содержит только DDL. Необязательный unbounded `SELECT` вынесен в `04a-preview-kafka-source.sql`; запускай preview отдельно и останавливай после просмотра, иначе он будет занимать SQL Client.

В другом PowerShell отправь фиксированный dataset:

```powershell
./labs/flink-iceberg/scripts/publish-orders.ps1
```

Job читает Kafka source. Дождись продвижения watermark и completed checkpoint после поступления данных. Открой новую сессию через `sql-client.ps1`, затем выполни `06-query-iceberg.sql`. Проверь, что появился Iceberg snapshot. Завершение checkpoint и видимость snapshot — отдельные наблюдения.

Запиши в evidence:

- Kafka topic/partition/offset до и после публикации;
- Flink Job ID, parallelism, checkpoint ID и duration;
- строки результата `window_start × window_end × region`;
- Iceberg snapshot id, operation, committed timestamp;
- число data files, file sizes, snapshot summary;
- сколько времени прошло между последней записью и table visibility.

## 3. Lab B — поздние и out-of-order записи

В `data/orders.jsonl` последняя запись намеренно имеет event time раньше ранее отправленного события. Для чистого прогона создай отдельный topic `orders-late` и отдельную целевую таблицу, подставь эти имена в source, producer и SQL запросы. Новый `group.id` не исключает прежние записи из чтения при `earliest-offset`. Зафиксируй порядок событий, watermark и вывод окон.

Ответь:

1. Закрылось ли окно до поздней строки?
2. Появилась ли строка в таблице, обновился ли агрегат или запись стала late?
3. Что изменится при bounded out-of-orderness 5s → 30s?
4. Какой компромисс между event completeness, latency и state retention?

## 4. Lab C — наблюдение checkpoint и recovery

Выполни [recovery drill](runbooks/recovery-drill.md) с двумя порциями событий. Сохрани Job ID, фактически восстановленный checkpoint, offsets и Iceberg snapshot. Сравни итоговые ключи и агрегаты с контрольным прогоном без сбоя.

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
