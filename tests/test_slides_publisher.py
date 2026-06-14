from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from mentor_lab.cli import main
from mentor_lab.slide_assets import SlideAssetCatalog
from mentor_lab.slides_publisher import (
    DriveFile,
    DriveUser,
    PublishGuardError,
    SlidePublisher,
)


ROOT = Path(__file__).resolve().parents[1]
LESSON_02_SLIDES = (
    "https://docs.google.com/presentation/d/"
    "17Ae88PoniaFU34egsFPwC0PndAOoXMze4qV1pIKQkaI/edit?usp=sharing"
)


def invoke(args):
    stdout = StringIO()
    try:
        with redirect_stdout(stdout):
            exit_code = main(args)
    except SystemExit as exc:
        exit_code = int(exc.code)
    return exit_code, stdout.getvalue()


def test_slide_asset_catalog_maps_lesson_02_to_greenplum_drive_taxonomy():
    asset = SlideAssetCatalog.default(ROOT).get("greenplum-partitioning")

    assert asset.route_name == "greenplum-partitioning"
    assert asset.expected_owner_email == "pavelkov007@gmail.com"
    assert asset.google_slides_url == LESSON_02_SLIDES
    assert asset.taxonomy.root_folder_name == "lessons"
    assert asset.taxonomy.direction_folder == "Greenplum"
    assert asset.taxonomy.lesson_folder == (
        "Lesson 02 - Partitioning, statistics and incremental loads"
    )
    assert asset.taxonomy.display_path == (
        "lessons/Greenplum/"
        "Lesson 02 - Partitioning, statistics and incremental loads"
    )


def test_slides_publish_dry_run_prints_account_folder_and_no_write_plan():
    exit_code, output = invoke(
        [
            "slides",
            "publish",
            "greenplum-partitioning",
            "--dry-run",
            "--confirm-account",
            "pavelkov007@gmail.com",
        ]
    )

    assert exit_code == 0, output
    assert "Slides publish dry-run" in output
    assert "Account: pavelkov007@gmail.com" in output
    assert "lessons/Greenplum/Lesson 02 - Partitioning" in output
    assert "Action: organize existing Google Slides" in output
    assert LESSON_02_SLIDES in output


def test_slides_verify_requires_oauth_client_json_without_traceback():
    exit_code, output = invoke(
        [
            "slides",
            "verify",
            "greenplum-partitioning",
            "--confirm-account",
            "pavelkov007@gmail.com",
        ]
    )

    assert exit_code == 1
    assert "--oauth-client-json is required" in output


def test_git_presentation_catalog_documents_drive_taxonomy_and_cli():
    catalog = (ROOT / "decks" / "README.md").read_text(encoding="utf-8")

    assert "lessons/Greenplum/Lesson 02 - Partitioning" in catalog
    assert "python3 mentor-lab.py slides publish greenplum-partitioning" in catalog
    assert "python3 mentor-lab.py slides verify greenplum-partitioning" in catalog
    assert "pavelkov007@gmail.com" in catalog


def test_slides_publisher_rejects_wrong_confirmed_account_before_drive_writes():
    gateway = FakeDriveGateway(user_email="pavelkov007@gmail.com")
    asset = SlideAssetCatalog.default(ROOT).get("greenplum-partitioning")

    with pytest.raises(PublishGuardError, match="confirm-account"):
        SlidePublisher(gateway).publish(asset, confirm_account="wrong@example.com")

    assert gateway.created_folders == []
    assert gateway.moved_files == []
    assert gateway.permissions == []


def test_slides_publisher_moves_existing_deck_to_direction_lesson_folder():
    gateway = FakeDriveGateway(user_email="pavelkov007@gmail.com")
    gateway.files["17Ae88PoniaFU34egsFPwC0PndAOoXMze4qV1pIKQkaI"] = DriveFile(
        file_id="17Ae88PoniaFU34egsFPwC0PndAOoXMze4qV1pIKQkaI",
        name="Greenplum Academy - Lesson 02",
        mime_type="application/vnd.google-apps.presentation",
        parents=("10QNQkH9fzfVP-xVaRO3AwbRBtF_m0zm3",),
        web_view_link=LESSON_02_SLIDES,
        anyone_reader=False,
    )
    gateway.slide_counts["17Ae88PoniaFU34egsFPwC0PndAOoXMze4qV1pIKQkaI"] = 18
    asset = SlideAssetCatalog.default(ROOT).get("greenplum-partitioning")

    result = SlidePublisher(gateway).publish(
        asset,
        confirm_account="pavelkov007@gmail.com",
    )

    assert result.passed is True
    assert [folder.name for folder in gateway.created_folders] == [
        "Greenplum",
        "Lesson 02 - Partitioning, statistics and incremental loads",
    ]
    assert gateway.moved_files == [
        (
            "17Ae88PoniaFU34egsFPwC0PndAOoXMze4qV1pIKQkaI",
            gateway.created_folders[-1].file_id,
        )
    ]
    assert gateway.permissions == [
        ("17Ae88PoniaFU34egsFPwC0PndAOoXMze4qV1pIKQkaI", "reader")
    ]
    assert "PASS slide_count: 18" in result.render()


def test_slides_verify_reports_missing_taxonomy_without_creating_folders():
    gateway = FakeDriveGateway(user_email="pavelkov007@gmail.com")
    asset = SlideAssetCatalog.default(ROOT).get("greenplum-partitioning")

    report = SlidePublisher(gateway).verify(
        asset,
        confirm_account="pavelkov007@gmail.com",
    )

    assert report.passed is False
    assert "FAIL folder_path" in report.render()
    assert gateway.created_folders == []


class FakeDriveGateway:
    def __init__(self, user_email: str) -> None:
        self.user = DriveUser(email=user_email, display_name="Test User")
        self.files: dict[str, DriveFile] = {}
        self.folders: dict[tuple[str, str], DriveFile] = {}
        self.slide_counts: dict[str, int] = {}
        self.created_folders: list[DriveFile] = []
        self.moved_files: list[tuple[str, str]] = []
        self.permissions: list[tuple[str, str]] = []

    def current_user(self) -> DriveUser:
        return self.user

    def find_folder(self, parent_id: str, name: str) -> DriveFile | None:
        return self.folders.get((parent_id, name))

    def create_folder(self, parent_id: str, name: str) -> DriveFile:
        folder = DriveFile(
            file_id=f"folder_{len(self.created_folders) + 1}",
            name=name,
            mime_type="application/vnd.google-apps.folder",
            parents=(parent_id,),
            web_view_link=f"https://drive.google.com/drive/folders/{name}",
            anyone_reader=False,
        )
        self.folders[(parent_id, name)] = folder
        self.created_folders.append(folder)
        return folder

    def get_file(self, file_id: str) -> DriveFile:
        return self.files[file_id]

    def move_file(self, file_id: str, parent_id: str, remove_parent_ids: tuple[str, ...]) -> DriveFile:
        _ = remove_parent_ids
        current = self.files[file_id]
        moved = DriveFile(
            file_id=current.file_id,
            name=current.name,
            mime_type=current.mime_type,
            parents=(parent_id,),
            web_view_link=current.web_view_link,
            anyone_reader=current.anyone_reader,
        )
        self.files[file_id] = moved
        self.moved_files.append((file_id, parent_id))
        return moved

    def set_anyone_reader(self, file_id: str) -> None:
        current = self.files[file_id]
        self.files[file_id] = DriveFile(
            file_id=current.file_id,
            name=current.name,
            mime_type=current.mime_type,
            parents=current.parents,
            web_view_link=current.web_view_link,
            anyone_reader=True,
        )
        self.permissions.append((file_id, "reader"))

    def count_presentation_slides(self, presentation_id: str) -> int:
        return self.slide_counts[presentation_id]

    def upload_pptx_as_slides(self, source_file: Path, title: str, parent_id: str) -> DriveFile:
        file_id = f"presentation_{len(self.files) + 1}"
        uploaded = DriveFile(
            file_id=file_id,
            name=title,
            mime_type="application/vnd.google-apps.presentation",
            parents=(parent_id,),
            web_view_link=f"https://docs.google.com/presentation/d/{file_id}/edit",
            anyone_reader=False,
        )
        self.files[file_id] = uploaded
        self.slide_counts[file_id] = 18
        return uploaded
