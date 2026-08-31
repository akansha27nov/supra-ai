# Agentic Extraction Pipeline (LangGraph) Implementation

This document details the LangGraph-based compliance screening architecture, designed to replace rigid single-shot extraction with a stateful, agentic workflow capable of bounded retries, classification-aware validation, and graceful human escalation.

## Core State (`AuditState`)
The pipeline passes a typed dictionary (`AuditState`) through each node, ensuring data mutation is structured and observable:
* **`raw_text`**: The unstructured text extracted from the PDF via `pdfplumber`.
* **`doc_type`**: The identified nature of the document (`lab_test_report`, `manufacturer_self_declaration`, `unknown`).
* **`extracted`**: The structured fields (e.g., SKU, dates, limits) captured by the LLM.
* **`field_status`**: Tracks the logical state of every field (`present`, `absent_expected`, `absent_appropriate`, `ambiguous`). This eliminates "false precision" where the LLM guesses a value that shouldn't exist.
* **`reconciliation_attempts`**: An integer counter capping retry loops to control costs and latency.
* **`needs_human_review`**: A boolean flag for first-class human escalation.
* **`audit_result`**: The final deterministic output from the rule engine.

## Node Topology

### 1. Extraction Node (`extract_node`)
Performs the initial pass over the raw text using `gpt-4o-mini` with a structured output schema (`ExtractedCertificateData`). It captures explicit values and distinguishes between measured test results and statutory limits.

### 2. Classification Node (`classify_doc_type_node`)
Before evaluating whether missing data constitutes a failure, this node classifies the document context. For example, a manufacturer self-declaration is not expected to contain a lab accreditation ID or an expiration date. 

### 3. Validation Node (`validate_fields_node`)
Evaluates the extracted fields against the document type. It assigns a status to each field:
* **`present`**: Valid data exists.
* **`absent_appropriate`**: Data is missing, but this is legally correct for the document type (e.g., no expiration date on a self-declaration).
* **`absent_expected`**: Data is missing and must be found (triggers a reconciliation retry).

### 4. Reconciliation Node (`reconcile_node`)
If fields are marked `absent_expected` or `ambiguous`, this node performs a targeted re-read of the document, specifically asking the LLM to locate the missing parameters. It is strictly bounded to a maximum of 2 attempts.

### 5. Rule Engine Node (`rule_engine_node`)
The deterministic arbiter. It evaluates the clean `extracted` data against hardcoded compliance thresholds (e.g., Lead > 1000 ppm). It explicitly ignores fields marked `absent_appropriate`, preventing crashes or false rejections. It scores the document and issues an `APPROVED`, `FLAGGED`, or `REJECTED` decision.

### 6. Human Review Node (`flag_for_human_review_node`)
If ambiguities persist after the 2-attempt reconciliation limit, the graph routes here. It outputs a `REQUIRES_HUMAN_REVIEW` decision, ensuring the system admits uncertainty rather than hallucinating passing data.

## Conditional Routing (Edges)
The flow depends heavily on the output of the Validation Node:
1. **If all fields are resolved** (either `present` or `absent_appropriate`): Route directly to the Rule Engine.
2. **If fields are missing and retries < 2**: Route to the Reconciliation Node for a targeted re-extraction, then loop back to Validation.
3. **If fields are missing and retries == 2**: Route to the Human Review Node to halt the loop and flag the document.