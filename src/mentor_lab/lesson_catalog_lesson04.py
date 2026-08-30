"""Lesson 04 curriculum: Apache Spark foundations with PySpark."""

from mentor_lab.lesson_catalog import Incident, Lesson, LessonStep


def lesson04() -> Lesson:
    """Return the evidence-first beginner Spark curriculum."""

    return Lesson(
        code="lesson-04",
        title="Apache Spark Foundations: Big Data и PySpark execution model",
        steps=[
            LessonStep(
                1,
                "Почему появился Big Data",
                "history",
                8,
                "Связать рост данных и отказоустойчивую распределённую обработку.",
                "Провести линию GFS → MapReduce → Hadoop → Spark.",
                "Назвать ограничения одного процесса и многошагового MapReduce.",
                "Ученик объясняет появление Spark через workload, а не через маркетинговые V.",
            ),
            LessonStep(
                2,
                "Spark как compute engine",
                "theory",
                7,
                "Отделить вычислительный движок от storage и orchestration.",
                "Разместить Spark между object storage/HDFS и scheduler.",
                "Выбрать задачу, где Spark нужен, и задачу, где он избыточен.",
                "Ученик не называет Spark базой данных или универсальной заменой SQL.",
            ),
            LessonStep(
                3,
                "Driver, executors и partitions",
                "architecture",
                10,
                "Построить рабочую модель Spark application.",
                "Показать standalone master, два workers и Spark client.",
                "Сопоставить application, driver, executor и partition.",
                "Ученик объясняет, где строится план и где выполняются tasks.",
            ),
            LessonStep(
                4,
                "Lazy execution: job, stage, task",
                "practice",
                10,
                "Связать transformations/actions с физическим исполнением.",
                "Попросить предсказать, когда появится job и где будет stage boundary.",
                "Найти action и wide transformation в пайплайне.",
                "Ученик связывает action с job, shuffle с новым stage, partition с task.",
            ),
            LessonStep(
                5,
                "PySpark DataFrame pipeline",
                "practice",
                15,
                "Собрать воспроизводимый ETL без Scala и Python UDF.",
                "Запустить marketplace pipeline и explain(formatted).",
                "Прочитать данные, очистить, join, aggregate и записать Parquet.",
                "Ученик получает корректный mart и validation evidence.",
            ),
            LessonStep(
                6,
                "Spark UI и инженерное решение",
                "assessment",
                10,
                "Научить принимать решение по plan/UI evidence.",
                "Связать Exchange со shuffle metrics и выдать exit ticket.",
                "Назвать root cause, безопасное изменение и проверку корректности.",
                "Ученик уходит с evidence checklist и домашним PySpark pack.",
            ),
        ],
    )


def lesson04_hints() -> dict[str, list[str]]:
    """Return progressive beginner-friendly Spark hints."""

    return {
        "spark-architecture": [
            "Driver строит план и координирует application; executors выполняют tasks.",
            "Cluster manager выдаёт ресурсы, но не оптимизирует DataFrame query.",
            "Один executor может последовательно выполнить много tasks разных stages.",
        ],
        "lazy-evaluation": [
            "select/filter создают новый DataFrame, но ещё не запускают job.",
            "Ищи action: count, collect, show или write.",
            "До action Spark может оптимизировать всю цепочку как единый план.",
        ],
        "spark-partitions": [
            "Partition — минимальная порция данных для одного task.",
            "Сравни df.rdd.getNumPartitions() до и после repartition/groupBy.",
            "Слишком крупная partition даёт straggler; слишком мелкая — scheduler overhead.",
        ],
        "spark-shuffle": [
            "В physical plan ищи Exchange.",
            "groupBy и join по несовместимым ключам требуют перегруппировать данные.",
            "Подтверди цену через Shuffle Read/Write в Spark UI, не только названием узла.",
        ],
        "spark-joins": [
            "Сначала оцени размер стороны после фильтров, затем выбирай стратегию.",
            "Маленькую dimension можно broadcast на executors и избежать shuffle fact.",
            "Broadcast не безопасен без size evidence: копия должна поместиться на каждом executor.",
        ],
        "spark-observability": [
            "SQL tab связывает DataFrame action с physical operators.",
            "Stages tab покажет tasks, shuffle bytes, spill и разброс duration.",
            "Environment tab подтверждает effective configs, а не предполагаемые defaults.",
        ],
    }


def lesson04_incident() -> Incident:
    """Return the first evidence-first Spark diagnosis scenario."""

    return Incident(
        code="spark-shuffle-regression",
        title="Marketplace PySpark pipeline missed its SLA",
        symptoms=(
            "A daily revenue job became slow after a customer enrichment join; "
            "Spark UI shows a large Exchange and uneven task durations."
        ),
        mission=(
            "Use the physical plan and Spark UI to decide whether the root cause "
            "is an unnecessary shuffle, skew, or unsafe driver-side collection."
        ),
        acceptance_criteria=[
            "Show the Exchange in explain(formatted).",
            "Connect the Exchange to a stage boundary and shuffle metrics.",
            "Check whether the customer dimension is safe to broadcast.",
            "Validate row counts and revenue before accepting the change.",
        ],
    )
