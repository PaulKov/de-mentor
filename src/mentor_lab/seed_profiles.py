"""Seed profile metadata for repeatable Greenplum exercises."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class SeedProfile:
    name: str
    title: str
    description: str
    file_path: Path
    container_path: str


class SeedProfileCatalog:
    """Catalog of seed profiles by lab."""

    def __init__(self, profiles_by_lab) -> None:
        self._profiles_by_lab = profiles_by_lab

    @classmethod
    def default(cls, project_root: Path) -> "SeedProfileCatalog":
        base = project_root / "labs" / "greenplum" / "seed"
        return cls(
            {
                "greenplum": [
                    SeedProfile(
                        "balanced",
                        "Balanced warehouse",
                        "Even distribution for baseline plan comparisons.",
                        base / "balanced.sql",
                        "/mentor-lab/seed/balanced.sql",
                    ),
                    SeedProfile(
                        "skewed",
                        "Skewed incident",
                        "Low-cardinality status distribution for diagnostics.",
                        base / "skewed.sql",
                        "/mentor-lab/seed/skewed.sql",
                    ),
                    SeedProfile(
                        "enterprise",
                        "Enterprise-heavy marketplace",
                        "A few large customers dominate revenue while rows stay distributed.",
                        base / "enterprise.sql",
                        "/mentor-lab/seed/enterprise.sql",
                    ),
                    SeedProfile(
                        "late-facts",
                        "Late arriving facts",
                        "Adds late facts to discuss incremental loads and partition hygiene.",
                        base / "late-facts.sql",
                        "/mentor-lab/seed/late-facts.sql",
                    ),
                    SeedProfile(
                        "bad-statistics",
                        "Stale statistics drill",
                        "Creates changed data without ANALYZE so estimates can be questioned.",
                        base / "bad-statistics.sql",
                        "/mentor-lab/seed/bad-statistics.sql",
                    ),
                    SeedProfile(
                        "bad-partitioning",
                        "Partitioning mismatch drill",
                        "Creates a mart shaped for pruning discussion.",
                        base / "bad-partitioning.sql",
                        "/mentor-lab/seed/bad-partitioning.sql",
                    ),
                    SeedProfile(
                        "wide-aoco",
                        "Wide AOCO fact drill",
                        "Creates a column-oriented table for heap versus AOCO discussion.",
                        base / "wide-aoco.sql",
                        "/mentor-lab/seed/wide-aoco.sql",
                    ),
                    SeedProfile(
                        "small-dimension-broadcast",
                        "Broadcast dimension drill",
                        "Creates a small filtered dimension for Broadcast Motion analysis.",
                        base / "small-dimension-broadcast.sql",
                        "/mentor-lab/seed/small-dimension-broadcast.sql",
                    ),
                ]
            }
        )

    def list(self, lab_name: str) -> List[SeedProfile]:
        return list(self._profiles(lab_name))

    def get(self, lab_name: str, profile_name: str) -> SeedProfile:
        profiles = self._profiles(lab_name)
        for profile in profiles:
            if profile.name == profile_name:
                return profile
        available = ", ".join(profile.name for profile in profiles)
        raise KeyError(
            f"Unknown seed profile '{profile_name}' for {lab_name}. "
            f"Available profiles: {available}."
        )

    def _profiles(self, lab_name: str) -> Iterable[SeedProfile]:
        try:
            return self._profiles_by_lab[lab_name]
        except KeyError as exc:
            available = ", ".join(self._profiles_by_lab)
            raise KeyError(f"Unknown lab '{lab_name}'. Available labs: {available}.") from exc
