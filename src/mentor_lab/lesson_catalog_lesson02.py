"""Lesson 02 catalog content kept separate from the LessonCatalog facade."""

from mentor_lab.lesson_catalog import Lesson, LessonStep


def lesson02() -> Lesson:
    """Return the Lesson 02 curriculum."""

    return Lesson(
        code="lesson-02",
        title="Partitioning, statistics and incremental loads in MPP",
        steps=[
            LessonStep(
                1,
                "Replay evidence from Lesson 01",
                "review",
                10,
                "Start from evidence quality before adding new physical design.",
                "Open the replay pack and ask which marker is missing.",
                "Name the weakest evidence gap from the previous homework.",
                "Student can connect Lesson 01 plan evidence to Lesson 02 design.",
            ),
            LessonStep(
                2,
                "Partition pruning and retention",
                "practice",
                15,
                "Separate partitioning from distribution using real predicates.",
                "Compare bad and good partition keys with EXPLAIN.",
                "Explain why sale_date pruning does not guarantee co-located joins.",
                "Student chooses partition key by filters/retention, not by habit.",
            ),
            LessonStep(
                3,
                "Statistics after incremental load",
                "practice",
                15,
                "Show why ANALYZE is part of the load contract.",
                "Inspect pg_stat_user_tables and compare plan estimates.",
                "Write when statistics must be refreshed after a load window.",
                "Student links stale estimates to bad Broadcast or Redistribute Motion.",
            ),
            LessonStep(
                4,
                "Late-arriving facts and idempotency",
                "design",
                12,
                "Design an incremental load that survives delayed facts.",
                "Walk through stage, bounded reload window, validation, and retry.",
                "Choose a strategy for facts that arrive after the reporting day.",
                "Student proposes bounded reload or partition-level replace with checks.",
            ),
            LessonStep(
                5,
                "AOCO partitions and maintenance",
                "advanced",
                10,
                "Connect column storage with append-heavy partitioned facts.",
                "Show AOCO DDL, catalog inspection, ATTACH/DETACH snippets.",
                "Explain which maintenance command is safe to run in class.",
                "Student can inspect partitions and name retention operations.",
            ),
            LessonStep(
                6,
                "Homework handoff and next lesson",
                "assessment",
                3,
                "Turn the class into a reproducible mini-project.",
                "Give homework deliverables, self-check commands, and rubric.",
                "Repeat what they will bring to the next session.",
                "Student leaves with DDL, EXPLAIN, stats policy, and validation tasks.",
            ),
        ],
    )


def lesson02_hints() -> dict[str, list[str]]:
    """Return progressive hints for Lesson 02."""

    return {
        "partition-pruning": [
            "Start with the WHERE predicate: partition pruning works only when the filter constrains the partition key.",
            "Compare EXPLAIN for the same date range on a table partitioned by load timestamp and by sale_date.",
            "Keep distribution separate: DISTRIBUTED BY controls segment placement and join locality.",
        ],
        "statistics": [
            "ANALYZE belongs to the load contract whenever a partition receives meaningful new data.",
            "Compare estimated rows before and after ANALYZE before changing DDL.",
            "Check pg_stat_user_tables and explain how stale estimates can change Motion and join strategy.",
        ],
        "incremental-loads": [
            "Write the load window first: source range, target partitions, retry behavior, and validation queries.",
            "Make the load idempotent with stage tables, deterministic keys, or partition-level replacement.",
            "Collect row counts and checksum-style aggregates before and after publishing the partition.",
        ],
        "late-arriving-facts": [
            "Treat late-arriving facts as a product requirement, not as an exception path.",
            "Use a bounded reload window when facts commonly arrive a few days late.",
            "Document what happens when a late fact lands outside the retention or correction window.",
        ],
        "aoco-maintenance": [
            "AOCO is a storage choice for scan-heavy append facts; it does not replace partitioning or distribution.",
            "Inspect leaf partitions with pg_partition_tree and gp_toolkit.gp_partitions before maintenance.",
            "Show ATTACH/DETACH as admin snippets; run destructive retention only in controlled practice.",
        ],
    }
