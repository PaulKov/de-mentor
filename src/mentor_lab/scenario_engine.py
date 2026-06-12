"""Scenario randomization and start instructions."""

import random
from dataclasses import dataclass

from mentor_lab.scenario_dsl import ScenarioDefinition, ScenarioDslCatalog


@dataclass(frozen=True)
class ScenarioStart:
    scenario: ScenarioDefinition
    seed: int

    def render(self) -> str:
        lines = [
            f"Scenario: {self.scenario.title}",
            f"Code: {self.scenario.code}",
            f"Difficulty: {self.scenario.difficulty}",
            f"Seed: {self.seed}",
            f"Seed profile: {self.scenario.seed_profile}",
            "",
            "Mission:",
        ]
        lines.extend(f"- {task}" for task in self.scenario.tasks)
        lines.extend(["", "Acceptance criteria:"])
        lines.extend(f"- {item}" for item in self.scenario.acceptance_criteria)
        lines.extend(
            [
                "",
                "Setup:",
                f"python3 mentor-lab.py seed {self.scenario.lab} --profile {self.scenario.seed_profile}",
                f"python3 mentor-lab.py diagnostics {self.scenario.lab} list",
            ]
        )
        return "\n".join(lines) + "\n"


class ScenarioRandomizer:
    """Picks deterministic scenarios so mentors can replay the same exercise."""

    def __init__(self, catalog: ScenarioDslCatalog) -> None:
        self._catalog = catalog

    @classmethod
    def default(cls) -> "ScenarioRandomizer":
        return cls(ScenarioDslCatalog.default())

    def pick(self, lab_name: str, difficulty: str, seed: int) -> ScenarioDefinition:
        scenarios = self._catalog.list(lab_name, difficulty=difficulty)
        if not scenarios:
            available = ", ".join(
                sorted({scenario.difficulty for scenario in self._catalog.list(lab_name)})
            )
            raise KeyError(
                f"No scenarios for difficulty '{difficulty}'. Available difficulties: {available}."
            )
        return random.Random(seed).choice(scenarios)

    def start(self, lab_name: str, difficulty: str, seed: int) -> ScenarioStart:
        return ScenarioStart(self.pick(lab_name, difficulty, seed), seed)
