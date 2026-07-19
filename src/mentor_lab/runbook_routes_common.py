"""Shared links for Greenplum mentor runbooks."""

from typing import List


def greenplum_common_links() -> List[str]:
    return [
        "decks/greenplum-theory/facilitator-guide.md",
        "lessons/lesson-01/docs/runbooks/student-prep.md",
        "lessons/lesson-01/docs/student-workbook.md",
        "lessons/lesson-01/homework/assignment.md",
        "labs/greenplum-625/examples/cluster-monitoring.sql",
        "labs/greenplum-625/examples/storage-and-partitioning.sql",
        "labs/greenplum-625/examples/partitioning-strategies.sql",
        "lessons/lesson-01/docs/deep-dives/partitioning-strategies.md",
    ]


def greenplum_partitioning_links() -> List[str]:
    return [
        "lessons/lesson-02/docs/README.md",
        "lessons/lesson-02/docs/student-workbook.md",
        "lessons/lesson-02/homework/assignment.md",
        "lessons/lesson-02/homework/plan.md",
        "labs/greenplum-625/examples/lesson02-partitioning-statistics-loads.sql",
        "labs/greenplum-625/examples/partitioning-strategies.sql",
        "lessons/lesson-01/docs/deep-dives/partitioning-strategies.md",
    ]


def greenplum_query_tuning_links() -> List[str]:
    return [
        "lessons/lesson-03/docs/README.md",
        "lessons/lesson-03/docs/student-workbook.md",
        "lessons/lesson-03/homework/assignment.md",
        "lessons/lesson-03/homework/plan.md",
        "lessons/lesson-03/docs/deep-dives/pg-statistic-internals.md",
        "lessons/lesson-03/docs/deep-dives/storage-physical-layout.md",
        "lessons/lesson-03/docs/deep-dives/temp-tables-and-spill.md",
        "labs/greenplum-625/examples/lesson03-homework-seed.sql",
        "labs/greenplum-625/examples/lesson03-class-demo.sql",
        "labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql",
        "lessons/lesson-03/homework/templates/evidence.md",
        "lessons/lesson-03/homework/templates/reconcile.sql",
        "labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql",
        "labs/greenplum-625/examples/lesson03-cardinality-histogram-demo.sql",
        "labs/greenplum-625/examples/lesson03-temp-on-commit-lifecycle.sql",
        "labs/greenplum-625/examples/lesson03-stats-analyze-lifecycle.sql",
        "labs/greenplum-625/examples/lesson03-e2e-case-metrics.sql",
        "labs/greenplum-625/examples/lesson03-storage-heap-ao-aoco.sql",
        "labs/greenplum-625/examples/lesson03-nlj-cte-temp-case.sql",
        "labs/greenplum-625/examples/lesson03-orca-ce-trap.sql",
        "labs/greenplum-625/examples/lesson03-legacy-ce-trap.sql",
        "labs/greenplum-625/examples/lesson03-principal-scd2-locus.sql",
        "lessons/lesson-03/docs/deep-dives/optimizer-legacy-vs-orca.md",
        "lessons/lesson-03/docs/deep-dives/principal-scd2-locus-redistribute.md",
        "lessons/lesson-03/artifacts/greenplum-query-tuning-appendix.pptx",
        "lessons/lesson-03/artifacts/case/ce-traps-metrics.md",
        "lessons/lesson-03/artifacts/case/principal-scd2-locus-metrics.md",
    ]
