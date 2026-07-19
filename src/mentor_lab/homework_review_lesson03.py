"""Mechanical homework gates for Lesson 03 (Greenplum query tuning).

Scores structure and hard gates only. Reasoning quality is human-reviewed
against lessons/lesson-03/homework/rubric.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence


REQUIRED_FILES = ("rewrite.sql", "reconcile.sql", "evidence.md")

EVIDENCE_HEADINGS = (
    "## A. Workload contract",
    "## B. Baseline plan diagnosis",
    "## C. Statistics causality",
    "## D. Stage design",
    "## E. End-to-end measurement",
    "## H. Reconciliation",
    "## I. Residual risks",
)

CLASS_DEMO_TEMP_NAMES = (
    "tmp_lesson03_sales_feb",
    "tmp_lesson03_sales_shaped",
)


@dataclass(frozen=True)
class Lesson03GateResult:
    """One mechanical check outcome."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Lesson03HomeworkReview:
    """Aggregate mechanical review for a Lesson 03 submission directory."""

    accepted: bool
    gates: Sequence[Lesson03GateResult]
    score: int
    notes: Sequence[str]

    def render(self) -> str:
        lines = [
            "# Lesson 03 homework review (mechanical)",
            "",
            f"Accepted: {'yes' if self.accepted else 'no'}",
            f"Mechanical score: {self.score}/100",
            "",
            "## Gates",
        ]
        for gate in self.gates:
            mark = "PASS" if gate.passed else "FAIL"
            lines.append(f"- [{mark}] {gate.name}: {gate.detail}")
        lines.extend(["", "## Notes"])
        for note in self.notes or ["No extra notes"]:
            lines.append(f"- {note}")
        lines.extend(
            [
                "",
                "## Next",
                "- Human review still applies for diagnosis quality, e2e numbers, and production decision.",
                "- See lessons/lesson-03/homework/rubric.md (hard gates + scored 100).",
            ]
        )
        return "\n".join(lines) + "\n"


class Lesson03HomeworkReviewer:
    """Directory-based mechanical checker for Lesson 03 submissions."""

    def review(self, submission: Path) -> Lesson03HomeworkReview:
        path = Path(submission)
        gates: List[Lesson03GateResult] = []
        notes: List[str] = []

        if path.is_file():
            gates.append(
                Lesson03GateResult(
                    "submission_layout",
                    False,
                    "expected a directory with rewrite.sql, reconcile.sql, evidence.md "
                    f"(got file {path.name})",
                )
            )
            return Lesson03HomeworkReview(
                accepted=False, gates=gates, score=0, notes=notes
            )

        if not path.is_dir():
            gates.append(
                Lesson03GateResult(
                    "submission_layout",
                    False,
                    f"path does not exist or is not a directory: {path}",
                )
            )
            return Lesson03HomeworkReview(
                accepted=False, gates=gates, score=0, notes=notes
            )

        missing = [name for name in REQUIRED_FILES if not (path / name).is_file()]
        gates.append(
            Lesson03GateResult(
                "submission_layout",
                not missing,
                "ok" if not missing else f"missing: {', '.join(missing)}",
            )
        )
        if missing:
            return Lesson03HomeworkReview(
                accepted=False, gates=gates, score=0, notes=notes
            )

        rewrite = (path / "rewrite.sql").read_text(encoding="utf-8")
        reconcile = (path / "reconcile.sql").read_text(encoding="utf-8")
        evidence = (path / "evidence.md").read_text(encoding="utf-8")

        rewrite_l = rewrite.lower()
        reconcile_l = reconcile.lower()
        evidence_l = evidence.lower()

        has_optimizer = bool(re.search(r"set\s+optimizer\s*=\s*(on|off)", rewrite_l))
        gates.append(
            Lesson03GateResult(
                "fixed_optimizer_marker",
                has_optimizer,
                "found SET optimizer = on|off in rewrite.sql"
                if has_optimizer
                else "rewrite.sql must contain SET optimizer = on|off for the rewrite proof",
            )
        )

        missing_headings = [h for h in EVIDENCE_HEADINGS if h not in evidence]
        # Allow slight heading variants for D/E
        if "## D. Stage design" in missing_headings and re.search(
            r"^## D\.", evidence, re.MULTILINE
        ):
            missing_headings = [h for h in missing_headings if h != "## D. Stage design"]
        if "## E. End-to-end measurement" in missing_headings and re.search(
            r"^## E\.", evidence, re.MULTILINE
        ):
            missing_headings = [
                h for h in missing_headings if h != "## E. End-to-end measurement"
            ]
        gates.append(
            Lesson03GateResult(
                "evidence_sections",
                not missing_headings,
                "ok" if not missing_headings else f"missing headings: {missing_headings}",
            )
        )

        e2e_ok = (
            "total pipeline" in evidence_l
            or "pipeline time" in evidence_l
            or ("monolith" in evidence_l and "candidate" in evidence_l)
        ) and (
            "merge" in evidence_l
            or "do not merge" in evidence_l
            or "needs larger-scale" in evidence_l
        )
        gates.append(
            Lesson03GateResult(
                "e2e_metrics_table",
                e2e_ok,
                "evidence mentions pipeline cost + production decision"
                if e2e_ok
                else "evidence.md must include end-to-end pipeline metrics and merge/do-not-merge decision",
            )
        )

        except_count = len(re.findall(r"\bexcept\s+all\b", reconcile_l))
        gates.append(
            Lesson03GateResult(
                "two_way_except_all",
                except_count >= 2,
                f"found {except_count} EXCEPT ALL (need ≥2 for both directions)"
                if except_count >= 2
                else "reconcile.sql must contain EXCEPT ALL in both directions",
            )
        )

        residual_ok = "## I. Residual risks" in evidence and len(
            evidence.split("## I. Residual risks", 1)[-1].strip()
        ) > 20
        gates.append(
            Lesson03GateResult(
                "residual_risk_present",
                residual_ok,
                "residual risks section has content"
                if residual_ok
                else "section I must list residual risks in addition to reconciliation",
            )
        )

        creates_temp = bool(re.search(r"create\s+temp\s+table", rewrite_l))
        if creates_temp:
            has_distributed = "distributed by" in rewrite_l
            has_analyze = bool(re.search(r"\banalyze\b", rewrite_l))
            has_drop = "drop table if exists" in rewrite_l
            stage_ok = has_distributed and has_analyze and has_drop
            detail_parts = []
            if not has_drop:
                detail_parts.append("missing DROP TABLE IF EXISTS (idempotency)")
            if not has_distributed:
                detail_parts.append("missing DISTRIBUTED BY")
            if not has_analyze:
                detail_parts.append("missing ANALYZE after TEMP")
            gates.append(
                Lesson03GateResult(
                    "temp_stage_mechanics",
                    stage_ok,
                    "TEMP stages have DROP + DISTRIBUTED BY + ANALYZE"
                    if stage_ok
                    else "; ".join(detail_parts),
                )
            )
        else:
            explored = (
                "temp boundary" in evidence_l
                or "materialization" in evidence_l
                or "без temp" in evidence_l
                or "no temp" in evidence_l
                or "отверг" in evidence_l
                or "reject" in evidence_l
            )
            gates.append(
                Lesson03GateResult(
                    "temp_stage_mechanics",
                    explored,
                    "no TEMP in rewrite — evidence documents TEMP boundary reject"
                    if explored
                    else "no CREATE TEMP: evidence must argue why materialization was rejected",
                )
            )

        demo_hits = [name for name in CLASS_DEMO_TEMP_NAMES if name in rewrite_l]
        if demo_hits and creates_temp:
            # Soft fail: reject if rewrite is essentially only class-demo names
            only_demo = all(
                name in rewrite_l for name in CLASS_DEMO_TEMP_NAMES
            ) and not re.search(r"create\s+temp\s+table\s+tmp_(?!lesson03_sales_)", rewrite_l)
            gates.append(
                Lesson03GateResult(
                    "no_class_demo_copy",
                    not only_demo,
                    "rewrite uses class-demo TEMP names as the only stages — design your own"
                    if only_demo
                    else f"class-demo names present ({', '.join(demo_hits)}); ensure own architecture + e2e",
                )
            )
            if not only_demo:
                notes.append(
                    "rewrite mentions class-demo TEMP names; human review should verify originality."
                )
        else:
            gates.append(
                Lesson03GateResult(
                    "no_class_demo_copy",
                    True,
                    "ok",
                )
            )

        mentor_ok = "mentor" in evidence_l or "dbname=mentor" in evidence_l
        gates.append(
            Lesson03GateResult(
                "mentor_database_mentioned",
                mentor_ok,
                "evidence mentions mentor database"
                if mentor_ok
                else "workload contract should state DB mentor",
            )
        )

        passed = sum(1 for g in gates if g.passed)
        score = round(100 * passed / len(gates)) if gates else 0
        accepted = all(g.passed for g in gates)
        if not accepted:
            notes.append(
                "Mechanical gates failed — fix structure before human rubric scoring."
            )
        return Lesson03HomeworkReview(
            accepted=accepted, gates=gates, score=score, notes=notes
        )
