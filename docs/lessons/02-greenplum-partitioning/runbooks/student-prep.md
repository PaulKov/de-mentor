# Подготовка Ученика К Lesson 02

## Что Установить

- Docker Desktop на macOS/Windows или Docker Engine на Linux.
- Git.
- Python 3.9+.
- Репозиторий `de-mentor`.

## Проверка macOS/Linux

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py readiness greenplum --platform macos
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py student greenplum-partitioning homework
```

Для Linux замени platform:

```bash
python3 mentor-lab.py readiness greenplum --platform linux
```

## Проверка Windows

```powershell
py mentor-lab.py doctor --full
py mentor-lab.py readiness greenplum --platform windows
py mentor-lab.py up greenplum
py mentor-lab.py check greenplum
py mentor-lab.py student greenplum-partitioning homework
```

## Что Принести

- результат `check greenplum`;
- вопрос по `partition pruning`;
- вопрос по statistics или `ANALYZE`;
- если есть домашка Lesson 01, файл с `EXPLAIN` и выводом `gp_segment_id`.

Workbook: [student-workbook.md](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/student-workbook.md).
