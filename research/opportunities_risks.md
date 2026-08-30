# Opportunities & Risks — AI-Assisted Supplier Compliance Screening

## AI opportunity

The opportunity is to reduce the manual effort involved in reviewing supplier documentation while giving procurement and compliance teams better visibility into product-documentation risk.

AI is particularly useful where documents are long, inconsistent, or stored in different formats.

### Where AI can help

| **Opportunity** | **How AI helps** | **Business value** |
|---|---|---|
| Document classification | Identifies declarations, test reports, specifications and other document types | Less manual sorting |
| Information extraction | Extracts model numbers, dates, supplier names, standards and other fields | Faster review |
| Cross-document comparison | Compares supplier documents with SKU records and other documents | Finds inconsistencies |
| Missing-information detection | Identifies missing documents or required fields | More complete product files |
| Evidence-based explanations | Shows the source of each finding | Easier verification and auditability |
| Risk prioritisation | Ranks cases using configurable business rules | Focuses staff on important cases |
| Supplier follow-up | Drafts requests for missing or conflicting information | Reduces repetitive work |
| Portfolio monitoring | Aggregates findings across products and suppliers | Gives management visibility |

## Where AI should not make the decision

The system should not:

- Certify products as legally compliant
- Decide that a product is safe for sale
- Provide final legal interpretations
- Invent missing information
- Automatically reject products based only on an AI-generated finding

The system provides **screening and decision support**. Qualified staff remain responsible for final decisions.

## Main risks

| **Risk** | **Example** | **Mitigation** |
|---|---|---|
| Incorrect extraction | Model number or date is read incorrectly | Validate critical fields |
| Hallucination | AI invents a standard or certificate | Require source evidence |
| False positive | Valid documentation is flagged | Human review and override |
| False negative | A real problem is missed | Test against labelled examples |
| Poor document quality | Scanned PDFs produce unreliable results | OCR, confidence checks and manual review |
| Regulatory overreach | AI claims legal compliance | Limit system to evidence screening |
| Privacy | Documents contain personal information | Minimise, anonymise and control access |
| Changing requirements | Rules become outdated | Keep rules configurable and reviewable |
| Cost | Large documents increase AI usage | Monitor cost per document |
| Over-reliance on AI | Reviewers accept findings without checking evidence | Evidence display and human approval |

## Opportunity by project stage

### Round 1 — Feasibility

Prove that AI can reliably:

- Classify documents
- Extract relevant fields
- Detect basic inconsistencies
- Produce evidence-linked findings
- Support a simple review dashboard

The test uses a small, controlled dataset.

### Round 2 — Validation and expansion

Extend the system to:

- More SKUs and suppliers
- More document types
- More validation rules
- More realistic document variation
- Supplier follow-up automation
- Review history and overrides
- More detailed portfolio-level reporting

Measure whether the system can produce a **meaningful improvement over the manual process**.

Key measures include:

- Review time
- Detection accuracy
- False-positive rate
- False-negative rate
- Evidence quality
- Number of cases requiring human intervention
- Supplier follow-up time
- Cost per document

## Risk-control principle

Every important finding should answer:

1. **What is wrong?**
2. **What evidence supports it?**
3. **What should the reviewer do next?**

If sufficient evidence is unavailable, the system should **abstain or request human review rather than guess**.

## Project hypothesis

> **A lightweight AI screening layer can reduce the effort required to review supplier documentation while improving the visibility and traceability of compliance issues, without replacing human compliance decisions.**