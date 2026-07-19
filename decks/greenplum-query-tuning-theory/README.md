# Презентация: Урок 03 — Декомпозиция и тюнинг тяжёлых запросов в MPP

## Артефакты

- PowerPoint: [greenplum-query-tuning-theory.pptx](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-query-tuning-theory.pptx) (30 слайдов)
- Google Slides: https://docs.google.com/presentation/d/1PMJJ8_EB65GfS0Ndj0hUSudCPwWyKEMt__GAz5rEGPU/edit?usp=sharing
- Исходники: `decks/greenplum-query-tuning-theory/slides/`
- Facilitator: [facilitator-guide.md](facilitator-guide.md)

## Сборка PPTX

```bash
python3 scripts/build_lesson03_pptx.py
```

## Темы

- self-service стенд Greenplum 6.25;
- стадии оптимизации и Legacy vs GPORCA;
- layered `EXPLAIN`, статистика, storage, TEMP.
