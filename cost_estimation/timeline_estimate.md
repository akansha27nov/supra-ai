# Timeline Estimate — AI-Assisted Supplier Compliance Screening

## Scenario recap

**Client:** Chleo, Head of Procurement and Supply Chain Operations at a mid-sized European omnichannel retailer (~200 employees, ~2,000 active SKUs). This timeline covers the full engagement: building out the Round 2 MVP and taking it from pilot to full-catalog rollout.

## Why 8 weeks, not 4

Round 1 proved the core mechanism (LLM extraction + deterministic rule engine) but only against a small, mostly synthetic document set. Round 1's real-world testing surfaced concrete extraction failure modes (missing dates, legal thresholds mistaken for measured values, self-declarations vs. lab reports needing different validation) that the original 4-week client-rollout timeline assumed away. Those findings mean the system genuinely needs to be hardened — with the LangGraph-based extraction pipeline described in `langgraph_design_spec.md` — before it's reliable enough to run in front of a client's live catalog. The timeline below reflects that: **weeks 1–6 are build and de-risking work (technical), weeks 5–8 are where the client-facing pilot and rollout actually happen**, overlapping deliberately so the pilot starts on real (if still-narrow) data rather than waiting for a "finished" system that doesn't exist yet.

This mirrors the phased build plan in `rollout_plan.md`; this document translates that same 8 weeks into what Chleo and her team experience and need to do at each stage.

## Phased plan

```text
Weeks 1–2        Weeks 3–4            Weeks 5–6                Weeks 7–8
Build core   --> Real lab data   -->  Gap notice + UI    -->   Pilot rollout &
& de-risk        + rule tests         + human review           full catalog
(technical)      (technical,          (client's category       (client-facing,
                  narrow pilot         pilot begins,            full 2,000-SKU
                  begins)              under full review)       catalog live)
```

### Weeks 1–2 — Build core pipeline and de-risk extraction

Technical work: implement the LangGraph-based extraction pipeline (document classification, missing/non-applicable field handling, bounded reconciliation, human-review routing — see `langgraph_design_spec.md`), and re-run the five existing real-world documents as a regression set. No client-facing pilot yet; this is the foundation the pilot depends on.

**Success criteria:** the five real documents run without unhandled exceptions, missing dates and statutory-vs-measured chemical values are handled correctly, and LangSmith traces show the graph's execution path end to end.

### Weeks 3–4 — Real lab reports, rule validation, and a narrow client pilot begins

Technical work: source 3–5 real laboratory test reports (a document type distinct from declarations of conformity), establish manual ground truth, and validate the rule engine against edge cases.

Client-facing work: in parallel, start the pilot on **one contained product category (~50–100 documents)**. Every AI decision — PASS, FLAGGED, or REJECTED — is reviewed by a human before anything is acted on. The goal here is not efficiency, it's **trust-building and error discovery**: does the system's judgment match what an experienced reviewer would conclude, and where does it disagree?

**Success criteria:** the review team can point to specific cases where the system's flagged issues were correct, and specific cases (if any) where they weren't — both are useful outcomes, since the second indicates what to calibrate before Weeks 5–6.

### Weeks 5–6 — Supplier gap notice, reviewer UI, and calibration

Technical work: build the Supplier Gap Notice generator and a lightweight reviewer UI (upload a PDF, see extraction, status, and reasoning).

Client-facing work: use Weeks 3–4's pilot findings to calibrate the rule engine (severity thresholds, which standards count as critical vs. general, lab-accreditation edge cases) and fill any SKU catalog gaps the pilot exposed. Expand the pilot to 2–3 more product categories, still under full human review, to confirm the calibrated rules generalise rather than being overfit to the first category.

**Success criteria:** reviewers can use the UI directly without touching code; gap notices are generated from real flagged issues, not invented ones; calibration is judged "done" against a pre-agreed bar (e.g., 90%+ agreement with human reviewer on pilot cases) rather than an open-ended improvement loop.

### Weeks 7–8 — Full catalog rollout, dashboard, and final validation

Client-facing work: deploy across the full ~2,000-SKU catalog, with the Tableau dashboard live for procurement/compliance leadership. Human review remains required for every FLAGGED and REJECTED case (per the project's explicit scope boundary — this system supports decisions, it does not make them). PASS cases can move to spot-check review rather than 100% review, once Weeks 1–6 have established the system's reliability on clean cases.

Technical work: final benchmark run comparing extraction accuracy by document type, cost/timeline documentation finalised, known limitations documented.

## What this timeline assumes (stated explicitly)

- The client can provide access to a representative document set for the pilot category within the first few days of Week 3 — if document access itself is the bottleneck, this timeline shifts accordingly.
- SKU catalog data (mandatory standards per product) already exists in some form and needs structuring, not building from scratch. If the client has no such catalog today, add 1–2 weeks before Week 1 to construct it.
- 3–5 real, publicly/legally usable laboratory test reports can be sourced for Weeks 3–4; if none are available, that phase narrows to declarations-of-conformity validation only, and lab-report handling becomes a Round 3 item.
- "Full rollout" in Weeks 7–8 means the pipeline is live and processing new/renewed certificates going forward — it does not mean every one of the ~2,000 existing SKUs' historical documentation gets re-screened in that window; a backlog-clearance plan would be a separate, additional workstream sized once the real backlog volume is known.

## What about complaince?

Full EU AI Act and GDPR documentation, a formal ROI calculation based on real measured review-time savings, and a strategic go-to-market/commercialisation plan are also inlcuded — this timeline covers building the hardened pipeline and getting it live across the catalog, but also the full consulting package around it.

## Risk to this timeline

The clearest risk to this schedule, consistent with the earlier risk register: **scope creep during Weeks 5–6** — the temptation to keep expanding rule coverage or UI polish indefinitely rather than locking calibration and moving to full rollout. Mitigation: define calibration "done" criteria before Week 5 starts (e.g., "agreement with human reviewer on 90%+ of pilot cases"), not an open-ended improvement loop. A secondary risk is that real lab reports (Weeks 3–4) turn out messier than the declarations of conformity tested so far — if extraction accuracy drops materially, Weeks 5–6 should absorb that fix before UI/gap-notice polish, per the adaptability note in `rollout_plan.md`.
