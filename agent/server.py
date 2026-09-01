# agent/server.py
from dotenv import load_dotenv
load_dotenv()

# Extract text (using pdfplumber like your script does)
import pdfplumber
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime, timezone

from agent.graph import graph
# Import your logging helpers from your run script or a shared module
# from agent.run_pdf import save_markdown_log, append_to_master_csv

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

@app.post("/api/audit")
async def audit_uploaded_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Save the uploaded file temporarily
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    raw_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                raw_text += t + "\n"
                
    # Run through LangGraph
    initial_state = {
        "file_name": file.filename,
        "raw_text": raw_text,
        "doc_type": "unknown",
        "extracted": {},
        "field_status": {},
        "reconciliation_attempts": 0,
        "needs_human_review": False,
        "review_reason": None,
        "audit_result": None,
    }
    
    result = graph.invoke(initial_state)
    
    # Optionally save logs here automatically
    # save_markdown_log([result])
    # append_to_master_csv([result])
    
    return {
        "file_name": file.filename,
        "doc_type": result.get("doc_type"),
        "needs_human_review": result.get("needs_human_review"),
        "extracted": result.get("extracted"),
        "audit_result": result.get("audit_result")
    }

@app.get("/api/logs")
async def get_audit_ledger():
    """Optional endpoint for your chat/dashboard to fetch past logs from CSV."""
    csv_path = Path("logs/master_audit_ledger.csv")
    if not csv_path.exists():
        return []
    
    df = pd.read_csv(csv_path, keep_default_na=False)
    df = df.fillna("")
    
    return df.to_dict(orient="records")