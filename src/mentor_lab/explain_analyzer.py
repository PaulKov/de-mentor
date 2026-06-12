"""Small EXPLAIN plan analyzer for Greenplum learning exercises."""

import re
from dataclasses import dataclass
from typing import Dict, List


_MOTION_TYPES = ("Redistribute Motion", "Broadcast Motion", "Gather Motion")
_JOIN_TYPES = ("Hash Join", "Nested Loop", "Merge Join")


@dataclass(frozen=True)
class ExplainAnalysis:
    plan: str
    motion_counts: Dict[str, int]
    join_algorithms: List[str]
    slices: List[str]
    hash_keys: List[str]
    findings: List[str]
    risks: List[str]


class ExplainPlanAnalyzer:
    """Extracts beginner-relevant MPP signals from Greenplum EXPLAIN text."""

    _QUERY_SQL = {
        "bad_customer_join": (
            "SELECT c.region, sum(f.amount) "
            "FROM lesson01.fact_sales_bad AS f "
            "JOIN lesson01.dim_customers AS c USING (customer_id) "
            "GROUP BY c.region"
        ),
        "good_customer_join": (
            "SELECT c.region, sum(f.amount) "
            "FROM lesson01.fact_sales_good AS f "
            "JOIN lesson01.dim_customers AS c USING (customer_id) "
            "GROUP BY c.region"
        ),
        "product_join": (
            "SELECT p.category, sum(f.amount) "
            "FROM lesson01.fact_sales_good AS f "
            "JOIN lesson01.dim_products AS p USING (product_id) "
            "GROUP BY p.category"
        ),
    }

    _SAMPLE_PLANS = {
        "bad_customer_join": """
Gather Motion 2:1  (slice1; segments: 2)
  -> Finalize HashAggregate
        -> Redistribute Motion 2:2  (slice2; segments: 2)
              Hash Key: dim_customers.region
              -> Streaming Partial HashAggregate
                    -> Hash Join
                          Hash Cond: (fact_sales_bad.customer_id = dim_customers.customer_id)
                          -> Redistribute Motion 2:2  (slice3; segments: 2)
                                Hash Key: fact_sales_bad.customer_id
                                -> Seq Scan on fact_sales_bad
                          -> Hash
                                -> Seq Scan on dim_customers
""",
        "good_customer_join": """
Gather Motion 2:1  (slice1; segments: 2)
  -> Finalize HashAggregate
        -> Redistribute Motion 2:2  (slice2; segments: 2)
              Hash Key: dim_customers.region
              -> Streaming Partial HashAggregate
                    -> Hash Join
                          Hash Cond: (fact_sales_good.customer_id = dim_customers.customer_id)
                          -> Seq Scan on fact_sales_good
                          -> Hash
                                -> Seq Scan on dim_customers
""",
        "product_join": """
Gather Motion 2:1  (slice1; segments: 2)
  -> Finalize HashAggregate
        -> Redistribute Motion 2:2  (slice2; segments: 2)
              Hash Key: dim_products.category
              -> Hash Join
                    Hash Cond: (fact_sales_good.product_id = dim_products.product_id)
                    -> Seq Scan on fact_sales_good
                    -> Hash
                          -> Broadcast Motion 2:2  (slice3; segments: 2)
                                -> Seq Scan on dim_products
""",
    }

    def analyze(self, plan: str) -> ExplainAnalysis:
        motion_counts = {motion: plan.count(motion) for motion in _MOTION_TYPES}
        join_algorithms = [join for join in _JOIN_TYPES if join in plan]
        slices = _unique(re.findall(r"slice\d+", plan))
        hash_keys = _unique(
            match.strip() for match in re.findall(r"Hash Key:\s*([^\n]+)", plan)
        )
        findings = self._findings(motion_counts, join_algorithms, slices)
        risks = self._risks(motion_counts, join_algorithms)
        return ExplainAnalysis(
            plan=plan,
            motion_counts=motion_counts,
            join_algorithms=join_algorithms,
            slices=slices,
            hash_keys=hash_keys,
            findings=findings,
            risks=risks,
        )

    def render(self, analysis: ExplainAnalysis) -> str:
        lines = [
            "# EXPLAIN Analysis",
            "",
            "## Motion nodes",
        ]
        for motion, count in analysis.motion_counts.items():
            lines.append(f"- {motion}: {count}")
        lines.extend(["", "## Join algorithms"])
        if analysis.join_algorithms:
            for join in analysis.join_algorithms:
                lines.append(f"- {join}")
        else:
            lines.append("- No join algorithm detected")
        lines.extend(["", "## Slices", ", ".join(analysis.slices) or "No slices detected"])
        lines.extend(["", "## Hash keys"])
        for key in analysis.hash_keys or ["No hash keys detected"]:
            lines.append(f"- {key}")
        lines.extend(["", "## Findings"])
        for finding in analysis.findings:
            lines.append(f"- {finding}")
        lines.extend(["", "## Risks"])
        for risk in analysis.risks:
            lines.append(f"- {risk}")
        lines.extend(
            [
                "",
                "## Questions to answer",
                "- Which rows move across the interconnect?",
                "- Which join key caused or avoided redistribution?",
                "- Is Gather Motion returning a small final result?",
            ]
        )
        return "\n".join(lines) + "\n"

    @classmethod
    def query_sql(cls, query_code: str) -> str:
        try:
            return cls._QUERY_SQL[query_code]
        except KeyError as exc:
            available = ", ".join(sorted(cls._QUERY_SQL))
            raise KeyError(
                f"Unknown query '{query_code}'. Available queries: {available}."
            ) from exc

    @classmethod
    def sample_plan(cls, query_code: str) -> str:
        try:
            return cls._SAMPLE_PLANS[query_code]
        except KeyError as exc:
            available = ", ".join(sorted(cls._SAMPLE_PLANS))
            raise KeyError(
                f"Unknown sample query '{query_code}'. Available queries: {available}."
            ) from exc

    @staticmethod
    def _findings(
        motion_counts: Dict[str, int],
        join_algorithms: List[str],
        slices: List[str],
    ) -> List[str]:
        findings: List[str] = []
        redistribute_count = motion_counts.get("Redistribute Motion", 0)
        if redistribute_count:
            findings.append(
                f"Network movement: Redistribute Motion appears {redistribute_count} time(s)."
            )
        if motion_counts.get("Broadcast Motion", 0):
            findings.append("Broadcast path: one input is copied to all segments.")
        if motion_counts.get("Gather Motion", 0):
            findings.append("Coordinator path: final rows are gathered to one process.")
        if join_algorithms:
            findings.append(f"Local join algorithm: {', '.join(join_algorithms)}.")
        if slices:
            findings.append(f"Slice boundaries detected: {', '.join(slices)}.")
        return findings or ["No major MPP signals detected."]

    @staticmethod
    def _risks(motion_counts: Dict[str, int], join_algorithms: List[str]) -> List[str]:
        risks: List[str] = []
        if motion_counts.get("Redistribute Motion", 0):
            risks.append("Redistribute Motion can dominate runtime when many rows move.")
        if motion_counts.get("Broadcast Motion", 0):
            risks.append("Broadcast Motion requires a genuinely small input.")
        if motion_counts.get("Gather Motion", 0):
            risks.append("Gather Motion is safe only for small final results.")
        if "Hash Join" in join_algorithms:
            risks.append("Hash Join can spill if the build side exceeds memory.")
        return risks or ["No obvious first-order risk detected."]


def _unique(values) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
