import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_PDF_DIR = DATA_DIR / "sample_pdfs"
REAL_WORLD_PDF_DIR = DATA_DIR / "real_world" / "raw"

from trace_sample import audit_certificate, extract_pdf_text, load_skus


def evaluate_dataset(dataset_label: str, data_file: Path, pdf_dir: Path, sku_file: Path):
    """Evaluates a dataset against ground truth with flat dict resilience."""
    if not data_file.exists():
        print(f"⚠️ Warning: Dataset file not found at {data_file}. Skipping.")
        return {"label": dataset_label, "total": 0, "correct": 0, "rows": []}

    with open(data_file, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    sku_catalog = load_skus(sku_file)

    print(f"\n" + "=" * 85)
    print(f"  RUNNING BENCHMARK: {dataset_label.upper()}")
    print("=" * 85)
    print(f"{'File':<40} {'Expected':<15} {'Actual':<15} {'Status'}")
    print("-" * 85)

    correct = 0
    dataset_rows = []

    for example in ground_truth:
        file_name = example["file_name"]
        pdf_path = pdf_dir / file_name

        if not pdf_path.exists():
            print(f"{file_name:<40} {'N/A':<15} {'FILE MISSING':<15} [MISSING]")
            continue

        cert_text = extract_pdf_text(pdf_path)
        associated_sku = example.get("associated_sku")

        # Flat-safe return access
        result = audit_certificate(file_name, cert_text, associated_sku, sku_catalog)

        exp_status = example["expected_audit_result"]["status"]
        exp_score = example["expected_audit_result"]["screening_priority_score"]
        expected_str = f"{exp_status}/{exp_score}"

        act_status = result["status"]
        act_score = result["screening_priority_score"]
        actual_str = f"{act_status}/{act_score}"

        is_match = expected_str == actual_str
        correct += int(is_match)

        status_flag = "[PASS]" if is_match else "[FAIL]"
        print(f"{file_name[:38]:<40} {expected_str:<15} {actual_str:<15} {status_flag}")

        if not is_match:
            print(f"   └── Flagged Issues: {result.get('flagged_issues', [])}")

        extracted = result.get("extracted_data") or result.get("extracted", {})
        chem_data = extracted.get("chemical_data", {})
        tested_lead = chem_data.get("tested_lead_ppm") if isinstance(chem_data, dict) else extracted.get("tested_lead_ppm")

        dataset_rows.append(
            {
                "dataset_type": dataset_label,
                "file_name": file_name,
                "certificate_id": extracted.get("certificate_id"),
                "supplier_name": extracted.get("supplier_name"),
                "associated_sku": associated_sku,
                "audit_status": act_status,
                "screening_priority_score": act_score,
                "tested_lead_ppm": tested_lead,
                "flagged_issues_detail": "; ".join(result.get("flagged_issues", [])),
            }
        )

    acc = (correct / len(ground_truth) * 100) if ground_truth else 0.0
    print("-" * 85)
    print(f"Subtotal ({dataset_label}): {correct}/{len(ground_truth)} correct ({acc:.1f}% accuracy)")

    return {
        "label": dataset_label,
        "total": len(ground_truth),
        "correct": correct,
        "rows": dataset_rows,
    }


def export_benchmark_results(synthetic_rows, real_rows, output_dir):
    """Exports dataset-specific CSVs without overwriting single-purpose CSV targets."""
    if synthetic_rows:
        syn_path = output_dir / "tableau_export.csv"
        with open(syn_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=synthetic_rows[0].keys())
            writer.writeheader()
            writer.writerows(synthetic_rows)
        print(f"  ✅ Saved Synthetic Export: {syn_path}")

    if real_rows:
        real_path = output_dir / "tableau_export_real.csv"
        with open(real_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=real_rows[0].keys())
            writer.writeheader()
            writer.writerows(real_rows)
        print(f"  ✅ Saved Real-World Export: {real_path}")

    combined = synthetic_rows + real_rows
    if combined:
        combined_path = output_dir / "tableau_export_combined.csv"
        with open(combined_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=combined[0].keys())
            writer.writeheader()
            writer.writerows(combined)
        print(f"  ✅ Saved Combined Master Export: {combined_path}")


def run_master_benchmark():
    print("=" * 85)
    print("      SUPRA AI COMPLIANCE AUDITOR - MASTER BENCHMARK SUITE")
    print("=" * 85)

    syn_results = evaluate_dataset(
        dataset_label="Synthetic",
        data_file=DATA_DIR / "ground_truth.json",
        pdf_dir=SYNTHETIC_PDF_DIR,
        sku_file=DATA_DIR / "skus.json",
    )

    real_results = evaluate_dataset(
        dataset_label="Real-World",
        data_file=DATA_DIR / "real_ground_truth.json",
        pdf_dir=REAL_WORLD_PDF_DIR,
        sku_file=DATA_DIR / "real_skus.json",
    )

    print("\n" + "-" * 85)
    print("  GENERATING TABLEAU EXPORTS")
    print("-" * 85)
    export_benchmark_results(
        synthetic_rows=syn_results["rows"],
        real_rows=real_results["rows"],
        output_dir=DATA_DIR,
    )

    total_docs = syn_results["total"] + real_results["total"]
    total_correct = syn_results["correct"] + real_results["correct"]
    overall_acc = (total_correct / total_docs * 100) if total_docs > 0 else 0.0

    print("\n" + "#" * 85)
    print("                      COMBINED BENCHMARK SUMMARY")
    print("#" * 85)
    syn_acc = (syn_results["correct"] / syn_results["total"] * 100) if syn_results["total"] else 0.0
    real_acc = (real_results["correct"] / real_results["total"] * 100) if real_results["total"] else 0.0

    print(f"  • Synthetic Dataset Accuracy : {syn_results['correct']}/{syn_results['total']} ({syn_acc:.1f}%)")
    print(f"  • Real-World Dataset Accuracy: {real_results['correct']}/{real_results['total']} ({real_acc:.1f}%)")
    print("  -------------------------------------------------------------")
    print(f"  • OVERALL ACCURACY           : {total_correct}/{total_docs} ({overall_acc:.1f}%)")
    print("#" * 85 + "\n")


if __name__ == "__main__":
    run_master_benchmark()