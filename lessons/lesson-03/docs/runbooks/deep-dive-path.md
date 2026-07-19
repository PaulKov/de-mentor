# Deep-Dive Path: Урок 03 (Core 90 → Full)

База: **`mentor`**. Схема: **`lesson03`**.

Сначала пройдите **[facilitator-skip-map.md](facilitator-skip-map.md)**:
1. Live: **Core 90** (~45 слайдов, 2 кейса).
2. Self-service / продолжение: **Full** (остальные кейсы + appendix).

## Слои

1. **Core 90 live** — проблема → план → stats (MCV/hist смысл) → storage decision → TEMP proof → кейсы **01** + (**03** или **08**).
2. **Остальные кейсы 02–09** — по одному или homework (не все live подряд).
3. **Appendix PPTX / Google** — history, CE, screenshots, ON COMMIT (кнопка «→ Appendix» → портал → «← Вернуться»).
4. Storage lab: `lesson03-storage-heap-ao-aoco.sql` + [storage-physical-layout.md](../deep-dives/storage-physical-layout.md).
5. Stats physical: filepath `pg_statistic` + [pg-statistic-internals.md](../deep-dives/pg-statistic-internals.md).
6. TEMP lifecycle: `lesson03-temp-on-commit-lifecycle.sql`.
7. Secrets labs: `#18/#14/#29` + Principal A `#42` / B `#41` / C `#38`.
8. Design review / Principal homework.

## Команды

```bash
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py runbook greenplum-query-tuning deep
python3 mentor-lab.py psql greenplum-625
```

```sql
\i /mentor-lab/examples/lesson03-e2e-case-metrics.sql
\i /mentor-lab/examples/lesson03-storage-heap-ao-aoco.sql
\i /mentor-lab/examples/lesson03-stats-analyze-lifecycle.sql
\i /mentor-lab/examples/lesson03-secret18-not-in-broadcast.sql
\i /mentor-lab/examples/lesson03-secret14-window-partition-skew.sql
\i /mentor-lab/examples/lesson03-secret29-values-params-broadcast.sql
\i /mentor-lab/examples/lesson03-secret42-distinct-by-segment.sql
\i /mentor-lab/examples/lesson03-secret41-autostats-partitions.sql
\i /mentor-lab/examples/lesson03-secret38-median-gather-qd.sql
SELECT pg_relation_filepath('pg_statistic'::regclass);
```
