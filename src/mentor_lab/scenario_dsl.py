"""Engine-neutral scenario DSL for repeatable academy exercises."""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ScenarioCheck:
    kind: str
    target: str
    expected: str

    def render(self) -> str:
        return f"  - type: {self.kind}\n    target: {self.target}\n    expected: {self.expected}"


@dataclass(frozen=True)
class ScenarioDefinition:
    lab: str
    engine: str
    code: str
    title: str
    difficulty: str
    seed_profile: str
    skills: List[str]
    checks: List[ScenarioCheck]
    tasks: List[str]
    acceptance_criteria: List[str]

    def render(self) -> str:
        lines = [
            f"scenario: {self.code}",
            f"title: {self.title}",
            f"engine: {self.engine}",
            f"difficulty: {self.difficulty}",
            f"seed_profile: {self.seed_profile}",
            "skills:",
        ]
        lines.extend(f"  - {skill}" for skill in self.skills)
        lines.append("tasks:")
        lines.extend(f"  - {task}" for task in self.tasks)
        lines.append("checks:")
        lines.extend(check.render() for check in self.checks)
        lines.append("acceptance_criteria:")
        lines.extend(f"  - {item}" for item in self.acceptance_criteria)
        return "\n".join(lines) + "\n"


class ScenarioDslCatalog:
    """Catalog of engine-neutral scenarios for current and future labs."""

    def __init__(self, scenarios_by_lab: Dict[str, List[ScenarioDefinition]]) -> None:
        self._scenarios_by_lab = scenarios_by_lab

    @classmethod
    def default(cls) -> "ScenarioDslCatalog":
        return cls(
            {
                "greenplum": [
                    ScenarioDefinition(
                        lab="greenplum",
                        engine="greenplum",
                        code="redistribute-join",
                        title="Large fact join is redistributed",
                        difficulty="medium",
                        seed_profile="balanced",
                        skills=["EXPLAIN literacy", "Join locality", "Distribution design"],
                        checks=[
                            ScenarioCheck("plan_contains", "bad_customer_join", "Redistribute Motion"),
                            ScenarioCheck("sql_result", "gp_segment_id balance", "less than 10 percentage points spread after fix"),
                        ],
                        tasks=[
                            "Read the plan and identify which side moves.",
                            "Explain why the join is not co-located.",
                            "Propose a corrected distribution strategy.",
                        ],
                        acceptance_criteria=[
                            "Submission names Redistribute Motion and join key.",
                            "Submission includes a validation query or plan comparison.",
                        ],
                    ),
                    ScenarioDefinition(
                        lab="greenplum",
                        engine="greenplum",
                        code="stale-statistics",
                        title="Optimizer chooses from stale cardinality",
                        difficulty="medium",
                        seed_profile="bad-statistics",
                        skills=["Statistics literacy", "Plan estimates", "Validation"],
                        checks=[
                            ScenarioCheck("sql_contains", "investigation", "ANALYZE"),
                            ScenarioCheck("plan_compare", "before_after", "estimate changes"),
                        ],
                        tasks=[
                            "Compare estimates before and after ANALYZE.",
                            "Separate statistics issues from distribution issues.",
                        ],
                        acceptance_criteria=[
                            "Submission shows stale statistics symptom.",
                            "Submission validates the fix with refreshed plan evidence.",
                        ],
                    ),
                    ScenarioDefinition(
                        lab="greenplum",
                        engine="greenplum",
                        code="large-gather",
                        title="Too many rows gather on the coordinator",
                        difficulty="hard",
                        seed_profile="enterprise",
                        skills=["Coordinator bottleneck", "Aggregation pushdown", "Runtime diagnostics"],
                        checks=[
                            ScenarioCheck("plan_contains", "large_result_query", "Gather Motion"),
                            ScenarioCheck("design_rule", "fix", "aggregate before final gather"),
                        ],
                        tasks=[
                            "Find the Gather Motion.",
                            "Reduce rows before the coordinator path.",
                            "Explain residual coordinator risk.",
                        ],
                        acceptance_criteria=[
                            "Submission explains why the coordinator is the bottleneck.",
                            "Submission proposes local aggregate/filter before Gather.",
                        ],
                    ),
                    ScenarioDefinition(
                        lab="greenplum",
                        engine="greenplum",
                        code="partition-pruning",
                        title="Partition key does not match workload",
                        difficulty="hard",
                        seed_profile="bad-partitioning",
                        skills=["Partition pruning", "Physical design", "Workload modeling"],
                        checks=[
                            ScenarioCheck("sql_contains", "ddl", "PARTITION BY RANGE"),
                            ScenarioCheck("reasoning", "filter", "filter key matches partition key"),
                        ],
                        tasks=[
                            "Identify the filter pattern.",
                            "Explain why the partition key does not prune well.",
                        ],
                        acceptance_criteria=[
                            "Submission separates partitioning from distribution.",
                            "Submission names the workload that benefits from the new partition key.",
                        ],
                    ),
                    ScenarioDefinition(
                        lab="greenplum",
                        engine="greenplum",
                        code="storage-model-choice",
                        title="Heap table used for analytical append fact",
                        difficulty="easy",
                        seed_profile="wide-aoco",
                        skills=["Storage model", "Columnar scan", "Compression trade-off"],
                        checks=[
                            ScenarioCheck("ddl_contains", "fact", "appendoptimized=true"),
                            ScenarioCheck("reasoning", "workload", "wide analytical scan"),
                        ],
                        tasks=[
                            "Compare heap, AO row, and AOCO for the workload.",
                            "Explain why storage format does not replace distribution design.",
                        ],
                        acceptance_criteria=[
                            "Submission names AOCO as a workload fit.",
                            "Submission preserves distribution reasoning.",
                        ],
                    ),
                ]
            }
        )

    def list(
        self, lab_name: str, difficulty: Optional[str] = None
    ) -> List[ScenarioDefinition]:
        scenarios = list(self._scenarios(lab_name))
        if difficulty:
            scenarios = [scenario for scenario in scenarios if scenario.difficulty == difficulty]
        return scenarios

    def get(self, lab_name: str, scenario_code: str) -> ScenarioDefinition:
        for scenario in self._scenarios(lab_name):
            if scenario.code == scenario_code:
                return scenario
        available = ", ".join(scenario.code for scenario in self._scenarios(lab_name))
        raise KeyError(
            f"Unknown scenario '{scenario_code}' for {lab_name}. "
            f"Available scenarios: {available}."
        )

    def _scenarios(self, lab_name: str) -> Iterable[ScenarioDefinition]:
        try:
            return self._scenarios_by_lab[lab_name]
        except KeyError as exc:
            available = ", ".join(self._scenarios_by_lab)
            raise KeyError(f"Unknown lab '{lab_name}'. Available labs: {available}.") from exc
