# Simple Path: Урок 03 (Core 60, GP 6.25)

## Цель

Problem-first за ~60 минут: симптом → plan profile lite → TEMP → metrics.  
Канон слайдов: **[facilitator-skip-map.md](facilitator-skip-map.md)** → режим **Core 60**.

## Что LIVE / что SKIP

| LIVE (~30) | SKIP |
| --- | --- |
| Проблема 13–17, план 18–29, stats lite 35–36/40/43/50, практика 60–63/66–68, wrap 105–107 | Front-словарь 4–12, «Детали ·», формулы AND, storage anatomy, кейсы 01–09 live |

Словарь — чипы «Термины» или «Аа Словарь» по вопросу. Appendix не открывать на проекторе.

## Шаги

1. `up` + `seed` → БД `mentor`, схема `lesson03`.
2. Baseline monolith: зафиксировать `SET optimizer=on`, снять EXPLAIN ANALYZE.
3. Plan 1–5 lite: Motion / cardinality / bottleneck.
4. TEMP rewrite + `ANALYZE` stages.
5. After plan + equivalence + метрики (`lesson03-e2e-case-metrics.sql`).
6. Checklist → homework (кейсы — самостятельно).

## Команды

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py runbook greenplum-query-tuning simple
python3 mentor-lab.py psql greenplum-625
```

```sql
\i /mentor-lab/examples/lesson03-e2e-case-metrics.sql
```
