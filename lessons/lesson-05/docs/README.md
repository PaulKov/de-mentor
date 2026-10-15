# Lesson 05 — цели и карта занятия

**Prerequisite:** [Lesson 04b — Distributed filesystems and object storage](../../lesson-04b-distributed-storage/README.md). Ученик должен различать bucket/key, object bytes, filer metadata и filesystem path. Это позволяет обсуждать Iceberg snapshot/catalog semantics отдельно от нижнего storage API.

## Учебные цели

К концу занятия ученик:

1. Отличает Iceberg table format от Parquet/Avro и catalog service.
2. Объясняет metadata JSON, manifest list, manifests, data/delete files и snapshots.
3. Прослеживает atomic metadata pointer update и понимает optimistic concurrency conflicts.
4. Разворачивает S3-compatible bucket, bootstraps Lakekeeper и создаёт warehouse.
5. Подключает Flink SQL к Lakekeeper и Nessie через Iceberg REST API, а к Hive Metastore — через Thrift `HiveCatalog`.
6. Объясняет, что HMS хранит для Iceberg table registration и pointer, а snapshots/manifests/data лежат в S3.
7. Связывает происхождение HMS с Hadoop/Hive и объясняет, почему возникли REST, cloud-managed и versioned catalogs.
8. Наблюдает, что объекты остаются в S3 после остановки catalog service.
9. Выбирает каталог по protocol, governance, branching, облаку и эксплуатации.
10. Отличает учебный стенд от production: identity, TLS, HA, database, credentials, backup и table maintenance.

## План на 3 ч 30 мин

| Время | Блок | Свидетельство |
| ---: | --- | --- |
| 0–15 мин | Table format vs object store vs catalog | схема трёх границ |
| 15–40 мин | Iceberg metadata и atomic commit | snapshot metadata chain |
| 40–60 мин | История Hive/HMS и зачем нужны новые каталоги | HMS ≠ Hive engine; разделены format и catalog |
| 60–75 мин | Поднять стенд | Compose health + endpoint checks |
| 75–105 мин | Lab A: Hive Metastore Thrift | `metadata_location` в HMS Postgres сопоставлен с JSON в S3 |
| 105–140 мин | Lab B: Lakekeeper | aggregate, `$snapshots`, `$files`, SeaweedFS objects |
| 140–160 мин | Lab C: Nessie | третий catalog, refs и S3 prefix |
| 160–180 мин | Сравнение alternatives | decision matrix и сценарий выбора |
| 180–200 мин | Production design review | backup/recovery и PoC evidence |
| 200–210 мин | Debrief + homework | исправленная схема и evidence plan |

## Схема

```mermaid
flowchart LR
  E[Engine: Flink / Spark / Trino] -->|Thrift| H[Hive Metastore]
  H -->|catalog rows / commit coordination| DB[(HMS Postgres)]
  E -->|Iceberg REST| L[Lakekeeper / Nessie / Glue]
  H -.->|current metadata pointer| M[Iceberg metadata]
  L -.->|current metadata pointer| M
  E -->|S3 GET/PUT| O[Object store: SeaweedFS / S3]
  M --> MF[Manifest list + manifests]
  MF --> D[Parquet data + delete files]
```

Каталог сериализует/координирует изменения таблицы и определяет current metadata. У HMS pointer находится в HMS database; у других каталогов состояние хранится по их реализации. Object store сохраняет Iceberg metadata и table files. Engine планирует чтение и пишет файлы. Ни одна роль не заменяет две остальные.

## Deep dives: от концепта до исходного кода

- [Iceberg metadata internals](deep-dives/iceberg-metadata-internals.md) — от задачи Hive-style layout до field IDs, manifests, sequence numbers, deletes и snapshot commit.
- [Catalog и commit protocols](deep-dives/catalog-commit-protocols.md) — REST lifecycle, optimistic CAS, Lakekeeper/Postgres/S3 и Nessie references, conflict/failure matrix.
- [Hive Metastore и эволюция каталогов](deep-dives/hive-metastore-and-catalog-evolution.md) — история HMS, Thrift internals, `metadata_location`, причины REST/cloud/versioned каталогов и production PoC.
- [История и альтернативы](deep-dives/table-formats-history-and-alternatives.md) — Iceberg vs Delta Lake/Hudi/Paimon, COW/MOR и выбор по workload.

Каждый deep dive содержит фрагменты кода/SQL, links на спецификацию и upstream реализацию, а также вопросы для senior-level защиты. Воркбук задаёт лабораторный маршрут; deep dives объясняют почему конкретные шаги работают.

## До занятия

- Docker Desktop в режиме Linux containers, около 6 GB свободной памяти Docker.
- Поднять стенд по [student prep](runbooks/student-prep.md).
- Открыть Flink UI, Lakekeeper UI, SeaweedFS filer UI и Nessie API.
- Проверить SQL-сессию и `SHOW CATALOGS;`: должны быть `hive_metastore`, `lakekeeper` и `nessie`.
- Не использовать demo credentials как образец production security.

## Проверочные вопросы

- Что гарантирует каталог, если два writer-а одновременно публикуют metadata?
- Почему удаление записи не обязано сразу удалять Parquet object?
- Что увидит Flink при недоступном Lakekeeper, но доступном SeaweedFS? И наоборот?
- Чем отличаются manifest rewrite, compaction и orphan-file cleanup?
- Какую часть состояния версионирует Nessie branch?
- Какие клиенты должны согласовать `FileIO`, format features и credentials?
