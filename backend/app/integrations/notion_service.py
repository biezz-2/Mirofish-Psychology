"""
Notion database / page extraction with pagination and property flattening.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from notion_client import Client

from ..config import Config
from ..utils.logger import get_logger
from ..utils.retry import retry_with_backoff

logger = get_logger("mirofish.notion")


def _plain_from_rich(rich: List[Dict[str, Any]]) -> str:
    if not rich:
        return ""
    parts = []
    for block in rich:
        pt = block.get("plain_text")
        if pt:
            parts.append(pt)
    return "".join(parts)


def flatten_property_value(prop_name: str, prop: Dict[str, Any]) -> str:
    """Map a Notion property object to a single cell string."""
    ptype = prop.get("type")
    if not ptype:
        return ""

    inner = prop.get(ptype)
    if inner is None:
        return ""

    if ptype == "title":
        return _plain_from_rich(inner)
    if ptype == "rich_text":
        return _plain_from_rich(inner)
    if ptype == "number":
        return "" if inner is None else str(inner)
    if ptype == "select":
        return (inner or {}).get("name", "") or ""
    if ptype == "multi_select":
        return ", ".join((s.get("name") or "") for s in inner if s.get("name"))
    if ptype == "status":
        return (inner or {}).get("name", "") or ""
    if ptype == "date":
        if not inner:
            return ""
        start = inner.get("start") or ""
        end = inner.get("end")
        return f"{start}–{end}" if end else start
    if ptype == "checkbox":
        return "yes" if inner else "no"
    if ptype == "url":
        return inner or ""
    if ptype == "email":
        return inner or ""
    if ptype == "phone_number":
        return inner or ""
    if ptype == "formula":
        ft = inner.get("type")
        if ft and inner.get(ft) is not None:
            return flatten_property_value(prop_name, {"type": ft, ft: inner.get(ft)})
        return ""
    if ptype == "unique_id":
        p = inner.get("prefix") or ""
        n = inner.get("number")
        return f"{p}{n}" if n is not None else ""
    if ptype in ("relation", "rollup", "people", "files", "created_by", "last_edited_by"):
        return str(inner)[:500]

    return str(inner)[:500]


def page_to_row(page: Dict[str, Any], property_order: List[str]) -> Dict[str, Any]:
    props = page.get("properties") or {}
    row: Dict[str, Any] = {"_page_id": page.get("id", "")}
    for name in property_order:
        row[name] = flatten_property_value(name, props.get(name, {}))
    row["_last_edited"] = page.get("last_edited_time", "")
    return row


class NotionExtractor:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or Config.NOTION_API_KEY
        if not key:
            raise ValueError("NOTION_API_KEY not configured")
        self._client = Client(auth=key)

    @staticmethod
    def _throttle():
        # Notion ~3 req/s average
        time.sleep(0.35)

    @retry_with_backoff(max_retries=4, initial_delay=0.5, exceptions=(Exception,))
    def query_database_all(self, database_id: str) -> List[Dict[str, Any]]:
        """Paginated databases.query."""
        results: List[Dict[str, Any]] = []
        cursor: Optional[str] = None
        while True:
            self._throttle()
            kwargs: Dict[str, Any] = {"database_id": database_id, "page_size": 100}
            if cursor:
                kwargs["start_cursor"] = cursor
            resp = self._client.databases.query(**kwargs)
            results.extend(resp.get("results") or [])
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")
        logger.info("Notion query_database_all: %s pages", len(results))
        return results

    def database_property_names(self, database_id: str) -> List[str]:
        self._throttle()
        db = self._client.databases.retrieve(database_id=database_id)
        props = db.get("properties") or {}
        # Stable order: title-like first, then alphabetical
        names = list(props.keys())
        title_first = [n for n in names if (props[n] or {}).get("type") == "title"]
        rest = sorted([n for n in names if n not in title_first])
        return title_first + rest

    def database_to_table(self, database_id: str) -> Dict[str, Any]:
        names = self.database_property_names(database_id)
        pages = self.query_database_all(database_id)
        rows = [page_to_row(p, names) for p in pages]
        return {"headers": names, "rows": rows, "count": len(rows)}
