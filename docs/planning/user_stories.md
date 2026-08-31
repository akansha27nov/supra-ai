# Supra AI Compliance Auditor — User Stories

## 1. Purpose

These user stories define the business and technical outcomes for the next iteration of the Supra AI Compliance Auditor. The project is decision support for supplier-compliance screening: AI extracts information from supplier documents, while deterministic rules perform the policy screening and a human remains responsible for final review.

The next iteration expands the current proof of concept from synthetic certificates and five real-world Declarations of Conformity (DoCs) toward a broader document set that also includes real laboratory test reports, supplier gap notices, and a lightweight user interface.

## 2. Personas

- **Compliance Manager** — needs trustworthy extraction and transparent screening results to prioritize human review.
- **Procurement Specialist / Vendor Manager** — needs clear, actionable supplier-document gaps and corrective-action requests.
- **Inventory / Product Manager** — needs supplier/manufacturer part numbers connected to internal SKUs so compliance evidence can be evaluated against the correct product.
- **Reviewer / Auditor** — needs to inspect the source document, extracted fields, rules triggered, and final status before making a decision.

## 3. Epic 1 — Document Extraction and Classification

### US-1.1 — Extract structured compliance data

> **As a Compliance Manager, I want supplier PDFs converted into structured JSON, so that compliance information can be screened consistently without manually searching every document.**

**Acceptance criteria**

- Given a PDF containing a compliance declaration or laboratory report, when the extraction workflow runs, then it returns the agreed schema including document classification, supplier, dates, standards, covered part numbers where stated, and chemical data where applicable.
- Given a document where a field is genuinely not stated, when extraction runs, then the field is represented as `null` rather than invented.
- Given a document with a field that is not applicable to its document type, when extraction runs, then the workflow records that state explicitly and does not treat it as a parsing failure.
- Given malformed or incomplete source text, when extraction cannot confidently resolve a field, then the workflow produces an explicit unresolved/ambiguous state and can route the document to human review.

### US-1.2 — Classify document type

> **As a Compliance Manager, I want the system to distinguish a manufacturer Declaration of Conformity from a laboratory test report, so that the correct expectations are applied to each document type.**

**Acceptance criteria**

- Given a manufacturer self-declaration, when classified, then the document is identified as `DECLARATION_OF_CONFORMITY`.
- Given a laboratory testing document, when classified, then the document is identified as `LAB_TEST_REPORT`.
- Given an unknown document type, when classification is uncertain, then the system does not guess and routes the document for review.
- A self-declaration without a laboratory accreditation ID must not automatically be treated as an unaccredited laboratory report.

### US-1.3 — Distinguish legal thresholds from measured results

> **As an Auditor, I want the system to distinguish a statutory/legal chemical limit from an actual measured laboratory result, so that a legal threshold is never mistaken for test evidence.**

**Acceptance criteria**

- Given a RoHS document containing a `1000 ppm` legal threshold but no measured lead result, when extracted, then `is_statutory_limit` is `true` and `tested_lead_ppm` remains `null`.
- Given a laboratory report containing an actual measured lead concentration, when extracted, then the measured value is stored as `tested_lead_ppm` and is not labeled as merely a statutory limit.
- Given an ambiguous chemical value, when the targeted reconciliation step cannot resolve its meaning, then the document is routed to human review rather than assigned a confident value.

## 4. Epic 2 — SKU Resolution and Policy Screening

### US-2.1 — Resolve supplier MPNs to internal SKUs

> **As an Inventory Manager, I want manufacturer part numbers extracted from compliance documents matched against the internal catalog, so that screening is performed against the correct product requirements.**

**Acceptance criteria**

- Given an extracted manufacturer part number that exists in the cross-reference catalog, when SKU resolution runs, then the corresponding internal SKU is returned.
- Given no matching SKU, when resolution runs, then the workflow records an explicit unmatched-SKU condition.
- An unmatched SKU must not be silently treated as a clean compliance result.

### US-2.2 — Apply deterministic screening rules

> **As a Procurement Specialist, I want structured evidence evaluated by deterministic rules, so that the final policy decision is reproducible and does not depend on an LLM making the compliance decision.**

**Acceptance criteria**

- Given valid structured extraction output, when the rule engine runs, then it returns `PASS`, `FLAGGED`, or `REJECTED` plus a priority/severity score.
- The rule engine applies the defined policy thresholds consistently.
- Missing or non-applicable values do not cause unhandled exceptions.
- The LLM may extract or reconcile evidence but must not invent the final policy status.

## 5. Epic 3 — Human Review and Supplier Gap Notice

### US-3.1 — Human-in-the-loop review

> **As a Compliance Manager, I want flagged or ambiguous cases routed for human review, so that uncertain evidence is not converted into an unsafe automated decision.**

**Acceptance criteria**

- Given unresolved extraction ambiguity, when the workflow finishes, then the document is marked for human review with a reason.
- Given a `FLAGGED` or `REJECTED` screening result, the reviewer can see the triggered rules and extracted evidence.
- The workflow does not present an unresolved case as confidently compliant.

### US-3.2 — Generate a supplier gap notice

> **As a Procurement Specialist, I want a pre-filled Supplier Gap Notice for failed documents, so that I can request corrective documentation from a supplier quickly and consistently.**

**Acceptance criteria**

- Given a `FLAGGED` or `REJECTED` result, when the Gap Notice step runs, then it identifies the supplier, document, failed rules, and required corrective action.
- The notice must use the actual rule-engine findings rather than inventing failures.
- The reviewer can inspect/edit the notice before sending it.

## 6. Epic 4 — User Interface and Reporting

### US-4.1 — Upload and inspect a document

> **As a Compliance Reviewer, I want a simple interface to upload a PDF and inspect its extraction and screening result, so that I can use the system without interacting directly with the code.**

**Acceptance criteria**

- The UI accepts a compliance PDF.
- The UI displays extraction results, screening status, priority score, and flagged issues.
- The UI clearly indicates when human review is required.
- The UI provides access to the generated Gap Notice when applicable.

### US-4.2 — Feed results to Tableau

> **As a Compliance Manager, I want audited structured results exported for Tableau, so that I can monitor supplier and product compliance at portfolio level.**

**Acceptance criteria**

- The pipeline exports a stable tabular schema.
- Synthetic and real-world datasets can remain distinguishable.
- New test data can be added without overwriting the existing Round 1 benchmark outputs.

## 7. Business Baseline

The current cost analysis uses assumptions rather than measured client operating data. The working baseline is approximately 30 minutes of human review per complex document at an illustrative $50/hour internal labor rate, or about $25/document. LangSmith measurements in the current evaluation set indicate approximately $0.0004 AI inference cost per certificate. These figures should be labeled as assumptions/observations and validated with real operating data before being presented as a client ROI claim.

The immediate objective is therefore to **measure review-time reduction during the pilot**, rather than claim a guaranteed ROI percentage.
