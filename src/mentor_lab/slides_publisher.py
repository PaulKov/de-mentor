"""Google Slides publication orchestration with an injectable Drive gateway."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Protocol

from mentor_lab.slide_assets import SlideAsset


SLIDES_MIME_TYPE = "application/vnd.google-apps.presentation"


class PublishGuardError(ValueError):
    """Raised before Drive writes when the requested account is unsafe."""


@dataclass(frozen=True)
class DriveUser:
    email: str
    display_name: str


@dataclass(frozen=True)
class DriveFile:
    file_id: str
    name: str
    mime_type: str
    parents: tuple[str, ...]
    web_view_link: str
    anyone_reader: bool


@dataclass(frozen=True)
class SlideCheck:
    code: str
    passed: bool
    detail: str

    def render(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"{status} {self.code}: {self.detail}"


@dataclass(frozen=True)
class SlidePublishReport:
    asset: SlideAsset
    file_id: str
    folder_path: str
    action: str
    checks: tuple[SlideCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def render(self) -> str:
        lines = [
            "Google Slides publication report",
            f"Route: {self.asset.route_name}",
            f"Action: {self.action}",
            f"Folder: {self.folder_path}",
            f"File: {self.file_id}",
            f"URL: {self.asset.google_slides_url or 'created during publish'}",
            "",
            "Checks:",
        ]
        lines.extend(f"- {check.render()}" for check in self.checks)
        return "\n".join(lines) + "\n"


class DriveGateway(Protocol):
    """Small Google Drive/Slides boundary used by the publisher."""

    def current_user(self) -> DriveUser:
        ...

    def find_folder(self, parent_id: str, name: str) -> Optional[DriveFile]:
        ...

    def create_folder(self, parent_id: str, name: str) -> DriveFile:
        ...

    def get_file(self, file_id: str) -> DriveFile:
        ...

    def move_file(
        self,
        file_id: str,
        parent_id: str,
        remove_parent_ids: tuple[str, ...],
    ) -> DriveFile:
        ...

    def set_anyone_reader(self, file_id: str) -> None:
        ...

    def count_presentation_slides(self, presentation_id: str) -> int:
        ...

    def upload_pptx_as_slides(
        self,
        source_file: Path,
        title: str,
        parent_id: str,
    ) -> DriveFile:
        ...


class SlidePublisher:
    """Publish or verify lesson decks inside the personal Drive taxonomy."""

    def __init__(self, gateway: DriveGateway) -> None:
        self._gateway = gateway

    def dry_run(self, asset: SlideAsset, confirm_account: str) -> str:
        return "\n".join(
            [
                "Slides publish dry-run",
                f"Account: {confirm_account}",
                f"Expected account: {asset.expected_owner_email}",
                f"Route: {asset.route_name}",
                f"Folder: {asset.taxonomy.display_path}",
                f"Action: {_publish_action(asset)}",
                f"PowerPoint: {asset.pptx_path}",
                f"Google Slides: {asset.google_slides_url or 'will be created'}",
                "Writes: disabled",
                "",
            ]
        )

    def publish(self, asset: SlideAsset, confirm_account: str) -> SlidePublishReport:
        user = self._guarded_user(asset, confirm_account)
        lesson_folder = self._ensure_folder_path(asset)
        action = _publish_action(asset)

        presentation_id = presentation_id_from_url(asset.google_slides_url)
        if presentation_id:
            file = self._gateway.get_file(presentation_id)
            file = self._gateway.move_file(
                file.file_id,
                lesson_folder.file_id,
                remove_parent_ids=tuple(file.parents),
            )
        else:
            file = self._gateway.upload_pptx_as_slides(
                asset.pptx_path,
                asset.title,
                lesson_folder.file_id,
            )
            presentation_id = file.file_id

        self._gateway.set_anyone_reader(file.file_id)
        file = self._gateway.get_file(file.file_id)
        return self._report(asset, file, lesson_folder.file_id, action, user.email)

    def verify(self, asset: SlideAsset, confirm_account: str) -> SlidePublishReport:
        user = self._guarded_user(asset, confirm_account)
        folders = self._find_folder_path(asset)
        if folders is None:
            return SlidePublishReport(
                asset=asset,
                file_id=presentation_id_from_url(asset.google_slides_url) or "",
                folder_path=asset.taxonomy.display_path,
                action="verify Google Slides taxonomy",
                checks=(
                    SlideCheck(
                        "account",
                        True,
                        user.email,
                    ),
                    SlideCheck(
                        "folder_path",
                        False,
                        f"missing {asset.taxonomy.display_path}",
                    ),
                ),
            )

        presentation_id = presentation_id_from_url(asset.google_slides_url)
        if not presentation_id:
            return self._missing_file_report(asset, folders[-1].file_id, user.email)

        file = self._gateway.get_file(presentation_id)
        return self._report(
            asset,
            file,
            folders[-1].file_id,
            "verify Google Slides taxonomy",
            user.email,
        )

    def _guarded_user(self, asset: SlideAsset, confirm_account: str) -> DriveUser:
        expected = asset.expected_owner_email
        if confirm_account != expected:
            raise PublishGuardError(
                f"--confirm-account must be {expected}, got {confirm_account}"
            )
        user = self._gateway.current_user()
        if user.email != expected:
            raise PublishGuardError(
                f"Google Drive account must be {expected}, got {user.email}"
            )
        return user

    def _ensure_folder_path(self, asset: SlideAsset) -> DriveFile:
        current_parent = asset.taxonomy.root_folder_id
        direction = _find_or_create(
            self._gateway,
            current_parent,
            asset.taxonomy.direction_folder,
        )
        lesson = _find_or_create(
            self._gateway,
            direction.file_id,
            asset.taxonomy.lesson_folder,
        )
        return lesson

    def _find_folder_path(self, asset: SlideAsset) -> Optional[tuple[DriveFile, DriveFile]]:
        direction = self._gateway.find_folder(
            asset.taxonomy.root_folder_id,
            asset.taxonomy.direction_folder,
        )
        if direction is None:
            return None
        lesson = self._gateway.find_folder(direction.file_id, asset.taxonomy.lesson_folder)
        if lesson is None:
            return None
        return (direction, lesson)

    def _report(
        self,
        asset: SlideAsset,
        file: DriveFile,
        lesson_folder_id: str,
        action: str,
        account_email: str,
    ) -> SlidePublishReport:
        checks = [
            SlideCheck("account", account_email == asset.expected_owner_email, account_email),
            SlideCheck("folder_path", lesson_folder_id in file.parents, asset.taxonomy.display_path),
            SlideCheck("mime_type", file.mime_type == SLIDES_MIME_TYPE, file.mime_type),
            SlideCheck("anyone_reader", file.anyone_reader, str(file.anyone_reader)),
        ]
        slide_count = self._gateway.count_presentation_slides(file.file_id)
        checks.append(
            SlideCheck(
                "slide_count",
                slide_count == asset.expected_slide_count,
                str(slide_count),
            )
        )
        return SlidePublishReport(
            asset=asset,
            file_id=file.file_id,
            folder_path=asset.taxonomy.display_path,
            action=action,
            checks=tuple(checks),
        )

    def _missing_file_report(
        self,
        asset: SlideAsset,
        lesson_folder_id: str,
        account_email: str,
    ) -> SlidePublishReport:
        _ = lesson_folder_id
        return SlidePublishReport(
            asset=asset,
            file_id="",
            folder_path=asset.taxonomy.display_path,
            action="verify Google Slides taxonomy",
            checks=(
                SlideCheck("account", True, account_email),
                SlideCheck("file", False, "missing Google Slides URL"),
            ),
        )


def presentation_id_from_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    match = re.search(r"/presentation/d/([^/]+)", url)
    if not match:
        return None
    return match.group(1)


def _find_or_create(gateway: DriveGateway, parent_id: str, name: str) -> DriveFile:
    existing = gateway.find_folder(parent_id, name)
    if existing is not None:
        return existing
    return gateway.create_folder(parent_id, name)


def _publish_action(asset: SlideAsset) -> str:
    if presentation_id_from_url(asset.google_slides_url):
        return "organize existing Google Slides"
    return "upload PowerPoint as Google Slides"
