"""
Background sync jobs + audit log (PRD F-08, F-09).
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..config import Config
from ..integrations.notion_service import NotionExtractor
from ..integrations.google_workspace import GoogleWorkspaceClient
from ..utils.logger import get_logger

logger = get_logger("mirofish.sync_job")


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SyncJob:
    id: str
    status: JobStatus = JobStatus.PENDING
    created_at: str = ""
    updated_at: str = ""
    error: Optional[str] = None
    result: Dict[str, Any] = field(default_factory=dict)
    log_lines: List[str] = field(default_factory=list)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _audit_path() -> str:
    raw = Config.SYNC_AUDIT_LOG_PATH or ""
    if raw:
        path = raw
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(__file__), "..", "..", path)
        path = os.path.normpath(path)
    else:
        path = os.path.join(os.path.dirname(__file__), "..", "..", "logs", "sync_audit.log")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def append_audit(event: Dict[str, Any]) -> None:
    event = {**event, "ts": _now_iso()}
    line = json.dumps(event, ensure_ascii=False) + "\n"
    try:
        with open(_audit_path(), "a", encoding="utf-8") as f:
            f.write(line)
    except OSError as e:
        logger.warning("audit log write failed: %s", e)


class SyncJobManager:
    _jobs: Dict[str, SyncJob] = {}
    _lock = threading.Lock()

    @classmethod
    def create_job(cls) -> SyncJob:
        jid = str(uuid.uuid4())
        job = SyncJob(id=jid, created_at=_now_iso(), updated_at=_now_iso())
        with cls._lock:
            cls._jobs[jid] = job
        append_audit({"action": "job_created", "job_id": jid})
        return job

    @classmethod
    def get(cls, job_id: str) -> Optional[SyncJob]:
        with cls._lock:
            return cls._jobs.get(job_id)

    @classmethod
    def _update(cls, job: SyncJob, **kwargs: Any) -> None:
        with cls._lock:
            for k, v in kwargs.items():
                setattr(job, k, v)
            job.updated_at = _now_iso()

    @classmethod
    def run_notion_to_google(
        cls,
        job_id: str,
        *,
        database_id: Optional[str] = None,
        spreadsheet_id: Optional[str] = None,
        new_sheet_title: Optional[str] = None,
        doc_title: Optional[str] = None,
    ) -> None:
        job = cls.get(job_id)
        if not job:
            return

        def worker():
            cls._update(job, status=JobStatus.RUNNING)
            append_audit({"action": "job_start", "job_id": job_id})
            try:
                db_id = (database_id or Config.NOTION_DATABASE_ID or "").strip()
                if not db_id:
                    raise ValueError("NOTION_DATABASE_ID or request database_id required")

                notion = NotionExtractor()
                table = notion.database_to_table(db_id)
                headers: List[str] = table["headers"]
                rows_data: List[Dict[str, Any]] = table["rows"]

                values: List[List[Any]] = [headers + ["_page_id", "_last_edited"]]
                for r in rows_data:
                    values.append([r.get(h, "") for h in headers] + [r.get("_page_id", ""), r.get("_last_edited", "")])

                google = GoogleWorkspaceClient()
                sid = spreadsheet_id
                if not sid:
                    title = new_sheet_title or f"MiroFish Notion sync {job_id[:8]}"
                    sid = google.create_spreadsheet(title)
                google.spreadsheet_write_values(sid, values)

                doc_id = None
                if doc_title:
                    summary_lines = [
                        f"# {doc_title}",
                        "",
                        f"Rows exported: {len(rows_data)}",
                        f"Database: {db_id}",
                        "",
                        "## Preview (first 5 rows)",
                    ]
                    for i, r in enumerate(rows_data[:5]):
                        summary_lines.append(f"- Row {i+1}: " + json.dumps({h: r.get(h) for h in headers[:8]}, ensure_ascii=False)[:500])
                    doc_id = google.create_doc_with_text(doc_title, "\n".join(summary_lines))

                result = {
                    "spreadsheet_id": sid,
                    "spreadsheet_url": google.sheet_url(sid),
                    "row_count": len(rows_data),
                    "document_id": doc_id,
                    "document_url": google.doc_url(doc_id) if doc_id else None,
                }
                cls._update(job, status=JobStatus.COMPLETED, result=result, error=None)
                job.log_lines.append("completed")
                append_audit({"action": "job_completed", "job_id": job_id, "result_keys": list(result.keys())})
            except Exception as e:
                logger.exception("sync job failed")
                cls._update(job, status=JobStatus.FAILED, error=str(e))
                job.log_lines.append(str(e))
                append_audit({"action": "job_failed", "job_id": job_id, "error": str(e)})

        t = threading.Thread(target=worker, daemon=True)
        t.start()
