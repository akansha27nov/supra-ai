# agent/run_pdf.py
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import uuid
import pdfplumber
from dotenv import load_dotenv
from pdfminer.pdfparser import PDFSyntaxError
from pdfplumber.utils.exceptions import PdfminerException

load_dotenv()
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agent.graph import graph

# --- Catalog scope note (read this before "fixing" skus.json) ---
# data/skus.json: 9 generic placeholder SKUs from Round 1 (e.g. "Over-Ear Wireless
#   Headphones"), built for the synthetic cert_XX_*.pdf sample set in data/sample_pdfs.
#   Those synthetic certs carry no product/model number at all (only a Certificate ID,
#   supplier, lab, and lead ppm) — they were never meant to be matched by part number,
#   so `covered_part_numbers` is intentionally empty here. Populating it against the
#   real-world DoC/lab-report set is NOT a safe mechanical fix: several categories
#   (headphones, speakers) have 2-3 competing real products with no principled way to
#   pick one as "the" SKU, one (power bank) has a capacity mismatch suggesting a
#   different product tier, and several real files (radio, soundbar, phone mount,
#   smartphone, AC power supply, home energy hub) have no catalog entry at all. Forcing
#   a match here would be a business decision, not a data-extraction one, and a wrong
#   guess could mask a real compliance issue on whichever product didn't get picked.
# data/real_skus.json: 5 SKUs purpose-built for the b2b real-world set (Envoy, ACH480,
#   Concens, Apogee, UNOnext) — these DO have real part numbers populated and verified
#   against match_sku(), since each has exactly one unambiguous real-world document.
DEFAULT_SKU_CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "skus.json"


def load_sku_catalog(catalog_path: Path) -> dict:
    """Loads a SKU catalog JSON (list or dict form) into a dict indexed by SKU code.
    Mirrors langsmith/trace_sample.py's load_skus() so both pipelines read the same
    catalog format consistently. Returns {} (not an error) if the catalog is missing —
    the pipeline still runs, it just can't do SKU-aware checks."""
    if not catalog_path or not Path(catalog_path).exists():
        print(f"Warning: SKU catalog not found at {catalog_path} — SKU matching will be skipped.")
        return {}

    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        catalog = {}
        for item in data:
            if isinstance(item, dict) and "sku" in item:
                catalog[item["sku"]] = item
        return catalog

    return data if isinstance(data, dict) else {}


def extract_raw_pdf_text(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    # Explicit page markers give the LLM a real signal for evidence_links'
                    # page_number field. Without this, all pages get concatenated into one
                    # blob and the model has to guess — confirmed wrong in testing (an item
                    # on page 2 was reported as page 1, since nothing in the text said otherwise).
                    text += f"[PAGE {i + 1}]\n{page_text}\n"
        return text
    except (PdfminerException, PDFSyntaxError) as e:
        print(f"Warning: Skipping invalid or corrupted PDF - {e}")
        return None
    except Exception as e:  # noqa: BLE001
        print(f"Warning: Unexpected error reading {pdf_path} - {e}")
        return None


def _corrupted_file_result(file_path: Path) -> dict:
    """Builds a graph.invoke()-shaped result for a file that couldn't be parsed at all,
    so it still shows up in the audit trail instead of silently vanishing. An unreadable
    supplier document is itself a finding (possible corruption, encryption, or a non-PDF
    file mislabeled as one) — it should be visible to a reviewer, not just a console line."""
    return {
        "file_name": file_path.name,
        "doc_type": "unknown",
        "extracted": {},
        "field_status": {},
        "reconciliation_attempts": 0,
        "needs_human_review": True,
        "review_reason": "File could not be parsed (corrupted, encrypted, or not a valid PDF).",
        "associated_sku": None,
        "sku_match_status": "not_attempted",
        "audit_result": {
            "score": 100,
            "decision": "REJECTED",
            "flags": [
                {
                    "code": "CORRUPTED_OR_UNREADABLE_FILE",
                    "severity_score": 100,
                    "message": "PDF could not be parsed — file may be corrupted, encrypted, or not a valid PDF.",
                }
            ],
            "audited_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def _infer_data_source_tag(file_path: Path) -> str:
    """Tags each LangSmith trace with where its input document came from, so real-world
    test runs and synthetic sample-data runs can be told apart / filtered in the
    LangSmith UI — this is what actually proves every real-world file was traced,
    not just that tracing exists somewhere in the codebase."""
    path_str = str(file_path).replace("\\", "/").lower()
    if "real_world" in path_str:
        return "real_world_data"
    if "sample_pdfs" in path_str:
        return "sample_data"
    return "unknown_source"


def audit_file(file_path: Path, sku_catalog: dict, associated_sku: str | None = None) -> dict:
    print(f"\n--- Auditing: {file_path.name} ---")
    raw_text = extract_raw_pdf_text(str(file_path))

    if not raw_text:
        result = _corrupted_file_result(file_path)
        print("Audit Result:", result["audit_result"])
        return result

    initial_state = {
        "file_name": file_path.name,
        "raw_text": raw_text,
        "doc_type": "unknown",
        "extracted": {},
        "field_status": {},
        "reconciliation_attempts": 0,
        "needs_human_review": False,
        "review_reason": None,
        "sku_catalog": sku_catalog,
        "associated_sku": associated_sku,
        "sku_match_status": "not_attempted",
        "audit_result": None,
    }

    data_source = _infer_data_source_tag(file_path)
    result = graph.invoke(
        initial_state,
        config={
            "run_name": f"audit_{file_path.name}",
            "tags": [data_source],
            "metadata": {"file_name": file_path.name, "data_source": data_source},
        },
    )
    result.setdefault("file_name", file_path.name)  # defensive: state should already carry this

    print(f"Document Type: {result.get('doc_type')}")
    print(f"Needs Human Review: {result.get('needs_human_review')}")
    print(f"Associated SKU: {result.get('associated_sku')} ({result.get('sku_match_status')})")
    print("Extracted Data:", result.get('extracted'))
    print("Audit Result:", result.get('audit_result'))

    return result


def save_extracted_data_json(results: list, output_dir: Path = Path("logs")) -> Path:
    """Persists the full extracted data (including covered_part_numbers) for every
    audited file to disk. Previously this only ever went to stdout via `print(...)` in
    audit_file() and was lost the moment the terminal closed — which is exactly why the
    SKU catalog's missing covered_part_numbers field took 3 separate runs across 19 files
    to properly diagnose. Run this after any batch to see exactly what was extracted.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    json_path = output_dir / f"extracted_data_{timestamp}.json"

    payload = [
        {
            "file_name": res.get("file_name"),
            "doc_type": res.get("doc_type"),
            "associated_sku": res.get("associated_sku"),
            "sku_match_status": res.get("sku_match_status"),
            "extracted": res.get("extracted"),
        }
        for res in results
    ]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    print(f"[INFO] Extracted data JSON saved: {json_path.resolve()}")
    return json_path


def save_markdown_log(results: list, output_dir: Path = Path("logs")) -> Path:
    """Generates a unique timestamped Markdown compliance audit report log."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f"audit_logs_{timestamp}.md"

    md_content = []
    md_content.append("# Compliance Audit Logs\n")

    current_time_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    md_content.append(f"**Generated At:** {current_time_str}\n")
    md_content.append(f"**Total Files Audited:** {len(results)}\n\n")

    md_content.append("| File Name | Associated SKU | SKU Match | Decision | Score | Flags / Violations |")
    md_content.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for res in results:
        file_name = res.get("file_name", "Unknown")
        sku = res.get("associated_sku") or "UNMATCHED"
        sku_match = res.get("sku_match_status", "not_attempted")

        audit_res = res.get("audit_result", {}) or {}
        decision = audit_res.get("decision", "UNKNOWN")
        score = audit_res.get("score", 0)

        flags = audit_res.get("flags", [])
        flag_msgs = []
        for f in flags:
            if isinstance(f, dict):
                flag_msgs.append(f"{f.get('code')}: {f.get('message')}")
            else:
                flag_msgs.append(str(f))

        flags_str = "<br>".join(flag_msgs) if flag_msgs else "None"
        md_content.append(f"| {file_name} | {sku} | {sku_match} | **{decision}** | {score} | {flags_str} |")

    output_path.write_text("\n".join(md_content), encoding="utf-8")
    print(f"\n[INFO] Markdown report exported: {output_path.resolve()}")
    return output_path


def append_to_master_csv(results: list, output_dir: Path = Path("logs")) -> Path:
    """Append audit results to the master CSV ledger.

    Every result receives a stable RecordID and starts with ReviewStatus=PENDING.
    The generated RecordID is also written back onto the result dict so API
    callers can immediately use it for human review.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "master_audit_ledger.csv"

    file_exists = csv_path.exists()
    current_time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "RecordID",
                "Timestamp",
                "File Name",
                "Supplier",
                "Associated SKU",
                "SKU Match Status",
                "Decision",
                "Score",
                "Flags",
                "ReviewStatus",
                "Reviewer",
            ])

        for res in results:
            record_id = res.get("record_id") or str(uuid.uuid4())

            # Make the ID available to API callers as well as the CSV.
            res["record_id"] = record_id

            file_name = res.get("file_name", "Unknown")
            sku = res.get("associated_sku") or "UNMATCHED"
            sku_match = res.get("sku_match_status", "not_attempted")

            # supplier_name lives in the extraction schema (agent/schemas.py) — it was
            # already being extracted, just never persisted to the ledger, so it fell
            # back to "Unknown Supplier" everywhere in the UI regardless of the document.
            extracted = res.get("extracted", {}) or {}
            supplier = extracted.get("supplier_name") or "Unknown Supplier"

            audit_res = res.get("audit_result", {}) or {}
            decision = audit_res.get("decision", "UNKNOWN")
            score = audit_res.get("score", 0)

            flags = audit_res.get("flags", [])
            flag_msgs = []

            for flg in flags:
                if isinstance(flg, dict):
                    flag_msgs.append(
                        f"{flg.get('code')}: {flg.get('message')}"
                    )
                else:
                    flag_msgs.append(str(flg))

            flags_str = " | ".join(flag_msgs) if flag_msgs else "None"

            writer.writerow([
                record_id,
                current_time_str,
                file_name,
                supplier,
                sku,
                sku_match,
                decision,
                score,
                flags_str,
                "PENDING",
                "",
            ])

    print(f"[INFO] Master CSV ledger updated: {csv_path.resolve()}")
    return csv_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the compliance audit pipeline against PDF(s).")
    parser.add_argument("target", help="A PDF file or a directory of PDFs to audit.")
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_SKU_CATALOG_PATH),
        help="Path to the SKU catalog JSON to match against (default: data/skus.json). "
             "Pass data/real_skus.json when auditing the real-world document set.",
    )
    parser.add_argument(
        "--sku",
        default=None,
        help="Force a specific associated SKU for every file in this run, instead of "
             "relying on automatic part-number matching (useful when auditing a single "
             "supplier's documents for one known product).",
    )
    args = parser.parse_args()

    sku_catalog = load_sku_catalog(Path(args.catalog))
    print(f"[INFO] Loaded {len(sku_catalog)} SKUs from {args.catalog}")

    target_path = Path(args.target)
    all_results = []

    if target_path.is_file() and target_path.suffix.lower() == ".pdf":
        res = audit_file(target_path, sku_catalog, associated_sku=args.sku)
        if res:
            all_results.append(res)
    elif target_path.is_dir():
        pdf_files = list(target_path.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files in {target_path}")
        for pdf_file in pdf_files:
            res = audit_file(pdf_file, sku_catalog, associated_sku=args.sku)
            if res:
                all_results.append(res)
    else:
        print(f"Error: '{target_path}' is not a valid PDF file or directory.")
        sys.exit(1)

    if all_results:
        save_markdown_log(all_results)
        save_extracted_data_json(all_results)
        append_to_master_csv(all_results)
