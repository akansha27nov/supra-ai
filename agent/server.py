# agent/server.py
from dotenv import load_dotenv
load_dotenv()

import shutil
from pathlib import Path

import pdfplumber
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import db
from agent.gap_notice import (
    approve_gap_notice_for_sending,
    create_gap_notice_record,
    generate_supplier_gap_notice,
    send_gap_notice,
    update_gap_notice_draft,
)
from agent.gap_notice_store import (
    get_record,
    get_record_by_audit_id,
    list_records,
    save_record,
)
from agent.graph import ExtractionFailedError, graph
from agent.run_pdf import load_sku_catalog
from agent.schemas import ApproveGapNoticeRequest, GapNoticeStatus, UpdateGapNoticeRequest
from agent.telegram_dispatch import (
    TelegramNotConfigured,
    is_configured as is_telegram_configured,
    send_gap_notice_sent_alert,
)

app = FastAPI(title="Compliance Audit API")

# Enable CORS so your React app (running on localhost:3000 or similar) can talk to Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MIN_EXTRACTABLE_CHARS = 40

# Load SKU catalog once at startup — the graph passes it through in state
# so the audit result carries sku context into the ledger.
SKU_CATALOG = load_sku_catalog(Path("data/skus.json"))
print(f"[startup] Loaded {len(SKU_CATALOG)} SKUs from data/skus.json")

# Creates audit_ledger + gap_notices tables in Postgres if they don't exist yet.
# Requires DATABASE_URL to be set 
db.init_db()


class ReviewDecisionRequest(BaseModel):
    decision: str  # "APPROVED" or "REJECTED"
    reviewer: str | None = None


class GapNoticeRequest(BaseModel):
    audit_id: str
    audit_result: dict
    extracted: dict
    supplier_name: str = "Supplier"
    associated_sku: str | None = None


@app.post("/api/audit")
async def audit_uploaded_pdf(file: UploadFile = File(...)):   # noqa: B008
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Save the uploaded file temporarily
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:    # noqa: ASYNC230
        shutil.copyfileobj(file.file, buffer)

    try:
        raw_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    raw_text += t + "\n"
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Could not read '{file.filename}' as a PDF — the file may be corrupted "
                f"or not actually a PDF. ({e.__class__.__name__})"
            ),
        ) from e

    if len(raw_text.strip()) < MIN_EXTRACTABLE_CHARS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"'{file.filename}' has no extractable text (found "
                f"{len(raw_text.strip())} characters). This usually means the PDF is a "
                "scanned image without a text layer. Please upload a text-based PDF, or "
                "run OCR on it first."
            ),
        )

    # Run through LangGraph — pass sku_catalog so the pipeline can do
    # SKU-aware checks and the result carries sku context into the ledger.
    initial_state = {
        "file_name": file.filename,
        "raw_text": raw_text,
        "doc_type": "unknown",
        "extracted": {},
        "field_status": {},
        "reconciliation_attempts": 0,
        "needs_human_review": False,
        "review_reason": None,
        "sku_catalog": SKU_CATALOG,
        "associated_sku": None,
        "sku_match_status": "not_attempted",
        "audit_result": None,
    }

    try:
        result = graph.invoke(
            initial_state,
            config={
                "run_name": f"audit_{file.filename}",
                "tags": ["live_upload"],
                "metadata": {"file_name": file.filename, "data_source": "live_upload"},
            },
        )
    except ExtractionFailedError as e:
        # Never persist a failed extraction as if it were a real audit — no row
        # goes into audit_ledger here, and the reviewer sees a clean, specific
        # reason rather than a generic 500 / a blank result.
        raise HTTPException(status_code=502, detail=e.reason) from e

    # Defensive passthrough fields — graph nodes may not set these,
    # but insert_audit_records reads them from the result dict.
    result.setdefault("file_name", file.filename)
    result.setdefault("associated_sku", None)
    result.setdefault("sku_match_status", "not_attempted")

    # Persist this audit to Postgres so the dashboard "Recent Document
    # Submissions" table picks it up on next loadLogs(), and so it
    # survives a Render restart/redeploy (the old CSV did not).
    db.insert_audit_records([result])

    return {
        "record_id": result.get("record_id"),
        "file_name": file.filename,
        "doc_type": result.get("doc_type"),
        "needs_human_review": result.get("needs_human_review"),
        "review_reason": result.get("review_reason"),
        "associated_sku": result.get("associated_sku"),
        "sku_match_status": result.get("sku_match_status"),
        "extracted": result.get("extracted"),
        "audit_result": result.get("audit_result"),
    }


@app.get("/api/logs")
async def get_audit_ledger():
    """Returns past audit logs from Postgres.

    Also joins in each row's gap-notice lifecycle status (AC-17 #6) by
    looking it up in the gap-notice store keyed by RecordID == audit_id, at
    read time rather than writing it into the ledger row itself — the ledger
    row is written once at audit time, before any gap notice can exist, so
    a written-in status column would go stale the moment a reviewer
    edited/approved/sent the notice.
    """
    records = db.fetch_audit_ledger()

    # Join in gap-notice status per record, when one exists. list_records()
    # once + an in-memory index avoids one store read per ledger row.
    notices_by_audit_id: dict[str, dict] = {}
    for notice in list_records():
        audit_id = notice.get("audit_id")
        if not audit_id:
            continue
        existing = notices_by_audit_id.get(audit_id)
        if existing is None or notice.get("updated_at", "") > existing.get("updated_at", ""):
            notices_by_audit_id[audit_id] = notice

    for record in records:
        notice = notices_by_audit_id.get(str(record.get("RecordID", "")))
        record["GapNoticeStatus"] = notice.get("status") if notice else ""

    return records


@app.patch("/api/logs/{record_id}/review")
async def submit_review_decision(
    record_id: str,
    body: ReviewDecisionRequest,
):
    """Persist a human reviewer's APPROVED/REJECTED decision."""
    decision = body.decision.strip().upper()

    if decision not in ("APPROVED", "REJECTED"):
        raise HTTPException(
            status_code=400,
            detail="decision must be APPROVED or REJECTED",
        )

    updated = db.update_review_status(record_id, decision, body.reviewer)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"No audit record found with id {record_id}",
        )

    return {
        "record_id": record_id,
        "review_status": decision,
        "reviewer": body.reviewer,
    }


@app.post("/api/gap-notice")
async def create_gap_notice(body: GapNoticeRequest):
    """Creates (or returns the existing) persisted gap-notice record for an audit.

    Idempotent per audit_id: if a record already exists it's returned as-is
    — including whatever edits or approval state a reviewer already made —
    and a fresh one is only generated and persisted the first time this
    audit is seen.
    """
    existing = get_record_by_audit_id(body.audit_id)
    if existing:
        return {"record": existing, "created": False}

    try:
        result = generate_supplier_gap_notice(
            audit_result=body.audit_result,
            extracted_data=body.extracted,
            supplier_name=body.supplier_name,
            associated_sku=body.associated_sku,
        )
    except ExtractionFailedError as e:
        raise HTTPException(status_code=502, detail=e.reason) from e

    if not isinstance(result, dict):
        # "No gap notice required..." early-return case — nothing to persist.
        return {"record": None, "created": False, "message": result}

    record = create_gap_notice_record(
        audit_id=body.audit_id,
        supplier_name=body.supplier_name,
        structured_notice=result,
    )
    save_record(record)
    return {"record": record, "created": True}


@app.get("/api/gap-notice/by-audit/{audit_id}")
async def get_gap_notice_by_audit(audit_id: str):
    """Lets the UI check "does a gap notice already exist for this audit?"
    before generating a fresh one. Placed before the /{notice_id} route
    below so "by-audit" isn't swallowed as a literal notice_id."""
    record = get_record_by_audit_id(audit_id)
    if not record:
        raise HTTPException(
            status_code=404, detail=f"No gap notice found for audit {audit_id}"
        )
    return record


@app.get("/api/gap-notice/{notice_id}")
async def get_gap_notice(notice_id: str):
    """Retrieval by notice_id."""
    record = get_record(notice_id)
    if not record:
        raise HTTPException(
            status_code=404, detail=f"No gap notice found with id {notice_id}"
        )
    return record


@app.patch("/api/gap-notice/{notice_id}")
async def edit_gap_notice(notice_id: str, body: UpdateGapNoticeRequest):
    """Persists a reviewer's edits to the draft and moves status -> EDITED."""
    record = get_record(notice_id)
    if not record:
        raise HTTPException(
            status_code=404, detail=f"No gap notice found with id {notice_id}"
        )

    updated = update_gap_notice_draft(record, body.model_dump())
    save_record(updated)
    return updated


@app.post("/api/gap-notice/{notice_id}/approve")
async def approve_gap_notice(notice_id: str, body: ApproveGapNoticeRequest):
    """Records that a compliance officer signed off on the current version
    and moves status -> APPROVED_FOR_SENDING."""
    record = get_record(notice_id)
    if not record:
        raise HTTPException(
            status_code=404, detail=f"No gap notice found with id {notice_id}"
        )

    approved = approve_gap_notice_for_sending(record, body.reviewer_id)
    save_record(approved)
    return approved


@app.post("/api/gap-notice/{notice_id}/send")
async def send_gap_notice_endpoint(notice_id: str):
    """Moves status -> SENT. Requires APPROVED_FOR_SENDING first.

    `dispatch_status` refers to *supplier* delivery and stays "simulated" —
    there is still no real email/SMTP/SendGrid integration wired up.

    If TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID are configured, a best-effort
    internal notification is posted confirming the notice was marked SENT —
    its failure never blocks or rolls back the SENT transition above.
    """
    record = get_record(notice_id)
    if not record:
        raise HTTPException(
            status_code=404, detail=f"No gap notice found with id {notice_id}"
        )

    if record.get("status") != GapNoticeStatus.APPROVED_FOR_SENDING:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot send notice in status '{record.get('status')}'; "
                "it must be APPROVED_FOR_SENDING first."
            ),
        )

    try:
        sent = send_gap_notice(record)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    save_record(sent)

    telegram_notification = "not_configured"
    if is_telegram_configured():
        try:
            send_gap_notice_sent_alert(sent)
            telegram_notification = "notified"
        except TelegramNotConfigured:
            telegram_notification = "not_configured"
        except Exception as exc:  # noqa: BLE001 - best-effort side channel
            print(f"[gap-notice] Telegram alert failed for {notice_id}: {exc}")
            telegram_notification = "failed"

    return {
        "record": sent,
        "dispatch_status": "simulated",
        "telegram_notification": telegram_notification,
    }
