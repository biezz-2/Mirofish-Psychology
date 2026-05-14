"""
PRD: Notion → Google sync API + config probe.
"""

import json
import os
from flask import Blueprint, jsonify, request

from ..config import Config
from ..integrations.notion_service import NotionExtractor
from ..services.sync_job_manager import SyncJobManager, JobStatus
from ..utils.locale import set_locale
from ..utils.logger import get_logger

from . import integration_bp

logger = get_logger("mirofish.api.integration")


def _ok(data=None, **extra):
    body = {"success": True, "data": data or {}}
    body.update(extra)
    return jsonify(body)


def _err(message, code=400):
    return jsonify({"success": False, "error": message}), code


@integration_bp.route("/config-status", methods=["GET"])
def config_status():
    notion = bool((Config.NOTION_API_KEY or "").strip())
    notion_db = bool((Config.NOTION_DATABASE_ID or "").strip())
    gpath = (Config.GOOGLE_APPLICATION_CREDENTIALS or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
    google_json = bool(gpath and os.path.isfile(gpath))
    google_folder = bool((Config.GOOGLE_DRIVE_FOLDER_ID or "").strip())
    return _ok(
        {
            "notion": notion,
            "notion_database_configured": notion_db,
            "google_credentials_file": google_json,
            "google_drive_folder_configured": google_folder,
            "llm_configured": bool((Config.LLM_API_KEY or "").strip()),
            "zep_configured": bool((Config.ZEP_API_KEY or "").strip()),
        }
    )


@integration_bp.route("/notion/preview", methods=["POST"])
def notion_preview():
    loc = request.headers.get("Accept-Language", "en")
    set_locale(loc if loc in ("zh", "en", "id", "es", "fr", "pt", "ru", "de") else "en")
    body = request.get_json(silent=True) or {}
    database_id = (body.get("database_id") or Config.NOTION_DATABASE_ID or "").strip()
    if not database_id:
        return _err("database_id or NOTION_DATABASE_ID required", 400)
    try:
        ext = NotionExtractor()
        table = ext.database_to_table(database_id)
        preview_rows = table["rows"][:20]
        return _ok(
            {
                "headers": table["headers"],
                "row_count": table["count"],
                "preview": preview_rows,
            }
        )
    except Exception as e:
        logger.exception("notion preview")
        return _err(str(e), 502)


@integration_bp.route("/sync/start", methods=["POST"])
def sync_start():
    body = request.get_json(silent=True) or {}
    job = SyncJobManager.create_job()
    SyncJobManager.run_notion_to_google(
        job.id,
        database_id=body.get("database_id"),
        spreadsheet_id=body.get("spreadsheet_id"),
        new_sheet_title=body.get("new_sheet_title"),
        doc_title=body.get("doc_title"),
    )
    return _ok({"job_id": job.id, "status": job.status.value})


@integration_bp.route("/sync/<job_id>", methods=["GET"])
def sync_status(job_id: str):
    job = SyncJobManager.get(job_id)
    if not job:
        return _err("job not found", 404)
    return _ok(
        {
            "job_id": job.id,
            "status": job.status.value,
            "error": job.error,
            "result": job.result,
            "log_lines": job.log_lines[-50:],
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }
    )


@integration_bp.route("/forms/create-placeholder", methods=["POST"])
def forms_placeholder():
    """P1 Google Forms: full create flow is out of MVP; return structured guidance."""
    return _err(
        "Google Forms creation via API is deferred (P1). Use Sheets export + manual form or extend google_workspace.Forms API.",
        501,
    )
