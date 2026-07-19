# Lab: Greenplum 6.25 Academy (Уроки 01–03)

Единый self-service стенд для всей Greenplum Academy.

## Требования

- Docker Desktop / Docker Engine.
- Python 3.9+.
- Файл `mentor-lab.py` из корня репозитория.

## Паспорт Docker-Кластера

| Параметр | Значение |
| --- | --- |
| CLI lab names | `greenplum` **или** `greenplum-625` (один compose) |
| Docker service | `greenplum-625` |
| Image | `andruche/greenplum:6.25.3-slim-arm64` (default) / `…-amd64` |
| Database | `mentor` (CLI создаёт из maintenance `postgres`) |
| User | `gpadmin` |
| Published port | `15436:5432` |
| Examples / seed | `/mentor-lab/examples`, `/mentor-lab/seed` |
| GPHOME | `/usr/local/gpdb` |

Фактическая topology внутри Greenplum (типичный slim-образ):

- `1 coordinator/master`: `content = -1`;
- `2 primary segments`: `content = 0` и `content = 1`;
- `0 mirror segments`: HA отключен, чтобы стенд был легким;
- `1 segment host`: все instances в одном Docker container.

CPU/RAM limits в `docker-compose.yml` **не заданы** — контейнер использует лимиты Docker Desktop/Engine.

## Быстрый старт

```bash
python3 mentor-lab.py up greenplum
# эквивалентно: python3 mentor-lab.py up greenplum-625

GREENPLUM_625_IMAGE=andruche/greenplum:6.25.3-slim-amd64 \
  python3 mentor-lab.py up greenplum

python3 mentor-lab.py seed greenplum --profile academy
python3 mentor-lab.py check greenplum
python3 mentor-lab.py psql greenplum
```

По урокам:

```bash
python3 mentor-lab.py seed greenplum --profile lesson01
python3 mentor-lab.py seed greenplum --profile lesson02
python3 mentor-lab.py seed greenplum --profile lesson03
```

## Подключение

```bash
python3 mentor-lab.py psql greenplum
psql "host=127.0.0.1 port=15436 dbname=mentor user=gpadmin"
```

## SQL Labs

```sql
\conninfo
\i /mentor-lab/examples/cluster-inspection.sql
\i /mentor-lab/examples/cluster-monitoring.sql
\i /mentor-lab/examples/storage-and-partitioning.sql
\i /mentor-lab/examples/partitioning-strategies.sql
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
\i /mentor-lab/examples/lesson03-homework-seed.sql
\i /mentor-lab/examples/lesson03-class-demo.sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
```

Проверка topology / disk:

```sql
SELECT content, role, preferred_role, mode, status, hostname, port
FROM gp_segment_configuration
ORDER BY content, role;

SELECT dfsegment, dfhostname, pg_size_pretty(dfspace::bigint * 1024) AS free_space
FROM gp_toolkit.gp_disk_free
ORDER BY dfsegment;
```

## GP6 dialect notes

- Storage: `appendonly=true` (не GP7 `appendoptimized`)
- Partitions: classic `PARTITION BY RANGE/LIST` + `START/END` / `VALUES`
- Catalog: `pg_partitions` (classic GP6; `gp_toolkit.gp_partitions` may be absent on slim images)
- Optimizer: `SET optimizer = on|off` (Legacy vs GPORCA)

## Monitoring notes

Use `gp_segment_id` in skew checks and `gpstate -s` outside psql as gpadmin.

## Остановка

```bash
python3 mentor-lab.py down greenplum
python3 mentor-lab.py reset greenplum
```
