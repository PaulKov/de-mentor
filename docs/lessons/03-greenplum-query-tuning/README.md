# Урок 03: Декомпозиция и тюнинг тяжёлых запросов в MPP

Третий урок Greenplum Academy. Стенд — **Greenplum 6.25.3** (`greenplum-625`), чтобы демо Legacy planner vs GPORCA было воспроизводимо.

Главная идея: Senior/Principal разбирает оптимизацию Greenplum по стадиям, сравнивает два оптимизатора, читает статистику до catalog/файлов, выбирает storage и декомпозирует тяжёлый OLAP через `TEMP`.

**GUC** (*Grand Unified Configuration*) — параметр сервера PostgreSQL/Greenplum. GUC `optimizer` выбирает, кто строит распределённый plan: `on` → GPORCA, `off` → Legacy. Полный словарь — в начале презентации и в [deep-dive](deep-dives/optimizer-legacy-vs-orca.md).

## Результат Урока

После урока ученик должен уметь:

- расшифровывать GUC / QD / QE / Motion / ORCA до чтения плана;
- объяснить pipeline `parse → rewrite → optimize → dispatch → execute` на дереве EXPLAIN;
- сравнить **Legacy Postgres planner** и **GPORCA**: плюсы/минусы, где какой эффективен;
- разобрать сложный `EXPLAIN` слоями: optimizer → Motion → join → estimates → scan;
- читать `pg_stats` / `pg_statistic` и связать slots со selectivity;
- выбрать Heap / AO / AOCO на GP 6.25 (`appendonly`) и объяснить физическую раскладку;
- использовать `TEMP` как physical stage с `ANALYZE` и distribution.

Вне scope: полноценный WLM и production RCA → Урок 04.

## Self-Service Стенд (GP 6.25)

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py psql greenplum-625
```

x86_64:

```bash
GREENPLUM_625_IMAGE=andruche/greenplum:6.25.3-slim-amd64 \
  python3 mentor-lab.py up greenplum-625
```

## Маршруты

| Маршрут | Когда использовать | Команда |
| --- | --- | --- |
| Упрощённый 60 минут | основной урок | `python3 mentor-lab.py runbook greenplum-query-tuning simple` |
| Deep-dive 90-120 минут | Principal internals | `python3 mentor-lab.py runbook greenplum-query-tuning deep` |
| Домашка 60-90 минут | самостоятельная работа | `python3 mentor-lab.py runbook greenplum-query-tuning homework` |

Учебный маршрут:

```bash
python3 mentor-lab.py academy greenplum-query-tuning start --student Иван --dry-run
python3 mentor-lab.py student greenplum-query-tuning bootstrap --platform macos
python3 mentor-lab.py student greenplum-query-tuning homework
```

## Практический SQL-Lab

- [lesson03-olap-decomposition-tuning.sql](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql)
- [lesson03-optimizer-legacy-vs-orca.sql](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql)

```sql
\i /mentor-lab/examples/lesson03-olap-decomposition-tuning.sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
SET optimizer = on;   -- GPORCA
SET optimizer = off;  -- Legacy
```

## Материалы

- [Презентация в Google Slides](https://docs.google.com/presentation/d/1FtZysVPcsq5BUmAhJ6FqaIt8fpIhPXd9cKC_C6TMdwM/edit?usp=sharing)
- [PowerPoint](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-query-tuning-theory.pptx)
- [Manifest](lesson.yaml)
- [Deep-dive: Legacy vs GPORCA](deep-dives/optimizer-legacy-vs-orca.md)
- [Deep-dive: статистика](deep-dives/pg-statistic-internals.md)
- [Deep-dive: storage](deep-dives/storage-physical-layout.md)
- [Deep-dive: TEMP/spill](deep-dives/temp-tables-and-spill.md)
- [Lab README](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum-625/README.md)
- [Homework](homework.md)
- [Workbook](student-workbook.md)
- [Mentor guide](mentor-guide.md)

## Контур Выпуска

```bash
python3 mentor-lab.py lesson-release greenplum-query-tuning verify
python3 scripts/build_lesson03_pptx.py
```

## Следующий Урок

Урок 04: workload management и production diagnostics.
