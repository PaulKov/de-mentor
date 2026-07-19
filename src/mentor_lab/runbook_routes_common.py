"""Shared links for Greenplum mentor runbooks."""

from typing import List


def greenplum_common_links() -> List[str]:
    return [
        "decks/greenplum-theory/facilitator-guide.md",
        "docs/lessons/01-greenplum/runbooks/student-prep.md",
        "docs/lessons/01-greenplum/student-workbook.md",
        "docs/lessons/01-greenplum/homework.md",
        "labs/greenplum-625/examples/cluster-monitoring.sql",
        "labs/greenplum-625/examples/storage-and-partitioning.sql",
        "labs/greenplum-625/examples/partitioning-strategies.sql",
        "docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md",
    ]


def greenplum_partitioning_links() -> List[str]:
    return [
        "docs/lessons/02-greenplum-partitioning/README.md",
        "docs/lessons/02-greenplum-partitioning/student-workbook.md",
        "docs/lessons/02-greenplum-partitioning/homework.md",
        "docs/lessons/02-greenplum-partitioning/runbooks/homework-plan.md",
        "labs/greenplum-625/examples/lesson02-partitioning-statistics-loads.sql",
        "labs/greenplum-625/examples/partitioning-strategies.sql",
        "docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md",
    ]


def greenplum_query_tuning_links() -> List[str]:
    return [
        "docs/lessons/03-greenplum-query-tuning/README.md",
        "docs/lessons/03-greenplum-query-tuning/student-workbook.md",
        "docs/lessons/03-greenplum-query-tuning/homework.md",
        "docs/lessons/03-greenplum-query-tuning/runbooks/homework-plan.md",
        "docs/lessons/03-greenplum-query-tuning/deep-dives/pg-statistic-internals.md",
        "docs/lessons/03-greenplum-query-tuning/deep-dives/storage-physical-layout.md",
        "docs/lessons/03-greenplum-query-tuning/deep-dives/temp-tables-and-spill.md",
        "labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql",
        "labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql",
        "docs/lessons/03-greenplum-query-tuning/deep-dives/optimizer-legacy-vs-orca.md",
    ]
