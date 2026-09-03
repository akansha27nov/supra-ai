# Supra AI — MVP Documentation

## 1. Purpose

Supra AI is a working AI-assisted supplier compliance screening MVP for mid-sized consumer-electronics retailers. Instead of a compliance team manually reading every supplier PDF, the product extracts structured facts from the document, checks those facts against deterministic compliance rules and an internal SKU catalog, and surfaces a prioritised, evidence-linked finding for a human reviewer to act on.

The MVP demonstrates the complete product loop:

**Upload PDF → LLM extraction → field validation / reconciliation → SKU resolution → deterministic rule screening → reviewer decision → supplier gap notice**

This is the Round 2 working MVP — a FastAPI backend running a LangGraph extraction/screening pipeline, plus a Next.js frontend for reviewers. It is distinct from the n8n POC in `poc/` (see `poc/poc_documentation.md`) and from the Round 1 baseline in `n8n/`.

Live frontend: [`supra-ai`](https://supra-ai.netlify.app/) · Live API: [`api`](https://supra-ai.onrender.com/) — fill in once the deployments are finalised.

## 2. What the MVP demonstrates

The core AI capability actually runs end to end against real PDFs, not synthetic mocks. The MVP is not a static prototype.

It currently supports:

- LLM-based extraction of certificate fields — supplier, dates, standards tested, measured chemical values, and page/section-linked evidence quotes;
- explicit field-status tracking (`present` / `absent_expected` / `absent_appropriate` / `ambiguous`) rather than silently treating a missing field as a pass;
- a bounded reconciliation loop that re-runs targeted extraction up to twice before escalating to a human, instead of guessing or looping forever;
- SKU resolution against an internal catalog with an explicit `matched` / `unmatched` / `not_attempted` state;
- a deterministic rule engine covering expiry, mandatory-standard coverage, lead-ppm thresholds (with a two-tier self-declared-vs-lab-verified exemption check), and lab accreditation;
- a `APPROVED` / `FLAGGED` / `REJECTED` / `REQUIRES_HUMAN_REVIEW` decision with a 0–100 score, persisted with structured evidence, not just a flat summary;
- human review of every audited document, with the AI never making the final compliance call;
- generation, editing, approval, and sending of a supplier gap notice for `FLAGGED`/`REJECTED` documents, with the full lifecycle status-tracked;
- a best-effort internal Telegram notification when a gap notice is marked sent;
- full observability — every graph run is traced in LangSmith;
- an audit-scoped **Copilot Chat** that lets a reviewer ask natural-language questions about a single flagged case — grounded in that case's own evidence, never in outside knowledge, and never able to change the audit's decision.

## 3. Architecture

### Frontend

- Next.js (TypeScript)
- Hosted on Netlify (`mvp/frontend/netlify.toml`, `@netlify/plugin-nextjs`)
- Pages: `/` (upload + inspect a single audit), `/audits` (queue), `/audits/[id]` (detail — evidence viewer, review actions, gap-notice modal), `/analytics`

The frontend talks to the backend over HTTPS/JSON via `lib/api.ts`, pointed at `NEXT_PUBLIC_API_URL` (falls back to `http://localhost:8000/api` for local development).

### Backend

- FastAPI (`agent/server.py`)
- Hosted on Render
- Routes: `POST /api/audit` (run the pipeline on an uploaded PDF), `GET /api/logs` (read the ledger, joined with live gap-notice status), `PATCH /api/logs/{id}/review` (human approve/reject), `/api/gap-notice*` (full gap-notice lifecycle: create, get, edit, approve, send), `POST /api/logs/{id}/chat` (Audit Copilot — ask a question about a single audit, scoped to that record's own evidence)

### Database

- Postgres, hosted on Render (`agent/db.py`, via `DATABASE_URL`)
- `init_db()` creates both tables on every startup if they don't already exist
- Persisted objects:
  - `audit_ledger` — one row per audited document (decision, score, flags, SKU match, review status)
  - `gap_notices` — the full supplier gap-notice lifecycle, linked back to the audit that triggered it

This replaces the MVP's earlier flat-file persistence (`logs/master_audit_ledger.csv`, `data/gap_notices.json`), which did not survive Render's ephemeral disk across redeploys or restarts.

### AI / orchestration

- LangGraph (`agent/graph.py`) is used to construct the extraction/validation/screening state machine.
- OpenAI models power structured-output extraction, and gap-notice drafting.
- LangSmith tracing is enabled via `LANGSMITH_PROJECT` (and `LANGSMITH_TRACING=true`) in `.env` for prompt/output inspection, latency, and debugging. The legacy `LANGCHAIN_PROJECT`/`LANGCHAIN_TRACING_V2` names are also read by the SDK as aliases — keep only the `LANGSMITH_*` versions set in `.env` to avoid traces silently splitting across two differently-named projects.

### System diagram

```text
┌────────────────────┐            ┌────────────────────┐            ┌────────────────────┐
│      Next.js       │  ──HTTP──▶ │      FastAPI       │ ─LangGraph▶│   agent/graph.py   │
│   (mvp/frontend)   │  ◀──JSON── │ (agent/server.py)  │ ◀─pipeline─│ LLM + rule engine  │
│      Netlify       │            │       Render       │            │      pipeline      │
└─────────┬──────────┘            └──────────┬─────────┘            └────────────────────┘
          │                                  │
          │  POST /api/logs/{id}/chat        ▼
          │                       ┌────────────────────┐
          └──────────────────────▶│ Postgres (Render)  │
                                  │    audit_ledger    │
                                  │    gap_notices     │
                                  └──────────┬─────────┘
                                             │ read-only
                                             ▼
                                  ┌────────────────────┐
                                  │ agent/copilot.py   │
                                  │ Audit Copilot Chat │
                                  │ (reuses graph.py's │
                                  │  LLM client)       │
                                  └────────────────────┘
```

## 4. Core AI flows

### 4.1 Extraction

`extract_node` sends the raw PDF text to an LLM with structured output, pulling out supplier name, certificate/lab IDs, issue/expiration dates, standards tested, measured lead concentration, and an `evidence_links` list mapping each field to its exact quote and page number.

The extraction prompt is deliberately explicit about not confusing a statutory chemical limit with a measured lab result, and about determining `exemption_independently_verified` whenever a lead exemption is cited — this distinction matters directly to the rule engine (Section 4.4).

### 4.2 Validation and reconciliation

`validate_fields_node` classifies every extracted field's status given the document type — `present`, `absent_expected` (should be there but isn't), `absent_appropriate` (fine to be missing for this doc type), or `ambiguous` (present but not trustworthy, e.g. an unrecognised statutory threshold value).

`route_after_validation` is the safety gate: if any field is `absent_expected` or `ambiguous`, the graph loops back through `reconcile_node` for a targeted re-extraction — bounded to 2 attempts. After that, or if `doc_type` couldn't be classified at all, it routes to `flag_for_human_review_node` instead of silently guessing.

### 4.3 SKU resolution

`resolve_sku_node` matches the extracted product against the internal SKU catalog (`data/skus.json`). The result is always one of `matched`, `unmatched`, or `not_attempted` — an unresolved product is never dropped silently, it flows into the rule engine as its own condition.

### 4.4 Rule engine

`rule_engine_node` runs deterministic checks: certificate expiry (including an "expiring soon" window), missing mandatory standards (weighted by whether the missing standard is safety-critical), lead-ppm threshold against the SKU's own limit, and lab accreditation.

The lead-ppm check has a two-tier exemption path: a cited exemption that the lab **independently verified** is treated as a lighter `FLAGGED` finding, while a **self-declared, unverified** exemption is treated as a `REJECTED` violation — a self-declaration alone is not sufficient grounds to waive a measured excess.

Every violation carries a severity score; the aggregate score maps to `APPROVED` (< 50), `FLAGGED` (50–84), or `REJECTED` (≥ 85).

### 4.5 Human review and gap notices

The rule engine's output is a recommendation, not a final decision. A reviewer approves or overrides it via `PATCH /api/logs/{id}/review`. For `FLAGGED`/`REJECTED` documents, a reviewer can generate a supplier gap notice, edit the draft, approve it, and send it — with each state transition persisted in `gap_notices` and a best-effort Telegram alert fired when a notice is marked sent.

### 4.6 Observability

Every LangGraph run — extraction, reconciliation attempts, rule evaluation — is traced in LangSmith under `LANGSMITH_PROJECT`, so a reviewer or engineer can inspect exactly what the model saw and produced for any audited document.

### 4.7 Reliability and error handling

Every LLM call in the app — extraction, document classification, reconciliation, and gap-notice drafting — goes through a single shared policy in `agent/llm_reliability.py` rather than a bare `.invoke()`:

- **Transient failures are retried**, not surfaced to the user: rate limits, timeouts, connection errors, and OpenAI 5xx responses get up to 3 attempts with exponential backoff (1s, 2s, 4s).
- **Failures that a retry can't fix are not retried.** An authentication error (bad API key) is a configuration problem, not a traffic problem — it fails immediately with a message saying so. A structured-output validation failure — typically caused by a low-quality scan or otherwise unparseable document — also fails immediately, since retrying won't make a garbled document parse better on attempt two.
- **Every failure path ends in one clean, human-readable message** (`ExtractionFailedError`), never a raw stack trace surfaced to the reviewer.
- **A pre-flight check in `agent/server.py`** rejects PDFs with fewer than 40 extractable characters — the scanned-image-PDF case — with a specific `422` explaining why, before an LLM call is even attempted.
- **A failed extraction is never persisted as if it succeeded.** `/api/audit` and `/api/gap-notice` both catch `ExtractionFailedError` and return a `502` with the real reason; no row is written to the Postgres audit ledger for a document that never actually finished processing.

This behaviour is covered by `tests/test_llm_reliability.py` — retry-then-succeed, retry-exhaustion, and the two non-retryable paths (auth error, unparseable document) are each asserted directly.

### 4.8 Audit Copilot Chat

`agent/copilot.py` is a reviewer-facing investigation layer, not a second compliance engine. It sits strictly after the audit pipeline and never feeds back into it.

**Context assembly.** For a given `record_id`, the handler pulls that single row from `audit_ledger` (via a new `db.get_audit_record()`) plus its gap notice, if one exists, and serializes them into a compact case-context block: file/supplier/SKU/decision/score, each rule violation's code, severity, message, and evidence (`exact_quote`, `page_number`, `section`), and — when present — the gap notice's failed rules and corrective action. No other audit's data is ever included in that context.

**Grounding.** The system prompt instructs the model to answer only from the supplied case context, to quote evidence rather than paraphrase from outside knowledge, and to never use decision language ("approved," "compliant," "fine") — the Copilot describes what the rule engine found, it does not re-judge it. When a question falls outside the supplied evidence, the model is instructed to say so explicitly and the response carries `grounded: false`, which the UI surfaces as a visible caveat rather than presenting an ungrounded answer with the same confidence as a grounded one.

**Reliability.** The LLM call goes through the same `invoke_with_retry` / `ExtractionFailedError` path as every other LLM call in the app (Section 4.7) — a Copilot failure returns a clean `502` with a human-readable reason, the same as a failed extraction, rather than a raw stack trace or a silently broken chat panel.

**Reuse, not duplication.** The Copilot calls the same `llm` client instance `agent/graph.py` already constructs — one model configuration for the whole app, not a second one to keep in sync.

**Frontend.** `CopilotChatPanel.tsx` renders as a slide-over on the audit detail page, scoped to the currently open `RecordID`. It carries a persistent disclosure ("AI-generated answers grounded in this case's evidence only — not a compliance decision") and visually flags any `grounded: false` reply. The panel is keyed on `RecordID` so that navigating between audits — which does not always fully remount the page component — still resets the conversation, preventing one audit's chat history from leaking into another's context.

**Observability.** Every Copilot call is tagged `copilot_chat` and tracks `record_id` in its LangSmith metadata, landing in the same project as extraction and gap-notice runs (Section 4.6) — one audit trail across the whole system, not a separate untraced surface.

**Scope.** The Copilot is scoped to one audit record at a time; it does not currently support focusing on a single finding within a multi-finding audit (all findings for the record are included in context together), and it is read-only — there is no path from a chat turn back into `review_status`, `audit_ledger`, or the gap-notice store.

## 5. Repository structure (MVP-relevant paths)

```
agent/
├── server.py            # FastAPI app — all HTTP routes
├── graph.py              # LangGraph pipeline: extraction → rules → routing
├── db.py                  # Postgres persistence (audit ledger + gap notices)
├── schemas.py              # Pydantic models (extraction, rule violations, gap notice records)
├── gap_notice.py            # Gap notice generation + lifecycle transitions
├── gap_notice_store.py       # Gap notice CRUD against Postgres
├── copilot.py                 # Audit Copilot Chat — context assembly + grounded LLM call
├── telegram_dispatch.py       # Best-effort Telegram notification on gap-notice SENT
└── run_pdf.py                 # CLI runner

mvp/frontend/
├── app/page.tsx               # Upload + single-audit inspection
├── app/audits/page.tsx         # Audit queue
├── app/audits/[id]/page.tsx     # Audit detail: evidence viewer, review actions, gap-notice modal, Copilot trigger
├── components/CopilotChatPanel.tsx   # Audit Copilot Chat slide-over, keyed on RecordID
└── lib/api.ts, lib/exportUtils.ts    # API client (incl. sendCopilotMessage), CSV export

tests/                          # pytest suite
```

## 6. How to run locally

### Backend

```bash
git clone <repo>
cd supra-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in OPENAI_API_KEY and DATABASE_URL at minimum
uvicorn agent.server:app --reload --port 8000
```

The API is now at `http://localhost:8000`. `init_db()` creates the Postgres tables automatically on first run if they don't exist — point `DATABASE_URL` at any Postgres instance (local, or Render's).

### Frontend

```bash
cd mvp/frontend
npm install
npm run dev
```

The app is now at `http://localhost:3000`, pointed at `http://localhost:8000/api` by default (see `lib/api.ts`); set `NEXT_PUBLIC_API_URL` to point at a deployed backend instead.

### Verify it's working

```bash
pytest tests/ -q
```

Expect all tests to pass. If `reportlab` isn't installed, one PDF-generation test is skipped rather than failing — that's expected.

## 7. Deployment

### Backend → Render

**Service type:** Web Service, Python environment.

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn agent.server:app --host 0.0.0.0 --port $PORT` |
| Root directory | repo root (imports are `agent.*`, resolved relative to the repo root — do not set a subdirectory) |
| Environment variables | Same as `.env` (Section 8) — set `OPENAI_API_KEY` and `DATABASE_URL` in Render's dashboard, not in a committed file |

**CORS.** `agent/server.py` currently sets `allow_origins=["*"]` (flagged inline as adjust-for-production). This works immediately but should be tightened to the deployed frontend's origin once that's stable.

### Database → Render Postgres

Provision a Render Postgres instance and attach its connection string as `DATABASE_URL` on the backend service. Render sometimes provides `postgres://`; `agent/db.py` normalises this to `postgresql://` for psycopg2.

### Frontend → Netlify

Builds from `mvp/frontend` (`netlify.toml`: `npm run build`, publish `.next`, via `@netlify/plugin-nextjs`). Set `NEXT_PUBLIC_API_URL` to the Render backend URL in Netlify's environment variables so the frontend stops pointing at `localhost:8000`.

## 8. Environment configuration

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | **Yes** | Powers all LLM extraction and gap-notice drafting calls |
| `DATABASE_URL` | **Yes** | Postgres connection string for the audit ledger + gap notices |
| `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LANGSMITH_ENDPOINT` (EU accounts only, for `ENDPOINT`) | No | LangSmith tracing; pipeline still runs without it, just unobserved. The legacy `LANGCHAIN_TRACING_V2`/`LANGCHAIN_PROJECT` names are also read by the SDK — set only the `LANGSMITH_*` versions in `.env` to avoid traces silently splitting across two differently-named projects |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | No | Enables the gap-notice-sent internal Telegram alert; silently skipped (`telegram_notification: "not_configured"`) if absent |
| `NOTION_API_KEY`, `NOTION_DATABASE_ID` | No | Used by the n8n POC / `langsmith/trace_sample.py` evaluation scripts, not by the FastAPI MVP itself |

Secrets must not be committed to the repository — see `.env.example` for the full template.

## 9. Testing and observability

The pytest suite covers:

- graph routing (`route_after_validation` — reconcile vs. resolve vs. escalate to human review);
- rule-engine decisions (expiry, standards, lead-ppm thresholds including both exemption tiers, lab accreditation, SKU match);
- schema validation and data-integrity checks;
- the audit-ledger CLI runner.

LangSmith tracing can be enabled for any of the above via `LANGSMITH_TRACING=true`. Every extraction, reconciliation attempt, rule evaluation, and Copilot chat turn is inspectable per run once tracing is on — Copilot runs are tagged `copilot_chat` and carry `record_id` in their metadata, landing in the same project as the rest of the pipeline rather than a separate, unlinked trace stream.

## 10. Current limitations

- **No dedicated non-English-document detection.** LLM calls retry on transient failures and fail cleanly (via `agent/llm_reliability.py`) rather than returning bad data — see Section 4.7 — but a non-English document that still produces *parseable*, low-quality structured output won't be flagged as such; it just scores whatever the extraction actually returned. A language-detection pass (e.g. `langdetect`) is a scoped next step, not yet built.
- **No auth.** Any client that can reach the API can call every endpoint. Scoped for MVP.
- **SKU catalog is a static JSON file** (`data/skus.json` / `data/real_skus.json`), not a live PIM/ERP integration.
- **Audit Copilot Chat is audit-scoped, not finding-scoped.** A reviewer can ask about any finding on the open audit, but there's no dedicated "focus on this one finding" mode yet (`docs/implementation_docs/copilot_chat.md` describes this as a recommended future refinement, not a current AC). All of a record's `FlagsDetail` is included in context together.
- **Copilot responses are not yet covered by an automated grounding-evaluation harness.** Manual testing against real flagged records confirms grounded, evidence-cited answers; a repeatable eval (e.g. a small labelled Q&A set scored for grounding) is a scoped next step, not yet built.

## 11. Relationship to the other deliverables

- **Round 1 POC** (`n8n/`) — the original workflow, unmodified, kept as a baseline for comparison.
- **Round 2 POC** (`poc/`) — the same n8n workflow extended with one new capability (gap-notice drafting) to show evolution without duplicating MVP depth — see `poc/poc_documentation.md`.
- **This MVP** — the real, running product. Everything the POC gestures at (draft generation) is here with full Postgres persistence, an editable/approvable/sendable lifecycle, structured evidence, and a proper reviewer UI.
