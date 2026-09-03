# POC Documentation — Supra AI Compliance Document Auditor (Round 2)

## 1. Tools Used

| Tool | Role |
|---|---|
| **n8n** | No-code/low-code workflow orchestration (form trigger, LLM calls, conditional routing, integrations) |
| **OpenAI (gpt-4o-mini)** | Structured document-field extraction and gap-notice drafting |
| **Notion** | Record-keeping database (master registry + high-risk review queue) |
| **Telegram** | Human-reviewer alerting for high-risk records |

This is the same tool set as the Round 1 POC — no new integrations were added for Round 2. The change is a new capability inside the existing workflow, not a new platform.

## 2. What This POC Demonstrates

A supplier certificate PDF is submitted through a web form. The workflow:

1. Extracts raw text from the PDF.
2. Uses an LLM to parse the text into structured fields (product name, certificate ID, supplier, lab, dates, standards, measured lead concentration).
3. Matches the extracted product against an internal SKU catalog and loads that SKU's mandatory-standards ruleset.
4. Runs a deterministic rule-based audit (expiry check, missing-standard check, chemical-threshold check, lab-accreditation check) and produces a 0–100 priority score.
5. Routes based on that score:
   - **Score ≥ 50 (high risk):** drafts a supplier gap-notice email, sends a Telegram alert (now including that draft) to a human reviewer, and logs the record to a Notion review queue.
   - **Score < 50:** logs the record to a standard Notion registry.
6. All terminal paths converge and are flattened into a row for BI/warehouse export.

## 3. Round 1 → Round 2 Evolution

### What existed in Round 1

The original workflow proved that a document could be read by an LLM, scored by a deterministic rule engine, and routed to a human reviewer when it crossed a risk threshold. It stopped there: a high-risk record produced an alert and a log entry, but nothing was drafted for the supplier — a human still had to write the corrective-action email from scratch after being notified.

### What changed for Round 2

This is the same underlying hypothesis and the same workflow, extended with the one capability the Round 2 MVP made central: **generating a supplier-facing gap notice from the actual rule-engine findings**, not just alerting that a problem exists.

A new node, **`Draft Gap Notice`**, was inserted on the high-risk branch between `IF High Risk Router` and `Telegram High-Risk Alert`. It takes the same `flagged_issues` list the rule engine already produces and drafts a short corrective-action email addressed to the supplier, using only the findings that were actually triggered — no invented content. That draft is now included directly in the Telegram alert reviewers already receive[, and logged alongside the record in the Notion high-risk queue].

This mirrors, at POC scale, the Gap Notice lifecycle built out fully in the Round 2 MVP (draft → edit → approve → send, backed by real persistence and an audit trail). The POC does not attempt that full lifecycle — it shows the single most representative new capability: **turning a rule violation into a draft corrective-action communication automatically**, which is the piece that was entirely absent in Round 1.

Everything else in the workflow (extraction, SKU matching, rule scoring, Notion logging, Telegram alerting, BI export) is unchanged from Round 1 and is documented in `n8n/workflow_documentation.md`.

## 4. Updated Workflow Architecture

```
[n8n Form Trigger: PDF upload]
        │
[Extract PDF Text]
        │
[Basic LLM Chain (GPT-4o-mini): structured field extraction]
        │
[Parse Extracted JSON]
        │
[Auto SKU Matcher & Rule Loader]
        │
[Compliance Engine & Priority Scoring]
        │
[Notion – Search Existing Cert]
        │
[IF Record Exists?]
        │
   ┌────┴─────┐
  TRUE       FALSE
   │           │
[Notion –    [IF High Risk Router (score ≥ 50)]
 Update             │
 Existing    ┌──────┴──────┐
 Record]    TRUE          FALSE
             │              │
      [Draft Gap Notice]  [Notion Master
             │              Registry
      [Telegram             (Standard
       High-Risk             Review)]
       Alert]                │
             │               │
      [Notion High-          │
       Risk Queue]           │
             │               │
             └───────┬───────┘
                     |
      [Merge Terminal Branches (append, 3 inputs)]
                      │
             [Format for Tableau Export]
```

**New node added:** `Draft Gap Notice` (`@n8n/n8n-nodes-langchain.chainLlm`, gpt-4o-mini), inserted between `IF High Risk Router` and `Telegram High-Risk Alert`.

**Existing nodes modified:**
- `Telegram High-Risk Alert` — message template now includes the drafted gap notice.
- [`Notion High-Risk Queue` — added a `Gap Notice Draft` rich-text property, if implemented.]

All other nodes are unchanged from the Round 1 workflow.

## 5. New Node Detail — Draft Gap Notice

**Type:** Basic LLM Chain (same pattern as the existing extraction node), gpt-4o-mini via OpenAI Chat Model.

**Input:** `flagged_issues`, `supplier_name`, `certificate_id`, and `status` from the `Compliance Engine & Priority Scoring` node's output — the same rule-engine findings the Telegram alert already uses, so the draft cannot cite an issue the deterministic rules didn't actually find.

**Prompt (paraphrased):** instructs the model to act as a procurement compliance officer, write a concise (under 150 words) corrective-action email to the named supplier listing only the flagged issues provided, request specific supporting documentation, and not invent any information not present in the input.

**Output:** plain-text email body, referenced downstream as `{{ $('Draft Gap Notice').item.json.text }}`.

## 6. What This Proves (Feasibility)

Carried over from Round 1, still true:
- Real API keys wired and working across three services (OpenAI, Notion, Telegram) — not a mockup.
- LLM extraction reliably returns structured, parseable JSON from unstructured PDF text.
- A genuine rule engine (not an LLM opinion) makes the pass/flag/reject decision; the LLM is used only for extraction and, now, drafting — never for the compliance decision itself.
- A real human-in-the-loop escalation path fires conditionally on a defined threshold, not on every record.

New for Round 2:
- The same rule-engine findings that trigger a human alert can also drive a grounded, non-hallucinated draft communication, with no additional data source — proving the "evidence → draft" pattern the MVP's Gap Notice lifecycle depends on works even in a no-code setting.

## 7. What This Does *Not* Prove — Limits vs. Production (and vs. the Round 2 MVP)

Carried over from Round 1:
- SKU matching is heuristic (filename/keyword matching), not robust entity resolution.
- No retry/error handling on LLM extraction failures.
- Single fixed Notion database and a hardcoded SKU catalog, not a real PIM/ERP integration.
- No data retention/PII handling policy implemented at the POC level (see `compliance/gdpr_documentation.md` for the Round 2 treatment of this).
- Priority-scoring thresholds are illustrative, not calibrated against historical outcomes.

New limits specific to the gap-notice capability:
- **The draft is never persisted, edited, approved, or sent from here.** It exists only inside a Telegram message[/Notion field] for a single run. The full lifecycle (persist → human edit → approve → send, with an audit trail and status tracking) is what the Round 2 MVP actually implements — the POC intentionally only proves the drafting step works, not the full workflow around it.
- **No structured evidence linkage.** The MVP's Gap Notice carries the exact quote, page number, and section behind each finding; this POC's draft is generated from the flat `flagged_issues` text only, with no page/quote traceability.
- **No document-type branching.** The POC does not distinguish a lab report from a declaration of conformity the way the MVP's rule engine does; it applies one rule set regardless of document type.
- **Single-supplier, single-document assumption.** No handling for a supplier with multiple concurrent open gap notices.

## 8. How to Reproduce

1. Import `poc/workflow_round2.json` into n8n (this is the updated Round 2 export; the original Round 1 workflow remains at `n8n/Supra AI - PDF-Only Compliance Document Auditor.json`, unmodified, for comparison).
2. Configure credentials: OpenAI API key, Notion integration token (with access to the target database), Telegram bot token + chat ID.
3. Set the Notion database ID in each Notion node to a database with at minimum: a title property (Certificate ID), `Supplier` (rich text), `Priority Score` (number), `Status` (status/select), `Flagged Issues` (rich text)[, `Gap Notice Draft` (rich text) if that property was added].
4. Activate the form trigger and upload a sample certificate PDF that will score ≥ 50 (e.g. one with a missing standard or an expired certificate) to exercise the new node.
5. Inspect the `Draft Gap Notice` node's output in the execution log, and confirm the drafted email appears in the resulting Telegram message.

## 9. Screenshots

See `poc/screenshots/` — `01_draft_gap_notice_node_config.png`, `02_telegram_alert_with_draft.png`, `03_workflow_overview.png`.
