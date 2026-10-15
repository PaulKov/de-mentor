# Iceberg catalog cheat sheet

## Commit chain

```text
catalog entry -> current metadata JSON -> snapshot -> manifest list -> manifests -> data/delete files
```

Новый S3 object не обязательно виден в таблице. Commit публикует metadata version через catalog. Старые snapshots/files остаются до expiration/GC.

## Flink SQL catalog: Hive Metastore

Full setup lives in [`01-catalogs.sql`](../../labs/flink-iceberg/sql/01-catalogs.sql); demo is [`04-hive-catalog-demo.sql`](../../labs/flink-iceberg/sql/04-hive-catalog-demo.sql).

```sql
CREATE CATALOG hive_metastore WITH (
  'type' = 'iceberg', 'catalog-type' = 'hive',
  'uri' = 'thrift://hive-metastore:9083',
  'warehouse' = 's3a://de-mentor-warehouse/hive',
  'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO',
  's3.endpoint' = 'http://seaweedfs:8333', 's3.path-style-access' = 'true',
  's3.access-key-id' = 'demouser', 's3.secret-access-key' = 'demosecret123456',
  'client.region' = 'us-east-1'
);
```

HMS PostgreSQL stores the logical table registration and pointer such as `metadata_location`; Iceberg JSON/manifests/data remain in S3. The Thrift catalog can be replaced with REST, Glue or a versioned catalog without changing the Iceberg table format, subject to migration and engine compatibility.

## Flink SQL catalog: Lakekeeper

Полная версия в [`01-catalogs.sql`](../../labs/flink-iceberg/sql/01-catalogs.sql).

```sql
CREATE CATALOG lakekeeper WITH (
  'type' = 'iceberg', 'catalog-type' = 'rest',
  'uri' = 'http://lakekeeper:8181/catalog', 'warehouse' = 'flink-demo',
  'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO',
  's3.endpoint' = 'http://seaweedfs:8333', 's3.path-style-access' = 'true',
  's3.access-key-id' = 'demouser', 's3.secret-access-key' = 'demosecret123456',
  'client.region' = 'us-east-1'
);
```

```sql
SHOW CATALOGS;
USE CATALOG lakekeeper;
SHOW DATABASES;
SHOW TABLES IN lesson05;
SELECT * FROM lesson05.catalog_comparison;
SELECT * FROM lesson05.`catalog_comparison$snapshots`;
SELECT * FROM lesson05.`catalog_comparison$files`;
```

## Production questions

- Кто владеет metadata pointer, credentials, encryption и audit?
- Для уже существующего Hive estate, зачем мигрировать с HMS? Какой конкретный REST/cloud/branch capability окупает стоимость?
- Где persisted checkpoints и как проверяется restore?
- Совместимы ли readers с format version/delete semantics writer-а?
- Какой rollback window защищён retention policy?
- Кто выдаёт object access: IAM, vended credentials, remote signing или static keys?
