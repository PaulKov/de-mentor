# Release Notes

## Lesson 02 MVP: Partitioning, Statistics And Incremental Loads

Этот релиз добавляет второй урок Greenplum Academy как отдельный учебный маршрут `greenplum-partitioning` поверх того же Docker-стенда `greenplum`.

### Новые команды

```bash
python3 mentor-lab.py lesson greenplum-partitioning
python3 mentor-lab.py runbook greenplum-partitioning simple
python3 mentor-lab.py runbook greenplum-partitioning deep
python3 mentor-lab.py runbook greenplum-partitioning homework
python3 mentor-lab.py student greenplum-partitioning bootstrap --platform macos
python3 mentor-lab.py student greenplum-partitioning homework
python3 mentor-lab.py academy greenplum-partitioning start --student Иван --dry-run
```

### Что Добавлено

- Каталог Lesson 02: partition pruning, retention, statistics after load, late-arriving facts, idempotency, AOCO partitions.
- Markdown runbooks: упрощенный маршрут, deep-dive маршрут и homework route.
- Workbook, mentor guide, homework, rubric и cheat-sheet.
- SQL-lab `labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql`.
- Academy Control Plane для Lesson 02 с отдельным deck/workbook/homework/sql artifacts.
- Route resolver: учебный маршрут `greenplum-partitioning` использует физический lab `greenplum`.

### Как Проверять

```bash
python3 -m pytest tests -q
python3 -m compileall -q src mentor-lab.py
python3 mentor-lab.py runbook greenplum-partitioning simple
python3 mentor-lab.py runbook greenplum-partitioning deep
python3 mentor-lab.py runbook greenplum-partitioning homework
python3 mentor-lab.py check greenplum
```

## Academy Self-Service v1

Этот релиз добавляет единый self-service маршрут для проведения первого урока Greenplum Academy.

### Новые команды

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py academy greenplum start --student Иван
python3 mentor-lab.py academy greenplum start --student Иван --dry-run
python3 mentor-lab.py academy greenplum start --student Иван --skip-lab
python3 mentor-lab.py student greenplum bootstrap --platform macos
python3 mentor-lab.py student greenplum bootstrap --platform windows
python3 mentor-lab.py student greenplum homework
```

### Что автоматизирует

- Создание `session.json` для Academy Control Plane.
- Экспорт session state в Nuxt portal repo.
- Подготовку команд запуска Greenplum, runbook и portal.
- Отдельный student-facing bootstrap для macOS, Windows и Linux.
- Видимый quality guard: `SLOC <= 400` и `avg clustering <= 0.180`.

### Как проверять

```bash
python3 -m pytest tests -q
python3 -m compileall -q src mentor-lab.py
python3 mentor-lab.py academy greenplum start --student Иван --dry-run
python3 mentor-lab.py student greenplum bootstrap --platform windows
python3 mentor-lab.py student greenplum homework
```
