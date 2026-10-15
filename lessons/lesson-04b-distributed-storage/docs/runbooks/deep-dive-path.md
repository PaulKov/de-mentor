# Deep dive path — 4 часа в группе + 6–8 часов самостоятельной работы

## Перед сессией

Прочитать [модель storage](../deep-dives/distributed-storage-internals.md), отдельные deep dives по [HDFS](../deep-dives/hdfs-internals.md), [Ceph](../deep-dives/ceph-internals.md), [SeaweedFS](../deep-dives/seaweedfs-internals.md) и [выбору продуктов/внедрению](../deep-dives/products-and-deployment.md). Пройти [student prep](student-prep.md), подготовить workload и decision worksheet. Для исторического контекста используй GFS/SOSP, HDFS, Ceph/OSDI и S3 launch sources в главах.

## Сессия

1. Написать на доске NFR трех jobs: 1 PB sequential scan, image service с миллиардом объектов, database с 5 ms p99 random write.
2. Разобрать interface semantics до product names: path vs key, atomic unit, lock, listing, range read, replace.
3. Нарисовать HDFS client → NameNode → DataNode pipeline, Ceph client → CRUSH → PG/OSD, SeaweedFS S3 → Filer → volume, Ozone key → OM → SCM/container/DataNode и Lustre path → MDT → striped OST data path.
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
- На бумаге сравнить Ozone OM/SCM/DataNode layers и HDFS NameNode/DataNode: что вынесено в отдельный control plane и какой Hadoop API остаётся доступен?
- Прочитать Lustre DNE/striping и объяснить, почему файл может обращаться одновременно к MDT и нескольким OST, а S3 `GET key` описывает другой contract.
- На конкретном RustFS release сверить documented S3 feature matrix, erasure-set geometry, node-failure behavior, healing и upgrade path; пометить неподтверждённое как PoC risk.

## Exit criteria

Студент может провести 10-минутную защиту: один primary design, две rejected alternatives из разных классов (например, Lustre vs Ozone), contract + data path, failure map, capacity/recovery assumptions, security boundary, cost model, PoC plan и restore evidence. Он не смешивает Lustre OST и S3 object, `ofs://` и POSIX mount, либо физическую EC redundancy и application-level transaction.
