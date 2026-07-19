# Матрица Оценки: Урок 03 (Principal Homework)

База: `mentor`. Схема: `lesson03`.

| Критерий | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Среда | Работа в `postgres` / нет `\conninfo` | Упомянут `mentor`, слабо | Явно `mentor` + зелёный `check greenplum-625` |
| Чтение плана | Нет слоёв Motion/join/estimates | Частично | Полный layered readout before **и** after |
| Статистика | Не смотрел catalog | Только `pg_stats` | `pg_stats` + `pg_statistic` + estimate-vs-actual narrative |
| Декомпозиция | Нет TEMP / CTE-only без proof | 1 TEMP без dual-stage | ≥2 TEMP + distribution + ANALYZE + co-location proof |
| Optimizer matrix | Нет сравнения | Только один SQL / один движок | 2×2: star-join case + final query, ORCA и Legacy |
| Spill / TEMP FS | Нет | Упомянуто словами | filepath `t_*` и/или constrained spill evidence |
| Reconciliation | Нет | Слабые counts | Equality/EXCEPT/checksum на окне **или** метрика расхождения + risk |
| Storage / policy | Не обоснован | Общие слова | Access pattern ↔ Heap/AO/AOCO + optimizer RFC |
| Evidence pack | Нет before/after | Есть планы, слабый вывод | Полный pack A–J из homework + residual risk |
| Adversarial | Нет | Один риск | Два способа сломать grain + закрытие |

## Порог

- **16–20**: accepted (Principal)
- **11–15**: нужна доработка evidence (не Principal-pass)
- **0–10**: повторить simple-path Урока 03, затем пересдача

## Авто-reject (любой пункт)

- смена `optimizer` между before/after rewrite proof;
- работа не в БД `mentor`;
- нет reconciliation и нет residual risk;
- `DISTRIBUTED RANDOMLY` на join-стадии без обоснования.
