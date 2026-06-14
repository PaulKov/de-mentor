"""Academy Control Plane contract for mentor and student lesson delivery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from mentor_lab.lesson_routes import LearningRoute, resolve_learning_route


CONTROL_PLANE_VERSION = "academy-control-plane/v1"


@dataclass(frozen=True)
class StageGuide:
    """Mentor-facing guide bound to one live lesson stage."""

    stage_code: str
    slides: str
    mentor_script: str
    show_commands: List[str]
    question: str
    expected_answer: str
    verification: str
    workbook_ref: str
    homework_ref: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_code": self.stage_code,
            "slides": self.slides,
            "mentor_script": self.mentor_script,
            "show_commands": self.show_commands,
            "question": self.question,
            "expected_answer": self.expected_answer,
            "verification": self.verification,
            "workbook_ref": self.workbook_ref,
            "homework_ref": self.homework_ref,
        }


@dataclass(frozen=True)
class AcademyControlPlane:
    """Serializable rich payload consumed by the Nuxt portal."""

    route: LearningRoute
    stage_guides: List[StageGuide]

    def to_dict(self) -> Dict[str, Any]:
        route = self.route
        return {
            "version": CONTROL_PLANE_VERSION,
            "mentor_mode": {
                "default_route": "simple",
                "runbook_commands": [
                    f"python3 mentor-lab.py runbook {route.name} simple",
                    f"python3 mentor-lab.py runbook {route.name} deep",
                    f"python3 mentor-lab.py runbook {route.name} homework",
                ],
                "slide_deck": route.deck_path,
                "google_slides": route.google_slides_url,
                "stage_guides": [guide.to_dict() for guide in self.stage_guides],
            },
            "student_mode": {
                "prep_runbook": route.prep_runbook_path,
                "workbook": route.workbook_path,
                "homework": route.homework_path,
                "self_check_commands": [
                    f"python3 mentor-lab.py doctor",
                    f"python3 mentor-lab.py check {route.physical_lab_name} --dry-run",
                    f"python3 mentor-lab.py homework {route.physical_lab_name} check --submission submissions/homework.md",
                ],
            },
            "portal_actions": {
                "start_command": (
                    f"python3 mentor-lab.py portal {route.name} start "
                    "--session <session-dir> --portal-dir de-mentor-portal"
                ),
                "export_command": (
                    f"python3 mentor-lab.py portal {route.name} export "
                    "--session <session-dir> --portal-dir de-mentor-portal"
                ),
                "open_command": (
                    f"python3 mentor-lab.py portal {route.name} open "
                    "--url http://127.0.0.1:3000"
                ),
            },
            "artifacts": _artifacts(route),
            "next_lesson": {
                "code": route.next_lesson.code,
                "title": route.next_lesson.title,
                "path": route.next_lesson.path,
            },
        }


class ControlPlaneBuilder:
    """Builds the default Academy Control Plane for a lab."""

    def build(self, lab_name: str) -> AcademyControlPlane:
        route = resolve_learning_route(lab_name)
        return AcademyControlPlane(
            route=route,
            stage_guides=_stage_guides(route),
        )


def _stage_guides(route: LearningRoute) -> List[StageGuide]:
    if route.lesson_code == "lesson-02":
        return _lesson02_stage_guides(route)
    return _lesson01_stage_guides(route)


def _lesson01_stage_guides(route: LearningRoute) -> List[StageGuide]:
    lab_name = route.physical_lab_name
    workbook = route.workbook_path
    homework = route.homework_path
    return [
        StageGuide(
            stage_code="environment",
            slides="1-4",
            mentor_script=(
                "Открой урок с цели, затем собери паспорт кластера: coordinator, "
                "segments, Docker context и команды проверки окружения."
            ),
            show_commands=[
                f"python3 mentor-lab.py check {lab_name} --dry-run",
                f"python3 mentor-lab.py readiness {lab_name} --platform macos",
            ],
            question="Почему Greenplum не равен просто набору шардированных PostgreSQL?",
            expected_answer=(
                "Есть единый optimizer/dispatcher, QD/QE execution, Motion, gangs, "
                "catalog-aware распределение и MPP-план целиком."
            ),
            verification="Ученик называет coordinator/master, primary segments и gp_segment_configuration.",
            workbook_ref=workbook,
            homework_ref=homework,
        ),
        StageGuide(
            stage_code="storage",
            slides="10-12",
            mentor_script=(
                "Покажи Heap, AO row и AOCO через runnable DDL, затем свяжи "
                "orientation=column с аналитическим scan pattern."
            ),
            show_commands=[
                "docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin greenplum "
                "psql -U gpadmin -d mentor -f /mentor-lab/examples/storage-and-partitioning.sql",
            ],
            question="Где включается column-store в Greenplum?",
            expected_answer="На уровне таблицы через WITH, на уровне column ENCODING и defaults через gp_default_storage_options.",
            verification="Ученик показывает appendoptimized=true и orientation=column в DDL или catalog output.",
            workbook_ref=workbook,
            homework_ref=homework,
        ),
        StageGuide(
            stage_code="plan-reading",
            slides="15, 24-28",
            mentor_script=(
                "Разбери EXPLAIN снизу вверх: scan, join, Motion, slice, gang. "
                "Отдельно проговори Broadcast vs Redistribute."
            ),
            show_commands=[
                f"python3 mentor-lab.py coach-plan {lab_name} --query bad_customer_join --sample",
            ],
            question="Что обычно означает Redistribute Motion 4:4?",
            expected_answer="Строки переезжают между QE по новому hash key, создавая границу slice.",
            verification="Ученик находит Motion и объясняет, какой join/distribution key его вызвал.",
            workbook_ref=workbook,
            homework_ref=homework,
        ),
        StageGuide(
            stage_code="practice",
            slides="18-21",
            mentor_script="Переведи разговор в evidence: симптом, план, skew, фикс, проверка до/после.",
            show_commands=[
                f"python3 mentor-lab.py autograde-sql {lab_name} --submission labs/greenplum/examples/student-solution-example.sql",
            ],
            question="Как доказать, что фикс помог, а не просто случайно ускорился запрос?",
            expected_answer="Нужны before/after EXPLAIN ANALYZE, gp_segment_id/skew evidence и одинаковый workload context.",
            verification="Submission содержит план, сегментную проверку, физическую причину и residual risk.",
            workbook_ref=workbook,
            homework_ref=homework,
        ),
        StageGuide(
            stage_code="homework",
            slides="22-23, 30",
            mentor_script="Закрой урок домашкой, критериями приемки и мостиком к Lesson 02.",
            show_commands=[
                f"python3 mentor-lab.py session {route.name} report --session <session-dir>",
                f"python3 mentor-lab.py homework {lab_name} check --submission submissions/homework.md",
            ],
            question="Что ученик принесет на следующий урок?",
            expected_answer="EXPLAIN evidence, homework SQL/design, вопросы про partition pruning/statistics/incremental loads.",
            verification="Ученик понимает deliverables и критерии приемки домашки.",
            workbook_ref=workbook,
            homework_ref=homework,
        ),
    ]


def _lesson02_stage_guides(route: LearningRoute) -> List[StageGuide]:
    workbook = route.workbook_path
    homework = route.homework_path
    sql_lab = "labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql"
    return [
        StageGuide(
            "replay",
            "1-3",
            "Начни с replay evidence: без EXPLAIN, gp_segment_id и validation partition design будет гаданием.",
            [
                "python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md",
            ],
            "Какой missing marker мешает Lesson 02?",
            "EXPLAIN, gp_segment_id, root cause, validation или residual risk.",
            "Ученик называет один evidence gap и его влияние на partitioning decision.",
            workbook,
            homework,
        ),
        StageGuide(
            "partition-pruning",
            "4-7",
            "Покажи bad/good partition key и объясни, что pruning/retention не заменяют DISTRIBUTED BY.",
            [
                "docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin greenplum bash -lc '. /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor -v ON_ERROR_STOP=1 -f /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql'",
                "SELECT * FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);",
            ],
            "Почему partition key не равен distribution key?",
            "Partition key отсекает partitions; distribution key размещает строки по segments и влияет на joins.",
            f"SQL-lab выполнен: {sql_lab}; ученик показывает EXPLAIN pruning.",
            workbook,
            homework,
        ),
        StageGuide(
            "statistics",
            "8-10",
            "Свяжи incremental load с optimizer contract: touched data должна получить свежую статистику.",
            [
                "ANALYZE lesson02.fact_sales_partitioned;",
                "SELECT schemaname, relname, n_live_tup, last_analyze FROM pg_stat_user_tables WHERE schemaname = 'lesson02' ORDER BY relname;",
            ],
            "Почему stale statistics опасны в MPP?",
            "Плохие estimates могут выбрать не тот join/Motion pattern и раздуть network exchange.",
            "Ученик показывает last_analyze и before/after EXPLAIN.",
            workbook,
            homework,
        ),
        StageGuide(
            "incremental-load",
            "11-14",
            "Разбери stage table, bounded reload window, late-arriving facts, retry и validation.",
            [
                "SELECT sale_date, count(*), sum(amount) FROM lesson02.fact_sales_stage GROUP BY sale_date ORDER BY sale_date;",
                "SELECT tableoid::regclass, count(*) FROM lesson02.fact_sales_partitioned GROUP BY tableoid::regclass ORDER BY 1;",
            ],
            "Как сделать load идемпотентным?",
            "Через deterministic keys, stage dedup, bounded replace/merge и validation before publish.",
            "Ответ содержит повторный запуск без двойной загрузки фактов.",
            workbook,
            homework,
        ),
        StageGuide(
            "homework",
            "15",
            "Закрой mini-project: DDL, pruning evidence, ANALYZE policy, late facts и residual risk.",
            [
                "python3 mentor-lab.py runbook greenplum-partitioning homework",
                "python3 mentor-lab.py student greenplum-partitioning homework",
            ],
            "Что принести на следующий урок?",
            "DDL, EXPLAIN, partition catalog checks, statistics policy и validation.",
            "Ученик понимает критерии приемки homework.",
            workbook,
            homework,
        ),
    ]


def _artifacts(route: LearningRoute) -> List[Dict[str, str]]:
    artifacts = [
        {"kind": "deck", "path": route.deck_path, "label": "Презентация урока"},
        {
            "kind": "runbook",
            "path": f"{route.docs_root}/runbooks/simple-path.md",
            "label": "Маршрут 60 минут",
        },
        {"kind": "workbook", "path": route.workbook_path, "label": "Workbook ученика"},
        {"kind": "homework", "path": route.homework_path, "label": "Домашка и критерии"},
    ]
    if route.google_slides_url:
        artifacts.insert(
            1,
            {
                "kind": "google_slides",
                "path": route.google_slides_url,
                "label": "Презентация Google Slides",
            },
        )
    artifacts.extend(
        {"kind": "sql", "path": path, "label": "SQL demo"} for path in route.sql_examples
    )
    return artifacts
