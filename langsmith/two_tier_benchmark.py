import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REAL_WORLD_DIR = DATA_DIR / "real_world" / "raw"

from trace_sample import (
    extract_certificate_data,
    extract_pdf_text,
    load_skus,
    screen_certificate,
)


# ==============================================================================
# TIER 1: LLM EXTRACTION PRECISION BENCHMARK (Real PDFs)
# ==============================================================================
def run_tier1_extraction_benchmark():
    ground_truth_path = DATA_DIR / "real_ground_truth.json"
    if not ground_truth_path.exists():
        print(f"⚠️ Tier 1 Skipped: {ground_truth_path} not found.")
        return 0.0

    with open(ground_truth_path, "r") as f:
        ground_truth = json.load(f)

    print("\n" + "=" * 90)
    print("  TIER 1: LLM EXTRACTION PRECISION BENCHMARK (REAL-WORLD PDFS)")
    print("=" * 90)

    field_scores = {
        "supplier_name": 0,
        "document_classification": 0,
        "certificate_id": 0,
        "issue_date": 0,
        "covered_part_numbers": 0,
    }
    total_docs = len(ground_truth)

    for case in ground_truth:
        file_name = case["file_name"]
        pdf_path = REAL_WORLD_DIR / file_name

        if not pdf_path.exists():
            print(f"⚠️ PDF File Missing: {file_name}")
            continue

        cert_text = extract_pdf_text(pdf_path)
        extracted = extract_certificate_data(cert_text)
        expected = case["expected_extraction"]

        # Precision assertions per field
        m_supp = extracted.get("supplier_name") == expected.get("supplier_name")
        m_class = extracted.get("document_classification") == expected.get("document_classification")
        m_id = extracted.get("certificate_id") == expected.get("certificate_id")
        m_date = extracted.get("issue_date") == expected.get("issue_date")
        
        ext_parts = set(extracted.get("covered_part_numbers") or [])
        exp_parts = set(expected.get("covered_part_numbers") or [])
        m_parts = ext_parts == exp_parts

        field_scores["supplier_name"] += int(m_supp)
        field_scores["document_classification"] += int(m_class)
        field_scores["certificate_id"] += int(m_id)
        field_scores["issue_date"] += int(m_date)
        field_scores["covered_part_numbers"] += int(m_parts)

        print(f"\nDocument: {file_name}")
        print(f"  • Supplier Match    : {'[PASS]' if m_supp else '[FAIL]'} (Got: {extracted.get('supplier_name')})")
        print(f"  • Doc Class Match   : {'[PASS]' if m_class else '[FAIL]'} (Got: {extracted.get('document_classification')})")
        print(f"  • Cert ID Match     : {'[PASS]' if m_id else '[FAIL]'} (Got: {extracted.get('certificate_id')})")
        print(f"  • Issue Date Match  : {'[PASS]' if m_date else '[FAIL]'} (Got: {extracted.get('issue_date')})")
        print(f"  • Part Numbers Match: {'[PASS]' if m_parts else '[FAIL]'} (Got: {extracted.get('covered_part_numbers')})")

    total_checks = total_docs * len(field_scores)
    total_passed = sum(field_scores.values())
    tier1_accuracy = (total_passed / total_checks * 100) if total_checks > 0 else 0.0

    print("\n" + "-" * 90)
    print(f"  TIER 1 SUMMARY: {total_passed}/{total_checks} fields verified ({tier1_accuracy:.1f}% Field Precision)")
    print("-" * 90)
    return tier1_accuracy


# ==============================================================================
# TIER 2: DECOUPLED POLICY SCREENING BENCHMARK (Rule Engine Unit Tests)
# ==============================================================================
def run_tier2_rule_engine_benchmark():
    print("\n" + "=" * 90)
    print("  TIER 2: POLICY SCREENING BENCHMARK (DECOUPLED RULE ENGINE UNIT TESTS)")
    print("=" * 90)

    sku_catalog = load_skus()

    test_cases = [
        {
            "test_name": "Edge Case 1: Expired Certificate Date",
            "mock_extracted_json": {
                "supplier_name": "Legacy Tech Corp",
                "document_classification": "DECLARATION_OF_CONFORMITY",
                "certificate_id": "EXP-2019-001",
                "issue_date": "2019-01-01",
                "expiration_date": "2021-01-01",
                "covered_part_numbers": ["SKU-DRV-ACH480"],
                "chemical_data": {"tested_lead_ppm": None, "is_statutory_limit": True}
            },
            "associated_sku": "SKU-DRV-ACH480",
            "expected_status": "REJECTED",
            "expected_min_score": 90
        },
        {
            "test_name": "Edge Case 2: Chemical Limit Violation (Lead > 1000 ppm)",
            "mock_extracted_json": {
                "supplier_name": "SGS Chemical Testing",
                "document_classification": "LAB_TEST_REPORT",
                "certificate_id": "LAB-2023-CHEM",
                "issue_date": "2024-01-15",
                "lab_accreditation_id": "DAKKS-1234",
                "covered_part_numbers": ["SKU-RES-10K-0805"],
                "chemical_data": {"tested_lead_ppm": 1450, "is_statutory_limit": False}
            },
            "associated_sku": "SKU-RES-10K-0805",
            "expected_status": "REJECTED",
            "expected_min_score": 95
        },
        {
            "test_name": "Edge Case 3: Perfectly Compliant Document",
            "mock_extracted_json": {
                "supplier_name": "ABB Oy",
                "document_classification": "DECLARATION_OF_CONFORMITY",
                "certificate_id": "3AXD10000746646",
                "issue_date": "2025-02-01",
                "expiration_date": "2027-02-01",
                "covered_part_numbers": ["ACH480-04"],
                "standards_found": [
                    "RoHS 2 Directive 2011/65/EU",
                    "RED Directive 2014/53/EU"
                ],
                "chemical_data": {"tested_lead_ppm": None, "is_statutory_limit": True}
            },
            "associated_sku": "SKU-DRV-ACH480",
            "expected_status": "PASS",
            "expected_min_score": 10
        }
    ]

    passed_tests = 0
    total_tests = len(test_cases)

    for case in test_cases:
        # Calls screen_certificate directly
        audit_result = screen_certificate(
            extracted=case["mock_extracted_json"],
            associated_sku=case["associated_sku"],
            sku_catalog=sku_catalog
        )

        act_status = audit_result["status"]
        act_score = audit_result["screening_priority_score"]
        
        status_match = act_status == case["expected_status"]
        score_match = act_score >= case["expected_min_score"]
        is_pass = status_match and score_match

        passed_tests += int(is_pass)

        print(f"\nTest: {case['test_name']}")
        print(f"  • Expected Status : {case['expected_status']} (Min Score: {case['expected_min_score']})")
        print(f"  • Actual Status   : {act_status} (Score: {act_score})")
        print(f"  • Verdict         : {'[PASS]' if is_pass else '[FAIL]'}")
        if not is_pass:
            print(f"    └── Triggered Flags: {audit_result.get('flagged_issues')}")

    tier2_accuracy = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
    print("\n" + "-" * 90)
    print(f"  TIER 2 SUMMARY: {passed_tests}/{total_tests} edge cases verified ({tier2_accuracy:.1f}% Rule Accuracy)")
    print("-" * 90)
    return tier2_accuracy


if __name__ == "__main__":
    print("=" * 90)
    print("      SUPRA AI COMPLIANCE AUDITOR - TWO-TIER VALIDATION SUITE")
    print("=" * 90)

    t1_acc = run_tier1_extraction_benchmark()
    t2_acc = run_tier2_rule_engine_benchmark()

    print("\n" + "#" * 90)
    print("                     FINAL TWO-TIER BENCHMARK VERDICT")
    print("#" * 90)
    print(f"  1. Tier 1 (LLM Extraction Precision) : {t1_acc:.1f}%")
    print(f"  2. Tier 2 (Rule Engine Policy Logic) : {t2_acc:.1f}%")
    print("  -------------------------------------------------------------")
    print(f"  OVERALL SYSTEM VALIDATION SCORE     : {((t1_acc + t2_acc) / 2):.1f}%")
    print("#" * 90 + "\n")