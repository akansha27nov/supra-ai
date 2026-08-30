# Cost Analysis — AI-Assisted Supplier Compliance Screening

## Scenario recap

**Client:** Chleo, Head of Procurement and Supply Chain Operations at a mid-sized European omnichannel retailer (~200 employees, ~2,000 active SKUs, consumer electronics sourced from EU and non-EU suppliers).

This document outlines the cost structure, operational savings, and unit economics for deploying the Supra AI Compliance Auditor across an electronics hardware supply chain.

## 1. AI inference cost (measured in LangSmith)

Real cost data captured from LangSmith across the 7-certificate evaluation set:

| Certificate | Tokens | Cost |
|---|---|---|
| cert_09_valid_smart_speaker.pdf | 386 | $0.0004 |
| (average across all 7 traces) | ~368 | ~$0.0004 |

**Finding: AI inference cost is not the cost driver of this project.** At ~$0.0004 per certificate, even at meaningful volume this stays negligible:

| Monthly volume | Monthly AI cost |
|---|---|
| 150 documents (assumption — see below) | ~$0.06 |
| 500 documents | ~$0.20 |
| 2,000 documents (full catalog in one pass) | ~$0.80 |


## 2. Volume assumption (stated explicitly — please validate against real data if available)

**Assumption: ~150 supplier documents require screening or re-screening per month.**

Basis for this estimate: with ~2,000 active SKUs, assuming a rough 7–8% monthly turnover in documentation needs (new product onboarding, supplier changes, and periodic certificate renewals — RoHS/CE certificates in this dataset run 2–4 year validity periods), that yields approximately 150 documents/month. This is a modeling assumption, not a measured figure from the client — it should be replaced with real onboarding/renewal cadence data before this number is used in a real engagement.

## 3. Build cost (upfront, one-time)

Illustrative solo AI-consultant engagement, scoped to a pilot (one product category, not the full catalog):

| Work item | Estimated effort |
|---|---|
| Document extraction pipeline (LLM-based field extraction) | 1 day |
| Rule engine (expiry, lead-threshold, lab-accreditation, mandatory-standards checks) | 1.5 days |
| SKU catalog integration and matching logic | 0.5 day |
| Dashboard (Tableau, stakeholder-facing) | 1 day |
| LangSmith observability setup + validation against labeled test set | 0.5 day |
| Pilot rollout, stakeholder walkthrough, documentation | 1 day |
| **Total** | **~5.5 consulting days** |

At an illustrative EU freelance AI-consultant day rate of €600–900, this is approximately **€3,300–5,000 for the pilot build**. This range is a planning assumption for the conversation with Chleo, not a fixed quote — actual scoping would depend on integration complexity with the client's real document storage/ERP systems, which is unknown at this stage.

## 4. Ongoing operating cost (monthly, post-pilot)

| Item | Estimated monthly cost |
|---|---|
| AI inference (150 docs/month) | ~$0.06 |
| LangSmith (observability, team tier) | ~$0–40 (many teams fit in the free/low tier at this volume) |
| n8n hosting (cloud, starter tier) | ~€20–50 |
| Notion (already in use at most companies, incremental cost ~$0) | ~$0 |
| Human review time (the actual ongoing cost) | See note below |

**The dominant ongoing cost is human review time**, not tooling. This system is explicitly designed as decision support, not autonomous decision-making (see `opportunities_risks.md`) — every flagged case still needs a qualified reviewer. The value proposition is *reducing* review time per document, not eliminating the review step. A full ROI calculation (hours saved × reviewer cost, compared against build + ongoing cost) belongs in Round 2 once pilot data on actual review-time reduction exists — Round 1 cannot honestly claim a specific ROI percentage without that measurement.

## Summary for the pitch

- AI compute cost: negligible (~$0.0004/document)
- Pilot build cost: ~5.5 consulting days (~€3,300–5,000), assumption-based
- Ongoing tooling cost: low (~€20–90/month at pilot scale)
- The real cost/benefit conversation is about **reviewer time saved per document**, which Round 1's pilot is specifically designed to start measuring — not something this stage can respons­ibly quantify yet
