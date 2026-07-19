# Simple Path: Урок 03 (60 минут, GP 6.25)

## Цель

Провести ученика от стенда GP 6.25 (БД **`mentor`**) к сравнению ORCA/Legacy и TEMP-декомпозиции с evidence.

## Шаги

1. `up` + `seed` стенда `greenplum-625` → БД `mentor`, схема `lesson03`.
2. `\conninfo`; `SHOW optimizer`; прогнать `lesson03-optimizer-legacy-vs-orca.sql`.
3. Layered EXPLAIN монолита (слайды pipeline/EXPLAIN).
4. `pg_stats` / `pg_statistic`.
5. TEMP rewrite + before/after при фиксированном optimizer.
6. Homework checklist (Principal 90м).

## Команды

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py runbook greenplum-query-tuning simple
python3 mentor-lab.py psql greenplum-625
```

```sql
\conninfo
\i /mentor-lab/examples/lesson03-olap-decomposition-tuning.sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;
```

## Слайды

1–4 (glossary), 5–25 (pipeline + plans), 26–35 (case/Motion), 36–48 (stats deep), 49–62 (storage/TEMP), 63–65 (proof).
