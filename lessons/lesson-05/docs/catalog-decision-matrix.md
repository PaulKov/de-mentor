# Сравнение Iceberg catalogs: decision matrix

Каталог отвечает на вопрос «как по имени таблицы получить её актуальную Iceberg metadata и согласованно опубликовать commit». Он не заменяет table format: Iceberg snapshots/manifests лежат в metadata files на storage. Это стартовая карта, не бенчмарк и не endorsement. До production выбора проверь версии, license/support model и точную engine matrix.

Колонки разделяют клиентский API, назначение продукта и вопросы PoC. Iceberg REST стандартизует обмен с движком, а хранение состояния, выдача credentials, поддержка refs и состав доступных операций зависят от реализации и версии.

| Вариант | API / модель | Когда рассматривать | Что проверить в PoC |
| --- | --- | --- | --- |
| **Lakekeeper** | Iceberg REST; projects/warehouses; storage profiles, authorization и delegation | self-hosted multi-engine lakehouse, S3-compatible storage | OIDC/authz, remote signing vs vended credentials, engine support, metadata DB backup/restore, upgrades |
| **Project Nessie** | Native version store + Iceberg REST; branches/tags/commits | branch-based isolation, experimentation, data product promotion | experimental status REST integration, version-store durability, merge conflicts, authz/S3 signing |
| **Apache Polaris** | REST catalog control plane for Iceberg catalogs | отдельное управление namespaces/catalogs через REST | maturity/release/support model, identity/federation, engine compatibility, HA/backup |
| **Apache Gravitino** | Основной сервер объединяет разнородные каталоги в metalake. Отдельный Iceberg REST API работает standalone или как auxiliary service, с JDBC, HMS или совместимым REST backend в 1.3.1 | Единый слой метаданных и управления доступом для нескольких источников или Iceberg REST поверх существующего HMS | Режим развёртывания и границы authz, backend и его recovery, поддержка операций в паре engine/server, S3 credentials, cache и поведение при записи в обход REST |
| **AWS Glue Data Catalog** | Управляемый каталог AWS. У Iceberg есть нативный `GlueCatalog` и региональный Iceberg REST endpoint; для REST смотри SigV4 и поддерживаемый AWS сценарий OAuth 2.0 | Lakehouse на AWS с IAM и Lake Formation | Разрешения каталога и S3, режим Glue/REST, account/region, доступные операции и конкретный Flink runtime, стоимость и переносимость |
| **Hive Metastore + Iceberg HiveCatalog** | Thrift; RDBMS-backed namespace/table records; для Iceberg таблиц — pointer на `metadata_location` | общий Hadoop/Hive/Spark/Trino estate и уже налаженные HMS operations | Hive/Thrift client jar matrix и Java compatibility, DB HA/backup/schema upgrades, lock configuration, authorization/Kerberos/TLS, multi-writer tests, table/partition scale. HMS Postgres хранит каталог, S3 хранит Iceberg metadata/data |
| **Hive Metastore Iceberg REST** | REST Iceberg API, реализованный поверх HMS в новых версиях Hive | сохранить HMS backend, одновременно подключать native Iceberg REST clients | доступность и зрелость REST endpoints в конкретном Hive release; возможность Hive 4.1+ нельзя предполагать в Hive 3.1.3/4.0.1; отдельно проверить API/auth/capabilities |
| **Iceberg Hadoop catalog** | metadata/catalog state в filesystem paths, без service | sandbox или изолированный warehouse | concurrent writers, namespace visibility, rename/locking, multi-engine safety |
| **Iceberg JDBC catalog** | обычная SQL DB хранит catalog metadata | SQL-backed вариант без REST service | DB HA/migrations, client support, auth и schema ownership |

## Как принимать решение

Оцени по 1–5: protocol/engine coverage; authn/authz/delegation; concurrency; branching; S3/cloud compatibility; HA/backup/restore; operational maturity; cost и exit path. Отделяй hard constraints: их нельзя компенсировать оценкой необязательного критерия.

## Эвристика

- Обязателен managed AWS control plane — сначала проверь Glue.
- Уже есть production HMS и он удовлетворяет engine/security/HA требованиям — сначала оцени продолжение `HiveCatalog`; миграция ради слова REST может не окупиться.
- Новым клиентам нужен Iceberg REST поверх существующего HMS — сравни Hive REST и Gravitino с Hive backend. Проверь, можно ли безопасно сохранить прямых Thrift writers в переходный период.
- Нужны branch/tag/review workflows — исследуй Nessie и отдельно проверь зрелость REST пути для выбранного engine.
- Нужен self-hosted REST с warehouse/storage profiles — оцени Lakekeeper.
- Нужно связать Hive, Iceberg и внешние системы в общем пространстве имён и управлять доступом из одного места — оцени полный Gravitino. Сопоставь его с Lakekeeper по объёму задачи, а с Nessie по тому, нужна ли федерация или ветвление состояния каталога.
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
- [Apache Gravitino 1.3.1 Iceberg REST](https://gravitino.apache.org/docs/1.3.1/iceberg-rest-service/)
- [AWS Glue Iceberg REST endpoint](https://docs.aws.amazon.com/glue/latest/dg/connect-glu-iceberg-rest.html)
- [Hive Metastore Iceberg REST Catalog API](https://hive.apache.org/docs/latest/admin/iceberg-rest-catalog/)
- [Flink 2.2 Hive connector dependencies](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/table/hive/overview/)
- [Deep dive: HMS and catalog evolution](deep-dives/hive-metastore-and-catalog-evolution.md)
- [Deep dive: Apache Gravitino, metalake, REST и commit](deep-dives/gravitino-internals.md)
