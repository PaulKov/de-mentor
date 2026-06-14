"""Greenplum prep mentor route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_routes_common import greenplum_common_links


def greenplum_prep_runbook() -> Runbook:
    common_links = greenplum_common_links()
    return Runbook(
                        lab_name="greenplum",
                        route="prep",
                        title="Student prep: Greenplum lesson 01 environment checklist",
                        description=(
                            "Self-service подготовка ученика к уроку: macOS, Windows и Linux, "
                            "Docker Desktop / Docker Engine, WSL 2, Python, Git, порт 15432 и smoke-check."
                        ),
                        stages=[
                            RunbookStage(
                                "За 1-2 дня до урока",
                                "no slides",
                                "Проверить железо и базовые инструменты",
                                (
                                    "Ученик готовит ноутбук: Docker запущен, Python и Git "
                                    "доступны из терминала, порт 15432 свободен."
                                ),
                                [
                                    "python3 --version",
                                    "py --version",
                                    "git --version",
                                    "docker --version",
                                    "docker compose version",
                                    "python3 mentor-lab.py doctor",
                                ],
                                "Что должно быть готово до начала урока?",
                                (
                                    "Docker работает, Docker Compose v2 доступен, Python 3.9+ "
                                    "запускает mentor-lab.py, Git умеет клонировать репозиторий."
                                ),
                                "Команды версий выполняются без ошибок, `doctor` печатает next action.",
                                [
                                    "docs/lessons/01-greenplum/runbooks/student-prep.md",
                                    "docs/lessons/01-greenplum/student-workbook.md",
                                    "docs/lessons/01-greenplum/homework.md",
                                ],
                            ),
                            RunbookStage(
                                "macOS",
                                "no slides",
                                "Docker Desktop и Terminal",
                                (
                                    "На macOS достаточно Docker Desktop, Git и Python 3.9+. "
                                    "psql локально ставить не нужно: CLI открывает psql внутри контейнера."
                                ),
                                [
                                    "docker compose version",
                                    "git clone https://github.com/PaulKov/de-mentor.git",
                                    "cd de-mentor",
                                    "python3 mentor-lab.py doctor",
                                    "python3 mentor-lab.py up greenplum",
                                    "python3 mentor-lab.py check greenplum",
                                    "python3 mentor-lab.py psql greenplum",
                                ],
                                "Что делать, если Docker Desktop не запущен?",
                                "Запустить Docker Desktop, дождаться running state и повторить `docker compose version`.",
                                "`check greenplum` показывает PASS, `psql` открывается внутри контейнера.",
                                [
                                    "docs/lessons/01-greenplum/runbooks/student-prep.md",
                                    "docs/lessons/01-greenplum/student-workbook.md",
                                    "labs/greenplum/README.md",
                                ],
                            ),
                            RunbookStage(
                                "Windows",
                                "no slides",
                                "Docker Desktop с WSL 2 backend",
                                (
                                    "На Windows нужен Docker Desktop с включенным WSL 2 backend. "
                                    "Команды запускаем из PowerShell в папке репозитория через `py`."
                                ),
                                [
                                    "py --version",
                                    "docker compose version",
                                    "git clone https://github.com/PaulKov/de-mentor.git",
                                    "cd de-mentor",
                                    "py mentor-lab.py doctor",
                                    "py mentor-lab.py up greenplum",
                                    "py mentor-lab.py check greenplum",
                                    "py mentor-lab.py psql greenplum",
                                ],
                                "Какая самая частая причина проблем на Windows?",
                                (
                                    "Docker Desktop не запущен, WSL 2 backend выключен, "
                                    "виртуализация отключена в BIOS/UEFI или PowerShell открыт не в папке репозитория."
                                ),
                                "`py mentor-lab.py check greenplum` проходит, порт 15432 не занят.",
                                [
                                    "docs/lessons/01-greenplum/runbooks/student-prep.md",
                                    "docs/lessons/01-greenplum/student-workbook.md",
                                    "labs/greenplum/README.md",
                                ],
                            ),
                            RunbookStage(
                                "Linux",
                                "no slides",
                                "Docker Engine и Compose plugin",
                                (
                                    "На Linux нужен Docker Engine, Docker Compose plugin и доступ "
                                    "к Docker daemon без `sudo` для стандартного CLI flow."
                                ),
                                [
                                    "python3 --version",
                                    "docker --version",
                                    "docker compose version",
                                    "groups | grep docker",
                                    "git clone https://github.com/PaulKov/de-mentor.git",
                                    "cd de-mentor",
                                    "python3 mentor-lab.py doctor",
                                    "python3 mentor-lab.py up greenplum",
                                    "python3 mentor-lab.py check greenplum",
                                ],
                                "Почему лучше настроить docker group заранее?",
                                "CLI вызывает `docker compose`; если Docker требует `sudo`, self-service команды ученика будут спотыкаться.",
                                "`docker compose version` и `check greenplum` проходят от обычного пользователя.",
                                [
                                    "docs/lessons/01-greenplum/runbooks/student-prep.md",
                                    "docs/lessons/01-greenplum/student-workbook.md",
                                    "labs/greenplum/README.md",
                                ],
                            ),
                            RunbookStage(
                                "За 15 минут до урока",
                                "no slides",
                                "Smoke-check стенда",
                                (
                                    "Ученик заранее скачивает image, стартует стенд, проверяет PASS "
                                    "и оставляет вопросы ментору."
                                ),
                                [
                                    "docker pull docker.io/woblerr/greenplum:7.1.0",
                                    "python3 mentor-lab.py up greenplum",
                                    "python3 mentor-lab.py check greenplum",
                                    "python3 mentor-lab.py runbook greenplum prep",
                                    "python3 mentor-lab.py down greenplum",
                                ],
                                "Что делать, если image pull не проходит?",
                                "Проверить интернет, VPN/proxy, доступ к Docker Hub и повторить до урока.",
                                "Есть PASS output или понятный вопрос с ошибкой для ментора.",
                                common_links + ["docs/lessons/01-greenplum/runbooks/student-prep.md"],
                            ),
                        ],
                    )
