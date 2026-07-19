# Домашка: Урок 03

## Задача

Стенд: `greenplum-625` (Greenplum 6.25).

Перепиши тяжёлый OLAP из `lesson03.v_heavy_olap_monolith` так, чтобы:

1. декомпозиция шла через один или несколько `TEMP`;
2. каждый TEMP имел осмысленный `DISTRIBUTED BY`;
3. после наполнения TEMP выполнялся `ANALYZE`;
4. before/after `EXPLAIN` снимались при **фиксированном** `SET optimizer` (укажи on или off);
5. отдельно приложи сравнение `optimizer=on` vs `off` на `v_star_join_orca_case` с выводом, где какой лучше;
6. объясни, какие поля статистики повлияли на решение.

## Deliverables

1. SQL-файл rewrite.
2. Markdown evidence pack:
   - before plan;
   - after plan;
   - `pg_stats` snippet;
   - почему выбран Heap/AO/AOCO для промежуточных/фактов;
   - residual risk (когда rewrite может изменить бизнес-результат).
3. Один вопрос к Уроку 04 (WLM / production diagnostics).

## Самопроверка

```bash
python3 mentor-lab.py check greenplum
python3 mentor-lab.py runbook greenplum-query-tuning homework
```

```sql
\i /mentor-lab/examples/lesson03-olap-decomposition-tuning.sql
EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;
-- ваш rewrite + EXPLAIN
```

## Критерий Приёмки

См. [rubric.md](rubric.md). Без before/after плана домашка не принимается.
