# n8n POC Documentation — Supra AI: PDF Compliance Document Auditor

## What it does

A supplier submits a test certificate PDF (e.g. an RoHS/CE lab report for a product SKU) through a web form. The workflow extracts the text, uses an LLM to parse it into structured fields (product name, certificate ID, supplier, lab, expiry date, tested lead concentration, standards covered), matches it against an internal SKU catalog and that SKU's mandatory compliance rules, runs a rule-based audit (expiry check, missing-standard check, chemical-threshold check, lab-accreditation check), and scores it with a 0–100 priority score. Records above the risk threshold trigger a Telegram alert to a human reviewer; everything is logged to Notion, and low-risk/registry records are additionally formatted for downstream BI export.

## Why this fits the use case

This is the "quality/risk pillar" data feed for the Engineering AI Control Tower: it demonstrates the same core mechanism the Control Tower's PR-review use case relies on — LLM-based structured extraction and rule-based scoring applied to an unstructured document, with a clear pass/flag/reject outcome and a human-in-the-loop escalation path for anything the automated layer can't confidently resolve on its own. It's also a clean, self-contained proof that the "AI reads an artifact → flags risk → routes to the right human or system" pattern is real and working end to end, not just theoretical.

## Actual workflow architecture (as implemented, post-fix)

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
[Notion –    [IF High Risk Router (score ≥ 70)]
 Update             │
 Existing    ┌──────┴──────┐
 Record]    TRUE          FALSE
             │              │
      [Telegram      [Notion Master
       High-Risk       Registry
       Alert]          (Standard
             │          Review)]
      [Notion High-           │
       Risk Queue]            │
             │                │
             └───────┬────────┘
                     |
      [Merge Terminal Branches (append, 3 inputs)]
                      │
             [Format for Tableau Export]
```

All three terminal paths — record update, high-risk/Telegram, and standard/Master Registry — now converge through a single `Merge Terminal Branches` node before reaching the export step, matching the original target-state design.

## Node-by-node summary

| Node | Purpose |
|---|---|
| n8n Form Trigger | Upload portal for supplier certificate PDFs |
| Extract PDF Text | Converts PDF binary to raw text |
| Basic LLM Chain (+ OpenAI Chat Model, gpt-4o-mini) | Extracts structured fields from raw certificate text into a defined JSON schema |
| Parse Extracted JSON | Cleans/parses the LLM's JSON output, stripping markdown fencing if present |
| Auto SKU Matcher & Rule Loader | Matches the extracted product to an internal SKU catalog (by filename pattern or fuzzy name match) and loads that SKU's mandatory-standards ruleset |
| Compliance Engine & Priority Scoring | Rule-based audit: expiry check, mandatory-standards check, lead-concentration threshold check, lab-accreditation check; produces a 0–100 priority score and a PASS/FLAGGED/REJECTED status |
| Notion – Search Existing Cert | Checks whether this certificate ID already has a record in the master Notion database |
| IF Record Exists? | Routes to update-existing vs. create-new |
| Notion – Update Existing Record | Updates score/status/issues on a pre-existing record (re-audit case) |
| IF High Risk Router | Routes new records by whether the priority score is ≥ 70 |
| Telegram High-Risk Alert | Sends a formatted alert with file, SKU, supplier, score, and flagged issues to a human reviewer |
| Notion High-Risk Queue | Logs the flagged/rejected record for human review |
| Notion Master Registry | Logs standard-review (lower-risk) records to the master database |
| Merge Terminal Branches | Reunites the three mutually-exclusive terminal paths (update-existing, high-risk, standard-review) into a single stream before export, since exactly one path fires per run |
| Format for Tableau Export | Flattens a record into a single row suitable for BI/warehouse export |

## What this proves (feasibility)

- Real API keys are wired and working across three services (OpenAI, Notion, Telegram) — not a mockup
- The LLM extraction step reliably returns structured, parseable JSON from unstructured PDF text
- A genuine rule engine (not just an LLM opinion) makes the pass/flag/reject decision, with the LLM used only for extraction — this is a deliberate transparency choice: the audit logic is auditable code, not an opaque model judgment
- A real human-in-the-loop escalation path exists and fires conditionally based on a defined threshold, not on every record

## What this does *not* prove / limits vs. production

- **SKU matching is heuristic** (filename regex + keyword overlap), not a robust entity-resolution system; it will mismatch on real-world messy filenames or unusual naming
- **No retry/error handling** on LLM extraction failures (e.g. a low-quality scan or non-English certificate) — a production version needs a fallback path, not a silent failure
- **Single fixed Notion database** and a hardcoded SKU catalog embedded directly in code (not pulled from a real product database) — fine for a proof of mechanism, not how this would be wired to a real PIM/ERP system
- **No data retention/PII handling policy implemented yet** — before production, any personal data in these documents (e.g. an individual's name on a lab report) would need to be addressed per GDPR (see `gdpr_documentation.md` in Round 2)
- **Priority scoring thresholds and point values are illustrative**, not calibrated against real historical outcomes — production tuning would need labeled historical audit data to validate false-positive/false-negative rates
- **The merge/export fix is reasoned through but not yet execution-tested** (see Known Issues below) — treat this as "should work" until confirmed by an actual end-to-end run of all three branches

## Known issues found and fixed during testing

- **Node-name reference mismatch**: `Notion Master Registry`'s `title` field referenced `$('Compliance Engine')`, a node that didn't exist — the actual node is named `Compliance Engine & Priority Scoring`. This was silently breaking the record title on every standard-review record. **Fixed** by correcting the node reference.
- **Field-mapping bug**: `Notion Master Registry`'s "Supplier" property was mapped to `extracted.certificate_id` instead of `extracted.supplier_name`, so the Supplier column would have shown the certificate ID twice. **Fixed** by correcting the source field.
- **Stale-property bug on re-audit**: `Notion – Update Existing Record` was reading `$json.property_priority_score`, `$json.property_status`, and `$json.property_flagged_issues` — property names that don't actually exist on a Notion search result (Notion's API nests properties under `properties.<Name>`, not a flat `property_` prefix). This would have written empty/undefined values every time a certificate was re-submitted. **Fixed** by pulling the freshly computed score, status, and flagged issues directly from the `Compliance Engine & Priority Scoring` node instead.
- **Latent bug in the export step**: `Format for Tableau Export` read `$input.first().json` and expected `.file_name`, `.extracted`, and `.audit_result` on it — but its immediate predecessor is always a Notion create/update node, which returns a Notion page object (`id`, `properties`, `url`...), not the pipeline's enriched data shape. This would have thrown a runtime error the first time any branch actually reached this step, including the one branch that was already wired. **Fixed** by having it read directly from the `Compliance Engine & Priority Scoring` node by name, independent of which branch it arrives from.
- **Branch convergence gap**: the high-risk (Telegram) branch and the update-existing branch previously ended without reconnecting to the export step, so only standard-review records ever reached the warehouse/BI export. **Fixed** by adding a `Merge Terminal Branches` node (append mode, 3 inputs) that reunites all three terminal paths before `Format for Tableau Export` runs.
- **Binary-field naming mismatch** (found during initial testing on an earlier iteration of this workflow pattern): the PDF extraction step originally referenced a binary property name that didn't match what the Form Trigger produced at runtime, due to a mismatch between the form field's internal name and its display label. Resolved by aligning the binary property name to the form's actual output key.

All fixes have been applied to the version of the workflow submitted with this documentation. **Not yet independently verified**: each of the three terminal paths (new low-risk certificate, new high-risk certificate, and re-submission of an existing certificate ID) should be run at least once end-to-end before this is presented live, since the merge/export fix has been reasoned through by code review but not yet executed against real n8n runtime behavior.

## How to reproduce

1. Import `Supra_AI_-_PDF-Only_Compliance_Document_Auditor.json` into n8n
2. Configure credentials: OpenAI API key, Notion integration token (with access to the target database), Telegram bot token + chat ID
3. Set the Notion database ID in each Notion node to a database with at minimum: a title property (used as Certificate ID), `Supplier` (rich text), `Priority Score` (number), `Status` (status/select), `Flagged Issues` (rich text)
4. Activate the form trigger and upload a sample certificate PDF
5. Inspect each node's output in the execution log to verify extraction, matching, and scoring at each step
