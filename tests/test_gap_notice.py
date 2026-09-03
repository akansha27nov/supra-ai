import pytest
from pydantic import ValidationError

from agent.gap_notice import create_gap_notice_record
from agent.schemas import GapNoticeEvidenceEntry, GapNoticeStatus


def test_create_gap_notice_record_uses_structured_evidence_detail():
    """evidence must come from evidence_detail (the rule engine's own
    RuleViolation.evidence), not the LLM's flat `evidence: list[str]`."""
    structured_notice = {
        "failed_rules": ["OLD_ISSUE_DATE"],
        "evidence": ["the certificate is dated 01.06.2020, which is over 2 years old"],
        "corrective_action": "Provide an updated certificate",
        "email_draft": "Dear Supplier, ...",
        "evidence_detail": [
            {"rule_code": "OLD_ISSUE_DATE", "exact_quote": "01.06.2020", "page_number": 1, "section": "date"},
        ],
    }

    record = create_gap_notice_record("audit-1", "Test Supplier", structured_notice)

    assert record["status"] == GapNoticeStatus.DRAFT
    assert len(record["evidence"]) == 1
    entry = record["evidence"][0]
    assert entry["rule_code"] == "OLD_ISSUE_DATE"
    assert entry["exact_quote"] == "01.06.2020"
    assert entry["page_number"] == 1
    assert entry["section"] == "date"


def test_create_gap_notice_record_defaults_to_empty_evidence_without_detail():
    """Backward compat: a caller (test, script) that doesn't supply
    evidence_detail should get an empty list, not a KeyError or the old
    flat-string evidence."""
    structured_notice = {
        "failed_rules": ["NO_SKU_MATCH"],
        "corrective_action": None,
        "email_draft": "Dear Supplier, ...",
    }

    record = create_gap_notice_record("audit-2", "Test Supplier", structured_notice)

    assert record["evidence"] == []


def test_create_gap_notice_record_handles_evidence_with_no_quote():
    """A violation with no SourceEvidence (evidence=None on the RuleViolation)
    should still produce a structured entry keyed by rule_code, just with
    null quote/page/section -- not be silently dropped."""
    structured_notice = {
        "failed_rules": ["NO_SKU_MATCH"],
        "corrective_action": None,
        "email_draft": "Dear Supplier, ...",
        "evidence_detail": [
            {"rule_code": "NO_SKU_MATCH", "exact_quote": None, "page_number": None, "section": None},
        ],
    }

    record = create_gap_notice_record("audit-3", "Test Supplier", structured_notice)

    assert len(record["evidence"]) == 1
    assert record["evidence"][0]["rule_code"] == "NO_SKU_MATCH"
    assert record["evidence"][0]["exact_quote"] is None


def test_gap_notice_evidence_entry_requires_rule_code():
    with pytest.raises(ValidationError):
        GapNoticeEvidenceEntry(exact_quote="some text")
