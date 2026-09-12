# E-LinkUp Product Roadmap
**Document ID:** ELU-RDM-001  
**Document Name:** Product Roadmap  
**Version:** 1.0  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Product Owner / PMO  
**Document Owner:** Product Owner  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-DOC-001, ELU-CHR-001, ELU-BRD-001, ELU-EFS-001, ELU-MSL-001, ELU-ADR-001, ELU-RSK-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP / Product Owner | Initial product roadmap aligned to BRD phases and ELU-EFS-001 |

---

## 1. Purpose

**ELU-RDM-001** defines which **modules and capabilities** ship in each product release of E-LinkUp.

It is the planning companion to:

- **ELU-BRD-001 – Business Requirements Document** (module catalogue)  
- **ELU-EFS-001 – Enterprise Functional Specification** (implementation depth)  
- **ELU-MSL-001 – Milestone Tracker** (delivery progress)  

Catalogue: **ELU-DOC-001 – Documentation Master Index**.

---

## 2. Release Strategy Overview

```text
v1.0  Foundation + Lead-to-Cash Core (Platform, CRM, Sales, Projects, Finance)
  │
  ▼
v1.1  Service Desk + Mature Shared Engines (Workflow, Rules, Notifications, Documents)
  │
  ▼
v2.0  Integration, Enterprise BI, API Gateway, AI Assist (optional)
  │
  ▼
v3.0  Advanced AI, Deep Industry Packs, Marketplace / Ecosystem
```

| Release | Theme | Target Editions | Primary Phase (BRD) |
|---------|-------|-----------------|---------------------|
| **v1.0** | Operate the business end-to-end | Community (subset), Professional, Enterprise | Phase 1 + Phase 2 |
| **v1.1** | Automate & support | Professional, Enterprise | Phase 3 |
| **v2.0** | Connect & analyse | Enterprise (full), Professional (partial) | Phase 4 |
| **v3.0** | Intelligence & ecosystem | Enterprise-first | Post Phase 4 |

---

## 3. Release v1.0 — Foundation & Lead-to-Cash

**Objective:** Deliver a commercially usable multi-tenant CRM/ERP spine for tenant **Euphoria**: onboard → sell → deliver → invoice → collect.

### 3.1 Modules in v1.0

| Domain | Module ID | Module | Priority | Notes |
|--------|-----------|--------|----------|-------|
| PF | PF-001 | Edition Management | High | Community / Professional / Enterprise matrix |
| PF | PF-002 | Tenant Management | Critical | Tenant isolation root |
| PF | PF-003 | Subscription Management | High | Trial / Active / Suspended / Expired |
| PF | PF-004 | Organization Management | Critical | Org hierarchy |
| PF | PF-005 | Branch Management | High | **IMPLEMENTED — NOT RELEASED** (backend functional layer; start authorisation 2026-09-12, Avijit / Project Coordinator); no release approval, no tag; AC-PF-005-04 deferred to PF-008; NTF/RPT deferred; Flutter UI (Batch 3) outstanding |
| PF | PF-006 | Department Management | High | |
| PF | PF-007 | Business Unit Management | Medium | |
| PF | PF-008 | User & Identity Management | Critical | JWT + Refresh (**ADR-004**) |
| PF | PF-009 | Roles & Permissions (RBAC) | Critical | |
| PF | PF-010 | Audit & Compliance | High | Baseline audit |
| PF | PF-011 | System Configuration | High | Tenant settings / localisation / branding |
| CRM | CRM-001 | Lead Management | Critical | |
| CRM | CRM-002 | Opportunity Management | Critical | |
| CRM | CRM-003 | Customer Management | Critical | |
| CRM | CRM-004 | Activity Management | High | |
| SAL | SAL-001 | Quotation Management | Critical | |
| SAL | SAL-002 | Proposal Management | Critical | Versioning |
| SAL | SAL-003 | Sales Order Management | Critical | |
| SAL | SAL-004 | Work Order Management | Critical | |
| PRJ | PRJ-001 | Project Management | Critical | |
| PRJ | PRJ-002 | Milestone Management | High | |
| PRJ | PRJ-003 | Task Management | Critical | |
| PRJ | PRJ-004 | Timesheet Management | High | |
| PRJ | PRJ-005 | Issue Management | Medium | |
| PRJ | PRJ-006 | Change Request Management | High | |
| FIN | FIN-001 | Invoice Management | Critical | |
| FIN | FIN-002 | Payment Management | Critical | |
| FIN | FIN-003 | Vendor Settlement | High | Professional+ (not Enterprise-only) |
| FIN | FIN-004 | Tax Management | High | GST & TDS |

### 3.2 Explicitly Out of v1.0

| Module | Deferred To |
|--------|-------------|
| SRV-001…003 Help Desk / SLA / Knowledge | v1.1 |
| CPS-001…003, CPS-005…006 advanced engines | v1.1 (basic stubs may exist in v1.0) |
| INT-001…004, CPS-004 BI, CPS-007 AI, CPS-008 Integration Framework | v2.0 |

### 3.3 v1.0 Success Criteria

- [ ] Tenant **Euphoria** can complete Lead → Payment path on Flutter Web  
- [ ] Tenant isolation verified (**ADR-001**)  
- [ ] REQ RTM coverage for all v1.0 workflows in **ELU-EFS-001** / **ELU-RTM-001**  
- [ ] Professional edition feature set demonstrable  

---

## 4. Release v1.1 — Automation & Service

**Objective:** Mature shared engines and customer support lifecycle.

### 4.1 Modules in v1.1

| Domain | Module ID | Module | Priority |
|--------|-----------|--------|----------|
| SRV | SRV-001 | Ticket Management | High |
| SRV | SRV-002 | SLA Management | High |
| SRV | SRV-003 | Knowledge Management | Medium |
| CPS | CPS-001 | Workflow Engine (Designer depth) | Critical |
| CPS | CPS-002 | Rule Engine | High |
| CPS | CPS-003 | Notification Engine (multi-channel) | High |
| CPS | CPS-005 | Audit Service (advanced) | High |
| CPS | CPS-006 | Document Management (version control depth) | High |

### 4.2 Platform Enablers (v1.1)

| Capability | Decision / Note |
|------------|-----------------|
| Redis + Celery | **ADR-008** — introduced in this release |
| SMS / WhatsApp / Push channels | Edition-gated; templates from EFS Notification Matrices |
| Workflow Designer UI | Flutter config screens for Tenant Admin |

### 4.3 v1.1 Success Criteria

- [ ] SLA breach escalations automated  
- [ ] Configurable approval workflows without code deploy  
- [ ] Document versioning for Proposal / Invoice attachments  

---

## 5. Release v2.0 — Integration, BI & AI Assist

**Objective:** Enterprise connectivity and insight.

### 5.1 Modules in v2.0

| Domain | Module ID | Module | Priority | Edition Focus |
|--------|-----------|--------|----------|---------------|
| INT | INT-001 | REST API Management | High | Enterprise |
| INT | INT-002 | Webhook Management | High | Enterprise |
| INT | INT-003 | OAuth Management | Medium | Enterprise |
| INT | INT-004 | Connector Management | Medium | Enterprise |
| CPS | CPS-004 | Reporting & Analytics / Enterprise BI | High | Professional+ / Enterprise BI |
| CPS | CPS-007 | AI Assistant (recommendations) | Low→Medium | Enterprise / Optional Professional |
| CPS | CPS-008 | Integration Framework | Medium | Enterprise |
| PF | PF-008+ | SSO / MFA hardening | High | Enterprise (**ADR-004**) |

### 5.2 v2.0 Success Criteria

- [ ] External system can create Lead / read Invoice via secured API consumer  
- [ ] Executive dashboards for pipeline, project health, receivables  
- [ ] Optional AI next-best-action on Lead / Opportunity (non-blocking)  

---

## 6. Release v3.0 — Intelligence & Ecosystem

**Objective:** Differentiated AI depth, industry packs, and partner ecosystem.

### 6.1 Candidate Themes (v3.0)

| Theme | Candidate Capabilities | Source |
|-------|------------------------|--------|
| Advanced AI | Predictive lead score, win probability, forecast assist | EFS Future Enhancements / CPS-007 |
| Customer portal | Self-service tickets, invoice view | CRM / SRV futures |
| Industry packs | EPC, IT Services, Govt contractor templates | Product strategy |
| Marketplace | Certified connectors, partner apps | INT-004 / CPS-008 |
| Mobile iOS | Flutter iOS client | Future ADR (extends **ADR-003**) |
| Physical tenancy option | DB-per-tenant for regulated buyers | Revisit **ADR-001** |

### 6.2 v3.0 Governance

Themes in §6.1 are **directional**. Each enters delivery only after:

1. Product Owner prioritisation  
2. New/updated **REQ-*** in **ELU-EFS-001** / BFS  
3. Decision recorded in **ELU-ADR-001** if architectural  

---

## 7. Module × Release Matrix (Summary)

| Module Family | v1.0 | v1.1 | v2.0 | v3.0 |
|---------------|:----:|:----:|:----:|:----:|
| PF-001…011 Platform Foundation | ● | ◐ | ◐ | ◐ |
| CRM-001…004 | ● | ◐ | ◐ | ◐ |
| SAL-001…004 | ● | ◐ | ◐ | ◐ |
| PRJ-001…006 | ● | ◐ | ◐ | ◐ |
| FIN-001…004 | ● | ◐ | ◐ | ◐ |
| SRV-001…003 | | ● | ◐ | ◐ |
| CPS Workflow/Rule/Notify/Audit/Doc | ◐ stub | ● | ◐ | ◐ |
| CPS Reporting / AI / Integration FW | | | ● | ◐ |
| INT-001…004 | | | ● | ◐ |
| Industry / Portal / iOS / Marketplace | | | | ● |

● Full release target ◐ Enhance / harden

---

## 8. Dependency Notes

| Dependency | Constraint |
|------------|------------|
| Documentation | v1.0 build uses **ELU-EFS-001** + **ELU-BFS-*** + **ELU-RTM-001** |
| Data | **ELU-DDD-*** / **ELU-ERD-*** required before schema freeze |
| API / UI | **ELU-API-*** / **ELU-UI-*** per domain sprint |
| Risks | Track blockers in **ELU-RSK-001** |
| Progress | Track delivery in **ELU-MSL-001** |

---

## 9. Roadmap Change Control

| Change Type | Approval |
|-------------|----------|
| Move module between v1.0 ↔ v1.1 | Product Owner + Solution Architecture |
| Slip v1.0 Critical module | Product Owner + PMO; update **ELU-MSL-001** + **ELU-RSK-001** |
| New v3.0 theme | Product Owner; optional ADR |

---

*© Euphoria Infotech (I) Limited — ELU-RDM-001 Product Roadmap*
