# Decision matrix — распределённые file/object storage

Сначала зафиксируй workload и hard constraints, затем оцени кандидатов. Шкала не заменяет PoC: `++` естественный fit, `+` возможен при проверке, `~` компромисс, `−` плохой fit.

| Workload / requirement | HDFS | Ceph | SeaweedFS | MinIO AIStor | AWS S3 | GCS | Azure ADLS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hadoop batch, large streaming scans on-prem | ++ | + | ~ | ~ | + | + | + |
| AWS-native lakehouse / managed operations | − | − | ~ | ~ | ++ | − | − |
| GCP analytics with object API and HNS option | − | − | ~ | ~ | − | ++ | − |
| Azure analytics requiring ACLs + Blob/DFS APIs | − | − | ~ | ~ | − | − | ++ |
| On-prem object API, self-managed operations | ~ | ++ | ++ | ++ | − | − | − |
| One substrate for block + file + object | − | ++ | + | − | − | ~ | ~ |
| Millions/billions of small blobs / media | ~ | + | ++ | + | ++ | ++ | ++ |
| Generic low-latency random-write database disk | ~ | ++ (RBD) | − | − | − | − | − |
| POSIX-like shared namespace, rename/locks | + | ++ (CephFS) | + (Filer/FUSE; verify semantics) | − | − | + (HNS-specific) | ++ (HNS) |
| Minimal storage operations team | − | − | ~ | ~ | ++ | ++ | ++ |

## Systems omitted by the first matrix: compare by interface, not name

The table below is a focused shortlist for HDFS, Ozone, Lustre, Ceph, SeaweedFS, and RustFS. Ratings are workload hypotheses; `++` means a native design match, not a performance guarantee.

| Workload / contract | HDFS | Apache Ozone | Lustre | Ceph | SeaweedFS | RustFS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Hadoop batch reading large files | ++ | ++ (`ofs://`, Hadoop ecosystem) | ~ (POSIX path, client integration needed) | + (CephFS/RGW choice changes semantics) | + (Hadoop client options; verify) | + (S3 clients; verify engine FileIO) |
| Hadoop-native object lakehouse | ~ (filesystem contract) | ++ (S3 + `ofs://`) | − | + (RGW S3) | + (S3) | + (S3; verify used Iceberg operations) |
| HPC parallel POSIX I/O | − | − | ++ | + (CephFS, benchmark workload) | − | − |
| VM/database block device | − | − | − | ++ (RBD) | − | − |
| Shared POSIX namespace | + (Hadoop FS semantics) | − (`ofs://` is Hadoop FS API, not a kernel POSIX mount) | ++ | ++ (CephFS) | + (Filer/FUSE; validate semantics) | − |
| On-prem S3 endpoint | − | ++ (S3 Gateway) | − | ++ (RGW) | ++ (S3 gateway) | ++ (S3-first) |
| Billions of keys with Hadoop scale-out | ~ (NameNode namespace sizing/federation) | ++ (primary design target; still PoC) | ~ (metadata layout and DNE) | + (RGW metadata/pool sizing) | + (volume-level master + external filer metadata) | + (check current implementation limits and metadata behavior) |
| Small-file or metadata-heavy namespace | −/`~` (file count drives NameNode memory) | + (small-file features; benchmark) | ~ (MDT/DNE/DOM choices) | ~ (metadata servers/pools; benchmark) | ++ (blob packing plus pluggable Filer store) | ~ (object API does not imply cheap LIST/HEAD at every scale) |
| Minimal platform operations team | − | − | − | − | ~ | ~ |

### Keep the interfaces straight

- HDFS and Lustre both present file paths, but their clients, write models and target workloads differ. Lustre is a parallel POSIX filesystem; HDFS is a Hadoop filesystem for large distributed datasets.
- Apache Ozone is an object store with Hadoop-oriented `ofs://` and an S3 Gateway. `ofs://` does not by itself provide POSIX kernel mount semantics.
- Lustre OST means Object Storage Target inside the filesystem architecture. It is not an S3 endpoint and does not make Lustre an object-storage service.
- Ceph's shared RADOS backend supports separate client contracts: RBD is block, CephFS is file, and RGW is object. Select and benchmark the correct interface.
- SeaweedFS exposes blob, Filer/path and S3 surfaces; operational durability spans both volume bytes and Filer metadata.
- RustFS is an S3-first project. Validate exact S3 calls, erasure-set placement, node-failure tolerance, repair, upgrades, observability, and support for the precise release; do not score it as a file or block system.

Official architecture starting points: [HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html), [Ozone](https://ozone.hadoop.apache.org/docs/core-concepts/architecture/overview/), [Lustre](https://wiki.lustre.org/Introduction_to_Lustre), [Ceph](https://docs.ceph.com/en/latest/architecture/), [SeaweedFS](https://github.com/seaweedfs/seaweedfs/blob/master/README.md), [RustFS](https://github.com/rustfs/rustfs/blob/main/ARCHITECTURE.md).

## Reading the table

- Cloud managed services reduce infrastructure operations but lock the workload into identity, pricing, regional topology and API-specific features.
- “On-prem object API” has choices with different internals: Ceph's RADOS and placement groups, SeaweedFS's volume/Filer architecture, MinIO's S3-focused erasure sets. Compare operating model and semantics, not only SDK compatibility.
- HDFS may win on a mature Hadoop cluster and lose for a lakehouse where independent engines need elastic shared storage. Cloud object store is not automatically faster or cheaper after request costs, network and small files.
- GCS HNS and Azure HNS/ADLS are explicit namespace options, not generic properties of all object stores. Confirm feature limitations before creating buckets/accounts or migrating data.
- Low-latency random writes to databases usually call for block devices/local NVMe or a storage-native database design; object APIs are not a general-purpose replacement.

## Decision worksheet

| Dimension | Required value | Candidate behavior / evidence | Gate |
| --- | --- | --- | --- |
| APIs and clients |  |  |  |
| Read/write latency, throughput, concurrency |  |  |  |
| Object/file count and size histogram |  |  |  |
| Consistency and atomicity |  |  |  |
| Failure domains and availability |  |  |  |
| Data durability, backup, RPO/RTO |  |  |  |
| Capacity efficiency/headroom |  |  |  |
| Security / encryption / audit / compliance |  |  |  |
| TCO including requests, egress, support and operations |  |  |  |
| Team's on-call capabilities and upgrade window |  |  |  |
| Exit / migration / data export |  |  |  |

## Make the PoC falsifiable

Before deployment choose a workload trace and pass thresholds. At minimum:

1. Upload/read/delete one object, multipart object and large range read through the exact production SDK/connector.
2. Test immediate GET/LIST after successful PUT and overwrite; repeat concurrent same-key writes.
3. Test 100 KB, 1 MB, 128 MB and multi-GB object classes with realistic fan-out, prefixes and parallelism.
4. Measure p50/p95/p99 latency, errors/retries, aggregate throughput, CPU, network, request cost and metadata rate.
5. Simulate one failure in each intended failure domain; record read/write availability and repair time.
6. Restore namespace/config/data in isolation and validate checksums + application-level reads.
7. Check lifecycle/retention/security policy using test identities; ensure operator and workload roles are separate.

Записывай тестовую версию и конфигурацию. Повторный benchmark после upgrade может изменить результат даже при прежнем API.
