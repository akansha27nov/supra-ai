import csv
import json
from pathlib import Path

from agent.run_pdf import (
    MASTER_LEDGER_FIELDNAMES,
    _migrate_legacy_ledger_if_needed,
    append_to_master_csv,
)


def _write_result(flags):
    return [{
        "file_name": "evidence-test.pdf",
        "associated_sku": "SKU-TEST",
        "sku_match_status": "matched",
        "extracted": {"supplier_name": "Evidence Test Supplier"},
        "audit_result": {
            "decision": "REJECTED",
            "score": 90,
            "flags": flags,
        },
    }]


def _read_rows(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_append_writes_flags_detail_with_structured_evidence(tmp_path):
    flags = [{
        "code": "OLD_ISSUE_DATE",
        "severity_score": 75,
        "message": "WARNING: too old",
        "evidence": {
            "field_name": "issue_date",
            "exact_quote": "01.06.2020",
            "page_number": 1,
            "section": "date",
        },
    }]

    csv_path = append_to_master_csv(_write_result(flags), output_dir=tmp_path)
    rows = _read_rows(csv_path)

    assert len(rows) == 1
    assert rows[0]["Flags"] == "OLD_ISSUE_DATE: WARNING: too old"

    parsed = json.loads(rows[0]["FlagsDetail"])
    assert parsed[0]["code"] == "OLD_ISSUE_DATE"
    assert parsed[0]["evidence"]["exact_quote"] == "01.06.2020"
    assert parsed[0]["evidence"]["page_number"] == 1
    assert parsed[0]["evidence"]["section"] == "date"


def test_append_writes_null_evidence_when_flag_has_none(tmp_path):
    flags = [{"code": "NO_SKU_MATCH", "severity_score": 50, "message": "no match", "evidence": None}]

    csv_path = append_to_master_csv(_write_result(flags), output_dir=tmp_path)
    rows = _read_rows(csv_path)

    parsed = json.loads(rows[0]["FlagsDetail"])
    assert parsed[0]["evidence"] is None


def test_append_creates_header_with_flags_detail_column(tmp_path):
    csv_path = append_to_master_csv(_write_result([]), output_dir=tmp_path)

    with open(csv_path, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))

    assert header == MASTER_LEDGER_FIELDNAMES
    assert "FlagsDetail" in header


def test_migrate_legacy_ledger_adds_empty_flags_detail_to_existing_rows(tmp_path):
    csv_path = tmp_path / "master_audit_ledger.csv"
    legacy_content = (
        "RecordID,Timestamp,File Name,Supplier,Associated SKU,SKU Match Status,"
        "Decision,Score,Flags,ReviewStatus,Reviewer\n"
        "abc-123,2026-09-02 06:07:56 UTC,Old Doc.pdf,Old Supplier,UNMATCHED,"
        "unmatched,FLAGGED,50,NO_SKU_MATCH: old flag,APPROVED,Executive Reviewer\n"
    )
    csv_path.write_text(legacy_content, encoding="utf-8")

    _migrate_legacy_ledger_if_needed(csv_path)

    rows = _read_rows(csv_path)
    assert len(rows) == 1
    assert rows[0]["FlagsDetail"] == "[]"
    # Existing flat Flags text must survive the migration untouched.
    assert rows[0]["Flags"] == "NO_SKU_MATCH: old flag"


def test_migrate_is_a_noop_on_an_already_migrated_file(tmp_path):
    csv_path = append_to_master_csv(_write_result([]), output_dir=tmp_path)
    before = csv_path.read_text(encoding="utf-8")

    _migrate_legacy_ledger_if_needed(csv_path)

    after = csv_path.read_text(encoding="utf-8")
    assert before == after


def test_append_after_migration_produces_uniform_columns(tmp_path):
    """Regression test for the exact production scenario: an existing
    legacy-format ledger, followed by a real append -- both old and new
    rows must end up with the same column count and be readable together.
    """
    csv_path = tmp_path / "master_audit_ledger.csv"
    legacy_content = (
        "RecordID,Timestamp,File Name,Supplier,Associated SKU,SKU Match Status,"
        "Decision,Score,Flags,ReviewStatus,Reviewer\n"
        "abc-123,2026-09-02 06:07:56 UTC,Old Doc.pdf,Old Supplier,UNMATCHED,"
        "unmatched,FLAGGED,50,NO_SKU_MATCH: old flag,APPROVED,Executive Reviewer\n"
    )
    csv_path.write_text(legacy_content, encoding="utf-8")

    flags = [{
        "code": "X", "severity_score": 90, "message": "bad",
        "evidence": {"field_name": "f", "exact_quote": "q", "page_number": 2, "section": "s"},
    }]
    append_to_master_csv(_write_result(flags), output_dir=tmp_path)

    rows = _read_rows(csv_path)
    assert len(rows) == 2
    assert all(set(row.keys()) == set(MASTER_LEDGER_FIELDNAMES) for row in rows)
    assert json.loads(rows[0]["FlagsDetail"]) == []
    assert json.loads(rows[1]["FlagsDetail"])[0]["evidence"]["exact_quote"] == "q"
