# agent/benchmark.py
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
SYNTH_DIR = DATA / "sample_pdfs"
REAL_DIR = DATA / "real_world" / "raw"

sys.path.insert(0, str(BASE))

from agent.run_pdf import extract_raw_pdf_text, load_sku_catalog
from agent.graph import graph


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_case(case, pdf_dir, sku_catalog):
    matching_files = list(pdf_dir.rglob(case["file_name"]))
    if not matching_files:
        raise FileNotFoundError(f"Could not find PDF file '{case['file_name']}' anywhere under {pdf_dir}")
    
    pdf_path = matching_files[0]
    raw_text = extract_raw_pdf_text(pdf_path)

    state = {
        "file_name": pdf_path.name,
        "raw_text": raw_text,
        "doc_type": "unknown",
        "extracted": {},
        "field_status": {},
        "reconciliation_attempts": 0,
        "needs_human_review": False,
        "review_reason": None,
        "sku_catalog": sku_catalog,
        "associated_sku": case.get("associated_sku"),
        "sku_match_status": "not_attempted",
        "audit_result": None,
    }

    return graph.invoke(state)


def main():
    sku_catalog = load_sku_catalog(DATA / "skus.json")
    real_catalog = load_sku_catalog(DATA / "real_skus.json")

    synthetic = load_json(DATA / "ground_truth.json")
    real = load_json(DATA / "real_ground_truth.json")

    # Keep only the 7 in-scope synthetic electronics cases
    synthetic = [
        x for x in synthetic
        if x["file_name"] in {
            "cert_02_expired_elec.pdf",
            "cert_04_valid_wireless_earbuds.pdf",
            "cert_05_missing_red_smartwatch.pdf",
            "cert_06_excess_lead_powerbank.pdf",
            "cert_07_suspicious_lab_monitor.pdf",
            "cert_08_expiring_soon_usb_hub.pdf",
            "cert_09_valid_smart_speaker.pdf",
        }
    ]

    totals = {"synthetic": 0, "real": 0}

    for name, cases, directory, catalog in [
        ("SYNTHETIC", synthetic, SYNTH_DIR, sku_catalog),
        ("REAL-WORLD", real, REAL_DIR, real_catalog),
    ]:
        print("\n" + "=" * 90)
        print(f"LANGGRAPH BENCHMARK: {name}")
        print("=" * 90)

        passed = 0

        for case in cases:
            result = run_case(case, directory, catalog)
            actual = result.get("audit_result") or {}

            expected_result = case["expected_audit_result"]

            expected_status = expected_result["status"]
            expected_score = expected_result["screening_priority_score"]

            # Your graph schema uses APPROVED; benchmark uses PASS.
            actual_status = actual.get("decision")
            if actual_status == "APPROVED":
                actual_status = "PASS"

            actual_score = actual.get("score")

            ok = (
                actual_status == expected_status
                and actual_score == expected_score
            )

            passed += int(ok)

            print(
                f"{case['file_name']:<45} "
                f"Expected {expected_status}/{expected_score:<3} "
                f"Actual {actual_status}/{actual_score:<3} "
                f"[{'PASS' if ok else 'FAIL'}]"
            )

        accuracy = passed / len(cases) * 100 if cases else 0
        totals["synthetic" if name == "SYNTHETIC" else "real"] = passed

        print("-" * 90)
        print(f"{name}: {passed}/{len(cases)} ({accuracy:.1f}%)")

    print("\n" + "#" * 90)
    print("LANGGRAPH BENCHMARK SUMMARY")
    print("#" * 90)
    print(f"Synthetic: {totals['synthetic']}/{len(synthetic)}")
    print(f"Real-world: {totals['real']}/{len(real)}")
    print(
        f"Overall: {(totals['synthetic'] + totals['real'])}/"
        f"{len(synthetic) + len(real)}"
    )
    print("#" * 90)


if __name__ == "__main__":
    main()