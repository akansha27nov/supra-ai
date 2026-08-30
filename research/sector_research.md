# Sector Research — AI-Assisted Supplier Compliance Screening

## Scenario

- **Sector:** Retail / Consumer Goods — Import and Distribution
- **Company size:** Mid-sized retailer, approximately 200 employees
- **Operating model:** Omnichannel European retailer
- **Active products:** Approximately 2,000 SKUs
- **Client stakeholder:** Chleo, Head of Procurement and Supply Chain Operations

Chleo is the Head of Procurement and Supply Chain Operations at a mid-sized European omnichannel retailer (~200 employees, ~2,000 SKUs). The company sources consumer electronics from European and non-European suppliers.

Supplier documentation is spread across PDFs, spreadsheets, email attachments, and internal systems. Procurement and compliance teams manually check documents before products are approved for sale.

**Core problem:** Chleo needs a faster way to identify incomplete, expired, or inconsistent supplier documentation and prioritise which products require human review.

The proposed solution is an **AI-assisted screening layer**, not an automated certification or legal decision system.

---
## Why this matters

Consumer electronics require multiple types of product and supplier evidence, and documentation may need to be checked again when products, suppliers, or certificates change.

For a mid-sized retailer, the problem is not necessarily the absence of compliance processes. It is the **manual effort and fragmented information required to maintain them**.

The opportunity is to help procurement and compliance teams answer:

> **Which products have documentation problems, what exactly is wrong, and which cases should we review first?**

---

## Key compliance context

Consumer electronics can be affected by several EU product-safety and environmental requirements depending on the product.

Relevant frameworks to investigate for the selected product category include:

- **CE marking and applicable EU product legislation**
- **RoHS** — restriction of hazardous substances
- **WEEE** — waste electrical and electronic equipment
- **EMC** — electromagnetic compatibility
- **Low Voltage Directive**, where applicable
- **EU Ecodesign / ESPR requirements**, where applicable

The exact requirements depend on the product. The MVP therefore checks **document evidence and predefined rules**, rather than attempting to determine legal compliance automatically.

---

## 3. Sector and Value-Chain Context

A simplified supplier-document lifecycle is:

```text
Supplier selection
    ↓
Product and supplier onboarding
    ↓
Document collection
    ↓
Document extraction and review
    ↓
SKU approval
    ↓
Import and sale
    ↓
Ongoing monitoring and renewal
    ↓
Audit, corrective action, withdrawal, or recall
```

### Stakeholders

| Stakeholder | Main concern | Desired outcome |
|---|---|---|
| Procurement | Delayed onboarding and repeated follow-up | Faster, clearer supplier review |
| Quality/compliance | Incomplete or inconsistent evidence | Reliable audit trail |
| Legal | Regulatory and liability exposure | Early escalation of high-risk cases |
| Product management | Delayed product launches | Transparent approval status |
| Suppliers | Repeated or unclear requests | Specific gap notices |
| Management | Unknown portfolio risk | Risk and backlog visibility |
| IT | Integration and maintenance effort | Low-complexity, modular solution |

---

## Key compliance context

Consumer electronics can be affected by several EU product-safety and environmental requirements depending on the product.

Relevant frameworks to investigate for the selected product category include:

- **CE marking and applicable EU product legislation**
- **RoHS** — restriction of hazardous substances
- **WEEE** — waste electrical and electronic equipment
- **EMC** — electromagnetic compatibility
- **Low Voltage Directive**, where applicable
- **EU Ecodesign / ESPR requirements**, where applicable

The exact requirements depend on the product. The MVP therefore checks **document evidence and predefined rules**, rather than attempting to determine legal compliance automatically.

## Competitive landscape

The market already contains established supplier-risk, product-compliance, procurement, and product-information platforms.

| **Player** | **Focus** | **Relevance** |
|---|---|---|
| ProductIP | Product compliance and regulatory information | Directly relevant to product-document compliance |
| Assent | Product compliance and supply-chain data | Directly relevant to supplier/product compliance |
| EcoVadis | Supplier sustainability assessments | Relevant to supplier risk, but broader |
| IntegrityNext | Supplier sustainability and compliance | Relevant to supplier risk and documentation |
| Prewave | Supply-chain risk monitoring | Relevant to supplier-risk visibility |
| SAP Ariba | Procurement and supplier management | Existing enterprise procurement infrastructure |
| Salsify | Product information management | Relevant to product-data management |

**Gap hypothesis:** existing platforms are generally broader enterprise systems. This project explores whether a **lighter, evidence-first screening workflow** could help a mid-sized retailer identify documentation gaps without replacing its existing procurement or compliance systems.

This is a hypothesis to validate through further competitor research, not a claim that competitors lack these capabilities.


## Data sources

Initial research and validation use:

- European Commission — CE marking and product compliance guidance
- EUR-Lex — EU legislation and regulatory texts
- European Commission — RoHS / WEEE / Ecodesign information
- Public product compliance and supplier-risk documentation from ProductIP, Assent, EcoVadis, IntegrityNext and Prewave
- Synthetic/anonymised supplier documents created specifically for the MVP
- A small manually labelled test set to measure screening accuracy