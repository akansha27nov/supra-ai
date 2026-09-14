# Sprint Plan — Round 2

## Planning Assumptions

**Team:** 1 developer/project owner + client reviewer/stakeholder support
**Working capacity:** 5 days/week, with approximately 0.5–1 day reserved for testing, documentation and stakeholder feedback.

Story points are used as **relative complexity**, not as a fixed conversion to working days. As a rough calibration check: 1 story point ≈ 1 focused dev-day at this capacity, based on comparable single-developer pilot work — useful for sanity-checking planned capacity against the 29-point total, not treated as a strict conversion rate.

The project is limited to **one pilot product category**. Weeks 7–8 do not represent a full 2,000-SKU deployment.

---

## Sprint 1 — Week 1
### Foundations & Data Readiness

**Sprint goal:**
Confirm that supplier data for the selected pilot category is sufficiently complete and usable before development continues.

**Owner:** Akansha
**Story:** EN-01
**Capacity:** 3 points

**Dependencies:**
- Client supplier list
- Sample documents
- Agreement on pilot category

**Exit criteria:**
- Supplier/document inventory completed.
- Documentation completeness measured.
- Data-quality risks documented.
- If documentation quality is below the agreed threshold, scope/capacity is re-estimated before Sprint 2.

**Deliverable:**
Pilot data-quality report.

---

## Sprint 2 — Week 2
### Document Classification

**Sprint goal:**
Reliably identify supported document types before extraction.

**Owner:** Akansha
**Story:** US-1
**Capacity:** 3 points

**Dependencies:**
- EN-01 complete
- Ground-truth classification set available

**Exit criteria:**
- Classification reaches the agreed ≥95% target on the validation set.
- Unknown documents are handled as `unrecognized`.
- Confidence is visible.
- Classification is traceable.

---

## Sprint 3 — Week 3
### Structured Extraction

**Sprint goal:**
Extract structured, evidence-linked fields from correctly classified pilot documents.

**Owner:** Akansha
**Story:** US-2
**Capacity:** 5 points

**Dependencies:**
- US-1 complete
- Document schemas defined
- Ground-truth extraction set available

**Exit criteria:**
- Field-level accuracy measured.
- Evidence links available for surfaced fields.
- JSON schema validation passes.
- Uncertain/missing values are explicitly represented.

**KPI:**
- Critical-field extraction accuracy ≥90% on the validated ground-truth set (matches the extraction target already stated in `rollout_plan.md` Phase 2 — kept identical across both documents on purpose).

---

## Sprint 4 — Week 4
### Failure Handling & Human Routing

**Sprint goal:**
Ensure the system fails safely instead of guessing and correctly routes uncertain records to human review.

**Owner:** Akansha
**Stories:** US-3, US-4
**Capacity:** 8 points

**Dependencies:**
- US-2 complete

**Exit criteria:**
- Missing-field test passes.
- Low-confidence test passes.
- Corrupted-file test passes.
- Wrong-schema test passes.
- Flagged records reach human review.
- No flagged record silently becomes compliant.
- Reviewer actions are auditable.
- Original AI values remain preserved after correction.

**KPI:**
- Silent-failure rate on the four failure-mode test cases (missing field, low confidence, corrupted file, wrong schema) — target 0, measured at sprint exit.
- % of flagged records reaching the review queue without manual intervention — target 100%, measured against the sprint's test batch.

**Risk gate:**
This sprint specifically addresses the class of failure demonstrated by the live bug in Round 1.

---

## Sprint 5 — Week 5
### ERP Read Access & Reviewer Calibration

**Sprint goal:**
Connect the pilot workflow to real ERP records in read-only mode and establish consistent reviewer behaviour.

**Owners:**
- ERP integration: Akansha / designated technical owner
- Reviewer calibration: Akansha + client reviewers

**Stories:** EN-02, EN-03
**Capacity:** 5 points

**Dependencies:**
- US-4 complete
- Client ERP access available
- Reviewers available

**Exit criteria:**
- Read-only ERP access demonstrated.
- No ERP write access exists.
- Pilot records can be linked to document/run IDs.
- Reviewer calibration completed.
- Reviewer agreement rate recorded.
- Calibration issues documented separately from technical defects.

---

## Sprint 6 — Week 6
### Security & Procurement Readiness

**Sprint goal:**
Resolve non-engineering deployment blockers before controlled live validation.

**Owners:** Akansha + client security/procurement stakeholders

**Stories:** EN-04, EN-05
**Capacity:** 5 points

**Dependencies:**
- EN-02 complete
- Client security contact available
- Client procurement/process owner available

**Exit criteria:**
- Security review documented.
- Access-control requirements confirmed.
- Data/logging handling reviewed.
- Procurement workflow documented.
- Human approval mapped to existing decision authority.
- Outstanding blockers have owners and remediation dates.

**Gate:**
No live pilot proceeds with an unresolved critical security or governance blocker.

---

## Sprint 7 — Week 7
### Controlled Limited-Category Live Run

**Sprint goal:**
Validate the complete workflow using real documents from the selected pilot category.

**Owner:** Akansha + client sponsor/reviewer

**Type:** Milestone / validation sprint
**New stories:** None

**Dependencies:**
- Sprints 1–6 complete
- Security/governance gate passed
- Pilot data available

**Scope:**
- Selected category only
- Controlled volume
- Human review enabled
- No full-catalogue deployment

**Exit criteria:**
- End-to-end workflow completes.
- Flagged items reach human review.
- Human actions are logged.
- Evidence is available for reviewer decisions.
- No silent critical failures.
- Live performance is recorded.

**KPI:**
- Classification accuracy on live pilot documents — target ≥95%, result to be recorded. This is the first measurement of this number against **live** data rather than the synthetic/ground-truth set.
- Notification/side-channel failure rate (e.g. Telegram alerts) — target 0 silent failures, i.e. any failure must be persisted and visible, not just logged to console. This is the first live-volume test of whether the Sprint 4 fix holds under real conditions.

**Important:**
Sprint 7 is **controlled operational validation, not production rollout**.

---

## Sprint 8 — Week 8
### Evidence-Based Go/No-Go Decision

**Sprint goal:**
Determine whether the solution should expand beyond the pilot category.

**Owner:** Akansha + client sponsor

**Type:** Decision milestone
**New stories:** None

**Deliverable:**
Go/no-go decision memo.

### Decision evidence

| Gate | Target | Result |
|---|---:|---:|
| Classification accuracy | ≥95% | Record actual result |
| Critical-field accuracy | ≥90% *(same target as Sprint 3 KPI / rollout_plan.md Phase 2)* | Record actual result |
| Silent critical failures | 0 | Record actual result |
| Silent notification/alert failures | 0 *(added after the Round 1 Telegram incident — see failure-mode register)* | Record actual result |
| Review routing | 100% of flagged cases | Record actual result |
| Evidence coverage | 100% of surfaced critical findings | Record actual result |
| Reviewer time/document | ≥20% reduction (conservative-case floor) vs. the 40% base-case assumption in `roi_risk_assessment.md` | Record actual result |
| Security | Approved | Yes/No |
| GDPR controls | Approved | Yes/No |
| ERP read integration | Stable | Yes/No |
| Procurement/process alignment | Approved | Yes/No |

### Decision rules

**GO**

All mandatory safety, traceability and security gates pass and the measured business value justifies further validation.

**CONDITIONAL GO**

No critical safety/security issue exists, but defined non-critical remediation remains. A restricted next step is permitted only with documented actions and owner.

**NO-GO**

A critical safety, security, traceability or governance gate fails, or the measured performance/business value does not justify expansion.

A **GO does not authorise deployment to all 2,000 SKUs**.

It authorises creation of a **new, separately scoped rollout plan for the next product category**.

---

# Story → Sprint Traceability

| ID | Type | Sprint | Owner | Points |
|---|---|---:|---|---:|
| EN-01 | Enabler | 1 | Akansha | 3 |
| US-1 | User story | 2 | Akansha | 3 |
| US-2 | User story | 3 | Akansha | 5 |
| US-3 | User story | 4 | Akansha | 3 |
| US-4 | User story | 4 | Akansha | 5 |
| EN-02 | Enabler | 5 | Akansha | 3 |
| EN-03 | Enabler | 5 | Akansha + reviewers | 2 |
| EN-04 | Enabler | 6 | Akansha + security | 3 |
| EN-05 | Enabler | 6 | Akansha + procurement | 2 |
| M-01 | Milestone | 7 | Akansha + sponsor | — |
| M-02 | Milestone | 8 | Akansha + sponsor | — |

**Total planned development/enabler capacity: 29 story points.**

---

# Principle

The project deliberately separates:

**Technical feasibility → controlled pilot → operational validation → evidence-based expansion.**

The system is not considered deployment-ready simply because the AI produces accurate outputs. Deployment also requires safe failure handling, traceability, human oversight, data protection, security, ERP readiness, reviewer calibration and organisational approval.
