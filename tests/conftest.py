import os
import sys
from pathlib import Path

import pytest


# Make the repository root importable when tests are run from any directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Prevent accidental real API calls during unit tests.
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
os.environ.setdefault("LANGCHAIN_API_KEY", "test-key")


@pytest.fixture
def base_extracted():
    return {
        "document_classification": "LAB_TEST_REPORT",
        "certificate_id": "CERT-001",
        "supplier_name": "Example Supplier",
        "issuing_lab": "Example Lab",
        "accreditation_id": "CNAS-L0001",
        "issue_date": "2026-01-01",
        "expiration_date": "2028-01-01",
        "covered_part_numbers": ["MODEL-001"],
        "standards_tested": [
            "RoHS Directive 2011/65/EU",
            "EN 62368-1:2020",
        ],
        "tested_lead_ppm": 100.0,
        "is_statutory_limit": False,
        "lead_exemption_cited": False,
    }


@pytest.fixture
def sku_catalog():
    return {
        "SKU-001": {
            "covered_part_numbers": ["MODEL-001"],
            "mandatory_standards": [
                "RoHS Directive 2011/65/EU",
                "EN 62368-1:2020",
            ],
            "max_lead_concentration_ppm": 1000,
        },
        "SKU-002": {
            "covered_part_numbers": ["MODEL-002"],
            "mandatory_standards": [
                "RED Directive 2014/53/EU",
                "RoHS Directive 2011/65/EU",
            ],
            "max_lead_concentration_ppm": 1000,
        },
        "SKU-003": {
            "covered_part_numbers": ["MODEL-003"],
            "mandatory_standards": [],
            "max_lead_concentration_ppm": 500,
        },
    }


@pytest.fixture
def base_state(base_extracted, sku_catalog):
    return {
        "file_name": "certificate.pdf",
        "raw_text": "Example compliance document",
        "doc_type": "lab_test_report",
        "extracted": base_extracted.copy(),
        "field_status": {
            "covered_part_numbers": "present",
            "accreditation_id": "present",
            "expiration_date": "present",
            "tested_lead_ppm": "present",
        },
        "reconciliation_attempts": 0,
        "needs_human_review": False,
        "review_reason": None,
        "sku_catalog": sku_catalog,
        "associated_sku": None,
        "sku_match_status": "not_attempted",
        "audit_result": None,
    }
