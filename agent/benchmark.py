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
from agent.graph import graph, _normalize_std

EVAL_FIELDS = [
    "covered_part_numbers",
    "accreditation_id",
    "issue_date",
    "expiration_date",
    "tested_lead_ppm",
    "standards_tested",
    "supplier_name"
]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_value(val):
    """Normalizes extracted vs ground-truth values for resilient comparison.

    Numeric fields (like tested_lead_ppm) are typed as float in the extraction schema, but
    ground-truth JSON files commonly write plain ints (e.g. 450). Prior to this fix these
    compared as the strings "450" vs "450.0" and never matched - confirmed via a real run
    showing 0/7 on tested_lead_ppm despite the extracted values being numerically correct.
    Try a numeric-aware comparison first; fall back to string comparison for genuinely
    non-numeric fields (supplier_name, certificate_id, etc.).
    """
    if isinstance(val, list):
        return sorted([str(v).strip().upper() for v in val if v])
    if val is None:
        return None
    try:
        return round(float(val), 4)
    except (TypeError, ValueError):
        return str(val).strip().upper()

def compare_field(predicted, actual, field_name=None):
    """standards_tested gets special handling: regulatory citations legitimately vary in
    wording ("RoHS Directive 2011/65/EU" vs "2011/65/EU" vs "Directive 2011/65/EU" are all
    the same rule). Comparing by literal string would produce false failures purely from
    wording, not real extraction inaccuracy. Reuse _normalize_std - the exact same
    core-code extraction the rule engine (_standard_is_covered in graph.py) already relies
    on to judge standard coverage - so this benchmark measures the same thing production
    actually cares about, not stricter-than-necessary string equality.
    """
    if field_name == "standards_tested":
        pred_list = predicted if isinstance(predicted, list) else ([predicted] if predicted else [])
        act_list = actual if isinstance(actual, list) else ([actual] if actual else [])
        pred_codes = sorted({_normalize_std(s) for s in pred_list if s})
        act_codes = sorted({_normalize_std(s) for s in act_list if s})
        return pred_codes == act_codes
    return normalize_value(predicted) == normalize_value(actual)

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

    # Trackers for extraction accuracy reporting
    eval_fields = [
        "covered_part_numbers",
        "accreditation_id",
        "issue_date",
        "expiration_date",
        "tested_lead_ppm",
        "standards_tested",
        "supplier_name"
    ]
    extraction_stats = {f: {"correct": 0, "total": 0} for f in eval_fields}
    doc_type_stats = {}
    total_ext_evals = 0
    overall_ext_correct = 0

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
            actual_extracted = result.get("extracted") or {}

            # 1. Existing Audit Decision & Score Check
            expected_result = case["expected_audit_result"]
            expected_status = expected_result["status"]
            expected_score = expected_result["screening_priority_score"]

            actual_status = actual.get("decision")
            if actual_status == "APPROVED":
                actual_status = "PASS"

            actual_score = actual.get("score")

            ok = (
                actual_status == expected_status
                and actual_score == expected_score
            )
            passed += int(ok)

            # 2. New Extraction Accuracy Check (Comparing AI extracted fields vs ground truth)
            expected_extraction = case.get("expected_extraction", {})
            doc_type = result.get("doc_type", "unknown")
            if doc_type not in doc_type_stats:
                doc_type_stats[doc_type] = {"correct": 0, "total": 0}

            for field in eval_fields:
                if field in expected_extraction:
                    pred_val = actual_extracted.get(field)
                    act_val = expected_extraction.get(field)

                    extraction_stats[field]["total"] += 1
                    doc_type_stats[doc_type]["total"] += 1
                    total_ext_evals += 1

                    if compare_field(pred_val, act_val, field_name=field):
                        extraction_stats[field]["correct"] += 1
                        doc_type_stats[doc_type]["correct"] += 1
                        overall_ext_correct += 1

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

    # Audit Summary
    print("\n" + "#" * 90)
    print("LANGGRAPH BENCHMARK SUMMARY (AUDIT DECISIONS)")
    print("#" * 90)
    print(f"Synthetic: {totals['synthetic']}/{len(synthetic)}")
    print(f"Real-world: {totals['real']}/{len(real)}")
    print(
        f"Overall: {(totals['synthetic'] + totals['real'])}/"
        f"{len(synthetic) + len(real)}"
    )
    print("#" * 90)

    # Extraction Accuracy Breakdown (Satisfies Round 2 AC)
    print("\n" + "#" * 90)
    print("ROUND 2 EXTRACTION ACCURACY REPORT (Target: >= 90%)")
    print("#" * 90)
    overall_acc = (overall_ext_correct / total_ext_evals * 100) if total_ext_evals > 0 else 0.0
    print(f"Overall Extraction Accuracy: {overall_acc:.1f}% ({overall_ext_correct}/{total_ext_evals})")
    
    print("\nField-Level Breakdown:")
    for fld, st in extraction_stats.items():
        f_acc = (st["correct"] / st["total"] * 100) if st["total"] > 0 else 0.0
        print(f"  - {fld:<25}: {st['correct']}/{st['total']} ({f_acc:.1f}%)")

    print("\nDocument-Type Breakdown:")
    for dt, st in doc_type_stats.items():
        d_acc = (st["correct"] / st["total"] * 100) if st["total"] > 0 else 0.0
        print(f"  - {dt:<25}: {st['correct']}/{st['total']} ({d_acc:.1f}%)")
    print("#" * 90)
    
if __name__ == "__main__":
    main()