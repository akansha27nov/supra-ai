# Supra AI — ROI and Risk Assessment

## 1. Executive Summary

Supra AI is an AI-assisted supplier compliance screening system for a mid-sized European consumer-electronics retailer.

The main expected business benefit is reduced reviewer effort when processing supplier compliance documents. The system is not expected to generate significant value through AI-inference cost savings because the estimated AI processing cost is already very low. The primary value driver is therefore the reviewer time released by faster document extraction, validation, and prioritisation.

The ROI analysis uses three scenarios:

- Conservative
- Base case
- Optimistic

The calculations are based on planning assumptions rather than measured customer results. Actual savings and ROI should be recalculated during a pilot using measured manual and AI-assisted screening times.

Under the base-case assumptions:

- Estimated annual labour-value opportunity: **€18,000**
- Estimated 12-month ROI: **274%**
- Estimated 36-month ROI: **781%**
- Estimated break-even point: **approximately 3 months**

These figures represent the value of reviewer capacity released. They should not automatically be interpreted as direct payroll reductions.

---

## 2. ROI Assumptions

| Assumption | Conservative | Base Case | Optimistic |
|---|---:|---:|---:|
| Active SKUs | 2,000 | 2,000 | 2,000 |
| Documents processed per month | 150 | 150 | 150 |
| Documents processed per year | 1,800 | 1,800 | 1,800 |
| Manual review time per document | 30 minutes | 30 minutes | 30 minutes |
| Estimated time saved with Supra AI | 20% | 40% | 60% |
| Reviewer loaded cost per hour | €40 | €50 | €60 |
| Upfront implementation cost | €5,000 | €4,150 | €3,300 |
| Monthly tooling cost | €90 | €55 | €20 |
| Estimated AI inference cost | Approximately $0.0004/document | Approximately $0.0004/document | Approximately $0.0004/document |

### Assumption Classification

| Type | Items |
|---|---|
| Measured or documented project value | Estimated AI processing cost of approximately $0.0004 per document |
| Repository/project assumptions | Approximately 2,000 active SKUs; approximately 150 documents per month |
| Planning assumptions | 30 minutes manual review time; €40–€60 reviewer cost per hour; 20%–60% time savings |
| Calculated outputs | Annual benefit, total cost, net benefit, ROI, and break-even period |
| Initial assessment | Likelihood and impact ratings in the risk matrix |
| Pilot validation requirements | Actual review time, actual time saved, reviewer cost, document volume, error rates, and production tooling costs |

The assumptions of 30 minutes per document, €50 per hour, and 40% time saved in the base case are planning assumptions. They have not yet been validated through a live customer pilot.

---

## 3. Upfront Costs

The estimated upfront implementation cost is based on the existing project cost analysis.

| Cost component | Estimated range | Base-case treatment |
|---|---:|---:|
| Solution design and workflow configuration | Included in estimate | Included |
| AI extraction and validation pipeline | Included in estimate | Included |
| Initial data preparation and test dataset | Included in estimate | Included |
| MVP interface and integration work | Included in estimate | Included |
| Testing, documentation, and deployment preparation | Included in estimate | Included |
| Total upfront implementation | €3,300–€5,000 | €4,150 |

The base case uses the midpoint of the estimated implementation range:

```text
(€3,300 + €5,000) / 2 = €4,150
```

The upfront estimate represents a focused pilot/MVP implementation. It does not represent the cost of a full enterprise deployment.

---
## 4. Ongoing Costs

| Ongoing cost | Conservative | Base Case | Optimistic |
|---|---:|---:|---:|
| Monthly tooling and platform costs | €90 | €55 | €20 |
| Annual tooling cost | €1,080 | €660 | €240 |
| 36-month tooling cost | €3,240 | €1,980 | €720 |
| Estimated AI inference cost | Low relative to reviewer labour | Low relative to reviewer labour | Low relative to reviewer labour |

The ongoing tooling estimate may include workflow automation, hosting, monitoring, storage, API usage, and related platform costs. Actual production costs may increase if document volume, retention, integration complexity, or monitoring requirements increase.

---
## 5. Quantified Business Value

### Annual Document Volume

```text
150 documents/month × 12 months = 1,800 documents/year
```

### Annual Manual Review Effort

```text
1,800 documents/year × 0.5 hours/document = 900 reviewer hours/year
```

### Annual Manual Review Value

```text
900 hours/year × €50/hour = €45,000/year
```

### Base-Case Labour-Value Opportunity

```text
€45,000 × 40% = €18,000/year
```

Therefore:

>The estimated annual labour-value opportunity is **€18,000** under the base-case planning assumptions.

This represents reviewer capacity released by reducing screening effort. It does not necessarily represent an immediate reduction in payroll expenditure. The released capacity may instead be used for deeper investigations, supplier follow-up, audit preparation, or other higher-value compliance work.

## 6. 12-Month ROI

**Formula** 
>ROI = (Net Benefit / Total Cost) × 100

Where:
```text
Net Benefit = Business Benefit − Total Cost
```

### Base-Case Calculation
**Annual benefit**
```text
1,800 documents × 0.5 hours × €50/hour × 40% = €18,000
```

**Total 12-month cost**
```text
€4,150 upfront implementation + (€55 monthly tooling × 12 months)
= €4,150 + €660
= €4,810
```

**Net benefit**
```text
€18,000 − €4,810 = €13,190
```

**12-month ROI**
```text
(€13,190 / €4,810) × 100 = 274.22%
```

## 7. 36-Month ROI
### Base-Case Calculation

**Three-year benefit**
```text
€18,000 annual benefit × 3 years = €54,000
```

**Total 36-month cost**
```text
€4,150 upfront implementation
+ (€55 monthly tooling × 36 months)
= €4,150 + €1,980
= €6,130
```

**Net benefit**
```text
€54,000 − €6,130 = €47,870
```

**36-month ROI**
```text
(€47,870 / €6,130) × 100 = 780.91%
```
*Estimated base-case 36-month ROI: approximately 781%.*

## 8. Break-Even Analysis
The base-case monthly labour-value opportunity is:
```text
€18,000 annual benefit / 12 months = €1,500/month
```

The estimated break-even period is:
```text
€4,150 upfront implementation cost / €1,500 monthly benefit = 2.77 months
```
>Estimated base-case break-even: approximately 3 months.

This is a simplified estimate. It excludes possible onboarding delays, training time, migration costs, internal project-management effort, and temporary parallel running of manual and automated processes.

Actual break-even should be recalculated during the pilot using measured review time before and after implementation.

## 9. Sensitivity Analysis

| Metric | Conservative | Base Case | Optimistic |
|---|---:|---:|---:|
| Annual benefit | €7,200 | €18,000 | €32,400 |
| 12-month total cost | €6,080 | €4,810 | €3,540 |
| 12-month net benefit | €1,120 | €13,190 | €28,860 |
| 12-month ROI | 18% | 274% | 274% |
| 36-month total cost | €8,240 | €6,130 | €4,020 |
| 36-month benefit | €21,600 | €54,000 | €97,200 |
| 36-month net benefit | €13,360 | €47,870 | €93,180 |
| 36-month ROI | 162% | 781% | 2,318% |
| Approximate break-even | 8.3 months | 2.8 months | 1.2 months |


### Scenario Calculations
### Conservative Scenario

```text
1,800 documents × 0.5 hours × €40/hour × 20% = €7,200 annual benefit
```

```text
12-month cost = €5,000 + (€90 × 12) = €6,080
12-month ROI = (€7,200 − €6,080) / €6,080 × 100
≈ 18%
```

### Base-Case Scenario

```text
1,800 documents × 0.5 hours × €50/hour × 40% = €18,000 annual benefit
```

```text
12-month cost = €4,150 + (€55 × 12) = €4,810
12-month ROI ≈ 274%
```

### Optimistic Scenario

```text
1,800 documents × 0.5 hours × €60/hour × 60% = = €32,400 annual benefit
```

```text
12-month cost = €3,300 + (€20 × 12) = €3,540
12-month ROI ≈ 815%
```

The sensitivity analysis demonstrates that ROI is primarily driven by:

- Actual manual review time per document.
- Actual reviewer labour cost.
- Percentage of screening effort saved.
- Monthly document volume.
- Implementation and tooling costs.

The largest uncertainty is not the AI inference cost. It is whether the system achieves the assumed reduction in human screening effort.

## 10. Risk Assessment

Risk scores use the following formula:

```text
Risk Score = Likelihood × Impact
```

Both likelihood and impact are rated from 1 to 5.

These are initial assessment scores for the MVP and should be reviewed during the pilot.

| # | Risk | Category | Likelihood | Impact | Score | Mitigation |
|---:|---|---|---:|---:|---:|---|
| 1 | Incorrect extraction causes a missed or incorrect finding | Technical | 3 | 5 | 15 | Use labelled evaluation data, field-level accuracy checks, evidence-linked extraction, confidence thresholds, and mandatory human review |
| 2 | Compliance rules become outdated or incomplete | Regulatory | 3 | 5 | 15 | Version all rules, assign rule ownership, schedule periodic regulatory review, and require approval before rule changes are deployed |
| 3 | Users treat AI output as a final compliance decision | Ethical / Governance | 2 | 5 | 10 | Maintain mandatory human approval, display clear decision boundaries, separate extracted facts from interpretations, and log reviewer decisions |
| 4 | Supplier documents contain confidential or personal information | Privacy / Technical | 3 | 4 | 12 | Apply data minimisation, use synthetic/public data for the capstone, restrict access, define retention controls, and document data flows |
| 5 | Poor-quality or scanned PDFs reduce extraction accuracy | Technical | 4 | 4 | 16 | Add document-quality detection, OCR fallback where available, unsupported-format handling, and human escalation |
| 6 | API, workflow, or LLM outage interrupts screening | Operational | 3 | 4 | 12 | Use retries, queues, monitoring, failure alerts, logging, and a documented manual fallback process |
| 7 | Incorrect SKU matching produces an incorrect screening result | Operational / Technical | 3 | 5 | 15 | Use exact and normalised matching, detect ambiguity, require human review for uncertain matches, and retain the source values |
| 8 | ROI assumptions overestimate actual time savings | Business | 3 | 3 | 9 | Measure manual baseline time, compare before-and-after screening time during the pilot, and update the financial model using observed results |

### Risk Score Classification

| Score | Level | Recommended Treatment |
|---:|---|---|
| 1–4 | Low | Monitor through normal project controls |
| 5–9 | Medium | Define an owner and review periodically |
| 10–14 | High | Implement documented mitigation before pilot expansion |
| 15–25 | Critical | Treat as a deployment blocker until adequately controlled |

## 11. Risk Matrix

The following matrix shows the initial risk position before mitigation.

| Impact \ Likelihood | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| 5 | 5 | 10 | 15 | 20 | 25 |
| 4 | 4 | 8 | 12 | 16 | 20 |
| 3 | 3 | 6 | 9 | 12 | 15 |
| 2 | 2 | 4 | 6 | 8 | 10 |
| 1 | 1 | 2 | 3 | 4 | 5 |

Initial highest-priority risks are:

- Poor-quality document processing: score 16
- Incorrect extraction: score 15
- Outdated compliance rules: score 15
- Incorrect SKU matching: score 15

These risks should receive priority during MVP testing and pilot planning.

## 12. Limitations and Validation Plan

### Limitations

The ROI model has the following limitations:

- The manual review time is a planning assumption.
- The reviewer cost per hour is a planning assumption.
- The percentage of time saved is not yet measured in a live environment.
- The document volume is based on an estimated workload of approximately 150 documents per month.
- The implementation cost represents a focused MVP rather than a full enterprise deployment.
- The tooling estimate may change depending on hosting, API usage, storage, monitoring, security, and integration requirements.
- Reviewer time released does not necessarily result in direct payroll savings.
- The model does not quantify avoided regulatory penalties, faster supplier onboarding, reduced audit preparation time, or improved supplier relationships.
- The model does not assign a monetary value to improved traceability or reduced compliance uncertainty.

### Pilot Validation Plan

During the pilot, the following metrics should be collected:

| Metric | Measurement Approach |
|---|---|
| Manual baseline time | Measure the time required to screen a defined sample without Supra AI |
| AI-assisted screening time | Measure the time required using Supra AI, including human review |
| Time saved | Compare baseline and AI-assisted screening time |
| Extraction accuracy | Compare extracted fields with manually labelled ground truth |
| Flag precision | Measure how many generated flags are confirmed by reviewers |
| Missed findings | Identify issues present in documents but not flagged by the system |
| Human override rate | Record how often reviewers disagree with the system |
| Documents processed | Track monthly document volume |
| Cost per document | Track actual API, hosting, storage, and workflow costs |
| User acceptance | Collect structured feedback from compliance reviewers |

The ROI model should be updated after the pilot using observed data. The base-case assumptions should not be presented as measured customer outcomes until they have been validated.

## 13. Conclusion

Supra AI has a potentially attractive ROI profile because the expected value is driven by reviewer time saved, while estimated AI processing costs are minimal.

The base-case scenario indicates:

- €18,000 estimated annual labour-value opportunity
- 274% estimated 12-month ROI
- 781% estimated 36-month ROI
- Approximately 3-month estimated break-even

These results are scenario-based planning estimates, not confirmed customer savings. The recommended next step is a controlled pilot that measures the manual baseline, AI-assisted review time, extraction accuracy, flag quality, and actual operating costs.

The business case should be considered successful only if the pilot confirms that efficiency gains are achieved without reducing evidence quality, human oversight, or compliance accountability.