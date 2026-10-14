# Iceberg catalog cheat sheet

## Commit chain

```text
catalog entry -> current metadata JSON -> snapshot -> manifest list -> manifests -> data/delete files
```

Новый S3 object не обязательно виден в таблице. Commit публикует metadata version через catalog. Старые snapshots/files остаются до expiration/GC.

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
- Где persisted checkpoints и как проверяется restore?
- Совместимы ли readers с format version/delete semantics writer-а?
- Какой rollback window защищён retention policy?
- Кто выдаёт object access: IAM, vended credentials, remote signing или static keys?
