# Урок 03: Декомпозиция и тюнинг тяжёлых запросов в MPP

Третий урок Greenplum Academy. Стенд — **Greenplum 6.25.3** (`greenplum-625`), БД **`mentor`** (как в Уроках 01–02), схема `lesson03`. Демо Legacy planner vs GPORCA воспроизводимо на GP 6.25.

Главная идея: Senior/Principal разбирает оптимизацию Greenplum по стадиям, сравнивает два оптимизатора, читает статистику до catalog/файлов, выбирает storage и декомпозирует тяжёлый OLAP через `TEMP`.

**GUC** `optimizer`: `on` → GPORCA, `off` → Legacy. Словарь — cheat-sheet / appendix, не три слайда в начале лекции.

**Презентация (Google Slides):** **439** слайдов (core + divider + appendix + порталы возврата). В начале: **Как смотреть** → **Оглавление** → **Словарь**. На слайдах теории — чипы терминов (наведение = кратко, клик = детали рядом / полный словарь). Футер: «☰ Меню», «Аа Словарь».

## Результат Урока

После урока ученик должен уметь:

- провести один кейс: симптом → plan profile → гипотеза → TEMP → metrics + equivalence;
- читать distributed `EXPLAIN ANALYZE` (Motion, estimate/actual, mem/spill, bottleneck);
- читать `pg_stats` / `pg_statistic` (включая физическую цепочку catalog→page→TOAST);
- выбрать Heap / AO / AOCO (`appendoptimized` / alias `appendonly`) и объяснить projection;
- использовать `TEMP` как physical stage с `DISTRIBUTED BY` + `ANALYZE`;
- формулировать ORCA/Legacy осторожно (shape на стенде ≠ industrial proof).

Вне scope: полноценный WLM и production RCA → Урок 05.

## Self-Service Стенд (GP 6.25)

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py psql greenplum-625
```

CLI создаёт БД `mentor` при `seed` / `check` / `psql` (образ boot'ится в maintenance DB `postgres`).

x86_64:

```bash
GREENPLUM_625_IMAGE=andruche/greenplum:6.25.3-slim-amd64 \
  python3 mentor-lab.py up greenplum-625
```

## Маршруты

| Маршрут | Когда использовать | Команда |
| --- | --- | --- |
| **Skip-map** | что LIVE/SKIP: Core 60 / 90 / Full | [facilitator-skip-map.md](runbooks/facilitator-skip-map.md) |
| Simple 60 мин | ~30 LIVE (incident→TEMP→proof) | `python3 mentor-lab.py runbook greenplum-query-tuning simple` |
| Core 90 мин | ~45 LIVE (+ 2 кейса, storage decision) | skip-map Core 90 + стенд |
| Full / Deep | остальные кейсы + appendix | `python3 mentor-lab.py runbook greenplum-query-tuning deep` |
| Homework Senior core | physical design + e2e proof | `python3 mentor-lab.py runbook greenplum-query-tuning homework` |

Учебный маршрут:

```bash
python3 mentor-lab.py academy greenplum-query-tuning start --student Иван --dry-run
python3 mentor-lab.py student greenplum-query-tuning bootstrap --platform macos
python3 mentor-lab.py student greenplum-query-tuning homework
```

## Практический SQL-Lab

| Файл | Роль |
| --- | --- |
| [lesson03-homework-seed.sql](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum-625/examples/lesson03-homework-seed.sql) | Homework prep (schema/data/views, **без** TEMP) |
| [lesson03-class-demo.sql](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum-625/examples/lesson03-class-demo.sql) | Урок: seed + worked TEMP (**не копировать в сдачу**) |
| [lesson03-optimizer-legacy-vs-orca.sql](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql) | Optimizer lab |

```sql
\i /mentor-lab/examples/lesson03-homework-seed.sql   -- homework
\i /mentor-lab/examples/lesson03-class-demo.sql      -- lecture only
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
SET optimizer = on;   -- GPORCA
SET optimizer = off;  -- Legacy
```

Шаблоны сдачи: [../homework/templates/evidence.md](../homework/templates/evidence.md) · [../homework/templates/reconcile.sql](../homework/templates/reconcile.sql).

## Материалы

- [Google Slides (full: core+appendix)](https://docs.google.com/presentation/d/1pBIOaqt9WkubsHqCN_p5kxtAhCLjPs6rxFGH9s-_o3c/edit?usp=sharing)
- [Full PPTX (439)](../artifacts/greenplum-query-tuning-theory.pptx)
- [Core-only PPTX (213)](../artifacts/greenplum-query-tuning-core.pptx)
- [Appendix-only PPTX (223)](../artifacts/greenplum-query-tuning-appendix.pptx)
- [E2E case metrics](../artifacts/case/metrics.md)
- [Manifest](lesson.yaml)
- [Deep-dive: Legacy vs GPORCA](deep-dives/optimizer-legacy-vs-orca.md)
- [Deep-dive: статистика](deep-dives/pg-statistic-internals.md)
- [Deep-dive: TEMP / ON COMMIT / spill](deep-dives/temp-tables-and-spill.md)
- [Deep-dive: storage Heap/AO/AOCO](deep-dives/storage-physical-layout.md)
- [Deep-dive: Principal SCD2 locus](deep-dives/principal-scd2-locus-redistribute.md)
- [Deep-dive: Secrets #18 NOT IN→Broadcast](deep-dives/secret18-not-in-broadcast.md)
- [Deep-dive: Secrets #14 Window PARTITION BY skew](deep-dives/secret14-window-partition-skew.md)
- [Deep-dive: Secrets #29 VALUES params→Broadcast fact](deep-dives/secret29-values-params-broadcast.md)
- [Deep-dive: Secrets #42 DISTINCT by segment](deep-dives/secret42-distinct-by-segment.md)
- [Deep-dive: Secrets #41 autostats×partitions](deep-dives/secret41-autostats-partitions.md)
- [Deep-dive: Secrets #38 median Gather QD](deep-dives/secret38-median-gather-qd.md)
- [SQL: E2E metrics](../../../../labs/greenplum-625/examples/lesson03-e2e-case-metrics.sql)
- [SQL: ORCA CE trap](../../../../labs/greenplum-625/examples/lesson03-orca-ce-trap.sql)
- [SQL: Legacy CE trap](../../../../labs/greenplum-625/examples/lesson03-legacy-ce-trap.sql)
- [SQL: Principal SCD2 locus](../../../../labs/greenplum-625/examples/lesson03-principal-scd2-locus.sql)
- [SQL: Secrets #18 NOT IN](../../../../labs/greenplum-625/examples/lesson03-secret18-not-in-broadcast.sql)
- [SQL: Secrets #14 Window skew](../../../../labs/greenplum-625/examples/lesson03-secret14-window-partition-skew.sql)
- [SQL: Secrets #29 VALUES params](../../../../labs/greenplum-625/examples/lesson03-secret29-values-params-broadcast.sql)
- [SQL: Secrets #42 DISTINCT map](../../../../labs/greenplum-625/examples/lesson03-secret42-distinct-by-segment.sql)
- [SQL: Secrets #41 autostats partitions](../../../../labs/greenplum-625/examples/lesson03-secret41-autostats-partitions.sql)
- [SQL: Secrets #38 median Gather](../../../../labs/greenplum-625/examples/lesson03-secret38-median-gather-qd.sql)
- [CE traps metrics](../artifacts/case/ce-traps-metrics.md)
- [Principal locus metrics](../artifacts/case/principal-scd2-locus-metrics.md)
- [SQL: storage Heap/AO/AOCO](../../../../labs/greenplum-625/examples/lesson03-storage-heap-ao-aoco.sql)
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

Урок 04: Apache Spark foundations — Big Data и PySpark execution model.
Урок 05: workload management и production diagnostics.
