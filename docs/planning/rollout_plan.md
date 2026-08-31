# Supra AI Compliance Auditor — 8-Week Rollout Plan

## Executive Summary

The project will use an eight-week phased plan, as discussed during review, to make the implementation timeline more realistic and adaptable.

The most important technical risk is reliable extraction from real-world compliance PDFs. Therefore, **LangGraph is implemented early** so that uncertainty handling, document classification, missing fields, and targeted reconciliation can be tested before the final user-facing layer is built.

The plan is intentionally phased: if real laboratory reports expose a larger extraction problem than expected, later work can be adjusted without invalidating the completed foundation.

```text
Weeks 1–2       Weeks 3–4          Weeks 5–6             Weeks 7–8
LangGraph  ---> Real Lab Data ---> Gap Notice + UI ---> Tableau + Final
& Core          + Rule Tests       + Human Review        Validation/Pitch
```

## Phase 1 — LangGraph Core and De-risking (Weeks 1–2)

**Goal:** Prove that the system can handle real PDFs without the failure modes observed in the initial real-world test.

### Deliverables
- Implement `langgraph_pipeline.py`.
- Define explicit graph state.
- Implement extraction, document classification, field validation, reconciliation, and bounded human-review routing.
- Run the five existing real-world DoCs as a regression set.
- Preserve deterministic rule-engine logic.
- Instrument graph execution in LangSmith.
- Update failure-mode analysis with observed results.

### Exit criteria
- Five real DoCs run without known unhandled exceptions.
- Missing expiration dates are handled safely.
- Legal thresholds are not treated as measured results.
- LangSmith traces show the graph path.
- Round 1 benchmark remains reproducible.

## Phase 2 — Real Lab Reports and Rule Validation (Weeks 3–4)

**Goal:** Test the system against the second major document type: actual laboratory reports.

### Deliverables
- Source approximately 3–5 publicly usable lab test reports.
- Establish manual ground truth.
- Extend extraction for chemical concentration tables.
- Test measured-vs-statutory-value reconciliation.
- Create/update BOM/MPN-to-SKU cross-reference data.
- Run Tier 1 extraction benchmark.
- Run Tier 2 deterministic rule-engine tests.

### Exit criteria
- Expanded benchmark has documented ground truth.
- Extraction target of >=90% is met or gaps are explicitly documented.
- Rule-engine edge cases are reproducible.
- Any new failure mode is captured in the failure-mode analysis.

## Phase 3 — Supplier Gap Notice and Front-End (Weeks 5–6)

**Goal:** Turn the backend capability into a usable reviewer workflow.

### Deliverables
- Implement Supplier Gap Notice generator.
- Generate notices from actual flagged issues.
- Add human approval/edit step.
- Build lightweight Streamlit UI.
- Support PDF upload.
- Display extraction, status, priority score, and reasons.
- Display/review the Gap Notice where applicable.

### Exit criteria
- A reviewer can upload a test PDF and understand the resulting decision.
- Flagged/rejected cases generate actionable notices.
- Ambiguous cases visibly require human review.
- UI does not bypass the deterministic policy layer.

## Phase 4 — Tableau, Business Metrics, Validation and Presentation (Weeks 7–8)

**Goal:** Complete the stakeholder-facing prototype and demonstrate the business case responsibly.

### Deliverables
- Maintain/update Tableau-compatible export.
- Keep synthetic and real-world data clearly identifiable.
- Run the final benchmark suite.
- Compare extraction accuracy by document type.
- Measure pilot review time where possible.
- Finalize cost and timeline documentation.
- Prepare architecture, benchmark, failure-mode, and live-demo slides.
- Clean repository and create logical commits.

### Exit criteria
- End-to-end demonstration works.
- Tableau dashboard reflects the latest validated export.
- Benchmark results are reproducible.
- Cost figures distinguish measurements from assumptions.
- Known limitations are documented.

## Adaptability / Risk Mitigation

| Risk | Early signal | Mitigation |
|---|---|---|
| Lab reports are much messier than DoCs | Extraction accuracy drops | Use reconciliation and expand targeted extraction tests before UI polish |
| Chemical tables are ambiguous | Legal limits mistaken for measurements | Require explicit measured-vs-statutory classification and human review |
| SKU matching is incomplete | Many unmatched products | Treat unmatched SKU as a visible data-quality condition; improve cross-reference |
| LangGraph adds complexity | No measurable improvement over baseline | Keep the graph bounded and compare it with the existing sequential pipeline |
| UI takes longer than expected | Backend is stable but front-end lags | Keep Streamlit intentionally lightweight |
| Benchmark is too small | High accuracy but limited coverage | Report sample size and limitations; add cases where time permits |

