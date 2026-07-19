# Lesson Release Report: greenplum-query-tuning

Status: READY_WITH_WARNINGS
Lesson: Декомпозиция и тюнинг тяжёлых запросов в MPP
Physical lab: greenplum-625
Google Slides: https://docs.google.com/presentation/d/1e5vpqatw6ccgeZF0PWLLWMzIqkb4SODE-IwKxrSyqB8/edit?usp=sharing
Drive folder: lessons/Greenplum/Lesson 03 - Decomposition and tuning of heavy MPP queries

## Проверки

- PASS manifest: docs/lessons/03-greenplum-query-tuning/lesson.yaml
- PASS slide_asset_catalog: lessons/Greenplum/Lesson 03 - Decomposition and tuning of heavy MPP queries
- PASS pptx_artifact: artifacts/lesson-03/greenplum-query-tuning-theory.pptx
- PASS google_slides_static: lessons/Greenplum/Lesson 03 - Decomposition and tuning of heavy MPP queries
- PASS session_control_plane: greenplum-query-tuning
- PASS safe_cli_commands: 10 commands
- PASS work_account_guard: pavelkov007@gmail.com
- WARN google_slides_live: pass --live-google-slides --confirm-account and --oauth-client-json

## Команды Выпуска

- `python3 mentor-lab.py up greenplum-625`
- `python3 mentor-lab.py check greenplum-625`
- `python3 mentor-lab.py seed greenplum-625 --profile lesson03`
- `python3 mentor-lab.py runbook greenplum-query-tuning simple`
- `python3 mentor-lab.py runbook greenplum-query-tuning deep`
- `python3 mentor-lab.py runbook greenplum-query-tuning homework`
- `python3 mentor-lab.py student greenplum-query-tuning homework`
- `python3 mentor-lab.py academy greenplum-query-tuning start --student Иван --dry-run`
- `python3 mentor-lab.py lesson-release greenplum-query-tuning publish-slides --dry-run --confirm-account pavelkov007@gmail.com`
- `python3 mentor-lab.py slides publish greenplum-query-tuning --dry-run --confirm-account pavelkov007@gmail.com`

## Что Дать Ученику

- `docs/lessons/03-greenplum-query-tuning/runbooks/student-prep.md`
- `docs/lessons/03-greenplum-query-tuning/student-workbook.md`
- `docs/lessons/03-greenplum-query-tuning/homework.md`
- `docs/lessons/03-greenplum-query-tuning/runbooks/homework-plan.md`
- `labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql`
