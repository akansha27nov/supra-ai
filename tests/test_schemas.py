import pytest
from pydantic import ValidationError

from agent.schemas import (
    AuditResult,
    DocumentClassification,
    ExtractedCertificateData,
    RuleViolation,
)


def test_document_classification_accepts_valid_values():
    result = DocumentClassification(
        doc_type="lab_test_report",
        confidence=0.95,
    )

    assert result.doc_type == "lab_test_report"
    assert result.confidence == 0.95


@pytest.mark.parametrize(
    "doc_type",
    ["manufacturer_self_declaration", "unknown"],
)
def test_document_classification_accepts_all_document_types(doc_type):
    result = DocumentClassification(doc_type=doc_type)
    assert result.doc_type == doc_type


def test_document_classification_rejects_invalid_type():
    with pytest.raises(ValidationError):
        DocumentClassification(doc_type="random_document")


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_document_classification_rejects_invalid_confidence(confidence):
    with pytest.raises(ValidationError):
        DocumentClassification(
            doc_type="unknown",
            confidence=confidence,
        )


def test_extracted_certificate_data_sanitizes_empty_dates():
    result = ExtractedCertificateData(
        issue_date="",
        expiration_date="not stated",
    )

    assert result.issue_date is None
    assert result.expiration_date is None


@pytest.mark.parametrize("value", ["n/a", "none", "null", "unknown", "not applicable"])
def test_extracted_certificate_data_sanitizes_missing_date_values(value):
    result = ExtractedCertificateData(issue_date=value)
    assert result.issue_date is None


def test_extracted_certificate_data_converts_single_part_number_to_list():
    result = ExtractedCertificateData(covered_part_numbers="MODEL-001")
    assert result.covered_part_numbers == ["MODEL-001"]


def test_extracted_certificate_data_defaults_lists():
    result = ExtractedCertificateData()

    assert result.covered_part_numbers == []
    assert result.standards_tested == []
    assert result.document_classification == "UNKNOWN"


def test_extracted_certificate_data_accepts_valid_lead_value():
    result = ExtractedCertificateData(tested_lead_ppm=1450)
    assert result.tested_lead_ppm == 1450


def test_rule_violation_validates_severity_range():
    result = RuleViolation(
        code="TEST",
        severity_score=50,
        message="Test violation",
    )

    assert result.severity_score == 50


@pytest.mark.parametrize("score", [-1, 101])
def test_rule_violation_rejects_invalid_severity(score):
    with pytest.raises(ValidationError):
        RuleViolation(
            code="TEST",
            severity_score=score,
            message="Test violation",
        )


def test_audit_result_defaults_flags():
    result = AuditResult(
        score=10,
        decision="APPROVED",
    )

    assert result.flags == []
    assert result.score == 10
    assert result.decision == "APPROVED"


@pytest.mark.parametrize(
    "decision",
    ["APPROVED", "FLAGGED", "REJECTED", "REQUIRES_HUMAN_REVIEW"],
)
def test_audit_result_accepts_all_decisions(decision):
    result = AuditResult(score=10, decision=decision)
    assert result.decision == decision


def test_audit_result_rejects_invalid_score():
    with pytest.raises(ValidationError):
        AuditResult(score=101, decision="APPROVED")
