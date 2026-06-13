"""Post-lesson debrief generation for students and mentors."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from mentor_lab.adaptive_review import AdaptiveReview, AdaptiveReviewer
from mentor_lab.misconceptions import MisconceptionCatalog, MisconceptionDiagnosis


@dataclass(frozen=True)
class Debrief:
    lab_name: str
    student_name: str
    pre_score: Optional[int]
    post_score: Optional[int]
    review: AdaptiveReview
    misconceptions: MisconceptionDiagnosis
    submission_path: Path

    @property
    def growth(self) -> Optional[int]:
        if self.pre_score is None or self.post_score is None:
            return None
        return self.post_score - self.pre_score

    def render(self) -> str:
        lab_title = self.lab_name.capitalize()
        lines = [
            f"# Debrief: {self.student_name} / {lab_title}",
            "",
            f"Submission: `{self.submission_path.as_posix()}`",
            f"Score: {self.review.score}/100",
        ]
        if self.growth is not None:
            lines.append(f"Рост: {self.growth:+d}")
        lines.extend(
            [
                "",
                "## Что получилось",
            ]
        )
        lines.extend(f"- {skill}: {score}/100" for skill, score in self.review.skill_scores.items())
        lines.extend(["", "## Что отправить ученику"])
        lines.extend(self._student_message())
        lines.extend(["", "## Misconceptions"])
        if self.misconceptions.matches:
            for card in self.misconceptions.matches:
                lines.extend(
                    [
                        f"- {card.title}: {card.hint}",
                        f"  follow-up: {card.follow_up}",
                    ]
                )
        else:
            lines.append("- Явных misconception patterns не найдено.")
        lines.extend(
            [
                "",
                "## Private mentor notes",
                f"- Next task: {self.review.next_task}",
                "- Начать следующий урок с проверки missing evidence и одного короткого EXPLAIN.",
                "",
            ]
        )
        return "\n".join(lines)

    def _student_message(self) -> list[str]:
        if self.review.score >= 90:
            return [
                "- Сильная работа: есть evidence и причинно-следственная связь.",
                "- Следующий фокус: усложнить задачу timed challenge и coordinator risk.",
            ]
        if self.review.score >= 70:
            return [
                "- База схвачена, но нужно усилить evidence before/after.",
                "- Следующий фокус: `EXPLAIN ANALYZE`, `gp_segment_id`, validation.",
            ]
        return [
            "- Нужно повторить MPP mental model и собрать evidence заново.",
            "- Следующий фокус: Motion, distribution key, join key и RCA.",
        ]


class DebriefGenerator:
    """Builds a concise post-lesson report from a submitted evidence file."""

    @classmethod
    def default(cls) -> "DebriefGenerator":
        return cls(AdaptiveReviewer.default(), MisconceptionCatalog.default())

    def __init__(
        self,
        reviewer: AdaptiveReviewer,
        misconceptions: MisconceptionCatalog,
    ) -> None:
        self._reviewer = reviewer
        self._misconceptions = misconceptions

    def generate(
        self,
        lab_name: str,
        student_name: str,
        submission_path: Path,
        pre_score: Optional[int] = None,
        post_score: Optional[int] = None,
    ) -> Debrief:
        content = submission_path.read_text(encoding="utf-8")
        return Debrief(
            lab_name=lab_name,
            student_name=student_name,
            pre_score=pre_score,
            post_score=post_score,
            review=self._reviewer.review(submission_path),
            misconceptions=self._misconceptions.diagnose(lab_name, content),
            submission_path=submission_path,
        )
