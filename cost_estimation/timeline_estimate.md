# Timeline Estimate — AI-Assisted Supplier Compliance Screening

## Scenario recap

**Client:** Chleo, Head of Procurement and Supply Chain Operations at a mid-sized European omnichannel retailer (~200 employees, ~2,000 active SKUs). This timeline covers the path from pilot to full catalog rollout.

## Phased rollout

### Week 1 — Pilot on one product category

Run the system on a single, contained product category (~50–100 documents) rather than the full catalog. Every AI decision — PASS, FLAGGED, or REJECTED — is reviewed by a human before anything is acted on. The goal of this week is not efficiency, it's **trust-building and error discovery**: does the system's judgment actually match what an experienced reviewer would conclude, and where does it disagree?

**Success criteria for Week 1:** the review team can point to specific cases where the system's flagged issues were correct, and specific cases (if any) where they weren't — both are useful outcomes, since the second indicates what to fix before Week 2.

### Weeks 2–3 — Rule calibration

Using Week 1's findings, adjust the rule engine: severity thresholds, which standards count as "critical" vs. general, and how the lab-accreditation legitimacy check handles edge cases the pilot surfaced. This is also when SKU catalog gaps get addressed — any product category the pilot touched that didn't have clean mandatory-standards data gets filled in.

Expand the pilot to 2–3 more product categories during this phase, still under full human review, to confirm the calibrated rules generalize rather than being overfit to the first category.

### Week 4 — Full catalog rollout

Deploy across the full ~2,000-SKU catalog, with the dashboard live for procurement/compliance leadership. Human review remains required for every FLAGGED and REJECTED case (per the project's explicit scope boundary — this system supports decisions, it does not make them). PASS cases can move to spot-check review rather than 100% review, once Weeks 1–3 have established the system's reliability on clean cases.

## What this timeline assumes (stated explicitly)

- The client can provide access to a representative document set for the pilot category within the first few days — if document access itself is the bottleneck, this timeline shifts accordingly.
- SKU catalog data (mandatory standards per product) already exists in some form and needs structuring, not building from scratch. If the client has no such catalog today, add 1–2 weeks before Week 1 to construct it.
- "Full rollout" in Week 4 means the pipeline is live and processing new/renewed certificates going forward — it does not mean every one of the ~2,000 existing SKUs' historical documentation gets re-screened in that week; a backlog clearance plan would be a separate, additional workstream sized once the real backlog volume is known.

## What Week 4 does not include (Round 2 scope)

Full EU AI Act and GDPR documentation, a formal ROI calculation based on real measured review-time savings, and a strategic go-to-market/commercialization plan are Round 2 deliverables — this timeline covers getting the pilot mechanism proven and rolled out, not the full consulting package around it.

## Risk to this timeline

The clearest risk to this schedule, consistent with the personal risk register from earlier planning: **scope creep during Weeks 2–3** — the temptation to keep expanding rule coverage indefinitely rather than locking calibration and moving to rollout. Mitigation: define calibration "done" criteria before Week 2 starts (e.g., "agreement with human reviewer on 90%+ of pilot cases"), not an open-ended improvement loop.
