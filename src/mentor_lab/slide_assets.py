"""Catalog of slide assets and their Google Drive taxonomy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mentor_lab.lesson_routes import LearningRoute, resolve_learning_route


PERSONAL_DRIVE_ROOT_ID = "10QNQkH9fzfVP-xVaRO3AwbRBtF_m0zm3"
PERSONAL_OWNER_EMAIL = "pavelkov007@gmail.com"


@dataclass(frozen=True)
class DriveTaxonomy:
    """Human-readable Drive folder placement for a lesson deck."""

    root_folder_id: str
    root_folder_name: str
    direction_folder: str
    lesson_folder: str

    @property
    def display_path(self) -> str:
        return "/".join(
            [
                self.root_folder_name,
                self.direction_folder,
                self.lesson_folder,
            ]
        )


@dataclass(frozen=True)
class SlideAsset:
    """One publishable presentation artifact."""

    route_name: str
    title: str
    pptx_path: Path
    google_slides_url: str | None
    expected_owner_email: str
    expected_slide_count: int
    taxonomy: DriveTaxonomy


class SlideAssetCatalog:
    """Resolve lesson names to publishable slide assets."""

    def __init__(self, assets: dict[str, SlideAsset]) -> None:
        self._assets = dict(assets)

    @classmethod
    def default(cls, project_root: Path) -> "SlideAssetCatalog":
        routes = [
            _asset_for_route(
                resolve_learning_route("greenplum"),
                project_root,
                lesson_folder="Lesson 01 - MPP foundations",
                expected_slide_count=32,
            ),
            _asset_for_route(
                resolve_learning_route("greenplum-partitioning"),
                project_root,
                lesson_folder=(
                    "Lesson 02 - Partitioning, statistics and incremental loads"
                ),
                expected_slide_count=18,
            ),
        ]
        return cls({asset.route_name: asset for asset in routes})

    def get(self, name: str) -> SlideAsset:
        route = resolve_learning_route(name)
        return self._assets[route.name]


def _asset_for_route(
    route: LearningRoute,
    project_root: Path,
    *,
    lesson_folder: str,
    expected_slide_count: int,
) -> SlideAsset:
    return SlideAsset(
        route_name=route.name,
        title=f"Greenplum Academy - {route.lesson_code}: {route.title}",
        pptx_path=project_root / route.deck_path,
        google_slides_url=route.google_slides_url,
        expected_owner_email=PERSONAL_OWNER_EMAIL,
        expected_slide_count=expected_slide_count,
        taxonomy=DriveTaxonomy(
            root_folder_id=PERSONAL_DRIVE_ROOT_ID,
            root_folder_name="lessons",
            direction_folder="Greenplum",
            lesson_folder=lesson_folder,
        ),
    )
