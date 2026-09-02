from agent.graph import (
    classify_doc_type_node,
    flag_for_human_review_node,
    reconcile_node,
    validate_fields_node,
)
from agent.schemas import DocumentClassification, ExtractedCertificateData


class FakeStructuredLLM:
    def __init__(self, result):
        self.result = result

    def invoke(self, prompt):
        return self.result


class FakeLLM:
    def __init__(self, result):
        self.result = result

    def with_structured_output(self, schema):
        return FakeStructuredLLM(self.result)


def test_validate_fields_marks_present_fields(base_state):
    result = validate_fields_node(base_state)

    assert result["field_status"]["covered_part_numbers"] == "present"
    assert result["field_status"]["accreditation_id"] == "present"
    assert result["field_status"]["expiration_date"] == "present"
    assert result["field_status"]["tested_lead_ppm"] == "present"
    assert result["needs_human_review"] is False


def test_validate_fields_requires_lead_for_lab_reports(base_state):
    base_state["extracted"]["tested_lead_ppm"] = None

    result = validate_fields_node(base_state)

    assert result["field_status"]["tested_lead_ppm"] == "absent_expected"


def test_validate_fields_does_not_require_lead_for_declarations(base_state):
    base_state["doc_type"] = "manufacturer_self_declaration"
    base_state["extracted"]["tested_lead_ppm"] = None

    result = validate_fields_node(base_state)

    assert result["field_status"]["tested_lead_ppm"] == "absent_appropriate"


def test_validate_fields_marks_missing_parts_as_expected(base_state):
    base_state["extracted"]["covered_part_numbers"] = []

    result = validate_fields_node(base_state)

    assert result["field_status"]["covered_part_numbers"] == "absent_expected"


def test_classify_doc_type_maps_lab_report(monkeypatch, base_state):
    import agent.graph as graph_module

    monkeypatch.setattr(
        graph_module,
        "llm",
        FakeLLM(
            DocumentClassification(
                doc_type="lab_test_report",
                confidence=0.99,
            )
        ),
    )

    result = classify_doc_type_node(base_state)

    assert result["doc_type"] == "lab_test_report"
    assert result["extracted"]["document_classification"] == "LAB_TEST_REPORT"


def test_classify_doc_type_maps_declaration(monkeypatch, base_state):
    import agent.graph as graph_module

    monkeypatch.setattr(
        graph_module,
        "llm",
        FakeLLM(
            DocumentClassification(
                doc_type="manufacturer_self_declaration",
                confidence=0.99,
            )
        ),
    )

    result = classify_doc_type_node(base_state)

    assert result["doc_type"] == "manufacturer_self_declaration"
    assert result["extracted"]["document_classification"] == (
        "DECLARATION_OF_CONFORMITY"
    )


def test_classify_doc_type_maps_unknown(monkeypatch, base_state):
    import agent.graph as graph_module

    monkeypatch.setattr(
        graph_module,
        "llm",
        FakeLLM(
            DocumentClassification(
                doc_type="unknown",
                confidence=0.2,
            )
        ),
    )

    result = classify_doc_type_node(base_state)

    assert result["doc_type"] == "unknown"
    assert result["extracted"]["document_classification"] == "UNKNOWN"


def test_reconcile_does_not_overwrite_existing_values(monkeypatch, base_state):
    import agent.graph as graph_module

    base_state["field_status"]["tested_lead_ppm"] = "absent_expected"

    reconciled = ExtractedCertificateData(
        tested_lead_ppm=None,
        covered_part_numbers=[],
        supplier_name="Updated Supplier",
    )

    monkeypatch.setattr(graph_module, "llm", FakeLLM(reconciled))

    result = reconcile_node(base_state)

    assert result["reconciliation_attempts"] == 1
    assert result["extracted"]["tested_lead_ppm"] == 100.0
    assert result["extracted"]["supplier_name"] == "Updated Supplier"


def test_reconcile_increments_attempt_count(monkeypatch, base_state):
    import agent.graph as graph_module

    base_state["reconciliation_attempts"] = 1
    base_state["field_status"]["tested_lead_ppm"] = "absent_expected"

    monkeypatch.setattr(
        graph_module,
        "llm",
        FakeLLM(ExtractedCertificateData(tested_lead_ppm=250)),
    )

    result = reconcile_node(base_state)

    assert result["reconciliation_attempts"] == 2
    assert result["extracted"]["tested_lead_ppm"] == 250


def test_human_review_node_creates_review_result(base_state):
    base_state["reconciliation_attempts"] = 2
    base_state["field_status"]["tested_lead_ppm"] = "absent_expected"

    result = flag_for_human_review_node(base_state)

    assert result["needs_human_review"] is True
    assert result["audit_result"]["decision"] == "REQUIRES_HUMAN_REVIEW"
    assert result["audit_result"]["score"] == 100
    assert "tested_lead_ppm" in result["review_reason"]
