
# System Architecture & UI/UX Design Specification
## Project: Supra AI — AI-Assisted Supplier Compliance Screening
**Document Version:** 2.0  
**Target Platform:** Desktop (1440px+) & Tablet Landscape (1024px+)  
**Primary Stakeholder:** Chleo, Head of Procurement and Supply Chain Operations  
**Target Users:** Procurement Officers, Quality & Compliance Reviewers, Supplier Operations[cite: 2, 3]  

---

## 1. Executive Summary & Product Vision

### 1.1 Context & Background
Supra AI is an enterprise-grade compliance screening layer built for Chleo, Head of Procurement and Supply Chain Operations at a mid-sized European omnichannel retailer (~200 employees, ~2,000 active consumer electronics SKUs sourced from EU and non-EU suppliers)[cite: 1, 3]. Supplier compliance documentation—such as CE declarations of conformity, RoHS restriction certificates, WEEE registrations, EMC test reports, and Low Voltage Directive files—is currently fragmented across PDFs, spreadsheets, and email threads[cite: 1, 3].

Manual checking introduces operational bottlenecks, delayed onboarding, and human fatigue errors (manual review error rates range from 5% to 15%). Supra AI addresses this by providing an evidence-linked screening layer: Tier 1 extracts structured data using an LLM, Tier 2 evaluates deterministic Python business rules, and Tier 3 surfaces prioritized evidence for human approval[cite: 1, 3].

### 1.2 UI/UX Transformation Objective
The initial Streamlit proof-of-concept (POC) relied on a developer-oriented layout: vertical single-column scrolling, unstyled raw JSON data trees (`{ "sku_code": NULL, ... }`), plain text decision banners, and static metrics.

This specification replaces that interface with a high-density **3-Zone Compliance Workspace** optimized for side-by-side audit sessions, document evidence mapping, activity-aware AI co-pilot support, and tablet/desktop ergonomics[cite: 1, 2, 3].

---

## 2. Information Architecture & Layout Paradigm

### 2.1 The 3-Zone Workspace Model
To prevent context switching and avoid switching between browser tabs or modal windows during document reviews, the platform uses a synchronous 3-zone layout.


