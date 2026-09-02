# Supra AI — Strategic Deployment and Commercialisation Plan

## 1. Executive Summary

Supra AI is an AI-assisted supplier compliance screening platform for retailers and distributors of regulated products, initially focused on consumer electronics documentation.

The platform:

1. Ingests supplier compliance documents such as CE declarations, RoHS certificates and test reports.
2. Extracts structured information from PDFs using AI.
3. Checks extracted information against deterministic compliance rules and the internal SKU catalogue.
4. Prioritises incomplete, expired or inconsistent records.
5. Provides evidence-linked findings for human review and approval.

Supra AI is a screening and workflow-support tool, not an autonomous compliance decision-maker. Final compliance decisions remain with qualified human reviewers.

The recommended commercialisation path is:

> **Proof of Concept → Controlled Pilot → Production Deployment → Optional Multi-tenant Scale**

The first target customer is a mid-sized European omnichannel retailer with approximately 200 employees, 2,000 active SKUs and a mixed EU/non-EU supplier base.

---

## 2. Strategic Objectives

The deployment should achieve five objectives:

- Reduce manual effort in supplier document review.
- Improve visibility of missing, expired and inconsistent documentation.
- Create a repeatable, auditable review process.
- Reduce compliance risk without replacing human accountability.
- Establish a commercially viable product that can expand beyond the initial customer.

The initial product scope should remain deliberately narrow:

- Consumer electronics.
- PDF-based supplier documentation.
- CE, RoHS and related declarations or test reports.
- Human-in-the-loop review.
- Integration with the client's SKU catalogue and document repository.

Additional product categories and regulatory regimes should be added only after the initial workflow has demonstrated reliable performance.

---

## 3. Deployment Principles

### Human accountability

Supra AI should recommend and prioritise actions, but it should not approve a product for sale or make an unreviewed legal compliance determination.

### Evidence-first outputs

Every finding should link to:

- The source document.
- The relevant page or text excerpt.
- The extracted field.
- The rule that produced the finding.
- The reviewer decision and timestamp.

### Deterministic policy layer

AI should be used primarily for document understanding and field extraction. Compliance checks should remain transparent, testable and configurable through a rule engine.

### Measured deployment

Each phase should have explicit entry and exit criteria. Progression should depend on measured performance, reviewer feedback and operational readiness rather than the existence of a working demonstration alone.

### Narrow initial scope

The first production release should support a limited document and product scope. Broad generalisation should be treated as a later commercial expansion objective.

---

# 4. Deployment Phases

## Phase 1 — Proof of Concept

### Purpose

Demonstrate that Supra AI can process representative supplier documentation and produce useful, evidence-linked screening results for a defined set of products.

### Scope

- One business unit or product category.
- 50–100 representative documents.
- 25–50 SKUs.
- CE and RoHS-related documentation.
- Manual upload or controlled folder ingestion.
- Existing dashboard and benchmark pipeline.
- Human validation of every result.

### Key activities

- Confirm business requirements and compliance policy rules.
- Map the client's SKU catalogue and required documentation.
- Collect representative documents, including poor-quality and incomplete examples.
- Configure extraction schemas and deterministic rules.
- Establish a labelled validation set.
- Run the pipeline against historical documents.
- Record false positives, false negatives and extraction failures.
- Define the target operating procedure for human reviewers.

### Deliverables

- Configured POC environment.
- Initial SKU and rule catalogue.
- Document ingestion process.
- Extraction and audit results.
- Reviewer feedback log.
- Baseline accuracy and time-saving report.
- Pilot business case.
- Go/no-go decision for pilot.

### Exit criteria

The POC may proceed to pilot when:

- At least 90% of in-scope documents are processed successfully.
- At least 95% of mandatory fields are extracted correctly on the agreed validation set.
- No critical compliance finding is silently missed in the validation set.
- Every finding has an evidence reference.
- Reviewers can understand and validate the output without technical assistance.
- Data handling, access control and retention requirements are agreed.
- The customer confirms that the pilot has a defined owner, dataset and success criteria.

The POC should not be considered proof of production readiness. The repository's current 12/12 agreement with labelled examples is a useful feasibility signal, but the sample is too small to establish production-scale reliability.

---

## Phase 2 — Controlled Pilot

### Purpose

Validate operational value, reliability and adoption using the customer's real workflow and a broader sample of supplier documentation.

### Recommended duration

8–12 weeks.

### Scope

- One customer.
- One or two product categories.
- 500–1,500 documents.
- 200–500 SKUs.
- 10–20 internal users or reviewers.
- Historical and newly received documents.
- Human review of all flagged records and a sample of unflagged records.
- Controlled integration with the client's document repository or intake process.

### Key activities

- Import and normalise the agreed SKU catalogue.
- Configure supplier, product and documentation metadata.
- Create a document-quality and exception taxonomy.
- Train reviewers on the workflow.
- Run Supra AI in parallel with the existing process for an initial baseline period.
- Compare processing time, finding quality and escalation rates.
- Tune extraction prompts, schemas and rules.
- Add confidence thresholds and mandatory human-review gates.
- Establish incident, correction and model-change procedures.
- Monitor cost per document and processing latency.
- Conduct weekly pilot reviews with business stakeholders.

### Pilot workstreams

| Workstream | Pilot objective | Evidence of success |
|---|---|---|
| Extraction | Capture supplier, product, standard and validity fields | Labelled-set precision and recall |
| Rule screening | Identify missing, expired or inconsistent documentation | Correctly classified audit outcomes |
| Workflow | Fit into procurement and compliance operations | Reviewer completion and adoption data |
| Usability | Make findings understandable and actionable | Reviewer satisfaction and low clarification rate |
| Controls | Preserve human accountability and auditability | Complete review history and evidence links |
| Economics | Establish a credible unit-cost model | Measured cost per document and time saved |

### Pilot exit criteria

A pilot may be recommended for full deployment when all critical criteria below are met:

- **Document processing success:** at least 95% of in-scope documents complete without technical failure.
- **Mandatory-field extraction:** at least 97% precision on critical fields, including supplier, product, declaration date, standards and document type.
- **Critical miss rate:** zero unresolved silent misses for critical compliance conditions in the agreed test set.
- **Audit classification:** at least 95% agreement with expert-labelled outcomes for in-scope rules.
- **Human review performance:** at least 30% reduction in average review time compared with the baseline process.
- **Finding usefulness:** at least 80% of flagged findings are judged actionable by reviewers.
- **Evidence coverage:** 100% of findings include a source document and evidence location.
- **Adoption:** at least 80% of assigned reviewers use the system during the final four weeks of the pilot.
- **Operational availability:** at least 99% availability during agreed business hours, excluding planned maintenance.
- **Security and governance:** customer-approved access, retention, incident response and change-control procedures.
- **Business case:** measured benefits support the proposed production subscription and implementation cost.
- **Owner commitment:** a named business owner accepts responsibility for policy configuration and final decisions.

A single critical compliance miss, unresolved access-control issue or inability to explain findings should block full deployment until remediated.

---

## Phase 3 — Full Production Deployment

### Purpose

Make Supra AI part of the customer's standard supplier-documentation and product-onboarding process.

### Scope

- All agreed consumer-electronics suppliers.
- Full in-scope SKU catalogue.
- New document intake and historical backlog.
- Role-based access for procurement, compliance and operations.
- Production monitoring and support.
- Formal service-level agreement.
- Integration with document storage and, where appropriate, procurement or product-information systems.

### Key activities

- Migrate from pilot configuration to production infrastructure.
- Finalise integration with document repositories and intake channels.
- Establish production rule ownership and approval workflow.
- Backfill the agreed historical document set.
- Introduce supplier-facing remediation workflows.
- Create monthly performance and risk reporting.
- Schedule periodic rule, prompt and benchmark reviews.
- Add automated alerts for expiring or missing documentation.
- Implement disaster recovery and operational runbooks.
- Conduct quarterly business reviews.

### Production operating model

- **Procurement:** requests and follows up supplier documentation.
- **Compliance:** owns rules, reviews exceptions and approves final outcomes.
- **Supply-chain operations:** monitors supplier and product readiness.
- **IT or data team:** owns integrations, access and technical support.
- **Supra AI provider:** maintains the platform, extraction pipeline, monitoring and agreed configuration.
- **Business owner:** approves scope changes, risk tolerance and expansion decisions.

### Production success criteria

After the first 90 days, the deployment should demonstrate:

- Sustained processing success of at least 98%.
- Stable or improving critical-field precision.
- At least 30–50% reduction in manual review time.
- Reduced backlog of incomplete or expired documentation.
- Consistent reviewer adoption.
- No material increase in unresolved compliance exceptions.
- Positive value contribution after subscription and operating costs.
- Documented evidence that reviewers act on prioritised findings.

---

## Phase 4 — Optional Scale

Scale should begin only after the initial production deployment is stable for at least one quarter.

### Potential expansion paths

1. **More product categories**
   - Household appliances.
   - Toys.
   - Batteries.
   - Personal protective equipment.
   - Other regulated consumer goods.

2. **More regulatory regimes**
   - Additional EU product requirements.
   - Country-specific documentation.
   - Customer-specific supplier policies.
   - Environmental and sustainability documentation.

3. **More workflow integrations**
   - ERP systems.
   - Product information management systems.
   - Supplier relationship management platforms.
   - Procurement suites.
   - Shared document repositories.

4. **Supplier self-service**
   - Supplier upload portal.
   - Automated gap notices.
   - Document replacement requests.
   - Supplier compliance status views.

5. **Portfolio analytics**
   - Supplier risk trends.
   - Category-level exposure.
   - Upcoming expiry workload.
   - Compliance readiness before product launch.

### Scale gate

Scale is approved when:

- The initial customer has achieved target KPIs for at least three consecutive months.
- The rule and configuration model can support a second customer without extensive custom code.
- Onboarding effort is documented and repeatable.
- Unit economics improve or remain acceptable at higher volumes.
- Monitoring can identify degradation by customer, product category and document type.
- The commercial team has a repeatable sales and implementation process.

---

# 5. Timeline and Milestones

The following plan assumes a 20-week path from POC to production, followed by an optional scale phase.

| Period | Phase | Major activities | Milestone |
|---|---|---|---|
| Weeks 1–2 | POC preparation | Confirm scope, rules, users, data access and success criteria | Signed POC charter |
| Weeks 3–4 | POC build | Configure ingestion, schemas, SKU mapping and deterministic rules | First end-to-end customer dataset processed |
| Weeks 5–6 | POC validation | Label results, assess errors, collect reviewer feedback | POC accuracy and value report |
| Week 7 | POC decision | Resolve critical issues and approve pilot design | Pilot go/no-go |
| Weeks 8–9 | Pilot setup | Integrations, access controls, training, baseline measurement | Pilot environment ready |
| Weeks 10–13 | Pilot operation | Process live or historical documents in parallel with existing workflow | Mid-pilot performance review |
| Weeks 14–16 | Pilot optimisation | Tune rules, thresholds, prompts and workflow | Final pilot dataset completed |
| Weeks 17–18 | Pilot evaluation | Measure KPIs, economics, adoption and operational risks | Full-deployment recommendation |
| Weeks 19–20 | Production launch | Production migration, support model and reporting | Production go-live |
| Months 6–9 | Stabilisation | Monitor performance, improve onboarding and expand usage | Three-month production review |
| Months 9–12 | Optional scale | Add categories, suppliers, integrations or customers | Scale investment decision |

---

# 6. Go-to-Market Strategy

## Target buyers

### Primary buyer

**Head of Procurement or Supply Chain Operations**

This buyer experiences the operational burden of chasing supplier documents, onboarding products and managing incomplete records. Their primary goals are speed, visibility and reduced manual work.

### Economic buyer

**Chief Operating Officer, Chief Procurement Officer or Finance Director**

This buyer cares about:

- Reduced operational cost.
- Faster product onboarding.
- Lower risk of selling products with incomplete documentation.
- Scalable compliance operations without proportional headcount growth.

### Key influencers

- Head of Compliance or Product Safety.
- Quality assurance manager.
- Legal and regulatory affairs team.
- IT and data-protection team.
- Product or merchandising leadership.
- Supplier-management team.

### Initial customer profile

The strongest early-adopter profile is:

- European retailer, distributor or marketplace.
- 100–1,000 employees.
- Hundreds to tens of thousands of active SKUs.
- Consumer electronics or other documentation-heavy products.
- Suppliers across multiple countries.
- Existing compliance review performed primarily through email, spreadsheets and PDFs.
- Clear human review process but limited automation.
- Sufficient document volume to create measurable operational value.

## Buyer pain points

- Supplier documentation is distributed across email, shared drives and spreadsheets.
- Reviewers spend time locating and comparing documents rather than resolving exceptions.
- Expiry dates and missing documents are difficult to track.
- Product and supplier records may not match consistently.
- Management lacks a current view of compliance workload and exposure.
- Compliance teams are reluctant to use opaque AI that makes unsupported decisions.

## Positioning

> **Supra AI turns fragmented supplier compliance documents into an auditable review queue—using AI to extract evidence, rules to screen requirements and humans to make the final decision.**

## Differentiators

1. **Human-in-the-loop by design**  
   Supra AI supports reviewers rather than replacing accountable compliance decisions.

2. **AI extraction plus deterministic rules**  
   The separation between document extraction and policy evaluation makes the output easier to test, explain and govern.

3. **Evidence-linked findings**  
   Reviewers can trace findings back to the source document and relevant text.

4. **SKU-aware screening**  
   Results are checked against product-specific requirements rather than generic document presence alone.

5. **Prioritised exceptions**  
   The product focuses attention on missing, expired and inconsistent documentation.

6. **Fast initial deployment**  
   The first version can operate using PDFs, a SKU catalogue and a controlled workflow without requiring a major systems replacement.

7. **Measurable operational value**  
   Success can be measured through review time, backlog reduction, finding quality and cost per document.

## Channels

### Direct enterprise sales

Best for the first three to five customers.

- Founder-led or specialist consultative sales.
- Targeted outreach to procurement, compliance and supply-chain leaders.
- Demonstrations using anonymised sample documents.
- Paid discovery or POC before a longer subscription commitment.

### Compliance and procurement consultancies

Consultancies can introduce Supra AI as part of:

- Supplier onboarding programmes.
- Product compliance audits.
- Documentation remediation projects.
- Procurement transformation programmes.

This channel can accelerate trust but may require partner margins and implementation enablement.

### Technology partnerships

Potential partners include:

- Document-management platforms.
- Procurement software providers.
- Product-information management vendors.
- ERP implementation partners.
- Specialist product compliance platforms.

The initial approach should favour integration partnerships rather than attempting to replace established systems.

### Industry events and content

Relevant content themes include:

- Managing supplier compliance at scale.
- Human oversight for AI-assisted compliance.
- Reducing documentation review backlogs.
- Building auditable AI workflows for procurement.
- Practical lessons from poor-quality supplier PDFs.

Content should focus on operational outcomes rather than generic AI capability.

---

# 7. Pricing and Packaging

Pricing should combine implementation revenue with recurring platform revenue.

## Recommended packages

| Package | Target customer | Indicative pricing | Included |
|---|---|---:|---|
| Discovery / POC | New customer validating the use case | €5,000–€10,000 one-off | Scope definition, data assessment, configured workflow, validation report |
| Pilot | One business unit or category | €15,000–€30,000 for 8–12 weeks | Configuration, controlled processing, training, KPI reporting and optimisation |
| Production — Core | Mid-sized retailer or distributor | €30,000–€60,000 annual subscription | Platform access, agreed document volume, dashboard, rule configuration and support |
| Production — Growth | Larger catalogue or multiple categories | €60,000–€120,000 annual subscription | Higher volume, integrations, advanced reporting and priority support |
| Enterprise | Large or multi-country organisation | Custom | Multiple business units, higher service levels, private deployment options and supplier workflows |

The pricing ranges are starting points for commercial testing. Final prices should be based on document volume, number of SKUs, integration complexity, support requirements and the value demonstrated during the pilot.

## Pricing structure

A practical production contract should contain:

- Annual platform subscription.
- Included document-processing allowance.
- Additional usage fee above the allowance.
- One-off implementation and integration fee.
- Optional premium support.
- Optional rules and category expansion fee.

### Usage metric

The simplest initial usage metric is the number of documents processed. However, pricing should avoid encouraging customers to upload duplicate or irrelevant files. The contract should define:

- What counts as a processed document.
- Whether reprocessing counts.
- Treatment of duplicate documents.
- OCR or unusually complex document surcharges.
- Maximum file size and supported formats.

## Commercial value proposition

The financial case should be based on measured customer results, including:

- Review hours avoided.
- Reduced backlog.
- Faster supplier or product onboarding.
- Earlier identification of expired documents.
- Reduced manual data entry.
- Improved management visibility.
- Fewer avoidable escalations.

A customer should be able to justify the subscription through operational savings and risk reduction without relying on an unsupported claim that the platform guarantees legal compliance.

---

# 8. Commercialisation Model

## Recommended model: B2B SaaS with implementation services

Supra AI should be commercialised as a software-as-a-service platform supported by paid configuration and integration services.

### Revenue streams

1. **Discovery and POC fees**
   - Paid assessment of data, rules and workflow.
   - Reduces unpaid presales work.
   - Creates a clear transition point to a pilot.

2. **Pilot fees**
   - Covers configuration, training, measurement and customer support.
   - Converts the use case into a quantified business case.

3. **Annual subscription**
   - Core recurring revenue.
   - Based on customer size, document volume, users and modules.

4. **Implementation fees**
   - SKU catalogue mapping.
   - Repository or API integration.
   - Rule configuration.
   - Historical backfill.
   - User training.

5. **Expansion revenue**
   - Additional product categories.
   - Additional regulatory rule sets.
   - Supplier portal.
   - Advanced analytics.
   - Higher processing volume.
   - Multi-country deployment.

6. **Partner revenue**
   - Referral or reseller arrangements with consultancies and technology partners.

## Contract structure

The initial production contract should be an annual agreement with:

- Defined scope and supported document types.
- Included volume.
- Service levels.
- Support hours and response targets.
- Customer responsibilities.
- Human-review responsibilities.
- Data-processing and retention terms.
- Change-control process for rules and workflows.
- Exit and data-export provisions.
- Renewal and expansion terms.

## Implementation model

### Standard onboarding

1. Business and compliance discovery.
2. Data and document assessment.
3. SKU catalogue mapping.
4. Rule configuration.
5. User and access setup.
6. Historical data import.
7. Validation against labelled examples.
8. User training.
9. Controlled launch.
10. Production handover.

The goal should be to reduce standard onboarding to 4–8 weeks after the product has completed its first few deployments.

## Build-versus-configure strategy

The product should use configuration wherever possible:

- Configurable document schemas.
- Configurable product and supplier fields.
- Versioned rules.
- Customer-specific thresholds.
- Reusable review states.
- Standard API and file-based connectors.

Custom code should be reserved for integrations and requirements that are likely to be reusable across multiple customers.

---

# 9. Stakeholder Communication Plan

## Stakeholder matrix

| Stakeholder | Information need | Frequency | Channel | Owner |
|---|---|---|---|---|
| Executive sponsor | Business value, risk, budget and milestones | Fortnightly during pilot; monthly in production | Steering meeting and summary report | Project lead |
| Procurement leadership | Backlog, supplier response and workflow performance | Weekly during pilot; monthly in production | Dashboard and review meeting | Procurement owner |
| Compliance reviewers | Findings, evidence quality, exceptions and rule changes | Weekly during pilot; ongoing in production | In-product queue, training and office hours | Compliance lead |
| Supply-chain operations | Product readiness, supplier delays and escalations | Weekly | Dashboard and exception report | Operations lead |
| IT / data protection | Access, integrations, incidents and data handling | At setup, then monthly or on change | Technical review and ticketing | Technical lead |
| Legal / regulatory | Scope, control design and decision accountability | At phase gates and major rule changes | Control review | Compliance lead |
| Suppliers | Document requests, missing information and remediation status | As triggered by workflow | Email or supplier portal | Procurement team |
| Supra AI delivery team | Defects, model performance, cost and roadmap | Daily internally; weekly with customer | Delivery stand-up and issue log | Product owner |

## Communication cadence

### Weekly pilot report

The weekly report should include:

- Documents received and processed.
- Processing failures.
- Findings by severity and type.
- Critical exceptions.
- Average review time.
- Reviewer adoption.
- Supplier response status.
- Open defects and corrective actions.
- KPI trend against target.

### Phase-gate report

Each gate report should contain:

- Scope completed.
- Results against agreed KPIs.
- Known limitations.
- Material incidents.
- Customer feedback.
- Commercial value estimate.
- Risks and mitigations.
- Recommendation: proceed, extend, remediate or stop.

### Production monthly report

The monthly report should include:

- Volume and throughput.
- Review-time savings.
- Critical findings and ageing.
- Expiring documents.
- False-positive and correction trends.
- Availability and processing latency.
- Cost per document.
- User adoption.
- Rule or configuration changes.
- Recommended improvements.

## Escalation rules

Escalate immediately to the compliance lead and executive sponsor when:

- A critical document is incorrectly classified as complete.
- A finding cannot be traced to evidence.
- The system processes a document against the wrong SKU or supplier.
- Access to customer data is incorrect or unauthorised.
- A rule change produces unexpected portfolio-wide results.
- Processing failures create a material review backlog.
- A production change affects extraction or rule outcomes without approval.

---

# 10. KPIs and Measurement Framework

## KPI definitions

### Technical KPIs

| KPI | Definition | POC target | Pilot target | Production target |
|---|---|---:|---:|---:|
| Processing success rate | Documents completing without technical failure | ≥90% | ≥95% | ≥98% |
| Critical-field precision | Correct extracted values divided by extracted values for critical fields | ≥95% | ≥97% | ≥98% |
| Critical-field recall | Correctly extracted required values divided by required values present | ≥90% | ≥95% | ≥97% |
| Critical miss rate | Critical compliance issues not surfaced by the system | 0 in test set | 0 in agreed validation set | 0 material incidents |
| Evidence coverage | Findings with source and evidence reference | 100% | 100% | 100% |
| Median processing latency | Time from submission to result | Baseline | Defined SLA | Within SLA |
| Availability | Service availability during agreed hours | N/A | ≥99% | ≥99.5% |

### Operational KPIs

| KPI | Definition | POC target | Pilot target | Production target |
|---|---|---:|---:|---:|
| Review-time reduction | Reduction against baseline manual review | Directional | ≥30% | ≥30–50% |
| Reviewer adoption | Assigned reviewers actively using the system | ≥60% | ≥80% | ≥85% |
| Actionable finding rate | Findings accepted as useful by reviewers | ≥70% | ≥80% | ≥85% |
| Backlog reduction | Reduction in overdue or unreviewed documents | Baseline established | ≥20% | Sustained reduction |
| First-pass resolution | Issues resolved without repeated manual rework | Baseline established | Improvement demonstrated | Quarterly improvement |
| Supplier response time | Time from request to acceptable replacement document | Baseline established | Improvement demonstrated | Measured by segment |

### Business KPIs

| KPI | Definition | Pilot target | Production target |
|---|---|---:|---:|
| Cost per processed document | Platform and variable processing cost divided by documents processed | Measured | Within contract margin target |
| Cost per reviewed exception | Total workflow cost divided by resolved exceptions | Baseline and improvement | Year-on-year reduction |
| Product onboarding time | Time from document submission to review-ready status | Improvement demonstrated | ≥20% reduction |
| Avoided manual hours | Baseline hours less assisted-process hours | Measured | Positive ROI |
| Subscription value coverage | Quantified annual benefit divided by annual subscription cost | ≥1.5x directional | ≥2x target |
| Expansion readiness | Number of additional categories or workflows suitable for rollout | At least one | Defined expansion pipeline |

## Greenlight decision: Pilot to full deployment

Full deployment should be greenlit only when:

1. Critical-field precision is at least 97% on a representative labelled pilot dataset.
2. No critical compliance issue is silently missed in the agreed validation set.
3. Processing success is at least 95%.
4. Review time is reduced by at least 30%.
5. At least 80% of target reviewers actively use the system.
6. At least 80% of flagged findings are considered actionable.
7. All findings contain evidence links.
8. Access, retention, support and incident processes are approved.
9. The customer has a named compliance owner.
10. The measured or defensible business case supports production pricing.

If technical KPIs pass but adoption or business-value KPIs fail, the deployment should be extended or redesigned rather than automatically moved to production.

---

# 11. Governance, Risk and Controls

## Key risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Incorrect extraction from poor-quality PDFs | Wrong screening result | Confidence thresholds, OCR fallback, human review and representative test data |
| False negative on a critical requirement | Compliance exposure | Critical-field validation, mandatory review gates and labelled regression tests |
| False positives overwhelm reviewers | Low adoption | Prioritisation, rule tuning and tracking of actionable finding rate |
| SKU-document mismatch | Incorrect product assessment | Product and supplier identifiers, manual confirmation for ambiguous matches |
| Regulatory rules change | Outdated screening | Versioned rule catalogue, named rule owner and scheduled reviews |
| Supplier documents are incomplete or misleading | Low-quality inputs | Supplier remediation workflow and evidence-preserving audit trail |
| Overreliance on synthetic data | Inflated performance results | Expand real-world labelled datasets before production |
| Integration failure | Workflow disruption | File-based fallback, monitoring and staged integration |
| Uncontrolled model or prompt change | Performance regression | Versioning, benchmark tests and change approval |
| Customer perceives the system as legal advice | Misuse | Clear product scope, human approval and contractual responsibility boundaries |

## Required controls

- Role-based access control.
- Authentication and least-privilege permissions.
- Audit logs for uploads, findings, edits and approvals.
- Versioned extraction schemas and rules.
- Regression benchmark for every material change.
- Confidence thresholds for automatic routing.
- Mandatory human review for critical or ambiguous findings.
- Data-retention and deletion configuration.
- Incident-response process.
- Exportable customer records.
- Monitoring for processing failures and abnormal output patterns.

---

# 12. Product Roadmap Supporting Commercialisation

## Release 1 — Pilot-ready

- Reliable PDF ingestion.
- Structured extraction schema.
- CE/RoHS rule set.
- SKU catalogue mapping.
- Evidence-linked findings.
- Reviewer dashboard.
- Manual correction workflow.
- Basic monitoring and audit logs.
- Benchmark and regression test suite.

## Release 2 — Production-ready

- Role-based access.
- Document repository integration.
- Expiry alerts.
- Supplier and product history.
- Configurable rules.
- Review queues by severity and owner.
- Production support tooling.
- Usage and cost reporting.
- Data export and retention controls.

## Release 3 — Scale-ready

- Multi-tenant architecture.
- Supplier portal.
- Self-service configuration.
- Additional categories and regulations.
- API integrations.
- Advanced analytics.
- Customer-level model and rule performance monitoring.
- Partner implementation toolkit.

---

# 13. Decision Rights

| Decision | Accountable owner | Required input |
|---|---|---|
| Product and regulatory scope | Customer compliance lead | Procurement and legal |
| Rule approval | Customer compliance lead | Supra AI product team |
| Production go-live | Executive sponsor | Compliance, IT and project lead |
| Model or prompt changes | Supra AI product owner | Benchmark and compliance review |
| Customer-specific configuration | Customer product owner | Compliance and procurement |
| Critical incident response | Joint customer and Supra AI leads | IT and compliance |
| Expansion to new categories | Executive sponsor | KPI and risk review |
| Pricing and renewal | Commercial owner | Measured ROI and usage data |

---

# 14. Commercialisation Milestones

The following milestones indicate movement from concept to a repeatable business:

### Milestone 1 — Validated problem

- Customer confirms that supplier-document review is a significant operational problem.
- A named business owner and representative document set are available.
- Baseline manual effort is measured.

### Milestone 2 — Validated solution

- POC processes representative documents.
- Critical fields and rules produce understandable results.
- Findings are evidence-linked.
- Reviewers confirm that the output is useful.

### Milestone 3 — Validated workflow

- Pilot users adopt the system.
- Review-time reduction is demonstrated.
- False positives and false negatives are understood and controlled.
- Integration and governance requirements are documented.

### Milestone 4 — Validated commercial case

- Customer accepts production pricing.
- Subscription value is supported by measured benefits.
- Implementation effort is repeatable.
- Support requirements are understood.

### Milestone 5 — Repeatable growth

- Second customer can be onboarded using standard configuration.
- Product-category expansion does not require major architectural changes.
- Partner or direct sales channels produce qualified opportunities.
- Gross margin and support economics are sustainable.

---

# 15. Recommended Immediate Actions

1. Create a POC charter with the initial customer.
2. Agree the exact in-scope product categories, standards and document types.
3. Obtain a representative labelled dataset containing both good and problematic documents.
4. Measure the current manual review time and backlog.
5. Define critical versus non-critical compliance fields.
6. Implement evidence-location capture for every finding.
7. Establish the pilot KPI baseline before changing the existing process.
8. Add regression tests covering real-world documents and known failure modes.
9. Identify the customer compliance owner and executive sponsor.
10. Prepare a paid pilot proposal with fixed scope, timeline and exit criteria.
11. Use pilot results to set production pricing rather than relying only on theoretical processing cost.
12. Delay broad category expansion until the initial production workflow has met its KPIs for at least three months.

---

# 16. Strategic Recommendation

Proceed with a controlled, paid pilot focused on consumer-electronics supplier documentation. Keep the product positioned as an auditable compliance-screening and workflow tool, not an autonomous compliance authority.

The strongest route to commercialisation is a high-touch B2B SaaS model:

- Paid POC.
- Paid implementation-led pilot.
- Annual production subscription.
- Expansion through additional document volumes, product categories, integrations and supplier workflows.

The pilot-to-production decision should be driven by critical-miss performance, reviewer adoption, measurable time savings, evidence quality and a credible customer ROI—not by extraction accuracy on a small synthetic dataset alone.
