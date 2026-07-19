# Lab: Greenplum 6.25 (Урок 03)

Self-service стенд для декомпозиции тяжёлых OLAP и сравнения **Legacy Postgres planner** vs **GPORCA**.

| Поле | Значение |
| --- | --- |
| Image (Apple Silicon default) | `andruche/greenplum:6.25.3-slim-arm64` |
| Image (x86_64) | `andruche/greenplum:6.25.3-slim-amd64` |
| Lab name | `greenplum-625` |
| Port | `15436 → 5432` |
| User / DB | `gpadmin` / `postgres` |
| GPHOME | `/usr/local/gpdb` |

## Быстрый старт

```bash
# Apple Silicon (default)
python3 mentor-lab.py up greenplum-625

# x86_64 / CI
GREENPLUM_625_IMAGE=andruche/greenplum:6.25.3-slim-amd64 python3 mentor-lab.py up greenplum-625

python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py psql greenplum-625
```

В psql:

```sql
\i /mentor-lab/examples/lesson03-olap-decomposition-tuning.sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
```

## Ученический маршрут Урока 03

```bash
python3 mentor-lab.py student greenplum-query-tuning bootstrap --platform macos
python3 mentor-lab.py runbook greenplum-query-tuning simple
python3 mentor-lab.py academy greenplum-query-tuning start --student Иван --dry-run
```

## Optimizer switch

```sql
SET optimizer = on;   -- GPORCA
SET optimizer = off;  -- legacy Postgres planner
SHOW optimizer;
```

## Остановка

```bash
python3 mentor-lab.py down greenplum-625
# полный сброс контейнера
python3 mentor-lab.py reset greenplum-625
```
