# Подготовка Ученика К Lesson 03

## Что Установить

- Docker Desktop на macOS/Windows или Docker Engine на Linux.
- Git.
- Python 3.9+.
- Репозиторий `de-mentor`.

## Проверка macOS/Linux

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py readiness greenplum-625 --platform macos
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py student greenplum-query-tuning homework
```

Для Linux замени platform:

```bash
python3 mentor-lab.py readiness greenplum-625 --platform linux
```

На x86_64:

```bash
GREENPLUM_625_IMAGE=andruche/greenplum:6.25.3-slim-amd64 \
  python3 mentor-lab.py up greenplum-625
```

## Проверка Windows

```powershell
py mentor-lab.py doctor --full
py mentor-lab.py readiness greenplum-625 --platform windows
py mentor-lab.py up greenplum-625
py mentor-lab.py seed greenplum-625 --profile lesson03
py mentor-lab.py check greenplum-625
py mentor-lab.py student greenplum-query-tuning homework
```

## Что Принести

- результат `check greenplum-625` (БД `mentor`, схема `lesson03`);
- вопрос по `SET optimizer` (session scope) или ORCA vs Legacy;
- вопрос по `pg_stats` / estimate fail;
- если есть домашка Lesson 02 — файл с pruning/`ANALYZE` evidence.

Workbook: [student-workbook.md](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/03-greenplum-query-tuning/student-workbook.md).
