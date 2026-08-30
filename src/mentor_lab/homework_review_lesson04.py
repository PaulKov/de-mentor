"""Mechanical evidence gates for the Lesson 04 PySpark homework pack."""

from __future__ import annotations

from pathlib import Path

from mentor_lab.homework_review import HomeworkReview


class Lesson04HomeworkReviewer:
    """Review reproducibility and evidence markers without executing student code."""

    _ACCEPTANCE_SCORE = 75
    _REQUIRED_FILES = ("pipeline.py", "evidence.md")
    _SKILLS = {
        "Explicit input contract": ("StructType", ".schema(", "input"),
        "DataFrame transformations": ("filter", "join", "groupBy"),
        "Idempotent Parquet output": ("mode(\"overwrite\")", "parquet", "output"),
        "Execution plan evidence": ("explain", "Exchange", "stage"),
        "Correctness evidence": ("count", "revenue", "roundtrip"),
        "Production reasoning": ("shuffle", "risk", "decision"),
    }
    _FORBIDDEN = (".collect()", ".toPandas()", "pyspark.sql.functions.udf")

    def review(self, submission: Path) -> HomeworkReview:
        """Return a stable review for a directory-based submission pack."""

        if not submission.is_dir():
            return HomeworkReview(
                score=0,
                accepted=False,
                skill_scores={},
                missing=["Submission must be a directory with pipeline.py and evidence.md"],
                next_actions=["Use lessons/lesson-04/submissions as the submission path"],
                next_actions_title="Next actions",
            )

        missing_files = [name for name in self._REQUIRED_FILES if not (submission / name).is_file()]
        if missing_files:
            return HomeworkReview(
                score=0,
                accepted=False,
                skill_scores={},
                missing=[f"Missing file: {name}" for name in missing_files],
                next_actions=["Copy the homework templates and complete both required files"],
                next_actions_title="Next actions",
            )

        pipeline = (submission / "pipeline.py").read_text(encoding="utf-8")
        evidence = (submission / "evidence.md").read_text(encoding="utf-8")
        combined = f"{pipeline}\n{evidence}".lower()

        skill_scores = {
            skill: round(
                100 * sum(marker.lower() in combined for marker in markers) / len(markers)
            )
            for skill, markers in self._SKILLS.items()
        }
        forbidden_hits = [marker for marker in self._FORBIDDEN if marker.lower() in pipeline.lower()]
        missing = [skill for skill, score in skill_scores.items() if score < 67]
        missing.extend(f"Forbidden full-data driver action: {marker}" for marker in forbidden_hits)
        score = round(sum(skill_scores.values()) / len(skill_scores))
        accepted = score >= self._ACCEPTANCE_SCORE and not missing and not forbidden_hits
        actions = [
            f"Add stronger evidence for: {item}"
            for item in missing
            if not item.startswith("Forbidden")
        ]
        actions.extend(f"Remove {marker}; aggregate or sample before driver collection" for marker in forbidden_hits)
        if not actions:
            actions = ["Pack passes mechanical gates; proceed to mentor review of plan/UI evidence"]
        return HomeworkReview(
            score=score,
            accepted=accepted,
            skill_scores=skill_scores,
            missing=missing,
            next_actions=actions,
            next_actions_title="Next actions",
        )
