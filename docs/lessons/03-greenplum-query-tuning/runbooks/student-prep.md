# Student Prep: Урок 03 (Greenplum 6.25)

## До Занятия

1. Docker Desktop запущен.
2. Поднять стенд Урока 03:

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
```

На x86_64:

```bash
GREENPLUM_625_IMAGE=andruche/greenplum:6.25.3-slim-amd64 \
  python3 mentor-lab.py up greenplum-625
```

3. Открыть workbook и презентацию.

## Self-Service Команды

```bash
python3 mentor-lab.py student greenplum-query-tuning bootstrap --platform macos
python3 mentor-lab.py runbook greenplum-query-tuning simple
python3 mentor-lab.py academy greenplum-query-tuning start --student <имя> --dry-run
python3 mentor-lab.py psql greenplum-625
```

## Что Иметь Под Рукой

- терминал;
- psql к `greenplum-625`;
- место под before/after EXPLAIN (включая `SET optimizer`).
