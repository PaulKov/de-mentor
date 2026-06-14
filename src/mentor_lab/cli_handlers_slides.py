"""CLI handlers for Google Slides publishing operations."""

from __future__ import annotations

import argparse
from pathlib import Path

from mentor_lab.cli_context import _project_root
from mentor_lab.google_drive_gateway import GoogleDriveGateway
from mentor_lab.slide_assets import SlideAssetCatalog
from mentor_lab.slides_publisher import PublishGuardError, SlidePublisher


def _handle_slides_publish(args: argparse.Namespace) -> int:
    asset = SlideAssetCatalog.default(_project_root()).get(args.lab_name)
    if args.dry_run:
        print(SlidePublisher(_NoopGateway()).dry_run(asset, args.confirm_account), end="")
        return 0

    try:
        publisher = SlidePublisher(_gateway_from_args(args))
        report = publisher.publish(asset, args.confirm_account)
    except (PublishGuardError, RuntimeError, KeyError) as exc:
        print(str(exc))
        return 1
    print(report.render(), end="")
    return 0 if report.passed else 1


def _handle_slides_verify(args: argparse.Namespace) -> int:
    asset = SlideAssetCatalog.default(_project_root()).get(args.lab_name)
    try:
        publisher = SlidePublisher(_gateway_from_args(args))
        report = publisher.verify(asset, args.confirm_account)
    except (PublishGuardError, RuntimeError, KeyError) as exc:
        print(str(exc))
        return 1
    print(report.render(), end="")
    return 0 if report.passed else 1


def _gateway_from_args(args: argparse.Namespace) -> GoogleDriveGateway:
    if not args.oauth_client_json:
        raise RuntimeError("--oauth-client-json is required without --dry-run")
    return GoogleDriveGateway.from_credentials_file(
        Path(args.oauth_client_json),
        args.refresh_token_env,
    )


class _NoopGateway:
    """Placeholder dependency used only by dry-run output."""
