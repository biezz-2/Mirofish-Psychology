"""Unit tests for Notion property flattening (no network)."""

import pytest

from app.integrations.notion_service import flatten_property_value, page_to_row


def test_flatten_title():
    prop = {"type": "title", "title": [{"plain_text": "Hello", "type": "text"}]}
    assert flatten_property_value("Name", prop) == "Hello"


def test_flatten_number():
    assert flatten_property_value("Age", {"type": "number", "number": 25}) == "25"
    assert flatten_property_value("X", {"type": "number", "number": None}) == ""


def test_page_to_row_order():
    page = {
        "id": "abc",
        "last_edited_time": "2026-01-01T00:00:00Z",
        "properties": {
            "A": {"type": "title", "title": [{"plain_text": "t", "type": "text"}]},
            "B": {"type": "number", "number": 3},
        },
    }
    row = page_to_row(page, ["A", "B"])
    assert row["A"] == "t"
    assert row["B"] == "3"
    assert row["_page_id"] == "abc"
