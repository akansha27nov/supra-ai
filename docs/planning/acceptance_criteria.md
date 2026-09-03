# Supra AI Compliance Auditor — Acceptance Criteria

## 1. Acceptance Philosophy

Acceptance is based on four separate dimensions:

1. **Extraction quality** — does the system represent what the document actually says?
2. **Policy execution** — does the deterministic rule engine apply the intended rules consistently?
3. **Operational safety** — does uncertainty become human review rather than fabricated certainty?
4. **Usability and rollout readiness** — can a reviewer use and understand the result?

Extraction accuracy and rule-engine accuracy must be evaluated separately.

## 2. Document Classification

### AC-01 — DoC classification
**Given** a manufacturer Declaration of Conformity  
**When** the document is processed  
**Then** `document_classification = DECLARATION_OF_CONFORMITY`.

### AC-02 — Lab report classification
**Given** a laboratory test report  
**When** the document is processed  
**Then** `document_classification = LAB_TEST_REPORT`.

### AC-03 — Unknown classification
**Given** a document that cannot be reliably classified  
**When** classification completes  
**Then** the system records an unknown/ambiguous state and routes it for human review.

## 3. Missing and Non-Applicable Fields

### AC-04 — Missing expiration date
**Given** a self-declaration with no stated expiration date  
**When** validation runs  
**Then** `expiration_date` may be `null`, the expiry check is skipped when appropriate, and no unhandled exception occurs.

### AC-05 — Missing laboratory information
**Given** a manufacturer self-declaration with no laboratory accreditation information  
**When** validation runs  
**Then** missing lab information does not by itself trigger an unaccredited-lab finding.

### AC-06 — Missing certificate ID
**Given** a document with no certificate identifier  
**When** extraction runs  
**Then** `certificate_id = null` rather than a fabricated identifier.

## 4. Chemical Evidence

### AC-07 — Statutory threshold
**Given** a document that states a legal RoHS lead limit of 1000 ppm but contains no measured lead result  
**When** extraction runs  
**Then** `is_statutory_limit = true` and `tested_lead_ppm = null`.

### AC-08 — Measured laboratory result
**Given** a laboratory report containing an actual measured lead concentration  
**When** extraction runs  
**Then** the measured concentration is stored separately from the legal limit.

### AC-09 — Ambiguous chemical value
**Given** a chemical value whose context cannot be confidently resolved  
**When** reconciliation reaches its maximum attempts  
**Then** the system routes the document to human review and does not invent a value.

## 5. SKU Matching

### AC-10 — Matching SKU
**Given** a supplier MPN present in the BOM/SKU cross-reference  
**When** SKU resolution runs  
**Then** the corresponding internal SKU is returned.

### AC-11 — Unmatched SKU
**Given** an extracted MPN not present in the current catalog  
**When** SKU resolution runs  
**Then** the result is explicitly marked as unmatched and the policy limitation is visible to the reviewer.

## 6. Rule Engine

### AC-12 — Deterministic decision
**Given** the same structured input and policy configuration  
**When** the rule engine executes repeatedly  
**Then** it produces the same status and severity score.

### AC-13 — Expired certificate
**Given** an applicable certificate whose expiration date is in the past  
**When** the rule engine runs  
**Then** the configured expired-certificate rule is triggered.

### AC-14 — Excess measured lead
**Given** an actual measured lead result above the configured statutory threshold  
**When** the rule engine runs  
**Then** the configured lead-excess rule is triggered.

### AC-15 — No measured lead value
**Given** no measured lead result exists  
**When** the rule engine runs  
**Then** it does not interpret `null` as zero and does not claim a passing measured-lead test.

## 7. Gap Notice

### AC-16 — Generate notice
**Given** an audit result of `FLAGGED` or `REJECTED`  
**When** the Gap Notice generator runs  
**Then** it produces a structured notice containing supplier, document, failed rules, evidence, and requested corrective action.

### AC-17 — Human approval
**Given** a generated Gap Notice  
**When** a reviewer opens it  
**Then** the reviewer can inspect/edit it before it is sent externally.

## 8. Observability

### AC-18 — LangSmith trace
**Given** a workflow execution  
**When** the LangGraph pipeline completes  
**Then** the run is observable as a trace containing the relevant graph execution path and extraction/reconciliation activity.

## 9. Audit Copilot Chat

### AC-19 — Copilot availability

**Given** a reviewer is viewing an audit
**When** the audit review interface loads
**Then** the Audit Copilot is available within the audit review context.

### AC-20 — Audit-scoped context

**Given** a reviewer has selected an audit
**When** the reviewer sends a message to Copilot
**Then** Copilot receives and uses the context of the selected audit.

### AC-21 — Finding investigation

**Given** an audit contains one or more findings
**When** the reviewer asks Copilot about a finding
**Then** Copilot can explain the finding using the available audit data.

### AC-22 — Evidence explanation

**Given** a finding has supporting evidence
**When** the reviewer asks why the finding was triggered
**Then** Copilot identifies and explains the relevant evidence and rule result.

### AC-23 — No modification of audit results

**Given** an audit contains an existing deterministic rule result
**When** the reviewer interacts with Copilot
**Then** Copilot does not modify, override, or recalculate the audit result.

### AC-24 — Audit isolation

**Given** a reviewer is working within a selected audit
**When** the reviewer asks Copilot a question
**Then** Copilot does not expose information belonging to unrelated audits.

### AC-25 — Uncertainty and missing evidence

**Given** the available audit evidence is insufficient to answer a question
**When** the reviewer asks Copilot
**Then** Copilot explicitly states that the available evidence is insufficient and does not fabricate information.

### AC-26 — Human-in-the-loop

**Given** Copilot provides an explanation or recommendation
**When** the reviewer evaluates the audit
**Then** the reviewer remains responsible for the final compliance decision.

## 10. Benchmark Threshold

For the Round 2 MVP, the target is **>=90% extraction accuracy against manually established ground truth** on the expanded real-world test set, with explicit reporting by field and document type.

The existing Round 1 benchmark result of 12/12 correct is retained as the current benchmark result; it should not be interpreted as proof of generalization to all future PDFs.
