from datetime import datetime, timedelta

from agent.graph import (
    resolve_sku_node,
    rule_engine_node,
)


def violation_codes(result):
    return {flag["code"] for flag in result["audit_result"]["flags"]}


def test_resolve_sku_matches_extracted_part_number(base_state):
    result = resolve_sku_node(base_state)

    assert result["associated_sku"] == "SKU-001"
    assert result["sku_match_status"] == "matched"


def test_resolve_sku_preserves_valid_explicit_sku(base_state):
    base_state["associated_sku"] = "SKU-002"

    result = resolve_sku_node(base_state)

    assert result["associated_sku"] == "SKU-002"
    assert result["sku_match_status"] == "matched"


def test_resolve_sku_does_not_preserve_unknown_explicit_sku(base_state):
    base_state["associated_sku"] = "SKU-NOT-FOUND"

    result = resolve_sku_node(base_state)

    assert result["associated_sku"] == "SKU-001"
    assert result["sku_match_status"] == "matched"


def test_resolve_sku_marks_unmatched_documents(base_state):
    base_state["extracted"]["covered_part_numbers"] = ["UNKNOWN-MODEL"]

    result = resolve_sku_node(base_state)

    assert result["associated_sku"] is None
    assert result["sku_match_status"] == "unmatched"


def test_clean_document_is_approved(base_state):
    base_state["associated_sku"] = "SKU-001"
    base_state["sku_match_status"] = "matched"

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "APPROVED"
    assert result["audit_result"]["score"] == 10
    assert result["audit_result"]["flags"] == []


def test_expired_certificate_is_rejected(base_state):
    base_state["extracted"]["expiration_date"] = "2020-01-01"
    base_state["associated_sku"] = "SKU-001"
    base_state["sku_match_status"] = "matched"

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "REJECTED"
    assert result["audit_result"]["score"] == 90
    assert "EXPIRED_CERTIFICATE" in violation_codes(result)


def test_excess_lead_is_rejected(base_state):
    base_state["extracted"]["tested_lead_ppm"] = 1500
    base_state["associated_sku"] = "SKU-001"
    base_state["sku_match_status"] = "matched"

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "REJECTED"
    assert result["audit_result"]["score"] == 95
    assert "LEAD_EXCESS_VIOLATION" in violation_codes(result)


def test_excess_lead_with_exemption_requires_review_flag(base_state):
    base_state["extracted"]["tested_lead_ppm"] = 1500
    base_state["extracted"]["lead_exemption_cited"] = True
    base_state["associated_sku"] = "SKU-001"
    base_state["sku_match_status"] = "matched"

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "FLAGGED"
    assert result["audit_result"]["score"] == 60
    assert "LEAD_EXEMPTION_CLAIMED" in violation_codes(result)


def test_missing_critical_standard_is_flagged(base_state):
    base_state["extracted"]["standards_tested"] = [
        "RoHS Directive 2011/65/EU"
    ]
    base_state["associated_sku"] = "SKU-001"
    base_state["sku_match_status"] = "matched"

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "FLAGGED"
    assert result["audit_result"]["score"] == 65
    assert "MISSING_STANDARD" in violation_codes(result)


def test_missing_noncritical_standard_has_lower_severity(base_state):
    base_state["sku_catalog"]["SKU-001"]["mandatory_standards"] = [
        "EN 55032"
    ]
    base_state["extracted"]["standards_tested"] = []
    base_state["associated_sku"] = "SKU-001"
    base_state["sku_match_status"] = "matched"

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "FLAGGED"
    assert result["audit_result"]["score"] == 65
    assert "MISSING_STANDARD" in violation_codes(result)


def test_unmatched_sku_is_flagged(base_state):
    base_state["sku_match_status"] = "unmatched"
    base_state["associated_sku"] = None

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "FLAGGED"
    assert result["audit_result"]["score"] == 50
    assert "NO_SKU_MATCH" in violation_codes(result)


def test_missing_issue_date_is_flagged(base_state):
    base_state["extracted"]["issue_date"] = None

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "FLAGGED"
    assert "MISSING_ISSUE_DATE" in violation_codes(result)


def test_invalid_issue_date_is_not_crashing(base_state):
    base_state["extracted"]["issue_date"] = "invalid-date"

    result = rule_engine_node(base_state)

    assert "MISSING_ISSUE_DATE" not in violation_codes(result)


def test_date_inconsistency_is_flagged(base_state):
    base_state["extracted"]["issue_date"] = "2026-06-01"
    base_state["extracted"]["expiration_date"] = "2026-05-01"

    result = rule_engine_node(base_state)

    assert "DATE_INCONSISTENCY" in violation_codes(result)


def test_missing_measured_lead_for_lab_report_is_flagged(base_state):
    base_state["extracted"]["tested_lead_ppm"] = None
    base_state["field_status"]["tested_lead_ppm"] = "absent_expected"

    result = rule_engine_node(base_state)

    assert "NO_MEASURED_LEAD_VALUE" in violation_codes(result)


def test_expiring_certificate_is_flagged(base_state):
    soon = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    base_state["extracted"]["expiration_date"] = soon

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "FLAGGED"
    assert result["audit_result"]["score"] == 60
    assert "EXPIRING_SOON" in violation_codes(result)


def test_missing_lab_accreditation_is_flagged(base_state):
    base_state["extracted"]["accreditation_id"] = None

    result = rule_engine_node(base_state)

    assert "UNACCREDITED_LABORATORY" in violation_codes(result)


def test_suspicious_lab_is_rejected(base_state):
    base_state["extracted"]["accreditation_id"] = "FAKE-ACC-000"

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "REJECTED"
    assert result["audit_result"]["score"] == 85
    assert "SUSPICIOUS_LABORATORY" in violation_codes(result)


def test_unknown_accreditation_prefix_is_unverified_not_rejected(base_state):
    base_state["extracted"]["accreditation_id"] = "SGS-HK-123"

    result = rule_engine_node(base_state)

    assert "UNVERIFIED_ACCREDITATION" in violation_codes(result)
    assert result["audit_result"]["decision"] == "APPROVED"
    assert result["audit_result"]["score"] == 30


def test_deprecated_safety_standard_is_rejected(base_state):
    base_state["extracted"]["standards_tested"].append("EN 60950")

    result = rule_engine_node(base_state)

    assert result["audit_result"]["decision"] == "REJECTED"
    assert "OBSOLETE_SAFETY_STANDARD" in violation_codes(result)


def test_deprecated_rohs_standard_is_flagged(base_state):
    base_state["extracted"]["standards_tested"].append("EN 50581")

    result = rule_engine_node(base_state)

    assert "OBSOLETE_ROHS_STANDARD" in violation_codes(result)
    assert result["audit_result"]["score"] == 75


def test_mislabeled_statutory_lead_value_is_corrected(base_state):
    base_state["extracted"]["tested_lead_ppm"] = 23800
    base_state["extracted"]["is_statutory_limit"] = True

    result = rule_engine_node(base_state)

    assert "LEAD_VALUE_MISLABELED" in violation_codes(result)
    assert "LEAD_EXCESS_VIOLATION" in violation_codes(result)
    assert result["audit_result"]["decision"] == "REJECTED"
    assert result["audit_result"]["score"] == 95
