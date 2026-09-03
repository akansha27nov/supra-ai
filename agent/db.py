# agent/db.py
"""Postgres-backed persistence for the audit ledger and gap-notice store.
"""
from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Any

import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool

_POOL: SimpleConnectionPool | None = None


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add a Postgres instance and set this "
            "env var before starting the server."
        )
    # Render's DATABASE_URL sometimes uses postgres:// — psycopg2 wants postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def _get_pool() -> SimpleConnectionPool:
    global _POOL
    if _POOL is None:
        _POOL = SimpleConnectionPool(1, 10, dsn=_database_url())
    return _POOL


@contextmanager
def _cursor():
    pool = _get_pool()
    conn = pool.getconn()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                yield cur
    finally:
        pool.putconn(conn)


def init_db() -> None:
    """Creates both tables if they don't exist yet. Safe to call on every startup."""
    with _cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_ledger (
                record_id TEXT PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
                file_name TEXT,
                supplier TEXT,
                associated_sku TEXT,
                sku_match_status TEXT,
                decision TEXT,
                score INTEGER,
                flags TEXT,
                flags_detail JSONB,
                review_status TEXT DEFAULT 'PENDING',
                reviewer TEXT DEFAULT ''
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS gap_notices (
                notice_id TEXT PRIMARY KEY,
                audit_id TEXT,
                updated_at TEXT,
                data JSONB NOT NULL
            );
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_gap_notices_audit_id ON gap_notices(audit_id);"
        )
    print("[startup] audit_ledger + gap_notices tables ready")


# ---------------------------------------------------------------------------
# Audit ledger (replaces logs/master_audit_ledger.csv)
# ---------------------------------------------------------------------------

def insert_audit_records(results: list[dict[str, Any]]) -> None:
    """Equivalent of the old append_to_master_csv(). Assigns a record_id if
    missing (and writes it back onto the result dict, same as before) and
    inserts one row per result with ReviewStatus=PENDING."""
    import uuid

    with _cursor() as cur:
        for res in results:
            record_id = res.get("record_id") or str(uuid.uuid4())
            res["record_id"] = record_id

            file_name = res.get("file_name", "Unknown")
            sku = res.get("associated_sku") or "UNMATCHED"
            sku_match = res.get("sku_match_status", "not_attempted")

            extracted = res.get("extracted", {}) or {}
            supplier = extracted.get("supplier_name") or "Unknown Supplier"

            audit_res = res.get("audit_result", {}) or {}
            decision = audit_res.get("decision", "UNKNOWN")
            score = audit_res.get("score", 0)

            flags = audit_res.get("flags", [])
            flag_msgs = []
            for flg in flags:
                if isinstance(flg, dict):
                    flag_msgs.append(f"{flg.get('code')}: {flg.get('message')}")
                else:
                    flag_msgs.append(str(flg))
            flags_str = " | ".join(flag_msgs) if flag_msgs else "None"

            flags_detail_json = json.dumps(
                flags,
                default=lambda o: o.model_dump() if hasattr(o, "model_dump") else str(o),
            )

            cur.execute(
                """
                INSERT INTO audit_ledger
                    (record_id, file_name, supplier, associated_sku, sku_match_status,
                     decision, score, flags, flags_detail, review_status, reviewer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, 'PENDING', '')
                ON CONFLICT (record_id) DO NOTHING;
                """,
                (
                    record_id, file_name, supplier, sku, sku_match,
                    decision, score, flags_str, flags_detail_json,
                ),
            )


def fetch_audit_ledger() -> list[dict[str, Any]]:
    """Equivalent of the old pandas read of master_audit_ledger.csv, already
    shaped the way the frontend expects (SKU, FlagsDetail parsed to a list)."""
    with _cursor() as cur:
        cur.execute(
            """
            SELECT record_id AS "RecordID",
                   timestamp AS "Timestamp",
                   file_name AS "File Name",
                   supplier AS "Supplier",
                   associated_sku AS "SKU",
                   sku_match_status AS "SKU Match Status",
                   decision AS "Decision",
                   score AS "Score",
                   flags AS "Flags",
                   flags_detail AS "FlagsDetail",
                   review_status AS "ReviewStatus",
                   reviewer AS "Reviewer"
            FROM audit_ledger
            ORDER BY timestamp DESC;
            """
        )
        rows = cur.fetchall()

    records = []
    for row in rows:
        record = dict(row)
        # psycopg2 already decodes JSONB to a Python list/dict; guard anyway.
        if not isinstance(record.get("FlagsDetail"), list):
            record["FlagsDetail"] = record.get("FlagsDetail") or []
        records.append(record)
    return records


def update_review_status(record_id: str, decision: str, reviewer: str | None) -> bool:
    """Equivalent of the old CSV read-modify-write in PATCH /api/logs/{id}/review.
    Returns False if no row matched (caller raises 404)."""
    with _cursor() as cur:
        cur.execute(
            """
            UPDATE audit_ledger
            SET review_status = %s,
                reviewer = COALESCE(%s, reviewer)
            WHERE record_id = %s;
            """,
            (decision, reviewer.strip() if reviewer else None, record_id),
        )
        return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Gap notices (replaces data/gap_notices.json)
# ---------------------------------------------------------------------------

def save_gap_notice(record: dict[str, Any]) -> dict[str, Any]:
    with _cursor() as cur:
        cur.execute(
            """
            INSERT INTO gap_notices (notice_id, audit_id, updated_at, data)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (notice_id) DO UPDATE
                SET audit_id = EXCLUDED.audit_id,
                    updated_at = EXCLUDED.updated_at,
                    data = EXCLUDED.data;
            """,
            (
                record["notice_id"],
                record.get("audit_id"),
                str(record.get("updated_at", "")),
                json.dumps(record, default=str),
            ),
        )
    return record


def get_gap_notice(notice_id: str) -> dict[str, Any] | None:
    with _cursor() as cur:
        cur.execute("SELECT data FROM gap_notices WHERE notice_id = %s;", (notice_id,))
        row = cur.fetchone()
    return row["data"] if row else None


def get_gap_notice_by_audit_id(audit_id: str) -> dict[str, Any] | None:
    with _cursor() as cur:
        cur.execute(
            """
            SELECT data FROM gap_notices
            WHERE audit_id = %s
            ORDER BY updated_at DESC
            LIMIT 1;
            """,
            (audit_id,),
        )
        row = cur.fetchone()
    return row["data"] if row else None


def list_gap_notices() -> list[dict[str, Any]]:
    with _cursor() as cur:
        cur.execute("SELECT data FROM gap_notices;")
        rows = cur.fetchall()
    return [row["data"] for row in rows]


def delete_gap_notice(notice_id: str) -> bool:
    with _cursor() as cur:
        cur.execute("DELETE FROM gap_notices WHERE notice_id = %s;", (notice_id,))
        return cur.rowcount > 0
