# agent/graph.py

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END, START

from agent.schemas import (
    DocumentClassification,
    ExtractedCertificateData,
    AuditResult,
    RuleViolation,
    FieldStatusType,
)


# ==========================================
# 1. State Definition
# ==========================================

class AuditState(TypedDict):
    file_name: str
    raw_text: str
    doc_type: Literal["lab_test_report", "manufacturer_self_declaration", "unknown"]
    extracted: Dict[str, Any]
    field_status: Dict[str, FieldStatusType]
    reconciliation_attempts: int
    needs_human_review: bool
    review_reason: Optional[str]
    audit_result: Optional[Dict[str, Any]]


# ==========================================
# 2. Graph Node Functions
# ==========================================

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)


def extract_node(state: AuditState) -> Dict[str, Any]:
    """Initial LLM extraction call."""
    structured_llm = llm.with_structured_output(ExtractedCertificateData)
    prompt = f"Extract compliance information from the following document:\n\n{state['raw_text']}"
    
    extracted: ExtractedCertificateData = structured_llm.invoke(prompt)
    
    return {
        "extracted": extracted.model_dump(),
        "reconciliation_attempts": 0,
        "needs_human_review": False,
        "review_reason": None,
    }


def classify_doc_type_node(state: AuditState) -> Dict[str, Any]:
    """Classifies document type prior to field validation."""
    structured_llm = llm.with_structured_output(DocumentClassification)
    prompt = (
        "Classify this compliance document as 'lab_test_report', 'manufacturer_self_declaration', or 'unknown'.\n"
        f"Text context:\n{state['raw_text'][:1500]}"
    )
    result: DocumentClassification = structured_llm.invoke(prompt)
    
    return {"doc_type": result.doc_type}


def validate_fields_node(state: AuditState) -> Dict[str, Any]:
    """Evaluates field presence vs doc_type expectations."""
    data = state["extracted"]
    doc_type = state.get("doc_type", "unknown")
    field_status: Dict[str, FieldStatusType] = {}

    # 1. SKU Code
    field_status["sku_code"] = "present" if data.get("sku_code") else "absent_expected"

    # 2. Accreditation ID
    if data.get("accreditation_id"):
        field_status["accreditation_id"] = "present"
    elif doc_type == "manufacturer_self_declaration":
        field_status["accreditation_id"] = "absent_appropriate"
    else:
        field_status["accreditation_id"] = "absent_expected"

    # 3. Expiration Date
    if data.get("expiration_date"):
        field_status["expiration_date"] = "present"
    elif doc_type == "manufacturer_self_declaration":
        field_status["expiration_date"] = "absent_appropriate"
    else:
        field_status["expiration_date"] = "absent_expected"

    # 4. Tested Lead PPM
    if data.get("tested_lead_ppm") is not None:
        field_status["tested_lead_ppm"] = "present"
    elif data.get("is_statutory_limit"):
        field_status["tested_lead_ppm"] = "absent_appropriate"
    else:
        field_status["tested_lead_ppm"] = "absent_appropriate"

    # Evaluate overall resolution state
    has_ambiguity = any(status in ["absent_expected", "ambiguous"] for status in field_status.values())
    
    return {
        "field_status": field_status,
        "needs_human_review": (has_ambiguity and state["reconciliation_attempts"] >= 2)
    }


def reconcile_node(state: AuditState) -> Dict[str, Any]:
    """Targeted re-extraction attempting to resolve absent_expected/ambiguous fields."""
    current_data = state["extracted"]
    attempts = state["reconciliation_attempts"]
    ambiguous_fields = [
        field for field, status in state["field_status"].items() 
        if status in ["absent_expected", "ambiguous"]
    ]
    
    reconcile_prompt = (
        f"Targeted Re-Extraction Attempt #{attempts + 1}.\n"
        f"We are missing or need clarification on these fields: {ambiguous_fields}.\n"
        f"Current extraction:\n{json.dumps(current_data, indent=2)}\n\n"
        f"Source Text:\n{state['raw_text']}"
    )
    
    structured_llm = llm.with_structured_output(ExtractedCertificateData)
    recalculated: ExtractedCertificateData = structured_llm.invoke(reconcile_prompt)
    
    updated_data = recalculated.model_dump()
    for k, v in updated_data.items():
        if v is not None:
            current_data[k] = v

    return {
        "extracted": current_data,
        "reconciliation_attempts": attempts + 1
    }


def rule_engine_node(state: AuditState) -> Dict[str, Any]:
    """Evaluates compliance logic cleanly respecting field_status states."""
    data = state["extracted"]
    statuses = state["field_status"]
    doc_type = state["doc_type"]
    score = 0
    violations: List[RuleViolation] = []
    
    # Check 1: Lead PPM (Skipped silently if absent_appropriate)
    if statuses.get("tested_lead_ppm") == "present" and not data.get("is_statutory_limit"):
        lead_ppm = data.get("tested_lead_ppm", 0.0)
        if lead_ppm > 1000.0:
            score += 95
            violations.append(
                RuleViolation(
                    code="LEAD_EXCESS_VIOLATION",
                    severity_score=95,
                    message=f"Measured {lead_ppm} ppm > threshold 1000 ppm"
                )
            )
    
    # Check 2: Expiration Date (Skipped silently if absent_appropriate)
    if statuses.get("expiration_date") == "present":
        exp_date_str = data.get("expiration_date")
        if exp_date_str:
            try:
                exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d")
                if exp_date < datetime.now():
                    score += 90
                    violations.append(
                        RuleViolation(
                            code="EXPIRED_CERTIFICATE",
                            severity_score=90,
                            message=f"Expired on {exp_date_str}"
                        )
                    )
            except ValueError:
                pass

    # Check 3: Laboratory Accreditation Validation
    if doc_type == "lab_test_report":
        acc_id = data.get("accreditation_id") or ""
        valid_prefixes = ("DAKKS-", "CNAS-", "UKAS-")
        if not acc_id:
            score += 70
            violations.append(
                RuleViolation(
                    code="UNACCREDITED_LABORATORY",
                    severity_score=70,
                    message="No accreditation ID present"
                )
            )
        elif not any(acc_id.startswith(prefix) for prefix in valid_prefixes):
            score += 85
            violations.append(
                RuleViolation(
                    code="SUSPICIOUS_LABORATORY",
                    severity_score=85,
                    message=f"ID '{acc_id}' failed prefix validation"
                )
            )

    final_score = min(score, 100)
    decision = "REJECTED" if final_score >= 85 else ("FLAGGED" if final_score >= 50 else "APPROVED")

    audit_result = AuditResult(
        score=final_score,
        decision=decision,
        flags=violations,
        audited_at=datetime.now(timezone.utc).isoformat()
    )

    return {"audit_result": audit_result.model_dump()}


def flag_for_human_review_node(state: AuditState) -> Dict[str, Any]:
    """First-class human escalation node when fields remain unresolved after 2 retries."""
    unresolved = [f for f, s in state["field_status"].items() if s in ["absent_expected", "ambiguous"]]
    reason = f"Unresolved fields after {state['reconciliation_attempts']} retries: {unresolved}"
    
    audit_result = AuditResult(
        score=100,
        decision="REQUIRES_HUMAN_REVIEW",
        flags=[
            RuleViolation(
                code="UNRESOLVED_CRITICAL_FIELDS",
                severity_score=100,
                message=reason
            )
        ],
        audited_at=datetime.now(timezone.utc).isoformat()
    )
    
    return {
        "needs_human_review": True,
        "review_reason": reason,
        "audit_result": audit_result.model_dump()
    }


# ==========================================
# 3. Conditional Edge Logic
# ==========================================

def route_after_validation(state: AuditState) -> Literal["rule_engine", "reconcile", "flag_for_human_review"]:
    """Routes based on field resolution and bounded reconciliation retries."""
    ambiguous = any(s in ["absent_expected", "ambiguous"] for s in state["field_status"].values())
    
    if not ambiguous:
        return "rule_engine"
    
    if state["reconciliation_attempts"] < 2:
        return "reconcile"
    
    return "flag_for_human_review"


# ==========================================
# 4. Graph Construction & Compilation
# ==========================================

builder = StateGraph(AuditState)

# Add Nodes
builder.add_node("extract", extract_node)
builder.add_node("classify_doc_type", classify_doc_type_node)
builder.add_node("validate_fields", validate_fields_node)
builder.add_node("reconcile", reconcile_node)
builder.add_node("rule_engine", rule_engine_node)
builder.add_node("flag_for_human_review", flag_for_human_review_node)

# Flow Edges
builder.add_edge(START, "extract")
builder.add_edge("extract", "classify_doc_type")
builder.add_edge("classify_doc_type", "validate_fields")

# Conditional Edges
builder.add_conditional_edges(
    "validate_fields",
    route_after_validation,
    {
        "rule_engine": "rule_engine",
        "reconcile": "reconcile",
        "flag_for_human_review": "flag_for_human_review"
    }
)

builder.add_edge("reconcile", "validate_fields")
builder.add_edge("rule_engine", END)
builder.add_edge("flag_for_human_review", END)

# Compile Executable Graph
graph = builder.compile()