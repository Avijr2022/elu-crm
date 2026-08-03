# E-LinkUp Documentation Framework
**Document ID:** ELU-DF-001  
**Document Name:** Enterprise Documentation Framework & Specification Template  
**Version:** 1.3  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Product Owner / Enterprise Solution Architecture / Business Analysis  
**Document Owner:** PMO  
**SEH Alignment:** ELU-SEH-001 – Software Engineering Handbook  
**Technology Stack:** Flutter (Web + Android) · Python FastAPI · PostgreSQL · JWT + Refresh Token · Docker · Linux VPS / Azure  
**Related Documents:** ELU-DOC-001, ELU-SEH-001, ELU-CHR-001, ELU-BRD-001, ELU-HLD-001, ELU-SAD-001, ELU-STORY-001, ELU-EFS-001, ELU-RTM-001  

---

## Document Control

| Field | Value |
|-------|-------|
| Status | Approved |
| Owner | PMO |
| Catalogue | See **ELU-DOC-001 – Documentation Master Index** |

### Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-30 | EIIP | Initial Documentation Framework and BFS seventeen-section template |
| 1.1 | 2026-07-31 | EIIP / PMO | Formalized document numbering (CHR/SEH/BRD/BFS/EFS/DDD/ERD/API/UI/RTM/TST); Status model; Version History; cross-reference rules; aligned Field Dictionary → ELU-DDD and Test Pack → ELU-TST |
| 1.2 | 2026-07-31 | EIIP / PMO | Added ELU-ADR Architecture Decision Log to numbering standard; decisions mandatory for significant architecture choices |
| 1.3 | 2026-07-31 | EIIP / PMO | Added ELU-RDM, ELU-RSK, ELU-DEV, ELU-MSL document types |

---

## 0. Purpose of This Framework

This framework defines the **single mandatory standard** for producing every E-LinkUp specification artefact:

| Artefact Family | Downstream Engineering Output |
|-----------------|-------------------------------|
| Business Functional Specification (BFS) | Tables, Data Dictionary, ERD, Rules, Workflow, APIs, Screens, RBAC, Notifications, Reports, Tests |
| Data Dictionary (ELU-DDD) | PostgreSQL DDL + SQLAlchemy models |
| API Specification | FastAPI routers + OpenAPI |
| Screen Specification | Flutter routes/widgets |
| Workflow Specification | Workflow Engine definitions |
| Test Specification | QA / automation cases |

**Rule:** No module enters development until its **Business Functional Specification (BFS)** is complete for all seventeen mandatory sections defined below.

This document is written for commercial multi-tenant SaaS quality comparable to Dynamics 365, SAP S/4, Salesforce, and Oracle Cloud ERP documentation discipline — adapted to Euphoria’s SEH and E-LinkUp architecture.

---

## 1. Documentation Hierarchy (SEH)

```text
ELU-DOC-001  Documentation Master Index  ← start here
ELU-DF-001   Documentation Framework (this document)
ELU-SEH-001  Software Engineering Handbook
ELU-CHR-001  Project Charter
ELU-BRD-001  Business Requirements Document
ELU-STORY-001 Business Story
ELU-HLD-001  Platform Blueprint / HLD
ELU-SAD-001  Software Architecture Document
ELU-EFS-001  Enterprise Functional Specification
ELU-RTM-001  Requirements Traceability Matrix
        │
        ▼
ELU-BFS-{DOM}   Business Functional Specification
        │
        ├── ELU-DDD-{DOM}   Data Dictionary
        ├── ELU-ERD-{DOM}   Entity Relationship Diagram
        ├── ELU-API-{DOM}   API Specification
        ├── ELU-UI-{DOM}    UI / Flutter Specification
        ├── ELU-TST-{DOM}   Test Specification
        ├── ELU-RBAC-{DOM}  Permission Matrix
        ├── ELU-NTF-{DOM}   Notification Catalogue
        └── ELU-RPT-{DOM}   Report Catalogue
```

### 1.0 Document Numbering Standard (Mandatory)

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

**Status values:** `Draft` | `In Review` | `Approved` | `Deprecated`  

**Cross-reference rule:** Always cite Document ID + title, e.g. **ELU-EFS-001 – Enterprise Functional Specification**.

Full catalogue: **ELU-DOC-001 – Documentation Master Index**.

### 1.1 Coding Convention (Mandatory)

| Level | Pattern | Example |
|-------|---------|---------|
| Domain | `{DOMAIN}` | `PF`, `CRM`, `SAL`, `PRJ`, `FIN`, `SRV`, `INT`, `CPS` |
| Module | `{DOMAIN}-{nnn}` | `CRM-001` Lead Management |
| Sub Module | `{DOMAIN}-{nnn}-{nnn}` | `CRM-001-001` Lead |
| Feature | `{DOMAIN}-{nnn}-{nnn}-{nnn}` | `CRM-001-001-001` Lead Capture |
| Business Rule | `BR-{DOMAIN}-{nnn}` | `BR-CRM-001` |
| Requirement | `REQ-{DOMAIN}-{nnn}` | `REQ-CRM-001` Create a Lead |
| NFR | `NFR-{DOMAIN}-{nnn}` | `NFR-CRM-001` Lead create p95 < 500ms |
| Workflow | `WF-{DOMAIN}-{nnn}` | `WF-CRM-001` |
| Test Case | `TC-{DOMAIN}-{nnn}` | `TC-CRM-001` |
| Table | snake_case plural/singular per data standard | `lead`, `lead_activity` |
| Permission | `{object}.{action}` | `lead.create` |
| API | `/api/v1/{domain}/{resources}` | `/api/v1/crm/leads` |
| Document | `ELU-{TYPE}-{CODE}` | `ELU-BFS-CRM`, `ELU-DDD-CRM`, `ELU-TST-CRM` |

### 1.2 Example Tenant & Actor Naming

| Convention | Value |
|------------|-------|
| Example tenant | **Euphoria** |
| Actor naming | CRM / ERP **user roles** only (no fictional third-party company names) |
| Object naming | Standard CRM/ERP nouns: Lead, Contact, Customer, Opportunity, Quotation, Sales Order, Project, Invoice, Ticket |

### 1.3 EFS Version 1.0 Enterprise Ready — Mandatory Artefacts

Every workflow in **ELU-EFS-001** must include these seven artefacts (in addition to the standard 15 EFS enrichment sections):

| # | Artefact | Anchor |
|---|----------|--------|
| 16 | Requirement IDs | `REQ-*` |
| 17 | Requirements Traceability Matrix | REQ → WF → Table → API → Screen → TC |
| 18 | State Transition Diagram | Allowed / Invalid / Re-open / Rollback |
| 19 | CRUD Responsibility Matrix | Role × Create/Read/Update/Approve/Delete |
| 20 | Non-Functional Requirements | Performance, Security, Audit, Scalability, Availability, Retention |
| 21 | UI Navigation | Flutter screen flow |
| 22 | API Contract Summary | Method × Endpoint × Purpose |

`REQ-*` is the **single project-wide traceability anchor** for BA, Development, and QA.

---

## 2. Mandatory BFS Template (Seventeen Sections)

Every **Module** and **Sub Module** BFS **must** contain the following sections **in this exact order**. Do not skip. Do not rename.

---

### Section 1 — Business Objective

| Subsection | Required Content |
|------------|------------------|
| 1.1 Why this module exists | Problem statement in enterprise terms |
| 1.2 Business value | Measurable / qualitative value for Euphoria tenant users |
| 1.3 Business scope | In scope / Out of scope |
| 1.4 Users involved | High-level role list (detail in §2) |
| 1.5 Module reference | Domain, Module ID, Sub Module ID, Feature ID, Priority, Phase, Release |

**Header block (mandatory on every BFS):**

```markdown
**Document ID:** ELU-BFS-{MODULE}
**Module:** {MODULE-ID} — {Module Name}
**Sub Module:** {SUB-ID} — {Sub Module Name}
**Feature:** {FEATURE-ID} — {Feature Name}
**Domain:** {DOMAIN}
**Priority / Phase / Release:** ...
**Example Tenant:** Euphoria
```

---

### Section 2 — Business Actors

List **every** user role with:

| Column | Description |
|--------|-------------|
| Actor | Role name |
| Type | Internal / External / System |
| Primary actions | What they do in this module |
| Secondary actions | View / approve / notify only |

Standard actor catalogue (extend per module as needed):

- Platform Admin  
- Tenant Admin  
- Sales Executive  
- Sales Manager  
- Pre-Sales / Solution Architect  
- Finance User  
- Project Manager  
- Team Member  
- Support Agent  
- Customer Contact  
- System (Workflow Engine, Rule Engine, Notification Engine, Scheduler)

---

### Section 3 — Business Story

Write the **complete user-to-user business story**:

- Real enterprise workflow (not marketing copy)  
- Every handoff between actors  
- CRM/ERP object names at each step  
- Exception paths (reject, expire, suspend, reopen)  
- Link to WF IDs where known  

Minimum length guidance: enough for a developer to understand lifecycle without verbal briefing.

---

### Section 4 — Business Workflow

Provide:

1. Linear ASCII / Mermaid flow (mandatory)  
2. Step table: Step No | Actor | Action | Input Object | Output Object | Engine used  

Example spine (platform-wide — modules use the relevant slice):

```text
Lead → Qualification → Opportunity → Quotation → Proposal → Approval
→ Sales Order → Work Order → Project → Milestone → Invoice → Payment → Closure
```

---

### Section 5 — Business States

Define **all** lifecycle states for the primary document/object.

| Column | Required |
|--------|----------|
| State Code | MACHINE_NAME |
| State Label | UI label |
| Description | Meaning |
| Allowed Next States | Transitions |
| Entry Actors | Who can move into this state |
| System Effects | Locks, notifications, feature gates |

Baseline state vocabulary (customise per module):

`Draft`, `Submitted`, `Under Review`, `Approved`, `Rejected`, `Active`, `On Hold`, `Cancelled`, `Completed`, `Closed`, `Archived`, `Expired`, `Suspended`

---

### Section 6 — Business Rules

Number every rule:

`BR-{DOMAIN}-{nnn}`

Each rule must state:

| Field | Content |
|-------|---------|
| Rule ID | BR-… |
| Statement | Precise normative rule (“shall / must”) |
| Type | Validation / Approval / Security / Calculation / Lifecycle |
| Severity | Error / Warning / Info |
| Enforcement | UI / API / DB / Workflow / Rule Engine |

Include validations **and** approval thresholds.

---

### Section 7 — Database Impact

List **all** required tables (masters + transactions + links + audit).

| Column | Content |
|--------|---------|
| Table Name | snake_case |
| Type | Master / Transaction / Link / Lookup / Audit |
| Purpose | One sentence |
| Tenant Scoped | Yes / No (almost always Yes) |

Do **not** invent physical column lists here — that belongs to Field Dictionary. Logical groups are in §9.

---

### Section 8 — Relationships

Document parent–child and cross-module FKs:

| Parent | Child | Cardinality | On Delete Policy | Notes |
|--------|-------|-------------|------------------|-------|
| customer | opportunity | 1:N | Restrict | … |

Include polymorphic links (e.g. Activity → Lead/Opportunity/Customer) explicitly.

---

### Section 9 — Field Groups

For **each table**, list **logical field groups only** (no physical fields yet):

Examples: General Information, Address, Commercial Information, Tax, Status, Assignment, Attachments, Audit.

This section feeds the Field Dictionary authoring workshop.

---

### Section 10 — REST APIs

List required endpoints:

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | /api/v1/... | Create | … |
| GET | … | Get by id / list | … |
| PUT | … | Full update | … |
| PATCH | … | Partial / status | … |
| DELETE | … | Soft delete / archive | … |
| GET | …/search | Search | … |
| GET | …/export | Export | … |

Standards:

- Prefix: `/api/v1/`  
- Auth: Bearer JWT (+ refresh token flow outside resource APIs)  
- Always enforce `tenant_id` server-side  
- Soft delete preferred over hard delete  

---

### Section 11 — Flutter Screens

Enumerate screens:

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| … List | List | … | Filters, sort, paging |
| … Create | Create | … | |
| … Edit | Edit | … | |
| … View / Detail | View | … | |
| … Search | Search | … | Advanced |
| … Approval | Approval | … | Inbox / action |
| … History | History | … | Audit / versions |

Web + Android share the same information architecture unless explicitly noted.

---

### Section 12 — RBAC Permissions

List every permission code:

`{resource}.{action}`

Standard actions: `create`, `read`, `update`, `delete`, `submit`, `approve`, `reject`, `assign`, `convert`, `export`, `import`, `print`, `cancel`, `restore`, `configure`

Map permissions to roles in a matrix (Actor × Permission).

---

### Section 13 — Notifications

For each event:

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| … | Email / SMS / WhatsApp / Push / Internal | … | NTF-… |

Channels are **capability targets**; Phase may gate SMS/WhatsApp/Push.

---

### Section 14 — Reports

Classify:

- Operational Reports  
- Management Reports  
- Executive Dashboard  
- KPIs  

Each report: Report ID, Name, Audience, Grain, Filters, Export formats.

---

### Section 15 — Audit Requirements

List auditable events (create, update, status change, approve, reject, assign, convert, soft delete, restore, login-related if identity module, export, permission change).

State retention reference: tenant security / compliance policy.

---

### Section 16 — Acceptance Criteria

Numbered, testable criteria (Given/When/Then or checklist). Module is **not Done** until all pass in UAT for tenant Euphoria scenarios.

---

### Section 17 — Future Enhancements

| Version | Ideas |
|---------|-------|
| v2.0 | … |
| v3.0 | … |

---

## 3. Downstream Artefact Templates (Summary)

### 3.1 Data Dictionary (`ELU-DDD-*`)

Per field: Name, Data Type, Length/Precision, Required, Default, PK/FK/UK/IDX, Description, Validation, UI Control, Remarks.

### 3.2 ERD Pack (`ELU-ERD-*`)

Logical ERD + Physical ERD; crow’s foot; tenant_id noted on all tenant tables.

### 3.3 API Spec (`ELU-API-*`)

OpenAPI 3.x; request/response schemas; error codes; pagination; idempotency keys where needed.

### 3.4 Screen Spec (`ELU-UI-*`)

Screen ID, route, widgets, validations, empty/error states, offline notes (Android), RBAC hide/disable rules.

### 3.5 Workflow Pack (`ELU-WF-*`)

States, transitions, guards, approver resolution, SLA timers, escalation.

### 3.6 Test Specification (`ELU-TST-*`)

Map each `REQ-*`, `BR-*`, and Acceptance Criterion to `TC-*`; include negative and multi-tenant isolation tests.

---

## 4. Cross-Cutting Standards (Apply to Every BFS)

### 4.1 Multi-Tenancy

- Every business table includes `tenant_id` (UUID, FK, indexed) unless explicitly platform-global (e.g. `edition`).  
- APIs never trust client `tenant_id` over JWT claim.  
- Isolation tests are mandatory Acceptance Criteria for every module.

### 4.2 Soft Delete & Versioning

- `is_deleted`, `is_active`, `version_no`, `created_by/on`, `modified_by/on` pattern unless justified otherwise.

### 4.3 Shared Engines

BFS must declare usage of:

| Engine | Module Code |
|--------|-------------|
| Workflow Engine | CPS-001 |
| Rule Engine | CPS-002 |
| Notification Engine | CPS-003 |
| Reporting & Analytics | CPS-004 |
| Audit Service | CPS-005 / PF-010 |
| Document Management | CPS-006 |
| AI Assistant | CPS-007 (optional) |
| Integration Framework | CPS-008 / INT-* |

### 4.4 Edition Gating

BFS must state minimum Edition (Community / Professional / Enterprise) per Feature ID from ELU-BRD-001.

### 4.5 Authentication

All APIs except health/public auth endpoints require JWT access token; refresh token rotation per security design in ELU-SAD-001.

---

## 5. Module Catalogue Covered by BFS Packs

| Domain | Modules | BFS Pack Location |
|--------|---------|-------------------|
| PF | PF-001 … PF-011 | `01-BFS-Platform-Foundation/` |
| CRM | CRM-001 … CRM-004 | `02-BFS-CRM/` |
| SAL | SAL-001 … SAL-004 | `03-BFS-Sales/` |
| PRJ | PRJ-001 … PRJ-006 | `04-BFS-Projects/` |
| FIN | FIN-001 … FIN-004 | `05-BFS-Finance/` |
| SRV | SRV-001 … SRV-003 | `06-BFS-Service/` |
| INT | INT-001 … INT-004 | `07-BFS-Integration/` |
| CPS | CPS-001 … CPS-008 | `08-BFS-Core-Platform/` |

**Total primary BFS units:** 44 Feature-level specifications (one per BRD Feature row), authored at Module grain with Sub Module/Feature explicit in the header.

---

## 6. Definition of Ready / Done

### 6.1 Definition of Ready (for Development Sprint)

- [ ] BFS §§1–17 complete  
- [ ] Module codes match ELU-BRD-001  
- [ ] Reviewed by BA + Solution Architect + Product Owner  
- [ ] Open questions logged (no silent gaps)  
- [ ] Dependencies on other modules listed  

### 6.2 Definition of Done (for Module Release)

- [ ] Data Dictionary (**ELU-DDD-***) + ERD (**ELU-ERD-***) approved  
- [ ] APIs implemented & contract-tested  
- [ ] Flutter screens match §11  
- [ ] RBAC enforced server-side  
- [ ] Notifications firing for §13 events  
- [ ] Reports available or explicitly deferred with PO sign-off  
- [ ] Audit events verified  
- [ ] Acceptance Criteria §16 passed in UAT  
- [ ] Multi-tenant isolation test passed  

---

## 7. Governance

| Role | Responsibility |
|------|----------------|
| Product Owner | Prioritise modules; accept BFS scope |
| Senior Business Analyst | Author BFS; maintain BR-* catalogue |
| Enterprise Solution Architect | Validate data, API, security, tenancy |
| Tech Lead | Confirm implementability |
| QA Lead | Derive **ELU-TST-*** / `TC-*` from **ELU-RTM-001**, §16 Acceptance Criteria, and `BR-*` |
| PMO | Document control, versioning, SEH compliance |

**Versioning:** Semantic on each BFS (`Major.Minor`). Breaking schema/API changes require Major bump + migration note.

---

## 8. Empty BFS Skeleton (Copy-Paste)

Authors must copy this skeleton for every new module (see packs for filled instances):

```markdown
# ELU-BFS-{MODULE} — {Module Name}
**Document ID:** ELU-BFS-{MODULE}
**Module:** {MODULE-ID} — {Name}
**Sub Module:** {SUB-ID} — {Name}
**Feature:** {FEATURE-ID} — {Name}
**Domain:** {DOMAIN}
**Priority / Phase / Release:** …
**Example Tenant:** Euphoria
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

## 1. Business Objective
### 1.1 Why this module exists
### 1.2 Business value
### 1.3 Business scope
### 1.4 Users involved
### 1.5 Module reference

## 2. Business Actors
(table)

## 3. Business Story
(narrative)

## 4. Business Workflow
(flow + step table)

## 5. Business States
(table)

## 6. Business Rules
(BR-… table)

## 7. Database Impact
(table list)

## 8. Relationships
(relationship table)

## 9. Field Groups
(per table)

## 10. REST APIs
(endpoint table)

## 11. Flutter Screens
(screen table)

## 12. RBAC Permissions
(permission + matrix)

## 13. Notifications
(event table)

## 14. Reports
(report catalogue)

## 15. Audit Requirements
(event list)

## 16. Acceptance Criteria
(checklist)

## 17. Future Enhancements
(v2 / v3)
```

---

## 9. Document Control

| Field | Value |
|-------|-------|
| Status | Approved for authoring |
| Next action | Produce complete BFS packs for all BRD modules under `Documentation/` |
| Owner | PMO |

---

*© Euphoria Infotech (I) Limited — E-LinkUp Enterprise Documentation Framework*
