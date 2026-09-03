# Use Case Definition — Supra AI

## 1. Business Problem Statement

Mid-sized European retailers selling consumer electronics must collect and verify supplier documentation such as CE declarations of conformity, RoHS evidence, laboratory test reports, technical specifications, and certificates.

Today, these documents are often received as emails and PDFs and reviewed manually. This creates several problems:

- Compliance teams spend significant time extracting information from unstructured documents.
- Missing, expired, or inconsistent documentation can be difficult to identify early.
- Information is fragmented across suppliers, products, spreadsheets, and document repositories.
- Manual checks are difficult to standardise and scale as the product catalogue grows.
- Compliance findings need to be explainable and auditable, while AI outputs may otherwise be perceived as a "black box."

The business therefore needs an AI-assisted solution that can **reduce manual screening effort while improving visibility, consistency, and traceability**.

The objective is **not to automate regulatory decision-making**. Instead, AI should assist compliance professionals by turning unstructured supplier documents into structured, reviewable information, applying predefined screening rules, and highlighting potential issues for human assessment.

---

## 2. Industry and AI Adoption Context

The proposed solution is aligned with the broader shift from AI experimentation toward operational use. However, broad AI adoption does not automatically demonstrate measurable business value. This distinction supports Supra AI's focus on a narrow, measurable workflow with clear ownership, defined evaluation criteria, and human oversight.

McKinsey's 2026 global survey reports that nearly nine in ten respondents say their organisations regularly use AI in at least one business function, while 44% report that AI is scaling across the enterprise. The same research shows that larger organisations are further ahead in scaling AI than smaller organisations. This supports the rationale for a focused use case with clear ownership, measurable outcomes, and limited implementation complexity.

McKinsey research on generative-AI benchmarking has also highlighted the importance of measuring AI systems rather than relying solely on qualitative impressions. In that research, 39% of surveyed C-suite leaders reported having benchmark standards for generative-AI tools, while performance and operational measures were prioritised more often than ethical and compliance measures. This supports Supra AI's emphasis on extraction accuracy, deterministic validation, evidence-linked findings, observability, and human review.

The 2025 Stanford AI Index reports that 78% of organisations used AI in at least one business function in 2024, up from 55% in 2023. It also reports that private investment in generative AI reached $33.9 billion in 2024. These figures demonstrate increasing AI adoption and investment, but they do not by themselves demonstrate that a specific compliance workflow will produce ROI.

Supra AI will therefore evaluate its own performance using workflow-specific measures including document extraction accuracy, rule-screening agreement, evidence traceability, screening time, and human-review outcomes.

---

## 3. Company Profile

| Attribute | Profile |
|---|---|
| Industry | Consumer electronics / omnichannel retail |
| Company size | Mid-sized European company |
| Employees | Approximately 200 |
| Product catalogue | Approximately 2,000 active SKUs |
| Suppliers | EU and non-EU suppliers |
| Compliance process | Primarily manual and document-based |
| Current challenge | Fragmented documentation and time-consuming verification |
| AI maturity | Early-stage / limited AI adoption |

The target client is a mid-sized European omnichannel retailer selling consumer electronics. The company is large enough to experience meaningful compliance-document workload but small enough that a focused AI solution can be piloted without requiring an enterprise-wide transformation.

The initial use case is deliberately centred on **supplier compliance documentation for consumer electronics**, rather than attempting to solve supplier management or regulatory compliance across all product categories.

---

## 4. Proposed AI Solution

**Supra AI** is an AI-assisted supplier compliance screening system.

A compliance user uploads or submits supplier documentation. The system then:

1. Ingests the document.
2. Classifies the document type.
3. Extracts relevant information using AI.
4. Structures the extracted information into standard compliance fields.
5. Resolves supplier product/model identifiers against the internal SKU catalogue where applicable.
6. Applies predefined deterministic business and compliance rules.
7. Identifies missing, inconsistent, expired, or potentially problematic information.
8. Assigns a review priority based on the screening result.
9. Shows supporting evidence from the source document.
10. Routes flagged or ambiguous cases to a human reviewer.
11. Provides an audit-scoped Copilot Chat that allows the reviewer to investigate findings, understand supporting evidence, and ask questions about the selected audit.
12. Generates a structured Supplier Gap Notice for applicable flagged or rejected screening outcomes.
13. Keeps the final compliance decision with a human reviewer.

### Example

A supplier submits a Declaration of Conformity for a product.

Supra AI could extract:

- Product name / model
- Manufacturer
- Supplier
- Applicable directives or regulations
- Declared standards
- Declaration date
- Certificate or document reference
- Part numbers / manufacturer part numbers

The system could then identify:

> **Potential issue:** Declaration date is missing.

or:

> **Review required:** The product model extracted from the document does not match the available SKU record.

For a flagged or rejected screening outcome, the system can generate a Supplier Gap Notice containing the supplier, document reference, failed screening rules, supporting evidence, and requested corrective action.

The compliance professional can inspect the source evidence, investigate the finding, edit the proposed communication where required, and make the final compliance decision.

System statuses such as **APPROVED, FLAGGED, or REJECTED** represent the outcome of the defined screening workflow. They are **not legally binding regulatory decisions** and do not replace professional assessment.

### System Type

**Human-in-the-loop AI document intelligence and compliance screening system.**

The architecture combines:

- LLM-based document understanding
- Structured information extraction
- Document classification
- Supplier/product identifier resolution
- Deterministic validation rules
- Evidence-based outputs
- AI observability and evaluation
- Human review
- Structured Gap Notice generation

The LLM is an **assistant**, not the final decision-maker.

---

## 5. Key Stakeholders and Interests

| Stakeholder | Interest / Concern |
|---|---|
| Compliance / Regulatory Team | Accuracy, traceability, explainability and reduced manual workload |
| Head of Procurement | Faster supplier onboarding and fewer documentation delays |
| Procurement Team | Clear visibility into supplier documentation gaps |
| Product Managers | Reliable SKU-level compliance information |
| IT / Data Team | Security, maintainability, integration and observability |
| Management | Cost reduction, risk reduction and measurable business value |
| Suppliers | Clear and consistent feedback on documentation gaps |
| Legal / Data Protection | GDPR compliance, appropriate data handling and accountability |

The **primary MVP user is the compliance professional**. Procurement, product management, IT/data, management, suppliers, and legal/data-protection stakeholders are secondary stakeholders.

---

## 6. User Journey

### Current Process

**Supplier → Email/PDF → Manual extraction → Manual checking → Spreadsheet/document repository → Follow-up → Compliance decision**

### Proposed Process

**Supplier document → Supra AI → Document classification → AI extraction → SKU/MPN resolution → Rule validation → Risk/review priority → Evidence review → Human decision → Optional Supplier Gap Notice**

The MVP focuses on improving the **document-screening and review portion** of this process rather than attempting to replace the entire supplier-management lifecycle.

### Audit Review with Copilot

After the automated screening workflow produces findings, the compliance reviewer can use **Audit Copilot Chat** within the context of the selected audit.

The reviewer can ask questions about:

- why a finding was triggered,
- which evidence supports the finding,
- what information was extracted from the source document,
- which deterministic rule produced the result,
- what information is missing or ambiguous,
- and what should be verified during human review.

The Copilot is **audit-scoped** and acts as an investigation and explanation layer over the existing screening results. It does not replace the deterministic rule engine and does not modify the underlying audit result.

The reviewer remains responsible for interpreting the evidence and making the final compliance decision.

The resulting workflow is:

**Supplier document → Supra AI → Classification → Extraction → SKU/MPN resolution → Rule validation → Findings → Evidence review → Audit Copilot investigation → Human decision → Optional Supplier Gap Notice**

The Copilot therefore supports the existing human-review stage rather than creating a separate compliance decision process.

---

## 7. Success Criteria

The MVP will be evaluated using a representative test dataset containing synthetic data and public/real-world supplier compliance documents, with manually established ground truth where applicable.

### AI Performance

- Target **≥95% field-level extraction accuracy** for the selected compliance fields against manually labelled ground-truth values.
- Target **≥90% agreement** between the deterministic rule-based screening results and manually verified ground-truth outcomes across the defined test cases.
- Provide supporting document evidence for **100% of AI-generated flags**.
- Report extraction performance separately by relevant field and document type.
- Explicitly distinguish missing, non-applicable, ambiguous, and extracted values rather than silently treating missing information as compliant.

### Business Performance

- Target a **≥50% reduction in initial document-screening time** compared with the defined manual baseline.
- Reduce the number of documents requiring complete manual review by prioritising higher-risk and ambiguous cases.
- Demonstrate a measurable reduction in time spent extracting and organising compliance information.
- Measure reviewer effort during pilot validation rather than claiming guaranteed ROI from AI inference cost alone.

### Trust and Governance

- **100% of final compliance decisions remain human-approved.**
- AI outputs must clearly distinguish between:
  - extracted facts,
  - deterministic rule findings,
  - and AI-generated interpretation or explanation.
- Every flagged finding must be traceable to supporting source evidence.
- AI runs should be observable through evaluation and monitoring data.
- Ambiguous or unresolved cases must be routed to human review rather than being treated as confidently compliant.
- The system must not use an AI-generated conclusion as the sole basis for final compliance, supplier-approval, or product-release decisions.

---

## 8. MVP Scope

The MVP will focus on a deliberately narrow capability:

> **Upload a supplier compliance document and receive a structured, evidence-backed compliance-screening result that a human reviewer can verify.**

The initial MVP focuses on supplier compliance documentation for consumer electronics, including relevant declarations and laboratory evidence. It does not attempt to cover every EU regulation, product category, or supplier-management process.

### Supported Core Workflow

The MVP should support:

- PDF document ingestion
- Document classification
- Structured extraction of agreed compliance fields
- Explicit handling of missing and non-applicable fields
- Detection of ambiguous information
- Distinction between statutory chemical limits and measured laboratory results where applicable
- Supplier/manufacturer part-number to internal SKU resolution where applicable
- Deterministic compliance screening
- Review-priority / risk indication
- Evidence-linked findings
- Human-review routing
- Audit-scoped Copilot Chat for investigation and explanation of audit findings and supporting evidence
- Supplier Gap Notice generation for applicable flagged/rejected cases
- Structured screening results suitable for review and downstream reporting

### MVP Output

For each processed document, the system should provide:

- Document identification and classification
- Supplier information
- Product / model information
- Part numbers and SKU matching status where applicable
- Extracted compliance information
- Relevant dates and certificate information
- Standards and regulatory information
- Chemical/test information where applicable
- Missing-field detection
- Rule-based validation results
- Potential issues / review flags
- Screening decision
- Confidence or review-priority information where available
- Evidence from the source document
- Human-review status
- Supplier Gap Notice information where applicable

This narrow scope ensures that the core AI capability can run end-to-end and be evaluated reliably.

---

## 9. Out-of-Scope Boundaries

The MVP will **not**:

- Make legally binding compliance decisions.
- Automatically approve or reject products or suppliers without human review.
- Replace qualified regulatory or compliance professionals.
- Guarantee that a product is legally compliant.
- Replace laboratory testing, certification, or official conformity assessment.
- Cover every EU regulation or product category.
- Act as a complete supplier-management platform.
- Act as a complete regulatory-management platform.
- Process real customer personal data.
- Automatically submit regulatory information to authorities.
- Provide legal advice.
- Use AI output as the sole basis for final compliance, supplier-approval, or product-release decisions.
- Automatically communicate a regulatory decision to a supplier without the required human review and approval.
- Use Copilot Chat as an autonomous compliance decision-maker or as a mechanism for overriding deterministic screening results.

Supplier Gap Notices are intended to support **document remediation and follow-up**. They do not constitute legal or regulatory determinations.

---

## 10. AI Transparency and Human Oversight

Transparency is a central requirement because the company's primary concern is that AI may be a "black box."

Supra AI therefore separates the workflow into three principal layers:

### Layer 1 — Extraction

The AI identifies information contained in the source document and converts it into a structured schema.

Where information is not stated, the system should represent it as missing rather than inventing a value. Where information is ambiguous or unresolved, the system should preserve that state and allow human review.

### Layer 2 — Validation

Deterministic rules check the extracted information against predefined requirements.

Examples include:

- document classification requirements,
- certificate expiry,
- mandatory standards,
- measured chemical thresholds,
- laboratory accreditation requirements,
- SKU matching,
- and other explicitly defined screening rules.

The rule engine should produce reproducible outcomes from the same inputs.

### Layer 3 — Human Decision

A compliance professional reviews:

- the extracted information,
- triggered rules,
- supporting evidence,
- unresolved or ambiguous information,
- and the resulting screening status.

The reviewer remains responsible for the final compliance decision. The Audit Copilot supports this review by explaining existing findings and evidence, but its responses are advisory and do not override deterministic screening results or transfer final decision-making responsibility from the reviewer.

---

## 11. Round 1 → Round 2 Evolution

### Round 1

The initial concept explored whether AI could support supplier compliance screening through:

- Sector research
- Opportunity and risk analysis
- A BI dashboard
- A lightweight automation POC
- AI monitoring / observability
- Preliminary cost and timeline estimates
- Initial synthetic and real-world document evaluation

The main hypothesis was:

> **AI can reduce the manual effort involved in reviewing supplier compliance documents without removing human accountability.**

### Round 2

**Decision: KEEP the industry and core use case.**

The Round 1 concept was retained because the use case provides:

- a clear business problem,
- a defined primary user,
- measurable AI performance criteria,
- a realistic MVP boundary,
- deterministic validation,
- evidence-based outputs,
- and a strong human-in-the-loop model.

Round 2 evolves the concept from a lightweight POC into a working MVP.

The focus is strengthened in five areas:

1. **End-to-end functionality** — the core document-screening workflow must actually run.
2. **Evaluation** — extraction and validation performance are measured against defined test data and ground truth.
3. **Transparency** — findings are linked to supporting source evidence.
4. **Governance** — human oversight, data protection, AI governance considerations, and risk controls are documented.
5. **Business value** — screening time, implementation cost, operating assumptions, and potential ROI are evaluated using explicit assumptions and measured pilot results where available.

The project deliberately remains narrow:

> **One reliable supplier-compliance screening capability is prioritised over a broad but incomplete compliance platform.**

---

## 12. Core Value Proposition

> **Supra AI helps compliance teams turn unstructured supplier documents into structured, evidence-backed compliance insights — reducing manual screening effort while keeping final decisions with humans.**

The strategic value is therefore not simply "using AI for compliance."

It is:

> **Using observable and controlled AI to make supplier-compliance screening faster, more consistent, and easier to review without transferring accountability from humans to an AI system.**

---

## References

- McKinsey & Company. (2026). *The State of AI in 2026: On the Road to ROI*.
- McKinsey & Company. (2025). *AI in the Workplace: A Report for 2025*.
- Stanford Institute for Human-Centered Artificial Intelligence. (2025). *The 2025 AI Index Report*.