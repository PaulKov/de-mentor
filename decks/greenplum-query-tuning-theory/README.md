# Презентация: Урок 03 — Декомпозиция и тюнинг тяжёлых запросов в MPP

## Артефакты

- **Google Slides (полный deck)**: https://docs.google.com/presentation/d/1pBIOaqt9WkubsHqCN_p5kxtAhCLjPs6rxFGH9s-_o3c/edit?usp=sharing  
  **149 слайдов** = 47 core → 1 divider «Appendix» → 101 appendix. Appendix смотрите **после** основных слайдов (с ~48-го).
- **Full PPTX** (то же содержимое): [greenplum-query-tuning-theory.pptx](https://github.com/PaulKov/de-mentor/blob/master/lessons/lesson-03/artifacts/greenplum-query-tuning-theory.pptx)
- **Core-only PPTX** (lite/лекция без encyclopedia): [greenplum-query-tuning-core.pptx](https://github.com/PaulKov/de-mentor/blob/master/lessons/lesson-03/artifacts/greenplum-query-tuning-core.pptx) — 47 слайдов
- **Appendix-only PPTX**: [greenplum-query-tuning-appendix.pptx](https://github.com/PaulKov/de-mentor/blob/master/lessons/lesson-03/artifacts/greenplum-query-tuning-appendix.pptx) — 101 слайд
- Исходники: `scripts/lesson03_core_slide_specs.py`, `scripts/lesson03_appendix_slide_specs.py`
- Case metrics: `lessons/lesson-03/artifacts/case/`

## Сборка PPTX

```bash
python3 scripts/build_lesson03_pptx.py
```

Пишет: core-only + appendix-only + full (core+divider+appendix).

## Темы core (слайды 1–47)

1. Incident → diagnosis (5-слайдовый EXPLAIN ANALYZE)
2. Statistics + physical `pg_statistic`
3. Heap / AO / AOCO
4. CE traps: ORCA + Legacy → TEMP
5. Principal SCD2 locus + proof metrics

## Appendix (с слайда 48)

Glossary, CE formulas, ORCA history, full screens, Principal SCD2 deep notes.
