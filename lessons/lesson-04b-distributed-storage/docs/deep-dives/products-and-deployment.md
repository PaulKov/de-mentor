# Deep Dive: выбор продукта, внедрение и эксплуатация

Storage product selection начинается с workload и operating model. Сравнивай конкретные версии и editions: API, failure behavior, license/support, compatibility и pricing меняются быстрее, чем базовые понятия.

## 1. Сравнительная характеристика representative systems

| Система | Primary contract / substrate | Особенная сторона | Хороший fit | Плохой fit / проверить |
| --- | --- | --- | --- | --- |
| **HDFS** | distributed filesystem, blocks + NameNode/DataNodes | streaming throughput, compute locality, Hadoop native semantics | on-prem Hadoop/Spark batch, большие scan-heavy files | мелкие объекты, public-cloud elastic access, много независимых namespaces, случайные overwrite |
| **Ceph** | RADOS + CRUSH; RBD block, CephFS, RGW S3/Swift | единый self-managed substrate для block/file/object, placement policy поверх heterogenous OSDs | private cloud, Kubernetes VM volumes + file share + S3 endpoint в одном fleet | малый ops team, нет места для recovery reserve, низкая допустимая сложность cluster-wide debugging |
| **SeaweedFS** | volume/blob store + Master + Filer metadata + gateways | master отслеживает volumes, append-oriented blobs, много файлов, filer metadata backend выбирается отдельно | self-hosted file/object service, media, edge/cloud tiering, большое число blobs | команды, которым нужны полностью одинаковые POSIX/S3 semantics; без отдельной экспертизы metadata DB/maintenance |
| **MinIO AIStor** | S3 API object service, erasure sets | object placement/sharding и erasure-code model напрямую сфокусированы на S3 | S3-native on-prem appliance/software, когда product edition/support и API subset прошли PoC | полноценная shared POSIX filesystem или multi-protocol block/file storage; необходимо отдельно оценивать текущую edition, license, support и feature matrix |
| **Amazon S3** | managed object service, bucket/key + versions/classes/lifecycle | AWS-managed scaling/operations, broad ecosystem, documented strong object read-after-write consistency | AWS-native lakehouse, backups, archives, artifacts, durable static blobs | local POSIX/low-latency random I/O, cloud-independent deployments, uncontrolled request/egress cost, multi-key transaction |
| **Google Cloud Storage** | managed object store; flat namespace or optional HNS buckets | strong global consistency; HNS can add folder resources/atomic folder rename for supported workloads | GCP analytics/AI, bulk objects, HNS-aware file-oriented jobs | relying on every flat-namespace feature in HNS buckets; check documented incompatibilities and migration is creation-time choice |
| **Azure Blob / ADLS Gen2** | Blob API with optional hierarchical namespace / Data Lake APIs | same HNS data can be reached through Blob and DFS APIs, with first-class directories and POSIX ACLs | Azure analytics and Hadoop ecosystems needing both object and directory operations | assuming all combinations of account features, ACLs, private endpoints and services are interchangeable; map support matrix by HNS mode |

### Product source notes

- HDFS separates NameNode namespace/block map from DataNode data; see [HDFS Architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html).
- Ceph unifies RADOS under [CephFS, RBD and RGW](https://docs.ceph.com/en/latest/architecture/); placement policies are [CRUSH rules](https://docs.ceph.com/en/latest/rados/operations/crush-map/).
- SeaweedFS exposes master, volume server, filer and S3 surfaces; see [upstream architecture](https://github.com/seaweedfs/seaweedfs/blob/master/README.md) and [S3 API mapping](https://github.com/seaweedfs/seaweedfs/wiki/Amazon-S3-API).
- [MinIO AIStor erasure coding](https://docs.min.io/aistor/operations/core-concepts/erasure-coding/) documents erasure sets, data/parity shards and quorum behavior; AIStor docs describe that edition. Verify the product/edition/version actually under evaluation.
- AWS lists object uses, storage classes and [strong read-after-write consistency for object PUT/DELETE](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html); it explicitly notes no atomic updates across keys.
- GCS documents [strongly consistent object/list operations](https://docs.cloud.google.com/storage/docs/consistency) and [HNS folders/atomic rename](https://docs.cloud.google.com/storage/docs/folders-overview); HNS differs from simulated prefix folders.
- Azure explains how [Blob and Data Lake APIs share HNS data, first-class directories and ACL enforcement](https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-multi-protocol-access).

These are not benchmark claims. A product's marketing phrase “S3-compatible” does not certify your used operations, semantics, performance or failure behavior.

## 2. Capability checklist for S3 compatibility

Build a table with client version × server version × used feature. Include at least:

| Surface | Probes |
| --- | --- |
| Authentication | SigV4 variants, temporary credentials, STS, IAM/policy conditions, path-style/virtual-host addressing |
| Namespace | bucket create/list/delete, key encoding, delimiter/prefix pagination, versioned listing |
| Writes | multipart initiate/upload/complete/abort, conditional `If-Match`/`If-None-Match`, server-side copy, replace same key |
| Reads | HEAD, GET range, version ID, checksum headers, metadata/tags, URL escaping |
| Durability/visibility | response ack meaning, GET after PUT, LIST after PUT, concurrent PUT, concurrent delete |
| Governance | versioning, retention/Object Lock, lifecycle expiration, replication, encryption/key rotation |
| Operations | throttling, retryable status, request IDs, metrics, audit logs, restore and bulk deletion |

Для каждого probe фиксируй expected HTTP/API result, actual result, retry policy, side effect, service version, config и evidence. Для Iceberg/Flink/Spark добавь table format writer requirements: atomic/conditional operations if needed, catalog credential vending, range reads, rename assumptions and checkpoint recovery. Test **тот SDK/connector**, который пойдёт в production; generic AWS CLI smoke test — только первый gate.

## 3. Когда filesystem mount к object API помогает и когда врёт

Mounting a bucket is useful for legacy applications that enumerate/read mostly immutable files, batch workloads, data science exploration or low-duty-cycle pipelines. It can improve integration by presenting paths. It can hurt when application expects:

- `rename` is metadata-only/atomic; object stores may implement copy then delete and the operation may be O(bytes) or O(objects);
- advisory locks, leases, `flock`, durable `fsync` or close-to-open consistency;
- millisecond `stat()` on billions of paths without request cost;
- random byte overwrite and low-latency sync writes;
- one transaction spanning several filenames;
- offline local behavior during cloud/network outage.

Adapters add local cache, writeback, consistency rules and failure modes. Record mount options, cache invalidation, maximum concurrency, multipart threshold, cleanup behavior and whether two clients can write the same key. For Spark/Trino/Flink, prefer their native object-store FileIO/connectors where supported; for Iceberg use the engine's tested FileIO/catalog implementation rather than assuming generic POSIX mount semantics.

## 4. On-prem: design around failure and repair, not just capacity

### Placement and hardware

1. Define failure domains honestly: disk, host, rack, power domain, top-of-rack switch, room, site. Map each one into replica/EC policy.
2. Choose data vs metadata media separately where product allows it. Namespace databases, OSD journals/WAL, RocksDB metadata and object bytes have different latency/write-amplification needs.
3. Size east-west network for normal client traffic **and** rebalance/backfill/repair. Reserve bandwidth for foreground p99; measure inter-rack, not only host-local throughput.
4. Design for headroom at failure threshold. A cluster with 70% raw utilization may have much less than 30% usable headroom after an uneven failure domain or EC placement constraint.
5. Use drive health, checksums/bitrot detection, scrub cadence and degraded-object inventory. A green TCP probe doesn't prove bytes are correct.

### Control plane and operations

- Keep quorum members, gateways, metadata databases and bulk bytes on explicit HA/backup plans. Do not call a service HA because its data plane has 3 copies.
- Upgrade through supported version hops; observe protocol/map changes and mixed-version periods. Test rollback and feature compatibility, not only a clean install.
- Throttle recovery, compaction, erasure encoding and lifecycle deletion. Rehearse a device loss at production scale in a maintenance window and record recovery time/data movement.
- Use redundant power/network, rack-aware placement and N+1 capacity. Keep spare drives/controllers and a tested operator escalation path.
- Monitor percent-full by pool/erasure set, degraded objects/PGs, under-replicated blocks, repair backlog/age, scrub errors, metadata p99, request p95/p99/5xx, slow disks, gateway saturation and network retransmits.
- Back up namespace/metadata/config/identity separately from data; automate a restore to a separate cluster and verify application-level reads. Define RPO/RTO separately for bytes and metadata.

Ceph exposes state transitions such as OSD up/in, PG active/clean/degraded and recovery/backfill; HDFS reports missing/under-replicated blocks; SeaweedFS requires volume, filer metadata and background maintenance visibility. Learn each system's native health model; a synthetic S3 `PUT/GET` doesn't expose all latent degraded states.

## 5. Cloud: managed infrastructure moves the work; it does not remove architecture

Cloud object store outsources disk/node repair, placement machinery and service availability to provider. The workload still owns:

- bucket/account/region and data-class selection;
- identity and resource policy, least privilege, key management, public-access block, audit;
- request cost, storage-class minimum duration/restore fee, retrieval latency and lifecycle;
- cross-AZ/region replication, versioning/retention, restore and legal requirements;
- transfer/egress, private endpoint routing, DNS, bandwidth and cross-account access;
- object-size/key distribution, listing strategy, concurrency/backoff and client-side caching;
- data migration, exit plan, export time, API-specific features and cost forecast.

Calculate total cost of ownership as a workload ledger, not `$ per GB-month` alone:

```text
TCO ≈ stored GB-month by class
    + PUT/GET/LIST/metadata request counts
    + retrieval / early-delete / restore charges
    + cross-AZ/region and internet egress
    + encryption/KMS calls + network endpoints
    + compute idle time waiting for storage
    + operational headcount / support tier / migration reserve
```

Cloud durability cannot compensate for a compromised key, accidental authorized delete, wrong lifecycle rule, catalog loss or untested restore. Versioning and Object Lock are not backups of application metadata or policies.

## 6. Hybrid and migration traps

Hybrid is valuable when data capture is on-prem but analytics/cloud ML is bursty, or a region has residency/connectivity constraints. It also introduces WAN latency/bandwidth, dual IAM, cache invalidation, egress cost, duplicate lifecycle policies and metadata divergence. Choose a single source of truth per dataset and a one-way or explicitly conflict-resolved sync direction.

Migration checklist:

1. Inventory client verbs and semantic expectations; record object/file count, size histogram, versions, tags, ACLs, legal holds and checksums.
2. Classify data by retention and access path; map keys/prefixes, account/namespace, encryption and ownership.
3. Benchmark `LIST`, `HEAD`, range GET, multipart and concurrent writes with production SDKs; run repeatable workload at realistic latency.
4. Copy to a new namespace without deleting source. Use checksums or provider-documented integrity primitives; compare counts, bytes, versions and ACL/policy results.
5. Dual-read/shadow jobs; avoid active dual-writes unless conflict, idempotency and reconciliation are specified.
6. Cut over catalog/client endpoint independently of bucket copy; verify Iceberg snapshot metadata and Flink checkpoint/restore references.
7. Retain rollback window, then apply tested retention cleanup. Never remove old data merely because a path listing looks complete.

## 7. Senior architecture exercises

### Case A — on-prem petabyte archive

Compare Ceph EC pool, SeaweedFS blob volumes, HDFS and appliance alternatives. Requirements: 5 PB logical, 2 sites, archive restore in hours, new writes daily, 10 TB/day ingest. Deliver rough disks/racks/network, replication/EC, metadata backup, expected restore throughput, utilization ceiling and on-call plan. Explicitly separate same-site media failure from site disaster recovery.

### Case B — cloud lakehouse

Two Flink jobs, Spark compaction, Trino readers, one Iceberg REST catalog and GCS/AWS/Azure object store. Define credentials per engine, object key ownership, failure handling if catalog or storage is down, snapshot maintenance, cloud cost counters and cross-engine compatibility matrix. Identify where storage consistency stops and Iceberg commit semantics begin.

### Case C — billions of small media objects

Compare SeaweedFS, object store plus CDN, file storage, database/blob hybrid. Include object size histogram, hot/cold tiers, lookup index, upload concurrency, cache invalidation, metadata backend scale and cleanup correctness. State which service owns media metadata versus object payload.

### Defense standard

Senior answer names alternatives rejected, assumptions, testable unknowns, failure-domain maps, p99 and RPO/RTO targets, exact recovery test, operations staffing, legal/security requirements and an exit plan. “Product X is scalable” is not evidence.
