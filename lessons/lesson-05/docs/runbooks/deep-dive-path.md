# Deep dive path — 3–4 часа

1. Выполнить [simple path](simple-path.md).
2. Пройти [Iceberg metadata internals](../deep-dives/iceberg-metadata-internals.md): metadata JSON → snapshots → manifests → files, field IDs, partition evolution, sequence numbers и deletes.
3. Проследить [catalog commit protocol](../deep-dives/catalog-commit-protocols.md), объяснить CAS/conflict/retry двух writers и failure windows.
4. Остановить Lakekeeper при активном SeaweedFS; отдельно описать обратный отказ.
5. Изучить Nessie refs через native API, создать review branch от `main`, подключить branch через Iceberg REST URI.
6. Сравнить v1/v2/v3 capabilities, copy-on-write/merge-on-read и [Iceberg/Delta/Hudi/Paimon](../deep-dives/table-formats-history-and-alternatives.md).
7. Спроектировать snapshot expiration, compaction, orphan cleanup и rollback window.
8. Заполнить [decision matrix](../catalog-decision-matrix.md).
9. Провести design review: auth, IAM, metadata backup, HA, SLO и engine matrix.
