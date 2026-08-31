# Agentic Extraction (LangGraph) — Design Spec

## Why this replaces the single-shot extraction call

The current `extract_certificate_data()` is one LLM call that must return every schema field every time. Real-world testing (see `failure_mode_analysis.md`) shows this forces false precision: when a field genuinely doesn't apply (no expiration date on an open-ended self-declaration, no measured lead ppm on a threshold-table document), a single-shot call has no way to say so — it guesses. The graph below adds exactly one capability the current pipeline lacks: **the ability to say "not applicable" or "not stated" instead of inventing a value**, and to distinguish a *measured result* from a *legal threshold* when both mention the same substance.

## Graph structure

```
                    ┌─────────────┐
                    │   extract   │  (same LLM call)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  classify   │  (lab_test_report vs
                    │  doc_type   │  manufacturer_self_declaration)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  validate   │  for each schema field: present,
                    │   fields    │  absent-but-expected, or absent-
                    └──────┬──────┘  and-appropriate-for-this-doc-type?
                           │
              ┌────────────┴────────────┐
              │                         │
       all required fields        Missing / ambiguous
       resolved (present OR             |
       correctly absent)                | 
              │                         | 
              │                         │
              │                  ┌──────▼──────┐
              │                  │  reconcile  │  targeted re-read:
              │                  │             │  "is this number a
              │                  │             │  measured result or
              │                  │             │  a legal limit?" (Max 2 retries)
              │                  └──────┬──────┘
              │                         │
              │              resolved ──┴── still ambiguous
              │                 │              │
              │                 ▼              ▼
              │           (loop back     ┌─────────────┐
              │            to validate)  │ flag_for_   │
              │                          │human_review │
              │                          └─────────────┘
              ▼
       ┌─────────────┐
       │ rule_engine │  
       │             │
       └─────────────┘
```

## State schema

```python
from typing import TypedDict, Literal

class AuditState(TypedDict):
    file_name: str
    raw_text: str
    doc_type: Literal["lab_test_report", "manufacturer_self_declaration", "unknown"]
    extracted: dict            # same fields as today
    field_status: dict         # per-field: "present" | "absent_expected" | "absent_appropriate" | "ambiguous"
    reconciliation_attempts: int
    needs_human_review: bool
    review_reason: str | None
```

## Key design decisions (and why)

- **`classify_doc_type` runs before validation, not after.** A self-declaration and a lab test report have genuinely different valid shapes — a self-declaration with no expiration date isn't a defect, it's normal. Validating against one fixed schema regardless of document type is exactly what produces false precision. Classifying first lets `validate_fields` apply different expectations per type.
- **`reconcile` is capped at 2 attempts, then routes to human review — it never loops indefinitely.** This matters for cost and latency (each reconciliation attempt is another LLM call) and, more importantly, for honesty: if the agent can't resolve an ambiguity after a second targeted look, the right answer is "flag it," not "keep guessing until something looks plausible."
- **The rule engine itself is untouched.** This is deliberate, not a shortcut — per the earlier discussion on agentic scope, the *decision* stays deterministic and auditable; only the *extraction* step gets agentic capability. The graph's whole job is handing the rule engine clean, honestly-labeled data — including "this field is not applicable" as a legitimate value, not a gap to paper over.
- **`flag_for_human_review` is a first-class outcome, not an error path.** A document that legitimately can't be auto-resolved (e.g., Apogee's RoHS Annex III cable exemption) should route to a person, exactly like a FLAGGED/REJECTED audit result does today — this is additive to the existing human-in-the-loop design, not a new category of failure.

## What changes in the rule engine's inputs (not its logic)

Two new legitimate field states the rule engine needs to accept, in addition to real values:

- `tested_lead_ppm: null` with `field_status["tested_lead_ppm"] = "absent_appropriate"` → skip the lead-threshold check silently (this document type doesn't report measured values) rather than treating `null` as `0` (which would currently and incorrectly always pass)
- `expiration_date: null` with the same "absent_appropriate" status for open-ended self-declarations → skip the expiry check rather than crashing on `datetime.strptime(None, ...)`, which is what today's code would actually do if it hit one of these 5 real documents right now

## Implementation note

This is a genuine LangGraph build (nodes, conditional edges, a cycle with a bounded retry), not a relabeled chain — worth being precise about that distinction in the Round 2 write-up, since "agentic" gets used loosely and this design earns the term specifically because of the conditional branching and bounded reconciliation loop, not just because multiple LLM calls happen in sequence.
