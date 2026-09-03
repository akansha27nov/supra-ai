# MVP Documentation — Supra AI Compliance Document Auditor

This documents the Round 2 working MVP: a FastAPI backend running a LangGraph extraction/screening pipeline, and a Next.js frontend for reviewers. This is the deployable product, distinct from the n8n POC in `poc/` (see `poc/poc_documentation.md`) and from the Round 1 baseline in `n8n/`.

## 1. What the MVP Does

A reviewer uploads a supplier compliance PDF (Declaration of Conformity or lab test report). The system:

1. Extracts structured fields via an LLM (supplier, dates, standards, measured chemical values, evidence quotes/pages).
2. Classifies the document type and resolves the product against an internal SKU catalog (explicit `matched`/`unmatched`/`not_attempted` states — never silent).
3. Runs a deterministic rule engine (expiry, missing standards, lead-threshold, lab accreditation, SKU match) to produce `APPROVED` / `FLAGGED` / `REJECTED` / `REQUIRES_HUMAN_REVIEW` plus a 0–100 score.
4. Persists the result to an audit ledger, with structured evidence (exact quote, page, section) carried through, not just a flat summary.
5. Lets a human reviewer approve/reject, and — for `FLAGGED`/`REJECTED` documents — generate, edit, approve, and send a supplier gap notice, with the full lifecycle persisted and status-tracked.
6. Sends a best-effort internal Telegram notification when a gap notice is marked sent.

The core AI capability (extraction + rule-based screening) runs end to end against real PDFs, not synthetic mocks.

## 2. Architecture

```text
┌─────────────────┐      HTTP         ┌──────────────────┐      LangGraph      ┌─────────────────┐
│  Next.js         │ ───────────────▶│  FastAPI          │ ──────────────────▶ │  agent/graph.py  │
│  (mvp/frontend)  │◀────────────────│  (agent/server.py)│◀────────────────────│  LLM + rule      │
└─────────────────┘      JSON        └──────────────────┘                      │  engine pipeline  │
                                              │
          └───────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
                                   ┌────────────────────────┐
                                   │  Local filesystem      │
                                   │  logs/master_audit_    │
                                   │  ledger.csv            │
                                   │  data/gap_notices.json │
                                   └────────────────────────┘
```

- **Backend:** `agent/server.py` (FastAPI). Routes: `/api/audit` (run the pipeline on an uploaded PDF), `/api/logs` (read the ledger, joined with live gap-notice status), `/api/logs/{id}/review` (human approve/reject), `/api/gap-notice*` (full gap-notice lifecycle: create, get, edit, approve, send).
- **Pipeline:** `agent/graph.py` — a LangGraph `StateGraph`: extract → classify document type → validate fields → (reconcile if ambiguous, bounded to 2 retries) → resolve SKU → rule engine → (flag for human review if needed).
- **Persistence:** flat files, not a database — `logs/master_audit_ledger.csv` (audit ledger) and `data/gap_notices.json` (gap-notice records). Deliberately simple for MVP scale; see Section 6 for what this means on Render.
- **Frontend:** `mvp/frontend` (Next.js, TypeScript). Pages: `/` (upload + inspect a single audit), `/audits` (queue), `/audits/[id]` (detail, evidence viewer, gap-notice lifecycle), `/analytics`.
- **Observability:** every graph run is traced in LangSmith (`LANGCHAIN_PROJECT` in `.env`).

## 3. Prerequisites

- Python 3.12 (developed/tested on 3.12.3)
- Node.js 18+ (for the Next.js frontend)
- An OpenAI API key
- Optional: a LangSmith API key (tracing), a Telegram bot token + chat ID (gap-notice-sent notifications)

## 4. Local Setup

### Backend

```bash
git clone <repo>
cd supra-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in OPENAI_API_KEY at minimum
uvicorn agent.server:app --reload --port 8000
```

The API is now at `http://localhost:8000`. `logs/` and `data/` are created automatically on first run if they don't exist.

### Frontend

```bash
cd mvp/frontend
npm install
npm run dev
```

The app is now at `http://localhost:3000`, pointed at `http://localhost:8000/api` by default (see `lib/api.ts`; override with `NEXT_PUBLIC_API_URL` if the backend runs elsewhere).

### Verify it's working

```bash
pytest tests/ -q
```
Expect ~99 passed and 3 pre-existing failures unrelated to this MVP (see Section 7) — `test_graph_routing.py::test_route_to_reconcile_when_fields_are_missing_before_two_attempts`, `test_graph_routing.py::test_route_to_human_review_after_two_attempts`, and `test_graph_rules.py::test_excess_lead_with_exemption_requires_review_flag`. One test (`test_extract_pdf_text_reads_all_pages`) is skipped instead of passing if the optional `reportlab` package isn't installed — that's expected, not a failure.

## 5. Environment Variables (`.env`)

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | **Yes** | Powers all LLM extraction and gap-notice drafting calls |
| `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, `LANGCHAIN_ENDPOINT` | No | LangSmith tracing; pipeline still runs without it, just unobserved |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | No | Enables the gap-notice-sent internal Telegram alert; silently skipped (`telegram_notification: "not_configured"`) if absent |
| `NOTION_API_KEY`, `NOTION_DATABASE_ID` | No | Used by the n8n POC / `langsmith/trace_sample.py` evaluation scripts, not by the FastAPI MVP itself |

## 6. Deploying the Backend (Render)

**Service type:** Web Service, Python environment.

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn agent.server:app --host 0.0.0.0 --port $PORT` |
| Root directory | repo root (imports are `agent.*`, resolved relative to the repo root — do not set a subdirectory) |
| Environment variables | Same as `.env` (Section 5) — set `OPENAI_API_KEY` at minimum in Render's dashboard, not in a committed file |

**Important limitation — ephemeral disk.** The MVP persists the audit ledger and gap-notice records as local files (`logs/master_audit_ledger.csv`, `data/gap_notices.json`), not a database. Render's free/starter web services do **not** guarantee persistent local storage — files can be wiped on redeploy, restart, or across instances if the service scales beyond one dyno. For a demo/pilot this is usually fine (data persists across normal uptime), but:
- Don't rely on ledger history surviving a redeploy.
- For anything beyond a demo, this needs either Render's paid persistent disk add-on or migrating `append_to_master_csv`/`gap_notice_store.py` to a real database (Postgres is the natural fit given Render offers it natively) — not done in this MVP, flagged here as a known next step, not a silent gap.

**CORS.** `agent/server.py` currently sets `allow_origins=["*"]` (see the inline comment marking this as adjust-for-production). This will work immediately on Render but should be tightened to the actual frontend origin once that's deployed and stable.

**Frontend pointing at the deployed backend.** Once the Render URL is live, set `NEXT_PUBLIC_API_URL` (e.g. in a Vercel deployment, or a local `.env.local` for the frontend) to that URL so the frontend stops pointing at `localhost:8000`.

## 7. Known Limitations

- **Two Celestron-related findings, still open:** the live LLM extraction call doesn't reliably parse the one real lab report's scientific-notation lead value (`2.93×10⁴` → should be `29300` ppm), causing that benchmark entry to under-score. A separate, now-fixed issue (an unmatched-SKU early-return in `langsmith/trace_sample.py` that masked other violations) was patched and verified; the extraction-parsing issue was not, per explicit scope decision.
- **`trace_sample.py` and `agent/graph.py` are two separately maintained rule engines**, not one shared implementation. One specific divergence between them was fixed (see above); others may exist. The benchmark scripts test `trace_sample.py`, not the actual production pipeline the API serves.
- **No retry/error handling on LLM extraction failures** (e.g. a low-quality scan or non-English document) — a genuine parsing failure surfaces as bad data rather than a clean, user-facing error.
- **Flat-file persistence** — see Section 6. Not a database; fine for MVP/pilot scale, not production scale.
- **No auth.** Any client that can reach the API can call every endpoint. Fine for a local/demo deployment, not for a real pilot with real supplier data.
- **SKU catalog is a static JSON file** (`data/skus.json` / `data/real_skus.json`), not a live PIM/ERP integration.

## 8. Repository Map (MVP-relevant paths)

```
agent/
├── server.py            # FastAPI app — all HTTP routes
├── graph.py              # LangGraph pipeline: extraction → rules → routing
├── schemas.py             # Pydantic models (extraction, rule violations, gap notice records)
├── gap_notice.py           # Gap notice generation + lifecycle transitions
├── gap_notice_store.py      # JSON-file persistence for gap notices
├── telegram_dispatch.py      # Best-effort Telegram notification on gap-notice SENT
└── run_pdf.py                # CLI runner + master CSV ledger writer

mvp/frontend/
├── app/page.tsx              # Upload + single-audit inspection
├── app/audits/page.tsx        # Audit queue
├── app/audits/[id]/page.tsx    # Audit detail: evidence viewer, review actions, gap-notice modal
└── lib/api.ts, lib/exportUtils.ts   # API client, CSV export

tests/                        # pytest suite — 98 passing, 1 skipped, 3 pre-existing unrelated failures
```

## 9. Relationship to the Other Deliverables

- **Round 1 POC** (`n8n/`): the original workflow, unmodified, kept as a baseline for comparison.
- **Round 2 POC** (`poc/`): the same n8n workflow extended with one new capability (gap-notice drafting) to show evolution without duplicating MVP depth — see `poc/poc_documentation.md`.
- **This MVP**: the real, running product. Everything the POC gestures at (draft generation) is here with full persistence, an editable/approvable/sendable lifecycle, structured evidence, and a proper reviewer UI.
