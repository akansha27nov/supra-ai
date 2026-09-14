# Supra AI Compliance Auditor — 8-Week Rollout Plan

## Executive Summary

The project follows an eight-week phased plan that separates **technical validation, controlled operational testing, and the final go/no-go decision**.

The objective of Weeks 1–6 is to establish a reliable and reviewable compliance-screening workflow. Weeks 7–8 are **not a full-catalogue rollout**. They are a controlled pilot and evidence-based decision phase for **one limited consumer-electronics category**.

The plan explicitly accounts for dependencies outside the AI pipeline, including supplier-data quality, ERP access, reviewer calibration, security, GDPR, and procurement/process readiness.

This document is the **client-facing summary** of the plan. `sprint_plan.md` is the canonical, story-level source of truth — owners, capacity, dependencies, and exit criteria live there. Each phase below states which sprints it summarises; if the two documents ever appear to disagree, `sprint_plan.md` wins.

```text
Weeks 1–2       Weeks 3–4        Weeks 5–6          Week 7             Week 8
Data +          Classification  Failure handling   Controlled         Go / Conditional
foundations     + extraction     + HITL + ERP      category pilot     Go / No-Go
   │                  │                │                 │                  │
   └──────────────────┴────────────────┴─────────────────┴──────────────────┘
                         Evidence-based validation
```

The planned outcome is **not automatic deployment to all ~2,000 SKUs**. A positive Week 8 decision authorizes only the next agreed deployment step.

---

# Phase 1 — Foundations and Data Readiness (Weeks 1–2)

**Maps to:** Sprint 1 (EN-01) + Sprint 2 (US-1).

## Goal

Establish a reliable technical and data foundation, and reliable document classification, before extraction logic is built.

## Deliverables

- Implement and validate the LangGraph workflow scaffold.
- Define explicit graph state and bounded processing paths.
- Implement document classification (US-1).
- Audit available supplier/document data for the pilot category.
- Establish the ground-truth validation set.
- Instrument pipeline execution in LangSmith using document/run identifiers without exposing unnecessary supplier personal data.
- Update the failure-mode register.

## Dependencies

- Client provides representative supplier documents.
- Pilot-category supplier/product list is available.
- Required sample PDFs are accessible.
- Data-quality issues are documented.

## Exit criteria

- Representative pilot data has been assessed.
- Five existing real-world DoCs remain reproducible as a regression set.
- No known unhandled exception exists for the validated input set.
- Classification reaches the agreed ≥95% target on the validation set (see Sprint 2 exit criteria).
- LangSmith traces provide end-to-end execution traceability.
- If pilot data quality is materially below the agreed threshold, scope/capacity is re-estimated before further expansion.

---

# Phase 2 — Structured Extraction and Failure Handling (Weeks 3–4)

**Maps to:** Sprint 3 (US-2) + Sprint 4 (US-3, US-4).

## Goal

Build and validate structured field extraction against a defined ground-truth set, then ensure the system fails safely and routes uncertain records to human review rather than guessing.

## Deliverables

- Implement structured field extraction and JSON-schema validation (US-2).
- Implement bounded reconciliation.
- Preserve deterministic rule-engine logic as a separate decision layer.
- Establish manual ground truth for the agreed validation sample.
- Validate mandatory-field extraction and evidence links.
- Test confidence and missing-field handling; test chemical concentration tables where applicable.
- Validate measured-vs-statutory-value distinction.
- Implement explicit incomplete/malformed extraction handling (US-3).
- Route unresolved or low-confidence records to human review (US-4).
- Ensure flagged records cannot silently receive a compliant status.
- Run field-level extraction benchmarks and deterministic rule-engine tests separately from AI extraction.

## Exit criteria

- Field-level extraction results are documented by field and document type.
- Critical-field accuracy is explicitly reported against a **≥90% target**.
- Missing-field, low-confidence, corrupted-file, and wrong-schema tests all pass (see Sprint 4 exit criteria — this is the sprint that directly addresses the class of failure demonstrated by the live bug in Round 1).
- Every flagged record reaches an explicit human-review path; no flagged record silently becomes compliant.
- Reviewer corrections preserve the original AI extraction.
- New failure modes are added to the failure-mode register.
- Results are reproducible from the documented validation set.

---

# Phase 3 — Operational Readiness (Weeks 5–6)

**Maps to:** Sprint 5 (EN-02, EN-03) + Sprint 6 (EN-04, EN-05).

## Goal

Close the non-engineering gaps — ERP access, reviewer calibration, security, GDPR, procurement — before any live pilot volume runs.

## Deliverables

- Implement/read-only-test ERP integration where technically available (EN-02).
- Calibrate reviewers using representative flagged cases (EN-03).
- Implement/update the lightweight reviewer UI; display source evidence, extracted values, confidence, status, and reasons.
- Generate supplier gap notices from validated flagged issues.
- Complete security and GDPR readiness checks required for the pilot (EN-04).
- Document procurement/process responsibilities for human approval (EN-05).

## Exit criteria

- ERP interaction is read-only for the pilot unless separately approved.
- Reviewer calibration has been completed on the agreed sample; agreement rate recorded.
- Required security, GDPR, and process dependencies are either approved or explicitly listed as blockers.
- Dashboard access control is confirmed or explicitly flagged as an outstanding gap — do not assume it exists without verifying it in the codebase.

---

# Phase 4 — Controlled Category Pilot (Week 7)

**Maps to:** Sprint 7 (M-01).

## Goal

Validate the complete workflow under controlled operational conditions for **one limited consumer-electronics category**.

This phase is a **pilot, not a production rollout**.

## Deliverables

- Run the agreed representative document sample through the complete workflow.
- Process new pilot documents where available.
- Route all flagged or unresolved cases to human review.
- Record reviewer decisions and corrections.
- Measure:
  - classification accuracy,
  - critical-field extraction accuracy,
  - evidence coverage,
  - unresolved/flagged rate,
  - silent critical misses,
  - **notification/side-channel failure rate** (e.g. Telegram alerts) — the first live-volume test of whether the Sprint 4 failure-handling fix actually holds under real conditions, not just synthetic test cases,
  - human review time,
  - SKU-resolution success,
  - system failures.
- Maintain a clear distinction between real and synthetic validation data.
- Record operational issues and newly discovered failure modes.

## Exit criteria

- All pilot records have an auditable processing outcome.
- No silent critical compliance failure is identified.
- No silent notification/side-channel failure is identified — any alert failure must be persisted and visible, not just logged to console.
- Human-review routing operates as designed.
- Evidence is available for critical extracted fields.
- Review-time measurement is available or its absence is documented.
- Outstanding technical, security, GDPR, ERP, and process risks are documented.

**No automatic expansion to the full ~2,000-SKU catalogue occurs in Week 7.**

---

# Phase 5 — Evidence-Based Go / No-Go Decision (Week 8)

**Maps to:** Sprint 8 (M-02).

## Goal

Determine whether the validated pilot provides sufficient evidence to proceed to the next limited deployment stage.

## Deliverables

- Final benchmark report.
- Accuracy results by document type and critical field.
- Silent-failure analysis (compliance **and** notification failures).
- Human-review agreement/calibration results.
- Review-time comparison where measurable.
- SKU-resolution results.
- Security/GDPR readiness status.
- ERP readiness status.
- Procurement/process readiness status.
- Updated cost/ROI assessment using measured results where available (see `roi_risk_assessment.md` for the planning-assumption baseline this update replaces).
- Final limitations and risk register.
- Stakeholder decision memo.

## Decision Gates

| Gate | Requirement |
|---|---|
| Classification | ≥95% on the validation set |
| Critical fields | ≥90% accuracy |
| Silent critical misses | No unresolved critical silent failures |
| Silent notification failures | Zero unlogged alert/webhook failures |
| Evidence | Critical findings have traceable source evidence |
| HITL | Flagged cases consistently reach human review |
| Reviewers | Human decisions are calibrated and auditable |
| Review time | Measured against the 40% base-case / 20% conservative-case reduction assumed in `roi_risk_assessment.md` |
| GDPR/security | Required pilot controls approved |
| ERP | Required integration/access conditions satisfied |
| Procurement/process | Human approval responsibilities agreed |
| Business case | Costs and benefits supported by evidence or clearly labelled assumptions |

## Decision outcomes

### GO

Proceed to the next **limited, explicitly scoped category/deployment stage**.

### CONDITIONAL GO

Proceed only after specified blockers or controls are completed. The decision memo must identify the conditions, owner, and deadline for each item.

### NO-GO

Do not expand the deployment scope. Return to the relevant technical, data, security, or process phase and address the identified failure.

A **GO decision does not authorize automatic deployment across the full ~2,000-SKU catalogue**.

---

# Capacity and Dependency Management

The plan assumes that engineering capacity is finite and that reviewer, client, security, ERP, and procurement activities may become bottlenecks.

Before each phase, the team records:

- available engineering capacity,
- reviewer capacity,
- client/data availability,
- ERP dependency status,
- security/GDPR dependency status,
- procurement/process dependency status,
- unresolved technical risks.

If a dependency consumes more capacity than planned, the **scope is reduced before quality gates are relaxed**.

---

# Risk Mitigation

| Risk | Early signal | Mitigation |
|---|---|---|
| Supplier data is incomplete | Missing documents/SKUs or poor metadata | Re-estimate pilot scope and resolve data gaps before expansion |
| Lab reports are significantly harder than DoCs | Critical-field accuracy drops | Expand targeted extraction tests and route uncertainty to HITL |
| Chemical tables are ambiguous | Measured/statutory confusion | Explicit field classification plus validation and human review |
| SKU matching is incomplete | High unresolved-MPN rate | Treat as a visible data-quality condition; improve cross-reference |
| LangGraph adds unnecessary complexity | No measurable reliability benefit | Keep graph bounded and compare against baseline |
| Reviewer workload is higher than expected | Flagged cases exceed capacity | Reduce pilot volume or increase reviewer capacity |
| ERP integration takes longer | Access/credentials unavailable | Keep pilot read-only and use controlled export where appropriate |
| Security/procurement is delayed | Required approvals outstanding | Do not treat technical success as production readiness |
| UI takes longer than expected | Backend ready but UI delayed | Keep reviewer interface lightweight |
| Benchmark is too small | High accuracy with limited coverage | Report confidence/limitations and expand validation where capacity permits |
| Pilot reveals new failure modes | Unexpected routing/extraction errors | Log, reproduce, test, and reassess before expansion |
| Notification/side-channel failures go unnoticed | Status shown as complete but no alert received | Persist notification outcomes with the record; never rely on console output alone (see Round 1 incident) |
| Business case is based mainly on assumptions | Review-time baseline unavailable | Label assumptions clearly and use pilot measurements before claiming ROI |

---

# Final Rollout Principle

**The eight-week plan ends with a decision, not a full rollout.**

The sequence is:

**Build → Validate → Harden → Calibrate → Controlled Category Pilot → Evidence-Based Go/No-Go**

Only if the pilot satisfies the agreed technical, compliance, operational, and business gates should the project move to the next deployment stage.
