"""Golden and anti-solution catalog for mentor debriefs."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class Solution:
    lab: str
    code: str
    title: str
    golden: str
    anti_solution: str
    mentor_notes: List[str]

    def render(self) -> str:
        lines = [
            f"# Solution: {self.title}",
            "",
            "## Golden solution",
            self.golden,
            "",
            "## Anti-solution",
            self.anti_solution,
            "",
            "## Mentor notes",
        ]
        lines.extend(f"- {note}" for note in self.mentor_notes)
        return "\n".join(lines) + "\n"


class SolutionCatalog:
    """Read-only solution key for live mentor discussion."""

    def __init__(self, solutions_by_lab: Dict[str, List[Solution]]) -> None:
        self._solutions_by_lab = solutions_by_lab

    @classmethod
    def default(cls) -> "SolutionCatalog":
        return cls(
            {
                "greenplum": [
                    Solution(
                        lab="greenplum",
                        code="redistribute-join",
                        title="Large fact join is redistributed",
                        golden=(
                            "Use the dominant large fact join key as the distribution key, "
                            "for example `DISTRIBUTED BY (customer_id)`, then validate with "
                            "`EXPLAIN` and `gp_segment_id` distribution checks."
                        ),
                        anti_solution=(
                            "Adding indexes or increasing memory without changing data placement "
                            "does not remove the interconnect cost of a large Redistribute Motion."
                        ),
                        mentor_notes=[
                            "Ask which side moves before discussing DDL.",
                            "Separate final Gather from join redistribution.",
                        ],
                    ),
                    Solution(
                        lab="greenplum",
                        code="stale-statistics",
                        title="Optimizer sees stale cardinality",
                        golden=(
                            "Run `ANALYZE` after the load, compare estimates before and after, "
                            "and only then decide whether physical design needs to change."
                        ),
                        anti_solution=(
                            "Rebuilding the table before checking statistics hides the root cause "
                            "and teaches cargo-cult tuning."
                        ),
                        mentor_notes=[
                            "Make the student quote estimated rows and actual Rows out.",
                        ],
                    ),
                    Solution(
                        lab="greenplum",
                        code="large-gather",
                        title="Large result gathers on coordinator",
                        golden=(
                            "Push filters and partial aggregation down to segments so only a small "
                            "final result reaches the coordinator."
                        ),
                        anti_solution=(
                            "Treating the coordinator as a parallel worker creates a single-process bottleneck."
                        ),
                        mentor_notes=[
                            "Tie this back to QD versus QE responsibility.",
                        ],
                    ),
                ]
            }
        )

    def list(self, lab_name: str) -> List[Solution]:
        return list(self._solutions(lab_name))

    def get(self, lab_name: str, solution_code: str) -> Solution:
        for solution in self._solutions(lab_name):
            if solution.code == solution_code:
                return solution
        available = ", ".join(solution.code for solution in self._solutions(lab_name))
        raise KeyError(
            f"Unknown solution '{solution_code}' for {lab_name}. "
            f"Available solutions: {available}."
        )

    def _solutions(self, lab_name: str) -> Iterable[Solution]:
        try:
            return self._solutions_by_lab[lab_name]
        except KeyError as exc:
            available = ", ".join(self._solutions_by_lab)
            raise KeyError(f"Unknown lab '{lab_name}'. Available labs: {available}.") from exc
