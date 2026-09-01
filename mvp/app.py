# app.py - streamlit UI for the AI Supplier Compliance Screening Agent

import sys
from pathlib import Path

import pandas as pd
import pdfplumber
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
if not (ROOT_DIR / "agent").exists():
    ROOT_DIR = ROOT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from agent.gap_notice import generate_supplier_gap_notice
from agent.graph import graph

st.set_page_config(
    page_title="AI Supplier Compliance Screening",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ AI Supplier Compliance Screening Agent")
st.markdown("Automated compliance verification using LangGraph, structured extraction, and deterministic rule validation.")

# Initialize Session State for Tableau / Dashboard Export
if "audit_history" not in st.session_state:
    st.session_state.audit_history = []

def extract_pdf_text(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text

# Sidebar Controls
st.sidebar.header("Document Upload")
uploaded_files = st.sidebar.file_uploader(
    "Upload Compliance PDFs (DoCs / Lab Reports)",
    type=["pdf"],
    accept_multiple_files=True
)

st.sidebar.markdown("---")
st.sidebar.header("Tableau / Dashboard Export")

if st.sidebar.button("Export Audit History to CSV"):
    if st.session_state.audit_history:
        df = pd.DataFrame(st.session_state.audit_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="💾 Download compliance_audit_export.csv",
            data=csv,
            file_name="compliance_audit_export.csv",
            mime="text/csv"
        )
    else:
        st.sidebar.warning("No audit runs recorded yet.")

# Main Interface Execution
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"📄 Audit Summary: {uploaded_file.name}")
        
        with st.spinner("Executing LangGraph Compliance Pipeline..."):
            raw_text = extract_pdf_text(uploaded_file)
            initial_state = {
                "file_name": uploaded_file.name,
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
            extracted = result.get("extracted", {})
            audit_res = result.get("audit_result", {}) or {}
            decision = audit_res.get("decision", "UNKNOWN")
            score = audit_res.get("score", 0)
            flags = audit_res.get("flags", [])

            # Record entry for CSV export
            st.session_state.audit_history.append({
                "file_name": uploaded_file.name,
                "doc_type": result.get("doc_type"),
                "sku_code": extracted.get("sku_code"),
                "decision": decision,
                "risk_score": score,
                "needs_human_review": result.get("needs_human_review"),
                "reconciliation_attempts": result.get("reconciliation_attempts"),
                "flags_count": len(flags),
                "audited_at": audit_res.get("audited_at")
            })

        # Top Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Doc Type", result.get("doc_type"))
        
        decision_color = {
            "APPROVED": "🟢",
            "FLAGGED": "🟡",
            "REJECTED": "🔴",
            "REQUIRES_HUMAN_REVIEW": "🟠"
        }.get(decision, "⚪")
        
        col2.metric("Decision", f"{decision_color} {decision}")
        col3.metric("Risk Priority Score", f"{score} / 100")
        col4.metric("Human Review Needed", "Yes" if result.get("needs_human_review") else "No")

        # Tabs for Deep Dive
        tab_details, tab_flags, tab_notice = st.tabs(["Extracted Data", "Violations & Flags", "✉️ Supplier Gap Notice"])

        with tab_details:
            st.json(extracted)

        with tab_flags:
            if flags:
                for flag in flags:
                    st.error(f"**[{flag['code']}]** (Severity: {flag['severity_score']})\n\n{flag['message']}")
            else:
                st.success("No risk violations detected.")

        with tab_notice:
            if decision != "APPROVED":
                st.markdown("#### Draft Supplier Request")
                supplier_name = st.text_input("Supplier Name", value="Supplier Inc.", key=f"sup_{uploaded_file.name}")
                
                draft_notice = generate_supplier_gap_notice(
                    audit_result=audit_res,
                    extracted_data=extracted,
                    supplier_name=supplier_name
                )
                
                edited_draft = st.text_area(
                    "Review & Edit Email Draft before sending:",
                    value=draft_notice,
                    height=250,
                    key=f"draft_{uploaded_file.name}"
                )
                st.button("Approve & Send Notice", key=f"send_{uploaded_file.name}", on_click=lambda: st.success("Notice queued for dispatch!"))
            else:
                st.info("Document is approved. No supplier gap notice required.")
                
        st.markdown("---")