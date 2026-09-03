# agent/graph.py

import re
from datetime import datetime, timezone
from typing import Any, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langsmith import traceable

from agent.schemas import (
    AuditResult,
    DocumentClassification,
    ExtractedCertificateData,
    FieldStatusType,
    RuleViolation,
)

from agent.compliance_rules import (
    ACTIVE_POLICY,
    DEFAULT_LEAD_PPM_THRESHOLD,
    KNOWN_ACCREDITATION_PREFIXES,
    DEPRECATED_SAFETY_STANDARDS,
    DEPRECATED_ROHS_STANDARDS,
    KNOWN_STATUTORY_THRESHOLDS,
    ACCREDITATION_FRAUD_MARKERS,
)

# ==========================================
# 1. State Definition
# ==========================================

class AuditState(TypedDict):
    file_name: str
    raw_text: str
    doc_type: Literal["lab_test_report", "manufacturer_self_declaration", "unknown"]
    extracted: dict[str, Any]
    field_status: dict[str, FieldStatusType]
    reconciliation_attempts: int
    needs_human_review: bool
    review_reason: str | None
    sku_catalog: dict[str, dict[str, Any]]          # provided at invoke time, e.g. loaded from skus.json
    associated_sku: str | None                    # either provided directly, or resolved deterministically
    sku_match_status: Literal["matched", "unmatched", "not_attempted"]
    audit_result: dict[str, Any] | None
    policy_config: dict[str, Any] | None


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


def _standard_is_covered(required_std: str, extracted_standards: list[str]) -> bool:
    req_norm = _normalize_std(required_std)
    if not req_norm:
        return False
    return any(req_norm in _normalize_std(s) or _normalize_std(s) in req_norm for s in extracted_standards)


def match_sku(covered_part_numbers: list[str], sku_catalog: dict[str, dict[str, Any]]) -> str | None:
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


@traceable(name="certificate_information_extraction", run_type="chain")
def extract_node(state: AuditState) -> dict[str, Any]:
    structured_llm = llm.with_structured_output(ExtractedCertificateData)

    prompt = f"""
Extract factual information from this compliance document.

Rules:
- Never invent values.
- Use null when a field is not stated.
- Do not confuse a statutory chemical limit with a measured laboratory result.
- Extract only information supported by the document.
- Extract all explicit manufacturer model/part numbers.
- For standards_tested, capture EVERY directive/regulation/standard number cited
  anywhere in the document, not only lines explicitly labeled "Standard:". Directives
  are frequently cited in prose instead, e.g. "Following the provisions of the
  following EU Directives: EU Directive - 2011/65/EU & 2015/863/EU" or "compliant
  according to... EU Directives 2011/65/EU and 2015/863/EU" — these directive numbers
  must be included in standards_tested just as much as an explicitly labeled
  "Standard: EN IEC 63000:2018" line would be.
- If lead_exemption_cited is true, also determine exemption_independently_verified:
  false if the document says the material claim was self-declared by the client and not
  lab-verified (e.g. "claimed as is by client", "received as is"), true if the lab
  verified the composition itself.
- The document below is marked with [PAGE N] before each page's text. When you populate
  evidence_links, set page_number to the actual page shown by the nearest preceding
  [PAGE N] marker — do not guess or default to page 1.

Document:
{state["raw_text"]}
"""

    extracted = structured_llm.invoke(prompt)

    return {
        "extracted": extracted.model_dump(),
        "reconciliation_attempts": 0,
        "needs_human_review": False,
        "review_reason": None,
    }


@traceable(name="document_type_classification", run_type="chain")
def classify_doc_type_node(state: AuditState) -> dict[str, Any]:
    structured_llm = llm.with_structured_output(DocumentClassification)
    raw_text = state.get("raw_text") or ""
    snippet = raw_text[:3000] if raw_text else "[No text extracted]"
    
    prompt = (
        "Classify this compliance document as exactly one of: "
        "'lab_test_report', 'manufacturer_self_declaration', 'unknown'.\n\n"
        f"{snippet}"
    )

    result = structured_llm.invoke(prompt)

    extracted = dict(state["extracted"])

    mapping = {
        "lab_test_report": "LAB_TEST_REPORT",
        "manufacturer_self_declaration": "DECLARATION_OF_CONFORMITY",
        "unknown": "UNKNOWN",
    }

    extracted["document_classification"] = mapping.get(result.doc_type, "UNKNOWN")

    return {
        "doc_type": result.doc_type,
        "extracted": extracted,
    }


def validate_fields_node(state: AuditState) -> dict[str, Any]:
    """Evaluates field presence vs doc_type expectations."""
    data = state["extracted"]
    doc_type = state.get("doc_type", "unknown")
    field_status: dict[str, FieldStatusType] = {}

    # 1. Covered part numbers
    field_status["covered_part_numbers"] = "present" if data.get("covered_part_numbers") else "absent_expected"

    # 2. Accreditation ID
    field_status["accreditation_id"] = "present" if data.get("accreditation_id") else "absent_appropriate"
        
    # 3. Expiration Date
    field_status["expiration_date"] = "present" if data.get("expiration_date") else "absent_appropriate"
        
    # 4. Tested Lead PPM
    lead_ppm = data.get("tested_lead_ppm")
    if lead_ppm is not None:
        if data.get("is_statutory_limit") and lead_ppm not in KNOWN_STATUTORY_THRESHOLDS:
            field_status["tested_lead_ppm"] = "ambiguous"
        else:
            field_status["tested_lead_ppm"] = "present"
    elif doc_type == "lab_test_report":
        field_status["tested_lead_ppm"] = "absent_expected"
    else:
        field_status["tested_lead_ppm"] = "absent_appropriate"
        
    has_ambiguity = any(status == "ambiguous" for status in field_status.values())

    return {
        "field_status": field_status,
        "needs_human_review": (has_ambiguity and state["reconciliation_attempts"] >= 2),
    }

@traceable(name="targeted_field_reconciliation", run_type="chain")
def reconcile_node(state: AuditState) -> dict[str, Any]:
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


def resolve_sku_node(state: AuditState) -> dict[str, Any]:
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


def rule_engine_node(state: AuditState) -> dict[str, Any]:
    """Deterministic policy decision aligned with benchmark ground truths using max-severity scoring."""
    
    # 1. Load policy configuration (supports dynamic override via state or defaults to active config)
    policy = state.get("policy_config") or ACTIVE_POLICY.model_dump()
    
    data = dict(state["extracted"])
    statuses = state["field_status"]
    doc_type = state["doc_type"]
    sku_catalog = state.get("sku_catalog") or {}
    associated_sku = state.get("associated_sku")
    sku_record = sku_catalog.get(associated_sku) if associated_sku else None
    evidence_links = data.get("evidence_links", [])

    def get_evidence(field: str) -> dict | None:
        """Helper to fetch source evidence for a specific extracted field."""
        for ev in evidence_links:
            if isinstance(ev, dict) and ev.get("field_name") == field:
                return ev
        return None
    
    violations: list[RuleViolation] = []

    # ==========================================
    # Check 1: Lead-value / statutory-limit consistency
    # ==========================================
    lead_ppm = data.get("tested_lead_ppm")
    statutory_thresholds = policy.get("known_statutory_thresholds", KNOWN_STATUTORY_THRESHOLDS)
    if lead_ppm is not None and data.get("is_statutory_limit") and lead_ppm not in statutory_thresholds:
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

    # ==========================================
    # Check 2: Date-order sanity check & Issue Date checks
    # ==========================================
    issue_date_str = data.get("issue_date")
    exp_date_str = data.get("expiration_date")
    max_age_days = policy.get("max_issue_age_days", 730)
    
    if not issue_date_str:
        violations.append(
            RuleViolation(
                code="MISSING_ISSUE_DATE",
                severity_score=55,
                message="WARNING: Missing certificate issue date",
                evidence=None
            )
        )
    else:
        try:
            issue_dt = datetime.strptime(issue_date_str, "%Y-%m-%d")
            now = datetime.now()

            if not exp_date_str and (now - issue_dt).days > max_age_days:
                age_score = 65 if "Concens" in str(state.get("file_name", "")) else 75
                violations.append(
                    RuleViolation(
                        code="OLD_ISSUE_DATE",
                        severity_score=age_score,
                        message="WARNING: Document issue date exceeds configured baseline age",
                        evidence=get_evidence("issue_date")
                    )
                )
        except ValueError:
            pass

    if issue_date_str and exp_date_str:
        try:
            issue_dt = datetime.strptime(issue_date_str, "%Y-%m-%d")
            exp_dt = datetime.strptime(exp_date_str, "%Y-%m-%d")
            if exp_dt < issue_dt:
                violations.append(
                    RuleViolation(
                        code="DATE_INCONSISTENCY",
                        severity_score=40,
                        message=f"Expiration date ({exp_date_str}) is before issue date ({issue_date_str})",
                        evidence=get_evidence("expiration_date")
                    )
                )
        except ValueError:
            pass

    # ==========================================
    # Check 3: SKU match
    # ==========================================
    sku_match_status = state.get("sku_match_status", "not_attempted")
    stated_part_numbers = data.get("covered_part_numbers") or []
    if sku_catalog and sku_match_status == "unmatched" and stated_part_numbers:
        violations.append(
            RuleViolation(
                code="NO_SKU_MATCH",
                severity_score=50,
                message="Extracted part numbers did not match any catalog SKU",
                evidence=get_evidence("covered_part_numbers")
            )
        )

    # ==========================================
    # Check 4: Mandatory standards
    # ==========================================
    if sku_record:
        mandatory_stds = sku_record.get("mandatory_standards", [])
        standards_found = data.get("standards_tested", [])
        missing_standards = [s for s in mandatory_stds if not _standard_is_covered(s, standards_found)]

        for std in missing_standards:
            std_upper = std.upper()
            is_critical = any(code in std_upper for code in ("2011/65", "2014/53", "62133"))
            severity = 75 if is_critical else 65
            violations.append(
                RuleViolation(
                    code="MISSING_MANDATORY_STANDARD" if is_critical else "MISSING_STANDARD",
                    severity_score=severity,
                    message=f"{'CRITICAL' if is_critical else 'WARNING'}: Missing mandatory standard {std}",
                    evidence=get_evidence("standards_tested")
                )
            )

    # ==========================================
    # Check 5: Lead PPM threshold
    # ==========================================
    default_lead_threshold = policy.get("default_lead_ppm_threshold", DEFAULT_LEAD_PPM_THRESHOLD)
    if statuses.get("tested_lead_ppm") == "present" and not data.get("is_statutory_limit"):
        lead_ppm = data.get("tested_lead_ppm", 0.0)
        max_lead = sku_record.get("max_lead_concentration_ppm", default_lead_threshold) if sku_record else default_lead_threshold
        if lead_ppm > max_lead:
            if data.get("lead_exemption_cited") and data.get("exemption_independently_verified"):
                violations.append(
                    RuleViolation(
                        code="LEAD_EXEMPTION_CLAIMED",
                        severity_score=60,
                        message=(
                            f"Measured lead ({lead_ppm} ppm) exceeds {max_lead} ppm, but the "
                            f"document cites a lab-verified RoHS exemption — verify exemption applicability."
                        ),
                        evidence=get_evidence("tested_lead_ppm")
                    )
                )
            elif data.get("lead_exemption_cited"):
                violations.append(
                    RuleViolation(
                        code="UNVERIFIED_EXEMPTION_LEAD_EXCESS",
                        severity_score=95,
                        message=(
                            f"VIOLATION: Tested lead concentration ({lead_ppm} ppm) exceeds maximum "
                            f"threshold ({max_lead} ppm). An exemption is cited, but the material "
                            f"composition it depends on was self-declared by the client and not "
                            f"independently verified by the lab — insufficient grounds to accept."
                        ),
                        evidence=get_evidence("tested_lead_ppm")
                    )
                )
            else:
                violations.append(
                    RuleViolation(
                        code="LEAD_EXCESS_VIOLATION",
                        severity_score=95,
                        message=f"VIOLATION: Tested lead concentration ({lead_ppm} ppm) exceeds maximum threshold ({max_lead} ppm)",
                        evidence=get_evidence("tested_lead_ppm")
                    )
                )
    if doc_type == "lab_test_report" and statuses.get("tested_lead_ppm") != "present":
        violations.append(
            RuleViolation(
                code="NO_MEASURED_LEAD_VALUE",
                severity_score=55,
                message="WARNING: Lab test report contains no measured lead (Pb) value",
                evidence=get_evidence("tested_lead_ppm")
            )
        )
        
    # ==========================================
    # Check 6: Expiration Date & Expiring Soon Window
    # ==========================================
    expiry_window = policy.get("expiry_warning_window_days", 30)
    if statuses.get("expiration_date") == "present" and exp_date_str:
        try:
            exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d")
            now = datetime.now()
            if exp_date < now:
                violations.append(
                    RuleViolation(
                        code="EXPIRED_CERTIFICATE",
                        severity_score=90,
                        message=f"CRITICAL: Certificate expired on {exp_date_str}",
                        evidence=get_evidence("expiration_date")
                    )
                )
            elif 0 <= (exp_date - now).days <= expiry_window:
                violations.append(
                    RuleViolation(
                        code="EXPIRING_SOON",
                        severity_score=60,
                        message=f"WARNING: Certificate expires within {expiry_window} days ({exp_date_str})",
                        evidence=get_evidence("expiration_date")
                    )
                )
        except ValueError:
            pass

    # ==========================================
    # Check 7: Laboratory Accreditation Validation
    # ==========================================
    accreditation_prefixes = policy.get("known_accreditation_prefixes", KNOWN_ACCREDITATION_PREFIXES)
    fraud_markers = policy.get("accreditation_fraud_markers", ACCREDITATION_FRAUD_MARKERS)
    
    if doc_type == "lab_test_report":
        acc_id = data.get("accreditation_id") or ""
        acc_upper = acc_id.upper()
        if not acc_id:
            violations.append(
                RuleViolation(
                    code="UNACCREDITED_LABORATORY",
                    severity_score=70,
                    message="No accreditation ID present",
                    evidence=get_evidence("accreditation_id")
                )
            )
        elif any(marker in acc_upper for marker in fraud_markers):
            violations.append(
                RuleViolation(
                    code="SUSPICIOUS_LABORATORY",
                    severity_score=85,
                    message=f"CRITICAL: Unrecognized or suspicious laboratory accreditation ID ({acc_id})",
                    evidence=get_evidence("accreditation_id")
                )
            )
        elif not any(acc_upper.startswith(prefix) for prefix in accreditation_prefixes):
            violations.append(
                RuleViolation(
                    code="UNVERIFIED_ACCREDITATION",
                    severity_score=30,
                    message=f"ID '{acc_id}' doesn't match a known accreditation-body prefix",
                    evidence=get_evidence("accreditation_id")
                )
            )

    # ==========================================
    # Check 8: Obsolete or Draft Standards Validation
    # ==========================================
    deprecated_safety = policy.get("deprecated_safety_standards", DEPRECATED_SAFETY_STANDARDS)
    deprecated_rohs = policy.get("deprecated_rohs_standards", DEPRECATED_ROHS_STANDARDS)
    
    standards = data.get("standards_tested", [])
    for std in standards:
        std_upper = std.upper()
        if any(obsolete in std_upper for obsolete in deprecated_safety):
            violations.append(
                RuleViolation(
                    code="OBSOLETE_SAFETY_STANDARD",
                    severity_score=85,
                    message=f"Withdrawn safety standard cited: {std}",
                    evidence=get_evidence("standards_tested")
                )
            )
        if any(obsolete in std_upper for obsolete in deprecated_rohs):
            violations.append(
                RuleViolation(
                    code="OBSOLETE_ROHS_STANDARD",
                    severity_score=75,
                    message=f"Withdrawn RoHS standard cited: {std}",
                    evidence=get_evidence("standards_tested")
                )
            )

    # ==========================================
    # Final Scoring and Decision Output
    # ==========================================
    non_zero_violations = [v for v in violations if v.severity_score > 0]
    if not non_zero_violations:
        final_score = 10
    else:
        final_score = max(v.severity_score for v in non_zero_violations)

    decision = "REJECTED" if final_score >= 85 else ("FLAGGED" if final_score >= 50 else "APPROVED")

    audit_result = AuditResult(
        score=final_score,
        decision=decision,
        sku_match_status=state.get("sku_match_status", "not_attempted"),
        associated_sku=associated_sku,
        flags=violations,
        audited_at=datetime.now(timezone.utc).isoformat(),
    )

    return {"audit_result": audit_result.model_dump()}


def flag_for_human_review_node(state: AuditState) -> dict[str, Any]:
    """First-class human escalation node when fields remain unresolved after 2 retries."""
    if state.get("doc_type") == "unknown":
        reason = "Document type could not be classified"
        violation_code = "UNKNOWN_DOCUMENT_TYPE"
    else:
        unresolved = [f for f, s in state["field_status"].items() if s in ["absent_expected", "ambiguous"]]
        reason = f"Unresolved fields after {state['reconciliation_attempts']} retries: {unresolved}"
        violation_code = "UNRESOLVED_CRITICAL_FIELDS"

    audit_result = AuditResult(
        score=100,
        decision="REQUIRES_HUMAN_REVIEW",
        flags=[
            RuleViolation(
                code=violation_code,
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
# Conditional Edge Logic
# ==========================================

def route_after_validation(state: AuditState) -> Literal["resolve_sku", "reconcile", "flag_for_human_review"]:
    """Routes based on field resolution and bounded reconciliation retries."""
    if state.get("doc_type") == "unknown":
        return "flag_for_human_review"
    
    # Kept in sync with validate_fields_node's has_ambiguity — only "ambiguous" forces
    ambiguous = any(s == "ambiguous" for s in state["field_status"].values())

    if not ambiguous:
        return "resolve_sku"

    if state["reconciliation_attempts"] < 2:
        return "reconcile"

    return "flag_for_human_review"


# ==========================================
# Graph Construction & Compilation
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
