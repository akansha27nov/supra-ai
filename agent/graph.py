# agent/graph.py

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, TypedDict
from langchain_openai import ChatOpenAI
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
    # --- SKU resolution (new) ---
    sku_catalog: Dict[str, Dict[str, Any]]          # provided at invoke time, e.g. loaded from skus.json
    associated_sku: Optional[str]                    # either provided directly, or resolved deterministically
    sku_match_status: Literal["matched", "unmatched", "not_attempted"]
    audit_result: Optional[Dict[str, Any]]


# ==========================================
# 2. Constants (kept in sync with langsmith/trace_sample.py —
#    if you change one, change the other, or better, factor both
#    out into a single shared `compliance_rules.py` module)
# ==========================================

DEFAULT_LEAD_PPM_THRESHOLD = 1000
KNOWN_ACCREDITATION_PREFIXES = ("DAKKS-", "CNAS-", "DAT-P-", "UKAS-", "ANAB-", "A2LA-")
DEPRECATED_SAFETY_STANDARDS = ("EN 60950", "EN 60065", "EN 55020")
DEPRECATED_ROHS_STANDARDS = ("EN 50581",)

# RoHS Annex II only ever specifies two restricted-substance threshold values:
# 100 ppm (Cadmium) or 1000 ppm (everything else, including lead). A value the
# LLM has tagged `is_statutory_limit=True` that isn't one of these two numbers
# is almost certainly a mislabeled *measured* result, not a real legal citation —
# this caught a real 23,800 ppm lead violation that was being silently skipped
# because it was mistagged as a statutory limit. See rule_engine_node Check -1.
KNOWN_STATUTORY_THRESHOLDS = (100.0, 1000.0)

# Explicit fraud/placeholder markers vs. "we just don't recognize this format" —
# these are NOT the same finding and shouldn't carry the same severity. A prefix
# allowlist cannot cover every real accreditation body's ID scheme (SGS-HK,
# LCSA-, AGC..., DAkkS variants without dashes, etc.) — real-world testing showed
# ~100% of genuine accreditation IDs failing a plain prefix check, which made the
# original SUSPICIOUS_LABORATORY flag (severity 85, alone enough to REJECT)
# functionally indistinguishable from "we haven't seen this format before."
ACCREDITATION_FRAUD_MARKERS = ("FAKE", "UNRECOGNIZED", "UNVERIFIED", "TEST-ONLY", "PLACEHOLDER")


def _normalize_std(std: str) -> str:
    """Extracts the core directive/standard identifier for resilient cross-matching,
    e.g. 'RoHS Directive 2011/65/EU (restricted substances)' -> '2011/65/EU'.
    Mirrors normalize_standard_code() in langsmith/trace_sample.py."""
    if not std:
        return ""
    std = std.upper()
    match = re.search(r"(\d{4}/\d+(?:/EU)?|\d{5}(?:-\d+)?)", std)
    if match:
        return match.group(1)
    return re.sub(r"[^A-Z0-9]", "", std)


def _standard_is_covered(required_std: str, extracted_standards: List[str]) -> bool:
    req_norm = _normalize_std(required_std)
    if not req_norm:
        return False
    return any(req_norm in _normalize_std(s) or _normalize_std(s) in req_norm for s in extracted_standards)


def match_sku(covered_part_numbers: List[str], sku_catalog: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """Deterministic (non-LLM) SKU resolution: matches extracted part/model numbers
    against each catalog entry's own `covered_part_numbers` cross-reference list.

    This is intentionally simple exact-match, not fuzzy matching — the n8n workflow's
    "Auto SKU Matcher & Rule Loader" node already has a fuzzy filename/keyword fallback
    pattern that's a reasonable next step if exact matching proves too brittle on messier
    real-world documents, but that's a deliberate scope decision, not an oversight.
    """
    if not covered_part_numbers or not sku_catalog:
        return None
    normalized_parts = {p.strip().upper() for p in covered_part_numbers if p}
    for sku_code, record in sku_catalog.items():
        catalog_parts = record.get("covered_part_numbers") or record.get("mpn_cross_reference") or []
        catalog_parts_normalized = {c.strip().upper() for c in catalog_parts}
        if normalized_parts & catalog_parts_normalized:
            return sku_code
    return None


# ==========================================
# 3. Graph Node Functions
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

    # 1. Covered part numbers — replaces the old sku_code check. A document should
    # always be able to say what it covers, so there's no "absent_appropriate" branch here.
    field_status["covered_part_numbers"] = "present" if data.get("covered_part_numbers") else "absent_expected"

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
    else:
        # Either it's a statutory limit (no measured value expected) or genuinely
        # not tested/stated — both are non-blocking for a self-declaration/threshold-only doc.
        field_status["tested_lead_ppm"] = "absent_appropriate"

    has_ambiguity = any(status in ["absent_expected", "ambiguous"] for status in field_status.values())

    return {
        "field_status": field_status,
        "needs_human_review": (has_ambiguity and state["reconciliation_attempts"] >= 2),
    }


def reconcile_node(state: AuditState) -> Dict[str, Any]:
    """Targeted re-extraction attempting to resolve absent_expected/ambiguous fields."""
    import json

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
        # Only overwrite if the reconciliation attempt actually found something —
        # an empty list/None shouldn't clobber a previously-successful partial extraction.
        if v not in (None, [], ""):
            current_data[k] = v

    return {
        "extracted": current_data,
        "reconciliation_attempts": attempts + 1,
    }


def resolve_sku_node(state: AuditState) -> Dict[str, Any]:
    """Deterministic (non-LLM) SKU resolution — runs once extraction is final, right
    before the rule engine. Uses an explicitly-provided `associated_sku` if the caller
    already knows it (e.g. selected from a dropdown in the UI, or supplied by a benchmark
    harness), otherwise attempts to match `covered_part_numbers` against the SKU catalog.
    Implements US-2.1 / AC-10 / AC-11: an unmatched SKU must be explicit, never silent.
    """
    sku_catalog = state.get("sku_catalog") or {}
    associated_sku = state.get("associated_sku")

    if associated_sku and associated_sku in sku_catalog:
        return {"associated_sku": associated_sku, "sku_match_status": "matched"}

    covered_parts = state["extracted"].get("covered_part_numbers", [])
    matched_sku = match_sku(covered_parts, sku_catalog)

    if matched_sku:
        return {"associated_sku": matched_sku, "sku_match_status": "matched"}

    return {"associated_sku": None, "sku_match_status": "unmatched"}


def rule_engine_node(state: AuditState) -> Dict[str, Any]:
    """Deterministic policy decision. This is the one place decisions get made —
    everything above this node only prepares clean, honestly-labeled evidence for it."""
    data = dict(state["extracted"])  # local copy — Check 1 may correct a mislabeled field below
    statuses = state["field_status"]
    doc_type = state["doc_type"]
    sku_catalog = state.get("sku_catalog") or {}
    associated_sku = state.get("associated_sku")
    sku_match_status = state.get("sku_match_status", "not_attempted")
    sku_record = sku_catalog.get(associated_sku) if associated_sku else None

    score = 0
    violations: List[RuleViolation] = []

    # Check 1: Lead-value / statutory-limit consistency sanity check. Zero severity —
    # this doesn't push the score, it just corrects the field and makes the correction
    # visible, so Check 5 below evaluates the real threshold check instead of skipping it.
    lead_ppm = data.get("tested_lead_ppm")
    if lead_ppm is not None and data.get("is_statutory_limit") and lead_ppm not in KNOWN_STATUTORY_THRESHOLDS:
        data["is_statutory_limit"] = False
        violations.append(
            RuleViolation(
                code="LEAD_VALUE_MISLABELED",
                severity_score=0,
                message=(
                    f"Extraction tagged {lead_ppm} ppm as a statutory limit, but RoHS thresholds "
                    f"are always 100 or 1000 ppm — treating this as a measured result instead."
                ),
            )
        )

    # Check 2: Date-order sanity check — catches likely OCR/extraction errors
    # (e.g. an expiration date a couple of days before the issue date) before they get
    # silently taken at face value by the expiration check further down.
    issue_date_str = data.get("issue_date")
    exp_date_str = data.get("expiration_date")
    if issue_date_str and exp_date_str:
        try:
            issue_dt = datetime.strptime(issue_date_str, "%Y-%m-%d")
            exp_dt = datetime.strptime(exp_date_str, "%Y-%m-%d")
            if exp_dt < issue_dt:
                score += 40
                violations.append(
                    RuleViolation(
                        code="DATE_INCONSISTENCY",
                        severity_score=40,
                        message=(
                            f"Expiration date ({exp_date_str}) is before issue date ({issue_date_str}) — "
                            f"likely an extraction/OCR error, needs manual verification against the source document."
                        ),
                    )
                )
        except ValueError:
            pass

    # Check 3: SKU match — if the catalog was supplied but nothing matched, that's a
    # real data-quality condition, not a silent pass (AC-11).
    if sku_catalog and sku_match_status == "unmatched":
        score += 50
        violations.append(
            RuleViolation(
                code="NO_SKU_MATCH",
                severity_score=50,
                message="Extracted part numbers did not match any catalog SKU — mandatory standards could not be verified",
            )
        )

    # Check 4: Mandatory standards (only evaluable once a SKU is matched — this is the
    # per-SKU logic that existed in trace_sample.py's screen_certificate())
    if sku_record:
        mandatory_stds = sku_record.get("mandatory_standards", [])
        standards_found = data.get("standards_tested", [])
        missing_standards = [s for s in mandatory_stds if not _standard_is_covered(s, standards_found)]

        for std in missing_standards:
            std_upper = std.upper()
            is_critical = any(code in std_upper for code in ("2011/65", "2014/53", "62133"))
            severity = 75 if is_critical else 65
            score += severity
            violations.append(
                RuleViolation(
                    code="MISSING_MANDATORY_STANDARD" if is_critical else "MISSING_STANDARD",
                    severity_score=severity,
                    message=f"{'CRITICAL' if is_critical else 'WARNING'}: Missing mandatory standard {std}",
                )
            )

    # Check 5: Lead PPM — threshold now comes from the matched SKU's own limit when
    # available, falling back to the global default otherwise.
    if statuses.get("tested_lead_ppm") == "present" and not data.get("is_statutory_limit"):
        lead_ppm = data.get("tested_lead_ppm", 0.0)
        max_lead = sku_record.get("max_lead_concentration_ppm", DEFAULT_LEAD_PPM_THRESHOLD) if sku_record else DEFAULT_LEAD_PPM_THRESHOLD
        if lead_ppm > max_lead:
            score += 95
            violations.append(
                RuleViolation(
                    code="LEAD_EXCESS_VIOLATION",
                    severity_score=95,
                    message=f"Measured {lead_ppm} ppm exceeds threshold {max_lead} ppm",
                )
            )

    # Check 7: Expiration Date (unchanged)
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
                            message=f"Expired on {exp_date_str}",
                        )
                    )
            except ValueError:
                pass

    # Check 4: Laboratory Accreditation Validation — two tiers, not one (see
    # ACCREDITATION_FRAUD_MARKERS comment above for why). Real accreditation IDs come
    # in many legitimate formats a static prefix list can't fully cover; treat an
    # unrecognized-but-plausible ID as "needs human verification," and reserve
    # REJECT-level severity for explicit fraud/placeholder markers.
    if doc_type == "lab_test_report":
        acc_id = data.get("accreditation_id") or ""
        acc_upper = acc_id.upper()
        if not acc_id:
            score += 70
            violations.append(
                RuleViolation(
                    code="UNACCREDITED_LABORATORY",
                    severity_score=70,
                    message="No accreditation ID present",
                )
            )
        elif any(marker in acc_upper for marker in ACCREDITATION_FRAUD_MARKERS):
            score += 85
            violations.append(
                RuleViolation(
                    code="SUSPICIOUS_LABORATORY",
                    severity_score=85,
                    message=f"ID '{acc_id}' contains an explicit fraud/placeholder marker",
                )
            )
        elif not any(acc_upper.startswith(prefix) for prefix in KNOWN_ACCREDITATION_PREFIXES):
            score += 30
            violations.append(
                RuleViolation(
                    code="UNVERIFIED_ACCREDITATION",
                    severity_score=30,
                    message=(
                        f"ID '{acc_id}' doesn't match a known accreditation-body prefix — "
                        f"format could not be auto-verified, recommend manual confirmation."
                    ),
                )
            )

    # Check 5: Obsolete or Draft Standards Validation
    standards = data.get("standards_tested", [])
    for std in standards:
        std_upper = std.upper()
        if any(obsolete in std_upper for obsolete in DEPRECATED_SAFETY_STANDARDS):
            score += 85
            violations.append(
                RuleViolation(
                    code="OBSOLETE_SAFETY_STANDARD",
                    severity_score=85,
                    message=f"Withdrawn safety standard cited: {std}",
                )
            )
        if any(obsolete in std_upper for obsolete in DEPRECATED_ROHS_STANDARDS):
            score += 75
            violations.append(
                RuleViolation(
                    code="OBSOLETE_ROHS_STANDARD",
                    severity_score=75,
                    message=f"Withdrawn RoHS standard cited: {std}",
                )
            )
        if "draft" in std.lower():
            score += 50
            violations.append(
                RuleViolation(
                    code="DRAFT_STANDARD_CITED",
                    severity_score=50,
                    message=f"Draft standard cited instead of final: {std}",
                )
            )

    # Check 6: Covered part numbers completeness 
    if statuses.get("covered_part_numbers") != "present":
        score += 55
        violations.append(
            RuleViolation(
                code="MISSING_PART_NUMBERS",
                severity_score=55,
                message="No covered part numbers extracted from the document",
            )
        )

    final_score = min(score, 100)
    decision = "REJECTED" if final_score >= 85 else ("FLAGGED" if final_score >= 50 else "APPROVED")

    audit_result = AuditResult(
        score=final_score,
        decision=decision,
        flags=violations,
        audited_at=datetime.now(timezone.utc).isoformat(),
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
                message=reason,
            )
        ],
        audited_at=datetime.now(timezone.utc).isoformat(),
    )

    return {
        "needs_human_review": True,
        "review_reason": reason,
        "audit_result": audit_result.model_dump(),
    }


# ==========================================
# 4. Conditional Edge Logic
# ==========================================

def route_after_validation(state: AuditState) -> Literal["resolve_sku", "reconcile", "flag_for_human_review"]:
    """Routes based on field resolution and bounded reconciliation retries."""
    ambiguous = any(s in ["absent_expected", "ambiguous"] for s in state["field_status"].values())

    if not ambiguous:
        return "resolve_sku"

    if state["reconciliation_attempts"] < 2:
        return "reconcile"

    return "flag_for_human_review"


# ==========================================
# 5. Graph Construction & Compilation
# ==========================================

builder = StateGraph(AuditState)

# Add Nodes
builder.add_node("extract", extract_node)
builder.add_node("classify_doc_type", classify_doc_type_node)
builder.add_node("validate_fields", validate_fields_node)
builder.add_node("reconcile", reconcile_node)
builder.add_node("resolve_sku", resolve_sku_node)
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
        "resolve_sku": "resolve_sku",
        "reconcile": "reconcile",
        "flag_for_human_review": "flag_for_human_review",
    },
)

builder.add_edge("reconcile", "validate_fields")
builder.add_edge("resolve_sku", "rule_engine")
builder.add_edge("rule_engine", END)
builder.add_edge("flag_for_human_review", END)

# Compile Executable Graph
graph = builder.compile()
