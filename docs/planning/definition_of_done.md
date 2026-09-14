# Definition of Done — Round 2

Applies to every user story and enabler story in `user_stories.md`, and to every sprint in `sprint_plan.md`.

A story is **Done** only when its own acceptance criteria and the applicable Definition of Done requirements have been satisfied.

## 1. Story Definition of Done

### Code & Testing
- [ ] Implementation is complete and committed to the repository.
- [ ] Code is peer-reviewed before merge, or self-reviewed with documented review notes if working solo.
- [ ] Unit tests covering the story's core logic are written and passing.
- [ ] At least one relevant failure-mode test is included.
- [ ] Full regression pipeline is run against the agreed ground-truth set.
- [ ] No regression against the last recorded baseline without an approved explanation.
- [ ] Test results are recorded as evidence, including date, test scope and outcome.

### Traceability & AI Observability
- [ ] Every classification/extraction run has a traceable, pseudonymous document/run ID.
- [ ] LangSmith tracing is enabled for the relevant workflow.
- [ ] LangSmith traces do not retain supplier personal data or unnecessary raw document content in plaintext.
- [ ] Every field surfaced to a reviewer has evidence linking it back to the source document (page/line or equivalent reference).
- [ ] AI output, validation result and human action can be linked through a common document/run ID.

### Compliance & Decision Control
- [ ] AI output is clearly distinguished from deterministic-rule output and human decisions.
- [ ] No compliance status is written to the system of record unless the record either passes the deterministic rule engine with no unresolved mandatory fields or receives an explicit human decision.
- [ ] Any human override records the original system result, reviewer decision, reviewer ID, timestamp and reason.
- [ ] A flagged or unresolved record cannot silently default to "compliant."

### GDPR & Data Handling
- [ ] Supplier personal data is not unnecessarily logged outside the access-controlled application.
- [ ] Data retention periods for uploaded documents, application records and observability logs are documented.
- [ ] Retention periods match the client-facing GDPR documentation.
- [ ] Reviewer dashboard and underlying data are role-restricted.
- [ ] Access credentials and secrets are not stored in source code or test evidence.

### Human-in-the-Loop
- [ ] Reviewer can see why a record was flagged.
- [ ] Reviewer can see the affected field, confidence and source evidence.
- [ ] Reviewer can approve, correct or reject where applicable.
- [ ] Corrections preserve the original AI extraction and record the reviewer-corrected value separately.
- [ ] Reviewer actions are auditable through reviewer ID and timestamp.

### Documentation
- [ ] Story scope and out-of-scope boundaries are documented.
- [ ] Dependencies and assumptions are recorded.
- [ ] Acceptance-test results are recorded.
- [ ] Newly discovered failure modes are added to the project failure-mode log.
- [ ] Any unresolved issue is explicitly recorded rather than hidden.
- [ ] Failures in side-channel notifications (e.g. alerts, webhooks) are persisted with the record they relate to, not only logged to console output.

### Demo
- [ ] Story is demonstrated using a real document where feasible.
- [ ] Demo evidence is recorded.
- [ ] Any bug discovered during demonstration is logged and triaged.
- [ ] A story with a known unresolved defect cannot be marked Done unless the defect is explicitly accepted as a documented exception by the project owner.

---

# 2. Sprint Definition of Done

A sprint is **Done** when:

- [ ] All committed stories/enablers satisfy the Story Definition of Done.
- [ ] Sprint goal has been evaluated against measurable exit criteria.
- [ ] Planned tests and regression checks have been completed.
- [ ] Known defects and newly discovered failure modes are documented.
- [ ] Sprint evidence is stored in the project documentation.
- [ ] Capacity used versus planned capacity is recorded.
- [ ] Any unfinished work is re-estimated and moved into the next sprint rather than silently carried over.
- [ ] Sprint outcome and next-step recommendation are documented.

---

# 3. Project Go/No-Go Definition

The project is not considered production-ready merely because the MVP works.

Expansion beyond the pilot category requires an evidence-based Go decision covering:

- Classification accuracy
- Field-level extraction accuracy
- Critical-field error rate
- Silent-failure rate
- Human-review routing accuracy
- Evidence-link coverage
- Reviewer time per document
- Security/access-control status
- GDPR/data-retention status
- ERP integration readiness
- Procurement/process approval

A **Go** decision permits planning of the next limited category.

A **Go** decision does not automatically authorise full 2,000-SKU deployment.

A **No-Go** decision requires documented remediation actions and re-evaluation before expansion.