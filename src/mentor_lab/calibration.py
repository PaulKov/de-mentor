"""Gold submission calibration examples for mentor consistency."""

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class CalibrationExample:
    lab_name: str
    level: str
    title: str
    score_band: str
    submission: str
    mentor_use: List[str]

    def render(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            f"Lab: {self.lab_name}",
            f"Level: {self.level}",
            f"Score band: {self.score_band}",
            "",
            "## Submission sample",
            self.submission,
            "",
            "## How mentor uses it",
        ]
        lines.extend(f"- {item}" for item in self.mentor_use)
        return "\n".join(lines) + "\n"


class CalibrationCatalog:
    """Small catalog of weak-to-senior answer examples."""

    def __init__(self, examples_by_lab: Dict[str, List[CalibrationExample]]) -> None:
        self._examples_by_lab = examples_by_lab

    @classmethod
    def default(cls) -> "CalibrationCatalog":
        return cls(
            {
                "greenplum": [
                    CalibrationExample(
                        lab_name="greenplum",
                        level="weak",
                        title="Weak submission",
                        score_band="0-49",
                        submission=(
                            "Запрос медленный, потому что Greenplum большой. Нужно добавить индекс "
                            "или увеличить память. Evidence отсутствует."
                        ),
                        mentor_use=[
                            "Показать, что мнение без EXPLAIN не является RCA.",
                            "Попросить один `gp_segment_id` check перед любым выводом.",
                        ],
                    ),
                    CalibrationExample(
                        lab_name="greenplum",
                        level="solid",
                        title="Solid submission",
                        score_band="70-84",
                        submission=(
                            "В плане есть Redistribute Motion по `customer_id`; таблица fact "
                            "распределена не по join key. Я предлагаю `DISTRIBUTED BY "
                            "(customer_id)` и проверяю before/after через EXPLAIN ANALYZE."
                        ),
                        mentor_use=[
                            "Отметить правильный evidence-first ход.",
                            "Дотренировать residual risk: skew и stale statistics.",
                        ],
                    ),
                    CalibrationExample(
                        lab_name="greenplum",
                        level="senior",
                        title="Senior-level submission",
                        score_band="85-100",
                        submission=(
                            "Symptom: customer aggregation медленная. Evidence: EXPLAIN показывает "
                            "Redistribute Motion 2:2 перед Hash Join, `gp_segment_id` показывает "
                            "приемлемый баланс после redesign. Physical cause: fact не co-located "
                            "с dimension по join key. Change: новый fact distributed by "
                            "`customer_id`, AOCO оставлен для append workload. Validation: "
                            "Redistribute исчез на join path, final Gather оставлен только для "
                            "малого результата. Residual risk: статистика после load и skew при "
                            "изменении cardinality."
                        ),
                        mentor_use=[
                            "Использовать как эталон evidence, RCA, fix, validation, risk.",
                            "Попросить ученика сравнить свой ответ с этим текстом по рубрике.",
                        ],
                    ),
                ]
            }
        )

    def list(self, lab_name: str) -> List[CalibrationExample]:
        return list(self._examples(lab_name))

    def get(self, lab_name: str, level: str) -> CalibrationExample:
        for example in self._examples(lab_name):
            if example.level == level:
                return example
        available = ", ".join(example.level for example in self._examples(lab_name))
        raise KeyError(
            f"Unknown calibration level '{level}' for {lab_name}. Available: {available}."
        )

    def _examples(self, lab_name: str) -> Iterable[CalibrationExample]:
        try:
            return self._examples_by_lab[lab_name]
        except KeyError as exc:
            available = ", ".join(self._examples_by_lab)
            raise KeyError(f"Unknown lab '{lab_name}'. Available labs: {available}.") from exc
