# Lesson Release Report: greenplum-query-tuning

Status: READY_WITH_WARNINGS
Lesson: Декомпозиция и тюнинг тяжёлых запросов в MPP
Physical lab: greenplum-625
Google Slides: https://docs.google.com/presentation/d/1pBIOaqt9WkubsHqCN_p5kxtAhCLjPs6rxFGH9s-_o3c/edit?usp=sharing
Drive folder: lessons/Greenplum/Lesson 03 - Decomposition and tuning of heavy MPP queries

## Проверки

- PASS manifest: lessons/lesson-03/docs/lesson.yaml
- PASS slide_asset_catalog: expected_slide_count **439** (core+divider+appendix)
- PASS pptx_artifact: lessons/lesson-03/artifacts/greenplum-query-tuning-theory.pptx
- PASS appendix_pptx: lessons/lesson-03/artifacts/greenplum-query-tuning-appendix.pptx
- PASS case_metrics: lessons/lesson-03/artifacts/case/metrics.md
- PASS google_slides_live: 215 slides published (final) — verify clicks in PPTX/PowerPoint; Google may need one Menu click after convert

## Команды Выпуска

- `python3 mentor-lab.py up greenplum-625`
- `python3 mentor-lab.py check greenplum-625`
- `python3 mentor-lab.py seed greenplum-625 --profile lesson03`
- `python3 scripts/build_lesson03_pptx.py`
- `python3 mentor-lab.py runbook greenplum-query-tuning simple`
- `python3 mentor-lab.py runbook greenplum-query-tuning deep`
- `python3 mentor-lab.py lesson-release greenplum-query-tuning publish-slides --dry-run --confirm-account ${GOOGLE_ACCOUNT}`
- `python3 mentor-lab.py slides publish greenplum-query-tuning --dry-run --confirm-account ${GOOGLE_ACCOUNT}`

## Что Дать Ученику

- Core PPTX / Google Slides (после republish)
- `lessons/lesson-03/docs/runbooks/student-prep.md`
- `lessons/lesson-03/docs/student-workbook.md`
- `lessons/lesson-03/docs/homework.md`
- `labs/greenplum-625/examples/lesson03-e2e-case-metrics.sql`
