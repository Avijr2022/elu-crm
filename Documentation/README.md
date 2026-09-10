# E-LinkUp Documentation Library
**Product:** E-LinkUp (By Euphoria Infotech)  
**Example Tenant:** Euphoria  
**Stack:** Flutter (Web + Android) · Python FastAPI · PostgreSQL · JWT + Refresh Token · Docker · Linux VPS / Azure  
**SEH:** ELU-SEH-001 – Software Engineering Handbook  

---

## Start Here

| Order | Document ID | Document | Path |
|------:|-------------|----------|------|
| 0 | **ELU-CON-001** | **Enterprise Engineering Constitution (Frozen)** | [00-Framework/ELU-CON-001-Enterprise-Engineering-Constitution.md](00-Framework/ELU-CON-001-Enterprise-Engineering-Constitution.md) · [00_Project_Constitution.md](00_Project_Constitution.md) |
| 0a | **ELU-AI-001** | Cursor AI Governance + Rules | [ELU-AI-001-Cursor-AI-Governance.md](ELU-AI-001-Cursor-AI-Governance.md) · [Cursor_Rules.md](Cursor_Rules.md) |
| 0b | **ELU-GOV-VAL-001** | Governance Validation Report (96% · STOP before code) | [ELU-GOV-VAL-001-Governance-Validation-Report.md](ELU-GOV-VAL-001-Governance-Validation-Report.md) |
| 1 | **ELU-DOC-001** | **Documentation Master Index** (central catalogue) | [ELU-DOC-001-Documentation-Master-Index.md](ELU-DOC-001-Documentation-Master-Index.md) |
| 2 | **ELU-MSL-001** | Milestone Tracker (progress dashboard) | [ELU-MSL-001-Milestone-Tracker.md](ELU-MSL-001-Milestone-Tracker.md) |
| 2a | **ELU-MSL-002** | CRM Build Tracker (implementation status) | [ELU-MSL-002-CRM-Build-Tracker.md](ELU-MSL-002-CRM-Build-Tracker.md) |
| 3 | **ELU-DF-001** | Documentation Framework | [00-Framework/ELU-DF-001-Documentation-Framework.md](00-Framework/ELU-DF-001-Documentation-Framework.md) |
| 4 | **ELU-RDM-001** | Product Roadmap | [ELU-RDM-001-Product-Roadmap.md](ELU-RDM-001-Product-Roadmap.md) |
| 5 | **ELU-EDM-001** | Edition × Module Matrix | [ELU-EDM-001-Edition-Module-Matrix.md](ELU-EDM-001-Edition-Module-Matrix.md) |
| 5a | **ELU-L2C-001** | Lead-to-Cash Docs Route (Completed) | [ELU-L2C-001-Lead-to-Cash-Docs-Route.md](ELU-L2C-001-Lead-to-Cash-Docs-Route.md) |
| 6 | **ELU-ADR-001** | Architecture Decision Log (incl. ADR-015 RLS + §7 AI immutability) | [ELU-ADR-001-Architecture-Decision-Log.md](ELU-ADR-001-Architecture-Decision-Log.md) |
| 7 | **ELU-EFS-001** | Enterprise Functional Specification v1.0 (Approved) | [../ProjectStartupfiles/ELU-EFS-001-Enterprise-Functional-Specification.md](../ProjectStartupfiles/ELU-EFS-001-Enterprise-Functional-Specification.md) |
| 8 | **ELU-EFS-SOT-001** | EFS Source-of-Truth Control | [10-EFS-V1-Ready/ELU-EFS-SOT-001.md](10-EFS-V1-Ready/ELU-EFS-SOT-001.md) |
| 9 | **ELU-DEV-001** | Development Standards | [ELU-DEV-001-Development-Standards.md](ELU-DEV-001-Development-Standards.md) |
| 10 | **ELU-RSK-001** | Project Risk Register | [ELU-RSK-001-Project-Risk-Register.md](ELU-RSK-001-Project-Risk-Register.md) |
| 11 | **ELU-RTM-001** | Master Requirements & Traceability Index | [10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md](10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md) |
| 12 | **ELU-SAD-001** | Software Architecture Document (Approved) | [../ProjectStartupfiles/ELU-SAD-001.md](../ProjectStartupfiles/ELU-SAD-001.md) |
| 13 | **ELU-STORY-001** | CRM Business Story | [../ProjectStartupfiles/ELU-CRM-Story.md](../ProjectStartupfiles/ELU-CRM-Story.md) |
| 14 | **ELU-SEC-001** | Threat Model | [12-Security-Ops/ELU-SEC-001-Threat-Model.md](12-Security-Ops/ELU-SEC-001-Threat-Model.md) |
| 15 | **ELU-OPS-001** | Backup & DR | [12-Security-Ops/ELU-OPS-001-Backup-DR.md](12-Security-Ops/ELU-OPS-001-Backup-DR.md) |
| 16 | **ELU-CMP-001** | Data Protection & Retention | [12-Security-Ops/ELU-CMP-001-Data-Protection.md](12-Security-Ops/ELU-CMP-001-Data-Protection.md) |

> Always check **Status** in **ELU-DOC-001** before implementing. Do not use **Deprecated** documents (e.g. **ELU-WF-001** is superseded for implementation by **ELU-EFS-001**). **Implementation is gated** until human approval after **ELU-GOV-VAL-001**.

---

## Document Numbering Standard

| Prefix | Document Type |
|--------|---------------|
| ELU-CHR | Project Charter |
| ELU-SEH | Software Engineering Handbook |
| ELU-BRD | Business Requirements Document |
| ELU-BFS | Business Functional Specification |
| ELU-EFS | Enterprise Functional Specification |
| ELU-DDD | Data Dictionary |
| ELU-ERD | Entity Relationship Diagram |
| ELU-API | API Specification |
| ELU-UI | UI Specification |
| ELU-RTM | Requirements Traceability Matrix |
| ELU-TST | Test Specification |
| ELU-ADR | Architecture Decision Log |
| ELU-RDM | Product Roadmap |
| ELU-EDM | Edition × Module Matrix |
| ELU-RSK | Project Risk Register |
| ELU-DEV | Development Standards |
| ELU-MSL | Milestone Tracker |
| ELU-DOC | Documentation Master Index |
| ELU-CON | Enterprise Engineering Constitution |
| ELU-AI | Cursor AI Governance |
| ELU-GOV-VAL | Governance Validation Report |
| ELU-DF | Documentation Framework |
| ELU-SAD | Software Architecture Document |
| ELU-SEC | Security / Threat Model |
| ELU-OPS | Operations (Backup/DR) |
| ELU-CMP | Compliance / Data Protection |

**Status:** Draft · In Review · Approved · Frozen · Deprecated  

Full rules: **ELU-DF-001 – Documentation Framework** · Catalogue: **ELU-DOC-001 – Documentation Master Index**

---

## Engineering Packs (v1.0 Lead-to-Cash)

| Document ID | Description | Path |
|-------------|-------------|------|
| ELU-DDD/ERD/API/UI/TST | **PF · CRM · SAL · PRJ · FIN** | [11-Engineering/](11-Engineering/) |
| ELU-CPS-STUB-001 | v1.0 shared approval/notification stubs | [11-Engineering/ELU-CPS-STUB-001.md](11-Engineering/ELU-CPS-STUB-001.md) |
| ELU-L2C-001 | Completion route (Done) | [ELU-L2C-001-Lead-to-Cash-Docs-Route.md](ELU-L2C-001-Lead-to-Cash-Docs-Route.md) |

---

## Enterprise Functional Specification (EFS)

| Document ID | Description | Path |
|-------------|-------------|------|
| **ELU-EFS-001** | **Approved** — Implementation SoT for workflows | [../ProjectStartupfiles/ELU-EFS-001-Enterprise-Functional-Specification.md](../ProjectStartupfiles/ELU-EFS-001-Enterprise-Functional-Specification.md) |
| **ELU-EFS-SOT-001** | Fragment roles & change control | [10-EFS-V1-Ready/ELU-EFS-SOT-001.md](10-EFS-V1-Ready/ELU-EFS-SOT-001.md) |
| **ELU-RTM-001** | Master Requirements Index + coverage checklist | [10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md](10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md) |

V1.0 companions: `10-EFS-V1-Ready/` (`V1-PF-CRM.md`, `V1-SAL-PRJ.md`, `V1-FIN-SRV-INT.md`)  
Enrichment extracts (do not edit independently): `09-EFS-Enrichments/`

---

## Business Functional Specification Packs

| Document ID | Domain | Path |
|-------------|--------|------|
| ELU-BFS-PF | Platform Foundation (PF-001…011) | [01-BFS-Platform-Foundation/ELU-BFS-PF-Platform-Foundation.md](01-BFS-Platform-Foundation/ELU-BFS-PF-Platform-Foundation.md) |
| ELU-BFS-CRM | CRM (CRM-001…004) | [02-BFS-CRM/ELU-BFS-CRM.md](02-BFS-CRM/ELU-BFS-CRM.md) |
| ELU-BFS-SAL | Sales (SAL-001…004) | [03-BFS-Sales/ELU-BFS-SAL.md](03-BFS-Sales/ELU-BFS-SAL.md) |
| ELU-BFS-PRJ | Projects (PRJ-001…006) | [04-BFS-Projects/ELU-BFS-PRJ.md](04-BFS-Projects/ELU-BFS-PRJ.md) |
| ELU-BFS-FIN | Finance (FIN-001…004) | [05-BFS-Finance/ELU-BFS-FIN.md](05-BFS-Finance/ELU-BFS-FIN.md) |
| ELU-BFS-SRV | Service (SRV-001…003) | [06-BFS-Service/ELU-BFS-SRV.md](06-BFS-Service/ELU-BFS-SRV.md) |
| ELU-BFS-INT | Integration (INT-001…004) | [07-BFS-Integration/ELU-BFS-INT.md](07-BFS-Integration/ELU-BFS-INT.md) |
| ELU-BFS-CPS | Core Platform (CPS-001…008) | [08-BFS-Core-Platform/ELU-BFS-CPS.md](08-BFS-Core-Platform/ELU-BFS-CPS.md) |

---

## Downstream Engineering Chain

```text
ELU-BFS-*  →  ELU-DDD-*  →  ELU-ERD-*  →  ELU-API-*  →  ELU-UI-*  →  ELU-TST-*
                 ↑
            ELU-EFS-001 + ELU-RTM-001 (REQ-* anchors)
            ELU-EDM-001 (edition gates) · ELU-SEC-001 · ADR-015
```

---

*© Euphoria Infotech (I) Limited — E-LinkUp Documentation Library*  
*Authoritative catalogue: ELU-DOC-001*
