# EU AI Act Compliance Documentation

**System:** Supra AI — AI-Assisted Supplier Compliance Screening  
**Document status:** MVP / pilot assessment  
**Assessment date:** 2026-09-03  
**Assessment owner:** Akansha Verma  
**Regulatory scope:** Regulation (EU) 2024/1689 — EU Artificial Intelligence Act, as amended by Regulation (EU) 2026/1744

> **Important:** This document is an initial regulatory assessment of the Supra AI MVP. It is not legal advice or a formal conformity assessment. The final legal classification depends on the actual provider, deployer, intended purpose, deployment environment, underlying AI models, contractual arrangements, and system configuration. This assessment must be reviewed before commercial deployment and whenever the intended purpose or system capabilities materially change.

---

# 1. Executive Compliance Position

Based on the current documented use case and repository architecture, Supra AI is assessed as an **AI system that is not currently identified as a prohibited AI practice or an Annex III high-risk AI system**.

The system is intended to:

- process supplier compliance documentation;
- extract structured information using an LLM;
- resolve product/model information against an internal SKU catalogue;
- apply deterministic compliance-screening rules;
- present evidence-linked findings;
- prioritise cases for review; and
- support, rather than replace, a human compliance decision.

The system is **not intended to make decisions about natural persons**, operate as a safety component, control physical systems, or perform an Annex III high-risk use case.

Accordingly, no mandatory high-risk classification has been identified for the current intended purpose.

The term **"minimal risk"** may be used as an explanatory shorthand, but it should not be interpreted as a formal risk category defined by the AI Act. The legally relevant conclusion is that the current use case has not been identified as prohibited, high-risk, or otherwise subject to a specific AI Act obligation beyond requirements that may apply generally or to particular system functionality.

The assessment is conditional on the current scope remaining unchanged.

---

# 2. System Description

Supra AI is an AI-assisted supplier and product compliance-screening system for consumer-electronics documentation.

The system is designed to:

1. Receive supplier documents such as CE declarations, RoHS evidence, laboratory test reports, and declarations of conformity.
2. Classify documents.
3. Extract structured information from documents using an LLM-based component.
4. Match extracted product identifiers against an internal SKU catalogue where applicable.
5. Apply deterministic compliance rules.
6. Identify missing, expired, inconsistent, ambiguous, or potentially problematic documentation.
7. Present evidence-linked findings and review-priority information.
8. Route flagged or ambiguous cases to human review.
9. Support generation of Supplier Gap Notices for applicable screening outcomes.
10. Keep the final compliance decision with a human reviewer.

The repository architecture separates:

**AI extraction → structured data → SKU matching → deterministic rules → evidence → human review**

This separation is an important governance control because an LLM-generated extraction is not itself treated as the final compliance decision.

---

# 3. Intended Purpose

The intended purpose is:

> **To assist compliance professionals in screening supplier compliance documentation for consumer-electronics products by extracting structured information, applying predefined deterministic rules, identifying potential documentation issues, and presenting evidence for human review.**

The system is intended for professional/business users such as:

- compliance professionals;
- procurement teams;
- supplier-management teams;
- product/compliance managers; and
- authorised reviewers.

The system is not intended to:

- provide legal advice;
- certify products;
- perform official conformity assessment;
- make legally binding regulatory decisions;
- automatically approve or reject products or suppliers;
- replace laboratory testing;
- replace qualified compliance professionals;
- profile natural persons;
- evaluate employees or candidates;
- make decisions concerning employment, credit, insurance, education, housing, essential services, law enforcement, migration, or justice;
- operate safety-critical physical equipment; or
- submit regulatory decisions or filings automatically to authorities.

---

# 4. AI Act Classification Assessment

## 4.1 Is Supra AI an AI system?

**Yes.**

The system uses an LLM-based component to extract information from supplier documents and therefore falls within the AI Act's concept of an AI system.

The repository also contains an agentic/LangGraph processing pipeline and AI observability/tracing.

---

# 5. Prohibited AI Practices

## 5.1 Assessment

**No prohibited practice has been identified for the documented MVP purpose.**

The current system does not intentionally perform:

- manipulative or deceptive AI practices prohibited by the AI Act;
- social scoring of natural persons;
- prohibited biometric categorisation;
- real-time remote biometric identification in publicly accessible spaces;
- prohibited emotion recognition;
- predictive criminal-risk assessment based on profiling of natural persons; or
- other documented prohibited practices.

The system processes supplier/product documentation rather than assessing individuals.

## 5.2 Control

The following prohibited-use boundary should be documented in product instructions and deployment agreements:

> Supra AI must not be configured or used to assess, rank, profile, manipulate, or make decisions about natural persons in contexts covered by prohibited AI practices.

If the intended purpose changes, the classification must be reassessed before deployment.

---

# 6. Annex I — Product/Safety-Component Assessment

## 6.1 Assessment

**No Annex I high-risk classification has been identified for the current deployment.**

The AI Act treats an AI system as high-risk under the relevant product-safety route where it is intended to be a safety component of a product, or is itself a product covered by specified Union harmonisation legislation, and the applicable product requires third-party conformity assessment. The current consolidated AI Act also clarifies that systems used solely for non-safety-related assistance, performance optimisation, service efficiency, automation, convenience, or quality control do not qualify as safety components on that basis alone.

Supra AI is currently a **document-screening application**.

It is not described as:

- embedded in a consumer-electronics product;
- controlling a physical product;
- implementing a safety function;
- acting as a safety component;
- determining a physical product's safety function; or
- being itself subject to product conformity assessment.

The fact that Supra AI processes CE, RoHS, laboratory-test, and conformity documents does not by itself make Supra AI a safety component.

## 6.2 Reclassification triggers

The assessment must be repeated if Supra AI is:

- embedded in a regulated product;
- used to control a regulated product;
- used to perform a safety function;
- marketed as a conformity/safety component;
- connected directly to safety-critical controls; or
- otherwise brought within the product legislation referenced by Annex I.

---

# 7. Annex III High-Risk Assessment

## 7.1 Assessment

**No Annex III high-risk use case has been identified for the current intended purpose.**

Annex III covers specific areas including:

- biometrics;
- critical infrastructure;
- education and vocational training;
- employment and worker management;
- access to essential private or public services;
- law enforcement;
- migration, asylum and border control; and
- administration of justice and democratic processes.

Supra AI does not currently operate in these use cases.

Although the system supports procurement and supply-chain activities, it does not make decisions about natural persons in the employment, credit, insurance, essential-services, education, law-enforcement, migration, or justice contexts covered by Annex III.

## 7.2 Annex III derogation

The AI Act contains specific rules under Article 6 for certain Annex III systems that do not pose significant risk and do not materially influence decision-making, subject to defined conditions. A provider relying on this route must document its assessment and comply with the applicable registration requirement.

This derogation is **not relied upon for the current Supra AI assessment**, because the documented system is not being classified as an Annex III system in the first place.

---

# 8. Natural-Person Decision Assessment

Supra AI currently evaluates:

- supplier documents;
- products;
- SKUs;
- manufacturer part numbers;
- standards;
- certificates;
- dates;
- laboratory evidence; and
- compliance-screening rules.

It is not intended to evaluate natural persons.

In particular, the system should not be extended to:

- supplier employee scoring;
- recruitment;
- worker performance assessment;
- individual trustworthiness scoring;
- credit decisions;
- insurance eligibility;
- access to essential services;
- education admissions;
- law enforcement;
- migration decisions; or
- judicial decision-making.

If a future feature evaluates a natural person, a new AI Act classification assessment must be completed.

---

# 9. Transparency Obligations

## 9.1 Current legal position

The original AI Act transparency obligations under Article 50 apply from **2 August 2026**. The European Commission published implementation guidance in July 2026.

Therefore, transparency should not be described merely as a future consideration.

## 9.2 Applicability to current Supra AI

The current documented workflow does not appear to trigger the principal Article 50 transparency cases because Supra AI is not currently documented as:

- a chatbot intended to interact directly with natural persons;
- an emotion-recognition system;
- a biometric-categorisation system;
- a deepfake-generation system; or
- a system publishing AI-generated text on matters of public interest without appropriate human review/editorial control.

The Commission's current guidance confirms that Article 50 applies to specified interactive AI and AI-generated-content use cases, rather than to every AI system simply because it uses an LLM.

## 9.3 Recommended transparency control

Even where Article 50 does not currently apply, the product should clearly communicate to professional users that:

> **Supra AI uses AI-assisted document extraction. Extracted information and screening findings must be reviewed against source evidence and do not constitute an autonomous legal or regulatory decision.**

If a conversational interface is introduced, the applicable Article 50 disclosure requirement must be implemented.

If the system begins generating AI-generated content for external publication, the applicable marking/labelling requirements must be assessed.

---

# 10. AI Literacy — Article 4

## 10.1 Current obligation

AI literacy is not merely a future recommendation.

Article 4 requires providers and deployers to take measures supporting AI literacy among staff and other persons involved in operating or using AI systems on their behalf. The provision was amended in July 2026 to clarify that the obligation is to support development of AI literacy rather than guarantee a specific level for every individual.

## 10.2 Supra AI control

Before pilot or production deployment, the provider/deployer should provide appropriate guidance covering:

- what the AI system does;
- what it does not do;
- how extraction confidence/uncertainty should be interpreted;
- how to inspect source evidence;
- how to recognise ambiguous results;
- when human escalation is required;
- how deterministic rule findings differ from AI interpretation;
- how to report errors;
- how to avoid automation bias;
- prohibited uses;
- data-handling requirements; and
- the reviewer's final accountability.

A short reviewer training guide should be maintained as part of the MVP/pilot documentation.

---

# 11. Human Oversight

Human oversight is a core requirement of the Supra AI design.

The intended workflow is:

```text
AI extraction
      ↓
Structured information
      ↓
Deterministic validation
      ↓
Finding / review priority
      ↓
Evidence inspection
      ↓
Human compliance decision
```

The reviewer should be able to inspect:

- extracted fields;
- source evidence;
- document classification;
- SKU/MPN matching;
- triggered rules;
- ambiguous or unresolved information;
- screening status; and
- proposed corrective action.

The reviewer should be able to challenge or correct an incorrect AI output.

The system must not be designed so that a model output is automatically treated as a legally binding compliance decision.

---

# 12. Accuracy, Robustness and Evaluation

The current project includes explicit evaluation of extraction and rule-screening performance.

The evaluation should cover:

- document classification;
- field-level extraction;
- document-type performance;
- SKU matching;
- deterministic rule outcomes;
- false positives;
- false negatives;
- ambiguous values;
- missing information;
- evidence traceability;
- poor-quality documents;
- reviewer overrides; and
- system failures.

The current benchmark should be reported separately from the regulatory classification.

The latest documented benchmark results show:

- **13/13 audit decisions:** 100%;
- **overall extraction accuracy:** 95.9%;
- `standards_tested`: 75%;
- lab-test-report extraction: 100%;
- manufacturer self-declaration extraction: 93.5%.

These results support the existence of an evaluation process but **do not establish production-scale reliability or universal compliance-document accuracy**.

In particular, the lower `standards_tested` result should remain visible as an evaluation limitation.

---

# 13. Evidence and Explainability

Every material finding should be traceable to:

1. the source document;
2. the extracted value;
3. the deterministic rule that evaluated the value; and
4. the resulting screening finding.

The system should distinguish:

### Extracted fact

> "The document states X."

### Rule finding

> "Configured rule Y was triggered because X does not satisfy condition Z."

### AI interpretation

> "The AI suggests that this information may require review."

These categories must not be presented as equivalent.

---

# 14. Deterministic Rule Engine

The compliance-screening rules should remain separate from probabilistic AI extraction wherever practical.

The rule engine should provide:

- reproducible outcomes;
- versioned rules;
- explicit thresholds;
- clear rule identifiers;
- evidence for triggered rules;
- test cases;
- change history; and
- human escalation for unresolved cases.

Rules should not silently change because of an LLM model update.

Changes to:

- regulatory assumptions;
- standards;
- thresholds;
- prompts;
- models;
- SKU data; or
- validation logic

should be version controlled and tested.

---

# 15. General-Purpose AI Model / Vendor Boundary

Supra AI uses an external or underlying LLM component.

The legal obligations of the **GPAI model provider** must be distinguished from the obligations of the **provider of the downstream Supra AI system**.

The AI Act imposes obligations on providers of general-purpose AI models, including technical documentation, information for downstream AI-system providers, copyright-related policies, and publication of a summary of training content. Additional requirements apply to GPAI models with systemic risk. These obligations have applied since 2 August 2025, with enforcement from 2 August 2026.

Supra AI should therefore maintain an inventory of:

- underlying model provider;
- model name;
- model/version;
- API/service version;
- contractual terms;
- data-use policy;
- model-training policy;
- known limitations;
- security information;
- relevant documentation;
- change notifications; and
- applicable subcontractors.

Supra AI should **not claim that it is itself a GPAI model provider** merely because it uses a GPAI model.

The exact legal role depends on whether the project develops, substantially modifies, or merely integrates the underlying model.

---

# 16. Provider Responsibilities

The legal provider of Supra AI must be identified before commercial deployment.

The provider should:

1. Define the intended purpose.
2. Maintain the classification assessment.
3. Document limitations and prohibited uses.
4. Maintain system and model/component inventories.
5. Maintain change control.
6. Maintain evaluation evidence.
7. Maintain human-oversight controls.
8. Provide appropriate instructions to deployers.
9. Support AI-literacy measures.
10. Monitor material incidents and system failures.
11. Maintain appropriate technical and organisational documentation.
12. Reassess classification after material system changes.

If the system becomes high-risk, additional statutory obligations apply.

---

# 17. Deployer Responsibilities

The deployer is the organisation using Supra AI in a professional context.

A deployer should:

- use the system within its intended purpose;
- provide appropriate human oversight;
- ensure users receive appropriate AI-literacy guidance;
- use appropriately relevant input data;
- monitor performance;
- retain required operational records;
- report relevant incidents;
- maintain a manual fallback process;
- prevent unauthorised use;
- investigate material errors;
- stop or restrict use where the system presents unacceptable risk; and
- not extend the system to a new high-risk use case without reassessment.

The deployer remains responsible for how the system is actually used in its operational environment.

---

# 18. Vendor and Subprovider Governance

The production architecture may contain:

- LLM/API providers;
- PDF/OCR services;
- cloud infrastructure;
- workflow/orchestration services;
- monitoring/observability platforms;
- authentication providers; and
- storage services.

A vendor register should be maintained.

| Vendor | Function | AI Act relevance | Evidence required |
|---|---|---|---|
| `[LLM provider]` | AI document extraction | Underlying model/service obligations depend on provider and service | Model/version, terms, technical information, data-use policy, security, change policy |
| `[OCR/PDF provider]` | Document processing | Depends on whether AI is used | Service description, model details if applicable, security and data handling |
| `[Cloud provider]` | Hosting/storage | Supporting infrastructure | Hosting location, security, access controls, subcontractors |
| `LangSmith` / equivalent | Observability/evaluation | Supporting AI infrastructure | Data flow, retention, access, security and deletion controls |
| `[Workflow platform]` | Orchestration | Depends on functionality | Architecture, security, AI functionality, version/change control |

A vendor should not automatically be treated as an AI Act provider merely because it supplies software used by Supra AI.

---

# 19. High-Risk Requirements — Future Conditional Section

If a future deployment is classified as high-risk, the relevant AI Act requirements must be addressed.

These include, depending on the applicable high-risk route:

- risk-management system;
- data and data-governance requirements;
- technical documentation;
- automatic logging;
- instructions for use;
- human oversight;
- accuracy;
- robustness;
- cybersecurity;
- quality-management system;
- conformity assessment;
- EU declaration of conformity;
- registration where applicable;
- post-market monitoring;
- serious-incident reporting;
- corrective action; and
- cooperation with competent authorities.

The current MVP should **not claim compliance with these high-risk requirements** unless the required evidence has been produced.

---

# 20. Important 2026 Application Dates

The AI Act has a staggered application timeline.

As of this assessment date, **3 September 2026**:

| Requirement | Application position |
|---|---|
| AI Act entered into force | 1 August 2024 |
| Prohibited practices | Applied from 2 February 2025 |
| AI literacy | Applied from 2 February 2025; Article 4 amended in 2026 |
| GPAI obligations | Applied from 2 August 2025 |
| General AI Act application | 2 August 2026 |
| Article 50 transparency obligations | Applied from 2 August 2026 |
| Annex III high-risk requirements | **2 December 2027** under the 2026 amendment |
| Annex I/product-safety high-risk requirements | **2 August 2028** under the 2026 amendment |

The July 2026 Digital Omnibus amendment changed the timing for the substantive high-risk requirements because of delays in standards, guidance, and national implementation infrastructure.

These dates should be rechecked whenever this document is materially updated.

---

# 21. AI Act Risk Register

| Risk | Impact | Mitigation | Status |
|---|---|---|---|
| Incorrect document extraction | High | Ground-truth evaluation and human evidence review | Implemented/tested |
| Incorrect compliance rule | High | Deterministic rule engine and rule tests | Implemented; ongoing maintenance |
| Ambiguous extraction treated as fact | High | Explicit ambiguity state and human review | Design requirement |
| Incorrect SKU matching | High | Explicit matching status and review of unmatched cases | Implemented in core pipeline; UI integration requires validation |
| AI output treated as legal decision | High | Human final decision and explicit scope boundary | Design control |
| Model update changes behaviour | Medium/High | Model/version and prompt change control | Required |
| Outdated compliance rule | High | Rule versioning and regulatory-source ownership | Required |
| Poor-quality PDF/OCR | Medium/High | Input-quality detection and human escalation | Required |
| Vendor/model outage | Medium | Manual fallback and operational monitoring | Required |
| Prompt injection/malicious document | High | Input validation and security testing | Required |
| Personal/confidential data exposure | High | Data minimisation, access control and vendor assessment | Required for real-data deployment |
| Unauthorised use outside intended purpose | High | Instructions, training, access control and classification review | Required |
| Expansion into high-risk use case | High | Mandatory reclassification before new use | Design control |
| Insufficient user AI literacy | Medium | Reviewer guidance and training | Required |
| Transparency obligation triggered by future feature | Medium | Feature-level Article 50 assessment | Ongoing |
| Underlying GPAI provider change | Medium/High | Vendor/model inventory and change notification | Required |

---

# 22. Current Repository Evidence

The repository currently provides evidence of:

- a documented supplier-compliance use case;
- a defined MVP boundary;
- AI-assisted document extraction;
- LangGraph-based workflow orchestration;
- deterministic compliance rules;
- SKU matching logic;
- human-review routing;
- evidence-linked findings;
- Gap Notice generation;
- synthetic and public/real-world evaluation documents;
- ground-truth evaluation;
- LangSmith observability;
- benchmark reporting;
- documented limitations and risks.

However, the repository should **not be interpreted as evidence that all AI Act obligations have already been operationalised**.

For example, the repository does not by itself establish:

- a formal legal provider identity;
- a formal deployer identity;
- a completed AI-literacy programme;
- production-grade quality management;
- complete vendor/GPAI documentation;
- formal regulatory incident procedures;
- production conformity assessment;
- high-risk registration;
- or full production technical documentation.

Those are deployment/governance matters.

---

# 23. Pre-Pilot Compliance Checklist

Before introducing real supplier data:

### System classification

- [ ] Intended purpose approved
- [ ] Prohibited-use boundaries documented
- [ ] Annex I assessment completed
- [ ] Annex III assessment completed
- [ ] Classification assumptions documented
- [ ] Reclassification triggers documented

### Provider/deployer

- [ ] Provider legal entity identified
- [ ] Deployer identified
- [ ] Responsibilities allocated
- [ ] User instructions approved
- [ ] Human-review owner appointed

### AI literacy

- [ ] Reviewer guidance prepared
- [ ] AI limitations documented
- [ ] Evidence-review process documented
- [ ] Escalation process documented
- [ ] Automation-bias guidance provided

### AI/model governance

- [ ] Underlying model identified
- [ ] Model version recorded
- [ ] Prompt version recorded
- [ ] Model/data-use terms reviewed
- [ ] Relevant GPAI documentation obtained where applicable
- [ ] Vendor/subprocessor inventory completed
- [ ] Change-control process established

### Evaluation

- [ ] Ground truth established
- [ ] Extraction benchmark completed
- [ ] Rule-engine benchmark completed
- [ ] False-positive analysis completed
- [ ] False-negative analysis completed
- [ ] SKU-matching evaluation completed
- [ ] Evidence traceability validated
- [ ] Known limitations documented

### Transparency

- [ ] AI-assisted nature of system documented for users
- [ ] Article 50 applicability assessed
- [ ] Interactive AI disclosure implemented if applicable
- [ ] AI-generated-content marking assessed if applicable

### Data/security

- [ ] GDPR assessment completed
- [ ] Vendor data flows mapped
- [ ] Hosting locations confirmed
- [ ] Retention controls defined
- [ ] Access controls implemented
- [ ] Security review completed

---

# 24. Reclassification Triggers

A new AI Act assessment is required before implementing any of the following:

- Individual-person scoring or profiling.
- Recruitment or employment decision support.
- Credit or insurance decision support.
- Education admissions or assessment.
- Essential-service eligibility decisions.
- Law-enforcement use.
- Migration/border-control use.
- Judicial decision support.
- Biometric identification/categorisation.
- Emotion recognition.
- Operation of critical infrastructure.
- Control of physical safety functions.
- Embedding Supra AI into a regulated product.
- Removal of mandatory human review.
- Automatic product or supplier approval/rejection.
- New autonomous decision-making functionality.
- Public-facing chatbot functionality.
- Generation of content that may trigger Article 50 obligations.
- Material changes to the underlying AI model or intended purpose.

---

# 25. Final Compliance Position

> **Current assessment: Supra AI is an AI system whose documented MVP use has not been identified as a prohibited AI practice, an Annex I safety-component high-risk system, or an Annex III high-risk use case.**

The current system is designed as an AI-assisted document-screening and decision-support tool for professional compliance users.

Its principal controls are:

- narrow intended purpose;
- deterministic screening rules;
- evidence-linked findings;
- explicit human review;
- evaluation against ground truth;
- AI observability;
- defined out-of-scope uses; and
- reclassification triggers.

The term **"minimal risk"** may be used informally to describe the current position, but the formal conclusion should remain:

> **No prohibited or high-risk classification has currently been identified for the documented intended purpose.**

The classification is conditional and must be reassessed if the system's purpose, users, data, autonomy, integration, or deployment environment changes.

Because the AI Act's general provisions are now applicable and Article 50 transparency obligations apply from 2 August 2026, the project should also ensure that applicable general requirements — particularly **AI literacy, transparency where triggered, provider/deployer governance, and appropriate documentation** — are not overlooked merely because the system is not high-risk.

For the current MVP, the immediate compliance priority is therefore:

1. Preserve the narrow intended purpose.
2. Maintain meaningful human oversight.
3. Document AI-literacy measures.
4. Maintain model/vendor/change records.
5. Continue extraction and rule evaluation.
6. Preserve evidence traceability.
7. Complete GDPR/security/vendor assessments before real-data deployment.
8. Reassess classification before material functionality or deployment changes.

---

# References

1. **Regulation (EU) 2024/1689 — Artificial Intelligence Act**, consolidated version including subsequent amendments.  
   [EUR-Lex — Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689)

2. **Regulation (EU) 2026/1744 — Digital Omnibus on AI**, amending Regulation (EU) 2024/1689, including Article 4 and the application dates for high-risk requirements.  
   [EUR-Lex — Regulation (EU) 2026/1744](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A32026R1744)

3. European Commission. **Guidelines on transparency obligations for providers and deployers of AI systems**, July 2026.  
   [European Commission — AI transparency guidelines](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems)

4. European Commission. **Transparency obligations under Article 50 of the AI Act**, updated 2026.  
   [European Commission — Article 50 FAQ](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act)

5. European Commission. **Guidelines for providers of general-purpose AI models**, 2026.  
   [European Commission — GPAI provider guidelines](https://digital-strategy.ec.europa.eu/en/policies/guidelines-gpai-providers)

6. European Commission. **General-purpose AI obligations under the AI Act**.  
   [European Commission — GPAI obligations](https://digital-strategy.ec.europa.eu/en/factpages/general-purpose-ai-obligations-under-ai-act)

7. European Commission. **Enforcement framework of the AI Act**, updated August 2026.  
   [European Commission — AI Act enforcement](https://digital-strategy.ec.europa.eu/en/policies/enforcement-ai-act)