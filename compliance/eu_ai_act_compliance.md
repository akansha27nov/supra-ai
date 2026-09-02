# EU AI Act Compliance Documentation

**System:** Supra AI — AI-Assisted Supplier Compliance Screening 
**Document status:** MVP assessment  
**Assessment date:** 2026-09-02  
**Assessment owner:** Akansha Verma  
**Regulatory scope:** Regulation (EU) 2024/1689 — EU Artificial Intelligence Act

> This document is an initial compliance assessment for the Supra AI MVP. It is not legal advice and should be reviewed by the system provider, deployer, and qualified EU regulatory counsel before commercial deployment.

---

## 1. System Description

Supra AI is an AI-assisted supplier and product compliance screening system for consumer-electronics documentation.

The system is designed to:

1. Receive supplier documents such as CE certificates, RoHS certificates, test reports, and declarations of conformity.
2. Extract structured information from PDFs and other supported documents using an LLM-based extraction component.
3. Match extracted product information against an internal SKU catalogue.
4. Apply deterministic compliance rules to identify missing, expired, inconsistent, or potentially problematic documentation.
5. Present evidence-linked findings and prioritised review items in a dashboard.
6. Require a human compliance reviewer to approve, reject, or override the result.

The intended system boundary is document and product compliance screening. The system is not designed to:

- Make autonomous legal or regulatory decisions.
- Determine whether an individual is suitable for employment, credit, insurance, education, housing, or access to essential services.
- Evaluate the personality, behaviour, trustworthiness, or risk of a natural person.
- Operate a safety component in a regulated product.
- Control physical machinery or infrastructure.
- Generate decisions that are binding on suppliers without human review.

The repository describes the architecture as an AI extraction layer, a transparent rule engine, and a human approval step. It also records that the current results are based on a small test set and do not demonstrate production-scale reliability or generalisation across all EU electrical-product documentation. <citation src="1"></citation>

---

# 2. Risk Classification and Step-by-Step Reasoning

## 2.1 Preliminary classification

**Proposed classification: Minimal-risk / non-high-risk AI system under the current intended purpose.**

The system does not appear to fall within the EU AI Act's prohibited-risk practices, high-risk categories, or specific transparency categories based on its documented MVP purpose.

This conclusion depends on the intended use remaining limited to supplier-document extraction, product/SKU matching, deterministic compliance checks, and human review.

## 2.2 Step-by-step assessment

### Step 1 — Is the system an AI system?

Yes.

Supra AI uses an LLM-based component to extract information from supplier documents. The repository also includes an agentic extraction pipeline and LangSmith tracing for the document-processing workflow. Therefore, the system falls within the broad scope of an AI system under the EU AI Act.

### Step 2 — Does the system use a prohibited AI practice?

No, based on the current design.

The system does not perform or appear to perform:

- Social scoring of natural persons.
- Manipulative or subliminal techniques intended to materially distort behaviour.
- Real-time remote biometric identification in publicly accessible spaces.
- Emotion recognition in workplaces or educational institutions.
- Predictive criminal-risk assessment of individuals based solely on profiling.
- Biometric categorisation of people using sensitive or protected characteristics.

The system processes supplier and product documentation rather than making assessments about natural persons.

### Step 3 — Is the system a safety component or a product covered by Annex I?

Not based on the current repository description.

The system supports compliance screening for consumer-electronics documentation, but it is not itself described as:

- A safety component of a regulated product.
- Embedded in a product.
- Used to control a product.
- Subject to a third-party conformity assessment as a product component.

The CE, RoHS, test-report, and declaration-of-conformity documents are inputs to the screening process. Their presence does not, by itself, make Supra AI a high-risk AI system.

This classification must be reassessed if Supra AI is later embedded in a regulated product, used to control product safety functions, or marketed as a component that determines the safety or conformity of a product.

### Step 4 — Does the system fall within an Annex III high-risk use case?

Not based on the current intended purpose.

The system is not intended for:

- Biometric identification or categorisation.
- Critical infrastructure management.
- Education or vocational training decisions.
- Employment, worker management, or access to self-employment.
- Access to essential private or public services.
- Law enforcement.
- Migration, asylum, or border control.
- Administration of justice or democratic processes.

Although the system supports procurement and supply-chain operations, it does not evaluate natural persons or make employment, credit, insurance, public-service, or other Annex III decisions.

### Step 5 — Does the system make decisions about natural persons?

No, based on the current scope.

The system evaluates documents, products, SKUs, standards, dates, and supplier-provided evidence. It is not intended to rank, profile, or determine the rights or opportunities of individual suppliers, employees, customers, or other natural persons.

If the system is later used to assess individual supplier representatives, employees, contractors, or sole traders as natural persons, the classification must be reviewed.

### Step 6 — Do the specific transparency obligations apply?

Not ordinarily, based on the current interaction model.

The system is not described as:

- A chatbot or conversational system interacting directly with end users.
- A system generating synthetic audio, image, video, or text intended to impersonate a person.
- An emotion-recognition or biometric-categorisation system.
- A system generating or manipulating deepfakes.

If a conversational assistant is added, users should be informed that they are interacting with an AI system. If the product later generates synthetic content, the applicable labelling and disclosure requirements must be assessed.

### Step 7 — Final classification

| Assessment area | Result | Rationale |
|---|---|---|
| AI system | Yes | Uses an LLM for document extraction |
| Prohibited practice | No identified practice | No prohibited manipulation, social scoring, or biometric use |
| Annex I product or safety component | No, based on current scope | Document-screening tool rather than product safety component |
| Annex III high-risk use case | No, based on current scope | Does not make decisions about natural persons or listed sectors |
| Specific transparency category | Not currently identified | No chatbot, biometric, emotion, or generative-media use documented |
| Proposed classification | Minimal-risk / non-high-risk | Intended use is supplier-document and product-compliance assistance |

## 2.3 Classification conditions

The proposed classification is valid only if the following conditions remain true:

- Human reviewers retain final decision authority.
- AI outputs are advisory and are not treated as legally binding compliance determinations.
- The system does not assess natural persons.
- The system is not embedded in or controlling a regulated product.
- The system is not used for employment, credit, insurance, essential services, law enforcement, migration, education, or justice decisions.
- The system does not perform biometric identification, biometric categorisation, or emotion recognition.
- Supplier and product screening remains separate from individual-person profiling.

Any material change to these conditions requires a documented classification review.

---

# 3. Mandatory Requirements Summary

## 3.1 Requirements for the current minimal-risk classification

The EU AI Act generally does not impose the full mandatory high-risk system obligations on a minimal-risk AI system used for the documented purpose.

Nevertheless, the project should implement the following controls as good governance and as preparation for potential future changes:

- Document the intended purpose and prohibited uses.
- Maintain human oversight and require reviewer approval.
- Record the source document and evidence supporting every extracted field or finding.
- Maintain version control for extraction prompts, models, SKU data, and compliance rules.
- Record system errors, reviewer overrides, and unresolved ambiguities.
- Test extraction accuracy against labelled ground truth.
- Test the rule engine separately from the AI extraction layer.
- Monitor poor-quality scans, OCR failures, unsupported formats, and missing evidence.
- Maintain an incident, complaint, and corrective-action process.
- Apply appropriate access control, retention, and data-minimisation measures.
- Reassess the EU AI Act classification before adding new use cases or integrations.

## 3.2 If the system becomes high-risk

If a future deployment brings Supra AI within an Annex III category or makes it a safety component of a regulated product, the following high-risk obligations would need to be addressed before placing the system on the market or putting it into service:

- Establish and maintain a documented risk-management system.
- Use appropriate and sufficiently representative data governance and management practices.
- Prepare and maintain detailed technical documentation.
- Maintain automatically generated logs appropriate to the system's operation.
- Provide clear instructions for use to deployers.
- Design and implement effective human oversight.
- Demonstrate appropriate levels of accuracy, robustness, and cybersecurity.
- Operate a quality-management system.
- Complete the applicable conformity-assessment procedure.
- Prepare an EU declaration of conformity.
- Apply the required CE marking where applicable.
- Register the system in the relevant EU database where required.
- Monitor the system after deployment.
- Report serious incidents and malfunctions as required.
- Take corrective action and cooperate with competent authorities.

The current MVP should not claim compliance with these high-risk obligations unless the required evidence has been produced.

## 3.3 If the system becomes limited-risk

If Supra AI adds a user-facing conversational interface, users should be clearly informed when they are interacting with an AI system.

If the system generates or manipulates synthetic text, images, audio, or video, the relevant artificial-content disclosure and labelling requirements should be assessed and implemented.

These obligations are use-case-specific. The current document-processing workflow does not, by itself, establish that the system falls into a limited-risk transparency category.

---

# 4. Role Map

## 4.1 Role allocation

The following role allocation is based on the current repository structure and intended deployment model. The legal roles should be confirmed contractually before the system is deployed commercially.

| Role | Entity | Key AI Act obligations |
|---|---|---|
| Provider | **Supra AI project owner and developer:** the individual, company, or organisation that develops Supra AI, determines its intended purpose, packages or deploys it as a product, and places it on the EU market. The exact legal entity is not identified in the repository and must be confirmed. | Define and document the intended purpose; complete and maintain the AI Act classification assessment; ensure the system complies with applicable requirements; maintain technical documentation and records; provide instructions and limitations to users; implement human-oversight controls; monitor performance and incidents; maintain a quality and change-control process; cooperate with authorities; and, if the system becomes high-risk, complete the applicable conformity-assessment, registration, declaration-of-conformity, CE-marking, post-market monitoring, and incident-reporting obligations. |
| Deployer | **The customer, procurement team, compliance team, or other organisation that uses Supra AI in a professional context to screen supplier and product documentation.** The specific deployer will depend on the eventual customer or internal business unit. | Use the system according to the provider's instructions and intended purpose; assign competent human reviewers; maintain effective human oversight; monitor the system in use; ensure input data is relevant and sufficiently representative for the intended task; keep relevant logs where required; inform affected users or persons where applicable; report serious incidents or risks to the provider and relevant authorities; suspend use when the system presents a serious risk; and avoid extending the system to unapproved high-risk uses. |
| Vendor (if applicable) | **Third-party AI, software, hosting, and observability vendors** used by Supra AI. This may include the LLM/API provider used for document extraction, cloud or hosting providers, OCR or PDF-processing services, workflow platforms, and tracing or monitoring tools such as LangSmith. The exact vendors, models, and contractual arrangements must be recorded in the vendor inventory. | Provide required information and documentation to the Supra AI provider where the vendor supplies an AI system or general-purpose AI model; disclose relevant model capabilities, limitations, usage restrictions, and technical information; maintain applicable documentation and risk controls; notify the provider of incidents or material changes; comply with applicable data-protection and security obligations; and cooperate with downstream providers and deployers. Vendors providing only hosting, storage, logging, or non-AI infrastructure may not themselves be AI Act providers, but their services remain relevant to the provider's technical documentation, cybersecurity, data-flow, and risk-management obligations. |

## 4.2 Provider

For the current project, the provider is the entity that controls the development and release of Supra AI and would place the system on the market or put it into service.

The repository identifies the system as an AI-assisted supplier compliance-screening application, but it does not establish the legal name of the provider. The provider field must therefore be completed before deployment:

- Legal name: `[insert legal entity]`
- Registered address: `[insert address]`
- EU representative, if required: `[insert details]`
- Product owner: `[insert name or role]`
- Compliance owner: `[insert name or role]`
- Technical owner: `[insert name or role]`

The provider's immediate responsibilities for the current MVP are to:

1. Define the intended purpose and system boundaries.
2. Prevent the system from being marketed as an autonomous conformity or legal decision-maker.
3. Maintain the classification assessment.
4. Document the model, prompts, rules, data, architecture, and limitations.
5. Validate extraction accuracy, rule accuracy, evidence traceability, and missed findings.
6. Maintain human-review and escalation controls.
7. Control changes to models, prompts, rules, data, dependencies, and integrations.
8. Maintain security, access control, retention, logging, and incident procedures.
9. Keep the technical documentation current.
10. Reassess the classification before changing the intended purpose or deployment context.

If the system later becomes high-risk, the provider would become responsible for the full set of high-risk provider obligations, including risk management, data governance, technical documentation, logging, instructions for use, human oversight, accuracy, robustness, cybersecurity, quality management, conformity assessment, registration, post-market monitoring, and serious-incident reporting.

## 4.3 Deployer

The deployer is the organisation using Supra AI under its authority in a professional context. A likely deployer is a procurement, supplier-quality, regulatory, or compliance function that uses the tool to review supplier documentation.

The deployer should nominate:

- A business owner responsible for the screening process.
- Trained compliance reviewers responsible for final decisions.
- A technical administrator responsible for access and operational monitoring.
- An incident owner responsible for escalating failures and suspected serious risks.

The deployer's responsibilities include:

1. Use Supra AI only for the approved supplier-document and product-screening purpose.
2. Ensure that human reviewers understand that AI output is advisory.
3. Require review of evidence before accepting or rejecting a finding.
4. Prevent automatic supplier rejection or product-conformity decisions unless separately approved and legally assessed.
5. Verify that documents submitted to the system are appropriate for the intended purpose.
6. Monitor false positives, false negatives, overrides, missing findings, and system failures.
7. Report material errors and incidents to the provider.
8. Maintain a manual fallback process when the service is unavailable or unreliable.
9. Restrict access to authorised users.
10. Ensure that personal, confidential, or commercially sensitive information is handled according to applicable data-protection and security requirements.
11. Stop or limit use if the system produces unreliable results or presents a serious risk.
12. Notify reviewers and other relevant users of material changes to system behaviour or instructions.

The deployer must not expand the system into employment, credit, insurance, public-service, law-enforcement, or other high-risk decision-making without completing a new legal and technical assessment.

## 4.4 Third-party vendors

The technical implementation may rely on several third-party services:

- An LLM or AI API for document extraction.
- PDF parsing or OCR services.
- Cloud hosting, storage, and networking.
- Workflow or orchestration platforms.
- Observability and tracing tools.
- Authentication, access-control, and monitoring services.

The project must maintain a vendor inventory containing:

| Vendor/service | Function | AI Act status | Required evidence |
|---|---|---|---|
| `[LLM/API provider]` | Document-field extraction | Potential provider of a general-purpose AI model or AI system; classification depends on the supplied service and contract | Model name and version, intended-use restrictions, technical documentation, data-processing terms, security information, incident channel, change-notification process |
| `[OCR/PDF provider]` | Text extraction or OCR | AI Act status depends on whether the service uses AI or only deterministic software | Service description, model information if applicable, accuracy information, data-flow and retention terms |
| `[Cloud provider]` | Hosting, storage, networking | Usually infrastructure provider rather than AI-system provider | Hosting location, security controls, access controls, retention, availability, subcontractors, incident process |
| `LangSmith` or equivalent | Tracing, evaluation, and observability | Usually a supporting platform; may process AI inputs and outputs | Data-flow description, retention settings, access controls, security documentation, export/deletion process |
| `[Workflow platform]` | Orchestration and automation | Depends on whether it provides AI functionality or only workflow execution | Functionality description, logs, security controls, change management, data-processing terms |

## 4.5 Vendor classification and contractual controls

A vendor's role must be assessed separately from Supra AI's classification.

A vendor that provides a general-purpose AI model or model-based API may have obligations applicable to general-purpose AI models. A vendor providing only hosting, storage, logging, or ordinary software infrastructure may not be an AI Act provider, although its service can still affect Supra AI's compliance.

The provider should obtain and retain, where applicable:

- Model and service identification.
- Version and release information.
- Intended-use and prohibited-use restrictions.
- Known limitations and performance information.
- Security and vulnerability information.
- Data retention and deletion terms.
- Whether customer inputs or outputs are used for training.
- Subprocessor and hosting information.
- Incident-notification commitments.
- Material-change notification commitments.
- Cooperation obligations for investigations and corrective actions.
- Documentation needed for the Supra AI technical file.

Third-party services must not be treated as automatically compliant merely because they are supplied by a large technology provider. The Supra AI provider remains responsible for understanding how those services affect the system's intended purpose, risk profile, data flows, performance, and user instructions.

## 4.6 Role changes and reclassification triggers

The role map must be reviewed if:

- A customer customises Supra AI for its own purposes.
- A customer places the system under its own name or brand.
- A customer substantially modifies the model, prompts, rules, or intended purpose.
- A vendor supplies a model that changes the system's capabilities or risk profile.
- Supra AI is embedded in a regulated product.
- The system begins making decisions about natural persons.
- The system is used without mandatory human review.
- A third party operates the system on behalf of multiple customers.
- The system is made available outside the original supplier-compliance use case.

A party may assume additional provider, deployer, importer, distributor, or product-manufacturer responsibilities depending on how the system is marketed, modified, branded, and placed into service.

---

# 5. Conformity Assessment Summary

## 5.1 Assessment conclusion

Based on the current intended purpose and architecture, Supra AI is assessed as a **minimal-risk, non-high-risk AI system** under the EU AI Act.

The system uses AI to extract information from supplier documentation, but the final screening outcome is generated through deterministic rules and reviewed by a human. The system is not intended to make autonomous legal decisions, assess natural persons, control a safety function, or determine access to an essential service.

Accordingly, a mandatory high-risk conformity assessment is not currently triggered by the documented MVP scope.

This conclusion is conditional. The classification must be reassessed if the system is integrated into a regulated product, used as a safety component, used to make decisions about individuals, or deployed in an Annex III context.

## 5.2 System architecture relevant to conformity

The compliance-relevant architecture consists of:

1. **Document intake**  
   Supplier certificates, declarations, test reports, and related files are submitted for processing.

2. **Document parsing and extraction**  
   An LLM-based component extracts structured fields such as product identifiers, standards, dates, supplier information, and document references.

3. **SKU matching**  
   Extracted product identifiers are compared with the internal SKU catalogue using exact and normalised matching.

4. **Deterministic compliance rules**  
   Rules identify missing standards, expired documents, inconsistent values, missing fields, and other configured conditions.

5. **Evidence-linked findings**  
   Findings are linked to extracted values and source documents where available.

6. **Human review**  
   A compliance reviewer assesses the evidence and approves, rejects, or overrides the system result.

7. **Monitoring and evaluation**  
   Benchmark data, ground truth, traces, accuracy results, and reviewer feedback are used to evaluate the pipeline.

The separation between AI extraction, deterministic rules, and human approval is a significant control. It reduces the risk that an unverified model output is treated as a final compliance decision.

## 5.3 Existing evidence in the repository

The repository provides evidence of the following controls:

- A documented supplier-compliance use case.
- A distinction between AI extraction and deterministic rule evaluation.
- Human approval as part of the intended operating model.
- Synthetic and real-world document sets.
- Ground-truth files for evaluation.
- Extraction and rule-engine benchmark scripts.
- Evidence of LangSmith tracing and observability.
- Risk assessment covering incorrect extraction, outdated rules, document quality, SKU matching, outages, privacy, governance, and ROI assumptions.
- A stated limitation that the current evaluation does not demonstrate production-scale reliability or broad generalisation.
- A documented need for controlled pilot validation.

These materials support an initial governance assessment but do not constitute a complete high-risk technical file or a formal legal conformity assessment.

## 5.4 Required pre-production checks

Before a production pilot, the project should complete the following checks:

- Confirm the legal entity acting as provider and the entity acting as deployer.
- Approve and version the intended purpose.
- Define prohibited uses and communicate them to users.
- Confirm that the system does not make decisions about natural persons.
- Define the human review workflow and escalation criteria.
- Establish minimum extraction-accuracy and missed-finding thresholds.
- Test false positives, false negatives, ambiguous SKU matches, expired documents, and poor-quality scans.
- Verify that each finding can be traced to source evidence.
- Document model, prompt, rule, data, and dependency versions.
- Define retention, access, deletion, and incident-handling procedures.
- Validate API, hosting, storage, and workflow failure handling.
- Complete a data-protection assessment where personal data is processed.
- Obtain legal review before making any claim that the system determines product conformity.

## 5.5 Conformity statement for the MVP

The following statement may be used internally:

> Supra AI is an AI-assisted supplier and product compliance screening system. In its current MVP scope, it extracts information from supplier documentation, applies deterministic screening rules, and presents evidence-linked findings to a human compliance reviewer. It does not make autonomous compliance decisions, assess natural persons, operate a safety component, or perform an Annex III high-risk use case. On this basis, the current intended use is assessed as minimal risk under the EU AI Act, with no mandatory high-risk conformity assessment currently identified. This assessment is conditional on the documented scope and must be reviewed before any material change in purpose, users, data, deployment environment, or system functionality.

---

# 6. Technical Documentation Outline

The following structure should be maintained as the technical documentation skeleton. Sections marked **[MVP]** are recommended immediately. Sections marked **[Conditional High-Risk]** become mandatory or substantially more detailed if the system is later classified as high-risk.

## 1. Document Control

1.1 Document title and system name  
1.2 Provider and deployer details  
1.3 Version history  
1.4 Approval history  
1.5 Assessment date  
1.6 Document owner  
1.7 Classification status  

## 2. Intended Purpose and Scope

2.1 Intended purpose  
2.2 Target users  
2.3 Target organisations and deployment context  
2.4 Supported document types  
2.5 Supported products and SKU categories  
2.6 Intended outputs  
2.7 Human decision boundary  
2.8 Prohibited and out-of-scope uses  
2.9 Foreseeable misuse  

## 3. Regulatory Classification

3.1 AI system determination  
3.2 Prohibited-practice assessment  
3.3 Annex I product and safety-component assessment  
3.4 Annex III assessment  
3.5 Transparency-obligation assessment  
3.6 Classification decision  
3.7 Classification assumptions and triggers for reassessment  

## 4. System Architecture

4.1 High-level architecture diagram  
4.2 Document intake  
4.3 PDF parsing and OCR  
4.4 LLM extraction component  
4.5 Structured output schema  
4.6 SKU matching  
4.7 Deterministic rule engine  
4.8 Evidence and source-value linking  
4.9 Dashboard and reviewer workflow  
4.10 Logging and monitoring  
4.11 External services and APIs  
4.12 System dependencies  

## 5. Model and AI Component Documentation

5.1 Model provider and model identifier  
5.2 Model version and configuration  
5.3 Prompt and instruction versions  
5.4 Input and output formats  
5.5 Context-window and token constraints  
5.6 Temperature and generation settings  
5.7 Structured-output constraints  
5.8 Fallback and retry behaviour  
5.9 Known model limitations  
5.10 Model-change management  

## 6. Data Governance

6.1 Data sources  
6.2 Synthetic test data  
6.3 Real-world test data  
6.4 Supplier document characteristics  
6.5 Data-selection criteria  
6.6 Ground-truth creation process  
6.7 Data-quality controls  
6.8 Missing, corrupted, and scanned documents  
6.9 Personal and confidential data handling  
6.10 Data minimisation  
6.11 Retention and deletion  
6.12 Access controls  
6.13 Data-flow diagram  

## 7. Compliance Rules and Knowledge Sources

7.1 Rule-engine purpose  
7.2 Rule catalogue  
7.3 Applicable standards and regulatory sources  
7.4 Rule ownership  
7.5 Rule versioning  
7.6 Effective dates  
7.7 Change-approval process  
7.8 Handling outdated or conflicting rules  
7.9 Rule-engine test cases  
7.10 Human escalation conditions  

## 8. Risk Management

8.1 Risk-management methodology  
8.2 Risk register  
8.3 Likelihood and impact scoring  
8.4 Technical risks  
8.5 Operational risks  
8.6 Governance and ethical risks  
8.7 Confidentiality and data risks  
8.8 Incorrect extraction risk  
8.9 Incorrect SKU-matching risk  
8.10 Outage and fallback risk  
8.11 Residual-risk assessment  
8.12 Risk acceptance and approval  

## 9. Human Oversight

9.1 Reviewer roles and responsibilities  
9.2 Human approval requirement  
9.3 Reviewer interface  
9.4 Confidence thresholds  
9.5 Escalation rules  
9.6 Override process  
9.7 Reviewer training  
9.8 Automation-bias controls  
9.9 Decision logging  
9.10 Suspension and shutdown procedure  

## 10. Performance Evaluation

10.1 Evaluation objectives  
10.2 Synthetic benchmark design  
10.3 Real-world benchmark design  
10.4 Extraction accuracy  
10.5 Field-level precision and recall  
10.6 Flag precision  
10.7 Missed findings  
10.8 False-positive analysis  
10.9 SKU-matching accuracy  
10.10 Human override rate  
10.11 Document-quality impact  
10.12 Cost and latency  
10.13 Acceptance thresholds  
10.14 Evaluation results and limitations  

## 11. Accuracy, Robustness, and Cybersecurity

11.1 Accuracy controls  
11.2 Input validation  
11.3 Unsupported-format handling  
11.4 OCR fallback  
11.5 Ambiguity detection  
11.6 Retry and queue behaviour  
11.7 Availability and outage handling  
11.8 Prompt-injection and malicious-document risks  
11.9 API-key and secret management  
11.10 Access control  
11.11 Audit logging  
11.12 Vulnerability management  
11.13 Security testing  
11.14 Backup and recovery  

## 12. Transparency and User Information

12.1 User instructions  
12.2 AI-assisted nature of the workflow  
12.3 Meaning of confidence scores  
12.4 Meaning and limitations of flags  
12.5 Human-review requirement  
12.6 Evidence display  
12.7 Known limitations  
12.8 Error-reporting process  
12.9 Applicable AI-generated-content disclosures, if functionality changes  

## 13. Quality Management and Change Control

13.1 Development lifecycle  
13.2 Code review  
13.3 Testing and release approval  
13.4 Model and prompt changes  
13.5 Rule changes  
13.6 Dataset changes  
13.7 Dependency changes  
13.8 Rollback procedure  
13.9 Supplier and third-party management  
13.10 Records management  

## 14. Deployment and Operations

14.1 Deployment environments  
14.2 Infrastructure configuration  
14.3 Environment variables and secrets  
14.4 Monitoring  
14.5 Alerting  
14.6 Incident response  
14.7 Manual fallback process  
14.8 User support  
14.9 Periodic review  
14.10 Decommissioning  

## 15. Post-Deployment Monitoring

15.1 Monitoring objectives  
15.2 Accuracy drift  
15.3 Document-distribution drift  
15.4 Rule and regulatory changes  
15.5 User override trends  
15.6 Missed-finding investigations  
15.7 Serious incident assessment  
15.8 Corrective actions  
15.9 Periodic reclassification  

## 16. Declarations and Supporting Records

16.1 Classification assessment  
16.2 Risk register  
16.3 Evaluation datasets  
16.4 Ground-truth files  
16.5 Benchmark results  
16.6 Model and prompt inventory  
16.7 Rule inventory  
16.8 Data-flow documentation  
16.9 Security and access-control records  
16.10 Incident records  
16.11 User instructions  
16.12 Legal and compliance approvals  

## 17. Conditional High-Risk Annexes

The following annexes should be completed if a future assessment classifies Supra AI as high-risk:

- Annex A — Detailed risk-management file
- Annex B — Data-governance evidence
- Annex C — Accuracy, robustness, and cybersecurity test results
- Annex D — Human-oversight validation
- Annex E — Automatically generated log specification
- Annex F — Quality-management-system evidence
- Annex G — Instructions for use
- Annex H — Post-market monitoring plan
- Annex I — Serious-incident reporting procedure
- Annex J — EU declaration of conformity
- Annex K — Conformity-assessment evidence
- Annex L — Technical-change and version history

---

# 7. Final Compliance Position

Supra AI should currently be treated as a **minimal-risk AI-assisted compliance-screening tool**, not as an autonomous product-conformity decision-maker.

The immediate compliance priority is therefore not a formal high-risk conformity assessment. It is to preserve the documented system boundaries, strengthen evidence traceability, validate extraction and flag quality, maintain human oversight, control rule changes, and reassess classification before expanding the product's purpose or deployment context.
