# Rubric — Lesson 04b (100 баллов)

| Критерий | Баллы | Strong evidence |
| --- | ---: | --- |
| Workload contract и выбор API | 15 | path/key/block semantics, access pattern, atomic unit и hard constraints явно перечислены |
| Системная архитектура и data path | 15 | metadata/control/data/placement components разведены; client bytes path непротиворечив |
| Capacity, replication/EC и topology | 15 | raw/usable/reserve расчёт; failure map учитывает rack/site и degraded repair |
| Product alternatives и ADR | 15 | сравнение минимум трех реалистичных альтернатив по разным storage contracts; корректно различены HDFS, Ozone, Lustre, Ceph, SeaweedFS и/или RustFS там, где они релевантны; причины отказа привязаны к требованиям |
| Security и governance | 10 | identity separation, TLS/encryption, audit, retention, least privilege и key rotation |
| Reliability, recovery, backup | 15 | отдельные RPO/RTO для bytes/metadata; runnable restore и post-restore validation |
| PoC и эксплуатационная модель | 10 | версии, realistic size/skew/concurrency, p99, LIST/multipart and pass/fail gates |
| Lab evidence and technical reasoning | 5 | корректный S3 request trace и разделение observed/inferred |

## Performance bands

- **90–100 — senior-ready**: design защищён цифрами и границами, признаны unknowns, PoC и restore воспроизводимы.
- **75–89 — strong**: выбор адекватен и почти полон, но часть costs/failure states требует конкретизации.
- **60–74 — developing**: продукт выбран по fit, но не доказаны recovery, metadata или semantics.
- **ниже 60 — revise**: имя продукта подменяет architecture; нет meaningful test, capacity reserve или rollback story.

## Hard reject

- Называть простой S3 prefix истинным каталогом или обещать rename/locking без проверки.
- Путать replication factor с числом независимых failure domains.
- Объявить Docker Compose laboratory proof production HA/durability/security.
- Не указывать, как восстановить metadata/catalog и как подтвердить целостность данных.
- Дать TCO только по стоимости хранения за GB, проигнорировав requests, network, retrieval и operations.
- Предлагать безусловное удаление старого source после copy без reconciliation/rollback period.
