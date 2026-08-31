# agent/run.py
import sys
from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv()

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agent.graph import graph

def run_test_audit(pdf_text: str):
    """Executes the LangGraph compliance pipeline against raw text input."""
    initial_state = {
        "raw_text": pdf_text,
        "doc_type": None,
        "extracted_data": {},
        "missing_fields": [],
        "retry_count": 0,
        "max_retries": 2,
        "audit_result": None,
        "status": "processing"
    }

    # Run the compiled graph synchronously
    final_state = graph.invoke(initial_state)
    return final_state

if __name__ == "__main__":
    sample_certificate_text = """
    LABORATORY TEST REPORT
    Report Number: TR-2026-9011
    SKU Code: SKU-ELE-002
    Accreditation: DAKKS-123456
    Issue Date: 2025-02-10
    Expiration Date: 2027-02-10
    
    Test Results:
    Standard Applied: RoHS Directive 2011/65/EU
    Lead (Pb) Content Measured: 15.4 ppm (Pass)
    """

    print("Running compliance audit pipeline...\n")
    result = run_test_audit(sample_certificate_text)

    print(f"Status: {result['status']}")
    print(f"Document Type: {result['doc_type']}")
    print("Extracted Data:", result['extracted_data'])
    print("Audit Result:", result['audit_result'])