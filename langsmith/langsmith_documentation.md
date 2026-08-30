# LangSmith Monitoring Documentation

## What was monitored

Every certificate audit run through `langsmith/trace_sample.py` is traced end to end in LangSmith, under the project `supra-ai-compliance`. Each of the 7 real certificate PDFs in the evaluation set produces one parent trace (`audit_certificate`), with two nested child spans:

- `certificate_information_extraction` — the LLM call that reads raw PDF text and returns structured fields (certificate ID, supplier, lab, dates, standards found, lead concentration)
- `compliance_screening` — the deterministic rule engine that takes those structured fields and produces a PASS/FLAGGED/REJECTED status, a 0–100 priority score, and a list of flagged issues

This nested structure means a single trace shows the complete story for one certificate: what raw text went in, what the LLM extracted from it, what rules were applied, and what decision came out — the full chain is inspectable, not just the final answer.

## Why this setup, specifically

The core transparency concern this project is built around — leadership's fear of AI as an unexplainable black box — is addressed directly here: the LLM is used *only* for extracting fields from unstructured text, never for making the compliance decision itself. The decision (PASS/FLAGGED/REJECTED and the priority score) comes from an auditable, deterministic rule engine that anyone can read and reason about, with severity constants and thresholds defined in code, not hidden inside a model. LangSmith's trace view makes this split visible: you can see exactly where the LLM's job ends and the rules engine's job begins, which is the evidence a skeptical stakeholder would want before trusting an automated compliance decision.

## What the dataset shows

`data/ground_truth.json` contains 7 labeled certificates spanning every decision path the rule engine can take:

| File | Expected outcome | What it tests |
|---|---|---|
| cert_02_expired_elec.pdf | REJECTED / 90 | Expiry check |
| cert_04_valid_wireless_earbuds.pdf | PASS / 10 | Clean baseline case |
| cert_05_missing_red_smartwatch.pdf | FLAGGED / 75 | Missing safety-critical standard (RED Directive) |
| cert_06_excess_lead_powerbank.pdf | REJECTED / 95 | Lead-concentration threshold breach |
| cert_07_suspicious_lab_monitor.pdf | REJECTED / 85 | Suspicious/unrecognized lab accreditation |
| cert_08_expiring_soon_usb_hub.pdf | FLAGGED / 60 | Expiring-within-30-days check |
| cert_09_valid_smart_speaker.pdf | PASS / 10 | Clean baseline case (different SKU) |

Running `python langsmith/trace_sample.py` executes the real pipeline (real PDF text → real LLM extraction → real rule engine) against all 7 and prints an expected-vs-actual comparison.

## Result

**7/7 (100%) agreement** between the pipeline's output and the labeled ground truth, using the real LLM extraction step (not a logic-only simulation).

## Model used

Extraction runs on **GPT-4.1-mini**, chosen for its more reliable structured-JSON output compared to GPT-4o-mini, at a modest cost difference that's immaterial at this project's volume (see `cost_analysis.md` for per-audit API cost, calculated at GPT-4.1-mini's published rate).

## Latency observed (measured, from LangSmith)

Full audit (`audit_certificate` parent trace, extraction + screening combined): **~2.27s average, range 2.13s–2.57s** across the 7 certificates in the evaluation set.

This is almost entirely extraction latency — the LLM call to structure raw certificate text into JSON. `compliance_screening` itself completes in under 0.01s, since it's pure deterministic Python logic with no external API call. In other words: essentially all of the system's latency budget is spent on the one step that talks to an outside model, and the actual compliance decision is instant once the structured data exists — a useful detail to point out in the presentation, since it reinforces that the "thinking" part of this system is fast, auditable code, not a slow model doing the reasoning.

At ~2.3s per certificate, a batch of 500 certificates (the volume referenced in the cost/timeline estimate) would take roughly 19 minutes sequentially, or a few minutes with reasonable parallelization.

## How to reproduce

1. Install dependencies: `pip install langsmith openai python-dotenv pypdf`
2. Set `OPENAI_API_KEY` and LangSmith credentials (`LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`) in `.env`
3. Ensure `data/skus.json`, `data/ground_truth.json`, and the 7 PDFs (in `data/sample_pdfs/`) are present
4. Run `python langsmith/trace_sample.py`
5. View traces at smith.langchain.com under the `supra-ai-compliance` project
