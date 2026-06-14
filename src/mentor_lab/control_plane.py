"""Academy Control Plane contract for mentor and student lesson delivery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


CONTROL_PLANE_VERSION = "academy-control-plane/v1"
LESSON_01_ROOT = "docs/lessons/01-greenplum"
LESSON_02_ROOT = "docs/lessons/02-greenplum-partitioning"


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

    lab_name: str
    stage_guides: List[StageGuide]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": CONTROL_PLANE_VERSION,
            "mentor_mode": {
                "default_route": "simple",
                "runbook_commands": [
                    f"python3 mentor-lab.py runbook {self.lab_name} simple",
                    f"python3 mentor-lab.py runbook {self.lab_name} deep",
                    f"python3 mentor-lab.py runbook {self.lab_name} homework",
                ],
                "slide_deck": "artifacts/greenplum-theory.pptx",
                "stage_guides": [guide.to_dict() for guide in self.stage_guides],
            },
            "student_mode": {
                "prep_runbook": f"{LESSON_01_ROOT}/runbooks/student-prep.md",
                "workbook": f"{LESSON_01_ROOT}/student-workbook.md",
                "homework": f"{LESSON_01_ROOT}/homework.md",
                "self_check_commands": [
                    f"python3 mentor-lab.py doctor",
                    f"python3 mentor-lab.py check {self.lab_name} --dry-run",
                    f"python3 mentor-lab.py homework {self.lab_name} check --submission submissions/homework.md",
                ],
            },
            "portal_actions": {
                "start_command": (
                    f"python3 mentor-lab.py portal {self.lab_name} start "
                    "--session <session-dir> --portal-dir de-mentor-portal"
                ),
                "export_command": (
                    f"python3 mentor-lab.py portal {self.lab_name} export "
                    "--session <session-dir> --portal-dir de-mentor-portal"
                ),
                "open_command": (
                    f"python3 mentor-lab.py portal {self.lab_name} open "
                    "--url http://127.0.0.1:3000"
                ),
            },
            "artifacts": [
                {
                    "kind": "deck",
                    "path": "artifacts/greenplum-theory.pptx",
                    "label": "Презентация Greenplum theory",
                },
                {
                    "kind": "runbook",
                    "path": f"{LESSON_01_ROOT}/runbooks/simple-path.md",
                    "label": "Маршрут 60 минут",
                },
                {
                    "kind": "workbook",
                    "path": f"{LESSON_01_ROOT}/student-workbook.md",
                    "label": "Workbook ученика",
                },
                {
                    "kind": "homework",
                    "path": f"{LESSON_01_ROOT}/homework.md",
                    "label": "Домашка и критерии",
                },
            ],
            "next_lesson": {
                "code": "02-greenplum-partitioning",
                "title": "Partitioning, statistics and incremental loads in MPP",
                "path": f"{LESSON_02_ROOT}/README.md",
            },
        }


class ControlPlaneBuilder:
    """Builds the default Academy Control Plane for a lab."""

    def build(self, lab_name: str) -> AcademyControlPlane:
        return AcademyControlPlane(
            lab_name=lab_name,
            stage_guides=_stage_guides(lab_name),
        )


def _stage_guides(lab_name: str) -> List[StageGuide]:
    workbook = f"{LESSON_01_ROOT}/student-workbook.md"
    homework = f"{LESSON_01_ROOT}/homework.md"
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
                f"python3 mentor-lab.py session {lab_name} report --session <session-dir>",
                f"python3 mentor-lab.py homework {lab_name} check --submission submissions/homework.md",
            ],
            question="Что ученик принесет на следующий урок?",
            expected_answer="EXPLAIN evidence, homework SQL/design, вопросы про partition pruning/statistics/incremental loads.",
            verification="Ученик понимает deliverables и критерии приемки домашки.",
            workbook_ref=workbook,
            homework_ref=homework,
        ),
    ]
