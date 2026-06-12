"""Timed challenge generation for Greenplum academy lessons."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from mentor_lab.scenario_dsl import ScenarioDefinition
from mentor_lab.scenario_engine import ScenarioRandomizer


@dataclass(frozen=True)
class TimedChallenge:
    scenario: ScenarioDefinition
    minutes: int
    seed: int
    started_iso: str
    deadline_iso: str

    def render(self) -> str:
        lines = [
            f"# Timed challenge: {self.scenario.title}",
            "",
            f"Difficulty: {self.scenario.difficulty}",
            f"Duration: {self.minutes} min",
            f"Seed: {self.seed}",
            f"Started: {self.started_iso}",
            f"Deadline: {self.deadline_iso}",
            "",
            "## Mission",
        ]
        lines.extend(f"- {task}" for task in self.scenario.tasks)
        lines.extend(
            [
                "",
                "## Evidence contract",
                "- Symptom",
                "- Plan evidence",
                "- Segment or runtime evidence",
                "- Physical cause",
                "- Change",
                "- Validation",
                "- Residual risk",
                "",
                "## Acceptance criteria",
            ]
        )
        lines.extend(f"- {item}" for item in self.scenario.acceptance_criteria)
        return "\n".join(lines) + "\n"


class ChallengeCatalog:
    """Starts replayable timed challenges."""

    def __init__(self, randomizer: ScenarioRandomizer) -> None:
        self._randomizer = randomizer

    @classmethod
    def default(cls) -> "ChallengeCatalog":
        return cls(ScenarioRandomizer.default())

    def start(
        self,
        lab_name: str,
        difficulty: str,
        minutes: int,
        seed: int,
    ) -> TimedChallenge:
        now = datetime.now(timezone.utc)
        deadline = now + timedelta(minutes=minutes)
        return TimedChallenge(
            scenario=self._randomizer.pick(lab_name, difficulty, seed),
            minutes=minutes,
            seed=seed,
            started_iso=now.isoformat(timespec="seconds"),
            deadline_iso=deadline.isoformat(timespec="seconds"),
        )
