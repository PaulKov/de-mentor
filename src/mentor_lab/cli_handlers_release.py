"""CLI handlers for lesson release pipeline commands."""

from __future__ import annotations

import argparse
from pathlib import Path

from mentor_lab.cli_context import _project_root
from mentor_lab.google_drive_gateway import GoogleDriveGateway
from mentor_lab.lesson_release import LessonReleaseVerifier
from mentor_lab.lesson_release_manifest import LessonReleaseManifestLoader
from mentor_lab.slide_assets import SlideAssetCatalog
from mentor_lab.slides_publisher import PublishGuardError, SlidePublisher


def _handle_lesson_release(args: argparse.Namespace) -> int:
    if args.release_command == "publish-slides":
        return _handle_publish_slides(args)

    try:
        manifest = LessonReleaseManifestLoader(_project_root()).load(args.lab_name)
        slide_report = _live_slide_report(args) if args.live_google_slides else None
        report = LessonReleaseVerifier(_project_root()).verify(
            manifest,
            slide_report=slide_report,
            live_google_requested=args.live_google_slides,
        )
    except (FileNotFoundError, ValueError, RuntimeError, PublishGuardError, KeyError) as exc:
        print(str(exc))
        return 1

    if args.release_command == "report":
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report.render(), encoding="utf-8")
        print(f"Lesson release report written to {output}")
        return 0 if report.passed else 1

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report.render(), encoding="utf-8")
    print(report.render(), end="")
    return 0 if report.passed else 1


def _handle_publish_slides(args: argparse.Namespace) -> int:
    asset = SlideAssetCatalog.default(_project_root()).get(args.lab_name)
    publisher = SlidePublisher(_NoopGateway()) if args.dry_run else SlidePublisher(_gateway(args))
    try:
        if args.dry_run:
            print(publisher.dry_run(asset, args.confirm_account), end="")
            return 0
        report = publisher.publish(asset, args.confirm_account)
    except (RuntimeError, PublishGuardError, KeyError) as exc:
        print(str(exc))
        return 1
    print(report.render(), end="")
    return 0 if report.passed else 1


def _live_slide_report(args: argparse.Namespace):
    if not args.confirm_account:
        raise RuntimeError("--confirm-account is required with --live-google-slides")
    if not args.oauth_client_json:
        raise RuntimeError("--oauth-client-json is required with --live-google-slides")
    asset = SlideAssetCatalog.default(_project_root()).get(args.lab_name)
    return SlidePublisher(_gateway(args)).verify(asset, args.confirm_account)


def _gateway(args: argparse.Namespace) -> GoogleDriveGateway:
    if not args.oauth_client_json:
        raise RuntimeError("--oauth-client-json is required without --dry-run")
    return GoogleDriveGateway.from_credentials_file(
        Path(args.oauth_client_json),
        args.refresh_token_env,
    )


class _NoopGateway:
    """Placeholder dependency used only by dry-run output."""
