# Rubric — Lesson 05 (100 points)

| Критерий | Баллы | Strong evidence |
| --- | ---: | --- |
| Table model, schema, deletes, format version | 20 | grain/key/null/update choices explicit |
| Catalog/storage architecture | 20 | REST path, S3 path, identities and failures correct |
| Reproducibility and correctness | 15 | DDL/code repeatable, counts + aggregate + schema checked |
| Snapshot/file interpretation | 15 | IDs, operations, manifests/files and partition interpreted |
| Catalog selection / ADR | 15 | hard constraints, tradeoffs and compatibility PoC |
| Operations and recovery | 15 | catalog backup, object durability, rollback and safe GC order |

## Hard reject

- Ручное удаление объектов из Iceberg table path.
- Утверждение, что uncommitted S3 file виден в таблице.
- Нет catalog metadata recovery strategy.
- Docker Compose demo объявлен production-ready.
- Guarantee claim без границ source/sink/checkpoint/catalog/client.
