# agent/gap_notice.py

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.append(str(Path(__file__).resolve().parent.parent))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agent.schemas import AuditResult

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

def generate_supplier_gap_notice(audit_result: dict, extracted_data: dict, supplier_name: str = "Supplier") -> str:
    """
    Generates a draft email to a supplier regarding compliance gaps.
    A human reviewer will approve this message before it is sent.
    """
    decision = audit_result.get("decision")
    flags = audit_result.get("flags", [])
    
    if decision == "APPROVED" or not flags:
        return "No gap notice required; document is approved."

    # Format the identified issues for the prompt
    issues_list = "\n".join([f"- {flag['code']}: {flag['message']}" for flag in flags])
    sku = extracted_data.get('sku_code') or "[Unknown SKU]"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional procurement and compliance officer. "
                   "Draft a concise, polite email to a supplier requesting updated documentation. "
                   "Clearly state the identified issues and provide evidence based on the compliance review. "
                   "Do not invent any information."),
        ("user", "Supplier Name: {supplier_name}\n"
                 "Product SKU: {sku}\n"
                 "Decision: {decision}\n"
                 "Identified Issues:\n{issues_list}\n\n"
                 "Please draft the gap notice email.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "supplier_name": supplier_name,
        "sku": sku,
        "decision": decision,
        "issues_list": issues_list,
    })
    
    return response.content

if __name__ == "__main__":
    # Example execution based on a failed run
    mock_audit_result = {
        'score': 100, 
        'decision': 'REQUIRES_HUMAN_REVIEW', 
        'flags': [
            {'code': 'UNRESOLVED_CRITICAL_FIELDS', 'severity_score': 100, 'message': "Unresolved fields after 2 retries: ['sku_code']"}
        ]
    }
    mock_extracted = {'sku_code': None}
    
    draft = generate_supplier_gap_notice(mock_audit_result, mock_extracted, "Concens A/S")
    print("\n--- Draft Supplier Gap Notice ---\n")
    print(draft)