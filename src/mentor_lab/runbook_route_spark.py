"""Mentor runbooks for Apache Spark Lesson 04."""

from mentor_lab.runbook_models import Runbook, RunbookStage


_DECK = "lessons/lesson-04/artifacts/apache-spark-foundations-theory.pptx"
_WORKBOOK = "lessons/lesson-04/docs/student-workbook.md"
_HOMEWORK = "lessons/lesson-04/homework/assignment.md"
_EXAMPLES = [
    "labs/spark/seed/generate_lesson04_data.py",
    "labs/spark/examples/lesson04_core_pipeline.py",
    "labs/spark/examples/lesson04_deep_join.py",
]
_LINKS = [
    _WORKBOOK,
    _HOMEWORK,
    "lessons/lesson-04/docs/cheat-sheet.md",
    "http://localhost:4040",
    "http://localhost:18080",
]


def _runbook(route: str, title: str, description: str, stages: list[RunbookStage]) -> Runbook:
    return Runbook(
        lab_name="spark-foundations",
        route=route,
        title=title,
        description=description,
        stages=stages,
        deck_path=_DECK,
        workbook_path=_WORKBOOK,
        homework_path=_HOMEWORK,
        sql_examples=_EXAMPLES,
    )


def spark_prep_runbook() -> Runbook:
    return _runbook(
        "prep",
        "Lesson 04 prep: Spark stand readiness",
        "Подготовка Dockerized Spark 4.2 cluster без локальной Java/PySpark установки.",
        [
            RunbookStage(
                "T-20…T-10",
                "—",
                "Environment",
                "Подними stand, сгенерируй class dataset и прогони smoke.",
                [
                    "python3 mentor-lab.py student spark-foundations start --profile lesson04",
                ],
                "Какие интерфейсы должны быть доступны?",
                "Master UI :18080, driver UI :4040 во время application, два workers.",
                "Все smoke markers PASS; dataset существует.",
                _LINKS,
            )
        ],
    )


def spark_simple_runbook() -> Runbook:
    return _runbook(
        "simple",
        "Lesson 04 Core 60: Big Data → PySpark evidence",
        "60 минут: история, mental model, DataFrame pipeline, plan и Spark UI.",
        [
            RunbookStage(
                "00:00-15:00",
                "1-8",
                "Big Data и история",
                "Начни с SLA локального pipeline; раскрой термин, 3V и причины distributed architecture.",
                ["python3 mentor-lab.py status spark"],
                "Когда Spark избыточен?",
                "Когда данные и SLA помещаются в один процесс/СУБД без распределённой цены.",
                "Ученик называет workload constraint, а не только volume.",
                _LINKS,
            ),
            RunbookStage(
                "15:00-28:00",
                "9-16",
                "MapReduce → Spark",
                "Свяжи GFS, MapReduce и Spark с болью multi-stage/iterative workloads.",
                ["python3 mentor-lab.py check spark --dry-run"],
                "Какая стоимость породила Spark?",
                "Повторный durable I/O и orchestration цепочек jobs для reuse/iterations.",
                "Ученик связывает pain → execution model → feature.",
                _LINKS,
            ),
            RunbookStage(
                "28:00-42:00",
                "17-29",
                "API, scheduler, lazy и cache",
                "Разведи Session/Context/RDD/DataFrame/Dataset; пройди путь action до executor slot.",
                ["python3 mentor-lab.py check spark --dry-run"],
                "Кто назначает task и что делает cache() до первого action?",
                "Driver scheduler назначает task; cache ленив и заполняется первым action.",
                "Ученик объясняет job → stages → TaskSet → tasks и reuse blocks.",
                _LINKS,
            ),
            RunbookStage(
                "42:00-54:00",
                "30-36",
                "Live PySpark pipeline",
                "Читай с schema, очисти, join, aggregate, explain, write Parquet.",
                [
                    "python3 mentor-lab.py spark-submit spark labs/spark/examples/lesson04_core_pipeline.py -- --hold-seconds 300"
                ],
                "Почему до count/write в UI нет job?",
                "DataFrame transformations lazy; action материализует план.",
                "Mart записан; counts/revenue/roundtrip PASS.",
                _LINKS,
            ),
            RunbookStage(
                "54:00-60:00",
                "37-39",
                "Plan, UI, exit ticket",
                "Найди Exchange и свяжи его со stage shuffle metrics.",
                ["open http://localhost:4040"],
                "Как доказать, что join дорогой?",
                "Exchange в plan + shuffle read/write + task distribution в UI.",
                "Ученик формулирует root cause, change и validation.",
                _LINKS,
            ),
        ],
    )


def spark_deep_runbook() -> Runbook:
    return _runbook(
        "deep",
        "Lesson 04 Deep 90: plans, shuffle и join strategy",
        "Core + 30 минут: plan layers, Python/JVM boundary, broadcast A/B и AQE.",
        [
            *spark_simple_runbook().stages[:3],
            RunbookStage(
                "42:00-58:00",
                "30-39",
                "Core pipeline + plan/UI",
                "Запусти core case, свяжи plan, stages/tasks, UI metrics и correctness.",
                [
                    "python3 mentor-lab.py spark-submit spark labs/spark/examples/lesson04_core_pipeline.py -- --hold-seconds 300"
                ],
                "Почему built-in expressions предпочтительнее Python UDF?",
                "Planner видит выражение; меньше Python/JVM serialization boundary.",
                "Ученик показывает physical plan и корректный output.",
                _LINKS,
            ),
            RunbookStage(
                "58:00-73:00",
                "40-49",
                "Spark vs MapReduce + scheduler internals",
                "Пройди cost matrices и scheduler stack от DAGScheduler до executor slot.",
                ["python3 mentor-lab.py status spark"],
                "Где Spark экономит I/O и кто принимает scheduling decision?",
                "DAG/persist экономят reuse; driver scheduler запускает tasks на выделенных executors.",
                "Ученик связывает cost model, TaskSet, locality и retry.",
                _LINKS,
            ),
            RunbookStage(
                "73:00-88:00",
                "50-58",
                "Execution/cache internals + join A/B",
                "Сравни plans, BlockManager reuse и shuffle/broadcast на одной семантике.",
                [
                    "python3 mentor-lab.py spark-submit spark labs/spark/examples/lesson04_deep_join.py -- --hold-seconds 300"
                ],
                "Когда broadcast ухудшит ситуацию?",
                "Когда build side велика после фильтров и копия не помещается на каждом executor.",
                "Ученик находит Exchange/BroadcastHashJoin и сравнивает UI metrics.",
                _LINKS,
            ),
            RunbookStage(
                "88:00-90:00",
                "59",
                "Production checklist",
                "Закрой collect/UDF/cache/small files/skew и выдай homework evidence pack.",
                ["python3 mentor-lab.py runbook spark-foundations homework"],
                "Какие три evidence обязательны перед merge?",
                "Plan/UI, correctness reconciliation, output/data-layout validation.",
                "Ученик повторяет deliverables и hard gates.",
                _LINKS,
            ),
        ],
    )


def spark_homework_runbook() -> Runbook:
    return _runbook(
        "homework",
        "Lesson 04 Homework: PySpark ETL Evidence Pack",
        "90–120 минут после зелёного check: pipeline, plan, quality и decision.",
        [
            RunbookStage(
                "00:00-20:00",
                "—",
                "Baseline",
                "Зафиксируй schema, counts, partitions и исходный physical plan.",
                [
                    "python3 mentor-lab.py student spark-foundations start --profile lesson04",
                    "python3 mentor-lab.py student spark-foundations init",
                ],
                "Что является baseline evidence?",
                "Input contract, counts, partition count, explain(formatted).",
                "Evidence A-C заполнены.",
                _LINKS,
            ),
            RunbookStage(
                "20:00-75:00",
                "—",
                "Own pipeline",
                "Собери свой mart без collect/toPandas и Python UDF.",
                ["python3 mentor-lab.py spark-submit spark lessons/lesson-04/submissions/pipeline.py"],
                "Где возникает shuffle и зачем он нужен?",
                "Exchange перегруппирует данные для join/groupBy; цена доказана в UI.",
                "Pipeline и plan evidence готовы.",
                _LINKS,
            ),
            RunbookStage(
                "75:00-120:00",
                "—",
                "Reconciliation и self-check",
                "Проверь counts, sums, persisted roundtrip и residual risks.",
                [
                    "python3 mentor-lab.py student spark-foundations test --submission lessons/lesson-04/submissions"
                ],
                "Что запрещает принять быстрое, но неверное изменение?",
                "Hard gates по correctness и reproducibility.",
                "Homework reviewer принимает pack.",
                _LINKS,
            ),
        ],
    )


def spark_runbooks() -> list[Runbook]:
    """Return all supported routes in stable CLI order."""

    return [
        spark_prep_runbook(),
        spark_simple_runbook(),
        spark_deep_runbook(),
        spark_homework_runbook(),
    ]
