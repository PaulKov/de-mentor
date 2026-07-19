"""Optimization cases for Lesson 03 — each starts with a dedicated title slide."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from lesson03_slide_blocks import case_title, stage_gate

GPDB_ARCHIVE = "https://github.com/greenplum-db/gpdb-archive/blob/main"
GPDB_ORCA = "https://github.com/apache/cloudberry/blob/main/src/backend/gporca"


def _k(spec: Dict[str, Any], kicker: str) -> Dict[str, Any]:
    out = dict(spec)
    out["kicker"] = kicker
    return out


CASES_SECTION_GATE = stage_gate(
    anchor="cases",
    num="6",
    title="Кейсы оптимизации",
    subtitle="Отдельные ловушки плана. У каждого кейса — титул → разбор → план/код → фикс.",
    cards=[
        ["Формат", "Проблема → сигнал в EXPLAIN → почему → как чинить → стенд.", "green"],
        ["CE", "Два кейса недооценки строк (ORCA и Legacy).", "red"],
        ["Motion / locus", "SCD2, NOT IN, window, VALUES, DISTINCT, median.", "amber"],
        ["Stats ETL", "Autostats не срабатывает на INSERT в parent.", "blue"],
    ],
)


def build_case_slides() -> List[Dict[str, Any]]:
    slides: List[Dict[str, Any]] = [CASES_SECTION_GATE]

    # --- Case 01: ORCA CE ---
    slides.append(
        case_title(
            anchor="case-orca-ce",
            num="01",
            title="ORCA недооценил строки → Nested Loop",
            subtitle="Три CTE + join к маленькой dim: план верит в «1 row».",
            problem="GPORCA выбирает Index Nested Loop при est≪actual.",
            plan_signal="Nested Loop + Broadcast/Index Scan, loops≈80k, rows=1→80000.",
            fix="TEMP stage + ANALYZE → Hash Join; не «просто SET optimizer».",
            lab="lesson03-orca-ce-trap.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 01 · Суть",
                "title": "Что → как → почему",
                "subtitle":
                "Скрипт: lesson03-orca-ce-trap.sql · metrics: ce-traps-metrics.md",
                "type": "cards",
                "cards": [
                    ["Что", "3 CTE + opaque preds → join к replicated dim с index.", "amber"],
                    ["Как", "ORCA: Nested Loop + Index Scan, est≈1, loops=80k.", "red"],
                    ["Почему", "Cardinality under-estimate после CTE/opaque фильтров.", "blue"],
                    ["Фикс", "TEMP + ANALYZE enriched stage → Hash Join ~21 ms (lab).", "green"],
                ],
            },
            {
                "kicker": "Кейс 01 · SQL",
                "title": "Стендовый запрос (ORCA)",
                "subtitle": "Предикаты почти keep-all. Статы нет / stale.",
                "type": "code",
                "code_kind": "SQL",
                "code": (
                    "SET optimizer = on;\n"
                    "WITH cte_orders AS ( … opaque … ),\n"
                    "     cte_active AS ( … ),\n"
                    "     cte_enriched AS ( … )\n"
                    "SELECT e.*, r.tier, r.score\n"
                    "FROM cte_enriched e\n"
                    "JOIN lesson03.orca_ref r USING (customer_id);"
                ),
            },
            {
                "kicker": "Кейс 01 · План",
                "title": "Плохой план и после TEMP",
                "subtitle": "Форма важнее абсолютных секунд на 2 seg.",
                "type": "code",
                "code_kind": "PLAN",
                "code": (
                    "BAD:\n"
                    "Nested Loop                 rows=1 → actual 80000\n"
                    "  -> Broadcast Motion        rows=1 → actual 80000\n"
                    "  -> Index Scan              loops=80000\n\n"
                    "GOOD (TEMP+ANALYZE):\n"
                    "Hash Join  est≈actual  ~21 ms"
                ),
            },
        ]
    )

    # --- Case 02: Legacy CE ---
    slides.append(
        case_title(
            anchor="case-legacy-ce",
            num="02",
            title="Legacy: EXISTS → Nested Loop Semi Join",
            subtitle="Тот же класс CE-ошибки, другой SQL и другой optimizer.",
            problem="Postgres planner выбирает Nested Loop Semi при under-estimate.",
            plan_signal="Nested Loop Semi Join, est≪actual, огромные loops.",
            fix="TEMP + ANALYZE; enable_nestloop на стенде включаем явно.",
            lab="lesson03-legacy-ce-trap.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 02 · Суть",
                "title": "Что → как → почему",
                "subtitle": "Почему нельзя один SQL на оба оптимизатора для демо.",
                "type": "cards",
                "cards": [
                    ["Что", "Opaque filters + EXISTS + join к dim.", "amber"],
                    ["Как", "Nested Loop Semi Join + Nested Loop (Legacy).", "red"],
                    ["Почему", "EXISTS «приглашает» semi; CE занижает rows.", "blue"],
                    ["Фикс", "Physical stage + ANALYZE → Hash Join ~22 ms.", "green"],
                ],
            },
            {
                "kicker": "Кейс 02 · План",
                "title": "Плохой план Legacy",
                "subtitle": "HashJoin остаётся ON — NL выбран стоимостью.",
                "type": "code",
                "code_kind": "PLAN",
                "code": (
                    "SET optimizer = off;\n"
                    "SET enable_nestloop = on;\n\n"
                    "Nested Loop\n"
                    "  -> Nested Loop Semi Join   rows=15 → actual 40060\n"
                    "       -> Seq Scan … est≈29\n"
                    "       -> Index Scan         loops=40060"
                ),
            },
            {
                "kicker": "Кейс 02 · Вывод",
                "title": "CE trap → TEMP, не «просто сменить optimizer»",
                "subtitle": "Смена движка без cardinality stage часто не лечит корень.",
                "type": "two",
                "left": [
                    "Диагноз",
                    "est≪actual на join/semi + index dim → NL-семейство. Смотрите loops=.",
                    "green",
                ],
                "right": [
                    "Лечение",
                    "Physical stage (TEMP) + ANALYZE; proof в ce-traps-metrics.md.",
                    "blue",
                ],
            },
        ]
    )

    # --- Case 03: SCD2 ---
    slides.append(
        case_title(
            anchor="case-scd2",
            num="03",
            title="SCD2: Redistribute при «согласованном» join",
            subtitle="Ключи join совпали с DISTRIBUTED BY — а Motion всё равно есть.",
            problem="CTE max(version) меняет locus: hash(biz_key) ≠ hash(biz_key, version).",
            plan_signal="Redistribute … Hash Key: biz_key (часто ×2).",
            fix="DISTRIBUTED BY (biz_key) под access pattern; TEMP только keys — мало.",
            lab="lesson03-principal-scd2-locus.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 03 · Суть",
                "title": "Иллюзия co-location",
                "subtitle": "Senior смотрит имена колонок. Нужно читать Hash Key.",
                "type": "cards",
                "cards": [
                    ["SQL", "fact ⋈ (biz_key, max(version)) — classic SCD2 latest.", "amber"],
                    ["Иллюзия", "DISTRIBUTED BY (biz_key, version_id) + USING тех же полей.", "red"],
                    ["Факт", "hash(пары) ≠ hash(biz_key) → Redistribute обязателен.", "blue"],
                    ["Фикс", "Модель: DISTRIBUTED BY (biz_key). Не «ещё ANALYZE».", "green"],
                ],
            },
            {
                "kicker": "Кейс 03 · План",
                "title": "A → B → C на стенде",
                "subtitle": "\\i lesson03-principal-scd2-locus.sql",
                "type": "code",
                "code_kind": "PLAN",
                "code": (
                    "A) composite dist + CTE max → Redistribute Hash Key: biz_key\n"
                    "B) TEMP latest BY (biz_key) → Redistribute FACT остаётся\n"
                    "C) fact BY (biz_key) → local join, только Gather\n\n"
                    "Бонус: int ⋈ int8 → Redistribute Hash Key: (id)::bigint"
                ),
            },
        ]
    )

    # --- Case 04: NOT IN ---
    slides.append(
        case_title(
            anchor="case-not-in",
            num="04",
            title="NOT IN раздувает Broadcast",
            subtitle="Антифильтр, который тиражирует всю внутреннюю таблицу.",
            problem="NOT IN (SELECT …) → Hash Left Anti Semi (Not-In) + Broadcast inner.",
            plan_signal="Broadcast Motion всей t2 на каждый сегмент.",
            fix="NOT EXISTS или LEFT JOIN … IS NULL + co-located ключи.",
            lab="lesson03-secret18-not-in-broadcast.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 04 · Суть",
                "title": "Что → как → почему → фикс",
                "subtitle": "Семантика Not-In (+ NULL) ≠ обычный anti-join.",
                "type": "cards",
                "cards": [
                    ["Что", "WHERE t1.n NOT IN (SELECT n FROM t2).", "amber"],
                    ["Как", "Not-In Join; часто Broadcast полной t2.", "red"],
                    ["Почему", "Xform Not-In + семантика NULL.", "blue"],
                    ["Фикс", "NOT EXISTS / LEFT JOIN IS NULL.", "green"],
                ],
            },
            {
                "kicker": "Кейс 04 · План",
                "title": "Broadcast vs Hash Anti",
                "subtitle": "Lab: форма важнее секунд на 2 seg.",
                "type": "code",
                "code_kind": "PLAN",
                "code": (
                    "A NOT IN:\n"
                    "  Hash Left Anti Semi (Not-In)\n"
                    "    -> Broadcast Motion  ← вся t2\n\n"
                    "B NOT EXISTS:\n"
                    "  Hash Anti Join  ← без Broadcast t2"
                ),
            },
            {
                "kicker": "Кейс 04 · Код GP",
                "title": "Куда смотреть в исходниках",
                "subtitle": "ORCA xform + Motion executor.",
                "type": "cards",
                "cards": [
                    [
                        "Xform Not-In",
                        f"{GPDB_ORCA}/libgpopt/src/xforms/CXformLeftAntiSemiJoinNotIn2HashJoinNotIn.cpp",
                        "red",
                    ],
                    [
                        "Broadcast",
                        f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp",
                        "amber",
                    ],
                    [
                        "Motion",
                        f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c",
                        "blue",
                    ],
                    ["Deep-dive", "deep-dives/secret18-not-in-broadcast.md", "green"],
                ],
            },
        ]
    )

    # --- Case 05: Window ---
    slides.append(
        case_title(
            anchor="case-window",
            num="05",
            title="Окно по константе → сегмент-жертва",
            subtitle="PARTITION BY ключ с NDV=1 собирает всю таблицу на один сегмент.",
            problem="WindowAgg требует все строки partition key вместе.",
            plan_signal="Redistribute Motion … Hash Key: <partition col>.",
            fix="Убрать бессмысленный PARTITION BY или DISTRIBUTED BY реальному ключу.",
            lab="lesson03-secret14-window-partition-skew.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 05 · Суть",
                "title": "Коллапс параллелизма",
                "subtitle": "Константа invalid_id = один hash = один QE.",
                "type": "cards",
                "cards": [
                    ["Что", "row_number() OVER (PARTITION BY invalid_id …).", "amber"],
                    ["Как", "Redistribute на partition key.", "red"],
                    ["Почему", "NDV=1 → victim segment, spill/workfile.", "blue"],
                    ["Фикс", "Смысл ключа? Иначе убрать PARTITION BY.", "green"],
                ],
            },
            {
                "kicker": "Кейс 05 · План",
                "title": "Redistribute → без Motion → rewrite",
                "subtitle": "\\i lesson03-secret14-window-partition-skew.sql",
                "type": "code",
                "code_kind": "PLAN",
                "code": (
                    "A) BY (id) + PARTITION BY const → Redistribute Hash Key: invalid_id\n"
                    "C) BY (invalid_id) → Motion нет, но NDV=1 → всё равно один seg\n"
                    "D) без PARTITION BY → Gather + WindowAgg (если ключ мусор)"
                ),
            },
            {
                "kicker": "Кейс 05 · Код GP",
                "title": "WindowAgg + hash-distribute",
                "subtitle": "deep-dives/secret14-window-partition-skew.md",
                "type": "cards",
                "cards": [
                    ["WindowAgg", f"{GPDB_ARCHIVE}/src/backend/executor/nodeWindowAgg.c", "green"],
                    [
                        "ORCA window",
                        f"{GPDB_ORCA}/libgpopt/src/xforms/CXformImplementSequenceProject.cpp",
                        "blue",
                    ],
                    [
                        "Hash Motion",
                        f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp",
                        "amber",
                    ],
                    ["Deep-dive", "secret14-window-partition-skew.md", "red"],
                ],
            },
        ]
    )

    # --- Case 06: VALUES ---
    slides.append(
        case_title(
            anchor="case-values",
            num="06",
            title="Параметры в VALUES двигают fact",
            subtitle="Красивый CTE с параметрами — едет большая таблица, не params.",
            problem="WITH data_batch AS (VALUES …) JOIN fact без ключа/статы.",
            plan_signal="Lab: Gather fact→QD; prod: часто Broadcast fact.",
            fix="WHERE/литералы; или DISTRIBUTED BY join-ключа + ANALYZE.",
            lab="lesson03-secret29-values-params-broadcast.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 06 · Суть",
                "title": "Какую сторону двигает Motion?",
                "subtitle": "Всегда читайте сторону Broadcast/Gather.",
                "type": "cards",
                "cards": [
                    ["Что", "CTE VALUES «параметры отчёта» ⋈ fact.", "amber"],
                    ["Как", "Fact едет к params (Gather/Broadcast).", "red"],
                    ["Почему", "CE rows≈1 без ANALYZE + RANDOM dist.", "blue"],
                    ["Фикс", "Scalar WHERE или dist key + ANALYZE.", "green"],
                ],
            },
            {
                "kicker": "Кейс 06 · План",
                "title": "A Gather → B local → D filter",
                "subtitle": "\\i lesson03-secret29-values-params-broadcast.sql",
                "type": "code",
                "code_kind": "PLAN",
                "code": (
                    "A RANDOM, no ANALYZE: Hash Join → Gather/Broadcast fact\n"
                    "B DISTRIBUTED BY (n_txt): Seq Scan fact, без Motion fact\n"
                    "D WHERE n_txt = '10': Filter — без join к VALUES\n"
                    "E IN (VALUES) ≠ IN list → ANY filter"
                ),
            },
            {
                "kicker": "Кейс 06 · Код GP",
                "title": "Motion + CE defaults",
                "subtitle": "deep-dives/secret29-values-params-broadcast.md",
                "type": "cards",
                "cards": [
                    [
                        "Broadcast",
                        f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp",
                        "red",
                    ],
                    [
                        "Hash redistribute",
                        f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp",
                        "amber",
                    ],
                    ["selfuncs", f"{GPDB_ARCHIVE}/src/backend/utils/adt/selfuncs.c", "blue"],
                    ["Deep-dive", "secret29-values-params-broadcast.md", "green"],
                ],
            },
        ]
    )

    # --- Case 07: DISTINCT map ---
    slides.append(
        case_title(
            anchor="case-distinct",
            num="07",
            title="Считаем DISTINCT по сегментам",
            subtitle="Map count(DISTINCT) на каждом seg → SUM. Exact только при dist key.",
            problem="Глобальный COUNT(DISTINCT) на огромной AOCO — spill/timeout.",
            plan_signal="Тяжёлый Aggregate/spill; map-версия — двухфазный HashAggregate.",
            fix="sum(cnt) GROUP BY gp_segment_id, если DISTINCT ⊆ DISTRIBUTED BY.",
            lab="lesson03-secret42-distinct-by-segment.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 07 · Суть",
                "title": "Exact vs overcount",
                "subtitle": "Фаза D стенда — обязательный negative case.",
                "type": "cards",
                "cards": [
                    ["Что", "COUNT(DISTINCT id) на большой AOCO.", "amber"],
                    ["Как", "sum(count DISTINCT) … GROUP BY gp_segment_id.", "blue"],
                    ["Exact", "Только если id на одном seg (dist key).", "green"],
                    ["Ловушка", "DISTRIBUTED RANDOMLY → SUM завышает.", "red"],
                ],
            },
            {
                "kicker": "Кейс 07 · План",
                "title": "Canonical vs map",
                "subtitle": "Lab может быть медленнее map — учим контракт exactness.",
                "type": "code",
                "code_kind": "PLAN",
                "code": (
                    "A) count(DISTINCT id) → Aggregate → Gather\n"
                    "B) sum per gp_segment_id → HashAggregate (seg, id) → sum\n"
                    "C) canonical = mapped\n"
                    "D) RANDOM: mapped > canonical"
                ),
            },
            {
                "kicker": "Кейс 07 · Код GP",
                "title": "Agg + GbAgg xform",
                "subtitle": "deep-dives/secret42-distinct-by-segment.md",
                "type": "cards",
                "cards": [
                    ["nodeAgg", f"{GPDB_ARCHIVE}/src/backend/executor/nodeAgg.c", "green"],
                    [
                        "ORCA HashAgg",
                        f"{GPDB_ORCA}/libgpopt/src/xforms/CXformGbAgg2HashAgg.cpp",
                        "blue",
                    ],
                    ["Motion", f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c", "amber"],
                    ["Контракт", "Exact только при coverage DISTINCT dist-ключом.", "red"],
                ],
            },
        ]
    )

    # --- Case 08: Autostats ---
    slides.append(
        case_title(
            anchor="case-autostats",
            num="08",
            title="Autostats молчит после INSERT в parent",
            subtitle="on_no_stats ≠ «стата появится сама» для партиций.",
            problem="INSERT в top-level parent не триггерит autostats на leaves.",
            plan_signal="Каталог: leaves MISSING pg_statistic после parent load.",
            fix="Явный ANALYZE parent/leaves в ETL; insert в leaf — другой контракт.",
            lab="lesson03-secret41-autostats-partitions.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 08 · Суть",
                "title": "Parent miss → leaf hit → ANALYZE",
                "subtitle": "Документированное поведение GP6, не баг.",
                "type": "cards",
                "cards": [
                    ["Что", "INSERT в parent партицированной таблицы.", "amber"],
                    ["Как", "gp_autostats_mode=on_no_stats не обновляет tree.", "red"],
                    ["Почему", "Autostats с leaf insert, не с parent.", "blue"],
                    ["Фикс", "ANALYZE в runbook ETL + проверка catalog.", "green"],
                ],
            },
            {
                "kicker": "Кейс 08 · Демо",
                "title": "Три шага на стенде",
                "subtitle": "\\i lesson03-secret41-autostats-partitions.sql",
                "type": "code",
                "code_kind": "SQL",
                "code": (
                    "SET gp_autostats_mode = on_no_stats;\n"
                    "INSERT INTO lesson03.sec41_sales …;     -- parent → MISSING\n"
                    "INSERT INTO lesson03.sec41_sales_1_prt_1 …; -- leaf → HAS stats\n"
                    "ANALYZE lesson03.sec41_sales;            -- ETL policy"
                ),
            },
            {
                "kicker": "Кейс 08 · Код GP",
                "title": "analyze.c + GUC",
                "subtitle": "deep-dives/secret41-autostats-partitions.md",
                "type": "cards",
                "cards": [
                    ["ANALYZE", f"{GPDB_ARCHIVE}/src/backend/commands/analyze.c", "green"],
                    ["GUC", f"{GPDB_ARCHIVE}/src/backend/utils/misc/guc.c", "blue"],
                    ["Док", "parent insert ≠ autostats; leaf insert = autostats.", "amber"],
                    ["Рядом", "gp_autostats_mode_in_functions внутри функции.", "red"],
                ],
            },
        ]
    )

    # --- Case 09: Median ---
    slides.append(
        case_title(
            anchor="case-median",
            num="09",
            title="Медиана собирает все строки на мастер",
            subtitle="Ordered-set aggregate = полный порядок = Gather-all на QD.",
            problem="percentile_disc глобально не считается локально exact.",
            plan_signal="Gather Motion N:1 почти всех rows → Aggregate на QD.",
            fix="Exact: мириться с Gather / sample. Approx: avg(local median) при RANDOM.",
            lab="lesson03-secret38-median-gather-qd.sql",
        )
    )
    slides.extend(
        [
            {
                "kicker": "Кейс 09 · Суть",
                "title": "Pure MPP theory",
                "subtitle":
                "Глобальный порядок нельзя посчитать по кускам без потерь.",
                "type": "cards",
                "cards": [
                    ["Что", "percentile_disc(0.5) WITHIN GROUP (ORDER BY n).", "amber"],
                    ["Как", "Gather почти всех строк на QD.", "red"],
                    ["Approx", "avg(local median) GROUP BY gp_segment_id.", "blue"],
                    ["Цена", "Помечать approximate в отчётах.", "green"],
                ],
            },
            {
                "kicker": "Кейс 09 · План",
                "title": "Exact Gather vs local medians",
                "subtitle": "Legacy показывает классическую форму; ORCA часто fallback.",
                "type": "code",
                "code_kind": "PLAN",
                "code": (
                    "A exact:\n"
                    "  Aggregate → Gather Motion (все rows) → Seq Scan\n\n"
                    "B approx:\n"
                    "  avg(percentile_disc … GROUP BY gp_segment_id)\n\n"
                    "Lab median=500; approx≈500.5"
                ),
            },
            {
                "kicker": "Кейс 09 · Код GP",
                "title": "orderedsetaggs.c",
                "subtitle": "deep-dives/secret38-median-gather-qd.md",
                "type": "cards",
                "cards": [
                    [
                        "Ordered-set",
                        f"{GPDB_ARCHIVE}/src/backend/utils/adt/orderedsetaggs.c",
                        "green",
                    ],
                    ["nodeAgg", f"{GPDB_ARCHIVE}/src/backend/executor/nodeAgg.c", "blue"],
                    ["Motion", f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c", "amber"],
                    ["Теория", "Глобальный порядок = данные к одному месту.", "red"],
                ],
            },
        ]
    )

    return slides


CASE_SLIDES = build_case_slides()
