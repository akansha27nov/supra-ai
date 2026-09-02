# Use Case Definition — Supra AI

## 1. Business Problem Statement

Mid-sized European retailers selling consumer electronics must collect and verify supplier documentation such as CE declarations, RoHS evidence, test reports, technical specifications, and certificates.

Today, these documents are often received as emails and PDFs and reviewed manually. This creates several problems:

- Compliance teams spend significant time extracting information from unstructured documents.
- Missing, expired, or inconsistent documentation can be difficult to identify early.
- Information is fragmented across suppliers, products, spreadsheets, and document repositories.
- Manual checks are difficult to standardise and scale as the product catalogue grows.
- Compliance decisions need to be explainable and auditable, but AI is often perceived as a "black box."

The business therefore needs an AI-assisted solution that can **reduce manual screening effort while improving visibility, consistency, and traceability**.

The objective is not to automate regulatory decision-making. Instead, AI should assist compliance professionals by turning unstructured supplier documents into structured, reviewable information and highlighting potential issues.

## Industry and AI Adoption Context

The proposed solution is aligned with a broader shift from AI experimentation toward operational use. However, general AI adoption does not automatically lead to measurable business value. This distinction supports the project's focus on a narrow, measurable workflow rather than a broad AI transformation programme.

McKinsey's global survey reports that nearly nine in ten organisations use AI regularly in at least one business function in 2026, while 44% report that AI is scaling across the enterprise. The same research indicates that larger organisations are more likely to scale AI than smaller organisations. This suggests that **mid-sized companies may benefit from focused use cases with clear ownership, defined KPIs, and limited implementation complexity.** 

McKinsey also reports that only 39% of surveyed organisations have established benchmark standards for generative AI tools. Among those using benchmarks, **performance and operational measures are prioritised more often than ethical and compliance measures.** This supports Supra AI's emphasis on extraction accuracy, deterministic validation, evidence-linked findings, monitoring, and human review rather than relying only on an LLM-generated answer.

The 2025 Stanford AI Index reports that 78% of organisations used AI in at least one business function in 2024, up from 55% in 2023. It also reports that global private investment in generative AI reached $33.9 billion in 2024. These figures show that AI adoption and investment are accelerating, but they do not by themselves demonstrate that a specific compliance workflow will produce ROI. Supra AI will therefore evaluate its own performance using document-level accuracy, validation agreement, screening time, traceability, and human-review outcomes.

---

## 2. Company Profile

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

The company is large enough to experience meaningful compliance-document workload but small enough that a focused AI solution can be piloted without requiring an enterprise-wide transformation.

---

## 3. Proposed AI Solution

**Supra AI** is an AI-assisted supplier compliance screening platform.

A compliance user uploads or submits supplier documentation. The system then:

1. Ingests the document.
2. Extracts relevant information using AI.
3. Structures the extracted information into standard compliance fields.
4. Compares the information against predefined business and compliance rules.
5. Identifies missing, inconsistent, or potentially problematic information.
6. Assigns a review priority.
7. Shows the relevant evidence supporting each finding.
8. Routes the result to a human compliance reviewer for final assessment.

### Example

A supplier submits a Declaration of Conformity for a product.

Supra AI could extract:

- Product name / model
- Manufacturer
- Applicable directives or regulations
- Declared standards
- Declaration date
- Signature / responsible person
- Certificate or document reference

The system could then flag:

> **Potential issue:** Document date is missing.

or:

> **Review required:** Product model extracted from the document does not match the SKU record.

The compliance professional can inspect the source document and either approve, reject, or investigate the finding.

### System Type

**Human-in-the-loop AI document intelligence and compliance screening system.**

The architecture combines:

- LLM-based document understanding
- Structured information extraction
- Deterministic validation rules
- Evidence-based outputs
- AI observability and evaluation
- Human review

The LLM is an **assistant**, not the final decision-maker.

---

## 4. Key Stakeholders and Interests

| Stakeholder | Interest / Concern |
|---|---|
| Compliance / Regulatory Team | Accuracy, traceability, explainability and reduced manual workload |
| Head of Procurement | Faster supplier onboarding and fewer documentation delays |
| Procurement Team | Clear visibility into supplier documentation gaps |
| Product Managers | Reliable SKU-level compliance status |
| IT / Data Team | Security, maintainability, integration and observability |
| Management | Cost reduction, risk reduction and measurable business value |
| Suppliers | Clear and consistent feedback on missing documentation |
| Legal / Data Protection | GDPR compliance, appropriate data handling and accountability |

The primary user of the MVP is the **compliance professional**, while management and procurement are secondary stakeholders.

---

## 5. User Journey

### Current Process

**Supplier → Email/PDF → Manual extraction → Manual checking → Spreadsheet → Follow-up → Compliance decision**

### Proposed Process

**Supplier document → Supra AI → AI extraction → Rule validation → Risk/priority flag → Evidence review → Human decision**

The MVP focuses on improving the middle of this process rather than attempting to replace the entire supplier-management lifecycle.

---

## 6. Success Criteria

The MVP will be evaluated using a representative synthetic/public test dataset.

### AI Performance

- Achieve **≥95% field-level extraction accuracy** measured against manually labelled ground-truth values for the selected compliance fields.
- Achieve ≥90% agreement between the system’s rule-based screening results and manually verified ground-truth outcomes across the defined test cases.
- Provide supporting document evidence for **100% of AI-generated flags**.

### Business Performance

- Reduce initial document-screening time by **≥50%** compared with the defined manual baseline.
- Reduce the number of documents requiring complete manual review by prioritising higher-risk cases.
- Demonstrate a measurable reduction in time spent extracting and organising compliance information.

### Trust and Governance

- **100% of final compliance decisions remain human-approved.**
- AI outputs must clearly distinguish between **extracted facts, rule-based findings, and AI-generated interpretation**.
- AI runs should be observable through evaluation and monitoring data.
- The system should allow a reviewer to trace a finding back to its source document.

---

## 7. MVP Scope

The MVP will focus on a deliberately narrow capability:

> **Upload a supplier compliance document and receive a structured compliance-screening result that a human reviewer can verify.**

The initial MVP will support a limited set of document types and compliance fields rather than attempting to cover every regulatory requirement.

### MVP Output

For each document, the system should provide:

- Document identification
- Extracted product information
- Extracted compliance information
- Missing-field detection
- Rule-based validation results
- Potential issues / review flags
- Confidence or review priority
- Evidence from the source document
- Human review status

This narrow scope ensures that the core AI capability can actually run end-to-end and be demonstrated reliably.

---

## 8. Out-of-Scope Boundaries

The MVP will **not**:

- Make legally binding compliance decisions.
- Automatically approve or reject products or suppliers.
- Replace qualified regulatory or compliance professionals.
- Guarantee that a product is legally compliant.
- Replace laboratory testing, certification, or official conformity assessment.
- Cover every EU regulation or product category.
- Process real customer personal data.
- Automatically send regulatory decisions to suppliers.
- Automatically submit information to regulatory authorities.
- Provide legal advice.
- Use AI output as the sole basis for final compliance, supplier-approval, or product-release decisions.

---

## 9. AI Transparency and Human Oversight

Transparency is a central requirement because the company's primary concern is that AI may be a "black box."

Supra AI therefore separates the workflow into three layers:

### Layer 1 — Extraction

The AI identifies information contained in the document.

### Layer 2 — Validation

Deterministic rules check the extracted information against predefined requirements.

### Layer 3 — Human Decision

A compliance professional reviews the evidence and determines the final outcome.

---

## 10. Round 1 → Round 2 Evolution

### Round 1

The initial concept explored whether AI could support supplier compliance screening through:

- Sector research
- Opportunity and risk analysis
- A BI dashboard
- A lightweight automation POC
- AI monitoring / observability
- Preliminary cost and timeline estimates

The main hypothesis was:

> **AI can reduce the manual effort involved in reviewing supplier compliance documents without removing human accountability.**

### Round 2

**Decision: KEEP the industry and core use case.**

The Round 1 concept was retained because the use case provides a clear business problem, measurable AI performance criteria, a realistic MVP boundary, and a strong opportunity to demonstrate transparent human-in-the-loop AI.

Round 2 therefore evolves the concept from a lightweight POC into a working MVP.

The focus is strengthened in five areas:

1. **End-to-end functionality** — the core document-screening workflow must actually run.
2. **Evaluation** — extraction and validation performance will be measured against a test dataset.
3. **Transparency** — findings will be linked to supporting evidence.
4. **Governance** — GDPR, EU AI Act considerations, human oversight, and risk controls will be documented.
5. **Business value** — time savings, implementation cost, ROI, and deployment requirements will be quantified.

The project deliberately remains narrow: **one reliable compliance-screening capability is prioritised over a broad but incomplete compliance platform.**

---

## 11. Core Value Proposition

> **Supra AI helps compliance teams turn unstructured supplier documents into structured, evidence-backed compliance insights — reducing manual screening effort while keeping final decisions with humans.**

The strategic value is therefore not simply "using AI for compliance."

It is **using observable and controlled AI to make compliance work faster, more consistent, and easier to review without transferring accountability from humans to an AI system.**

### References

- McKinsey & Company. (2026). *The state of AI in 2026: On the road to ROI*.  
  https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai

- Stanford Institute for Human-Centered Artificial Intelligence. (2025). *The 2025 AI Index Report*.  
  https://hai.stanford.edu/ai-index/2025-ai-index-report