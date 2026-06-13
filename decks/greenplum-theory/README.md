# Теоретическая Презентация Greenplum

Эта папка содержит исходники и экспортированные артефакты теоретической презентации для первого урока.

## Артефакты

- [Презентация PowerPoint](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx)
- [Гайд ведущего](https://github.com/PaulKov/de-mentor/blob/master/decks/greenplum-theory/facilitator-guide.md)
- [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md)
- [Deep dive по master/segment data path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md)

## Как Использовать

- [Презентация PowerPoint](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx) - светлая русскоязычная презентация для первого урока: 24 слайда основного маршрута и 8 appendix/deep-route слайдов.
- [Гайд ведущего](https://github.com/PaulKov/de-mentor/blob/master/decks/greenplum-theory/facilitator-guide.md) - поминутный план прохождения слайдов, talk track, вопросы ученику и переходы к практике.
- [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md) - standalone-объяснение QD, QE, slices, gangs и Motion в формате, удобном для ученика.
- [Deep dive по master/segment data path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md) - технический разбор master/coordinator, QD/QE, Motion, gpfdist и storage models.
- [Deep dive по partitioning strategies](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md) - разбор `PARTITION BY RANGE`, `PARTITION BY LIST`, `PARTITION BY HASH`, `DEFAULT partition`, `pg_partition_tree`, `gp_toolkit.gp_partitions` и `leaf_partitions`.
- Appendix-маршрут добавляет чтение `EXPLAIN`, физические joins в MPP, partition catalog и сравнение SMP/MPP/EPP/lakehouse.
- Runbook'и связывают презентацию с командами Greenplum:
  - [упрощенный маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/simple-path.md);
  - [расширенный маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/deep-dive-path.md);
  - [план домашки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/homework-plan.md).
- Workbook ученика заставляет доказать тезисы в SQL.
- CLI-проверки показывают состояние лаборатории.
- Mentor report превращает сессию в follow-up actions.

Презентация намеренно короткая: она задает mental model, а не заменяет hands-on практику.
