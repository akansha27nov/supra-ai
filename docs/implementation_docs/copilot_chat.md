# Audit Copilot Chat

## 1. Overview

Audit Copilot Chat is an audit-scoped conversational assistant that helps a human reviewer understand and investigate the findings produced by the Supra AI compliance audit.

The assistant is intentionally scoped to the currently selected audit. It uses the audit's findings, extracted document information, compliance-rule results, SKU context, and available evidence to answer reviewer questions.

The Copilot is an **interpretation and investigation layer**, not the compliance decision engine.

The system follows this principle:

> **AI explains the audit; deterministic rules determine the result; humans make the final decision.**

## 2. Why Copilot Chat Exists

The compliance dashboard identifies findings such as:

- Missing documentation
- Expired certificates
- Failed or incomplete checks
- Inconsistent supplier/product information
- Evidence that requires human review

A reviewer often needs additional context before deciding what to do.

Instead of manually navigating between documents, extracted fields, rules, and audit results, the reviewer can ask questions such as:

- "Why was this SKU flagged?"
- "Which requirement failed?"
- "What evidence supports this finding?"
- "Is the certificate expired or simply missing an expiry date?"
- "Which supplier documents are relevant to this finding?"
- "What should I verify manually?"
- "Show me the evidence behind this result."
- "Are there other findings in this audit with the same issue?"

Copilot Chat reduces investigation time while keeping the underlying compliance decision transparent.

## 3. Scope

Copilot Chat is scoped to **one audit at a time**.

The assistant should only use information associated with the selected audit and its approved context.

### In scope

- Audit findings
- Audit status and summary
- Supplier information available to the audit
- SKU/product information available to the audit
- Extracted certificate/document fields
- Compliance-rule results
- Finding severity/status
- Evidence and document references
- Recommended reviewer actions
- Comparisons between findings within the same audit

### Out of scope

- Making a new compliance decision
- Changing the result of a deterministic rule
- Approving or rejecting a supplier
- Inventing missing evidence
- Treating an LLM response as regulatory advice
- Accessing unrelated audits unless explicitly supported by the product
- Modifying audit data through chat

## 4. User Experience

The Copilot is exposed from the audit detail/review experience.

Conceptually:

```text
Audit
 │
 ├── Audit summary
 ├── Findings
 │    ├── Finding A
 │    ├── Finding B
 │    └── Finding C
 │
 ├── Evidence
 │
 └── Copilot Chat
       │
       ├── Audit context
       ├── Finding context
       ├── Evidence context
       └── Conversation
```

When the reviewer opens Copilot from an audit, the selected audit becomes the root context for the conversation.

When the reviewer opens Copilot from a particular finding, that finding should become the initial focus while retaining the surrounding audit context.

## 5. Context Model

The chat request should be constructed from structured audit data rather than passing an entire application state to the model.

Recommended context hierarchy:

```text
Audit
 ├── audit_id
 ├── audit status
 ├── audit summary
 │
 ├── Findings
 │    ├── finding_id
 │    ├── SKU
 │    ├── supplier
 │    ├── rule/result
 │    ├── severity
 │    └── status
 │
 ├── Evidence
 │    ├── document
 │    ├── extracted fields
 │    └── source/reference
 │
 └── Compliance rules
      ├── rule ID
      ├── requirement
      └── deterministic result
```

The model should receive the minimum context required to answer the question.

## 6. Core Principle: Evidence-First Answers

Copilot responses should be grounded in the audit evidence.

Where possible, responses should distinguish between:

1. **Observed evidence**
2. **Deterministic rule result**
3. **AI interpretation**
4. **Recommended human follow-up**

Example:

```text
Finding: CE declaration missing

Evidence:
No CE declaration was found for SKU ABC-123 in the documents
associated with this audit.

Rule result:
FAIL — CE declaration is mandatory for this SKU.

Interpretation:
The audit currently has insufficient evidence of CE conformity.

Recommended human action:
Confirm whether the declaration exists outside the supplied document set
before taking a final supplier/compliance action.
```

This separation is important because the assistant must not turn an inference into a fact.

## 7. Response Behaviour

Copilot should:

- Answer using the selected audit context.
- Prefer structured audit data over assumptions.
- Reference the relevant finding or evidence.
- Clearly state when information is unavailable.
- Distinguish evidence from interpretation.
- Recommend human verification when appropriate.
- Avoid changing the audit result.
- Avoid presenting regulatory conclusions beyond the rules represented in the system.

Copilot should not:

- Hallucinate certificates, dates, suppliers, or standards.
- Claim that a document exists when it is not in the audit context.
- Override a deterministic compliance rule.
- Convert an ambiguous finding into a definitive compliance conclusion.
- Hide uncertainty from the reviewer.

## 8. Example Questions

### Finding investigation

```text
Why was SKU ABC-123 flagged?
```

Expected response structure:

```text
The SKU was flagged because the audit rule requiring [requirement]
returned FAIL.

Evidence:
[relevant evidence]

Rule:
[rule/result]

What to verify:
[human review step]
```

### Evidence investigation

```text
What evidence caused this finding?
```

The response should identify the relevant document/extracted field and explain how it relates to the rule result.

### Audit-level investigation

```text
What are the most important issues in this audit?
```

The assistant should summarise the existing findings rather than independently re-score the audit.

### Human-review support

```text
What should I verify before approving this supplier?
```

The response should turn the existing findings into a practical reviewer checklist.

## 9. Architecture

The recommended flow is:

```text
Reviewer
   │
   ▼
Audit Copilot UI
   │
   ▼
Chat API / Copilot service
   │
   ├── Audit context loader
   │
   ├── Finding/evidence retrieval
   │
   └── Conversation history
   │
   ▼
LLM
   │
   ▼
Grounded response
   │
   ▼
Reviewer
```

The Copilot should sit **after the audit pipeline**, rather than replacing it.

```text
Supplier documents
       │
       ▼
Document extraction
       │
       ▼
Compliance rules ───────► Audit result
       │                       │
       │                       ▼
       └──────────────► Copilot Chat
                              │
                              ▼
                         Human reviewer
```

This preserves the existing system's separation between AI extraction, deterministic compliance evaluation, and human approval.

## 10. Relationship to the Existing Agent

The existing `agent/` implementation contains the agentic extraction and compliance workflow.

Copilot Chat should not duplicate that workflow.

The responsibilities should remain separated:

| Component | Responsibility |
|---|---|
| Document extraction | Extract structured information |
| Compliance rule engine | Determine rule results |
| Audit pipeline | Produce findings and evidence |
| Dashboard | Present audit results |
| Copilot Chat | Explain/investigate existing results |
| Human reviewer | Make final business/compliance decision |

This separation prevents the conversational model from becoming an uncontrolled second compliance engine.

## 11. Guardrails

Every chat request should carry an explicit audit identifier.

Conceptually:

```json
{
  "audit_id": "<selected-audit>",
  "finding_id": "<optional-selected-finding>",
  "message": "<reviewer question>"
}
```

The backend should resolve the permitted context from `audit_id` rather than trusting arbitrary context supplied by the client.

The model should be instructed that:

```text
You are an audit investigation assistant.

Use only the supplied audit context.

Do not invent evidence.

Do not change or override deterministic compliance results.

If evidence is insufficient, say so.

Clearly distinguish:
- evidence
- rule result
- interpretation
- recommended human verification

The human reviewer remains responsible for the final decision.
```

## 12. Auditability

Copilot interactions should be observable independently from the compliance result.

At minimum, log:

- `audit_id`
- `finding_id` when applicable
- timestamp
- user/session identifier where appropriate
- question
- response
- model/version
- retrieved context identifiers
- latency
- error status

Do not rely on chat history alone as evidence of the compliance decision.

The authoritative audit result remains the structured audit output and deterministic rule evaluation.

## 13. Observability

The existing project already uses LangSmith for pipeline tracing and evaluation.

Copilot Chat should use the same observability approach where practical, while keeping chat traces distinguishable from the core compliance pipeline.

Recommended trace metadata:

```text
feature = audit_copilot
audit_id = ...
finding_id = ...
model = ...
environment = ...
```

Useful metrics include:

- Chat requests per audit
- Response latency
- Error rate
- Average conversation length
- Retrieval/context failures
- Questions with insufficient evidence
- Reviewer feedback
- Most common question categories

## 14. Security and Data Boundaries

Because audit documents can contain supplier and product information, the Copilot must inherit the access controls of the underlying audit.

A user who cannot access an audit should not be able to query it through Copilot.

The chat layer should also avoid exposing unrelated audit information through conversational context.

Sensitive document contents should only be supplied to the model when required to answer the question.

## 15. Known Limitations

Copilot Chat does not independently establish regulatory compliance.

Its answers are dependent on:

- The quality of extracted document data
- The completeness of the selected audit
- The deterministic rules implemented by the system
- The evidence available to the model
- The model's ability to interpret that evidence

If evidence is missing, the correct response is to surface the gap rather than infer the missing information.

## 16. Acceptance Criteria

Copilot Chat is considered successfully implemented when:

- [ ] Chat can be opened from a specific audit.
- [ ] Chat receives the correct audit context.
- [ ] Chat can optionally focus on a selected finding.
- [ ] Responses are grounded in audit evidence.
- [ ] The assistant can explain why a finding exists.
- [ ] The assistant can identify supporting evidence.
- [ ] The assistant does not modify deterministic compliance results.
- [ ] The assistant explicitly communicates missing/uncertain evidence.
- [ ] Audit boundaries are enforced server-side.
- [ ] Chat interactions are observable.
- [ ] Human review remains the final decision point.

## 17. Example End-to-End Interaction

**Reviewer**

> Why is this supplier showing a high-risk finding?

**Copilot**

> The supplier is flagged because two findings in this audit require human review.
>
> **Finding 1:** The required CE declaration was not found for SKU ABC-123.  
> **Rule result:** FAIL.  
> **Evidence:** No matching declaration appears in the documents supplied for this audit.
>
> **Finding 2:** The available certificate has an expiry date that is earlier than the audit review date.  
> **Rule result:** FAIL.
>
> Based on the current audit evidence, the supplier should remain in human review. The audit does not establish whether additional documents exist outside the supplied document set.

This is the intended behaviour: **explain the existing audit rather than inventing a new decision.**

## 18. Implementation References

Relevant implementation areas:

```text
agent/
    # audit/extraction/rule workflow

dashboard/
    # audit review experience

docs/
    implementation_docs/
        copilot_audit_chat.md
```

The README should link to this document under the implementation/documentation section.

## 19. Product Positioning

Copilot Chat should be described as:

> **An audit-aware investigation assistant that helps reviewers understand findings, trace evidence, and decide what to verify next.**

It should not be described as:

> "An AI that determines supplier compliance."

The distinction is central to Supra AI's trust, transparency, and human-in-the-loop design.