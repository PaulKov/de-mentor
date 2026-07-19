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


def _gp625_profiles(base: Path) -> List[SeedProfile]:
    """Profiles for the shared Greenplum 6.25 academy stand."""

    return [
        SeedProfile(
            "academy",
            "Full academy (lessons 01–03)",
            "Loads mentor.lesson01 + lesson02 + lesson03 on Greenplum 6.25.",
            base / "academy.sql",
            "/mentor-lab/seed/academy.sql",
        ),
        SeedProfile(
            "lesson01",
            "Lesson 01 core dataset",
            "Skewed/good facts, dims and Motion views in mentor.lesson01.",
            base / "lesson01.sql",
            "/mentor-lab/seed/lesson01.sql",
        ),
        SeedProfile(
            "lesson02",
            "Lesson 02 partitioning lab",
            "Partitioned facts, stage, late facts and ANALYZE in mentor.lesson02.",
            base / "lesson02.sql",
            "/mentor-lab/seed/lesson02.sql",
        ),
        SeedProfile(
            "lesson03",
            "Lesson 03 OLAP + optimizer dataset",
            "Loads mentor.lesson03 schema, AOCO fact, star-join ORCA case and TEMP stages.",
            base / "lesson03.sql",
            "/mentor-lab/seed/lesson03.sql",
        ),
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
            "Reloads lesson01 core (includes skewed status distribution).",
            base / "lesson01.sql",
            "/mentor-lab/seed/lesson01.sql",
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


class SeedProfileCatalog:
    """Catalog of seed profiles by lab."""

    def __init__(self, profiles_by_lab) -> None:
        self._profiles_by_lab = profiles_by_lab

    @classmethod
    def default(cls, project_root: Path) -> "SeedProfileCatalog":
        base_625 = project_root / "labs" / "greenplum-625" / "seed"
        profiles = _gp625_profiles(base_625)
        # Both CLI lab names share the same Greenplum 6.25 stand.
        return cls(
            {
                "greenplum-625": profiles,
                "greenplum": profiles,
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
