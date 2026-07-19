# Release Notes

## Урок 03: Декомпозиция и тюнинг тяжёлых запросов в MPP

Этот релиз добавляет третий урок Greenplum Academy как отдельный учебный маршрут `greenplum-query-tuning` на physical lab `greenplum-625` (Greenplum 6.25.3).

### Новые команды

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py lesson greenplum-query-tuning
python3 mentor-lab.py runbook greenplum-query-tuning simple
python3 mentor-lab.py runbook greenplum-query-tuning deep
python3 mentor-lab.py runbook greenplum-query-tuning homework
python3 mentor-lab.py student greenplum-query-tuning bootstrap --platform macos
python3 mentor-lab.py student greenplum-query-tuning homework
python3 mentor-lab.py academy greenplum-query-tuning start --student Иван --dry-run
python3 scripts/build_lesson03_pptx.py
```

### Что Добавлено

- Каталог Урока 03: стадии оптимизатора, Legacy vs GPORCA, layered EXPLAIN, pg_statistic internals, Heap/AO/AOCO, TEMP/spill, OLAP rewrite.
- Markdown runbooks: simple, deep-dive, homework.
- Workbook, mentor guide, homework, rubric, cheat-sheet и 3 deep-dive документа.
- Отдельный physical lab `greenplum-625` на Greenplum 6.25.3 (`andruche/greenplum`).
- SQL-lab `labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql`.
- Demo Legacy vs GPORCA: `labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql`.
- PPTX `artifacts/greenplum-query-tuning-theory.pptx` (30 слайдов) + declarative sources.
- Academy Control Plane и Lesson Release Manifest для Урока 03.
- Deep-dive `optimizer-legacy-vs-orca.md`.

### Как Проверять

```bash
python3 -m pytest tests/test_lesson_03_query_tuning.py tests/test_presentation_artifact.py -q
python3 mentor-lab.py runbook greenplum-query-tuning simple
python3 mentor-lab.py lesson-release greenplum-query-tuning verify
```

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
