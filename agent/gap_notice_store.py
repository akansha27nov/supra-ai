# agent/gap_notice_store.py
"""File-backed persistence for GapNoticeRecord, keyed by notice_id and linked
via audit_id.

AC-17 background: create_gap_notice_record(), update_gap_notice_draft(), and
approve_gap_notice_for_sending() in gap_notice.py are pure functions -- each
takes a record dict in and returns a modified record dict out, with nowhere
for that dict to land. Call create_gap_notice_record() twice and you get two
unrelated dicts, not "the same notice, now with an edit." This module gives
those functions a place to persist their output: a single JSON file, keyed by
notice_id, matching the existing CSV/JSON logging pattern already used
elsewhere in this repo (logs/master_audit_ledger.csv,
logs/extracted_data_*.json) rather than introducing a database dependency for
an MVP.

Concurrency note: this is a read-modify-write on a JSON file guarded by an
in-process lock. That's fine for the current single FastAPI worker process,
but it is NOT safe across multiple worker processes -- swap for a real
datastore (SQLite, Postgres, etc.) before scaling out.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()

DEFAULT_STORE_PATH = Path("data/gap_notices.json")


def _load(store_path: Path) -> dict[str, Any]:
    if not store_path.exists():
        return {}
    text = store_path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    return json.loads(text)


def _save(store_path: Path, data: dict[str, Any]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temp file and atomically replace, so a crash mid-write can't
    # leave the store as truncated/invalid JSON.
    tmp_path = store_path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    tmp_path.replace(store_path)


def save_record(
    record: dict[str, Any], store_path: Path = DEFAULT_STORE_PATH
) -> dict[str, Any]:
    """Upserts a GapNoticeRecord dict, keyed by its notice_id."""
    with _LOCK:
        data = _load(store_path)
        data[record["notice_id"]] = record
        _save(store_path, data)
    return record


def get_record(
    notice_id: str, store_path: Path = DEFAULT_STORE_PATH
) -> dict[str, Any] | None:
    """Retrieval by notice_id (AC-17 #2 -- there was previously no way to do this)."""
    with _LOCK:
        data = _load(store_path)
    return data.get(notice_id)


def get_record_by_audit_id(
    audit_id: str, store_path: Path = DEFAULT_STORE_PATH
) -> dict[str, Any] | None:
    """Returns the most-recently-updated notice for a given audit_id, if any.

    This is what closes AC-17 #5: an auditor looking at a rejected document
    can now ask "does a gap notice already exist for this audit?" instead of
    starting from zero every visit. In principle an audit could accumulate
    more than one notice over time (e.g. re-drafted after further supplier
    correspondence); returning the latest by updated_at keeps this a single,
    well-defined lookup rather than requiring history-browsing UI in this pass.
    """
    with _LOCK:
        data = _load(store_path)
    matches = [r for r in data.values() if r.get("audit_id") == audit_id]
    if not matches:
        return None
    return max(matches, key=lambda r: r.get("updated_at", ""))


def list_records(store_path: Path = DEFAULT_STORE_PATH) -> list[dict[str, Any]]:
    with _LOCK:
        data = _load(store_path)
    return list(data.values())


def delete_record(notice_id: str, store_path: Path = DEFAULT_STORE_PATH) -> bool:
    with _LOCK:
        data = _load(store_path)
        if notice_id not in data:
            return False
        del data[notice_id]
        _save(store_path, data)
    return True
