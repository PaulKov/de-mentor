# Workbook ученика — Iceberg, S3 и REST catalogs

Ориентир: **3–4 часа**. Нужны основы SQL, Parquet и object storage. Открой [lab README](../../labs/flink-iceberg/README.md) рядом с workbook.

## 1. Не смешивай три роли

| Компонент | Отвечает за | Примеры |
| --- | --- | --- |
| Table format | snapshots, schema, partition spec, files и deletes | Apache Iceberg |
| Catalog | имя таблицы → current metadata location; сериализация commits | Hive Metastore, Lakekeeper, Nessie, Glue |
| Storage | чтение/запись файлов по object paths | AWS S3, SeaweedFS, ADLS, GCS |

Parquet — формат data file. Iceberg — описание таблицы и изменений во времени. S3 — объектная API поверхность. Lakekeeper не хранит строки, а SeaweedFS не определяет актуальный snapshot.

## 2. Что лежит в S3

```text
catalog entry -> metadata.json -> snapshot -> manifest-list.avro -> manifest.avro -> data.parquet / delete files
```

- **Metadata JSON** хранит schema, partition specs, table properties и snapshots.
- **Snapshot** — логическое состояние после commit; ссылается на manifest list.
- **Manifest list** описывает manifests и partition statistics.
- **Manifest** перечисляет data/delete files и column/value metrics.
- **Data file** хранит строки, обычно Parquet. Delete files меняют логическое содержимое без переписывания всех data files.
- Commit создаёт новую metadata version и обновляет catalog entry. Старые файлы нужны для time travel/rollback и удаляются отдельно по retention policy.

Iceberg использует optimistic concurrency. Writer читает текущую версию, готовит snapshot и пробует обновить каталог. Если другой writer уже изменил таблицу, commit может конфликтовать; writer должен перечитать состояние и безопасно повторить операцию. Наличие Parquet object само по себе не означает, что snapshot опубликован.

### Delete semantics

- **Copy-on-write** переписывает затронутые data files, упрощая чтение ценой write amplification.
- **Merge-on-read** записывает position/equality deletes и применяет их при чтении/компактации.
- Iceberg v2 добавляет row-level deletes. Проверь поддержку reader/writer по выбранным engine versions.

## 3. От Hadoop/Hive к современным каталогам

Hive появился из практической задачи Facebook: Hadoop масштабировал хранение и вычисления, но ad hoc MapReduce был слишком низкоуровневым для аналитиков. Hive добавил таблицы, колонки, partitions и SQL-абстракцию. HMS вынес регистрацию таблиц из процесса отдельного query engine в общую Thrift-службу с backend RDBMS; другие Hadoop-клиенты могли использовать тот же реестр. Iceberg не заменил HMS автоматически: его можно использовать с HMS как `HiveCatalog`.

Позже добавились другие потребности: файловая metadata таблицы должна хорошо работать поверх object storage, клиенты хотят общий HTTP API вместо согласования Hive/Thrift jar-ов, cloud-команды хотят managed control plane и IAM, а командам с data product workflows нужны versioned branches. Это разные оси выбора, не просто «старый плохой каталог → новый хороший». История и internals: [deep dive: HMS и эволюция каталогов](deep-dives/hive-metastore-and-catalog-evolution.md).

## 4. REST Catalog: протокол общий, продукты разные

Flink создаёт `CREATE CATALOG` с `catalog-type=rest` и URI. Клиент вызывает REST для namespace/table metadata, а `FileIO` читает и пишет S3. Каталог может выдать временные credentials или подписать запросы; также клиент может использовать отдельную IAM identity. В лабораторной Flink получает локальные credentials напрямую для детерминированной практики.

До выбора продукта заполни [decision matrix](catalog-decision-matrix.md). Сравни protocol, security model, branching, engine compatibility, operational ownership и восстановление.

## 5. Lab A — Lakekeeper + SeaweedFS

1. Запусти Compose и сохрани вывод `docker compose ps`.
2. Открой [Lakekeeper UI](http://localhost:18181/ui/) и [SeaweedFS filer UI](http://localhost:18888). S3 credentials `demouser / demosecret123456` действуют только в local demo.
3. Запусти `./labs/flink-iceberg/scripts/sql-client.ps1`.
4. В этой SQL-сессии выполни [`02-lakekeeper-demo.sql`](../../labs/flink-iceberg/sql/02-lakekeeper-demo.sql). Запиши `category × rows_count × revenue`.
5. Выполни metadata queries `$snapshots` и `$files` из файла.
6. Найди SeaweedFS prefix `de-mentor-warehouse/lakekeeper/`; сопоставь metadata/data files с snapshot.
7. Останови только Lakekeeper: `docker compose -f labs/flink-iceberg/compose.yaml stop lakekeeper`. S3 objects остаются. Затем выполни `start lakekeeper`.

Запиши metadata location, snapshot id, file count и разницу поведения при catalog outage и object-store outage.

## 6. Lab B — тот же Iceberg REST API, Nessie

1. В той же SQL-сессии выполни [`03-nessie-demo.sql`](../../labs/flink-iceberg/sql/03-nessie-demo.sql).
2. Сравни результат с Lakekeeper. Nessie пишет в отдельный prefix `nessie/`.
3. Проверь `/api/v2/config` и `/api/v2/trees` на <http://localhost:19120>. Создай короткоживущую ветку `lesson05-review` от `main` через Nessie API или CLI.
4. Подключи Iceberg REST к branch URI и сформулируй, что branch версионирует и что не копирует.

Nessie хранит refs в persistent RocksDB volume, но здесь это single-node demo. Upstream помечает Iceberg REST integration Nessie как experimental; здесь мы изучаем протокол, а не рекомендуем production deployment.

## 7. Lab C — Hive Metastore Thrift + Iceberg на S3

1. Убедись, что `hive-metastore` и отдельный `hive-metastore-postgres` healthy. Thrift endpoint внутри Compose: `thrift://hive-metastore:9083`; с хоста он опубликован как `localhost:19083`.
2. Открой новый Flink SQL Client и выполни [`01-catalogs.sql`](../../labs/flink-iceberg/sql/01-catalogs.sql), затем введи `SHOW CATALOGS;`. Убедись, что зарегистрирован `hive_metastore`.
3. Выполни [`04-hive-catalog-demo.sql`](../../labs/flink-iceberg/sql/04-hive-catalog-demo.sql). Запиши aggregate, snapshot id и список data files.
4. В SeaweedFS найди prefix `de-mentor-warehouse/hive/`. Iceberg metadata JSON, manifests и Parquet должны лежать там.
5. В другой PowerShell покажи table parameters в backend HMS PostgreSQL:

   ```powershell
   docker compose -f labs/flink-iceberg/compose.yaml exec hive-metastore-postgres `
     psql -U hive -d hive_metastore -c 'SELECT t."TBL_NAME", p."PARAM_KEY", p."PARAM_VALUE" FROM "TABLE_PARAMS" p JOIN "TBLS" t USING ("TBL_ID") WHERE t."TBL_NAME" = $$hms_catalog_comparison$$ AND p."PARAM_KEY" IN ($$metadata_location$$, $$previous_metadata_location$$, $$table_type$$) ORDER BY p."PARAM_KEY";'
   ```

6. Сопоставь `metadata_location` с metadata JSON object в S3. Затем выключи только `hive-metastore`: файлы сохранятся, но имя таблицы через этот каталог временно не разрешается.
7. Сравни HMS с Lakekeeper: оба связывают namespace/table с Iceberg metadata, но HMS здесь использует Thrift и свою PostgreSQL; Lakekeeper предоставляет Iceberg REST и собственную warehouse/storage control plane.

**Контрольный вопрос:** какая информация должна пережить отказ HMS, чтобы таблицу можно было зарегистрировать заново, и почему нельзя выбирать «последний JSON по имени файла» простым `LIST` в S3?

## 8. Table maintenance — не удаляй файлы вручную

Составь порядок для snapshot retention/rollback window, compaction, expiration старых snapshots и orphan-file cleanup. Безопасный принцип: сначала commit/retention policy, затем rewrite/expire, потом garbage collection. Ручное удаление object может испортить видимый snapshot.

## 9. Senior design review

Кейс: 12 команд, Flink/Spark/Trino, два S3 account и один self-hosted object store, project isolation, audit, branch-based testing, восстановление catalog metadata.

Выбери каталог(и), нарисуй system boundary, IAM, backup/restore и maintenance. Перечисли предположения, требующие PoC: credentials delegation, engine compatibility, concurrency, HA и upgrades.

Сдай [evidence template](../homework/templates/evidence.md) как `lessons/lesson-05/submissions/evidence.md`. Скриншоты не заменяют конкретные IDs/числа.
