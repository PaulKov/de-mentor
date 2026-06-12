"""Pre/post assessment content for the Greenplum lesson."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class AssessmentQuestion:
    prompt: str
    options: Dict[str, str]
    answer: str
    explanation: str


@dataclass(frozen=True)
class Assessment:
    lab_name: str
    mode: str
    title: str
    questions: List[AssessmentQuestion]

    @property
    def answer_key(self) -> List[str]:
        return [question.answer for question in self.questions]

    def score(self, answers: Iterable[str]) -> int:
        normalized = [answer.strip().upper() for answer in answers]
        total = len(self.questions)
        correct = sum(
            1
            for expected, actual in zip(self.answer_key, normalized)
            if expected == actual
        )
        return round(correct * 100 / total) if total else 0

    def render(self) -> str:
        lines = [self.title, ""]
        for index, question in enumerate(self.questions, start=1):
            lines.append(f"{index}. {question.prompt}")
            for key, value in question.options.items():
                lines.append(f"   {key}. {value}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


class AssessmentCatalog:
    """Read-only pre/post assessment catalog."""

    def __init__(self, assessments: Dict[str, Dict[str, Assessment]]) -> None:
        self._assessments = assessments

    @classmethod
    def default(cls) -> "AssessmentCatalog":
        pre_questions = [
            _q(
                "Что чаще всего показывает Redistribute Motion?",
                ("A", "Сортировку результата"),
                ("B", "Перераспределение строк по новому ключу между segments"),
                ("C", "Локальный индексный lookup"),
                "B",
                "Redistribute Motion означает segment-to-segment shuffle.",
            ),
            _q(
                "Почему low-cardinality distribution key опасен?",
                ("A", "Он запрещает Hash Join"),
                ("B", "Он всегда включает columnstore"),
                ("C", "Он может собрать большую долю строк на одном segment"),
                "C",
                "Низкая cardinality часто приводит к skew.",
            ),
            _q(
                "Что означает co-located join?",
                ("A", "Обе стороны уже лежат на нужных segments по join key"),
                ("B", "Обе стороны собраны на master"),
                ("C", "Dimension всегда broadcast-ится"),
                "A",
                "Co-location снижает сетевую цену join.",
            ),
            _q(
                "Что должен делать master/coordinator?",
                ("A", "Хранить все fact rows"),
                ("B", "Планировать, dispatch-ить и собирать небольшой результат"),
                ("C", "Всегда выполнять Hash Join"),
                "B",
                "Master - control plane, а не основной data plane.",
            ),
            _q(
                "Что доказывает `gp_segment_id`?",
                ("A", "Физическое распределение строк по segments"),
                ("B", "Тип compression"),
                ("C", "Количество columns"),
                "A",
                "`gp_segment_id` делает skew измеримым.",
            ),
        ]
        post_questions = [
            _q(
                "Motion в плане появился перед Hash Join. Что проверишь первым?",
                ("A", "Цвет терминала"),
                ("B", "Совпадает ли distribution key с join key"),
                ("C", "Имя схемы"),
                "B",
                "Join locality зависит от физического размещения данных.",
            ),
            _q(
                "Когда Broadcast Motion может быть нормальным?",
                ("A", "Когда broadcast side маленькая после фильтров"),
                ("B", "Когда fact table больше 1 TB"),
                ("C", "Когда нет statistics"),
                "A",
                "Broadcast малой стороны часто дешевле shuffle большой.",
            ),
            _q(
                "Что значит большой Gather Motion?",
                ("A", "Потенциальный bottleneck на coordinator/single process"),
                ("B", "Гарантированное отсутствие skew"),
                ("C", "Автоматический partition pruning"),
                "A",
                "Gather должен возвращать небольшой final result.",
            ),
            _q(
                "Какой storage чаще подходит для больших append-heavy фактов?",
                ("A", "AO/AOCO с осознанной compression/encoding стратегией"),
                ("B", "Только temporary table"),
                ("C", "Любой, distribution все исправит"),
                "A",
                "Storage выбирается после grain/distribution/workload.",
            ),
            _q(
                "Почему MPP не просто большой PostgreSQL?",
                ("A", "Потому что network и distribution становятся частью плана"),
                ("B", "Потому что SQL другой язык"),
                ("C", "Потому что нет optimizer"),
                "A",
                "MPP добавляет физику движения данных.",
            ),
        ]
        return cls(
            {
                "greenplum": {
                    "pre": Assessment("greenplum", "pre", "Pre-assessment: Greenplum", pre_questions),
                    "post": Assessment("greenplum", "post", "Post-assessment: Greenplum", post_questions),
                }
            }
        )

    def get(self, lab_name: str, mode: str) -> Assessment:
        try:
            return self._assessments[lab_name][mode]
        except KeyError as exc:
            raise KeyError(f"Unknown assessment '{mode}' for {lab_name}.") from exc


def _q(prompt, a, b, c, answer, explanation) -> AssessmentQuestion:
    return AssessmentQuestion(
        prompt=prompt,
        options={a[0]: a[1], b[0]: b[1], c[0]: c[1]},
        answer=answer,
        explanation=explanation,
    )
