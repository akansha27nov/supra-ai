# User Stories — Round 2

## Pilot Scope

The stories below apply to the agreed pilot product category and its supported document types. The supported document types must match the types actually implemented and represented in the validated ground-truth dataset.

---

## US-1 — Classify Uploaded Document

**As a** compliance reviewer
**I want** the system to identify the document type before extraction
**So that** the correct extraction schema is selected.

### Acceptance Criteria

- Given a PDF belonging to a supported pilot document type, the system assigns the correct document type on the agreed validation set with a target accuracy of ≥95%.
- Given an unsupported or unknown document, the system returns `unrecognized` rather than forcing a known schema.
- Classification label and confidence are visible before field extraction.
- Classification is traceable through a document/run ID.
- Classification does not perform field extraction.

### Out of Scope

- Field extraction → US-2
- Handling incomplete/malformed documents → US-3
- Reviewer routing → US-4

**Story points:** 3
**Dependency:** None
**Owning code:** `agent/graph.py::classify_doc_type_node`
**Tests:** `tests/test_graph_routing.py`, `tests/test_graph_validation.py`

---

## US-2 — Extract Evidence-Linked Structured Fields

**As a** compliance reviewer
**I want** mandatory fields extracted from a correctly classified document
**So that** I can review structured information instead of manually reading the entire PDF.

### Acceptance Criteria

- Given a document correctly classified by US-1, the system applies the appropriate schema.
- Mandatory fields are extracted where the information is present.
- Each extracted field contains a confidence value.
- Each field surfaced to the reviewer contains evidence linking it to the source document.
- Extraction output validates against the document-type JSON schema.
- Missing, ambiguous or uncertain fields are represented explicitly rather than fabricated.
- Field-level accuracy is measured against the agreed ground-truth dataset.

### Out of Scope

- Document classification → US-1
- Failure detection/routing → US-3
- Compliance decision logic → existing deterministic rule engine
- Human review workflow → US-4

**Story points:** 5
**Dependency:** US-1
**Owning code:** `agent/graph.py::extract_node`, `agent/schemas.py`
**Tests:** `tests/test_graph_validation.py`, `tests/test_schemas.py`

---

## US-3 — Detect Incomplete or Malformed Extraction

**As a** compliance reviewer
**I want** the system to identify incomplete, uncertain or malformed input
**So that** the system does not silently produce an apparently compliant result from unreliable data.

### Acceptance Criteria

- A missing mandatory field results in an explicit unresolved/needs-review state.
- A low-confidence mandatory field is identified and named.
- Corrupted or unreadable input fails gracefully.
- Password-protected or unsupported input produces a controlled error state.
- Wrong-schema documents are detected rather than silently processed as the wrong type.
- Flagged records cannot bypass the review workflow and become compliant automatically.
- Tests cover at least:
  - missing field;
  - low-confidence field;
  - corrupted file;
  - wrong-schema document.

### Out of Scope

- Reviewer interface and decision workflow → US-4
- Changes to the underlying compliance rule logic

**Story points:** 3
**Dependency:** US-2
**Owning code:** `agent/graph.py::validate_fields_node`, `agent/graph.py::route_after_validation`
**Tests:** `tests/test_graph_validation.py`, `tests/test_graph_routing.py`

---

## US-4 — Route and Resolve Human Review

**As a** compliance reviewer
**I want** uncertain records routed to a review queue with evidence and explanations
**So that** I can make an informed final decision.

### Acceptance Criteria

- A `needs_review` record appears in the reviewer queue without requiring manual re-import.
- The reviewer sees:
  - flagged field;
  - reason for flag;
  - confidence;
  - extracted value;
  - source evidence.
- Reviewer can approve, correct or reject the record where applicable.
- Reviewer corrections preserve the original AI extraction.
- Reviewer action records reviewer ID and timestamp.
- A human override records the original system result and reason for the override.
- No flagged record can silently default to compliant.
- Records that pass the deterministic rule engine are clearly distinguished from records requiring human sign-off.

### Out of Scope

- Classification → US-1
- Field extraction → US-2
- Failure detection → US-3
- Redesign of the deterministic compliance rules

**Story points:** 5
**Dependency:** US-3
**Owning code:** `agent/graph.py::flag_for_human_review_node`; `agent/gap_notice.py` (`generate_supplier_gap_notice`, `create_gap_notice_record`, `approve_gap_notice_for_sending`, `send_gap_notice`); `agent/gap_notice_store.py`; `agent/server.py` (`PATCH /api/logs/{record_id}/review`, `POST /api/gap-notice`, `POST /api/gap-notice/{notice_id}/approve`, `POST /api/gap-notice/{notice_id}/send`)
**Tests:** `tests/test_graph_rules.py`, `tests/test_gap_notice.py`

---

# Enabler Stories

## EN-01 — Pilot Data Readiness

**Goal:** Establish whether the selected pilot category contains sufficient, usable supplier documentation.

### Acceptance Criteria

- Supplier/document inventory is completed.
- Completeness and currency of documentation are measured.
- Missing or outdated documentation is quantified.
- Data-quality risks are documented.
- If data quality is below the agreed threshold, capacity and scope are re-estimated before development continues.

**Story points:** 3
**Sprint:** 1
**Owning code:** none — data/process audit, not a pipeline component. Output is the pilot data-quality report, not a module.

---

## EN-02 — Read-Only ERP Integration

**Goal:** Allow the system to read the relevant pilot-category records without write access.

### Acceptance Criteria

- Connector accesses only agreed pilot-category data.
- No write operation is available.
- Authentication and credentials follow the approved security process.
- Integration errors are handled explicitly.
- Retrieved records can be linked to the corresponding document/run ID.

**Story points:** 3
**Sprint:** 5
**Owning code:** not yet built — no ERP connector exists in the current repo. Left explicitly unfilled rather than omitted, since it's a genuine gap, not an oversight.

---

## EN-03 — Reviewer Calibration

**Goal:** Establish consistent human-review decisions.

### Acceptance Criteria

- Review guidance is provided to reviewers.
- Two reviewers independently assess an agreed sample of flagged records.
- Agreement rate is recorded.
- Disagreements are analysed and categorised.
- Calibration issues are documented separately from software defects.

**Story points:** 2
**Sprint:** 5
**Owning code:** none — human-process activity, measured via the `ReviewStatus`/`Reviewer` fields already in `agent/db.py`'s `audit_ledger` table, surfaced through `PATCH /api/logs/{record_id}/review`.

---

## EN-04 — Security Review

**Goal:** Confirm that security controls are sufficient for the limited pilot.

### Acceptance Criteria

- Access control reviewed.
- Credential/secrets management reviewed.
- Data storage reviewed.
- Observability/logging reviewed.
- Security findings documented.
- Required security actions have owners and deadlines.
- Security sign-off is recorded before the live pilot.

**Story points:** 3
**Sprint:** 6
**Owning code:** cross-cutting — covers `DATABASE_URL` / `TELEGRAM_BOT_TOKEN` / `OPENAI_API_KEY` handling in `.env` (never committed, per `.gitignore`) and dashboard role-restriction. Role-restriction is **not yet implemented** — `agent/server.py` currently has no auth layer. Named here explicitly as the Sprint 6 gap to close, not assumed done.

---

## EN-05 — Procurement and Process Alignment

**Goal:** Confirm where AI output fits within the existing compliance approval process.

### Acceptance Criteria

- Existing decision authority is documented.
- Human approval step is mapped to the existing process.
- AI does not introduce an unauthorised decision-maker.
- Procurement requirements are documented.
- Outstanding commercial/process dependencies are recorded.

**Story points:** 2
**Sprint:** 6
**Owning code:** none — process/organisational deliverable, documented as a decision memo, not implemented in the repo.
