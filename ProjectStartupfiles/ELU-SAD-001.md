# E-LinkUp Software Architecture Document (SAD)
**Document ID:** ELU-SAD-001  
**Document Name:** Software Architecture Document  
**Version:** 1.0  
**Status:** In Review  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Euphoria Infotech (I) Limited  
**Document Owner:** Solution Architecture / PMO  
**Example Tenant:** Euphoria  
**Tagline:** *"Connecting Business. Streamlining Growth."*  
**Related Documents:** ELU-DOC-001, ELU-CHR-001, ELU-HLD-001, ELU-BRD-001, ELU-STORY-001, ELU-EFS-001, ELU-DF-001, ELU-ADR-001

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-30 | EIIP | Initial Software Architecture Document
| 1.0a | 2026-07-31 | EIIP / PMO | Status In Review; Version History; Related Documents aligned to ELU-DOC-001 |

> Catalogue entry: **ELU-DOC-001 – Documentation Master Index**. Cross-references must cite Document IDs (see **ELU-DF-001 – Documentation Framework**).

## 1. Introduction

### 1.1 Purpose

This Software Architecture Document (SAD) describes the **system architecture** of E-LinkUp: a secure, scalable, cloud-native, multi-tenant SaaS platform that unifies CRM, Sales, Projects, Finance, Service, Workflow Automation, and Business Intelligence.

It translates **ELU-CHR-001 – Project Charter**, **ELU-HLD-001 – Platform Blueprint**, **ELU-STORY-001 – CRM Business Story**, and **ELU-EFS-001 – Enterprise Functional Specification** into an implementable technical architecture for tenant **Euphoria** and all future tenants.

### 1.2 Scope

| In Scope | Out of Scope |
|----------|--------------|
| Logical & physical architecture | Detailed UI pixel specs |
| Multi-tenant data model principles | Full OpenAPI YAML (separate API pack) |
| Layered services & shared engines | Infrastructure as Code templates |
| Security, RBAC, audit architecture | Vendor contract negotiations |
| Technology stack & deployment topology | AI model training pipelines |
| Edition / feature gating | Mobile store publishing process |
| Traceability to BRD modules | |

### 1.3 Audience

- Solution Architects & Tech Leads  
- Backend (FastAPI) & Frontend (Flutter) engineers  
- DevOps / Cloud engineers  
- Security & Compliance reviewers  
- PMO and Product Owners  

### 1.4 Definitions

| Term | Definition |
|------|------------|
| **Tenant** | Isolated customer organisation (e.g. Euphoria) on the shared platform |
| **CRM User** | Authenticated user acting under RBAC (Sales Executive, PM, etc.) |
| **CRM Object** | Domain entity: Lead, Contact, Customer, Opportunity, Activity, etc. |
| **Edition** | Community / Professional / Enterprise feature pack |
| **Shared Engine** | Cross-module platform capability (Workflow, Rule, Notification, …) |

---

## 2. Architectural Goals & Constraints

### 2.1 Goals

| ID | Goal | Rationale |
|----|------|-----------|
| AG-01 | Complete lead-to-cash lifecycle in one platform | Eliminate spreadsheet fragmentation |
| AG-02 | Strong multi-tenant isolation | SaaS safety for Euphoria and peers |
| AG-03 | Configurable workflows & rules | Industry/tenant variation without forks |
| AG-04 | Enterprise security & auditability | Governance for IT services, govt, EPC |
| AG-05 | Single UI family (Flutter Web + Android) | Consistent CRM user experience |
| AG-06 | Edition-based product packaging | Community → Professional → Enterprise |
| AG-07 | Extensibility via API / webhooks | Phase 4 integrations |

### 2.2 Constraints

| ID | Constraint |
|----|------------|
| AC-01 | Backend: Python FastAPI |
| AC-02 | Database: PostgreSQL (tenant-aware) |
| AC-03 | ORM: SQLAlchemy |
| AC-04 | Auth: JWT (Argon2id password hashing); Enterprise adds SSO/MFA |
| AC-05 | Storage: MinIO for documents |
| AC-06 | Containers: Docker; reverse proxy Nginx |
| AC-07 | CI/CD: GitHub Actions; Hosting Azure / Linux VPS |
| AC-08 | Redis + Celery from Phase 3 for cache/queues |

### 2.3 Quality Attributes

| Attribute | Target Approach |
|-----------|-----------------|
| Security | JWT, RBAC, tenant filters, encryption flags, audit |
| Scalability | Stateless API nodes; DB indexing by tenant_id; later Redis/Celery |
| Availability | Containerised services behind Nginx; health checks |
| Maintainability | Domain modules + shared engines; clear BRD IDs |
| Observability | Audit service + structured logs + MIS dashboards |
| Portability | Docker images runnable on Azure or VPS |

---

## 3. System Context

### 3.1 Context Diagram

```text
                    ┌─────────────────────────┐
                    │   CRM Users (Euphoria)  │
                    │ Sales Exec, Mgr, PM,    │
                    │ Finance, Support, Admin │
                    └───────────┬─────────────┘
                                │ Flutter Web / Android
                                ▼
┌──────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│ Customer     │─────►│      E-LinkUp        │◄─────│ Platform Admin    │
│ Contact      │ email│  Multi-Tenant SaaS   │      │ (Euphoria Infotech│
│ (external)   │/portal│                     │      │  operators)       │
└──────────────┘      └──────────┬──────────┘      └──────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
        MinIO Storage     PostgreSQL DB      Ext. Systems
        (Documents)       (Tenant data)      (API/Webhooks P4)
```

### 3.2 Product Positioning

E-LinkUp is an **Enterprise Business Operations Platform**, not CRM-only:

- Customer Relationship Management  
- Sales & Quotation Management  
- Project Lifecycle Management  
- Finance & Billing  
- Help Desk  
- Workflow Automation  
- Business Intelligence  
- AI-Assisted Operations (Phase 4)  

---

## 4. Logical Architecture

### 4.1 Layered View

```text
┌────────────────────────────────────────────────────────────┐
│ Presentation Layer                                         │
│  Flutter Web  │  Flutter Android                           │
└───────────────────────────┬────────────────────────────────┘
                            │ HTTPS / REST (JWT)
┌───────────────────────────▼────────────────────────────────┐
│ Edge Layer                                                 │
│  Nginx Reverse Proxy  │  API Gateway (Enterprise)          │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│ Application Layer (FastAPI)                                │
│ ┌─────────────┐ ┌────────────────────────────────────────┐ │
│ │ Auth        │ │ Business Services                      │ │
│ │ Tenant Mgmt │ │ CRM │ Sales │ Projects │ Finance │ SRV │ │
│ │ Org / RBAC  │ │                                            │
│ └─────────────┘ └────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Shared Enterprise Services                             │ │
│ │ Workflow │ Rule │ Approval │ Notification │ Document   │ │
│ │ Reporting │ Audit │ Integration Framework              │ │
│ └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│ Data & Infrastructure                                      │
│ PostgreSQL │ MinIO │ Redis* │ Celery* │ Docker │ Azure/VPS │
└────────────────────────────────────────────────────────────┘
  * Phase 3+
```

### 4.2 Domain Module Map (BRD Traceability)

| Domain | Module IDs | Architecture Service |
|--------|------------|----------------------|
| Platform Foundation (PF) | PF-001…011 | Tenant, Edition, Subscription, Org, User, RBAC, Audit, Config |
| CRM | CRM-001…004 | CRM Engine — Lead, Opportunity, Customer, Activity |
| Sales (SAL) | SAL-001…004 | Sales Engine — Quotation, Proposal, Sales Order, Work Order |
| Projects (PRJ) | PRJ-001…006 | Project Engine — Project, Milestone, Task, Timesheet, Issue, CR |
| Finance (FIN) | FIN-001…004 | Finance Engine — Invoice, Payment, Settlement, Tax |
| Service (SRV) | SRV-001…003 | Help Desk — Ticket, SLA, Knowledge |
| Integration (INT) | INT-001…004 | REST, Webhooks, OAuth, Connectors |
| Core Platform (CPS) | CPS-001…008 | Shared engines + AI + Integration Framework |

### 4.3 Dynamic Configuration Model

Runtime behaviour for Euphoria (and every tenant) is driven by:

```text
Tenant
  → Workflow Definition
  → State Definitions
  → Approval Rules
  → Business Rules
  → Notifications
  → Permissions
  → Forms
```

This keeps CRM user journeys configurable without code forks.

---

## 5. Multi-Tenancy Architecture

### 5.1 Isolation Model

| Aspect | Design |
|--------|--------|
| Strategy | Shared application + shared DB schema with **mandatory `tenant_id`** on business tables |
| Enforcement | Middleware / repository filters; never trust client-supplied tenant alone |
| Admin boundary | Platform Admin operates cross-tenant; Tenant Admin only within Euphoria |
| Soft delete | Logical delete flags; no orphan hard deletes when transactions exist |

### 5.2 Tenant Bootstrap (Architecture)

Aligned with WF-PF-001:

1. Create Tenant + Edition + Subscription  
2. Seed Organization (HO)  
3. Create Tenant Admin User + Admin Role  
4. Seed Settings, Security, Localisation, Branding  
5. Activate → JWT-authenticated CRM users may operate  

### 5.3 Edition Feature Gating

| Layer | Community | Professional | Enterprise |
|-------|-----------|--------------|------------|
| Auth | ✓ | ✓ | ✓ + SSO/MFA |
| CRM | ✓ | ✓ | ✓ |
| Sales | Basic | ✓ | ✓ |
| Projects | — | ✓ | ✓ |
| Finance | — | ✓ | ✓ |
| Help Desk | — | ✓ | ✓ |
| Workflow Engine | — | Limited | ✓ |
| Rule Engine | — | Basic | ✓ |
| Documents | Basic | ✓ | ✓ |
| Reports | Basic | Advanced | Enterprise BI |
| Audit | Basic | Standard | Advanced |
| AI Services | — | Optional | ✓ |
| API Gateway | — | — | ✓ |
| Integrations | — | Basic | Enterprise |
| Multi-tenancy | Single Tenant | Optional | Full SaaS |

Feature flags resolve at login / module load from Edition + Subscription status.

---

## 6. Security Architecture

### 6.1 Authentication

```text
User Login (email/password)
  → Verify password_hash (Argon2id)
  → Check account_status / tenant status / subscription
  → Issue JWT access (+ refresh policy)
  → Optional MFA / SSO (Enterprise)
```

### 6.2 Authorisation (RBAC)

```text
JWT → user_id + tenant_id + role_id
  → Permission set (e.g. lead.create, opportunity.update, invoice.approve)
  → Resource check (object.tenant_id == token.tenant_id)
  → Allow / Deny + Audit
```

Illustrative CRM permissions: `lead.*`, `opportunity.*`, `customer.*`, `quotation.approve`, `project.manage`, `invoice.issue`, `ticket.assign`, `tenant.suspend` (platform only).

### 6.3 Tenant Security Profile

Stored in `tenant_security` (see BRD PF-002): password policy, expiry, MFA, session timeout, max login attempts, lock duration, IP whitelist flag, audit retention, encryption flag.

### 6.4 Data Protection

- Passwords: hash only (never plaintext)  
- Transport: TLS terminated at Nginx  
- At rest: storage/DB encryption per deployment policy  
- Documents: MinIO with tenant-prefixed object keys + RBAC on links  

---

## 7. Data Architecture

### 7.1 Core Platform Tables (Foundation)

| Table ID | Name | Role |
|----------|------|------|
| TBL-PF-001 | tenant | Tenant master |
| TBL-PF-002 | tenant_contact | Contacts |
| TBL-PF-003 | tenant_address | Addresses |
| TBL-PF-004 | tenant_branding | UI branding |
| TBL-PF-005 | tenant_settings | Business prefs |
| TBL-PF-006 | tenant_security | Security policy |
| TBL-PF-007 | tenant_localization | Locale / formats |
| TBL-PF-008 | organization | Org hierarchy |
| TBL-PF-009 | edition | Product editions |
| TBL-PF-010 | subscription | Licence lifecycle |
| TBL-PF-011 | users | CRM users |

Common columns pattern: `is_active`, `is_deleted`, `version_no`, `created_by/on`, `modified_by/on`.

### 7.2 CRM Object Model (Logical)

```text
Tenant (Euphoria)
 └── Customer (Account)
      ├── Contact
      ├── Lead ──────────────► Opportunity
      │                              │
      │                              ├── Quotation / Proposal
      │                              ├── Sales Order
      │                              │       └── Work Order
      │                              │              └── Project
      │                              │                    ├── Milestone / Task
      │                              │                    ├── Timesheet / Issue / CR
      │                              │                    └── Invoice ← Payment
      ├── Activity (polymorphic link to Lead/Opp/Customer/Project/Ticket)
      └── Ticket ← SLA / Knowledge
```

### 7.3 Cross-Cutting Data Rules

| Rule | Implementation |
|------|----------------|
| Tenant isolation | `tenant_id` NOT NULL + index + query filter |
| Optimistic locking | `version_no` on updates |
| Soft delete | `is_deleted`; unique constraints consider active rows |
| Audit | Append-only audit / tenant_audit style records |
| Referential integrity | FK restrict on delete when children exist |

---

## 8. Application Architecture

### 8.1 Service Decomposition

| Service | Responsibility | Tech Mapping |
|---------|----------------|--------------|
| Authentication Engine | Login, JWT, password, MFA hooks | FastAPI + JWT + Argon2id |
| SaaS / Tenant Engine | Tenant lifecycle, edition, subscription | FastAPI + PostgreSQL |
| Organization Service | Org tree, branches, departments, BUs | FastAPI |
| CRM Engine | Lead, Opportunity, Customer, Activity | FastAPI |
| Sales Engine | Quotation, Proposal, SO, WO | FastAPI |
| Project Engine | Project delivery objects | FastAPI |
| Finance Engine | Invoice, Payment, Settlement, Tax | FastAPI |
| Help Desk Service | Ticket, SLA, Knowledge | FastAPI |
| Workflow Engine | Designer, instances, approvals | FastAPI + PostgreSQL |
| Rule Engine | Configurable business rules | Python rules |
| Notification Service | Multi-channel alerts | Celery + Redis (P3) |
| Document Service | Versioned files | MinIO |
| Analytics Service | Dashboards / MIS | PostgreSQL + BI |
| Audit Service | System & business audit | PostgreSQL |
| Integration Framework | REST/Webhook/OAuth/Connectors | FastAPI Gateway |

### 8.2 API Style

- Versioned REST: `/api/v1/...`  
- Example platform: `/api/v1/platform/tenants`  
- CRM pattern (illustrative): `/api/v1/crm/leads`, `/opportunities`, `/customers`, `/activities`  
- Sales / Projects / Finance under `/api/v1/sales|projects|finance/...`  
- Idempotent where needed for payments and workflow actions  
- Problem+JSON or consistent error envelope  

### 8.3 Workflow Runtime

```text
Business Event (e.g. Quotation Submitted)
  → Workflow Engine loads definition for tenant+object
  → Evaluate Rule Engine (amount matrix, role)
  → Create approval tasks for Sales Manager / Finance User
  → Notification Service alerts assignees
  → On decision → transition CRM object state
  → Audit Service records actor + decision
```

### 8.4 UI Architecture

| Surface | Users | Notes |
|---------|-------|-------|
| Flutter Web | Primary CRM desktop users | Module shells gated by edition + RBAC |
| Flutter Android | Field / mobile CRM users | Same API contract |
| Tenant Branding | Colors, logo, theme | From `tenant_branding` |

Initial platform screens (Tenant Admin / Platform Admin): Tenant List, Create Tenant, Profile, Branding, Settings, Subscription, Security, Localization, Audit History.

---

## 9. Deployment Architecture

### 9.1 Runtime Topology

```text
Internet
   │
   ▼
Nginx (TLS, reverse proxy, static)
   │
   ▼
FastAPI App Containers (N replicas)
   │
   ├── PostgreSQL (primary; replicas optional later)
   ├── MinIO (document buckets)
   ├── Redis + Celery workers (Phase 3+)
   └── Observability (logs/metrics — deployment choice)
```

### 9.2 Environments (Recommended)

| Environment | Purpose |
|-------------|---------|
| Dev | Feature development |
| Test / QA | Workflow & RBAC acceptance |
| UAT | Euphoria stakeholder validation |
| Prod | Live multi-tenant SaaS |

### 9.3 CI/CD

GitHub Actions → build Docker images → run tests → deploy to Azure / Linux VPS.

---

## 10. Cross-Cutting Concerns

### 10.1 Logging & Audit

- Application logs: request id, tenant_id, user_id, route, latency  
- Business audit: CRM object lifecycle and approvals (PF-010 / CPS-005)  

### 10.2 Notifications

Events: Tenant Created/Activated/Suspended, Trial Expiring, Lead Assigned, Approval Pending, Invoice Issued, Payment Overdue, SLA Breach, Ticket Updates.

### 10.3 Reporting

Active Tenants, Pipeline by Stage, Project Health, Invoice Ageing, SLA Attainment, Edition Distribution — served by Analytics Service; Enterprise BI in Phase 4.

### 10.4 Integration (Phase 4)

| Capability | Use |
|------------|-----|
| REST API Management | Inbound/outbound business APIs |
| Webhooks | Event push to subscriber URLs |
| OAuth | Third-party delegated auth |
| Connectors | Packaged ERP/email/accounting links |

---

## 11. Architecture Decision Records (Summary)

Authoritative decision records (Decision ID, Date, Reason, Alternatives, Final Decision, Impact) are maintained in:

> **ELU-ADR-001 – Architecture Decision Log**

| ADR | Decision | Status | Detail |
|-----|----------|--------|--------|
| ADR-001 | Shared DB + `tenant_id` isolation (not DB-per-tenant in v1) | Accepted | ELU-ADR-001 |
| ADR-002 | FastAPI + PostgreSQL + SQLAlchemy core stack | Accepted | ELU-ADR-001 |
| ADR-003 | Flutter for Web and Android clients | Accepted | ELU-ADR-001 |
| ADR-004 | JWT auth; SSO/MFA Enterprise-only | Accepted | ELU-ADR-001 |
| ADR-005 | MinIO for documents (not DB BLOBs) | Accepted | ELU-ADR-001 |
| ADR-006 | Soft delete + version_no optimistic locking | Accepted | ELU-ADR-001 |
| ADR-007 | Shared engines preferred over per-module duplicates | Accepted | ELU-ADR-001 |
| ADR-008 | Redis/Celery deferred to Phase 3 | Accepted | ELU-ADR-001 |
| ADR-009 | Edition matrix drives module visibility | Accepted | ELU-ADR-001 |
| ADR-010 | REQ-* as project-wide traceability anchor | Accepted | ELU-ADR-001 |
| ADR-011 | EFS as implementation source of truth for workflows | Accepted | ELU-ADR-001 |
| ADR-012 | Document numbering & status governance | Accepted | ELU-ADR-001 |
| ADR-013 | Community / Professional / Enterprise packaging | Accepted | ELU-ADR-001 |
| ADR-014 | Docker + Azure / Linux VPS hosting model | Accepted | ELU-ADR-001 |

---

## 12. Phased Architecture Delivery

| Phase | Release | Architecture Focus |
|-------|---------|-------------------|
| **Phase 1** | v1.0 | Auth, Tenant, Org, Users, RBAC, Config, Audit, Editions |
| **Phase 2** | v1.0 | CRM, Sales, Projects, Finance engines + Flutter modules |
| **Phase 3** | v1.5 | Workflow/Rule/Notification/Document maturity; Help Desk; Redis/Celery |
| **Phase 4** | v2.0 | API Gateway, Integrations, Enterprise BI, AI Assistant |

---

## 13. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missed tenant filter | Data leak | Central repository base + automated tests |
| Workflow complexity explosion | Delivery delay | Start with reusable approval pattern; tenant templates |
| Large document store growth | Cost / perf | MinIO lifecycle policies; size quotas per edition |
| Monolith growth | Velocity | Keep clear module packages; extract workers in P3 |
| Edition misconfiguration | Wrong feature access | Server-side feature gate, not UI-only hiding |

---

## 14. Traceability

| Architecture Concern | Story | Workflow | BRD |
|----------------------|-------|----------|-----|
| Tenant isolation & bootstrap | Act I | WF-PF-001…003 | PF-001…011 |
| Lead → Opportunity user flow | Act II | WF-CRM-001…004 | CRM-001…004 |
| Quote → Order → WO | Act II | WF-SAL-001…003 | SAL-001…004 |
| Project delivery | Act III | WF-PRJ-001…003 | PRJ-001…006 |
| Invoice → Payment | Act IV | WF-FIN-001…002 | FIN-001…004 |
| Ticket / SLA | Act V | WF-SRV-001 | SRV-001…003 |
| Shared engines | §9 Story | §9 WF | CPS-001…008 |
| Integrations | Act V / future | WF-INT-* | INT-001…004 |

---

## 15. Document Control

| Field | Value |
|-------|-------|
| Status | Draft v1.0 |
| Example Tenant | Euphoria |
| Review Cycle | Architecture Review Board + PMO |
| Next Artifacts | API Specification Pack, ERD Pack, Flutter Screen Inventory, Threat Model |

---

*© Euphoria Infotech (I) Limited — E-LinkUp Internal Documentation*
