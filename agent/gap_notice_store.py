# agent/gap_notice_store.py
"""Persistence for GapNoticeRecord, keyed by notice_id and linked via audit_id.

Was a single JSON file guarded by an in-process threading.Lock() — fine for
one worker process, not safe across multiple, and wiped on every Render
restart/redeploy since the filesystem is ephemeral. This now delegates to
agent/db.py (Postgres), keeping the exact same function names and signatures
so nothing importing from this module (agent/server.py) needs to change.
"""
from __future__ import annotations

from typing import Any

from agent import db


def save_record(record: dict[str, Any]) -> dict[str, Any]:
    """Upserts a GapNoticeRecord dict, keyed by its notice_id."""
    return db.save_gap_notice(record)


def get_record(notice_id: str) -> dict[str, Any] | None:
    """Retrieval by notice_id."""
    return db.get_gap_notice(notice_id)


def get_record_by_audit_id(audit_id: str) -> dict[str, Any] | None:
    """Returns the most-recently-updated notice for a given audit_id, if any."""
    return db.get_gap_notice_by_audit_id(audit_id)


def list_records() -> list[dict[str, Any]]:
    return db.list_gap_notices()


def delete_record(notice_id: str) -> bool:
    return db.delete_gap_notice(notice_id)
