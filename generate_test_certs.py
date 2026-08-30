import os
from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data/sample_pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PDFCert(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "SUPRA AI - TEST COMPLIANCE DOCUMENT", border=False, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)

def build_pdf(filename, title, cert_id, supplier, lab, acc_id, issue, expiry, standards, lead_ppm):
    pdf = PDFCert()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(5)
    
    details = [
        ("Certificate ID:", cert_id),
        ("Supplier Name:", supplier),
        ("Testing Laboratory:", lab),
        ("Lab Accreditation No:", acc_id),
        ("Date of Issuance:", issue),
        ("Expiration Date:", expiry),
        ("Tested Lead Content:", f"{lead_ppm} ppm")
    ]
    
    for label, val in details:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(55, 8, label, border=0)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, val, border=0, new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Evaluated Standards & Regulations:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    
    for std in standards:
        pdf.cell(0, 7, f"- {std}", new_x="LMARGIN", new_y="NEXT")
        
    pdf.output(os.path.join(OUTPUT_DIR, filename))
    print(f"Generated: {filename}")

if __name__ == "__main__":
    # 01: Valid Wireless Headphones (Pass Scenario)
    build_pdf("cert_01_valid_headphones.pdf", "CE RED & ROHS COMPLIANCE CERTIFICATE", "RED-DE-2025-99412",
              "Bavarian Audio Tech GmbH", "TUV Rheinland LGA Products GmbH", "DAKKS-D-PL-12042-01-00",
              "2025-06-15", "2028-06-14", ["RED Directive 2014/53/EU", "RoHS Directive 2011/65/EU", "EN 62368-1:2020"], 210)

    # 02: Expired Desk Lamp (Expired Certificate & Missing Safety Standard)
    build_pdf("cert_02_expired_elec.pdf", "ROHS & CE COMPLIANCE TEST REPORT", "ROHS-CN-2022-10492",
              "Shenzhen Shentech Electronics Co., Ltd.", "SGS-CSTC Standards Technical Services Co., Ltd.", "CNAS-L0641",
              "2022-01-10", "2025-01-09", ["CE Directive 2014/30/EU", "RoHS Directive 2011/65/EU"], 450)

    # 03: Unaccredited Internal Lab Charger (Unaccredited Testing & Missing LVD Directive)
    build_pdf("cert_03_unaccredited_lab_charger.pdf", "MANUFACTURER SELF-DECLARATION OF CONFORMITY", "SELF-EC-2026-0012",
              "Global Electronics Supply Ltd.", "Internal Quality Control Dept (Unaccredited)", "NONE",
              "2026-02-01", "2027-02-01", ["CE Directive 2014/30/EU", "RoHS Directive 2011/65/EU"], 380)

    # 04: Valid Wireless Earbuds (Pass Scenario)
    build_pdf("cert_04_valid_wireless_earbuds.pdf", "CE RED & ROHS COMPLIANCE CERTIFICATE", "RED-EU-2026-88102",
              "AudioTech Solutions HK Ltd.", "DEKRA Testing and Certification GmbH", "DAT-P-029/97-01",
              "2026-01-15", "2029-01-14", ["RED Directive 2014/53/EU", "RoHS Directive 2011/65/EU", "EN 62368-1:2020"], 320)

    # 05: Missing RED Directive Smartwatch (Missing Wireless Regulatory Rule)
    build_pdf("cert_05_missing_red_smartwatch.pdf", "EMC & ROHS COMPLIANCE REPORT", "CE-CN-2025-55109",
              "Guangzhou Wearable Tech Co., Ltd.", "Eurofins Product Testing", "DAKKS-D-PL-14031-01-00",
              "2025-09-01", "2028-08-31", ["CE Directive 2014/30/EU (EMC)", "RoHS Directive 2011/65/EU"], 510)

    # 06: Excess Lead Power Bank (RoHS Heavy Metals Chemical Violation)
    build_pdf("cert_06_excess_lead_powerbank.pdf", "ROHS CHEMICAL ANALYSIS TEST REPORT", "ROHS-FAIL-2026-901",
              "PowerMax Energy Ltd.", "Intertek Testing Services China", "CNAS-L0182",
              "2026-03-10", "2028-03-09", ["CE Directive 2014/30/EU", "RoHS Directive 2011/65/EU"], 1450)

    # 07: Suspicious / Unrecognized Lab Monitor (Fraud / Quality Risk)
    build_pdf("cert_07_suspicious_lab_monitor.pdf", "INTERNATIONAL CERTIFICATE OF QUALITY", "CERT-FAKE-99042",
              "Apex Display Systems Inc.", "Global Fast Certs Ltd (Unrecognized)", "FAKE-ACC-000",
              "2026-05-01", "2029-05-01", ["CE Directive 2014/35/EU", "CE Directive 2014/30/EU", "RoHS Directive 2011/65/EU"], 210)

    # 08: Expiring Soon USB Hub (Time-Sensitive Operational Triage)
    build_pdf("cert_08_expiring_soon_usb_hub.pdf", "CE EMC & ROHS DECLARATION", "CE-EU-2023-11029",
              "Dongguan Peripheral Cables Co.", "Bureau Veritas Consumer Products", "DAKKS-D-PL-12003-01-00",
              "2023-09-15", "2026-09-15", ["CE Directive 2014/30/EU", "RoHS Directive 2011/65/EU"], 390)

    # 09: Valid Smart Speaker (Pass Scenario)
    build_pdf("cert_09_valid_smart_speaker.pdf", "EU DECLARATION OF CONFORMITY (RED & ERP)", "RED-DE-2026-00418",
              "SoundHome Audio GmbH", "TUV SUD Product Service GmbH", "DAT-P-022/95-00",
              "2026-04-10", "2029-04-09", ["RED Directive 2014/53/EU", "RoHS Directive 2011/65/EU", "ErP Directive 2009/125/EC"], 180)