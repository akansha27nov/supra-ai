# agent/server.py
from dotenv import load_dotenv

load_dotenv()

import shutil
import uuid
from pathlib import Path

import pandas as pd
import pdfplumber
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.gap_notice import generate_supplier_gap_notice
from agent.graph import graph
from agent.run_pdf import append_to_master_csv, load_sku_catalog

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

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Load SKU catalog once at startup — the graph passes it through in state
# so the audit result carries sku context into the ledger.
SKU_CATALOG = load_sku_catalog(Path("data/skus.json"))
print(f"[startup] Loaded {len(SKU_CATALOG)} SKUs from data/skus.json")


def _migrate_ledger_columns() -> None:
    """One-time migration for rows written before RecordID/ReviewStatus/Reviewer existed."""
    csv_path = LOG_DIR / "master_audit_ledger.csv"
    if not csv_path.exists():
        return

    df = pd.read_csv(csv_path, keep_default_na=False)
    changed = False

    if "RecordID" not in df.columns:
        df.insert(0, "RecordID", [str(uuid.uuid4()) for _ in range(len(df))])
        changed = True
    if "Supplier" not in df.columns:
        # Backfilling real supplier names for historic rows would need re-parsing the
        # source PDFs, which we don't have handles to here — mark them explicitly
        # rather than silently leaving a blank cell.
        df["Supplier"] = "Unknown Supplier"
        changed = True
    if "ReviewStatus" not in df.columns:
        df["ReviewStatus"] = "PENDING"
        changed = True
    if "Reviewer" not in df.columns:
        df["Reviewer"] = ""
        changed = True

    if changed:
        df.to_csv(csv_path, index=False)
        print(f"[startup] Migrated {csv_path} to include RecordID/Supplier/ReviewStatus")


_migrate_ledger_columns()


class ReviewDecisionRequest(BaseModel):
    decision: str  # "APPROVED" or "REJECTED"
    reviewer: str | None = None


class GapNoticeRequest(BaseModel):
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

    raw_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                raw_text += t + "\n"

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

    result = graph.invoke(
        initial_state,
        config={
            "run_name": f"audit_{file.filename}",
            "tags": ["live_upload"],
            "metadata": {"file_name": file.filename, "data_source": "live_upload"},
        },
    )

    # Defensive passthrough fields — graph nodes may not set these,
    # but append_to_master_csv reads them from the result dict.
    result.setdefault("file_name", file.filename)
    result.setdefault("associated_sku", None)
    result.setdefault("sku_match_status", "not_attempted")

    # Persist this audit to the master CSV ledger so the dashboard
    # "Recent Document Submissions" table picks it up on next loadLogs().
    append_to_master_csv([result], output_dir=LOG_DIR)

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
    """Returns past audit logs from the master CSV ledger.
    Normalizes column names so the frontend always receives `SKU` (not
    `Associated SKU`), keeping the AuditLog interface stable."""
    csv_path = LOG_DIR / "master_audit_ledger.csv"
    if not csv_path.exists():
        return []

    df = pd.read_csv(csv_path, keep_default_na=False)
    df = df.fillna("")

    # Normalize column name for the frontend
    if "Associated SKU" in df.columns and "SKU" not in df.columns:
        df = df.rename(columns={"Associated SKU": "SKU"})

    return df.to_dict(orient="records")


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

    csv_path = LOG_DIR / "master_audit_ledger.csv"

    if not csv_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No audit ledger found.",
        )

    df = pd.read_csv(csv_path, keep_default_na=False)

    required_columns = {"RecordID", "ReviewStatus"}
    missing = required_columns - set(df.columns)

    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Ledger missing columns: {', '.join(sorted(missing))}",
        )

    match = df["RecordID"].astype(str) == str(record_id)

    if not match.any():
        raise HTTPException(
            status_code=404,
            detail=f"No audit record found with id {record_id}",
        )

    df.loc[match, "ReviewStatus"] = decision

    # Add Reviewer column to older ledgers without breaking migration.
    if "Reviewer" not in df.columns:
        df["Reviewer"] = ""

    if body.reviewer:
        df.loc[match, "Reviewer"] = body.reviewer.strip()

    df.to_csv(csv_path, index=False)

    return {
        "record_id": record_id,
        "review_status": decision,
        "reviewer": body.reviewer,
    }


@app.post("/api/gap-notice")
async def create_gap_notice(body: GapNoticeRequest):
    """Generates a draft supplier gap-notice email from an existing audit result.
    A human reviewer edits/approves this before it's actually sent — this endpoint
    only drafts it, it never sends anything itself."""
    draft = generate_supplier_gap_notice(
        audit_result=body.audit_result,
        extracted_data=body.extracted,
        supplier_name=body.supplier_name,
        associated_sku=body.associated_sku,
    )
    return {"draft": draft}
