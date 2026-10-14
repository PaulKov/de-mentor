# Deep dive path — 4+ часа

## Перед сессией

Прочитать обе главы [internals](../deep-dives/distributed-storage-internals.md) и [products/deployment](../deep-dives/products-and-deployment.md), пройти [student prep](student-prep.md), подготовить workload и decision worksheet. Для поиска исторического контекста используй ссылки на GFS/SOSP, HDFS, Ceph/OSDI и S3 launch в конце главы.

## Сессия

1. Написать на доске NFR трех jobs: 1 PB sequential scan, image service с миллиардом объектов, database с 5 ms p99 random write.
2. Разобрать interface semantics до product names: path vs key, atomic unit, lock, listing, range read, replace.
3. Нарисовать GFS/HDFS lineage и tradeoffs, затем сравнить Ceph's CRUSH/RADOS и SeaweedFS master/volume/filer.
4. Вывести `3×` и `8+3` overhead, поверх наложить physical rack/AZ failure map. Назвать recovery bandwidth, quorum и repair threshold.
5. Выполнить S3 lab из [workbook](../student-workbook.md). Для каждого HTTP/API status объяснить, что он доказал и что ещё нет.
6. Сделать capability matrix для используемого клиента: multipart, versioning, conditional operations, range, checksums, `LIST`, IAM, retention.
7. Посчитать TCO для on-prem vs cloud: storage class, request counts, network, restore, support, staffing и migration export.
8. Защитить архитектуру перед group review и записать PoC thresholds.

## Пять необязательных исследований

- Изучить официальный [Ceph CRUSH documentation](https://docs.ceph.com/en/latest/rados/operations/crush-map/) и объяснить failure-domain rule на собственном topology tree.
- Сравнить filer metadata store и SeaweedFS volume data backup; предложить consistent restore order.
- Провести workload replay с 1 KB, 100 KB, 128 MB и 5 GB objects. Записать p50/p99 и metadata/request count.
- Рассмотреть, что меняют GCS HNS folders / Azure ADLS HNS в Hadoop/analytics workload и какие API features требуют отдельной проверки.
- Для Iceberg warehouse определить, почему snapshot commit является multi-file/table metadata problem, а не `rename` S3 prefix.

## Exit criteria

Студент может провести 10-минутную защиту: один primary design, две rejected alternatives, contract + data path, failure map, capacity/recovery assumptions, security boundary, cost model, PoC plan и restore evidence.
