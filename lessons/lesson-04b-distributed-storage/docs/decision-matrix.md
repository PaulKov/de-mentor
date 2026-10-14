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
