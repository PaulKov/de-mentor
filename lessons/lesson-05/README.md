# Lesson 05 — Iceberg on S3: REST catalogs with Lakekeeper and Nessie

Стенд: **`flink-iceberg`** · Формат: **Iceberg v2** · Storage: **SeaweedFS / S3 API** · Catalogs: **Lakekeeper + Project Nessie**

| Раздел | Путь | Зачем |
| --- | --- | --- |
| Теория и workbook | [docs/](docs/) | metadata, snapshots, object storage и catalog |
| Internals | [deep-dives/](docs/deep-dives/) | история формата, metadata graph, commit/CAS и сравнение форматов |
| Runbooks | [docs/runbooks/](docs/runbooks/) | короткий, глубокий и восстановительный маршруты |
| Homework | [homework/](homework/) | спроектировать и доказать Iceberg lakehouse |
| SQL и сервисы | [../../labs/flink-iceberg/](../../labs/flink-iceberg/) | практика на общем S3 bucket и двух каталогах |
| Evidence | [submissions/](submissions/) | submission layout |

Перед этим уроком пройди [Lesson 04b: distributed filesystems and object storage](../lesson-04b-distributed-storage/): там объяснены object keys, S3 API, SeaweedFS topology и границы гарантии storage. Здесь эти знания используются для отдельного разбора Iceberg metadata/catalog commits.

## Результат урока

Ученик прослеживает путь от `INSERT` до Iceberg snapshot, объясняет разделение каталога и S3, поднимает Lakekeeper REST catalog, сравнивает его с Nessie и аргументированно выбирает каталог для заданного окружения.

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
- [Deep dive: metadata и snapshot internals](docs/deep-dives/iceberg-metadata-internals.md)
- [Deep dive: catalog и commit protocols](docs/deep-dives/catalog-commit-protocols.md)
- [История и альтернативы table formats](docs/deep-dives/table-formats-history-and-alternatives.md)
- [Homework](homework/assignment.md)
- [Rubric](homework/rubric.md)

← [Все уроки](../README.md) · Далее → [Lesson 06: Kafka + Flink + Iceberg](../lesson-06/)
