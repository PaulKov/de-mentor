# Сравнение Iceberg catalogs: decision matrix

Это стартовая карта, не бенчмарк и не endorsement. До production выбора проверь версии, license/support model и точную engine matrix.

| Вариант | API / модель | Когда рассматривать | Что проверить в PoC |
| --- | --- | --- | --- |
| **Lakekeeper** | Iceberg REST; projects/warehouses; storage profiles, authorization и delegation | self-hosted multi-engine lakehouse, S3-compatible storage | OIDC/authz, remote signing vs vended credentials, engine support, metadata DB backup/restore, upgrades |
| **Project Nessie** | Native version store + Iceberg REST; branches/tags/commits | branch-based isolation, experimentation, data product promotion | experimental status REST integration, version-store durability, merge conflicts, authz/S3 signing |
| **Apache Polaris** | REST catalog control plane for Iceberg catalogs | отдельное управление namespaces/catalogs через REST | maturity/release/support model, identity/federation, engine compatibility, HA/backup |
| **AWS Glue Data Catalog** | AWS-managed catalog; engine integrations vary | lakehouse целиком на AWS, IAM/Glue уже стандарт | конкретный Flink connector/runtime, account/region, maintenance, cost, portability |
| **Hive Metastore** | традиционный metastore API; Iceberg integration у движков | существующий Hadoop/Spark estate | не путать HiveCatalog и REST, HA/locking/auth, metadata compatibility |
| **Iceberg Hadoop catalog** | metadata/catalog state в filesystem paths, без service | sandbox или изолированный warehouse | concurrent writers, namespace visibility, rename/locking, multi-engine safety |
| **Iceberg JDBC catalog** | обычная SQL DB хранит catalog metadata | SQL-backed вариант без REST service | DB HA/migrations, client support, auth и schema ownership |

## Как принимать решение

Оцени по 1–5: protocol/engine coverage; authn/authz/delegation; concurrency; branching; S3/cloud compatibility; HA/backup/restore; operational maturity; cost и exit path. Отделяй hard constraints: их нельзя компенсировать оценкой необязательного критерия.

## Эвристика

- Обязателен managed AWS control plane — сначала проверь Glue.
- Нужны branch/tag/review workflows — исследуй Nessie и отдельно проверь зрелость REST пути для выбранного engine.
- Нужен self-hosted REST с warehouse/storage profiles — оцени Lakekeeper.
- Уже есть Hive estate — сравни стоимость миграции, а не новизну REST.
- Polaris рассматривай как самостоятельную REST альтернативу, проверяя эксплуатационную модель и поддержку.
- Hadoop/JDBC могут подойти в отдельных случаях, но не гарантируют HA/security без отдельного дизайна.

## Upstream

- [Iceberg REST catalog](https://iceberg.apache.org/docs/latest/rest-catalog/)
- [Lakekeeper S3 profiles](https://docs.lakekeeper.io/docs/latest/storage-s3/)
- [Lakekeeper getting started](https://docs.lakekeeper.io/getting-started/)
- [Nessie Iceberg REST configuration and status](https://projectnessie.org/guides/iceberg-rest/)
- [Nessie S3/SeaweedFS getting started](https://projectnessie.org/guides/try-nessie/)
- [Apache Polaris](https://polaris.apache.org/)
