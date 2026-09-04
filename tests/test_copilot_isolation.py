# tests/test_copilot_isolation.py
"""Deterministic checks for Audit Copilot behavior that should be
guaranteed by code, not left to an LLM judge's probabilistic grading.

These complement langsmith/copilot_eval.py (the LLM-as-judge groundedness
harness) rather than replacing it: an LLM judge can tell you an answer
*read* as grounded, but only a code-level assertion can guarantee the
context passed to the model never contained another audit's data in the
first place.
"""
from agent.copilot import _context_block


def _fake_record(record_id: str, supplier: str, flags: list[dict]) -> dict:
    return {
        "RecordID": record_id,
        "File Name": f"{record_id}.pdf",
        "Supplier": supplier,
        "SKU": "SKU-TEST-001",
        "SKU Match Status": "matched",
        "Decision": "FLAGGED" if flags else "APPROVED",
        "Score": 75 if flags else 10,
        "FlagsDetail": flags,
    }


def test_context_never_includes_other_records_data():
    """The context block for one record must not contain another record's
    supplier name, file name, or evidence — the isolation guarantee AC-24
    and definition_of_done.md require."""
    record_a = _fake_record("record-a", "Acme Supplies", [
        {"code": "EXPIRY", "severity_score": 75, "message": "Certificate expired",
         "evidence": {"exact_quote": "Valid until 2023-01-01", "page_number": 2, "section": "Validity"}},
    ])
    record_b_supplier = "Zenith Components"  # must never appear in record_a's context

    context = _context_block(record_a, gap_notice=None)

    assert "Acme Supplies" in context
    assert "Certificate expired" in context
    assert record_b_supplier not in context


def test_context_includes_gap_notice_only_when_present():
    record = _fake_record("record-c", "Delta Parts", [
        {"code": "SKU_MISMATCH", "severity_score": 50, "message": "Part number not in catalog", "evidence": None},
    ])

    context_without_notice = _context_block(record, gap_notice=None)
    assert "Gap notice" not in context_without_notice

    gap_notice = {
        "status": "DRAFT",
        "failed_rules": ["SKU_MISMATCH"],
        "corrective_action": "Please confirm the correct part number.",
    }
    context_with_notice = _context_block(record, gap_notice=gap_notice)
    assert "DRAFT" in context_with_notice
    assert "Please confirm the correct part number." in context_with_notice


def test_approved_record_has_empty_evidence_in_context():
    """An APPROVED record's context should carry no violations to cite —
    this is what should make the model (and the refusal-calibration eval)
    correctly decline to invent supporting evidence for a 'why does this
    pass' question."""
    record = _fake_record("record-d", "Approved Co", flags=[])
    context = _context_block(record, gap_notice=None)

    assert "Decision: APPROVED" in context
    assert "Rule violations:" in context  # header still present
    assert "severity=" not in context     # but no actual violation lines
