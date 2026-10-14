# Homework — спроектировать распределённое хранилище

## Цель

Подготовить architecture decision record для одного из кейсов. Решение должно быть проверяемым, включать альтернативы и учитывать эксплуатацию, а не только закупку raw capacity.

## Выбери один кейс

### A. Backup / archive platform

- 5 PB логических данных, 80 TB новых данных в сутки;
- 90% объектов старше 30 дней читаются реже одного раза в год;
- restore 1 TB менее чем за 6 часов;
- нужна immutability на 30 дней и независимый site disaster recovery.

### B. Streaming lakehouse

- 40 TB live Iceberg, Kafka → Flink, параллельные Spark compaction и Trino scans;
- 4 записи/чтения engine групп и 20 reader jobs;
- p99 нового snapshot виден query engine менее чем за 60 секунд;
- надо сохранять snapshot для rollback 14 дней; daily backfill и schema evolution.

### C. Media object service

- 8 млрд изображений, median 90 KB / p99 8 MB;
- 60% GET приходится на 1% hot keys, загрузка до 50k objects/s;
- public delivery идет через CDN; оригиналы и derivatives имеют разное retention.

### D. Shared private-cloud data platform

- Kubernetes VM disks, NFS-like shared project directories и S3 lakehouse objects;
- storage team из 5 человек, nightly upgrade windows;
- четыре rack, 1 site, данные одной AZ/rack потери должны переживать; backup второго site пока только budget proposal.

## Deliverables

Создай `lessons/lesson-04b-distributed-storage/submissions/<name>/`:

1. `adr.md`: use case, NFR, hard constraints, выбранная архитектура и две rejected alternatives.
2. `architecture.md`: block/file/object contracts, components, control/data paths, namespace, placement и identity boundary; Mermaid diagram обязателен.
3. `capacity-and-cost.md`: logical/raw, replica/EC, usable reserve, metadata, network/repair budget; для cloud — requests, restore, egress, KMS и support.
4. `failure-matrix.md`: потеря disk/node/rack/site, network partition, metadata DB outage, accidental delete и credential compromise; expected response, detection, RPO/RTO.
5. `poc-plan.md`: конкретные SDK/client versions, workload/object histogram, p50/p95/p99 thresholds, concurrency, S3 semantics, test fixture и pass/fail criteria.
6. `restore-runbook.md`: кто принимает решение, порядок восстановления metadata/identity/data, validation и rollback.
7. `evidence.md`: результаты лабораторной SeaweedFS; отдели наблюдаемое от inferred.

## Обязательные вопросы

- Почему выбран object/file/block интерфейс и какой API verb является риском?
- Где хранится source of truth для namespace/metadata и как его восстановить?
- Что означает ack у write? Каково поведение concurrent writes одного key?
- На каком failure domain находятся shards и сколько свободного raw space остается после отказа?
- Сколько часов/day занимает repair/restore при ограниченном network bandwidth?
- Как защищены object deletion, catalog metadata, identities и encryption keys?
- Как измеряется стоимость request/list/restore/egress, кроме GB-month?
- Какая миграция/rollback стратегия если PoC не подтвердит SLO или API semantics?

## Сдача

Скопируй структуру из `submissions/README.md` и приложи evidence без секретов, customer data или токенов. Скриншот можно приложить, но он не заменяет command output, counts, checksums, version и timestamp.
