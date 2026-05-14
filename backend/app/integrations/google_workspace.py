"""
Google Drive / Docs / Sheets using service account JSON (GOOGLE_APPLICATION_CREDENTIALS).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import Config
from ..utils.logger import get_logger
from ..utils.retry import retry_with_backoff

logger = get_logger("mirofish.google")

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]


def _credentials_path() -> str:
    path = Config.GOOGLE_APPLICATION_CREDENTIALS or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not path or not os.path.isfile(path):
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS must point to a service account JSON file"
        )
    return path


class GoogleWorkspaceClient:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            _credentials_path(), scopes=SCOPES
        )
        self._drive = build("drive", "v3", credentials=creds, cache_discovery=False)
        self._docs = build("docs", "v1", credentials=creds, cache_discovery=False)
        self._sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
        self._folder_id = (Config.GOOGLE_DRIVE_FOLDER_ID or "").strip() or None

    @retry_with_backoff(max_retries=3, initial_delay=1.0, exceptions=(HttpError, OSError))
    def create_spreadsheet(self, title: str) -> str:
        meta: Dict[str, Any] = {"properties": {"title": title}}
        if self._folder_id:
            meta["parents"] = [self._folder_id]
        file = (
            self._drive.files()
            .create(body=meta, fields="id", supportsAllDrives=True)
            .execute()
        )
        sid = file.get("id")
        logger.info("Created spreadsheet %s", sid)
        return sid

    @retry_with_backoff(max_retries=3, initial_delay=1.0, exceptions=(HttpError, OSError))
    def spreadsheet_write_values(self, spreadsheet_id: str, values: List[List[Any]], range_a1: str = "Sheet1!A1") -> Dict[str, Any]:
        body = {"values": values}
        return (
            self._sheets.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_a1,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )

    @retry_with_backoff(max_retries=3, initial_delay=1.0, exceptions=(HttpError, OSError))
    def create_doc_with_text(self, title: str, body_text: str) -> str:
        meta: Dict[str, Any] = {
            "name": title,
            "mimeType": "application/vnd.google-apps.document",
        }
        if self._folder_id:
            meta["parents"] = [self._folder_id]
        file = (
            self._drive.files()
            .create(body=meta, fields="id", supportsAllDrives=True)
            .execute()
        )
        doc_id = file["id"]
        if body_text:
            chunk = 8000
            for i in range(0, len(body_text), chunk):
                part = body_text[i : i + chunk]
                doc = self._docs.documents().get(documentId=doc_id).execute()
                body = doc.get("body") or {}
                content = body.get("content") or []
                if not content:
                    insert_index = 1
                else:
                    insert_index = content[-1].get("endIndex", 2) - 1
                    if insert_index < 1:
                        insert_index = 1
                self._docs.documents().batchUpdate(
                    documentId=doc_id,
                    body={
                        "requests": [
                            {"insertText": {"location": {"index": insert_index}, "text": part}}
                        ]
                    },
                ).execute()
        logger.info("Created doc %s", doc_id)
        return doc_id

    def doc_url(self, doc_id: str) -> str:
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    def sheet_url(self, spreadsheet_id: str) -> str:
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
