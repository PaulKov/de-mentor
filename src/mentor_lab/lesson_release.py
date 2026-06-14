"""Preflight release checks for a lesson route."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

from mentor_lab.lesson_release_manifest import LessonReleaseManifest
from mentor_lab.session_experience import SessionManager
from mentor_lab.slide_assets import SlideAssetCatalog
from mentor_lab.slides_publisher import SlidePublishReport


@dataclass(frozen=True)
class ReleaseCheck:
    code: str
    status: str
    detail: str

    def render(self) -> str:
        return f"{self.status} {self.code}: {self.detail}"


@dataclass(frozen=True)
class LessonReleaseReport:
    manifest: LessonReleaseManifest
    checks: tuple[ReleaseCheck, ...]

    @property
    def passed(self) -> bool:
        return not any(check.status == "FAIL" for check in self.checks)

    @property
    def status_label(self) -> str:
        if not self.passed:
            return "BLOCKED"
        if any(check.status == "WARN" for check in self.checks):
            return "READY_WITH_WARNINGS"
        return "READY"

    def render(self) -> str:
        lines = [
            f"# Lesson Release Report: {self.manifest.route}",
            "",
            f"Status: {self.status_label}",
            f"Lesson: {self.manifest.title}",
            f"Physical lab: {self.manifest.physical_lab}",
            f"Google Slides: {self.manifest.google_slides_url}",
            f"Drive folder: {self.manifest.drive_folder}",
            "",
            "## Проверки",
            "",
        ]
        lines.extend(f"- {check.render()}" for check in self.checks)
        lines.extend(
            [
                "",
                "## Команды Выпуска",
                "",
            ]
        )
        lines.extend(f"- `{command}`" for command in self.manifest.safe_cli_commands)
        lines.extend(
            [
                "",
                "## Что Дать Ученику",
                "",
            ]
        )
        lines.extend(f"- `{path}`" for path in self.manifest.student_handoff)
        return "\n".join(lines) + "\n"


class LessonReleaseVerifier:
    """Builds release-readiness evidence from a manifest and local artifacts."""

    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root

    def verify(
        self,
        manifest: LessonReleaseManifest,
        *,
        slide_report: SlidePublishReport | None = None,
        live_google_requested: bool = False,
    ) -> LessonReleaseReport:
        checks = [
            ReleaseCheck("manifest", "PASS", manifest.source_path.relative_to(self._project_root).as_posix()),
            self._route_matches_slide_catalog(manifest),
            self._local_artifacts_exist(manifest),
            self._google_static_check(manifest),
            self._session_control_plane_check(manifest),
            self._safe_cli_commands_check(manifest),
            self._work_account_guard(manifest),
            self._google_live_check(slide_report, live_google_requested),
        ]
        return LessonReleaseReport(manifest=manifest, checks=tuple(checks))

    def _route_matches_slide_catalog(self, manifest: LessonReleaseManifest) -> ReleaseCheck:
        asset = SlideAssetCatalog.default(self._project_root).get(manifest.route)
        expected = (
            asset.google_slides_url == manifest.google_slides_url
            and asset.expected_owner_email == manifest.expected_owner_email
            and asset.expected_slide_count == manifest.expected_slide_count
            and asset.taxonomy.display_path == manifest.drive_folder
        )
        status = "PASS" if expected else "FAIL"
        return ReleaseCheck("slide_asset_catalog", status, asset.taxonomy.display_path)

    def _local_artifacts_exist(self, manifest: LessonReleaseManifest) -> ReleaseCheck:
        missing = [
            path
            for path in manifest.all_local_artifacts
            if not (self._project_root / path).exists()
        ]
        if missing:
            return ReleaseCheck("local_artifacts", "FAIL", ", ".join(missing))
        return ReleaseCheck("pptx_artifact", "PASS", manifest.deck_path)

    def _google_static_check(self, manifest: LessonReleaseManifest) -> ReleaseCheck:
        url_ok = "/presentation/d/" in manifest.google_slides_url
        owner_ok = manifest.expected_owner_email == "pavelkov007@gmail.com"
        folder_ok = manifest.drive_folder.startswith("lessons/Greenplum/")
        if url_ok and owner_ok and folder_ok:
            return ReleaseCheck("google_slides_static", "PASS", manifest.drive_folder)
        return ReleaseCheck("google_slides_static", "FAIL", "Google Slides metadata mismatch")

    def _session_control_plane_check(self, manifest: LessonReleaseManifest) -> ReleaseCheck:
        with tempfile.TemporaryDirectory(prefix="mentor-release-") as tmp:
            session_dir = SessionManager().start(manifest.route, "Release Bot", Path(tmp))
            state = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
        control_plane = state["control_plane"]
        deck_ok = control_plane["mentor_mode"]["slide_deck"] == manifest.deck_path
        slides_ok = control_plane["mentor_mode"]["google_slides"] == manifest.google_slides_url
        if deck_ok and slides_ok:
            return ReleaseCheck("session_control_plane", "PASS", manifest.route)
        return ReleaseCheck("session_control_plane", "FAIL", "session.json points to stale assets")

    def _safe_cli_commands_check(self, manifest: LessonReleaseManifest) -> ReleaseCheck:
        invalid = [
            command
            for command in manifest.safe_cli_commands
            if not command.startswith("python3 mentor-lab.py ")
        ]
        if invalid:
            return ReleaseCheck("safe_cli_commands", "FAIL", ", ".join(invalid))
        return ReleaseCheck("safe_cli_commands", "PASS", f"{len(manifest.safe_cli_commands)} commands")

    def _work_account_guard(self, manifest: LessonReleaseManifest) -> ReleaseCheck:
        content = manifest.source_path.read_text(encoding="utf-8")
        if "pavel.a.kovalev@1win.pro" in content:
            return ReleaseCheck("work_account_guard", "FAIL", "work account leaked")
        return ReleaseCheck("work_account_guard", "PASS", manifest.expected_owner_email)

    def _google_live_check(
        self,
        slide_report: SlidePublishReport | None,
        live_google_requested: bool,
    ) -> ReleaseCheck:
        if slide_report is None:
            status = "FAIL" if live_google_requested else "WARN"
            return ReleaseCheck(
                "google_slides_live",
                status,
                "pass --live-google-slides --confirm-account and --oauth-client-json",
            )
        status = "PASS" if slide_report.passed else "FAIL"
        return ReleaseCheck("google_slides_live", status, slide_report.folder_path)
