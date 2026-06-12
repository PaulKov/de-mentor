"""Mentor runbook catalog for lesson delivery routes."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class RunbookStage:
    """One teachable block in a mentor-facing route."""

    timebox: str
    slides: str
    title: str
    mentor_talk: str
    commands: List[str]
    question: str
    expected_answer: str
    check: str
    links: List[str]

    def render(self, index: int) -> str:
        """Render the stage as compact Markdown for terminal output."""

        lines = [
            f"## Stage {index}: {self.timebox} - {self.title}",
            f"Slides: {self.slides}",
            f"Mentor: {self.mentor_talk}",
            "",
            "Команды:",
        ]
        lines.extend(f"  {command}" for command in self.commands)
        lines.extend(
            [
                f"Что спрашиваем: {self.question}",
                f"Expected answer: {self.expected_answer}",
                f"Как проверяем: {self.check}",
                "Links:",
            ]
        )
        lines.extend(f"- {link}" for link in self.links)
        return "\n".join(lines)


@dataclass(frozen=True)
class Runbook:
    """Full mentor route for a Greenplum lesson variant."""

    lab_name: str
    route: str
    title: str
    description: str
    stages: List[RunbookStage]

    def render(self) -> str:
        """Render a complete route for CLI usage."""

        lines = [
            f"# {self.title}",
            "",
            self.description,
            "",
            "Deck: artifacts/greenplum-theory.pptx",
            "Workbook: docs/lessons/01-greenplum/student-workbook.md",
            "Homework: docs/lessons/01-greenplum/homework.md",
            "SQL examples: labs/greenplum/examples/storage-and-partitioning.sql",
            "Partitioning examples: labs/greenplum/examples/partitioning-strategies.sql",
            "Monitoring examples: labs/greenplum/examples/cluster-monitoring.sql",
            "",
        ]
        for index, stage in enumerate(self.stages, start=1):
            lines.append(stage.render(index))
            lines.append("")
        return "\n".join(lines)


class RunbookCatalog:
    """Read-only catalog for CLI-printable mentor routes."""

    def __init__(self, runbooks: Iterable[Runbook]) -> None:
        self._runbooks: Dict[str, Dict[str, Runbook]] = {}
        for runbook in runbooks:
            self._runbooks.setdefault(runbook.lab_name, {})[runbook.route] = runbook

    @classmethod
    def default(cls) -> "RunbookCatalog":
        """Create the built-in Greenplum lesson routes."""

        common_links = [
            "decks/greenplum-theory/facilitator-guide.md",
            "docs/lessons/01-greenplum/runbooks/student-prep.md",
            "docs/lessons/01-greenplum/student-workbook.md",
            "docs/lessons/01-greenplum/homework.md",
            "labs/greenplum/examples/cluster-monitoring.sql",
            "labs/greenplum/examples/storage-and-partitioning.sql",
            "labs/greenplum/examples/partitioning-strategies.sql",
            "docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md",
        ]
        return cls(
            [
                Runbook(
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
                ),
                Runbook(
                    lab_name="greenplum",
                    route="simple",
                    title="Simple path: Greenplum lesson 01, 60 minutes",
                    description=(
                        "Базовый маршрут: дать mental model, показать storage, "
                        "distribution, skew, Motion и закончить коротким design review."
                    ),
                    stages=[
                        RunbookStage(
                            "00:00-10:00",
                            "1-6",
                            "Собираем карту Greenplum",
                            (
                                "Покажи, что Greenplum не sharded PostgreSQL: QD "
                                "планирует, QE исполняют slices в gang-процессах."
                            ),
                            [
                                "python3 mentor-lab.py up greenplum",
                                "python3 mentor-lab.py check greenplum",
                                "python3 mentor-lab.py psql greenplum",
                            ],
                            "Что делает master/coordinator, а что делают segments?",
                            (
                                "Master/QD принимает SQL, строит и dispatch-ит план; "
                                "segments/QE читают локальные данные и исполняют slices."
                            ),
                            "Ученик может словами развести control plane и data plane.",
                            common_links,
                        ),
                        RunbookStage(
                            "10:00-22:00",
                            "7-12",
                            "Storage и columnstore",
                            (
                                "Покажи Heap vs AO row vs AOCO, затем как включить "
                                "columnstore через appendoptimized=true и orientation=column."
                            ),
                            [
                                "\\i /mentor-lab/examples/cluster-monitoring.sql",
                                "docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin greenplum bash -lc '. /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor -v ON_ERROR_STOP=1 -f /mentor-lab/examples/storage-and-partitioning.sql'",
                                "\\d+ lesson01.storage_aoco_demo",
                                "SELECT c.relname, am.amname AS access_method FROM pg_class c LEFT JOIN pg_am am ON am.oid = c.relam JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'lesson01' AND c.relname LIKE 'storage_%_demo' ORDER BY c.relname;",
                            ],
                            "Почему AOCO не исправляет плохой distribution key?",
                            (
                                "AOCO ускоряет scan/compression по колонкам, но строки "
                                "все равно должны быть равномерно размещены по сегментам."
                            ),
                            "Есть три demo table и catalog checks показывают heap/AO/AOCO.",
                            common_links,
                        ),
                        RunbookStage(
                            "22:00-42:00",
                            "13-18",
                            "Distribution, skew и EXPLAIN",
                            (
                                "Дай ученику workbook: сначала gp_segment_id, затем "
                                "EXPLAIN, затем сравнение плохой и хорошей таблицы."
                            ),
                            [
                                "SELECT gp_segment_id, count(*) FROM lesson01.fact_sales_bad GROUP BY gp_segment_id ORDER BY gp_segment_id;",
                                "EXPLAIN ANALYZE SELECT c.region, sum(f.amount) FROM lesson01.fact_sales_bad f JOIN lesson01.dim_customers c USING (customer_id) GROUP BY c.region;",
                                "EXPLAIN ANALYZE SELECT c.region, sum(f.amount) FROM lesson01.fact_sales_good f JOIN lesson01.dim_customers c USING (customer_id) GROUP BY c.region;",
                            ],
                            "На что первым делом смотришь в плане Greenplum?",
                            "На Motion nodes, join key vs distribution key, Rows out и skew.",
                            "Ученик называет Redistribute/Gather Motion и причину skew.",
                            common_links,
                        ),
                        RunbookStage(
                            "42:00-60:00",
                            "19-23",
                            "Incident, design review и homework",
                            (
                                "Переведи упражнение в RCA: что сломалось, чем доказали, "
                                "какой fix и что принести на следующий урок."
                            ),
                            [
                                "\\i /mentor-lab/examples/partitioning-strategies.sql",
                                "SELECT * FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);",
                                "SELECT * FROM gp_toolkit.gp_partitions WHERE schemaname = 'lesson01';",
                                "python3 mentor-lab.py incident start greenplum skewed-distribution",
                                "python3 mentor-lab.py grade greenplum --dry-run",
                                "python3 mentor-lab.py runbook greenplum homework",
                            ],
                            "Чем partition key отличается от distribution key?",
                            (
                                "Partition key режет данные для pruning/retention; "
                                "distribution key размещает строки по сегментам."
                            ),
                            "Ученик формулирует grain, distribution, partition, leaf_partitions and checks.",
                            common_links,
                        ),
                    ],
                ),
                Runbook(
                    lab_name="greenplum",
                    route="deep",
                    title="Deep-dive path: Greenplum lesson 01, 90-120 minutes",
                    description=(
                        "Расширенный маршрут: основной урок плюс QD/QE internals, "
                        "EXPLAIN ladder, physical joins, Broadcast vs Redistribute и storage caveats."
                    ),
                    stages=[
                        RunbookStage(
                            "00:00-15:00",
                            "1-8",
                            "QD/QE, gang и slices",
                            (
                                "Разбери QD/QE сначала через аналогию, затем технически: "
                                "plan делится на slices, QueryDispatchDesc уезжает на QE."
                            ),
                            [
                                "python3 mentor-lab.py lesson greenplum --step 2",
                                "python3 mentor-lab.py hint greenplum plan-reading",
                                "python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join --sample",
                            ],
                            "Почему slice почти всегда связан с Motion boundary?",
                            (
                                "Slice описывает часть плана, которую исполняет gang; "
                                "Motion соединяет producer/consumer slices между QE."
                            ),
                            "Ученик объясняет QD, QE, gang, slice без чтения C-кода.",
                            common_links
                            + ["docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md"],
                        ),
                        RunbookStage(
                            "15:00-40:00",
                            "9-16",
                            "Storage, defaults и partitioning intro",
                            (
                                "Покажи table/column/database/role/instance defaults. "
                                "Instance-level gpconfig оставь как production snippet."
                            ),
                            [
                                "\\i /mentor-lab/examples/storage-and-partitioning.sql",
                                "\\i /mentor-lab/examples/partitioning-strategies.sql",
                                "SHOW gp_default_storage_options;",
                                "SELECT c.relname, am.amname AS access_method FROM pg_class c LEFT JOIN pg_am am ON am.oid = c.relam JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'lesson01' AND c.relname LIKE 'storage_%_demo' ORDER BY c.relname;",
                                "SELECT * FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);",
                                "SELECT * FROM gp_toolkit.gp_partitions WHERE schemaname = 'lesson01';",
                                "EXPLAIN SELECT sum(amount) FROM lesson01.fact_sales_partition_good WHERE sale_date >= DATE '2024-01-01' AND sale_date < DATE '2024-02-01';",
                            ],
                            "Почему partitioning intro не заменяет distribution design?",
                            (
                                "Partitioning дает pruning/retention по range/list; "
                                "distribution решает parallel placement и join locality."
                            ),
                            "Ученик находит PARTITION BY RANGE, PARTITION BY LIST, PARTITION BY HASH, DEFAULT partition, leaf_partitions, ATTACH PARTITION and DETACH PARTITION.",
                            common_links,
                        ),
                        RunbookStage(
                            "40:00-75:00",
                            "24-27",
                            "EXPLAIN ladder и joins",
                            (
                                "Раздели локальный алгоритм join и MPP data movement: "
                                "Hash Join отдельно, Broadcast/Redistribute/co-located отдельно."
                            ),
                            [
                                "python3 mentor-lab.py hint greenplum physical-joins",
                                "EXPLAIN SELECT c.region, sum(f.amount) FROM lesson01.fact_sales_good f JOIN lesson01.dim_customers c USING (customer_id) GROUP BY c.region;",
                                "EXPLAIN SELECT p.category, sum(f.amount) FROM lesson01.fact_sales_good f JOIN lesson01.dim_products p USING (product_id) GROUP BY p.category;",
                            ],
                            "Когда Broadcast лучше Redistribute?",
                            (
                                "Когда broadcast-side мала после фильтров и дешевле "
                                "разослать ее всем segments, чем перераскладывать большой fact."
                            ),
                            "Ученик заполняет plan-reading ladder из student-workbook.md.",
                            common_links
                            + ["docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md"],
                        ),
                        RunbookStage(
                            "75:00-120:00",
                            "28-30",
                            "Source anchors, caveats и next lesson",
                            (
                                "Закрой deep route source anchors: cdbdisp_query.c, "
                                "nodeMotion.c, nodeHashjoin.c; затем выдай homework и Lesson 02."
                            ),
                            [
                                "python3 mentor-lab.py runbook greenplum homework",
                                "python3 mentor-lab.py report greenplum --dry-run",
                                "python3 mentor-lab.py certificate greenplum --dry-run",
                            ],
                            "Что ученик принесет на Lesson 02?",
                            (
                                "DDL модели, skew checks, EXPLAIN evidence, вопросы по "
                                "partition pruning/statistics/incremental loads."
                            ),
                            "Есть acceptance criteria и список deliverables из homework.md.",
                            common_links
                            + [
                                "docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md",
                                "docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md",
                            ],
                        ),
                    ],
                ),
                Runbook(
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
                ),
            ]
        )

    def get(self, lab_name: str, route: str) -> Runbook:
        """Return one route or raise KeyError with a user-facing message."""

        try:
            return self._runbooks[lab_name][route]
        except KeyError as exc:
            raise KeyError(f"Unknown runbook route: {lab_name} {route}") from exc
