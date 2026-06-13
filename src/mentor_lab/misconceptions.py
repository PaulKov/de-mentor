"""Misconception bank for adaptive mentor interventions."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class MisconceptionCard:
    code: str
    title: str
    signals: List[str]
    mentor_question: str
    mini_experiment: str
    hint: str
    follow_up: str

    def matches(self, content_lower: str) -> bool:
        return any(signal.lower() in content_lower for signal in self.signals)

    def render(self) -> str:
        return "\n".join(
            [
                f"# Misconception: {self.title}",
                "",
                f"Code: {self.code}",
                "",
                "## Signals",
                *[f"- {signal}" for signal in self.signals],
                "",
                "## Mentor question",
                f"- {self.mentor_question}",
                "",
                "## Мини-эксперимент",
                f"- {self.mini_experiment}",
                "",
                "## Hint",
                f"- {self.hint}",
                "",
                "## follow-up",
                f"- {self.follow_up}",
                "",
            ]
        )


@dataclass(frozen=True)
class MisconceptionDiagnosis:
    lab_name: str
    matches: List[MisconceptionCard]

    def render(self) -> str:
        lines = [f"# Misconception diagnosis: {self.lab_name}", ""]
        if not self.matches:
            lines.extend(
                [
                    "No misconception pattern detected.",
                    "",
                    "Next step: ask for EXPLAIN, gp_segment_id, physical cause and validation.",
                    "",
                ]
            )
            return "\n".join(lines)

        for card in self.matches:
            lines.extend(
                [
                    f"## {card.title}",
                    f"- Code: {card.code}",
                    f"- Question: {card.mentor_question}",
                    f"- мини-эксперимент: {card.mini_experiment}",
                    f"- Hint: {card.hint}",
                    f"- follow-up: {card.follow_up}",
                    "",
                ]
            )
        return "\n".join(lines)


class MisconceptionCatalog:
    """Read-only misconception catalog for Greenplum lesson interventions."""

    def __init__(self, cards_by_lab: Dict[str, List[MisconceptionCard]]) -> None:
        self._cards_by_lab = cards_by_lab

    @classmethod
    def default(cls) -> "MisconceptionCatalog":
        return cls(
            {
                "greenplum": [
                    MisconceptionCard(
                        code="partition-equals-distribution",
                        title="partition key != distribution key",
                        signals=[
                            "partition key equals distribution key",
                            "partition key = distribution key",
                            "partition key это то же самое что distribution key",
                            "partition key как distribution key",
                            "оба отвечают за распределение",
                        ],
                        mentor_question=(
                            "Какой механизм отвечает за pruning, а какой за locality "
                            "join и баланс строк по segments?"
                        ),
                        mini_experiment=(
                            "Сравнить `PARTITION BY RANGE (sale_date)` и "
                            "`DISTRIBUTED BY (customer_id)`, затем проверить "
                            "`EXPLAIN` и `gp_segment_id`."
                        ),
                        hint=(
                            "Partitioning режет таблицу по predicate/retention, "
                            "distribution раскладывает строки по segments."
                        ),
                        follow_up=(
                            "Добавить в homework отдельные поля: partition workload, "
                            "distribution workload и проверку `pg_partition_tree`."
                        ),
                    ),
                    MisconceptionCard(
                        code="master-reads-all-data",
                        title="master читает все данные",
                        signals=[
                            "master читает все данные",
                            "coordinator читает все данные",
                            "все данные проходят через master",
                            "qd читает таблицу",
                        ],
                        mentor_question=(
                            "Где выполняется scan большой таблицы: на QD или QE?"
                        ),
                        mini_experiment=(
                            "Показать план с segment scan, Motion и Gather Motion: "
                            "QD координирует, QE читают локальные данные."
                        ),
                        hint=(
                            "QD планирует и собирает финальный результат, QE исполняют "
                            "slice на segments; исключения обсуждаем через COPY/gpfdist."
                        ),
                        follow_up=(
                            "Пройти `python3 mentor-lab.py teach greenplum simple --stage 1` "
                            "и отдельно объяснить QD/QE/Gather Motion."
                        ),
                    ),
                    MisconceptionCard(
                        code="motion-is-always-bad",
                        title="Motion всегда плохо",
                        signals=[
                            "motion всегда плохо",
                            "любого motion надо избегать",
                            "broadcast всегда плохо",
                            "redistribute всегда плохо",
                        ],
                        mentor_question=(
                            "Когда Broadcast Motion маленького dimension дешевле, чем "
                            "Redistribute большого fact?"
                        ),
                        mini_experiment=(
                            "Сравнить product join с Broadcast Motion и customer join "
                            "с Redistribute Motion через visualizer."
                        ),
                        hint=(
                            "Motion - это цена data movement; важно оценивать объем, "
                            "сторону движения и частоту."
                        ),
                        follow_up=(
                            "Собрать evidence pack по redistribute-join и назвать, какая "
                            "сторона двигается."
                        ),
                    ),
                    MisconceptionCard(
                        code="aoco-always-faster",
                        title="AOCO всегда быстрее heap",
                        signals=[
                            "aoco всегда быстрее",
                            "columnstore всегда быстрее",
                            "heap не нужен",
                            "ao column для всех таблиц",
                        ],
                        mentor_question=(
                            "Что будет с маленькой frequently updated dimension в AOCO?"
                        ),
                        mini_experiment=(
                            "Сравнить heap dimension и AOCO fact через `\\d+`, "
                            "storage catalog и workload pattern."
                        ),
                        hint=(
                            "AOCO хорош для аналитических append scans; heap проще для "
                            "маленьких mutable таблиц."
                        ),
                        follow_up=(
                            "В homework добавить storage choice по каждой таблице, а не "
                            "один default на все."
                        ),
                    ),
                ]
            }
        )

    def list(self, lab_name: str) -> List[MisconceptionCard]:
        return list(self._cards(lab_name))

    def get(self, lab_name: str, code: str) -> MisconceptionCard:
        for card in self._cards(lab_name):
            if card.code == code:
                return card
        available = ", ".join(card.code for card in self._cards(lab_name))
        raise KeyError(
            f"Unknown misconception '{code}' for {lab_name}. Available: {available}."
        )

    def diagnose(self, lab_name: str, text: str) -> MisconceptionDiagnosis:
        content_lower = text.lower()
        matches = [card for card in self._cards(lab_name) if card.matches(content_lower)]
        return MisconceptionDiagnosis(lab_name=lab_name, matches=matches)

    def _cards(self, lab_name: str) -> Iterable[MisconceptionCard]:
        try:
            return self._cards_by_lab[lab_name]
        except KeyError as exc:
            available = ", ".join(self._cards_by_lab)
            raise KeyError(f"Unknown lab '{lab_name}'. Available labs: {available}.") from exc
