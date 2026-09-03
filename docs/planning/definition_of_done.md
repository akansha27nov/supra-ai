# Supra AI Compliance Auditor — Definition of Done

## 1. Definition of Done for the Round 2 MVP

A feature or milestone is considered done only when the implementation is working, testable, observable, documented, and demonstrated against representative data.

## 2. Technical DoD

- [ ] Code is committed to the existing repository with logical, descriptive commits.
- [ ] Existing Round 1 outputs remain reproducible and are not overwritten by Round 2 work.
- [ ] LangGraph `StateGraph` is implemented with explicit state and conditional routing.
- [ ] PDF text extraction succeeds on the supported test documents.
- [ ] LLM extraction produces the agreed structured schema.
- [ ] Missing and non-applicable fields are represented explicitly rather than guessed.
- [ ] Chemical legal limits are distinguishable from measured laboratory values.
- [ ] Reconciliation is bounded (maximum two attempts) and unresolved cases route to human review.
- [ ] Deterministic rule-engine logic remains separate from LLM reasoning.
- [ ] No known unhandled exception occurs for the five real-world DoCs already tested.
- [ ] LangSmith provides a trace for end-to-end graph execution.
- [ ] Audit Copilot Chat is available from the audit review context.
- [ ] Copilot requests are explicitly scoped to the selected audit.
- [ ] Copilot can access the relevant findings and supporting evidence for the selected audit.
- [ ] Copilot does not access or expose information from unrelated audits.
- [ ] Copilot does not modify or override deterministic rule-engine results.
- [ ] Copilot explicitly communicates missing, ambiguous, or insufficient evidence rather than fabricating information.
- [ ] Copilot conversation errors and failed requests are handled without breaking the audit-review workflow.

## 3. Data and Evaluation DoD

- [ ] Five existing real-world DoCs remain available as the first real-world regression set.
- [ ] Three to five real laboratory test reports are added where legally/publicly usable.
- [ ] Ground truth is manually established for the expanded real-world set.
- [ ] Extraction results are evaluated field-by-field.
- [ ] Overall extraction target is >=90% on the agreed benchmark.
- [ ] DoC and lab-report results are reported separately where useful.
- [ ] Tier 2 rule-engine tests cover representative APPROVED, FLAGGED, and REJECTED cases.
- [ ] Synthetic and real-world benchmark exports remain separately identifiable.
- [ ] Representative audit questions are tested against known findings and evidence.
- [ ] Copilot responses are evaluated for grounding against the selected audit context.
- [ ] Copilot is tested on findings with sufficient evidence and findings with missing/ambiguous evidence.
- [ ] Copilot is tested to confirm that it does not expose information from unrelated audits.

## 4. Business/Operational DoD

- [ ] Human review remains part of the workflow for flagged and uncertain cases.
- [ ] Reviewer can use Copilot to investigate and understand audit findings.
- [ ] Reviewer can identify the evidence and rule result relevant to a Copilot response.
- [ ] Copilot is clearly presented as reviewer assistance rather than the final compliance decision-maker.
- [ ] Copilot-assisted review/investigation time can be measured during the pilot where applicable.
- [ ] Reviewer can understand why a document received its status.
- [ ] Supplier Gap Notice can be generated from actual rule findings.
- [ ] Front-end prototype supports document upload and result inspection.
- [ ] Tableau export remains compatible with the existing dashboard.
- [ ] Pilot review time is measured rather than assumed where possible.

## 5. Documentation DoD

- [ ] User stories are documented.
- [ ] Acceptance criteria use explicit Given/When/Then statements for critical behavior.
- [ ] Rollout plan is documented across eight weeks.
- [ ] Failure-mode analysis is updated after each significant real-data test.
- [ ] README explains setup and the latest benchmark command.
- [ ] Environment variables are documented through `.env.example`.
- [ ] Round 1 is clearly separated from Round 2 through repository history, directories, filenames, or commits.
- [ ] Audit Copilot implementation is documented in `docs/implementation_docs/copilot_chat.md`.
- [ ] Audit Copilot user story is documented in `docs/planning/user_stories.md`.
- [ ] Audit Copilot acceptance criteria are documented using Given/When/Then statements.
- [ ] Audit Copilot's human-oversight and audit-scoping behaviour is documented.
- [ ] Strategic/deployment documentation identifies Audit Copilot as a reviewer-facing capability.
