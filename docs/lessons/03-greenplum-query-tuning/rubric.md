# Матрица Оценки: Урок 03

| Критерий | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Чтение плана | Нет слоёв Motion/join/estimates | Частично | Полный layered readout |
| Статистика | Не смотрел catalog | Только `pg_stats` | `pg_stats` + `pg_statistic` и связь с selectivity |
| Декомпозиция | Нет TEMP / CTE-only без proof | TEMP есть, но без distribution/ANALYZE | TEMP + distribution + ANALYZE + proof |
| Storage | Не обоснован | Общие слова | Связь access pattern ↔ Heap/AO/AOCO |
| Evidence | Нет before/after | Есть планы, слабый вывод | Планы + counts + residual risk |

## Порог

- 8–10: accepted
- 5–7: нужна доработка evidence
- 0–4: повторить simple-path Урока 03
