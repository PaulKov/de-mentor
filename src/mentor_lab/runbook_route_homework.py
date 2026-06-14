"""Greenplum homework mentor route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_routes_common import greenplum_common_links


def greenplum_homework_runbook() -> Runbook:
    common_links = greenplum_common_links()
    return Runbook(
                        lab_name="greenplum",
                        route="homework",
                        title="Homework plan: Greenplum lesson 01",
                        description=(
                            "План самостоятельной работы на 60-90 минут и мост в "
                            "Lesson 02: Partitioning, statistics and incremental loads in MPP."
                        ),
                        stages=[
                            RunbookStage(
                                "00:00-10:00",
                                "23, 30",
                                "Понять задачу и собрать DDL sketch",
                                "Ученик начинает с grain, а не с ключей или индексов.",
                                [
                                    "python3 mentor-lab.py info greenplum",
                                    "python3 mentor-lab.py runbook greenplum simple",
                                ],
                                "Какой факт самый большой и какой у него grain?",
                                "Fact grain написан до physical design.",
                                "В шаблоне homework.md заполнены facts/dimensions/grain.",
                                common_links,
                            ),
                            RunbookStage(
                                "10:00-45:00",
                                "11-16",
                                "Distribution, storage и partitioning evidence",
                                "Нужно приложить SQL, skew checks и хотя бы один EXPLAIN.",
                                [
                                    "python3 mentor-lab.py up greenplum",
                                    "python3 mentor-lab.py check greenplum",
                                    "python3 mentor-lab.py seed greenplum --profile enterprise --dry-run",
                                    "docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin greenplum bash -lc '. /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor -v ON_ERROR_STOP=1 -f /mentor-lab/examples/storage-and-partitioning.sql'",
                                    "docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin greenplum bash -lc '. /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor -v ON_ERROR_STOP=1 -f /mentor-lab/examples/partitioning-strategies.sql'",
                                ],
                                "Почему выбранный partition key не обязан совпадать с distribution key?",
                                "Один оптимизирует pruning/retention, другой - segment placement.",
                                "Есть `gp_segment_id`, `EXPLAIN` и storage catalog output.",
                                common_links,
                            ),
                            RunbookStage(
                                "45:00-90:00",
                                "24-30",
                                "Deep optional и подготовка к Lesson 02",
                                (
                                    "Сильный ученик добавляет plan-reading ladder, joins "
                                    "analysis и список вопросов по partition pruning/statistics."
                                ),
                                [
                                    "python3 mentor-lab.py hint greenplum plan-reading",
                                    "python3 mentor-lab.py hint greenplum physical-joins",
                                    "python3 mentor-lab.py grade greenplum --dry-run",
                                ],
                                "Что обязательно принести на следующий урок?",
                                (
                                    "DDL, rationale, self-check commands, EXPLAIN evidence, "
                                    "риски late-arriving facts и statistics after load."
                                ),
                                (
                                    "Домашка проходит criteria из homework.md и содержит "
                                    "вопросы к Lesson 02."
                                ),
                                common_links + ["docs/lessons/01-greenplum/runbooks/homework-plan.md"],
                            ),
                        ],
                    )
