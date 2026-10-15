# Deep Dive: Iceberg изнутри — от строки до snapshot

Этот документ разбирает не API вызовов, а контракт формата. Iceberg — табличная система метаданных поверх файлов объектов: Parquet/ORC/Avro хранят строки и колоночные статистики, Iceberg описывает согласованный набор файлов, а catalog сериализует публикацию нового состояния. Если понять только «таблица лежит в папке», потеряются schema evolution, partition evolution, time travel и причина, почему случайный файл в S3 не становится строкой таблицы.

## 1. Историческая задача: почему каталог каталогов перестал быть таблицей

В ранних data lakes таблицу обычно моделировали как набор директорий, часто `table/year=2025/month=01/`, плюс Hive Metastore, где лежал список partitions и их locations. Это работало, пока таблицы менялись главным образом append-ами, partitions были заранее понятны, а запросы использовали один совместимый набор правил.

На больших озёрах обнаружились системные ограничения: метастор должен был перечислять огромное число partitions; rename/drop column мог менять интерпретацию старых файлов; изменение схемы и партиционирования требовало координировать писателей и читателей; concurrent overwrite мог оставить читателю смесь старого и нового состояния. Пути директорий сами по себе не дают транзакционный snapshot.

Iceberg создавался в Netflix с 2017 года, был передан Apache Software Foundation в 2018 году и задумывался как открытый table format для больших аналитических таблиц. Ключевой поворот — не добавить ещё один формат строк, а сделать метаданные таблицы версионируемым графом небольших файлов с атомарным переключением текущего корня. [История в ASF](https://news.apache.org/foundation/entry/asf-project-spotlight-apache-iceberg) · [Спецификация](https://iceberg.apache.org/spec/).

## 2. Три независимые плоскости

```text
SQL/DataStream plan
  │ engine выбирает файлы и кодирует строки
  ▼
Table format: Iceberg metadata graph ──► Parquet / ORC / Avro objects
  │ TableOperations: load, validate, commit
  ▼
Catalog: имя таблицы → актуальное metadata location

Object store: байты файлов, без знания семантики таблицы
```

**Engine** — Flink, Spark, Trino — исполняет вычисление и использует библиотеку Iceberg. **Format** определяет, как из файлов составляется snapshot, как идентифицируются поля и какие delete применяются. **Catalog** связывает логическое имя с текущим metadata file и решает, может ли писатель атомарно опубликовать обновление. **Object store** отвечает за байты и операции хранения. Наличие `s3://bucket/path/part-000.parquet` не делает его частью таблицы: файл виден только после того, как commit metadata включил его в snapshot.

## 3. Цепочка метаданных и стоимость планирования

```text
catalog.current_metadata_location
  └── v42.metadata.json
       ├── current schema id, schema history, field IDs
       ├── partition specs, sort orders, table properties
       ├── refs, snapshots, metadata log
       └── snapshot S42
            └── snap-42-....avro   (manifest list)
                 ├── manifest-01.avro → data files, partition tuples, metrics
                 ├── manifest-02.avro → data files, partition tuples, metrics
                 └── delete-manifest.avro → position/equality deletes
                      └── data-....parquet / delete-....parquet
```

Metadata JSON — маленький корень таблицы. Snapshot фиксирует видимое состояние. Manifest list даёт состав manifests, их partition summaries и число added/existing/deleted файлов; engine может отбросить целые manifests до чтения самих списков. Manifest — Avro-файл со строкой на каждый content file, его partition tuple, record count, bounds/null counts и прочими метриками. Читатель применяет фильтры в несколько ступеней: snapshot → manifest-list summary → manifest partition/column metrics → row-group statistics в Parquet → остаточный фильтр к строке.

Manifest — не «директория партиции». Один manifest может описывать файлы из разных значений partition, а манифесты могут переиспользоваться между snapshots. Это помогает не переписывать весь индекс таблицы при append. `$files` показывает файлы текущего состояния, а не историю каждой операции; для истории служат `$snapshots`, `$history`, `$manifests` и `$entries` (точный набор metadata tables зависит от engine/версии).

Практическая проверка в этом стенде:

```sql
SELECT committed_at, snapshot_id, operation, summary
FROM lakekeeper.demo.catalog_comparison$snapshots
ORDER BY committed_at DESC;

SELECT file_path, file_format, record_count, file_size_in_bytes,
       partition, lower_bounds, upper_bounds
FROM lakekeeper.demo.catalog_comparison$files;
```

Сравните один append с небольшим числом событий и несколько частых append-ов: число маленьких файлов и manifests растёт отдельно от числа строк. В production нужны sizing буферов/commit interval, compaction и расписание snapshot expiration; автоматическое удаление orphan objects не следует запускать, не понимая возраста файлов и незавершённых писателей.

## 4. Идентичность колонок: почему поле имеет ID, а не только имя

В Parquet Iceberg хранит field ID в schema metadata. Имя `customer_id` можно безопасно изменить, поле можно удалить, а новое поле с тем же именем — добавить как новое, не перепутав его со старым: reader проектирует значения по ID, не по текущему текстовому имени и не по позиции колонки. Пропущенный в старом файле ID разрешается как `null` либо default в соответствии со schema evolution rules.

```text
старый файл: field-id=7 name="cust_id" value=42
новая schema: field-id=7 name="customer_id"
reader: id=7 → 42

опасная схема без ID: позиция 2 меняет смысл после drop/rename → неверные данные
```

Поэтому вручную скопировать Parquet внутрь `data/` и добавить строку в manifest — некорректный способ загрузки. Форматная библиотека должна назначить IDs, применить актуальную schema и записать корректные метрики.

## 5. Partition transforms и эволюция без переезда данных

Hive-подход часто заставляет приложение вычислять и записывать `year=.../month=...`; запрос должен знать layout, а смена partition scheme превращается в миграцию файлов и каталогов. Iceberg задаёт скрытые transforms, например `days(event_ts)`, `months(event_ts)`, `bucket(64, user_id)`, `truncate(8, code)`, сохраняя исходную колонку в строке. Planner переводит predicate над source column в ограничения для файловых partitions.

```sql
CREATE TABLE lakekeeper.demo.events (
  event_id BIGINT,
  event_ts TIMESTAMP_LTZ(3),
  region STRING,
  amount DECIMAL(18, 2)
) PARTITIONED BY (days(event_ts), region);

-- Позже можно добавить новый partition spec, не переписывая старые данные.
ALTER TABLE lakekeeper.demo.events
  SET ('write.distribution-mode' = 'hash');
```

Каждый spec имеет ID. Manifest сообщает, по какому spec записан каждый файл, поэтому старые и новые файлы читаются одной таблицей. Неполная эволюция не гарантирует хороший pruning: predicate должен быть преобразуем в transform, statistics могут быть недостаточно селективны, а слишком много мелких files/manifests может стоить дороже, чем экономия scan.

## 6. Snapshot, sequence number и delete semantics

Snapshot — immutable описание состояния. Append обычно добавляет файлы и новый snapshot, не меняя уже опубликованные файлы. Update/delete в v2 могут использовать **position delete** (конкретный file path + row position) или **equality delete** (набор field IDs и значений, совпадение строки). Ряд engine/write path выбирает стратегию: copy-on-write переписывает затронутые data files; merge-on-read добавляет delete files, которые должны быть применены при чтении или последующей compaction.

V2 sequence number фиксирует относительный возраст content. Это важно: equality/position delete применяется к подходящим data files согласно семантике snapshot/sequence, а не просто «к любому файлу с похожей строкой». `file_sequence_number` отвечает, когда файл появился; `data sequence number` нужен, чтобы определить, какой delete относится к какому содержимому. При rebase после конфликта commit получит номер успешно опубликованной версии, а не устаревший предварительный номер.

Не следует обобщать «Iceberg = merge-on-read» или «Iceberg = copy-on-write»: format поддерживает модель deletes, а конкретный engine, SQL operation, format version и параметры определяют write path. V3 включает дальнейшие возможности вроде row lineage и deletion vectors; перед использованием нового feature проверьте одновременно спецификацию, версию Iceberg-библиотеки, reader-ов и writer-ов. Например, наш стенд закреплён на **v2**, чтобы показать широко понятный и совместимый контракт.

## 7. Что физически означает commit

1. Writer читает текущий metadata JSON и строит план изменений относительно snapshot S42.
2. Task-ы записывают новые immutable data/delete files в уникальные object keys. На этом шаге они ещё не входят в таблицу.
3. Committer собирает manifests/manifest list и пишет новый metadata JSON со snapshot S43.
4. Catalog атомарно проверяет, что current metadata всё ещё указывает на базу S42, и меняет pointer на metadata S43.
5. Читатель, загрузивший S42 раньше, продолжает видеть консистентный старый snapshot; новый читатель после refresh видит S43.
6. Если compare-and-swap не прошёл, writer обнаружил concurrent commit. Он перечитывает актуальное состояние, проверяет конфликтующие файлы/условия и либо безопасно повторяет metadata update, либо возвращает конфликт.

Сам факт успешного `PUT` файла не означает commit. Неудача до шага 4 может оставить orphan file. Очистка orphan files — отдельная операция с возрастным grace period, иначе можно стереть файлы, которые writer ещё собирается включить в commit.

## 8. Источники и код для чтения реализации

- [Iceberg specification: metadata, snapshots, optimistic concurrency, manifests, v1/v2/v3](https://iceberg.apache.org/spec/)
- [Iceberg schema evolution](https://iceberg.apache.org/docs/latest/evolution/)
- [Partitioning and transforms](https://iceberg.apache.org/docs/latest/partitioning/)
- [Flink writes: SQL and DataStream examples](https://iceberg.apache.org/docs/latest/flink-writes/)
- [Iceberg source tree](https://github.com/apache/iceberg/tree/main/core/src/main/java/org/apache/iceberg): начинайте с `TableMetadata`, `Snapshot`, `ManifestFile`, `ManifestEntry`, `BaseMetastoreTableOperations`; для Flink — `flink/v2.2/flink/src/main/java/org/apache/iceberg/flink/sink/`.

### Вопросы для защиты

1. Почему Parquet-файл, который виден в SeaweedFS, может быть orphan и не входить в таблицу?
2. Как reader понимает колонку после rename, если у старого файла другое имя?
3. Какие объекты прочитает planner при predicate `event_ts >= ...` и какие уровни pruning возможны?
4. Чем sequence number отличается от snapshot ID?
5. Почему cleanup orphan files должен учитывать длинные checkpoints и commit retries?
