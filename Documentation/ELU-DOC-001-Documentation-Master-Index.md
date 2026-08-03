# E-LinkUp Documentation Master Index
**Document ID:** ELU-DOC-001  
**Document Name:** Documentation Master Index  
**Version:** 1.2  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Product Management Office (PMO)  
**Document Owner:** PMO  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-DF-001, ELU-SEH-001, ELU-CHR-001, ELU-EFS-001  

---

## 1. Purpose

**ELU-DOC-001** is the **central catalogue** for all E-LinkUp project documentation.  

Teams must consult this index before starting work to confirm:

- The correct **Document ID**  
- Current **Version** and **Status**  
- **Owner**  
- **Related Documents**  

**Rule:** Do not implement against a document with Status = `Deprecated` or an older version than listed here.

---

## 2. Document Numbering Standard

All controlled documents use:

```text
ELU-{TYPE}-{NNN}[-{SUFFIX}]
```

### 2.1 Primary Document Type Prefixes

| Prefix | Document Type | Purpose |
|--------|---------------|---------|
| **ELU-CHR** | Project Charter | Vision, mission, scope, positioning |
| **ELU-SEH** | Software Engineering Handbook | Engineering standards & lifecycle |
| **ELU-BRD** | Business Requirements Document | Domain → Module → Feature catalogue |
| **ELU-BFS** | Business Functional Specification | Module/sub-module functional depth |
| **ELU-EFS** | Enterprise Functional Specification | Workflow implementation specification |
| **ELU-DDD** | Data Dictionary | Field-level definitions (formerly Field Dictionary) |
| **ELU-ERD** | Entity Relationship Diagram | Logical / physical data models |
| **ELU-API** | API Specification | REST / OpenAPI contracts |
| **ELU-UI** | UI Specification | Flutter screen specifications |
| **ELU-RTM** | Requirements Traceability Matrix | REQ → WF → Table → API → Screen → TC |
| **ELU-TST** | Test Specification | Test cases & QA packs (formerly ELU-TC) |
| **ELU-ADR** | Architecture Decision Log | Significant decisions with reason, alternatives, impact |
| **ELU-RDM** | Product Roadmap | Release plan v1.0–v3.0 and module mapping |
| **ELU-RSK** | Project Risk Register | Risk · Probability · Impact · Mitigation |
| **ELU-DEV** | Development Standards | Day-to-day FastAPI / Flutter coding standards |
| **ELU-MSL** | Milestone Tracker | Programme progress dashboard |

### 2.2 Extended / Supporting Prefixes (E-LinkUp Library)

| Prefix | Document Type | Purpose |
|--------|---------------|---------|
| **ELU-DOC** | Documentation Master Index | This catalogue |
| **ELU-DF** | Documentation Framework | Templates & mandatory section rules |
| **ELU-SAD** | Software Architecture Document | System architecture |
| **ELU-HLD** | High-Level Design / Platform Blueprint | Architecture blueprint |
| **ELU-STORY** | Business Story | User-to-user narrative |
| **ELU-WF** | Workflow Specification | Base workflow narratives (superseded by EFS for implementation) |
| **ELU-RBAC** | Permission Matrix | Role × permission packs |
| **ELU-NTF** | Notification Catalogue | Event × channel × template |
| **ELU-RPT** | Report Catalogue | Operational / MIS / Executive reports |

### 2.3 Status Values (Mandatory on Every Document)

| Status | Meaning | May be used for implementation? |
|--------|---------|----------------------------------|
| **Draft** | Work in progress | No (except spikes with PO approval) |
| **In Review** | Circulating for BA / Architect / PO review | No |
| **Approved** | Baseline for the stated version | **Yes** |
| **Deprecated** | Replaced by a newer document/version | **No** — follow Related Documents |

### 2.4 Version History (Mandatory on Every Document)

Every controlled document must include a revision table:

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | YYYY-MM-DD | Author / Org | Initial release |
| 1.1 | … | … | Description of change |

### 2.5 Cross-Reference Rule

Wherever another document is mentioned, cite its **Document ID and title**:

> See **ELU-EFS-001 – Enterprise Functional Specification**.

Do **not** write vague references such as “see the workflow document.”

---

## 3. Master Catalogue

### 3.1 Governance & Index

| Document ID | Title | Version | Status | Owner | Path / Location | Related Documents |
|-------------|-------|---------|--------|-------|-----------------|-------------------|
| ELU-DOC-001 | Documentation Master Index | 1.0 | Approved | PMO | `Documentation/ELU-DOC-001-Documentation-Master-Index.md` | ELU-DF-001, ELU-SEH-001 |
| ELU-DF-001 | Documentation Framework & Specification Template | 1.1 | Approved | PMO | `Documentation/00-Framework/ELU-DF-001-Documentation-Framework.md` | ELU-DOC-001, ELU-SEH-001, ELU-EFS-001, ELU-ADR-001 |
| ELU-ADR-001 | Architecture Decision Log | 1.0 | Approved | Solution Architecture / PMO | `Documentation/ELU-ADR-001-Architecture-Decision-Log.md` | ELU-DOC-001, ELU-SAD-001, ELU-EFS-001, ELU-DF-001 |
| ELU-RDM-001 | Product Roadmap | 1.0 | Approved | Product Owner | `Documentation/ELU-RDM-001-Product-Roadmap.md` | ELU-DOC-001, ELU-BRD-001, ELU-EFS-001, ELU-MSL-001, ELU-RSK-001 |
| ELU-RSK-001 | Project Risk Register | 1.0 | Approved | PMO | `Documentation/ELU-RSK-001-Project-Risk-Register.md` | ELU-DOC-001, ELU-RDM-001, ELU-MSL-001, ELU-ADR-001 |
| ELU-DEV-001 | Development Standards | 1.0 | Approved | Tech Lead | `Documentation/ELU-DEV-001-Development-Standards.md` | ELU-DOC-001, ELU-SEH-001, ELU-SAD-001, ELU-ADR-001, ELU-EFS-001 |
| ELU-MSL-001 | Milestone Tracker | 1.0 | Approved | PMO | `Documentation/ELU-MSL-001-Milestone-Tracker.md` | ELU-DOC-001, ELU-RDM-001, ELU-RSK-001, ELU-EFS-001 |
| ELU-SEH-001 | Software Engineering Handbook | — | Planned | Engineering | *(to be authored)* | ELU-DF-001, ELU-DEV-001, ELU-CHR-001, ELU-ADR-001 |

### 3.2 Charter, Requirements & Architecture

| Document ID | Title | Version | Status | Owner | Path / Location | Related Documents |
|-------------|-------|---------|--------|-------|-----------------|-------------------|
| ELU-CHR-001 | Project Charter *(alias ELU-PC-001)* | 1.0 | Draft | PMO | Source: `CRM Documentation.docx` | ELU-BRD-001, ELU-HLD-001, ELU-SAD-001 |
| ELU-BRD-001 | Business Requirements Document | 1.0 | Draft | PMO / BA | Source: `CRMFeature.xlsx` (BRD sheet) | ELU-CHR-001, ELU-BFS-*, ELU-EFS-001 |
| ELU-HLD-001 | Platform Blueprint / HLD | 1.0 | Draft | Solution Architecture | Source: `CRM Documentation.docx` | ELU-CHR-001, ELU-SAD-001 |
| ELU-SAD-001 | Software Architecture Document | 1.0 | In Review | Solution Architecture | `ELU-SAD-001.md` | ELU-CHR-001, ELU-HLD-001, ELU-EFS-001, ELU-BRD-001, ELU-ADR-001 |
| ELU-STORY-001 | CRM Business Story (User-to-User) | 1.1 | Approved | PMO / BA | `ELU-CRM-Story.md` | ELU-CHR-001, ELU-EFS-001, ELU-WF-001 |

### 3.3 Workflow & Enterprise Functional Specification

| Document ID | Title | Version | Status | Owner | Path / Location | Related Documents |
|-------------|-------|---------|--------|-------|-----------------|-------------------|
| ELU-WF-001 | Business Workflow Documentation | 1.1 | Deprecated | PMO | `ELU-Workflow-Documentation.md` | **Superseded for implementation by ELU-EFS-001** (base narrative retained) |
| ELU-EFS-001 | Enterprise Functional Specification — Workflow Domain | 1.0 | Approved | Solution Architecture / BA / PO | `ELU-EFS-001-Enterprise-Functional-Specification.md` | ELU-WF-001, ELU-BRD-001, ELU-BFS-*, ELU-RTM-001, ELU-SAD-001, ELU-DF-001 |
| ELU-RTM-001 | Master Requirements & Traceability Index | 1.0 | Approved | BA / QA | `Documentation/10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md` | ELU-EFS-001, ELU-TST-* |

### 3.4 Business Functional Specifications (BFS Packs)

| Document ID | Title | Version | Status | Owner | Path / Location | Related Documents |
|-------------|-------|---------|--------|-------|-----------------|-------------------|
| ELU-BFS-PF | Platform Foundation BFS (PF-001…011) | 1.0 | Approved | BA | `Documentation/01-BFS-Platform-Foundation/ELU-BFS-PF-Platform-Foundation.md` | ELU-BRD-001, ELU-EFS-001, ELU-DF-001 |
| ELU-BFS-CRM | CRM BFS (CRM-001…004) | 1.0 | Approved | BA | `Documentation/02-BFS-CRM/ELU-BFS-CRM.md` | ELU-BRD-001, ELU-EFS-001 |
| ELU-BFS-SAL | Sales BFS (SAL-001…004) | 1.0 | Approved | BA | `Documentation/03-BFS-Sales/ELU-BFS-SAL.md` | ELU-BRD-001, ELU-EFS-001 |
| ELU-BFS-PRJ | Projects BFS (PRJ-001…006) | 1.0 | Approved | BA | `Documentation/04-BFS-Projects/ELU-BFS-PRJ.md` | ELU-BRD-001, ELU-EFS-001 |
| ELU-BFS-FIN | Finance BFS (FIN-001…004) | 1.0 | Approved | BA | `Documentation/05-BFS-Finance/ELU-BFS-FIN.md` | ELU-BRD-001, ELU-EFS-001 |
| ELU-BFS-SRV | Service BFS (SRV-001…003) | 1.0 | Approved | BA | `Documentation/06-BFS-Service/ELU-BFS-SRV.md` | ELU-BRD-001, ELU-EFS-001 |
| ELU-BFS-INT | Integration BFS (INT-001…004) | 1.0 | Approved | BA | `Documentation/07-BFS-Integration/ELU-BFS-INT.md` | ELU-BRD-001, ELU-EFS-001 |
| ELU-BFS-CPS | Core Platform Services BFS (CPS-001…008) | 1.0 | Approved | BA | `Documentation/08-BFS-Core-Platform/ELU-BFS-CPS.md` | ELU-BRD-001, ELU-EFS-001 |

### 3.5 Planned Downstream Engineering Packs

| Document ID Pattern | Title | Version | Status | Owner | Related Documents |
|---------------------|-------|---------|--------|-------|-------------------|
| ELU-DDD-{DOM} | Data Dictionary | — | Planned | Data Architect / BA | ELU-BFS-*, ELU-ERD-*, ELU-EFS-001 |
| ELU-ERD-{DOM} | Entity Relationship Diagram | — | Planned | Data Architect | ELU-DDD-*, ELU-BFS-* |
| ELU-API-{DOM} | API Specification (OpenAPI) | — | Planned | Tech Lead | ELU-EFS-001, ELU-BFS-* |
| ELU-UI-{DOM} | UI / Flutter Specification | — | Planned | Frontend Lead | ELU-EFS-001, ELU-BFS-* |
| ELU-TST-{DOM} | Test Specification | — | Planned | QA Lead | ELU-RTM-001, ELU-EFS-001, ELU-BFS-* |
| ELU-RBAC-{DOM} | Permission Matrix | — | Planned | Security / BA | ELU-EFS-001 (CRUD matrices) |
| ELU-NTF-{DOM} | Notification Catalogue | — | Planned | BA | ELU-EFS-001 |
| ELU-RPT-{DOM} | Report Catalogue | — | Planned | BA / Analytics | ELU-EFS-001 |

---

## 4. Recommended Reading Order

| Order | Audience | Documents |
|------:|----------|-----------|
| 1 | Everyone | **ELU-DOC-001** (this index) → **ELU-DF-001** |
| 2 | Business / Product | **ELU-CHR-001** → **ELU-STORY-001** → **ELU-BRD-001** |
| 3 | BA / Architect | **ELU-BFS-*** → **ELU-EFS-001** → **ELU-RTM-001** |
| 4 | Engineering | **ELU-SAD-001** → **ELU-DEV-001** → **ELU-EFS-001** → planned **ELU-DDD / ERD / API / UI / TST** |
| 5 | QA / PMO | **ELU-MSL-001** → **ELU-RSK-001** → **ELU-RTM-001** → **ELU-TST-*** |
| 6 | Product | **ELU-RDM-001** → **ELU-BRD-001** → **ELU-MSL-001** |

---

## 5. Document Lifecycle

```text
Draft → In Review → Approved → (revision) Draft/In Review → Approved
                              ↘ Deprecated (when replaced)
```

| Action | Who | Updates |
|--------|-----|---------|
| Create document | Author | Register row in **ELU-DOC-001** |
| Change status | Document Owner | Update status here + on document header |
| Approve version | PO + Architect (as applicable) | Set Status = Approved; bump Version History |
| Deprecate | PMO | Set Status = Deprecated; point Related Documents to successor |

---

## 6. Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP / PMO | Initial Master Index; formalized document numbering standard, status model, and catalogue of existing + planned artefacts |
| 1.1 | 2026-07-31 | EIIP / PMO | Registered ELU-ADR-001 Architecture Decision Log; added ELU-ADR prefix to numbering standard |
| 1.2 | 2026-07-31 | EIIP / PMO | Registered ELU-RDM-001, ELU-RSK-001, ELU-DEV-001, ELU-MSL-001 |

---

*© Euphoria Infotech (I) Limited — ELU-DOC-001 Documentation Master Index*
