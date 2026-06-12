"""Catalog of realistic Greenplum query tuning exercises."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class QueryTuningTask:
    code: str
    title: str
    symptom: str
    investigation: str
    success_criteria: List[str]


class QueryTuningCatalog:
    """Read-only tuning task catalog."""

    def __init__(self, tasks_by_lab: Dict[str, List[QueryTuningTask]]) -> None:
        self._tasks_by_lab = tasks_by_lab

    @classmethod
    def default(cls) -> "QueryTuningCatalog":
        return cls(
            {
                "greenplum": [
                    QueryTuningTask(
                        "missing-statistics",
                        "Statistics are stale after load",
                        "Optimizer estimates differ sharply from Rows out.",
                        "Run ANALYZE and compare EXPLAIN before/after.",
                        ["Show old estimate", "Run ANALYZE", "Show changed plan or estimate"],
                    ),
                    QueryTuningTask(
                        "redistribute-join",
                        "Join redistributes a large fact",
                        "Redistribute Motion appears before Hash Join on the fact side.",
                        "Compare distribution key with join key and test a co-located version.",
                        ["Name moved rows", "Name join key", "Propose distribution strategy"],
                    ),
                    QueryTuningTask(
                        "bad-partitioning",
                        "Filter cannot prune partitions",
                        "Query scans more date ranges than the business question needs.",
                        "Align partition key with retention/pruning workload.",
                        ["Name filter column", "Name partition key", "Explain pruning risk"],
                    ),
                    QueryTuningTask(
                        "large-gather",
                        "Too many rows return to coordinator",
                        "Gather Motion carries an unnecessarily large intermediate result.",
                        "Push aggregate/filter to segments before final gather.",
                        ["Find Gather Motion", "Estimate result size", "Push local reduction"],
                    ),
                    QueryTuningTask(
                        "storage-model-choice",
                        "Heap used for append-heavy analytical fact",
                        "Large scan-heavy fact behaves like a mutable OLTP table.",
                        "Evaluate AO row vs AOCO column with compression.",
                        ["Name workload", "Choose storage", "Explain compression trade-off"],
                    ),
                ]
            }
        )

    def list(self, lab_name: str) -> List[QueryTuningTask]:
        return list(self._tasks(lab_name))

    def get(self, lab_name: str, code: str) -> QueryTuningTask:
        for task in self._tasks(lab_name):
            if task.code == code:
                return task
        available = ", ".join(task.code for task in self._tasks(lab_name))
        raise KeyError(f"Unknown tuning task '{code}'. Available tasks: {available}.")

    def _tasks(self, lab_name: str) -> Iterable[QueryTuningTask]:
        try:
            return self._tasks_by_lab[lab_name]
        except KeyError as exc:
            available = ", ".join(self._tasks_by_lab)
            raise KeyError(f"Unknown lab '{lab_name}'. Available labs: {available}.") from exc
