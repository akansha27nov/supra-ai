# Real-World Data: Confirmed Failure Modes vs. Current Schema

**Method note:** these 5 documents are real, publicly-hosted compliance declarations from real companies (Enphase, ABB, Concens, Apogee, Delta) — not synthetic. This document originally contained a manual, hand-read prediction of failure modes; it has since been updated with **actual results from running `real_world_test.py` against the real downloaded PDFs**, using the live pipeline (real `extract_pdf_text()`, real LLM extraction, real rule engine).

## Confirmed result: 5 out of 5 real documents crash the current rule engine

Every single real document triggered the identical error: `strptime() argument 1 must be str, not None`. None of the 5 real certificates report an expiration date — the current code assumes one always exists and calls `datetime.strptime()` on it unconditionally.

## Confirmed result: 4 out of 5 misread the RoHS legal threshold as a measured value

| Document | `tested_lead_ppm` extracted | What it actually is |
|---|---|---|
| Enphase | 1000 | Legal threshold from a substance table, not a measurement |
| Concens | 1000 | Legal threshold |
| Apogee | 1000 | Legal threshold |
| Delta | 1000 | Legal threshold |
| ABB | `None` | Correctly extracted as absent — ABB's document has no substance table at all, just a blanket statement |

**Why this is the most important finding, not just a data quirk:** the date crash happened to stop execution before the lead check ran. But if the date field had been handled gracefully, the lead check (`1000 > 1000`) would have evaluated to **False** — meaning the system would have silently reported these certificates as passing the lead check, when in reality **no measurement was ever reported at all**. This is a false-compliance risk hiding behind a crash that happened to mask it.

## What worked correctly (worth stating honestly, not just the failures)

- `issuing_lab` and `lab_accreditation_id` were correctly extracted as `None` across all 5 documents — the LLM did not fabricate a fake lab or accreditation ID when none was present. All 5 are genuine manufacturer self-declarations, and extraction reported that honestly.
- `certificate_id` was correctly `None` for 3 of 5 documents where no such identifier genuinely exists in the source text, rather than being invented.
- Supplier names, standards cited, and issue dates (where present) were all extracted accurately.

## What this means for the LangGraph design

The two confirmed failure modes map directly onto the two things `langgraph_design_spec.md` was already designed to fix:

1. **The crash** → the rule engine needs to treat a missing expiration date as "not applicable" (skip the expiry check) rather than assuming absence is invalid input.
2. **The threshold/measurement confusion** → this is exactly what the `reconcile` node's targeted re-read ("is this number a measured result or a legal limit?") is for. This confirmed result is strong evidence that step is necessary, not speculative design.

## Immediate low-effort fix available before the full LangGraph build

A quick defensive patch — treat `None` expiration/lead values as "skip this check, flag as unverifiable" instead of crashing — would already prevent the crash and the silent false-compliance risk, without requiring the full agentic rebuild. Worth doing as an immediate fix regardless of LangGraph timeline, since it's the difference between "the system crashes on real data" and "the system correctly says it can't verify this and asks for human review" — a much better failure mode to show anyone who asks.

