# Use Cases — AI-Assisted Supplier Compliance Screening

## Use case 1 — AI supplier-document screening

**Primary use case**

### What it does

A procurement or compliance employee provides documents associated with a product.

The system:

1. Identifies the document type
2. Extracts relevant information
3. Checks required fields and dates
4. Compares information with the internal SKU record
5. Compares information across documents
6. Identifies potential problems
7. Provides evidence for each finding
8. Prioritises cases for human review

### Example

The supplier test report states:

> Model: X100

The internal SKU record states:

> Model: X110

The system produces:

**High priority — product identifier mismatch**

It identifies both sources so the reviewer can verify the discrepancy.

### Round 1

Test the core screening workflow using a small labelled dataset.

### Round 2

Expand the test to more documents, suppliers, document formats and validation rules, and compare performance with the existing manual process.

---

## Use case 2 — Compliance risk dashboard

### What it does

The screening results are presented in a management dashboard showing the current state of the product portfolio.

The dashboard can show:

- Products reviewed
- Complete vs incomplete files
- Open documentation issues
- High-priority cases
- Expiring documents
- Issues by supplier
- Issues by product/category
- Review backlog
- Average review time
- Estimated commercial value affected

The dashboard answers:

> **Which products have documentation problems, what type of problems are they, and where should the team focus first?**


---

## Use case 3 — Supplier gap notice

### What it does

When a documentation issue is identified, the system creates a draft request for the supplier.

Example:

> Please provide an updated test report for Model X110. The document provided currently references Model X100, which does not match our product record.

The draft is based on the detected issue and supporting evidence.

A human reviewer approves the message before it is sent.

---

## How the use cases fit together

```text
Supplier documents
        ↓
AI document screening
        ↓
Findings + evidence
        ↓
Risk prioritisation
        ↓
Compliance dashboard
        ↓
Human review
        ↓
Supplier gap notice
        ↓
Reviewer decision / updated document
        ↓
Re-screen
```

The system therefore creates a **continuous review loop**, rather than a one-time document check.
