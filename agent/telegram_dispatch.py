# agent/telegram_dispatch.py
"""Telegram notification for gap-notice lifecycle events.
"""
from __future__ import annotations

import os
from typing import Any

import requests

TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramNotConfigured(Exception):
    """Raised when TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID isn't set."""


def is_configured() -> bool:
    return bool(os.getenv("TELEGRAM_BOT_TOKEN")) and bool(os.getenv("TELEGRAM_CHAT_ID"))


def _format_sent_alert(record: dict[str, Any]) -> str:
    """Plain-text alert — deliberately NOT Markdown/HTML formatted.

    Every field here (supplier_name, failed_rules, approved_by) originates
    from parsed supplier documents or the rule engine, not from a fixed,
    reviewed template. Telegram's Markdown parser treats _, *, `, [ as
    formatting delimiters; an odd count of any of them anywhere in this
    message — one unescaped underscore in a single rule code is enough —
    desyncs the parser for everything after it and the whole send fails
    with a 400, even though nothing about the content is actually invalid.
    Plain text has no delimiters to get out of sync, so it can't fail this
    way regardless of what a future rule code or supplier name contains.
    """
    failed_rules = record.get("failed_rules") or []
    issues_block = "\n".join(f"- {r}" for r in failed_rules) or "- (none listed)"

    return (
        "\U0001F4E4 GAP NOTICE SENT\n\n"
        f"Supplier: {record.get('supplier_name', 'N/A')}\n"
        f"Audit ID: {record.get('audit_id', 'N/A')}\n"
        f"Notice ID: {record.get('notice_id', 'N/A')}\n"
        f"Approved by: {record.get('approved_by') or 'N/A'}\n\n"
        f"Failed Rules:\n{issues_block}\n\n"
        "This confirms the notice was recorded as SENT in Supra AI. "
        "No supplier-facing email dispatch is wired up yet — this alert "
        "is for internal visibility only."
    )


def send_gap_notice_sent_alert(record: dict[str, Any]) -> dict[str, Any]:
    """Posts a SENT notification for `record` to the configured Telegram chat.

    Raises TelegramNotConfigured if the env vars aren't set. Raises
    requests.RequestException on network/API failures. Callers should treat
    this as best-effort: a Telegram failure should never block or roll back
    the underlying SENT status transition, which is the actual lifecycle
    state change and is persisted independently of whether this notification
    succeeds.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise TelegramNotConfigured(
            "TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID not set in environment"
        )

    response = requests.post(
        f"{TELEGRAM_API_BASE}/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": _format_sent_alert(record)
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()