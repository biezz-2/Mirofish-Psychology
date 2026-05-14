"""
PRD: analysis + research questions + question bank.
"""

import json
import os
from flask import Blueprint, jsonify, request

from ..config import Config
from ..integrations.google_workspace import GoogleWorkspaceClient
from ..services.research_service import ResearchService
from ..utils.locale import set_locale
from ..utils.logger import get_logger
from ..utils.llm_client import LLMClient

from . import research_bp

logger = get_logger("mirofish.api.research")


def _ok(data=None, **extra):
    body = {"success": True, "data": data or {}}
    body.update(extra)
    return jsonify(body)


def _err(message, code=400):
    return jsonify({"success": False, "error": message}), code


@research_bp.route("/question-bank", methods=["GET"])
def question_bank():
    path = os.path.join(os.path.dirname(__file__), "..", "prd_assets", "question_bank.json")
    path = os.path.normpath(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _ok(data)


@research_bp.route("/analyze", methods=["POST"])
def analyze():
    loc = request.headers.get("Accept-Language", "en")
    set_locale(loc if loc in ("zh", "en", "id", "es", "fr", "pt", "ru", "de") else "en")
    body = request.get_json(silent=True) or {}
    payload = body.get("data") or body.get("payload")
    if payload is None:
        return _err("JSON body must include 'data' object", 400)
    template = body.get("template", "apa_psi")
    write_doc = body.get("write_google_doc")
    doc_title = body.get("doc_title", "MiroFish Analysis")
    try:
        svc = ResearchService()
        markdown = svc.analyze_psychology_data(payload, locale=loc, template=template)
        out: dict = {"markdown": markdown}
        if write_doc and (Config.GOOGLE_APPLICATION_CREDENTIALS or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")):
            try:
                g = GoogleWorkspaceClient()
                doc_id = g.create_doc_with_text(str(doc_title), markdown)
                out["document_id"] = doc_id
                out["document_url"] = g.doc_url(doc_id)
            except Exception as e:
                logger.warning("google doc write failed: %s", e)
                out["document_error"] = str(e)
        return _ok(out)
    except Exception as e:
        logger.exception("analyze")
        return _err(str(e), 502)


@research_bp.route("/questions", methods=["POST"])
def questions():
    loc = request.headers.get("Accept-Language", "en")
    set_locale(loc if loc in ("zh", "en", "id", "es", "fr", "pt", "ru", "de") else "en")
    body = request.get_json(silent=True) or {}
    payload = body.get("data") or body.get("payload") or {}
    methods = body.get("methods") or ["foq", "qualitative", "quantitative", "critical"]
    count = int(body.get("count_per_method") or 5)
    try:
        svc = ResearchService()
        result = svc.generate_questions(payload, methods, locale=loc, count_per_method=count)
        return _ok({"questions": result})
    except Exception as e:
        logger.exception("questions")
        return _err(str(e), 502)


@research_bp.route("/llm-smoke", methods=["POST"])
def llm_smoke():
    """Minimal LLM call to verify NVIDIA / OpenAI-compatible endpoint (PRD T-02 smoke)."""
    body = request.get_json(silent=True) or {}
    prompt = body.get("prompt") or "Reply with exactly: OK"
    try:
        client = LLMClient()
        text = client.chat(
            [{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=32,
        )
        return _ok({"reply": text.strip(), "model": client.model, "base_url": client.base_url})
    except Exception as e:
        logger.exception("llm smoke")
        return _err(str(e), 502)
