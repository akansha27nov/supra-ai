# agent/server.py
from dotenv import load_dotenv

load_dotenv()

import shutil
from pathlib import Path

import pandas as pd
import pdfplumber
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

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

    result = graph.invoke(initial_state)

    # Defensive passthrough fields — graph nodes may not set these,
    # but append_to_master_csv reads them from the result dict.
    result.setdefault("file_name", file.filename)
    result.setdefault("associated_sku", None)
    result.setdefault("sku_match_status", "not_attempted")

    # Persist this audit to the master CSV ledger so the dashboard
    # "Recent Document Submissions" table picks it up on next loadLogs().
    append_to_master_csv([result], output_dir=LOG_DIR)

    return {
        "file_name": file.filename,
        "doc_type": result.get("doc_type"),
        "needs_human_review": result.get("needs_human_review"),
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
