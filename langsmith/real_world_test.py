"""
Run the CURRENT (pre-LangGraph) extraction pipeline against 5 real, publicly-sourced compliance 
documents, to get the actual "before" baseline that langsmith/langgraph_design_spec.md was 
designed against.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from trace_sample import (
    extract_certificate_data,
    extract_pdf_text,
    load_skus,
    screen_certificate,
)

REAL_WORLD_DIR = Path(__file__).resolve().parent.parent / "data" / "real_world" / "raw"

def run():
    sku_catalog = load_skus()
    docs = sorted(REAL_WORLD_DIR.glob("*.pdf"))

    if not docs:
        print(f"No real-world PDFs found in {REAL_WORLD_DIR}")
        return

    for doc_path in docs:
        print("=" * 90)
        print(f"DOCUMENT: {doc_path.name}")
        print("=" * 90)

        raw_text = extract_pdf_text(doc_path)

        try:
            extracted = extract_certificate_data(raw_text)
            print("EXTRACTED FIELDS:")
            for k, v in extracted.items():
                print(f"  {k}: {v!r}")
        except Exception as e:  # noqa: BLE001
            print(f"EXTRACTION FAILED: {e}")
            continue

        try:
            # No SKU mapping for real-world docs yet (not in our catalog which is fabricated) —
            # this deliberately exercises the "no SKU match" path too.
            result = screen_certificate(extracted, associated_sku=None, sku_catalog=sku_catalog)
            print(f"\nRULE ENGINE RESULT: {result['status']} / {result['screening_priority_score']}")
            print(f"FLAGGED ISSUES: {result['flagged_issues']}")
        except Exception as e:   # noqa: BLE001
            print(f"\nRULE ENGINE CRASHED: {e}")
            print("(this is itself a finding — note it in the failure mode analysis)")

        print()


if __name__ == "__main__":
    run()
