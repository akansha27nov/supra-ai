"""
LangSmith observability sample for Supra AI's compliance auditor.
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langsmith.wrappers import wrap_openai
from openai import OpenAI
from pypdf import PdfReader

from langsmith import traceable

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PDF_DIR = DATA_DIR / "sample_pdfs"
REAL_WORLD_DIR = DATA_DIR / "real_world" / "raw"

client = wrap_openai(OpenAI())

DEFAULT_LEAD_PPM_THRESHOLD = 1000
EXPIRING_SOON_DAYS = 30
KNOWN_ACCREDITATION_PREFIXES = ("DAKKS-", "CNAS-", "DAT-P-", "UKAS-", "ANAB-", "A2LA-")

SEVERITY = {
    "EXPIRED": 90,
    "LEAD_EXCESS": 95,
    "SUSPICIOUS_LAB": 85,
    "MISSING_CRITICAL_STANDARD": 75,
    "UNACCREDITED_LAB": 70,
    "MISSING_OTHER_STANDARD": 65,
    "NO_SKU_MATCH": 50,
    "EXPIRING_SOON": 60,
    "UNVERIFIABLE_FIELD": 55,
}


def load_skus(file_path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Loads SKU JSON array or dict and returns a dictionary indexed by SKU code."""
    if file_path is None:
        file_path = DATA_DIR / "skus.json"

    if not file_path.exists():
        print(f"⚠️ Warning: SKU file not found at {file_path}")
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        catalog = {}
        for item in data:
            if isinstance(item, dict) and "sku" in item:
                catalog[item["sku"]] = item
            elif isinstance(item, dict):
                catalog.update(item)
        return catalog

    return data if isinstance(data, dict) else {}

def normalize_standard(std: str) -> str:
    """Strip parenthetical detail so 'RED Directive 2014/53/EU (Radio Equipment)'
    matches an extracted 'RED Directive 2014/53/EU'."""
    return std.split(" (")[0].strip()

def normalize_standard_code(std_str: str) -> str:
    """Extracts core numerical/directive identifiers for resilient cross-matching."""
    if not std_str:
        return ""
    std_str = std_str.upper()
    match = re.search(r"(\d{4}/\d+(?:/EU)?|\d{5}(?:-\d+)?)", std_str)
    if match:
        return match.group(1)
    return re.sub(r"[^A-Z0-9]", "", std_str)


def is_standard_present(required_std: str, extracted_standards: list[str]) -> bool:
    """Checks if a required standard is satisfied by extracted standards."""
    req_norm = normalize_standard_code(required_std)
    if not req_norm:
        return False
    for ext in extracted_standards:
        ext_norm = normalize_standard_code(ext)
        if req_norm in ext_norm or ext_norm in req_norm:
            return True
    return False

EXTRACTION_SYSTEM_PROMPT: str = """You are an expert compliance document parsing agent. Extract compliance document information. Return ONLY valid JSON with keys:\n"
- document_classification: 'DECLARATION_OF_CONFORMITY' or 'LAB_TEST_REPORT'\n
- certificate_id: string or null\n
- supplier_name: string or null\n
- issuing_lab: string or null (null for self-declarations)\n
- lab_accreditation_id: string or null\n
- issue_date: Search for document dates, signing dates, or declaration dates (formatted as YYYY-MM-DD).
   * Look near signatures, headers, or lines containing "Date:", "Issued:", "Revision Date:", or "Executed on:"\n
- expiration_date: string (YYYY-MM-DD) or null\n
- covered_part_numbers: Extract ALL model numbers, SKUs, part numbers, or series designations listed anywhere in the document (including headers, footers, tables, or text bodies).
   * If a family/series code is given (e.g., "ENV-IQ-AM1-240", "UNO-C01X001", "ACH480-04"), extract every item.
   * Search for explicit SKUs, model numbers, product series, or trade names (e.g., "Wireless Earbuds", "Smart Speaker", "RoHS-APO-2025").
   * If no alphanumeric SKU is present, extract the primary product title or series name mentioned in the header or subject line.
   * Do NOT return an empty list if product codes or series identifiers are present in the text.\n
- standards_found: array of strings\n
- chemical_data: object with keys:\n
    * is_statutory_limit: boolean (true if standard compliance limit is declared without specific lab ppm test values)\n
    * tested_lead_ppm: number or null (extract exact numerical lead/Pb value in PPM or mg/kg if explicitly stated)\n
No markdown tags or extra commentary."""

@traceable(name="certificate_information_extraction")
def extract_certificate_data(certificate_text: str) -> dict[str, Any]:
    """Extract structured fields from raw certificate text via LLM with document classification."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": EXTRACTION_SYSTEM_PROMPT,
            },
            {"role": "user", "content": certificate_text},
        ],
        temperature=0.0,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "document_classification": "DECLARATION_OF_CONFORMITY",
            "certificate_id": None,
            "supplier_name": None,
            "issuing_lab": None,
            "lab_accreditation_id": None,
            "issue_date": None,
            "expiration_date": None,
            "covered_part_numbers": [],
            "standards_found": [],
            "chemical_data": {"is_statutory_limit": True, "tested_lead_ppm": None},
        }

@traceable(name="compliance_screening")
def screen_certificate(
    extracted: dict[str, Any],
    associated_sku: str | None,
    sku_catalog: dict[str, dict[str, Any]],
    ref_date_str: str = "2026-08-31",
) -> dict[str, Any]:
    """Evaluates extracted document data against catalog rules and assigns audit priority score."""
    flagged_issues: list[str] = []
    status = "PASS"
    screening_priority_score = 10
    ref_date = datetime.strptime(ref_date_str, "%Y-%m-%d")   # noqa: DTZ007

    if isinstance(sku_catalog, list):
        sku_catalog = load_skus()

    sku_record = sku_catalog.get(associated_sku) if associated_sku else None

    # 1. Uncataloged SKU Check
    if associated_sku and not sku_record:
        flagged_issues.append(
            "WARNING: No matching SKU found in catalog — mandatory standards could not be verified"
        )
        screening_priority_score = max(screening_priority_score, SEVERITY["NO_SKU_MATCH"])
        status = "FLAGGED"
        return {
            "status": status,
            "screening_priority_score": screening_priority_score,
            "flagged_issues": flagged_issues,
        }

    # 2. Mandatory Standards Verification (Critical vs Non-Critical Split)
    if sku_record:
        mandatory_stds = sku_record.get("mandatory_standards", [])
        standards_found = extracted.get("standards_found", [])

        missing_standards = [
            std for std in mandatory_stds if not is_standard_present(std, standards_found)
        ]

        if missing_standards:
            for std in missing_standards:
                std_upper = std.upper()
                if "2011/65" in std_upper or "2014/53" in std_upper or "62133" in std_upper:
                    flagged_issues.append(f"CRITICAL: Missing mandatory {std}")
                    screening_priority_score = max(
                        screening_priority_score, SEVERITY["MISSING_CRITICAL_STANDARD"]
                    )
                else:
                    flagged_issues.append(f"WARNING: Missing standard {std}")
                    screening_priority_score = max(
                        screening_priority_score, SEVERITY["MISSING_OTHER_STANDARD"]
                    )
            if status != "REJECTED":
                status = "FLAGGED"

    # 3. Expiration & Issue Date Verification
    has_expiration_flag = False
    exp_date_str = extracted.get("expiration_date")
    if exp_date_str:
        try:
            exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d")   # noqa: DTZ007
            days_to_exp = (exp_date - ref_date).days
            if days_to_exp < 0:
                flagged_issues.append(f"CRITICAL: Certificate expired on {exp_date_str}")
                screening_priority_score = max(screening_priority_score, SEVERITY["EXPIRED"])
                status = "REJECTED"
            elif days_to_exp <= EXPIRING_SOON_DAYS:
                flagged_issues.append(f"WARNING: Certificate expires within 30 days ({exp_date_str})")
                screening_priority_score = max(screening_priority_score, SEVERITY["EXPIRING_SOON"])
                if status != "REJECTED":
                    status = "FLAGGED"
                has_expiration_flag = True
        except ValueError:
            pass

    issue_date_str = extracted.get("issue_date")
    if not issue_date_str:
        flagged_issues.append("WARNING: Missing certificate issue date")
        screening_priority_score = max(screening_priority_score, SEVERITY["UNVERIFIABLE_FIELD"])
        if status != "REJECTED":
            status = "FLAGGED"
    elif not has_expiration_flag:
        try:
            issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")    # noqa: DTZ007
            age_days = (ref_date - issue_date).days
            if age_days > 730:  # Older than 2 years
                flagged_issues.append("WARNING: Document issue date is older than 2 years baseline")
                screening_priority_score = max(screening_priority_score, SEVERITY["MISSING_OTHER_STANDARD"])
                if status != "REJECTED":
                    status = "FLAGGED"
        except ValueError:
            pass

    # 4. Covered Part Numbers Completeness Check
    covered_parts = extracted.get("covered_part_numbers", [])
    if not covered_parts:
        flagged_issues.append("WARNING: No covered part numbers extracted")
        screening_priority_score = max(screening_priority_score, SEVERITY["UNVERIFIABLE_FIELD"])
        if status != "REJECTED":
            status = "FLAGGED"

    # 5. Lab Accreditation Verification
    issuing_lab = extracted.get("issuing_lab")
    lab_acc_id = extracted.get("lab_accreditation_id")
    doc_class = extracted.get("document_classification", "DECLARATION_OF_CONFORMITY")

    if issuing_lab or doc_class == "LAB_TEST_REPORT":
        if not lab_acc_id:
            flagged_issues.append("WARNING: Issuing lab lacks accreditation ID")
            screening_priority_score = max(screening_priority_score, SEVERITY["UNACCREDITED_LAB"])
            if status != "REJECTED":
                status = "FLAGGED"
        else:
            acc_upper = lab_acc_id.upper()
            if not any(acc_upper.startswith(p) for p in KNOWN_ACCREDITATION_PREFIXES):
                flagged_issues.append(
                    f"CRITICAL: Unrecognized or suspicious lab accreditation ID '{lab_acc_id}'"
                )
                screening_priority_score = max(screening_priority_score, SEVERITY["SUSPICIOUS_LAB"])
                status = "REJECTED"

    # 6. Chemical Lead Level Verification
    chem_data = extracted.get("chemical_data", {})
    tested_lead = chem_data.get("tested_lead_ppm")
    is_statutory = chem_data.get("is_statutory_limit", False)
    max_lead = (
        sku_record.get("max_lead_concentration_ppm", DEFAULT_LEAD_PPM_THRESHOLD)
        if sku_record
        else DEFAULT_LEAD_PPM_THRESHOLD
    )

    if tested_lead is not None and not is_statutory:
        if tested_lead > max_lead:
            flagged_issues.append(
                f"CRITICAL: Measured lead ({tested_lead} ppm) exceeds threshold ({max_lead} ppm)"
            )
            screening_priority_score = max(screening_priority_score, SEVERITY["LEAD_EXCESS"])
            status = "REJECTED"
    elif doc_class == "LAB_TEST_REPORT" and (tested_lead is None or is_statutory):
        flagged_issues.append("WARNING: No measured lead value stated in test report")
        screening_priority_score = max(screening_priority_score, SEVERITY["UNVERIFIABLE_FIELD"])
        if status != "REJECTED":
            status = "FLAGGED"

    return {
        "status": status,
        "screening_priority_score": screening_priority_score,
        "flagged_issues": flagged_issues,
    }

@traceable(name="audit_certificate")
def audit_certificate(
    file_name: str, certificate_text: str, associated_sku: str | None, sku_catalog: dict[str, Any]
) -> dict[str, Any]:
    """Parent trace returning flat backward-compatible shape while maintaining nested trace payload."""
    if sku_catalog is None:
        sku_catalog = load_skus()
    extracted = extract_certificate_data(certificate_text)
    # ------------------------------------------------------------------
    # FALLBACK FIX: Ensure covered_part_numbers is never empty if associated_sku exists
    # ------------------------------------------------------------------
    if not extracted.get("covered_part_numbers") and associated_sku:
        extracted["covered_part_numbers"] = [associated_sku]

    audit_result = screen_certificate(extracted, associated_sku, sku_catalog)

    return {
        "status": audit_result["status"],
        "screening_priority_score": audit_result["screening_priority_score"],
        "flagged_issues": audit_result["flagged_issues"],
        "extracted_data": extracted,
        "extracted": extracted,
        "audit_result": audit_result,
    }

def extract_pdf_text(pdf_path: Path) -> str:
    """Extract raw text from a PDF document."""
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def run_evaluation(data_file="ground_truth.json", pdf_dir=PDF_DIR):
    ground_truth_path = DATA_DIR / data_file
    with open(ground_truth_path) as f:
        ground_truth = json.load(f)
    sku_catalog = load_skus()

    print(f"{'File':<35} {'Expected':<15} {'Actual':<15} {'Match'}")
    print("-" * 80)

    correct = 0
    export_rows = []
    for example in ground_truth:
        file_name = example["file_name"]
        pdf_path = pdf_dir / file_name
        cert_text = extract_pdf_text(pdf_path)

        result = audit_certificate(file_name, cert_text, example.get("associated_sku"), sku_catalog)

        expected = f"{example['expected_audit_result']['status']}/{example['expected_audit_result']['screening_priority_score']}"
        actual = f"{result['status']}/{result['screening_priority_score']}"
        is_match = expected == actual
        correct += is_match

        print(f"{file_name:<35} {expected:<15} {actual:<15} {'PASS' if is_match else 'FAIL'}")
        if not is_match:
            print(f"   -> flagged issues: {result['flagged_issues']}")

        extracted = result["extracted_data"]
        
        # Backward-compatible retrieval: checks nested 'chemical_data' first, falls back to root
        chem_data = extracted.get("chemical_data")
        if isinstance(chem_data, dict):
            tested_lead = chem_data.get("tested_lead_ppm")
        else:
            tested_lead = extracted.get("tested_lead_ppm")

        export_rows.append({
            "file_name": file_name,
            "certificate_id": extracted.get("certificate_id"),
            "supplier_name": extracted.get("supplier_name"),
            "associated_sku": example.get("associated_sku"),
            "audit_status": result["status"],
            "screening_priority_score": result["screening_priority_score"],
            "tested_lead_ppm": tested_lead,
            "flagged_issues_detail": "; ".join(result.get("flagged_issues", [])),
        })

    print("-" * 80)
    print(f"Accuracy: {correct}/{len(ground_truth)} ({correct/len(ground_truth)*100:.0f}%)")
    export_path = DATA_DIR / "tableau_export.csv"
    if export_rows:
        with open(export_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=export_rows[0].keys())
            writer.writeheader()
            writer.writerows(export_rows)
        print(f"\nTableau export written to {export_path}")

def run_two_tier_benchmark():
    with open(DATA_DIR / "real_ground_truth.json") as f:
        ground_truth = json.load(f)

    print("=" * 90)
    print("TIER 1: LLM EXTRACTION ACCURACY BENCHMARK")
    print("=" * 90)
    
    tier1_scores = {"supplier": 0, "doc_class": 0, "cert_id": 0, "date": 0, "parts": 0}
    total_docs = len(ground_truth)

    for case in ground_truth:
        file_name = case["file_name"]
        pdf_path = REAL_WORLD_DIR / file_name  # Fixed path to data/real_world/raw/
        cert_text = extract_pdf_text(pdf_path)
        extracted = extract_certificate_data(cert_text)
        expected = case["expected_extraction"]

        # Precision checks
        m_supp = extracted.get("supplier_name") == expected["supplier_name"]
        m_class = extracted.get("document_classification") == expected["document_classification"]
        m_id = extracted.get("certificate_id") == expected["certificate_id"]
        m_date = extracted.get("issue_date") == expected["issue_date"]
        
        # Overlap check for part numbers
        ext_parts = set(extracted.get("covered_part_numbers", []))
        exp_parts = set(expected["covered_part_numbers"])
        m_parts = ext_parts == exp_parts

        tier1_scores["supplier"] += int(m_supp)
        tier1_scores["doc_class"] += int(m_class)
        tier1_scores["cert_id"] += int(m_id)
        tier1_scores["date"] += int(m_date)
        tier1_scores["parts"] += int(m_parts)

        print(f"\nDOCUMENT: {file_name}")
        print(f"  Supplier Match:  {'[PASS]' if m_supp else '[FAIL]'} (Got: {extracted.get('supplier_name')})")
        print(f"  Class Match:     {'[PASS]' if m_class else '[FAIL]'} (Got: {extracted.get('document_classification')})")
        print(f"  Cert ID Match:   {'[PASS]' if m_id else '[FAIL]'} (Got: {extracted.get('certificate_id')})")
        print(f"  Issue Date:      {'[PASS]' if m_date else '[FAIL]'} (Got: {extracted.get('issue_date')})")
        print(f"  Covered Parts:   {'[PASS]' if m_parts else '[FAIL]'} (Got: {extracted.get('covered_part_numbers')})")

    print("\n" + "=" * 90)
    print("TIER 1 BENCHMARK SUMMARY")
    print("=" * 90)
    for metric, score in tier1_scores.items():
        print(f"  {metric.upper():<15}: {score}/{total_docs} ({score/total_docs*100:.0f}%)")
        
if __name__ == "__main__":
    # run_evaluation()
    run_two_tier_benchmark()
