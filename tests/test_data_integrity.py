import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


@pytest.mark.parametrize(
    "filename",
    ["ground_truth.json", "real_ground_truth.json"],
)
def test_ground_truth_is_valid_json_array(filename):
    path = DATA_DIR / filename

    if not path.exists():
        pytest.skip(f"{filename} is not present")

    data = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(data, list)
    assert data

    for item in data:
        assert "file_name" in item
        assert "expected_extraction" in item
        assert "expected_audit_result" in item

        audit = item["expected_audit_result"]
        assert audit["status"] in {"PASS", "FLAGGED", "REJECTED"}
        assert isinstance(audit["screening_priority_score"], int)
        assert 0 <= audit["screening_priority_score"] <= 100


def test_sku_catalog_is_valid():
    path = DATA_DIR / "skus.json"

    if not path.exists():
        pytest.skip("data/skus.json is not present")

    catalog = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(catalog, (list, dict))

    records = catalog if isinstance(catalog, list) else list(catalog.values())

    for record in records:
        assert isinstance(record, dict)
        assert (
            "sku" in record
            or "covered_part_numbers" in record
            or "mpn_cross_reference" in record
        )
