# Lesson 05 — Iceberg on S3: Hive Metastore, Lakekeeper, Nessie и Gravitino

Стенд: **`flink-iceberg`** · Формат: **Iceberg v2** · Storage: **SeaweedFS / S3 API** · Catalogs: **Hive Metastore Thrift, Lakekeeper, Nessie и Gravitino Iceberg REST**

| Раздел | Путь | Зачем |
| --- | --- | --- |
| Теория и workbook | [docs/](docs/) | metadata, snapshots, object storage и catalog |
| Internals | [deep-dives/](docs/deep-dives/) | история Hive/HMS, metadata graph, commit protocols, REST и сравнение форматов |
| Runbooks | [docs/runbooks/](docs/runbooks/) | короткий, глубокий и восстановительный маршруты |
| Homework | [homework/](homework/) | спроектировать и доказать Iceberg lakehouse |
| SQL и сервисы | [../../labs/flink-iceberg/](../../labs/flink-iceberg/) | три базовых каталога и профиль Gravitino на общем S3 bucket |
| Evidence | [submissions/](submissions/) | submission layout |

Перед этим уроком пройди [Lesson 04b: distributed filesystems and object storage](../lesson-04b-distributed-storage/): там объяснены object keys, S3 API, SeaweedFS topology и границы гарантии storage. Здесь эти знания используются для отдельного разбора Iceberg metadata/catalog commits.

## Результат урока

Ученик прослеживает путь от `INSERT` до Iceberg snapshot и сопоставляет каталожный указатель с файлами в S3. Сравнивает HMS Thrift, Lakekeeper REST, Nessie refs и Gravitino с JDBC backend, различает Iceberg REST API и федерацию через metalake и аргументирует выбор каталога для заданного окружения.

## Быстрый старт

```powershell
./labs/flink-iceberg/scripts/up.ps1
./labs/flink-iceberg/scripts/sql-client.ps1
```

Выполнять из корня `de-mentor`. Адреса UI и состав сервисов: [lab README](../../labs/flink-iceberg/README.md).

- [Индекс и цели](docs/README.md)
- [Workbook ученика](docs/student-workbook.md)
- [План ментора](docs/mentor-guide.md)
- [Сравнение каталогов](docs/catalog-decision-matrix.md)
- [Deep dive: Hive Metastore и эволюция каталогов](docs/deep-dives/hive-metastore-and-catalog-evolution.md)
- [Deep dive: Gravitino, metalake и Iceberg REST](docs/deep-dives/gravitino-internals.md) · [Lab D](docs/runbooks/gravitino-lab.md)
- [Deep dive: metadata и snapshot internals](docs/deep-dives/iceberg-metadata-internals.md)
- [Deep dive: catalog и commit protocols](docs/deep-dives/catalog-commit-protocols.md)
- [История и альтернативы table formats](docs/deep-dives/table-formats-history-and-alternatives.md)
- [Homework](homework/assignment.md)
- [Rubric](homework/rubric.md)

← [Все уроки](../README.md) · Далее → [Lesson 06: Kafka + Flink + Iceberg](../lesson-06/)
