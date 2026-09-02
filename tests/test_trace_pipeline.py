import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
TRACE_SAMPLE_PATH = ROOT / "langsmith" / "trace_sample.py"

spec = importlib.util.spec_from_file_location(
    "local_trace_sample",
    TRACE_SAMPLE_PATH,
)

if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load {TRACE_SAMPLE_PATH}")

trace_sample = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace_sample)

extract_certificate_data = trace_sample.extract_certificate_data
extract_pdf_text = trace_sample.extract_pdf_text
is_standard_present = trace_sample.is_standard_present
load_skus = trace_sample.load_skus
normalize_standard_code = trace_sample.normalize_standard_code
screen_certificate = trace_sample.screen_certificate


def test_normalize_standard_code_extracts_directive_number():
    assert normalize_standard_code(
        "RoHS Directive 2011/65/EU (restricted substances)"
    ) == "2011/65/EU"


def test_normalize_standard_code_removes_punctuation():
    assert normalize_standard_code("EN 62368-1:2020") == "62368-1"


def test_normalize_standard_code_handles_empty_values():
    assert normalize_standard_code("") == ""
    assert normalize_standard_code(None) == ""


def test_is_standard_present_matches_equivalent_formats():
    assert is_standard_present(
        "RoHS Directive 2011/65/EU",
        ["2011/65/EU"],
    )


def test_is_standard_present_returns_false_for_missing_standard():
    assert not is_standard_present(
        "RED Directive 2014/53/EU",
        ["RoHS Directive 2011/65/EU"],
    )


def test_load_skus_supports_list_format(tmp_path):
    path = tmp_path / "skus.json"
    path.write_text(
        json.dumps(
            [
                {
                    "sku": "SKU-001",
                    "covered_part_numbers": ["MODEL-001"],
                }
            ]
        ),
        encoding="utf-8",
    )

    result = load_skus(path)

    assert result == {
        "SKU-001": {
            "sku": "SKU-001",
            "covered_part_numbers": ["MODEL-001"],
        }
    }


def test_load_skus_supports_dict_format(tmp_path):
    path = tmp_path / "skus.json"
    path.write_text(
        json.dumps(
            {
                "SKU-001": {
                    "covered_part_numbers": ["MODEL-001"],
                }
            }
        ),
        encoding="utf-8",
    )

    result = load_skus(path)

    assert result["SKU-001"]["covered_part_numbers"] == ["MODEL-001"]


def test_load_skus_returns_empty_dict_for_missing_file(tmp_path):
    result = load_skus(tmp_path / "missing.json")
    assert result == {}


def test_extract_certificate_data_parses_plain_json(monkeypatch):
    class FakeMessage:
        content = json.dumps(
            {
                "document_classification": "LAB_TEST_REPORT",
                "certificate_id": "CERT-001",
                "covered_part_numbers": ["MODEL-001"],
            }
        )

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        chat = type("Chat", (), {})()
        chat.completions = FakeCompletions()

    monkeypatch.setattr(trace_sample, "client", FakeClient())

    result = extract_certificate_data("certificate text")

    assert result["certificate_id"] == "CERT-001"
    assert result["covered_part_numbers"] == ["MODEL-001"]


def test_extract_certificate_data_strips_markdown_json(monkeypatch):
    class FakeMessage:
        content = '```json\n{"certificate_id": "CERT-002"}\n```'

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        chat = type("Chat", (), {})()
        chat.completions = FakeCompletions()

    monkeypatch.setattr(trace_sample, "client", FakeClient())

    result = extract_certificate_data("certificate text")

    assert result["certificate_id"] == "CERT-002"


def test_extract_certificate_data_returns_safe_fallback_for_invalid_json(
    monkeypatch,
):
    class FakeMessage:
        content = "not valid json"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        chat = type("Chat", (), {})()
        chat.completions = FakeCompletions()

    monkeypatch.setattr(trace_sample, "client", FakeClient())

    result = extract_certificate_data("certificate text")

    assert result["certificate_id"] is None
    assert result["covered_part_numbers"] == []
    assert result["chemical_data"]["is_statutory_limit"] is True


def test_screen_certificate_passes_clean_document():
    extracted = {
        "document_classification": "LAB_TEST_REPORT",
        "issue_date": "2026-01-01",
        "expiration_date": "2028-01-01",
        "covered_part_numbers": ["MODEL-001"],
        "issuing_lab": "Example Lab",
        "lab_accreditation_id": "CNAS-L0001",
        "standards_found": [
            "RoHS Directive 2011/65/EU",
            "EN 62368-1:2020",
        ],
        "chemical_data": {
            "tested_lead_ppm": 100,
            "is_statutory_limit": False,
        },
    }

    catalog = {
        "SKU-001": {
            "mandatory_standards": [
                "RoHS Directive 2011/65/EU",
                "EN 62368-1:2020",
            ],
            "max_lead_concentration_ppm": 1000,
        }
    }

    result = screen_certificate(
        extracted,
        "SKU-001",
        catalog,
        ref_date_str="2026-08-31",
    )

    assert result["status"] == "PASS"
    assert result["screening_priority_score"] == 10
    assert result["flagged_issues"] == []


def test_screen_certificate_rejects_excess_lead():
    extracted = {
        "document_classification": "LAB_TEST_REPORT",
        "issue_date": "2026-01-01",
        "expiration_date": "2028-01-01",
        "covered_part_numbers": ["MODEL-001"],
        "issuing_lab": "Example Lab",
        "lab_accreditation_id": "CNAS-L0001",
        "standards_found": [],
        "chemical_data": {
            "tested_lead_ppm": 1500,
            "is_statutory_limit": False,
        },
    }

    catalog = {
        "SKU-001": {
            "mandatory_standards": [],
            "max_lead_concentration_ppm": 1000,
        }
    }

    result = screen_certificate(
        extracted,
        "SKU-001",
        catalog,
        ref_date_str="2026-08-31",
    )

    assert result["status"] == "REJECTED"
    assert result["screening_priority_score"] == 95
    assert any("Measured lead" in issue for issue in result["flagged_issues"])


def test_screen_certificate_rejects_expired_document():
    extracted = {
        "document_classification": "DECLARATION_OF_CONFORMITY",
        "issue_date": "2024-01-01",
        "expiration_date": "2025-01-01",
        "covered_part_numbers": ["MODEL-001"],
        "issuing_lab": None,
        "lab_accreditation_id": None,
        "standards_found": [],
        "chemical_data": {
            "tested_lead_ppm": None,
            "is_statutory_limit": True,
        },
    }

    catalog = {
        "SKU-001": {
            "mandatory_standards": [],
            "max_lead_concentration_ppm": 1000,
        }
    }

    result = screen_certificate(
        extracted,
        "SKU-001",
        catalog,
        ref_date_str="2026-08-31",
    )

    assert result["status"] == "REJECTED"
    assert result["screening_priority_score"] == 90


def test_extract_pdf_text_reads_all_pages(tmp_path):
    pytest.importorskip("reportlab")

    from reportlab.pdfgen import canvas

    pdf_path = tmp_path / "sample.pdf"
    pdf = canvas.Canvas(str(pdf_path))
    pdf.drawString(50, 750, "Page one")
    pdf.showPage()
    pdf.drawString(50, 750, "Page two")
    pdf.save()

    text = extract_pdf_text(pdf_path)

    assert "Page one" in text
    assert "Page two" in text
