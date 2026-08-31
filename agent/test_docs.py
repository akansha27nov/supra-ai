# agent/test_docs.py

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agent.graph import graph

# Real text extracted from your 5 uploaded DoCs
DOCS_TO_TEST = [
    {
        "name": "Enphase Energy (RoHS DoC)",
        "text": """
        Certificate number: V2023012303
        RoHS EC DECLARATION OF CONFORMITY
        Enphase Energy, Inc. 
        Products identified as: ENV-IQ-AM1-240, ENV-S-AM1-230-60, ENV-S-AB-120-A, ENV-S-WB-230
        Enphase certifies that products are RoHS2 6/6 and RoHS-3 10/10 compliant according to EU Directives 2011/65/EU and 2015/863/EU.
        Standard: EN IEC 63000:2018
        Signed on behalf of Enphase Energy, Inc.: Karen Maxwell, Vice President, Quality
        """
    },
    {
        "name": "ABB (ACH480 RoHS DoC)",
        "text": """
        ABB EU Declaration of Conformity RoHS Directive 2011/65/EU and Delegated Directive (EU) 2015/836
        Manufacturer: ABB Oy, Hiomotie 13, 00380 Helsinki, Finland.
        Product: Frequency converter ACH480-04
        In conformity with Directive 2011/65/EU (RoHS) and Commission Delegated Directive (EU) 2015/863.
        Harmonized standard: EN IEC 63000:2018
        Helsinki, 8 Oct 2021
        """
    },
    {
        "name": "Apogee Instruments (RoHS, REACH, PROP 65)",
        "text": """
        CERTIFICATE OF COMPLIANCE EU RoHS, REACH, & California PROP 65 Declaration of Conformity
        Apogee Instruments, Inc. 721 W 1800 N Logan, Utah 84321 USA
        RoHS 2 – Directive 2011/65/EU, RoHS 3 – Directive 2015/863/EU
        Products do not contain hazardous substances except some mechanical cable assemblies containing greater than 0.1% by weight lead concentration under RoHS Annex III, exemption 6(c).
        Signed: June 2025, Bruce Bugbee, President
        """
    },
    {
        "name": "Concens A/S (RoHS Declaration)",
        "text": """
        concens - excellent electric actuators CE RoHS DECLARATION OF CONFORMITY
        Directive 2011/65/EU, Directive 2015/863 (RoHS 3) and Directive 2017/2102/EU.
        Products supplied by Concens A/S are RoHS compliant. Lead 0,1%, Mercury 0,1%, Cadmium 0,01%, Hexavalent chromium 0.1%.
        Exceptions for lead (Pb) subject to 2011/65/EU Annex III: 6(a), 6(c.).
        Esbjerg, Denmark, Januar 2020, René Lynge, Managing Director
        """
    },
    {
        "name": "Delta Electronics (UNOnext EU RoHS2.0)",
        "text": """
        Certificate of EU RoHS2.0 Compliance
        Manufacturer: Delta Electronics, Inc. No. 256, Yangguang St., Neihu District, Taipei 11491, Taiwan
        Product: UNOnext Indoor Air Quality Monitor
        Type Designation: UNO-C01X001, UNO-C07X011, UNO-C01X000
        Following RoHS Directive 2011/65/EU and EU/2015/863.
        Date: 2025/1/22, Person responsible: Elliot Chen
        """
    }
]

def evaluate_all():
    print(f"{'='*40}\nEvaluating {len(DOCS_TO_TEST)} Real DoCs\n{'='*40}\n")
    
    for i, doc in enumerate(DOCS_TO_TEST, 1):
        print(f"[{i}] Testing: {doc['name']}")
        initial_state = {
            "raw_text": doc["text"],
            "doc_type": None,
            "extracted_data": {},
            "missing_fields": [],
            "retry_count": 0,
            "max_retries": 2,
            "audit_result": None,
            "status": "processing"
        }
        
        result = graph.invoke(initial_state)
        
        print(f"  Status: {result['status']}")
        print(f"  Doc Type: {result['doc_type']}")
        print(f"  Decision: {result['audit_result'].get('decision') if result['audit_result'] else 'N/A'}")
        print(f"  Flags/Issues: {result['audit_result'].get('flags', []) if result['audit_result'] else 'N/A'}")
        print("-" * 40)

if __name__ == "__main__":
    evaluate_all()