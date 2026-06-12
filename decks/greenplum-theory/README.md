# Greenplum Theory Deck

This folder contains the source and exported artifacts for the lesson-01 theory presentation.

## Артефакты

- [Презентация PowerPoint](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx)
- [Facilitator guide](https://github.com/PaulKov/de-mentor/blob/master/decks/greenplum-theory/facilitator-guide.md)
- [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md)
- [Master/segment data path deep dive](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md)

## Как Использовать

- [Презентация PowerPoint](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx) - светлая русскоязычная презентация для первого урока: 24 слайда основного маршрута и 8 appendix/deep-route слайдов.
- [Facilitator guide](https://github.com/PaulKov/de-mentor/blob/master/decks/greenplum-theory/facilitator-guide.md) - поминутный план прохождения слайдов, talk track, вопросы ученику и переходы к практике.
- [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md) - standalone-объяснение QD, QE, slices, gangs и Motion в формате, удобном для ученика.
- [Master/segment data path deep dive](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md) - deep-dive по master/coordinator, QD/QE, Motion, gpfdist и storage models.
- [Partitioning strategies deep dive](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md) - deep-dive по `PARTITION BY RANGE`, `PARTITION BY LIST`, `PARTITION BY HASH`, `DEFAULT partition`, `pg_partition_tree`, `gp_toolkit.gp_partitions` и `leaf_partitions`.
- Appendix track добавляет чтение `EXPLAIN`, физические joins в MPP, partition catalog и сравнение SMP/MPP/EPP/lakehouse.
- Runbooks связывают deck с командами Greenplum:
  - [Simple path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/simple-path.md);
  - [Deep-dive path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/deep-dive-path.md);
  - [Homework plan](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/homework-plan.md).
- Workbook заставляет ученика доказать тезисы в SQL.
- CLI checks проверяют состояние лаборатории.
- Mentor report превращает сессию в follow-up actions.

Презентация намеренно короткая: она задает mental model, а не заменяет hands-on практику.
