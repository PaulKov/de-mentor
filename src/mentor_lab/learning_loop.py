"""Learning-loop reports that connect assessment, evidence, and next practice."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from mentor_lab.adaptive_review import AdaptiveReview, AdaptiveReviewer


@dataclass(frozen=True)
class SkillMapItem:
    title: str
    score: int
    status: str
    evidence: str
    next_action: str


@dataclass(frozen=True)
class SpacedPracticeItem:
    when: str
    task: str
    check: str


@dataclass(frozen=True)
class LearningLoopReport:
    lab_name: str
    pre_score: int
    post_score: int
    adaptive_review: AdaptiveReview
    skill_map: List[SkillMapItem]
    spaced_practice: List[SpacedPracticeItem]
    submission_path: Optional[Path] = None

    @property
    def growth(self) -> int:
        return self.post_score - self.pre_score

    @property
    def review_score(self) -> int:
        return self.adaptive_review.score

    def render(self) -> str:
        lab_title = self.lab_name.capitalize()
        lines = [
            f"# Learning Loop: {lab_title}",
            "",
            f"Pre-test: {self.pre_score}/100",
            f"Post-test: {self.post_score}/100",
            f"Рост: {self.growth:+d}",
            f"Evidence review: {self.review_score}/100",
            "",
            "## Как Читать Отчет",
            (
                "Карта показывает не общий талант ученика, а ближайшие учебные "
                "рычаги: что уже можно усложнять, что закрепить, а что лучше "
                "повторить с ментором."
            ),
            "",
            "## Карта Навыков",
            "| Навык | Score | Статус | Evidence | Следующее действие |",
            "|---|---:|---|---|---|",
        ]
        for item in self.skill_map:
            lines.append(
                "| "
                f"{item.title} | {item.score}/100 | {item.status} | "
                f"{item.evidence} | {item.next_action} |"
            )

        lines.extend(["", "## Обратная Связь По Evidence"])
        if self.submission_path:
            lines.append(f"- Evidence-файл: `{self.submission_path.as_posix()}`")
        else:
            lines.append(
                "- evidence-файл не передан: отчет построен по ручному `--review` score."
            )
        lines.append("- Рекомендуемый шаблон: `submissions/query-tuning.md`")
        lines.append("- Missing evidence:")
        for marker in self.adaptive_review.missing or ["нет пропущенных evidence markers"]:
            lines.append(f"  - {marker}")
        lines.append(f"- Следующая задача: {_localized_next_task(self.adaptive_review.next_task)}")

        lines.extend(["", "## Интервальная Практика"])
        for item in self.spaced_practice:
            lines.append(f"- **{item.when}**: {item.task} Проверка: {item.check}")

        weak_skill = min(self.skill_map, key=lambda item: item.score)
        lines.extend(
            [
                "",
                "## Следующий Шаг Ментора",
                (
                    f"- Начать следующий touchpoint с навыка `{weak_skill.title}`: "
                    f"{weak_skill.next_action}"
                ),
                "",
            ]
        )
        return "\n".join(lines)


class LearningLoopBuilder:
    """Builds a concise follow-up report for the Greenplum lesson."""

    _SUPPORTED_LABS = {"greenplum"}

    @classmethod
    def default(cls) -> "LearningLoopBuilder":
        return cls(AdaptiveReviewer.default())

    def __init__(self, reviewer: AdaptiveReviewer) -> None:
        self._reviewer = reviewer

    def build(
        self,
        lab_name: str,
        pre_score: int,
        post_score: int,
        submission_path: Optional[Path] = None,
        review_score: Optional[int] = None,
    ) -> LearningLoopReport:
        normalized_lab = lab_name.lower()
        if normalized_lab not in self._SUPPORTED_LABS:
            raise KeyError(f"Unknown learning loop lab: {lab_name}")

        pre = _validated_score(pre_score, "pre_score")
        post = _validated_score(post_score, "post_score")
        review = self._review(submission_path, review_score)
        skill_map = self._skill_map(post, review)
        return LearningLoopReport(
            lab_name=normalized_lab,
            pre_score=pre,
            post_score=post,
            adaptive_review=review,
            skill_map=skill_map,
            spaced_practice=_spaced_practice(skill_map),
            submission_path=submission_path,
        )

    def _review(
        self,
        submission_path: Optional[Path],
        review_score: Optional[int],
    ) -> AdaptiveReview:
        if submission_path is not None:
            return self._reviewer.review(submission_path)

        score = _validated_score(review_score or 0, "review_score")
        return AdaptiveReview(
            score=score,
            skill_scores={},
            missing=["evidence-файл не передан"],
            next_task=(
                "Собрать evidence submission: EXPLAIN, gp_segment_id, RCA, "
                "change и validation."
            ),
        )

    def _skill_map(self, post_score: int, review: AdaptiveReview) -> List[SkillMapItem]:
        scores = review.skill_scores
        review_score = review.score
        distribution_score = _average(
            [
                _score(scores, "Root cause reasoning", review_score),
                _score(scores, "Change design", review_score),
            ]
        )
        return [
            _item(
                "MPP mental model",
                post_score,
                "post-assessment, QD/QE/slice/gang questions",
                "связать Motion с распределенным исполнением без подсказки",
            ),
            _item(
                "EXPLAIN literacy",
                _score(scores, "EXPLAIN evidence", review_score),
                "Redistribute Motion, Broadcast Motion, Hash Join, slice",
                "разобрать один план сверху вниз и назвать дорогие Motion",
            ),
            _item(
                "Distribution design",
                distribution_score,
                "distribution key, join key, DISTRIBUTED BY",
                "обосновать co-located join и риск skew на DDL",
            ),
            _item(
                "Runtime diagnostics",
                _score(scores, "Segment diagnostics", review_score),
                "gp_segment_id, gp_toolkit, segment-level checks",
                "добавить segment evidence до вывода о root cause",
            ),
            _item(
                "Validation discipline",
                _score(scores, "Validation", review_score),
                "EXPLAIN ANALYZE before/after, row counts, timing",
                "закрывать каждую гипотезу измерением before/after",
            ),
            _item(
                "Evidence quality",
                review_score,
                "complete submission: symptom, evidence, cause, fix, risk",
                "оформить ответ так, чтобы другой инженер мог его проверить",
            ),
        ]


def _validated_score(score: int, name: str) -> int:
    if score < 0 or score > 100:
        raise ValueError(f"{name} must be between 0 and 100.")
    return score


def _score(scores: Dict[str, int], key: str, fallback: int) -> int:
    return scores.get(key, fallback)


def _average(scores: List[int]) -> int:
    return round(sum(scores) / len(scores))


def _item(title: str, score: int, evidence: str, action: str) -> SkillMapItem:
    return SkillMapItem(
        title=title,
        score=score,
        status=_status(score),
        evidence=evidence,
        next_action=_next_action(score, action),
    )


def _status(score: int) -> str:
    if score >= 85:
        return "сильная зона"
    if score >= 70:
        return "закрепить"
    if score >= 60:
        return "дотренировать"
    return "повторить с ментором"


def _next_action(score: int, action: str) -> str:
    if score >= 85:
        return f"усложнить: {action}"
    return action


def _spaced_practice(skill_map: List[SkillMapItem]) -> List[SpacedPracticeItem]:
    weak_skill = min(skill_map, key=lambda item: item.score)
    return [
        SpacedPracticeItem(
            when="+1 день",
            task=(
                f"закрыть слабое место `{weak_skill.title}` на одном коротком "
                "EXPLAIN/RCA упражнении"
            ),
            check="есть SQL или EXPLAIN fragment и короткий вывод",
        ),
        SpacedPracticeItem(
            when="+3 дня",
            task=(
                "повторить storage/partitioning demo: heap vs AOCO, "
                "partition pruning и distribution"
            ),
            check="есть `\\d+`, catalog query и ответ почему partition key != distribution key",
        ),
        SpacedPracticeItem(
            when="+7 дней",
            task=(
                "собрать mini-capstone: mart DDL, план запроса, skew check, "
                "validation и residual risk"
            ),
            check="работа проходит adaptive-review без missing critical evidence",
        ),
    ]


def _localized_next_task(next_task: str) -> str:
    translations = {
        "Run the hard timed challenge and explain coordinator risk.": (
            "пройти hard timed challenge и отдельно объяснить риск coordinator/master."
        ),
        "Repeat Broadcast vs Redistribute plan reading with the visualizer.": (
            "повторить разбор Broadcast vs Redistribute через visualizer."
        ),
        "Add before/after validation evidence to the submission.": (
            "добавить в submission validation evidence до и после изменения."
        ),
        "Redo the scenario with a stricter evidence contract.": (
            "повторить сценарий с более строгим evidence contract."
        ),
    }
    return translations.get(next_task, next_task)
