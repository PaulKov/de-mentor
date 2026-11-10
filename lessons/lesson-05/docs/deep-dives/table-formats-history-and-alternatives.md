# Deep Dive: История lakehouse table formats и альтернативы Iceberg

Сравнение форматов имеет смысл после фиксации одинаковой задачи: несколько движков читают одну таблицу в object storage, нужны ACID-like commits, schema/partition evolution, time travel и корректная конкурентная запись. Parquet — это формат файла; Iceberg/Delta/Hudi/Paimon — правила версионирования множества файлов. Каталог (Lakekeeper, Nessie, Glue, Hive Metastore, Polaris) — ещё отдельная ось.

## Историческая линия

| Период | Поворот | Что осталось нерешённым |
|---|---|---|
| Hadoop/Hive, раннее озеро | таблица = directory/partition layout + metastore; batch читатели сканируют файлы | дорогой listing, schema/partition договорённости, конкуренция writers, неатомарные переписывания |
| Hudi, 2016–2017; open source от Uber | инкрементальные upsert/CDC и record-level changes для аналитического lake | сложные индексы/write modes и необходимость compaction для MOR |
| Iceberg, Netflix, 2017; ASF 2018 | открытая спецификация, snapshots и manifest tree, скрытые transforms и эволюция таблицы | формату нужны совместимые readers/writers и корректный catalog commit implementation |
| Delta Lake, Databricks, 2019; затем Delta UniForm / каталог-экосистема | transaction log и тесная Spark/Databricks интеграция, позже более открытая interop story | проверять feature parity и наиболее подходящий runtime/каталог для конкретных функций |
| Paimon, вырос из Flink Table Store, 2022+ | streaming-native primary-key tables, changelog production и быстрые Flink updates | учитывать engine ecosystem и различие между streaming state table и широким interchange lake format |
| REST catalogs и общие interop APIs | стандартизировать client/catalog границу | единый HTTP протокол не стандартизует каждую auth/branch/maintenance возможность |

Даты — ориентиры происхождения, а не рейтинг зрелости. [История Iceberg в ASF](https://news.apache.org/foundation/entry/asf-project-spotlight-apache-iceberg) · [Hudi: project overview](https://hudi.apache.org/docs/overview/) · [Delta Lake: protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md) · [Paimon architecture](https://paimon.apache.org/docs/master/concepts/overview/).

## Архитектурное сравнение

| Свойство | Iceberg | Delta Lake | Hudi | Paimon |
|---|---|---|---|---|
| Главный индекс | metadata JSON → snapshot → manifest list → manifests | `_delta_log` transaction log/checkpoints → active files | timeline of instants + file groups/file slices + metadata/index tables | snapshots/manifests/manifest lists + primary-key table machinery |
| Базовая модель concurrency | optimistic commit поверх table metadata pointer через catalog | optimistic transaction log protocol; конфликтные действия и isolation зависят от operation | timeline writer/reader model; concurrency control / lock provider зависит от deployment | snapshot commit and streaming-oriented write model, details depend on table type/config |
| Сильная сторона | engine-neutral table specification, field IDs, partition evolution, snapshots | Databricks/Spark-centered ecosystem, broad SQL/ML runtime and protocol development | incremental ingestion/upsert and CDC patterns; MOR/COW options | Flink-first streaming tables/changelog and primary-key workflows |
| Основная цена | разные engine versions могут поддерживать разные features; small files/snapshots need maintenance | некоторые advanced features связаны с runtime/platform/version matrix; protocol compatibility must be checked | operational complexity of indexing, compaction, clustering and timeline | interoperability matrix and engine maturity can differ from Iceberg for a given consumer |
| Когда рассматривать | multi-engine analytics lake with open metadata contract | organization standardized on Delta-compatible stack or has specific Delta workload requirements | CDC-heavy lake ingestion, record-level update workloads | continuous Flink ingestion, changelog-heavy table serving |

Не смешивайте **format feature** и **catalog feature**. Branching может быть форматом Iceberg refs или catalog-level Nessie refs с разной областью согласованности. S3 signing — storage access capability каталога, не свойство Parquet. ACID не означает, что любые два writer-а или любые engine versions автоматически совместимы.

## Режимы обновления: COW и MOR

Для апдейта маленького числа строк в большом Parquet file есть два крайних решения:

```text
Copy-on-write (COW): read old file → rewrite survivors + changed rows → commit new file
Merge-on-read (MOR): append data file + delete file → commit; reader merges on scan
                                               → later compaction rewrites clean files
```

COW переносит стоимость в write path и часто упрощает scan. MOR снижает стоимость частых writes, но повышает read amplification, усложняет поддерживаемые читателями операции и создаёт compaction debt. Это не буквальный бинарный флаг в одинаковом смысле у всех форматов: compare operation types, delete representation, compaction scheduler and connector capabilities.

## Как выбирать по workload, а не по лозунгу

1. **Чтение несколькими engines**: составьте матрицу версии engine × read/write operation × table format feature. Протокол и «может прочитать Parquet» не равны полной поддержке schema evolution, deletes, branch/time-travel.
2. **CDC/upsert**: измерьте долю изменённых rows per file, размер файла, update latency и расход compaction. Hudi и Paimon заслуживают отдельного benchmark при интенсивных ключевых обновлениях; Iceberg upsert также возможен, но зависит от format v2, PK configuration и writer behavior.
3. **Append analytics**: сравните throughput, target file size, commit interval, planning latency, manifest/log growth и maintenance.
4. **Независимость от cloud**: проверить IAM, object-store APIs, catalog deployment, encryption, governance и operational ownership, а не только SQL syntax.
5. **Recovery**: проверить одновременно restore catalog DB, retention snapshots, object versioning, GC behavior и возможность читать старые snapshots выбранным engine.

## Мини-эксперимент в стенде

Используйте одинаковую последовательность для таблицы Iceberg: 100 небольших appends, один overwrite/delete, затем compact/expire snapshots в отдельном namespace. Измерьте:

- data/delete object count и bytes;
- число snapshots/manifests и query planning time;
- commit latency p50/p95, conflict count, checkpoint-to-commit delay;
- scan read amplification при MOR/поддерживаемом upsert path;
- время recovery после завершения Flink на последнем completed checkpoint.

Если есть доступ к отдельным песочницам Delta/Hudi/Paimon, повторите workload одинаковой семантики. Не сравнивайте append в одном продукте с upsert в другом или разные file sizes.

## Каталоги — соседняя, но самостоятельная матрица

| Каталог | Главное отличие | Альтернативный выбор, если… |
|---|---|---|
| Lakekeeper | REST catalog service + warehouse/storage credential model | нужны централизованные Iceberg REST policies и S3 access integration |
| Nessie | branches/tags и commit graph на уровне нескольких таблиц | нужен Git-like review workflow для data changes |
| Apache Polaris | open REST catalog с governance/identity направлением | нужен нейтральный каталог для engine/client ecosystem и соответствующий feature set |
| AWS Glue | managed AWS catalog | данные и IAM полностью в AWS и приемлемая облачная зависимость |
| Hive Metastore / Hadoop | традиционные интеграционные модели | уже есть эксплуатационный стек; подтвердить transactional semantics, concurrency и object-store поддержку |
| JDBC | SQL DB backed catalog | нужна управляемая собственной командой простая транзакционная основа |

Перед фиксацией выбора проверяйте текущие release docs и capability endpoints: open-source проекты меняются быстро. [Apache Polaris](https://polaris.apache.org/) · [Iceberg catalog options](https://iceberg.apache.org/docs/latest/#catalogs).

## Вопрос Senior-собеседования

«Мы выбрали Iceberg, значит можем одним транзакционным запросом изменить 12 таблиц?» Ответ должен назвать границу Iceberg snapshot (одна таблица), отдельно объяснить, может ли выбранный catalog versioning слой обеспечить атомарное состояние нескольких таблиц, и описать downstream engines’ visibility/branch routing. Формат сам по себе не отвечает на multi-table transaction вопрос.
