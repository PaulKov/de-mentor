"""Lesson telemetry summaries for mentor follow-up."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TelemetryReport:
    pre_score: int
    post_score: int
    review_score: int

    @property
    def growth(self) -> int:
        return self.post_score - self.pre_score

    def render(self) -> str:
        return "\n".join(
            [
                "# Lesson telemetry",
                "",
                f"Pre-score: {self.pre_score}/100",
                f"Post-score: {self.post_score}/100",
                f"Submission review: {self.review_score}/100",
                f"Growth: {self.growth:+d}",
                "",
                "## Interpretation",
                f"- {self._interpretation()}",
                "",
                "## Recommended next focus",
                f"- {self._next_focus()}",
                "",
            ]
        )

    def _interpretation(self) -> str:
        if self.growth >= 40 and self.review_score >= 80:
            return "The student converted theory into practical diagnostic evidence."
        if self.growth >= 25:
            return "The student learned the concepts, but evidence quality needs reinforcement."
        return "The student needs another guided pass through the core MPP mental model."

    def _next_focus(self) -> str:
        if self.review_score < 75:
            return "Broadcast vs Redistribute evidence and RCA structure."
        if self.post_score < 80:
            return "Coordinator bottlenecks, Gather Motion, and runtime diagnostics."
        return "Hard timed challenge with large Gather and partition pruning."
