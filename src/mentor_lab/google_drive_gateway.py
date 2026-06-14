"""Minimal Google Drive and Slides API gateway for publishing decks."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from mentor_lab.slides_publisher import DriveFile, DriveUser


DRIVE_API = "https://www.googleapis.com/drive/v3"
SLIDES_API = "https://slides.googleapis.com/v1/presentations"
FOLDER_MIME = "application/vnd.google-apps.folder"
SLIDES_MIME = "application/vnd.google-apps.presentation"
PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


@dataclass(frozen=True)
class OAuthCredentials:
    client_id: str
    client_secret: str
    refresh_token: str

    @classmethod
    def from_file_and_env(
        cls,
        client_json: Path,
        refresh_token_env: str,
    ) -> "OAuthCredentials":
        payload = json.loads(client_json.read_text(encoding="utf-8"))
        client = payload.get("installed") or payload.get("web") or payload
        refresh_token = _env_or_launchctl(refresh_token_env)
        if not refresh_token:
            raise RuntimeError(f"Missing refresh token env: {refresh_token_env}")
        return cls(
            client_id=client["client_id"],
            client_secret=client["client_secret"],
            refresh_token=refresh_token,
        )


class GoogleDriveGateway:
    """HTTP implementation of the DriveGateway protocol."""

    def __init__(self, credentials: OAuthCredentials) -> None:
        self._credentials = credentials
        self._access_token: Optional[str] = None

    @classmethod
    def from_credentials_file(
        cls,
        client_json: Path,
        refresh_token_env: str,
    ) -> "GoogleDriveGateway":
        return cls(OAuthCredentials.from_file_and_env(client_json, refresh_token_env))

    def current_user(self) -> DriveUser:
        data = self._request_json(
            "GET",
            f"{DRIVE_API}/about?fields=user(emailAddress,displayName)",
        )
        user = data["user"]
        return DriveUser(
            email=user["emailAddress"],
            display_name=user.get("displayName", ""),
        )

    def find_folder(self, parent_id: str, name: str) -> Optional[DriveFile]:
        query = (
            f"mimeType='{FOLDER_MIME}' and "
            f"name='{_drive_query_escape(name)}' and "
            f"'{parent_id}' in parents and trashed=false"
        )
        params = urllib.parse.urlencode(
            {
                "q": query,
                "fields": "files(id,name,mimeType,parents,webViewLink,permissions)",
                "pageSize": "1",
                "supportsAllDrives": "true",
            }
        )
        data = self._request_json("GET", f"{DRIVE_API}/files?{params}")
        files = data.get("files", [])
        if not files:
            return None
        return _drive_file(files[0])

    def create_folder(self, parent_id: str, name: str) -> DriveFile:
        payload = {
            "name": name,
            "mimeType": FOLDER_MIME,
            "parents": [parent_id],
        }
        data = self._request_json(
            "POST",
            f"{DRIVE_API}/files?fields=id,name,mimeType,parents,webViewLink,permissions",
            payload,
        )
        return _drive_file(data)

    def get_file(self, file_id: str) -> DriveFile:
        fields = "id,name,mimeType,parents,webViewLink,permissions"
        data = self._request_json(
            "GET",
            f"{DRIVE_API}/files/{file_id}?fields={fields}&supportsAllDrives=true",
        )
        return _drive_file(data)

    def move_file(
        self,
        file_id: str,
        parent_id: str,
        remove_parent_ids: tuple[str, ...],
    ) -> DriveFile:
        params = {
            "addParents": parent_id,
            "fields": "id,name,mimeType,parents,webViewLink,permissions",
            "supportsAllDrives": "true",
        }
        if remove_parent_ids:
            params["removeParents"] = ",".join(remove_parent_ids)
        query = urllib.parse.urlencode(params)
        data = self._request_json("PATCH", f"{DRIVE_API}/files/{file_id}?{query}", {})
        return _drive_file(data)

    def set_anyone_reader(self, file_id: str) -> None:
        payload = {"type": "anyone", "role": "reader"}
        try:
            self._request_json(
                "POST",
                f"{DRIVE_API}/files/{file_id}/permissions?supportsAllDrives=true",
                payload,
            )
        except RuntimeError as exc:
            if "already exists" not in str(exc):
                raise

    def count_presentation_slides(self, presentation_id: str) -> int:
        data = self._request_json("GET", f"{SLIDES_API}/{presentation_id}?fields=slides")
        return len(data.get("slides", []))

    def upload_pptx_as_slides(
        self,
        source_file: Path,
        title: str,
        parent_id: str,
    ) -> DriveFile:
        boundary = "mentor-lab-upload-boundary"
        metadata = {
            "name": title,
            "mimeType": SLIDES_MIME,
            "parents": [parent_id],
        }
        body = _multipart_body(boundary, metadata, source_file)
        headers = {
            "Authorization": f"Bearer {self._token()}",
            "Content-Type": f"multipart/related; boundary={boundary}",
        }
        params = urllib.parse.urlencode(
            {
                "uploadType": "multipart",
                "fields": "id,name,mimeType,parents,webViewLink,permissions",
                "supportsAllDrives": "true",
            }
        )
        request = urllib.request.Request(
            f"https://www.googleapis.com/upload/drive/v3/files?{params}",
            data=body,
            headers=headers,
            method="POST",
        )
        return _drive_file(self._open_json(request))

    def _request_json(
        self,
        method: str,
        url: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Authorization": f"Bearer {self._token()}"}
        if payload is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        return self._open_json(request)

    def _open_json(self, request: urllib.request.Request) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Google API error {exc.code}: {detail}") from exc

    def _token(self) -> str:
        if self._access_token:
            return self._access_token
        payload = urllib.parse.urlencode(
            {
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret,
                "refresh_token": self._credentials.refresh_token,
                "grant_type": "refresh_token",
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        data = self._open_json(request)
        self._access_token = data["access_token"]
        return self._access_token


def _env_or_launchctl(name: str) -> str:
    value = os.environ.get(name)
    if value:
        return value
    try:
        completed = subprocess.run(
            ["launchctl", "getenv", name],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return ""
    return completed.stdout.strip()


def _drive_query_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _drive_file(data: dict[str, Any]) -> DriveFile:
    return DriveFile(
        file_id=data["id"],
        name=data.get("name", ""),
        mime_type=data.get("mimeType", ""),
        parents=tuple(data.get("parents", [])),
        web_view_link=data.get("webViewLink", ""),
        anyone_reader=_has_anyone_reader(data.get("permissions", [])),
    )


def _has_anyone_reader(permissions: list[dict[str, Any]]) -> bool:
    return any(
        permission.get("type") == "anyone" and permission.get("role") == "reader"
        for permission in permissions
    )


def _multipart_body(boundary: str, metadata: dict[str, Any], source_file: Path) -> bytes:
    body = [
        f"--{boundary}\r\n".encode("utf-8"),
        b"Content-Type: application/json; charset=UTF-8\r\n\r\n",
        json.dumps(metadata).encode("utf-8"),
        b"\r\n",
        f"--{boundary}\r\n".encode("utf-8"),
        f"Content-Type: {PPTX_MIME}\r\n\r\n".encode("utf-8"),
        source_file.read_bytes(),
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(body)
