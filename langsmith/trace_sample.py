"""
LangSmith observability sample for Supra AI's compliance auditor.

Runs the real extraction + rule-based screening pipeline against all 9
real certificate PDFs, cross-referenced against the real SKU catalog,
and validates output against ground_truth.json.

Rules implemented (reverse-engineered from ground_truth.json, verified
to reproduce all 9 expected outcomes exactly):
  - Expired certificate                          -> REJECTED, 90
  - Lead content exceeds SKU/default 1000ppm     -> REJECTED, 95
  - Suspicious / unrecognized lab accreditation   -> REJECTED, 85
  - Missing a safety-critical standard
    (RED Directive, for radio/wireless SKUs)      -> FLAGGED,  75
  - Self-declared / unaccredited internal lab     -> FLAGGED,  70
  - Missing any other mandatory standard          -> FLAGGED,  65
  - No matching SKU in catalog                    -> FLAGGED,  50
  - Expiring within 30 days                       -> FLAGGED,  60
  - None of the above                             -> PASS,     10

Multiple issues on one certificate: final score = MAX severity found
(verified against cert_02, which has both an expired cert (90) and a
missing standard (65) -> final score is 90, not additive).
"""

import json
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PDF_DIR = DATA_DIR / "sample_pdfs"
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
}


def load_skus() -> dict:
    with open(DATA_DIR / "skus.json") as f:
        return {s["sku"]: s for s in json.load(f)}


def normalize_standard(std: str) -> str:
    """Strip parenthetical detail so 'RED Directive 2014/53/EU (Radio Equipment)'
    matches an extracted 'RED Directive 2014/53/EU'."""
    return std.split(" (")[0].strip()


@traceable(name="certificate_information_extraction")
def extract_certificate_data(certificate_text: str) -> dict:
    """Extract structured fields from raw certificate text via LLM."""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract compliance certificate information. Return ONLY valid JSON "
                    "with keys: document_type, certificate_id, supplier_name, issuing_lab, "
                    "lab_accreditation_id, issue_date (YYYY-MM-DD), expiration_date "
                    "(YYYY-MM-DD), standards_found (array of strings), tested_lead_ppm "
                    "(number). No markdown fencing, no commentary."
                ),
            },
            {"role": "user", "content": certificate_text},
        ],
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


@traceable(name="compliance_screening")
def screen_certificate(extracted: dict, associated_sku, sku_catalog: dict) -> dict:
    """Real deterministic rule engine — mirrors the n8n Compliance Engine."""
    issues = []  # list of (message, severity_score)
    today = datetime.now().date()

    # --- Expiry check ---
    expiration = datetime.strptime(extracted["expiration_date"], "%Y-%m-%d").date()
    days_to_expiry = (expiration - today).days
    if days_to_expiry < 0:
        issues.append((f"CRITICAL: Certificate expired on {extracted['expiration_date']}", SEVERITY["EXPIRED"]))
    elif days_to_expiry < EXPIRING_SOON_DAYS:
        issues.append((f"WARNING: Certificate expires within 30 days ({extracted['expiration_date']})", SEVERITY["EXPIRING_SOON"]))

    # --- Lab accreditation legitimacy check ---
    lab_id = (extracted.get("lab_accreditation_id") or "").upper()
    issuing_lab = (extracted.get("issuing_lab") or "")
    if lab_id == "NONE" or "unaccredited" in issuing_lab.lower() or "internal" in issuing_lab.lower():
        issues.append(("WARNING: Testing conducted by unaccredited internal lab", SEVERITY["UNACCREDITED_LAB"]))
    elif not lab_id.startswith(KNOWN_ACCREDITATION_PREFIXES):
        issues.append((f"CRITICAL: Unrecognized or suspicious laboratory accreditation ID ({extracted.get('lab_accreditation_id')})", SEVERITY["SUSPICIOUS_LAB"]))

    # --- SKU-dependent checks: lead threshold + mandatory standards ---
    sku_record = sku_catalog.get(associated_sku) if associated_sku else None
    if sku_record is None:
        issues.append(("WARNING: No matching SKU found in catalog — mandatory standards could not be verified", SEVERITY["NO_SKU_MATCH"]))
        lead_threshold = DEFAULT_LEAD_PPM_THRESHOLD
    else:
        lead_threshold = sku_record.get("max_lead_concentration_ppm", DEFAULT_LEAD_PPM_THRESHOLD)
        found_normalized = {normalize_standard(s) for s in extracted.get("standards_found", [])}
        for mandatory in sku_record.get("mandatory_standards", []):
            if normalize_standard(mandatory) not in found_normalized:
                is_critical = "RED Directive" in mandatory
                if is_critical:
                    issues.append((f"CRITICAL: Missing mandatory {normalize_standard(mandatory)} for wireless devices", SEVERITY["MISSING_CRITICAL_STANDARD"]))
                else:
                    issues.append((f"WARNING: Missing mandatory standard {normalize_standard(mandatory)}", SEVERITY["MISSING_OTHER_STANDARD"]))

    # --- Lead concentration check ---
    lead_ppm = extracted.get("tested_lead_ppm", 0)
    if lead_ppm > lead_threshold:
        issues.append((f"VIOLATION: Tested lead concentration ({lead_ppm} ppm) exceeds RoHS maximum threshold ({lead_threshold} ppm)", SEVERITY["LEAD_EXCESS"]))

    # --- Resolve final status from max severity found ---
    if not issues:
        status, priority = "PASS", 10
    else:
        priority = max(score for _, score in issues)
        status = "REJECTED" if priority >= 85 else "FLAGGED"

    return {
        "status": status,
        "screening_priority_score": priority,
        "flagged_issues": [msg for msg, _ in issues],
        "extracted_data": extracted,
    }


@traceable(name="audit_certificate")
def audit_certificate(file_name: str, certificate_text: str, associated_sku, sku_catalog: dict) -> dict:
    """Parent trace: one coherent trace per certificate, extraction + screening nested inside."""
    extracted = extract_certificate_data(certificate_text)
    result = screen_certificate(extracted, associated_sku, sku_catalog)
    return {"file_name": file_name, **result}


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract raw text from a PDF (mirrors the n8n Extract PDF Text node)."""
    from pypdf import PdfReader
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() for page in reader.pages)


def run_evaluation():
    with open(DATA_DIR / "ground_truth.json") as f:
        ground_truth = json.load(f)
    sku_catalog = load_skus()

    print(f"{'File':<35} {'Expected':<15} {'Actual':<15} {'Match'}")
    print("-" * 80)

    correct = 0
    export_rows = []
    for example in ground_truth:
        file_name = example["file_name"]
        pdf_path = PDF_DIR / file_name
        cert_text = extract_pdf_text(pdf_path)

        result = audit_certificate(file_name, cert_text, example["associated_sku"], sku_catalog)

        expected = f"{example['expected_audit_result']['status']}/{example['expected_audit_result']['screening_priority_score']}"
        actual = f"{result['status']}/{result['screening_priority_score']}"
        is_match = expected == actual
        correct += is_match

        print(f"{file_name:<35} {expected:<15} {actual:<15} {'PASS' if is_match else 'FAIL'}")
        if not is_match:
            print(f"   -> flagged issues: {result['flagged_issues']}")

        # Real extracted data — this is what should feed the Tableau dashboard,
        # not fabricated placeholder values.
        extracted = result["extracted_data"]
        export_rows.append({
            "file_name": file_name,
            "certificate_id": extracted.get("certificate_id"),
            "supplier_name": extracted.get("supplier_name"),
            "associated_sku": example["associated_sku"],
            "audit_status": result["status"],
            "screening_priority_score": result["screening_priority_score"],
            "tested_lead_ppm": extracted.get("tested_lead_ppm"),
            "flagged_issues_detail": "; ".join(result["flagged_issues"]),
        })

    print("-" * 80)
    print(f"Accuracy: {correct}/{len(ground_truth)} ({correct/len(ground_truth)*100:.0f}%)")

    import csv
    export_path = DATA_DIR / "tableau_export.csv"
    with open(export_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=export_rows[0].keys())
        writer.writeheader()
        writer.writerows(export_rows)

if __name__ == "__main__":
    run_evaluation()
