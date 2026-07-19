"""Lesson 03 catalog content kept separate from the LessonCatalog facade."""

from mentor_lab.lesson_catalog import Lesson, LessonStep


def lesson03() -> Lesson:
    """Return the Lesson 03 curriculum."""

    return Lesson(
        code="lesson-03",
        title="Декомпозиция и тюнинг тяжёлых запросов в MPP",
        steps=[
            LessonStep(
                1,
                "Стенд GP 6.25 и стадии оптимизации",
                "review",
                8,
                "Понять pipeline parse→rewrite→optimize→dispatch→execute на greenplum-625.",
                "Поднять стенд и показать SHOW optimizer.",
                "Назвать стадии и где выбирается Legacy/ORCA.",
                "Ученик отделяет optimize stage от execute/Motion.",
            ),
            LessonStep(
                2,
                "Legacy vs GPORCA",
                "practice",
                12,
                "Сравнить два оптимизатора на одном SQL и назвать trade-off.",
                "Прогнать lesson03-optimizer-legacy-vs-orca.sql.",
                "Сказать, где ORCA обычно лучше и где Legacy достаточнее.",
                "Ученик приводит плюсы/минусы и evidence из EXPLAIN.",
            ),
            LessonStep(
                3,
                "Чтение сложного EXPLAIN слоями",
                "practice",
                10,
                "Научить layered plan reading: optimizer → Motion → join → estimates → scan.",
                "Разобрать EXPLAIN monolith по слоям.",
                "Найти самый дорогой Motion и подозрительные estimates.",
                "Ученик объясняет план без «просто медленный join».",
            ),
            LessonStep(
                4,
                "Статистика до pg_statistic",
                "practice",
                10,
                "Связать selectivity с MCV/histogram/n_distinct для обоих optimizer.",
                "Показать pg_stats и сырой pg_statistic.",
                "Объяснить, какой slot влияет на predicate.",
                "Ученик связывает stale/wrong stats с плохим Motion/join.",
            ),
            LessonStep(
                5,
                "Физическое хранение Heap/AO/AOCO",
                "design",
                8,
                "Выбрать storage под access pattern на GP 6.25 (appendonly).",
                "Сравнить dim Heap и fact AOCO.",
                "Обосновать storage для fact и dimension.",
                "Ученик не предлагает AOCO как универсальный ускоритель.",
            ),
            LessonStep(
                6,
                "TEMP-декомпозиция, spill и homework",
                "practice",
                12,
                "Переписать OLAP через TEMP при фиксированном optimizer и сдать evidence.",
                "Пройти TEMP stages и выдать homework/rubric.",
                "Доказать before/after и residual risk.",
                "Ученик уходит с rewrite + optimizer policy checklist.",
            ),
        ],
    )


def lesson03_hints() -> dict[str, list[str]]:
    """Return progressive hints for Lesson 03."""

    return {
        "plan-reading": [
            "Сначала зафиксируй optimizer on/off, затем найди Motion и ключ перераспределения.",
            "Сравни estimate rows с actual rows, прежде чем менять SQL.",
            "Один узел плана должен объясняться одной физической причиной.",
        ],
        "optimizer": [
            "SET optimizer=on включает GPORCA; off — legacy Postgres planner.",
            "Сравнивайте один и тот же SQL в одной psql-сессии: on, потом off.",
            "ORCA сильнее на many-join; Legacy часто достаточнее на простых запросах.",
        ],
        "statistics": [
            "Открой pg_stats для колонок из WHERE/JOIN, затем сырой pg_statistic.",
            "MCV объясняет equality/IN, histogram — range predicates.",
            "После существенного load/TEMP наполнения делай ANALYZE до следующего EXPLAIN.",
        ],
        "storage-layout": [
            "Heap удобен для update-friendly dims; AOCO — для scan-heavy fact с узкой projection.",
            "Широкий text/jsonb payload в row-store раздувает IO даже если колонка не нужна в SELECT.",
            "Storage не заменяет DISTRIBUTED BY и не лечит skew.",
        ],
        "temp-decomposition": [
            "TEMP нужен, когда требуется новый physical stage: distribution + stats + lifecycle.",
            "Сужай данные фильтром до материализации, иначе TEMP увеличит стоимость.",
            "Spill temporary files и CREATE TEMP TABLE — разные механизмы.",
        ],
        "olap-rewrite": [
            "Делай before/after EXPLAIN на одном workload window.",
            "Каждый TEMP этап должен уменьшать cardinality или shuffle bytes.",
            "Зафиксируй residual risk: где rewrite может изменить бизнес-grain.",
        ],
    }
