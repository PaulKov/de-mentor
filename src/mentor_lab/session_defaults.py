"""Default stage graph and CLI commands for Academy sessions."""

from __future__ import annotations

from typing import List

from mentor_lab.session_model import SessionStage, SkillNode

def _default_stages(lab_name: str) -> List[SessionStage]:
    return [
        SessionStage(
            code="environment",
            title="Окружение и паспорт кластера",
            timebox="00:00-10:00",
            mentor_focus="Проверить Docker, поднять Greenplum, показать topology.",
            student_action="Запустить doctor/check и назвать coordinator/segments.",
            command=f"python3 mentor-lab.py check {lab_name} --dry-run",
        ),
        SessionStage(
            code="storage",
            title="Heap, AO row, AOCO",
            timebox="10:00-22:00",
            mentor_focus="Сравнить row-store и column-store на DDL и catalog checks.",
            student_action="Объяснить, где включается orientation=column.",
            command=(
                "docker compose -f labs/greenplum/docker-compose.yml exec -T -u "
                "gpadmin greenplum psql -U gpadmin -d mentor -f "
                "/mentor-lab/examples/storage-and-partitioning.sql"
            ),
        ),
        SessionStage(
            code="plan-reading",
            title="EXPLAIN, Motion, QD/QE/gang/slice",
            timebox="22:00-40:00",
            mentor_focus="Показать, как Motion режет план на slices.",
            student_action="Найти Redistribute/Broadcast/Gather Motion в плане.",
            command=f"python3 mentor-lab.py coach-plan {lab_name} --query bad_customer_join --sample",
        ),
        SessionStage(
            code="practice",
            title="Практика и evidence",
            timebox="40:00-55:00",
            mentor_focus="Собрать evidence pack и проверить SQL submission.",
            student_action="Сформулировать причину, фикс и проверку до/после.",
            command=(
                f"python3 mentor-lab.py autograde-sql {lab_name} "
                "--submission labs/greenplum/examples/student-solution-example.sql"
            ),
        ),
        SessionStage(
            code="homework",
            title="Домашка и следующий урок",
            timebox="55:00-60:00",
            mentor_focus="Передать student handoff, критерии и Lesson 02.",
            student_action="Назвать, что принесет на следующий урок.",
            command=f"python3 mentor-lab.py session {lab_name} report --session <session-dir>",
        ),
    ]


def _default_skill_graph() -> List[SkillNode]:
    return [
        SkillNode(
            code="topology",
            title="Кластер и topology",
            level="intro",
            evidence="Ученик объясняет coordinator/master, primary segments и gp_segment_configuration.",
        ),
        SkillNode(
            code="qd-qe",
            title="QD/QE/gang/slice",
            level="core",
            evidence="Ученик связывает QD, QE, gang, slice и Motion с EXPLAIN.",
        ),
        SkillNode(
            code="storage",
            title="Heap/AO/AOCO",
            level="core",
            evidence="Ученик показывает appendoptimized=true и orientation=column в DDL.",
        ),
        SkillNode(
            code="explain-motion",
            title="EXPLAIN и Motion",
            level="core",
            evidence="Ученик отличает Broadcast Motion, Redistribute Motion и Gather Motion.",
        ),
        SkillNode(
            code="evidence",
            title="Evidence-first debugging",
            level="practice",
            evidence="Submission содержит симптом, план, skew check, фикс и validation.",
        ),
    ]


def _default_commands(lab_name: str) -> List[str]:
    return [
        "python3 mentor-lab.py doctor",
        f"python3 mentor-lab.py readiness {lab_name} --platform macos",
        f"python3 mentor-lab.py up {lab_name}",
        f"python3 mentor-lab.py check {lab_name}",
        f"python3 mentor-lab.py runbook {lab_name} simple",
        f"python3 mentor-lab.py teach {lab_name} simple --stage 1",
        f"python3 mentor-lab.py coach-plan {lab_name} --query bad_customer_join --sample",
        f"python3 mentor-lab.py dataset {lab_name} generate --scale small --seed 42 --skew high --late-facts --wide-rows --output artifacts/generated-enterprise.sql",
        f"python3 mentor-lab.py evidence {lab_name} collect redistribute-join --output submissions/redistribute-join.md",
        f"python3 mentor-lab.py autograde-sql {lab_name} --submission labs/greenplum/examples/student-solution-example.sql --output artifacts/sql-autograde.md",
        f"python3 mentor-lab.py session {lab_name} report --session <session-dir> --output artifacts/{lab_name}-session-report.md",
        f"python3 mentor-lab.py ci-smoke {lab_name} --dry-run",
    ]
