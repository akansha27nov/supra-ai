# GDPR Documentation — Supra AI

**System:** Supra AI — AI-Assisted Supplier Compliance Screening  
**Author:** Akansha Verma  
**Document status:** MVP / pilot assessment  
**Assessment date:** 2026-09-03
**Review date:** 2026-09-03

> **Important:** This document is an initial GDPR assessment for the Supra AI MVP and capstone. It is not a legal opinion or a substitute for advice from the controller's Data Protection Officer or legal counsel. Before processing real supplier or employee-related personal data, the controller must confirm the actual purposes, lawful basis, data flows, vendors/subprocessors, hosting locations, international transfers, retention periods, security measures, data-subject procedures, and whether a DPIA is required.

---

# 1. Scope and System Purpose

Supra AI is designed to assist compliance teams with reviewing supplier and product documentation, including:

- CE declarations of conformity
- RoHS evidence
- Laboratory test reports
- Supplier certificates
- Technical specifications
- Supplier-provided product documentation
- Internal SKU and product records

The system extracts structured information from documents, resolves product or manufacturer part numbers against internal SKU records where applicable, applies deterministic compliance rules, and presents evidence-linked findings for human review.

The intended purpose is **supplier-document screening and decision support**, not automated legal or regulatory decision-making.

The system should not be used to:

- Evaluate individuals' personality, behaviour, trustworthiness, or employment suitability.
- Profile individuals.
- Make automated decisions about a person's legal rights or access to services.
- Process special-category personal data unless separately assessed and justified.
- Treat AI output as a final legal or regulatory decision.
- Retain supplier documents or extracted personal data longer than necessary.
- Use supplier documents for unrelated model-training or secondary purposes unless separately assessed, legally permitted, and appropriately disclosed.

For the MVP and capstone, synthetic or publicly available documents should be used wherever possible. Real supplier documents should only be introduced after the controller has approved the data-flow, security, retention, vendor, transfer, and governance arrangements.

---

# 2. GDPR Applicability

GDPR applies where Supra AI processes personal data within the scope of the GDPR.

Many supplier compliance documents are primarily about **products, companies, laboratories, certificates, and technical information** and may contain little or no personal data.

However, personal data may appear incidentally, for example:

- Names of supplier contacts
- Business email addresses
- Business telephone numbers
- Names and signatures of responsible persons
- Names of laboratory personnel
- Names appearing in declarations or certificates
- Reviewer comments
- User account information
- Audit-log identifiers
- Uploaded document metadata
- Correspondence associated with supplier remediation

The fact that information appears in a business document does not automatically make it non-personal data. Where information relates to an identified or identifiable natural person, it should be treated as personal data.

The project therefore follows a **data-minimisation approach**: process only the personal data necessary for the defined compliance-screening purpose.

---

# 3. GDPR Roles

## 3.1 Controller

The controller is the organisation that determines the purposes and means of processing personal data.

For a customer deployment, the likely controller is the retailer or other organisation operating the supplier-compliance process.

The final controller determination must be based on the actual deployment rather than the software architecture alone.

## 3.2 Processor

If Supra AI is operated as a service on behalf of a customer and processes personal data according to the customer's documented instructions, the Supra AI service provider may act as a processor.

A processor arrangement should be documented through an appropriate Data Processing Agreement where required.

Processor obligations should include, as applicable:

- Processing personal data only on documented controller instructions.
- Maintaining confidentiality.
- Implementing appropriate technical and organisational security measures.
- Supporting data-subject rights requests.
- Assisting with breach management.
- Assisting with DPIAs and regulatory consultations where required.
- Controlling subprocessors appropriately.
- Providing relevant compliance information to the controller.
- Deleting or returning personal data at the end of the processing relationship, subject to applicable legal requirements.

The controller/processor relationship must be confirmed against the actual facts and contractual arrangements. EDPB guidance emphasises that these roles depend on the substantive determination of purposes and means, rather than simply on contractual labels.

## 3.3 Independent third parties

Some vendors may act as independent controllers for specific processing activities, such as billing, fraud prevention, legal compliance, or their own security operations.

Their role must therefore be assessed individually.

A vendor must not automatically be classified as a processor merely because it receives data from Supra AI.

---

# 4. Data Flow Map

## 4.1 High-level data flow

```text
Supplier / customer user
        |
        | Uploads supplier documents and/or enters review information
        v
Supra AI application
        |
        | File validation and metadata handling
        v
Temporary document processing
        |
        | PDF parsing / text extraction / OCR where applicable
        v
AI extraction service
        |
        | Structured extraction result
        v
Extraction and validation layer
        |
        | Normalisation / validation / evidence association
        v
SKU matching + deterministic rule engine
        |
        | Screening findings / review status
        v
Reviewer interface
        |
        | Human inspection / review / decision
        v
Results / audit records / evaluation data
        |
        +----> Optional Gap Notice generation
        |
        +----> Monitoring / observability
```

## 4.2 Data-flow principle

Personal data should only be sent to an external AI or infrastructure provider where:

1. The transfer is necessary for the documented purpose.
2. The data is covered by an appropriate legal basis.
3. The vendor relationship has been assessed.
4. Appropriate contractual protections are in place.
5. International-transfer requirements have been assessed where applicable.
6. Appropriate security controls are implemented.
7. Retention and deletion arrangements are understood.

The actual data flow must be verified against the deployed architecture before real personal data is processed.

---

# 5. Categories of Data

## 5.1 Supplier and business data

Expected business information includes:

- Supplier name
- Manufacturer name
- Supplier identifier
- Product name
- Product model
- Manufacturer part number
- Internal SKU
- Certificate/document reference
- Applicable standards
- Compliance dates
- Laboratory information
- Accreditation information
- Test results
- Compliance findings

Most of this information is expected to concern legal entities, products, and technical documentation rather than natural persons.

## 5.2 Potential personal data

Potential personal data includes:

| Data category | Example | Purpose |
|---|---|---|
| Business contact data | Supplier contact name/email | Supplier-document administration |
| Professional identity | Name/title of responsible person | Document verification |
| Signature information | Signed declaration | Verification of document evidence |
| User account data | Reviewer identity | Access control and auditability |
| Review metadata | Reviewer, timestamp, action | Audit trail |
| Communication data | Gap Notice recipient | Supplier remediation |
| Technical metadata | IP/log information where collected | Security and operations |

## 5.3 Special-category data

The system is **not designed to process special-category personal data** under Article 9 GDPR.

If special-category data is discovered in an uploaded document, it should not automatically be processed as ordinary compliance data. The controller should assess whether the data can be removed, redacted, excluded, or otherwise handled lawfully.

Special-category processing requires specific additional conditions under Article 9.

---

# 6. Data Minimisation

Supra AI should apply the GDPR principle of data minimisation.

Only information necessary for supplier-compliance screening should be extracted, retained, displayed, or transmitted.

Controls should include:

- Do not collect personal data merely because it appears in a document.
- Do not request unnecessary user information.
- Do not use supplier documents for unrelated purposes.
- Avoid copying entire documents into logs where structured fields or evidence excerpts are sufficient.
- Avoid storing unnecessary prompt/response data.
- Restrict access to supplier documents and reviewer information.
- Prefer synthetic/public documents during development and evaluation.

GDPR Article 5 requires personal data to be adequate, relevant, and limited to what is necessary for the processing purpose.

---

# 7. Purpose Limitation

The defined purpose of personal-data processing is:

> **To support the review, validation, remediation, and auditability of supplier compliance documentation.**

Data should not subsequently be used for unrelated purposes without an appropriate legal and governance assessment.

In particular, supplier documents should not automatically be:

- Used to train unrelated AI models.
- Used for employee profiling.
- Used for marketing.
- Used to assess supplier employees personally.
- Shared with unrelated third parties.
- Used to make unrelated commercial or employment decisions.

Any secondary use requires separate assessment under the GDPR principles and applicable legal basis.

---

# 8. Lawful Basis

The controller must identify and document the lawful basis for each processing activity.

Potential bases may include:

| Processing activity | Potential lawful basis | Confirmation required |
|---|---|---|
| Supplier compliance screening | Legitimate interests and/or legal obligation, depending on the controller's obligations | Controller/legal review |
| Processing supplier contact details | Legitimate interests and/or contract | Controller/legal review |
| Maintaining compliance records | Legal obligation and/or legitimate interests | Controller/legal review |
| Security logging | Legitimate interests and/or legal obligation | Controller/legal review |
| Sending remediation communications | Contract and/or legitimate interests | Controller/legal review |
| Evaluation/development using real documents | Separate assessment required | Do not assume |

**Consent should not be treated as the default lawful basis.**

The correct lawful basis depends on the actual purpose, controller, contractual context, applicable regulatory obligations, and balancing of interests where legitimate interests is relied upon.

GDPR Article 6 requires processing to have an applicable lawful basis.

---

# 9. Transparency and Privacy Information

Where personal data is processed, the controller should provide appropriate privacy information to affected individuals where required.

The privacy notice should explain, as applicable:

- Identity of the controller
- Purpose of processing
- Categories of personal data
- Lawful basis
- Recipients/categories of recipients
- International transfers
- Retention periods
- Data-subject rights
- Right to object where applicable
- Complaint rights
- Automated decision-making information where applicable

The system should not rely on a generic statement that "AI is used."

The controller should explain the role of AI in the workflow in understandable terms, including that Supra AI performs extraction and rule-based screening while final compliance decisions remain with humans.

---

# 10. Automated Decision-Making and Human Oversight

Supra AI is designed as a **human-in-the-loop screening system**.

The intended workflow is:

```text
AI extraction
      ↓
Deterministic rule screening
      ↓
Finding / review priority
      ↓
Human evidence review
      ↓
Human final decision
```

The system must not be configured so that an AI result automatically becomes a legally or similarly significant decision concerning an individual.

The documented use case explicitly excludes automated final compliance decisions.

Where personal data is involved, Article 22 GDPR and related guidance on automated individual decision-making must nevertheless be considered for the actual deployment.

Human involvement must be **meaningful**, not merely a nominal approval step. The reviewer should have access to the relevant extracted information, triggered rules, source evidence, and unresolved issues and should be able to investigate or challenge the result.

---

# 11. Accuracy and Data Quality

GDPR requires personal data to be accurate and, where necessary, kept up to date.

Supra AI should therefore:

- Preserve the distinction between extracted facts and AI interpretation.
- Avoid inventing missing values.
- Represent missing information explicitly.
- Represent ambiguous information as unresolved.
- Provide source evidence for findings.
- Allow human correction of erroneous extracted information.
- Avoid treating an uncertain AI extraction as a verified fact.
- Maintain appropriate correction mechanisms for stored personal data.

AI extraction accuracy testing is documented separately in the project's evaluation and benchmark documentation.

---

# 12. Data Retention

A final retention schedule cannot be defined until the production deployment and controller requirements are known.

The following **proposed retention framework** should therefore be treated as a deployment decision rather than an existing system configuration:

| Data | Proposed approach |
|---|---|
| Uploaded supplier PDF | Retain only for the documented compliance purpose and agreed period |
| Extracted structured data | Retain only while required for screening/audit purposes |
| Temporary processing files | Delete as soon as operationally possible |
| AI prompts/responses | Minimise and retain only where necessary for evaluation, audit, or security |
| Reviewer actions | Retain according to the compliance/audit retention requirement |
| Security logs | Retain according to security and legal requirements |
| Benchmark data | Prefer synthetic/public data; apply separate controls to real data |
| Gap Notices | Retain according to supplier-compliance record requirements |

The controller must define:

- Retention period
- Deletion trigger
- Legal hold process, if applicable
- Backup deletion/expiry approach
- Vendor deletion process
- Procedure for responding to erasure requests

"Keep indefinitely for audit purposes" should not be used without a documented legal/business justification.

---

# 13. Data-Subject Rights

Where personal data is processed, procedures should exist for applicable data-subject rights, including:

- Right of access
- Right to rectification
- Right to erasure
- Right to restriction
- Right to object
- Right to data portability where applicable
- Rights relating to automated decision-making where applicable

The actual applicability of each right depends on the processing activity and legal basis.

Supra AI should support the controller by being able to identify relevant stored records and, where applicable, correct, restrict, export, or delete personal data.

A formal request-handling process should be defined before production deployment.

---

# 14. Security of Processing

The controller and applicable processors must implement security measures appropriate to the risk.

Relevant controls for Supra AI should include:

## 14.1 Access control

- Authentication for reviewer access.
- Least-privilege permissions.
- Restricted access to uploaded documents.
- Restricted access to evaluation and monitoring data.
- Separation between development and production environments.
- Access removal when personnel no longer require access.

## 14.2 Data protection

Where appropriate:

- Encryption in transit.
- Encryption at rest.
- Secure temporary storage.
- Secure deletion.
- Secrets management.
- No API keys or credentials committed to source control.

## 14.3 Application security

- File-type validation.
- File-size limits.
- Malicious-file protection where appropriate.
- Input validation.
- Dependency management.
- Logging of security-relevant events.
- Protection against unauthorised document access.

## 14.4 AI-specific controls

- Do not expose supplier documents unnecessarily to model providers.
- Do not use customer documents for unrelated model training without appropriate assessment and agreement.
- Minimise sensitive content in prompts.
- Record model/provider configuration where necessary for auditability.
- Monitor extraction failures and anomalous behaviour.
- Preserve evidence of how material findings were generated.

## 14.5 Current MVP status

The repository demonstrates the AI extraction, rule-engine, evidence, evaluation, and observability concepts, but **the existence of these application features does not by itself demonstrate production-grade GDPR security compliance**.

Production deployment therefore requires a separate security review.

---

# 15. International Data Transfers

Any transfer of personal data outside the EEA must be identified and assessed.

The controller should maintain a current map of:

- Hosting locations
- AI model provider locations
- Cloud infrastructure locations
- Logging/monitoring locations
- Support-provider access locations
- Backup locations
- Subprocessor locations

Where personal data is transferred to a third country, the controller must identify an appropriate transfer mechanism under Chapter V GDPR, such as an applicable adequacy decision or an appropriate safeguard such as Standard Contractual Clauses, where applicable.

The controller should also assess whether supplementary measures are required.

The EDPB recommends that organisations first identify and map transfers, determine the applicable transfer tool, and assess whether additional safeguards are necessary.

**Current status:** actual Supra AI production transfer locations and providers have not been established in the repository and must therefore be completed before real personal data is processed.

---

# 16. AI Provider and Subprocessor Governance

Before using an external LLM or AI service with real supplier documents, the controller/provider should document:

- Provider legal entity
- Processing role
- Hosting locations
- Data-processing terms
- Subprocessors
- Retention policy
- Model-training/data-use policy
- Security controls
- International transfers
- Deletion process
- Incident-notification process
- Applicable certifications or assurance information where relevant

The project should maintain a vendor/subprocessor register for production.

No assumption should be made that an AI API is automatically GDPR-compliant merely because it is a well-known provider.

---

# 17. Data Processing Agreement

Where a service provider acts as a processor, the parties should establish an appropriate Data Processing Agreement.

The agreement should address, as applicable:

- Subject matter and duration
- Nature and purpose of processing
- Types of personal data
- Categories of data subjects
- Documented controller instructions
- Confidentiality
- Security measures
- Subprocessor arrangements
- International transfers
- Data-subject assistance
- Breach assistance
- DPIA assistance
- Audit/compliance information
- Return/deletion of data

The final DPA should be reviewed against the actual service architecture and vendor contracts.

---

# 18. Data Breach Management

A documented personal-data breach procedure should exist before production use.

The procedure should define:

1. Detection
2. Initial containment
3. Internal escalation
4. Impact assessment
5. Identification of affected data
6. Identification of affected individuals
7. Processor-to-controller notification where applicable
8. Supervisory-authority assessment
9. Data-subject notification assessment
10. Remediation
11. Documentation and lessons learned

Processors should notify the controller without undue delay after becoming aware of a personal-data breach where required by the applicable arrangement.

The controller must assess whether notification to the supervisory authority is required and, where applicable, whether affected individuals must also be informed.

---

# 19. Data Protection Impact Assessment (DPIA)

A DPIA should be completed where the planned processing is likely to result in a high risk to individuals' rights and freedoms.

The EDPB states that controllers must carry out a DPIA before processing where the processing is likely to result in high risk.

For the current Supra AI MVP, the intended workflow is relatively narrow:

- Supplier compliance documents
- Primarily business/product information
- Limited personal-data processing
- No intended special-category processing
- No intended profiling of individuals
- Human final decision-making
- No intended automated decisions concerning individuals

This **does not automatically mean that a DPIA is unnecessary**.

The controller must perform and document a DPIA screening assessment against the actual production processing, applicable supervisory-authority requirements, scale, technologies, data categories, and risks.

If the assessment identifies likely high risk that cannot be sufficiently mitigated, a full DPIA should be completed before processing begins.

As of 2026, the EDPB has also published a DPIA template for consultation/use as part of its work to harmonise DPIA reporting.

---

# 20. Privacy by Design and by Default

Supra AI should implement privacy considerations during system design rather than treating them as a post-deployment task.

Design principles include:

- Minimise personal data collection.
- Restrict processing to the compliance-screening purpose.
- Prefer synthetic/public documents during development.
- Separate development, testing, and production data.
- Avoid unnecessary persistence of raw documents.
- Restrict access to uploaded documents.
- Avoid unnecessary personal data in logs.
- Provide deletion mechanisms.
- Keep human review and accountability explicit.
- Prevent unintended secondary use of supplier data.
- Document external AI-provider data handling.

The EDPB's guidance on data protection by design and by default emphasises considering privacy safeguards when determining the means of processing and assessing risks on a case-by-case basis.

---

# 21. Records of Processing Activities

For a production deployment, the controller should determine whether a Record of Processing Activities (ROPA) is required and maintain one where applicable.

The relevant processing activity can be documented approximately as:

| Field | Description |
|---|---|
| Processing activity | Supplier compliance document screening |
| Purpose | Extract, validate, review and remediate supplier compliance documentation |
| Data subjects | Supplier contacts, responsible persons, internal reviewers where applicable |
| Personal data | Business contact information, names, signatures, user/reviewer metadata |
| Special categories | Not intentionally processed |
| Recipients | Authorised internal users and approved processors/subprocessors |
| Transfers | To be determined from actual deployment |
| Retention | To be defined by controller |
| Security | Access control, encryption, secure storage, deletion, logging |
| Legal basis | To be confirmed by controller |
| DPIA | Screening required; full DPIA if high-risk criteria apply |

---

# 22. Supplier Gap Notices and Personal Data

Supra AI can generate a Supplier Gap Notice when the compliance workflow identifies applicable documentation issues.

A Gap Notice may contain:

- Supplier name
- Document reference
- Failed screening rules
- Supporting evidence
- Corrective action
- Draft supplier communication

Because this communication may contain personal contact information, the following controls apply:

- Only necessary recipient information should be used.
- The content should be reviewed before sending.
- The communication should not contain unnecessary personal data.
- The communication should not state that an AI system has made a legally binding regulatory determination.
- Sending should remain subject to the documented human-review workflow.
- The final communication channel and retention period must be defined by the controller.

---

# 23. Human Review and Accountability

Human oversight is a core control of Supra AI.

The reviewer should be able to inspect:

- Extracted fields
- Document classification
- SKU/MPN matching result
- Triggered deterministic rules
- Evidence supporting findings
- Ambiguous or unresolved information
- Screening decision
- Generated Gap Notice where applicable

The reviewer must be able to investigate and correct erroneous AI output.

The system should not present an AI-generated interpretation as though it were an independently verified fact.

Final responsibility for compliance decisions remains with the authorised human reviewer.

---

# 24. GDPR Risk Register

| Risk | Impact | Mitigation | Current status |
|---|---|---|---|
| Unnecessary personal data in supplier PDFs | Medium | Data minimisation and controlled document scope | Design requirement |
| Personal data sent to external AI provider | High | Vendor assessment, DPA, transfer assessment, minimisation | Must complete before real-data pilot |
| Unauthorised document access | High | Authentication, least privilege, secure storage | Production control required |
| Excessive retention | Medium | Defined retention schedule and deletion process | Not yet finalised |
| Inaccurate AI extraction | Medium/High | Ground-truth evaluation, evidence, human review | Evaluation implemented; production governance required |
| Automated decision-making | High | Human final decision and no automated legal decisions | Design control |
| Special-category data appearing unexpectedly | High | Scope restriction, detection/redaction/escalation | Control required |
| International transfer risk | High | Transfer mapping and appropriate Chapter V mechanism | Must assess actual vendors |
| Supplier Gap Notice sent incorrectly | Medium/High | Human review before sending | Workflow control required |
| Personal data exposed in logs | Medium | Log minimisation and access control | Production control required |
| Breach of supplier documents | High | Security controls and incident response | Production process required |
| Secondary use/model training | High | Purpose limitation and provider contractual controls | Must verify provider terms |

---

# 25. Current MVP GDPR Position

The repository demonstrates several privacy-supporting design principles:

- Narrow supplier-compliance purpose
- Human-in-the-loop review
- No intended automated legal/regulatory decision
- Evidence-linked findings
- Structured extraction rather than unrestricted AI output
- Deterministic validation rules
- Synthetic/public evaluation data
- Explicit out-of-scope treatment of real customer personal data
- AI observability/evaluation

However, the repository **does not by itself constitute evidence of full production GDPR compliance**.

The following items remain deployment dependencies:

- Confirm controller identity.
- Confirm processor/subprocessor roles.
- Complete vendor inventory.
- Complete AI-provider data-processing assessment.
- Confirm hosting locations.
- Assess international transfers.
- Execute required DPAs.
- Define retention periods.
- Implement deletion procedures.
- Implement production access controls.
- Implement appropriate encryption and secrets management.
- Establish data-subject request procedures.
- Establish breach-response procedures.
- Complete DPIA screening and full DPIA if required.
- Complete the production ROPA where required.
- Approve the privacy notice.
- Define production security and governance ownership.

---

# 26. Pilot Data-Handling Policy

For the capstone/MVP demonstration:

### Preferred

- Synthetic documents
- Publicly available compliance documents
- Synthetic supplier identities
- Synthetic SKU/catalogue data
- Non-sensitive evaluation data

### Avoid unless explicitly approved

- Real employee data
- Real customer data
- Personal contact information not required for the demonstration
- Sensitive personal data
- Confidential supplier information
- Production credentials
- Unapproved real supplier documents

If real supplier documents are required for a pilot, the controller must first confirm the lawful basis, purpose, retention, security, vendor processing, international transfers, and applicable contractual controls.

---

# 27. GDPR Implementation Checklist

Before real-data pilot or production deployment:

- [ ] Controller identified
- [ ] DPO/privacy contact identified or not-applicable determination documented
- [ ] Processing purposes documented
- [ ] Data categories documented
- [ ] Data-subject categories documented
- [ ] Lawful basis confirmed for each processing purpose
- [ ] Special-category data assessment completed
- [ ] Data-minimisation controls documented
- [ ] Privacy notice reviewed
- [ ] Processor/controller roles confirmed
- [ ] DPA executed where required
- [ ] Vendor/subprocessor inventory completed
- [ ] AI-provider terms reviewed
- [ ] Model-training/data-use terms reviewed
- [ ] Hosting locations documented
- [ ] International-transfer assessment completed
- [ ] Appropriate transfer mechanisms implemented where required
- [ ] Retention schedule approved
- [ ] Deletion process implemented
- [ ] Data-subject rights process established
- [ ] Access-control model implemented
- [ ] Encryption requirements implemented
- [ ] Secrets management implemented
- [ ] Security logging reviewed
- [ ] Breach-response procedure established
- [ ] DPIA screening completed
- [ ] Full DPIA completed if required
- [ ] ROPA completed where required
- [ ] Production security review completed
- [ ] Human-review accountability confirmed
- [ ] Supplier Gap Notice review process confirmed
- [ ] Production owner assigned

---

# 28. Conclusion

Supra AI is designed as a **narrow, human-in-the-loop supplier compliance screening system**, not as an autonomous regulatory decision-maker.

The GDPR risk profile is reduced by:

- limiting the business purpose,
- minimising personal data,
- avoiding intentional processing of special-category data,
- keeping final decisions with humans,
- using deterministic rules for screening,
- linking findings to source evidence,
- preferring synthetic/public data during development,
- and requiring explicit governance before real supplier data is introduced.

The main GDPR risks are not created by the document-screening concept itself but by the **actual production data flows, external AI providers, retention arrangements, security controls, international transfers, and deployment practices**.

Therefore:

> **Supra AI can be designed for GDPR-aligned deployment, but the current MVP repository should be treated as a technical prototype/pilot assessment rather than evidence of completed production GDPR compliance.**

Production use should begin only after the controller has completed the outstanding legal, vendor, security, retention, transfer, and DPIA assessments applicable to the actual deployment.

---

# References

1. European Union. *Regulation (EU) 2016/679 — General Data Protection Regulation*, including Articles 5, 6, 9, 22, 28, 30, 32 and 35.  
   [EUR-Lex — GDPR Regulation (EU) 2016/679](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679&utm_source=chatgpt.com)

2. European Data Protection Board. *Guidelines 07/2020 on the concepts of controller and processor in the GDPR*.

3. European Data Protection Board. *Automated individual decision-making and profiling*.

4. European Data Protection Board. *Data Protection Impact Assessments — High Risk Processing*.

5. European Data Protection Board. *Data Protection Impact Assessment*.

6. European Data Protection Board. *Recommendations 01/2020 on measures that supplement transfer tools to ensure compliance with the EU level of protection of personal data*.

7. European Data Protection Board. *Template for Data Protection Impact Assessment* (2026 consultation).