# Deep dives — distributed storage

Прочитай общую storage модель, затем три product-specific главы. В конце каждой главы есть commands/code, failure cases и senior exercise. Версии и API поведение меняются; проверяй документы своего release.

## Рекомендуемый порядок

1. [Общие модели и data paths](distributed-storage-internals.md) — block/file/object, history, metadata, replication и EC.
2. [HDFS internals](hdfs-internals.md) — Hadoop filesystem, NameNode namespace, DataNode blocks, HA/federation и striped EC.
3. [Ceph internals](ceph-internals.md) — RADOS, CRUSH, PG/OSD, RGW, RBD и CephFS как отдельные интерфейсы над общим storage substrate.
4. [SeaweedFS internals](seaweedfs-internals.md) — Master, volume/needle layout, Filer metadata, S3 gateway и tiering.
5. [Выбор продуктов и deployment](products-and-deployment.md) — сравнение с Apache Ozone, Lustre, RustFS, cloud services, PoC и operational design.

## Быстрая карта: что решает каждый

| Система | Внешний контракт | Ключевая внутренняя идея | Архитектурный вопрос senior-уровня |
| --- | --- | --- | --- |
| HDFS | Hadoop filesystem path | NameNode metadata отдельно от data blocks, клиент стримит блоки через DataNode pipeline | масштабируется ли namespace и как восстановить HA без потери edits? |
| Ceph | RADOS plus RBD / CephFS / RGW | clients вычисляют PG/OSD placement по cluster map + CRUSH | выдерживает ли сеть, OSD topology и свободная емкость backfill/recovery? |
| SeaweedFS | blob ID, Filer paths, S3 gateway | master учитывает volumes, а не каждый blob; volume stores append-oriented needles | достаточно ли durable Filer metadata и как объемы обслуживаются/ремонтируются? |
| Apache Ozone | S3 + Hadoop `ofs://` | OM namespace отдельно от SCM container/block management | выдерживает ли metadata control plane key cardinality и нужна ли совместимость с Hadoop APIs? |
| Lustre | POSIX parallel filesystem | MDT владеет metadata/layout, clients разносят I/O по OSTs | как настроены stripe layout, MDT scale, fabric и lifecycle kernel clients? |
| RustFS | S3-first object API | object shards distributed across erasure sets | какие API/failure/upgrade properties подтверждены на конкретной версии, а не предполагаются по совместимости? |

Ozone, Lustre и RustFS намеренно идут в product comparison, а не выдаются за эквивалентные замены HDFS, Ceph или SeaweedFS. Их internals полезны для выбора, но лабораторный Compose этого урока поднимает SeaweedFS только в single-node учебной конфигурации.
