# E-LinkUp Documentation Library
**Product:** E-LinkUp (By Euphoria Infotech)  
**Example Tenant:** Euphoria  
**Stack:** Flutter (Web + Android) · Python FastAPI · PostgreSQL · JWT + Refresh Token · Docker · Linux VPS / Azure  
**SEH:** ELU-SEH-001 – Software Engineering Handbook  

---

## Start Here

| Order | Document ID | Document | Path |
|------:|-------------|----------|------|
| 1 | **ELU-DOC-001** | **Documentation Master Index** (central catalogue) | [ELU-DOC-001-Documentation-Master-Index.md](ELU-DOC-001-Documentation-Master-Index.md) |
| 2 | **ELU-MSL-001** | Milestone Tracker (progress dashboard) | [ELU-MSL-001-Milestone-Tracker.md](ELU-MSL-001-Milestone-Tracker.md) |
| 3 | **ELU-DF-001** | Documentation Framework | [00-Framework/ELU-DF-001-Documentation-Framework.md](00-Framework/ELU-DF-001-Documentation-Framework.md) |
| 4 | **ELU-RDM-001** | Product Roadmap | [ELU-RDM-001-Product-Roadmap.md](ELU-RDM-001-Product-Roadmap.md) |
| 5 | **ELU-ADR-001** | Architecture Decision Log | [ELU-ADR-001-Architecture-Decision-Log.md](ELU-ADR-001-Architecture-Decision-Log.md) |
| 6 | **ELU-EFS-001** | Enterprise Functional Specification v1.0 (Approved) | [../ELU-EFS-001-Enterprise-Functional-Specification.md](../ELU-EFS-001-Enterprise-Functional-Specification.md) |
| 7 | **ELU-DEV-001** | Development Standards | [ELU-DEV-001-Development-Standards.md](ELU-DEV-001-Development-Standards.md) |
| 8 | **ELU-RSK-001** | Project Risk Register | [ELU-RSK-001-Project-Risk-Register.md](ELU-RSK-001-Project-Risk-Register.md) |
| 9 | **ELU-RTM-001** | Master Requirements & Traceability Index | [10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md](10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md) |
| 10 | **ELU-SAD-001** | Software Architecture Document | [../ELU-SAD-001.md](../ELU-SAD-001.md) |
| 11 | **ELU-STORY-001** | CRM Business Story | [../ELU-CRM-Story.md](../ELU-CRM-Story.md) |

> Always check **Status** in **ELU-DOC-001** before implementing. Do not use **Deprecated** documents (e.g. **ELU-WF-001** is superseded for implementation by **ELU-EFS-001**).

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
| ELU-RSK | Project Risk Register |
| ELU-DEV | Development Standards |
| ELU-MSL | Milestone Tracker |
| ELU-DOC | Documentation Master Index |
| ELU-DF | Documentation Framework |
| ELU-SAD | Software Architecture Document |

**Status:** Draft · In Review · Approved · Deprecated  

Full rules: **ELU-DF-001 – Documentation Framework** · Catalogue: **ELU-DOC-001 – Documentation Master Index**

---

## Enterprise Functional Specification (EFS)

| Document ID | Description | Path |
|-------------|-------------|------|
| **ELU-EFS-001** | **Approved** — Version 1.0 Enterprise Ready (REQ IDs, RTM, State Transitions, CRUD, NFR, UI Nav, API Contracts) | [ELU-EFS-001-Enterprise-Functional-Specification.md](../ELU-EFS-001-Enterprise-Functional-Specification.md) |
| **ELU-RTM-001** | Master Requirements Index | [ELU-RTM-001-Master-Requirements-Index.md](10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md) |

V1.0 source fragments: `10-EFS-V1-Ready/` (`V1-PF-CRM.md`, `V1-SAL-PRJ.md`, `V1-FIN-SRV-INT.md`)

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
```

---

*© Euphoria Infotech (I) Limited — E-LinkUp Documentation Library*  
*Authoritative catalogue: ELU-DOC-001*
