"""Runtime diagnostics catalog for Greenplum mentoring exercises."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class DiagnosticProbe:
    code: str
    title: str
    skill: str
    description: str
    sql: str

    def render(self) -> str:
        return "\n".join(
            [
                f"# Diagnostic: {self.title}",
                "",
                f"Skill: {self.skill}",
                "",
                self.description,
                "",
                "```sql",
                self.sql,
                "```",
                "",
            ]
        )


class DiagnosticsCatalog:
    """Read-only diagnostics that can be shown or executed from the CLI."""

    def __init__(self, probes_by_lab: Dict[str, List[DiagnosticProbe]]) -> None:
        self._probes_by_lab = probes_by_lab

    @classmethod
    def default(cls) -> "DiagnosticsCatalog":
        return cls(
            {
                "greenplum": [
                    DiagnosticProbe(
                        "segment-skew",
                        "Segment skew by table",
                        "MPP diagnostics",
                        "Shows how rows are physically distributed across segments.",
                        (
                            "SELECT gp_segment_id, count(*) AS rows_on_segment\n"
                            "FROM lesson01.fact_sales_bad\n"
                            "GROUP BY gp_segment_id\n"
                            "ORDER BY gp_segment_id;"
                        ),
                    ),
                    DiagnosticProbe(
                        "active-queries",
                        "Active query snapshot",
                        "Runtime observability",
                        "Shows currently active sessions and their wait state.",
                        (
                            "SELECT pid, usename, state, wait_event_type, wait_event, query\n"
                            "FROM pg_stat_activity\n"
                            "WHERE state <> 'idle'\n"
                            "ORDER BY query_start NULLS LAST;"
                        ),
                    ),
                    DiagnosticProbe(
                        "table-statistics",
                        "Statistics freshness",
                        "Optimizer literacy",
                        "Surfaces row estimates and analyze timestamps for lesson tables.",
                        (
                            "SELECT schemaname, relname, n_live_tup, last_analyze, last_autoanalyze\n"
                            "FROM pg_stat_user_tables\n"
                            "WHERE schemaname = 'lesson01'\n"
                            "ORDER BY relname;"
                        ),
                    ),
                    DiagnosticProbe(
                        "spill-risk",
                        "Hash join spill risk proxy",
                        "Execution memory",
                        "Combines wide facts and hash joins into a concrete spill discussion.",
                        (
                            "EXPLAIN ANALYZE\n"
                            "SELECT c.region, sum(f.amount)\n"
                            "FROM lesson01.fact_sales_bad f\n"
                            "JOIN lesson01.dim_customers c USING (customer_id)\n"
                            "GROUP BY c.region;"
                        ),
                    ),
                    DiagnosticProbe(
                        "segment-balance",
                        "Good table segment balance",
                        "Distribution validation",
                        "Compares the corrected distribution with the skewed table.",
                        (
                            "SELECT gp_segment_id, count(*) AS rows_on_segment\n"
                            "FROM lesson01.fact_sales_good\n"
                            "GROUP BY gp_segment_id\n"
                            "ORDER BY gp_segment_id;"
                        ),
                    ),
                ]
            }
        )

    def list(self, lab_name: str) -> List[DiagnosticProbe]:
        return list(self._probes(lab_name))

    def get(self, lab_name: str, probe_code: str) -> DiagnosticProbe:
        for probe in self._probes(lab_name):
            if probe.code == probe_code:
                return probe
        available = ", ".join(probe.code for probe in self._probes(lab_name))
        raise KeyError(
            f"Unknown diagnostic probe '{probe_code}' for {lab_name}. "
            f"Available probes: {available}."
        )

    def _probes(self, lab_name: str) -> Iterable[DiagnosticProbe]:
        try:
            return self._probes_by_lab[lab_name]
        except KeyError as exc:
            available = ", ".join(self._probes_by_lab)
            raise KeyError(f"Unknown lab '{lab_name}'. Available labs: {available}.") from exc
