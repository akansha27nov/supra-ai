# GDPR Documentation

**System:** Supra AI — AI-Assisted Supplier Compliance Screening  
**Repository:** `akansha27nov/supra-ai`  
**Document status:** MVP / pilot assessment  
**Assessment date:** 2026-09-02  
**Controller:** `[insert legal entity]`  
**Data Protection Officer:** `[insert name/contact or not applicable]`  
**EU representative:** `[insert if applicable]`

> This document is an initial GDPR assessment for the Supra AI MVP. It must be completed with the legal identity of the controller, actual vendors, hosting locations, retention periods, and deployment arrangements before production use. It is not legal advice.

---

# 1. Scope and System Purpose

Supra AI is designed to assist compliance teams with reviewing supplier and product documentation, including:

- CE certificates
- RoHS certificates
- Test reports
- Declarations of conformity
- Supplier-provided product documentation
- Internal SKU and product records

The system extracts structured information from documents, matches products against SKU records, applies compliance rules, and presents evidence-linked findings for human review.

The system should not be used to:

- Evaluate individuals' personality, behaviour, trustworthiness, or employment suitability.
- Make automated decisions about a person's legal rights or access to services.
- Process special-category data unless specifically assessed and justified.
- Treat AI output as a final legal or regulatory decision.
- Retain supplier documents or extracted data for longer than necessary.

For the MVP and capstone, synthetic or publicly available documents should be used wherever possible. Real supplier documents should only be introduced after the data-flow, security, retention, vendor, and transfer controls have been approved.

---

# 2. GDPR Roles

## 2.1 Controller

The controller is the organisation that determines why and how personal data is processed through Supra AI.

Likely controller:

- The business operating the supplier-compliance process; or
- The customer using Supra AI for its own supplier-document screening.

Controller identity:

- Legal name: `[insert entity]`
- Registered address: `[insert address]`
- Contact: `[insert contact]`
- DPO: `[insert DPO details or not applicable]`

## 2.2 Processor

Supra AI's provider may act as a processor when it processes supplier or customer data on behalf of a customer.

The processor must:

- Process personal data only on documented controller instructions.
- Maintain confidentiality.
- Apply appropriate technical and organisational security measures.
- Use subprocessors only with appropriate authorisation.
- Assist with data-subject rights requests.
- Assist with security incidents, DPIAs, and regulatory consultations.
- Delete or return personal data at the end of the service.
- Provide information necessary to demonstrate compliance.
- Maintain a current subprocessor list.

The exact controller–processor relationship must be confirmed in the customer contract and data-processing agreement.

## 2.3 Independent third parties

Some vendors may process data for their own purposes, such as fraud prevention, billing, legal compliance, or service security. Their role must be assessed individually. They must not automatically be treated as processors.

---

# 3. Data Flow Map

## 3.1 High-level data flow

```text
Supplier / customer user
        |
        | Uploads supplier documents and enters SKU or review information
        v
Supra AI application
        |
        | Access control, file validation, metadata capture
        v
Document storage / temporary processing area
        |
        | PDF parsing, OCR where applicable, text extraction
        v
LLM or AI extraction API
        |
        | Structured fields returned to Supra AI
        v
Extraction and validation layer
        |
        | Normalisation, confidence checks, source-value linking
        v
SKU matching and deterministic compliance rule engine
        |
        | Missing, expired, inconsistent, or potentially non-compliant findings
        v
Reviewer dashboard
        |
        | Human review, approval, rejection, override, comments
        v
Results, audit records, metrics, and monitoring
