# Round 1 Decision — Supra AI Compliance Auditor

## 1. Decision Summary

**Decision: Proceed to Round 2 with the existing architecture as the baseline, while prioritizing real-world validation and LangGraph-based extraction improvements.**

Round 1 successfully established the core proof of concept:

- PDF documents can be converted into structured compliance data.
- Structured data can be passed to a deterministic rule engine.
- Screening results can be exported for Tableau.
- LangSmith can provide observability around the AI extraction/screening workflow.
- The benchmark suite produced 7/7 correct synthetic results and 5/5 correct real-world results, for 12/12 on the current benchmark set.

These results justify continuing the project, but **do not justify claiming that the system is generally solved or production-ready**. The real-world set is still small and currently consists of five manufacturer self-declarations.

## 2. Key Round 1 Evidence

### Synthetic benchmark

**7/7 correct (100%)**

The synthetic set validates the intended policy behavior across representative edge cases such as expiry, missing standards, excess lead, suspicious laboratory information, and valid certificates.

### Real-world benchmark

**5/5 correct (100%) on the current labeled set**

The five real documents are manufacturer Declarations of Conformity from public sources. They provide valuable evidence that the pipeline can operate on genuine documents, but they do not yet represent the full target document population.

```text
python langsmith/master_benchmark.py
=====================================================================================
      SUPRA AI COMPLIANCE AUDITOR - MASTER BENCHMARK SUITE
=====================================================================================

=====================================================================================
  RUNNING BENCHMARK: SYNTHETIC
=====================================================================================
File                                     Expected        Actual          Status
-------------------------------------------------------------------------------------
cert_02_expired_elec.pdf                 REJECTED/90     REJECTED/90     [PASS]
cert_04_valid_wireless_earbuds.pdf       PASS/10         PASS/10         [PASS]
cert_05_missing_red_smartwatch.pdf       FLAGGED/75      FLAGGED/75      [PASS]
cert_06_excess_lead_powerbank.pdf        REJECTED/95     REJECTED/95     [PASS]
cert_07_suspicious_lab_monitor.pdf       REJECTED/85     REJECTED/85     [PASS]
cert_08_expiring_soon_usb_hub.pdf        FLAGGED/60      FLAGGED/60      [PASS]
cert_09_valid_smart_speaker.pdf          PASS/10         PASS/10         [PASS]
-------------------------------------------------------------------------------------
Subtotal (Synthetic): 7/7 correct (100.0% accuracy)

=====================================================================================
  RUNNING BENCHMARK: REAL-WORLD
=====================================================================================
File                                     Expected        Actual          Status
-------------------------------------------------------------------------------------
03- RoHS DoC V2023012303 Envoys.pdf      FLAGGED/55      FLAGGED/55      [PASS]
ACH480_RoHS_DoC.pdf                      FLAGGED/75      FLAGGED/75      [PASS]
RoHS-Certificate-of-Compliance-Concens   FLAGGED/65      FLAGGED/65      [PASS]
RoHS_REACH_PROP65_Declaration_of_Confo   PASS/10         PASS/10         [PASS]
UNOnext_CE_ROHS_Delta.pdf                PASS/10         PASS/10         [PASS]
-------------------------------------------------------------------------------------
Subtotal (Real-World): 5/5 correct (100.0% accuracy)

-------------------------------------------------------------------------------------
  GENERATING TABLEAU EXPORTS
-------------------------------------------------------------------------------------
  ✅ Saved Synthetic Export: /Users/akanshaverma/Projects/AC-bootcamp/supra-ai/data/tableau_export.csv
  ✅ Saved Real-World Export: /Users/akanshaverma/Projects/AC-bootcamp/supra-ai/data/tableau_export_real.csv
  ✅ Saved Combined Master Export: /Users/akanshaverma/Projects/AC-bootcamp/supra-ai/data/tableau_export_combined.csv

#####################################################################################
                      COMBINED BENCHMARK SUMMARY
#####################################################################################
  • Synthetic Dataset Accuracy : 7/7 (100.0%)
  • Real-World Dataset Accuracy: 5/5 (100.0%)
  -------------------------------------------------------------
  • OVERALL ACCURACY           : 12/12 (100.0%)
#####################################################################################
```

### Important limitation

The current real-world set does not yet provide enough laboratory-test-report coverage to demonstrate robust handling of actual measured chemical concentrations in lab tables.

## 3. Decision Rationale

The most important lesson from Round 1 was not simply the benchmark percentage. It was the discovery of real-world failure modes:

1. Missing expiration dates exposed an assumption in the original rule-engine input handling.
2. Legal RoHS thresholds could be mistaken for measured chemical values.
3. Synthetic SKU catalogs naturally produced unmatched-SKU warnings when applied to real documents.
4. Real supplier documents have different valid shapes depending on whether they are self-declarations or laboratory reports.

These findings support the proposed LangGraph design.

LangGraph is therefore being introduced specifically to provide:

- document-type-aware validation,
- explicit missing/not-applicable states,
- targeted reconciliation,
- bounded retries,
- and human-review route.

The deterministic rule engine remains the policy decision layer.

## 4. Round 2 Priority Order

The implementation order is intentionally risk-first:

1. **LangGraph extraction and validation**
2. **Real laboratory test reports + ground truth**
3. **SKU/BOM cross-reference validation**
4. **Supplier Gap Notice**
5. **Streamlit front end**
6. **Tableau/business metrics/final presentation**

This order follows the principle discussed during review: identify the technically difficult part early so that later UI and presentation work is not built on an unreliable extraction foundation.

## 5. What Round 1 Does and Does Not Prove

### Round 1 demonstrates

- The end-to-end concept is feasible.
- Deterministic policy screening can be separated from AI extraction.
- The pipeline can produce stakeholder-facing structured output.
- Real-world documents reveal useful failure modes that synthetic data alone would not expose.
- The current benchmark can be reproduced.

### Round 1 does not demonstrate

- Production-scale reliability.
- Generalization to all EU electrical-product documentation.
- Reliable interpretation of every laboratory chemical table.
- Complete SKU coverage.
- Autonomous compliance decision-making.
- A measured client ROI.

## 6. Round 2 Success Decision

Round 2 should be considered successful if it can demonstrate:

- 90% extraction accuracy against the agreed expanded ground-truth set;
- safe handling of missing/non-applicable fields;
- correct distinction between legal thresholds and measured results;
- deterministic and reproducible rule execution;
- traceable LangSmith/LangGraph execution;
- actionable Supplier Gap Notices;
- a usable reviewer-facing UI;
- and a clear Tableau reporting path.

If a serious extraction limitation is discovered during real laboratory-report testing, the plan should adapt by prioritizing that limitation over lower-risk presentation polish.
