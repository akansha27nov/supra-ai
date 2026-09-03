import sys
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
sys.path.append(str(Path(__file__).resolve().parent.parent))

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable
import uuid
from agent.llm_reliability import ExtractionFailedError, invoke_with_retry  # noqa: F401 (re-exported for callers)
from agent.schemas import GapNoticeRecord, GapNoticeStatus

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# ==========================================
# 1. Output Schema
# ==========================================

class StructuredGapNotice(BaseModel):
    """Structured notice isolating the components of a compliance gap."""
    supplier_name: str = Field(..., description="Name of the supplier.")
    document_reference: str = Field(..., description="Reference to the document or SKU evaluated.")
    failed_rules: list[str] = Field(..., description="List of compliance rules that failed.")
    evidence: list[str] = Field(..., description="List of exact quotes or evidence from the document causing the failures.")
    corrective_action: str = Field(..., description="Required actions the supplier must take to resolve the gaps.")
    email_draft: str = Field(..., description="A concise, polite draft email to the supplier containing all of the above.")

# ==========================================
# 2. Generator Function
# ==========================================

@traceable(name="generate_supplier_gap_notice", run_type="chain")
def generate_supplier_gap_notice(
    audit_result: dict,
    extracted_data: dict,
    supplier_name: str = "Supplier",
    associated_sku: str | None = None,
) -> dict[str, Any] | str:
    """
    Generates a structured notice containing distinct data fields and a draft email 
    to a supplier regarding compliance gaps.
    """
    decision = audit_result.get("decision")
    flags = audit_result.get("flags", [])

    if decision == "APPROVED" or not flags:
        return "No gap notice required; document is approved."

    actionable_flags = [f for f in flags if f.get("severity_score", 0) > 0]
    if not actionable_flags:
        return "No gap notice required; no actionable violations were found."

    issues_info = []
    evidence_detail: list[dict[str, Any]] = []
    for flag in actionable_flags:
        issue_text = f"- Rule: {flag.get('code')}\n  Message: {flag.get('message')}"
        evidence = flag.get("evidence")
        quote = None
        page_number = None
        section = None
        if evidence:
            if isinstance(evidence, dict):
                quote = evidence.get("exact_quote")
                page_number = evidence.get("page_number")
                section = evidence.get("section")
            else:
                quote = getattr(evidence, "exact_quote", None)
                page_number = getattr(evidence, "page_number", None)
                section = getattr(evidence, "section", None)
            if quote:
                issue_text += f"\n  Evidence: {quote}"

        evidence_detail.append({
            "rule_code": flag.get("code"),
            "exact_quote": quote,
            "page_number": page_number,
            "section": section,
        })

        issues_info.append(issue_text)

    issues_list = "\n\n".join(issues_info)

    covered_parts = extracted_data.get("covered_part_numbers") or []
    sku_display = associated_sku or (", ".join(covered_parts) if covered_parts else "[Unknown SKU]")
    doc_id = extracted_data.get("certificate_id") or "Unknown Document ID"

    prompt = ChatPromptTemplate.from_messages([
        (
            "system", 
            ( 
                "You are a professional procurement and compliance officer. "
                "Extract the required structured fields and draft a concise, polite email to a supplier "
                "requesting updated documentation based on the identified compliance gaps and evidence. "
                "Do not invent any information."
            )
        ),
        (
            "user", 
            (
                "Supplier Name: {supplier_name}\n"
                "Product / SKU: {sku}\n"
                "Document Reference: {doc_id}\n"
                "Decision: {decision}\n"
                "Identified Issues & Evidence:\n{issues_list}\n\n"
                "Please generate the structured gap notice and email draft."
            )
        )
    ])

    structured_llm = llm.with_structured_output(StructuredGapNotice)
    chain = prompt | structured_llm
    
    response = invoke_with_retry(
        lambda: chain.invoke({
            "supplier_name": supplier_name,
            "sku": sku_display,
            "doc_id": doc_id,
            "decision": decision,
            "issues_list": issues_list,
        }),
        step="gap_notice_draft",
    )

    result = response.model_dump()
    result["evidence_detail"] = evidence_detail
    return result

@traceable(name="create_gap_notice_record", run_type="chain")
def create_gap_notice_record(
    audit_id: str,
    supplier_name: str,
    structured_notice: dict
) -> dict[str, Any]:
    """Initializes a persisted gap notice record in 'DRAFT' status from generated output.

    `evidence` is populated from structured_notice["evidence_detail"] (the
    rule engine's own RuleViolation.evidence, threaded through by
    generate_supplier_gap_notice) rather than structured_notice["evidence"]
    (the LLM's free-text paraphrase), so the persisted record's evidence
    field carries real page/quote/section linkage. Falls back to an empty
    list for any caller that doesn't supply evidence_detail (e.g. a manually
    constructed structured_notice dict in a test or script).
    """
    record = GapNoticeRecord(
        notice_id=str(uuid.uuid4()),
        audit_id=audit_id,
        supplier_name=supplier_name,
        status=GapNoticeStatus.DRAFT,
        failed_rules=structured_notice.get("failed_rules", []),
        evidence=structured_notice.get("evidence_detail", []),
        corrective_action=structured_notice.get("corrective_action"),
        editable_email_draft=structured_notice.get("email_draft", ""),
    )
    return record.model_dump()


@traceable(name="update_gap_notice_draft", run_type="chain")
def update_gap_notice_draft(
    record: dict[str, Any],
    updates: dict[str, Any]
) -> dict[str, Any]:
    """Updates the notice content with reviewer edits and changes status to EDITED."""
    record["editable_email_draft"] = updates.get("editable_email_draft", record["editable_email_draft"])
    if updates.get("corrective_action"):
        record["corrective_action"] = updates.get("corrective_action")
    
    record["status"] = GapNoticeStatus.EDITED
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    return record


@traceable(name="approve_gap_notice_for_sending", run_type="chain")
def approve_gap_notice_for_sending(
    record: dict[str, Any],
    reviewer_id: str
) -> dict[str, Any]:
    """Records that the reviewed/edited version is approved for external sending."""
    record["status"] = GapNoticeStatus.APPROVED_FOR_SENDING
    record["approved_by"] = reviewer_id
    record["approved_at"] = datetime.now(timezone.utc).isoformat()
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    return record


@traceable(name="send_gap_notice", run_type="chain")
def send_gap_notice(record: dict[str, Any]) -> dict[str, Any]:
    """Transitions an APPROVED_FOR_SENDING record to SENT.
    """
    if record.get("status") != GapNoticeStatus.APPROVED_FOR_SENDING:
        raise ValueError(
            f"Cannot send a notice in status '{record.get('status')}'; "
            "it must be APPROVED_FOR_SENDING first."
        )
    record["status"] = GapNoticeStatus.SENT
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    return record