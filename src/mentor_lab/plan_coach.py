"""Opinionated coaching layer on top of Greenplum EXPLAIN analysis."""

from dataclasses import dataclass
from typing import Optional

from mentor_lab.explain_analyzer import ExplainAnalysis, ExplainPlanAnalyzer


@dataclass(frozen=True)
class PlanCoachReport:
    lab_name: str
    query_code: str
    analysis: ExplainAnalysis

    def render(self) -> str:
        lines = [
            f"# Query Plan Coach: {self.lab_name}",
            "",
            f"Query: `{self.query_code}`",
            "",
            "## What the plan says",
        ]
        for motion, count in self.analysis.motion_counts.items():
            lines.append(f"- {motion}: {count}")
        lines.append(f"- Join algorithms: {', '.join(self.analysis.join_algorithms) or 'not detected'}")
        lines.append(f"- Slices: {', '.join(self.analysis.slices) or 'not detected'}")

        lines.extend(
            [
                "",
                "## Root cause hypothesis",
                self._root_cause(),
                "",
                "## Next SQL to run",
                "```sql",
                "EXPLAIN ANALYZE",
                ExplainPlanAnalyzer.query_sql(self.query_code) + ";",
                "",
                "SELECT gp_segment_id, count(*) AS rows_on_segment",
                "FROM lesson01.fact_sales_bad",
                "GROUP BY gp_segment_id",
                "ORDER BY gp_segment_id;",
                "```",
                "",
                "## Mentor prompts",
                "- Какая сторона join переезжает по interconnect?",
                "- Этот Motion связан с join key, group key или финальным result set?",
                "- Какой evidence докажет, что изменение помогло?",
                "",
            ]
        )
        return "\n".join(lines)

    def _root_cause(self) -> str:
        motion = self.analysis.motion_counts
        if motion.get("Redistribute Motion", 0) >= 2:
            return (
                "Вероятна неудачная locality join: строки крупной таблицы "
                "перераспределяются по join/group key перед локальной работой."
            )
        if motion.get("Broadcast Motion", 0):
            return (
                "План копирует одну сторону join на все segments. Это нормально только "
                "для маленькой dimension с актуальной статистикой."
            )
        if motion.get("Gather Motion", 0):
            return (
                "Финальный результат идет к coordinator. Нужно проверить, что до Gather "
                "уже выполнены фильтрация и агрегация."
            )
        return "Крупных MPP-сигналов не видно; проверь estimates, statistics и фильтры."


class PlanCoach:
    """Builds mentor-friendly explanations from raw or sampled EXPLAIN plans."""

    def __init__(self, analyzer: Optional[ExplainPlanAnalyzer] = None) -> None:
        self._analyzer = analyzer or ExplainPlanAnalyzer()

    def coach(self, lab_name: str, query_code: str, plan: str) -> PlanCoachReport:
        return PlanCoachReport(
            lab_name=lab_name,
            query_code=query_code,
            analysis=self._analyzer.analyze(plan),
        )
