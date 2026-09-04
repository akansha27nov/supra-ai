# Supra AI — AI-Assisted Supplier Compliance Screening

**Capstone project — Round 1 (pitch) + Round 2 (consulting package + working MVP)**

## Scenario

**Client:** Chleo, Head of Procurement and Supply Chain Operations at a mid-sized European omnichannel retailer (~200 employees, ~2,000 active SKUs, consumer electronics sourced from EU and non-EU suppliers).

**Problem:** Supplier compliance documentation (CE/RoHS certificates, test reports, declarations of conformity) is spread across PDFs, spreadsheets, and email, and checked manually. Chleo needs a faster way to identify incomplete, expired, or inconsistent supplier documentation and prioritise which products need human review — without an AI system making the compliance decision itself.

**Solution shape:** an AI-assisted screening layer that extracts structured data from supplier certificates, checks it against deterministic compliance rules and the internal SKU catalog, and surfaces prioritised, evidence-linked findings on a dashboard for human reviewers. The AI extracts; a transparent, auditable rule engine decides; a human approves.

**Round 1 decision:** KEEP — proceed to Round 2 with the existing architecture as the baseline (see `feedback/round1_decision.md`).

## Live MVP

Live here: [supra-ai](https://supra-ai.netlify.app/)
| Layer | Where | Notes |
|---|---|---|
| Frontend | Netlify (Next.js, `mvp/frontend`) | Reviewer UI — upload, audit queue, audit detail, analytics |
| Backend | Render (FastAPI, `agent/server.py`) | LangGraph extraction + rule-engine pipeline |
| Database | Render Postgres | Audit ledger (`audit_ledger`) + gap-notice records (`gap_notices`), via `agent/db.py` |

**Presentation Deck:** [docs/Supra_AI_Presentation.pdf](docs/Supra_AI_Presentation.pdf)

## What the MVP does

A reviewer uploads a supplier compliance PDF (Declaration of Conformity or lab test report). The system:

1. Extracts structured fields via an LLM (supplier, dates, standards, measured chemical values, evidence quotes/pages).
2. Classifies the document type and resolves the product against an internal SKU catalog (`matched` / `unmatched` / `not_attempted`).
3. Runs a deterministic rule engine (expiry, missing standards, lead-threshold, lab accreditation, SKU match) to produce `APPROVED` / `FLAGGED` / `REJECTED` / `REQUIRES_HUMAN_REVIEW` plus a 0–100 score.
4. Persists the result to the Postgres audit ledger, with structured evidence (exact quote, page, section) carried through.
5. Lets a human reviewer approve/reject, and — for `FLAGGED`/`REJECTED` documents — generate, edit, approve, and send a supplier gap notice, with the full lifecycle persisted and status-tracked.
6. Sends a best-effort internal Telegram notification when a gap notice is marked sent.
7. Provides an audit-scoped Copilot Chat that helps reviewers investigate findings, understand supporting evidence, and navigate the audit without changing the underlying compliance decision.

The core AI capability (extraction + rule-based screening) runs end to end against real PDFs, not synthetic mocks. Latest benchmark: 13/13 audit decisions agreeing with labelled ground truth, 95.9% overall extraction accuracy (see `strategic_plan.md`).

## System Architecture

```
                    +----------------------+
                    |   Next.js Frontend   |
                    |   mvp/frontend       |
                    |                      |
                    +----------+-----------+
                               |
                               v   HTTPS / JSON  (NEXT_PUBLIC_API_URL)
                    +----------------------+
                    |       FastAPI        |
                    |   agent/server.py    |
                    |                      |
                    +----------+-----------+
                               |
                               v
                 +-------------------------------------+
                 |      agent/graph.py / LangGraph     |
                 |  deterministic audit state machine  |
                 +-------------------+-----------------+
                                     |
        +----------------------------+-----------------------------+
        |                            |                             |
        v                            v                             v
+-------------------+   +---------------------------+    +--------------------------+
| extract_node      |   | validate_fields_node       |   | resolve_sku_node         |
| LLM field         |-->| absent/ambiguous check     |-->| match product against    |
| extraction        |   | + reconcile_node loop      |   | SKU catalog              |
| (OpenAI)          |   | (bounded, max 2 attempts)  |   | data/skus.json           |
+-------------------+   +---------------------------+    +--------------------------+
                                     |
                                     v
                    +----------------------------------+
                    | rule_engine_node                 |
                    | expiry / mandatory standards /   |
                    | lead ppm threshold / lab         |
                    | accreditation / SKU match        |
                    +----------------+-----------------+
                                     |
                                     v
                    +---------------------------------+
                    | audit_result                    |
                    | APPROVED / FLAGGED / REJECTED / |
                    | REQUIRES_HUMAN_REVIEW           |
                    | + 0-100 score + evidence        |
                    +----------------+----------------+
                                     |
                                     v
                    +---------------------------------+
                    | Postgres                        |
                    | audit_ledger  +  gap_notices    |
                    | (agent/db.py, via DATABASE_URL) |
                    +----------------+----------------+
                                     |
                                     v
                    +--------------------------------------+
                    | Outputs                              |
                    | - reviewer approve / reject          |
                    |   (/api/logs/{id}/review)            |
                    | - gap notice draft/edit/approve/send |
                    |   (/api/gap-notice*)                 |
                    | - Telegram alert on notice sent      |
                    | - LangSmith trace of every run       |
                    +------------------+-------------------+
                                       |
                                       v
                    +--------------------------------------+
                    | Audit Copilot Chat                   |
                    | (agent/copilot.py)                   |
                    | POST /api/logs/{id}/chat             |
                    | reads audit_ledger + gap_notices;    |
                    | reuses graph.py's LLM client;        |
                    | grounded, audit-scoped, read-only —  |
                    | never writes back to the ledger      |
                    +--------------------------------------+
```

Supra AI runs on a central **LangGraph** deterministic state machine (`agent/graph.py`) that extracts, validates, resolves, and screens supplier compliance documents behind a single FastAPI backend. Check `mvp/mvp_documentation.md` for the full request/response contract.

- **Entrypoint:**
  * **Next.js reviewer UI** (`mvp/frontend`) — upload a certificate, inspect an audit, review the evidence, act on gap notices.
- **Backend / pipeline:**
  * **FastAPI** (`agent/server.py`) — `POST /api/audit`, `GET /api/logs`, `PATCH /api/logs/{id}/review`, `/api/gap-notice*`, `POST /api/logs/{id}/chat`.
  * **LangGraph state machine** (`agent/graph.py`) — `extract → classify_doc_type → validate_fields → (reconcile, bounded to 2 retries) → resolve_sku → rule_engine → (flag_for_human_review if unresolved)`.
  * **Audit Copilot** (`agent/copilot.py`) — assembles a single audit's `FlagsDetail`/evidence/gap-notice into context, calls the same LLM client `graph.py` uses, returns a grounded answer plus a `grounded` flag the UI surfaces when the question falls outside the case's evidence.
- **External services & stack:**
  * **OpenAI** — structured-output extraction of certificate fields, gap-notice drafting, and Copilot chat responses.
  * **Postgres on Render** (`agent/db.py`) — durable store for the audit ledger and the gap-notice lifecycle, replacing the earlier flat-file (CSV/JSON) persistence.
  * **LangSmith** — every graph run and Copilot chat turn is traced for observability (`LANGSMITH_PROJECT`; the legacy `LANGCHAIN_PROJECT`/`LANGCHAIN_TRACING_V2` names are also read by the SDK, but `LANGSMITH_*` is the source of truth in `.env` — keep only one project name set to avoid traces silently splitting across two projects).
  * **Telegram Bot API** — best-effort internal notification when a gap notice is marked sent.
- **Outputs:** 
  * a reviewer-facing audit queue and detail view, an editable/approvable/sendable supplier gap notice, and a full audit trail in Postgres.
  * Audit Copilot Chat — reviewer-facing conversational investigation of the selected audit and its evidence, read-only against the compliance decision.

### Execution Flow & Decision Tree

`route_after_validation` is the safety gate that keeps the pipeline from silently guessing on incomplete documents:

1. **Extraction (`extract_node`):** an LLM call turns raw PDF text into structured fields — supplier, dates, standards, measured chemical values, evidence quotes/pages.
2. **Validation (`validate_fields_node`):** every field is marked `present`, `absent_expected`, `absent_appropriate`, or `ambiguous` given the document type.
3. **Reconciliation gate (`route_after_validation`):** if any field is `absent_expected` or `ambiguous` **and** fewer than 2 reconciliation attempts have run, the graph loops back through `reconcile_node` for a targeted re-extraction. After 2 failed attempts (or an unclassifiable `doc_type`), it routes to `flag_for_human_review_node` instead of guessing.
4. **SKU resolution (`resolve_sku_node`):** once fields are resolved, the product is matched against the internal SKU catalog (`matched` / `unmatched` / `not_attempted` — never silent).
5. **Rule engine (`rule_engine_node`):** deterministic checks — expiry, mandatory standards, lead-ppm threshold (with a two-tier exemption check: a self-declared exemption is treated differently from a lab-verified one), lab accreditation, SKU match — produce a decision and a 0–100 score.
6. **Human review:** the AI never makes the final compliance call. A reviewer approves/rejects via the UI, and for `FLAGGED`/`REJECTED` documents can generate, edit, approve, and send a supplier gap notice.

## Repository structure

```
supra-ai/
├── research/                    # Sector research, opportunity/risk mapping, use cases (Round 1)
│   ├── sector_research.md
│   ├── opportunities_risks.md
│   └── use_cases.md
├── data/                        # Sample + real-world PDFs, ground truth, SKU catalog, benchmark exports
├── n8n/                         # Round 1 POC (n8n workflow, unmodified baseline)
├── poc/                         # Round 2 POC — same n8n workflow + gap-notice drafting
│   ├── workflow_round2.json
│   ├── poc_documentation.md
│   └── screenshots/
├── langsmith/                   # Tracing + benchmark scripts
│   ├── trace_sample.py
│   ├── master_benchmark.py
│   ├── two_tier_benchmark.py
│   └── langsmith_documentation.md
├── agent/                       # LangGraph pipeline + FastAPI backend (deployed on Render)
│   ├── server.py                 # FastAPI app — all HTTP routes
│   ├── graph.py                  # LangGraph pipeline: extraction → rules → routing
│   ├── db.py                     # Postgres persistence (audit ledger + gap notices)
│   ├── schemas.py                # Pydantic models
│   ├── gap_notice.py             # Gap notice generation + lifecycle
│   ├── gap_notice_store.py
│   ├── copilot.py                # Audit Copilot Chat — context assembly + grounded LLM call
│   ├── telegram_dispatch.py
│   └── run_pdf.py                # CLI runner
├── mvp/
│   ├── frontend/                 # Next.js reviewer UI (deployed on Netlify)
│   └── mvp_documentation.md      # Full MVP write-up: architecture, setup, deployment, limitations
├── dashboard/                    # Tableau dashboard + documentation
├── cost_estimation/               # cost_analysis.md, timeline_estimate.md
├── compliance/
│   ├── eu_ai_act_compliance.md
│   └── gdpr_documentation.md
├── docs/
│   ├── planning/                 # rollout_plan.md, user_stories.md, acceptance_criteria.md, definition_of_done.md
│   ├── implementation_docs/       # langgraph_implementation.md, copilot_chat.md
│   └── product_requirement/       # design_doc.md
├── feedback/
│   ├── Supra_AI_Round1_Presentation.pdf
│   └── round1_decision.md
├── tests/                         # pytest suite
├── use_case_definition.md
├── roi_risk_assessment.md
├── strategic_plan.md
├── requirements.txt
├── .env.example
└── generate_test_certs.py
```

## Setup

### Backend (FastAPI + Postgres)

```bash
git clone https://github.com/akansha27nov/supra-ai.git
cd supra-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in OPENAI_API_KEY and DATABASE_URL at minimum
uvicorn agent.server:app --reload --port 8000
```

The API is now at `http://localhost:8000`. `init_db()` creates the Postgres tables automatically on first run if they don't exist — point `DATABASE_URL` at any Postgres instance (local, or Render's).

### Frontend (Next.js)

```bash
cd mvp/frontend
npm install
npm run dev
```

The app is now at `http://localhost:3000`, pointed at `http://localhost:8000/api` by default (see `lib/api.ts`); override with `NEXT_PUBLIC_API_URL` to point at a deployed backend (e.g. the Render URL).

### Verify it's working

```bash
pytest tests/ -q
```

See `mvp/mvp_documentation.md` for expected pass/fail counts and known pre-existing failures.

## Deployment

- **Frontend → Netlify:** builds from `mvp/frontend` (`netlify.toml`: `npm run build`, publish `.next`, via `@netlify/plugin-nextjs`). Set `NEXT_PUBLIC_API_URL` to the Render backend URL in Netlify's environment variables.
- **Backend → Render (Web Service, Python):** build command `pip install -r requirements.txt`, start command `uvicorn agent.server:app --host 0.0.0.0 --port $PORT`, root directory = repo root (imports are `agent.*`). Set `OPENAI_API_KEY` and `DATABASE_URL` in Render's dashboard, not in a committed file.
- **Database → Render Postgres:** provision a Render Postgres instance and attach its connection string as `DATABASE_URL` on the backend service. Render sometimes provides `postgres://`; `agent/db.py` normalises this to `postgresql://` for psycopg2.

Full deployment notes, environment variables, and known limitations are in `mvp/mvp_documentation.md`.

## Other deliverables

- **Dashboard**: open `dashboard/Supra AI Compliance Auditor.twbx` in Tableau, connected to `data/tableau_export.csv`. See `dashboard/dashboard_documentation.md`.
- **Round 1 POC**: `n8n/` — original workflow, kept as a baseline. **Round 2 POC**: `poc/` — the same workflow extended with gap-notice drafting; see `poc/poc_documentation.md` for the Round 1 → Round 2 evolution.
- **Use case definition**: `use_case_definition.md` — business problem, company profile, solution, stakeholders, success criteria.
- **ROI & risk**: `roi_risk_assessment.md` — conservative/base/optimistic ROI scenarios, upfront + ongoing costs, risk matrix.
- **Compliance**: `compliance/eu_ai_act_compliance.md` and `compliance/gdpr_documentation.md` — risk classification, obligations, data flows, DPIA.
- **Strategic plan**: `strategic_plan.md` — POC → pilot → full deployment path, GTM, KPIs, commercialisation.
- **Research pack**: `research/` — sector context, opportunity/risk mapping, use cases.
- **Cost/timeline**: `cost_estimation/` — measured AI inference cost (~$0.0004/certificate), volume assumptions, build cost, implementation timeline.

## What this project does and does not prove

The MVP demonstrates that the end-to-end concept is feasible, that deterministic policy screening can be separated from AI extraction, that the system runs as a deployed product  against real supplier documents, and that real-world documents reveal failure modes synthetic data alone would not expose. See `mvp/mvp_documentation.md` (Known Limitations) and `strategic_plan.md` for what's scoped next.
