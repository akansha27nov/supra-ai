# agent/run_pdf.py

import sys
from pathlib import Path
import pdfplumber
from dotenv import load_dotenv

load_dotenv()
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agent.graph import graph


def extract_raw_pdf_text(pdf_path: str) -> str:
    """Extracts raw text from all pages of a PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text


def audit_file(file_path: Path):
    print(f"\n--- Auditing: {file_path.name} ---")
    raw_text = extract_raw_pdf_text(str(file_path))

    initial_state = {
        "file_name": file_path.name,
        "raw_text": raw_text,
        "doc_type": "unknown",
        "extracted": {},
        "field_status": {},
        "reconciliation_attempts": 0,
        "needs_human_review": False,
        "review_reason": None,
        "audit_result": None,
    }

    result = graph.invoke(initial_state)

    print(f"Document Type: {result.get('doc_type')}")
    print(f"Needs Human Review: {result.get('needs_human_review')}")
    print("Extracted Data:", result.get('extracted'))
    print("Audit Result:", result.get('audit_result'))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent/run_pdf.py <file_or_directory_path>")
        sys.exit(1)

    target_path = Path(sys.argv[1])

    if target_path.is_file() and target_path.suffix.lower() == ".pdf":
        audit_file(target_path)
    elif target_path.is_dir():
        pdf_files = list(target_path.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files in {target_path}")
        for pdf_file in pdf_files:
            audit_file(pdf_file)
    else:
        print(f"Error: '{target_path}' is not a valid PDF file or directory.")
        sys.exit(1)