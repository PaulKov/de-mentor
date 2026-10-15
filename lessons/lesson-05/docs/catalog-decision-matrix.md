# Сравнение Iceberg catalogs: decision matrix

Каталог отвечает на вопрос «как по имени таблицы получить её актуальную Iceberg metadata и согласованно опубликовать commit». Он не заменяет table format: Iceberg snapshots/manifests лежат в metadata files на storage. Это стартовая карта, не бенчмарк и не endorsement. До production выбора проверь версии, license/support model и точную engine matrix.

| Вариант | API / модель | Когда рассматривать | Что проверить в PoC |
| --- | --- | --- | --- |
| **Lakekeeper** | Iceberg REST; projects/warehouses; storage profiles, authorization и delegation | self-hosted multi-engine lakehouse, S3-compatible storage | OIDC/authz, remote signing vs vended credentials, engine support, metadata DB backup/restore, upgrades |
| **Project Nessie** | Native version store + Iceberg REST; branches/tags/commits | branch-based isolation, experimentation, data product promotion | experimental status REST integration, version-store durability, merge conflicts, authz/S3 signing |
| **Apache Polaris** | REST catalog control plane for Iceberg catalogs | отдельное управление namespaces/catalogs через REST | maturity/release/support model, identity/federation, engine compatibility, HA/backup |
| **AWS Glue Data Catalog** | AWS-managed catalog; engine integrations vary | lakehouse целиком на AWS, IAM/Glue уже стандарт | конкретный Flink connector/runtime, account/region, maintenance, cost, portability |
| **Hive Metastore + Iceberg HiveCatalog** | Thrift; RDBMS-backed namespace/table records; для Iceberg таблиц — pointer на `metadata_location` | общий Hadoop/Hive/Spark/Trino estate и уже налаженные HMS operations | Hive/Thrift client jar matrix и Java compatibility, DB HA/backup/schema upgrades, lock configuration, authorization/Kerberos/TLS, multi-writer tests, table/partition scale. HMS Postgres хранит каталог, S3 хранит Iceberg metadata/data |
| **Hive Metastore Iceberg REST** | REST Iceberg API, реализованный поверх HMS в новых версиях Hive | сохранить HMS backend, одновременно подключать native Iceberg REST clients | доступность и зрелость REST endpoints в конкретном Hive release; возможность Hive 4.1+ нельзя предполагать в Hive 3.1.3/4.0.1; отдельно проверить API/auth/capabilities |
| **Iceberg Hadoop catalog** | metadata/catalog state в filesystem paths, без service | sandbox или изолированный warehouse | concurrent writers, namespace visibility, rename/locking, multi-engine safety |
| **Iceberg JDBC catalog** | обычная SQL DB хранит catalog metadata | SQL-backed вариант без REST service | DB HA/migrations, client support, auth и schema ownership |

## Как принимать решение

Оцени по 1–5: protocol/engine coverage; authn/authz/delegation; concurrency; branching; S3/cloud compatibility; HA/backup/restore; operational maturity; cost и exit path. Отделяй hard constraints: их нельзя компенсировать оценкой необязательного критерия.

## Эвристика

- Обязателен managed AWS control plane — сначала проверь Glue.
- Уже есть production HMS и он удовлетворяет engine/security/HA требованиям — сначала оцени продолжение `HiveCatalog`; миграция ради слова REST может не окупиться.
- Новым клиентам нужен единый Iceberg REST API, а Thrift client dependency graph становится проблемой — сравни Lakekeeper, Polaris, Hive REST и другие реализации по конкретным endpoints/auth.
- Нужны branch/tag/review workflows — исследуй Nessie и отдельно проверь зрелость REST пути для выбранного engine.
- Нужен self-hosted REST с warehouse/storage profiles — оцени Lakekeeper.
- Polaris рассматривай как самостоятельную REST альтернативу, проверяя эксплуатационную модель и поддержку.
- Hadoop/JDBC могут подойти в отдельных случаях, но не гарантируют HA/security без отдельного дизайна.

## Почему HMS не закрыл все новые потребности

HMS решил раннюю задачу: совместный каталог схем, таблиц и partitions для Hadoop-инструментов. Iceberg улучшил **модель таблицы и metadata**, но мог оставить HMS как внешний указатель. Следующий шаг эволюции относится уже к **API и управлению платформой**: REST развязывает клиента и Hive-библиотеки, облачные каталоги снимают часть on-call, storage-aware сервисы дают управляемые credentials/policies, а Nessie добавляет refs/branching для целых наборов таблиц. Эти требования ортогональны. Поэтому PoC может выбрать HMS+Iceberg, Glue+Iceberg или REST+Iceberg, не меняя сам table format.

## Upstream

- [Iceberg REST catalog](https://iceberg.apache.org/docs/latest/rest-catalog/)
- [Lakekeeper S3 profiles](https://docs.lakekeeper.io/docs/latest/storage-s3/)
- [Lakekeeper getting started](https://docs.lakekeeper.io/getting-started/)
- [Nessie Iceberg REST configuration and status](https://projectnessie.org/guides/iceberg-rest/)
- [Nessie S3/SeaweedFS getting started](https://projectnessie.org/guides/try-nessie/)
- [Apache Polaris](https://polaris.apache.org/)
- [Hive Metastore Iceberg REST Catalog API](https://hive.apache.org/docs/latest/admin/iceberg-rest-catalog/)
- [Flink 2.2 Hive connector dependencies](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/table/hive/overview/)
- [Deep dive: HMS and catalog evolution](deep-dives/hive-metastore-and-catalog-evolution.md)
