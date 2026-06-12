# Greenplum Theory Deck

This folder contains the source and exported artifacts for the lesson-01 theory presentation.

## Артефакты

```text
artifacts/greenplum-theory.pptx
decks/greenplum-theory/facilitator-guide.md
docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md
docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md
```

## Как Использовать

- `greenplum-theory.pptx` - светлая русскоязычная презентация для первого урока: 24 слайда основного маршрута и 7 appendix/deep-route слайдов.
- `facilitator-guide.md` - поминутный план прохождения слайдов, talk track, вопросы ученику и переходы к практике.
- `qd-qe-gang-slices-explained.md` - standalone-объяснение QD, QE, slices, gangs и Motion в формате, удобном для ученика.
- `master-segment-data-path.md` - deep-dive по master/coordinator, QD/QE, Motion, gpfdist и storage models.
- Appendix track добавляет чтение `EXPLAIN`, физические joins в MPP и сравнение SMP/MPP/EPP/lakehouse.
- Runbooks связывают deck с командами Greenplum:
  - `docs/lessons/01-greenplum/runbooks/simple-path.md`;
  - `docs/lessons/01-greenplum/runbooks/deep-dive-path.md`;
  - `docs/lessons/01-greenplum/runbooks/homework-plan.md`.
- Workbook заставляет ученика доказать тезисы в SQL.
- CLI checks проверяют состояние лаборатории.
- Mentor report превращает сессию в follow-up actions.

Презентация намеренно короткая: она задает mental model, а не заменяет hands-on практику.
