# E-LinkUp Workflow Documentation
**Document ID:** ELU-WF-001  
**Document Name:** Detailed Business Workflow Documentation (User-to-User)  
**Version:** 1.1  
**Status:** Deprecated  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Euphoria Infotech (I) Limited  
**Document Owner:** Product Management Office (PMO)  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-DOC-001, ELU-EFS-001 (successor for implementation), ELU-STORY-001, ELU-BRD-001, ELU-SAD-001

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-30 | EIIP | Initial workflow documentation
| 1.1 | 2026-07-30 | EIIP | Euphoria tenant; user-to-user actors
| 1.1a | 2026-07-31 | EIIP / PMO | Status set to Deprecated for implementation use; superseded by ELU-EFS-001 |

> Catalogue entry: **ELU-DOC-001 – Documentation Master Index**. Cross-references must cite Document IDs (see **ELU-DF-001 – Documentation Framework**).

## 1. Purpose

This document defines the **end-to-end operational workflows** of E-LinkUp for tenant **Euphoria** — from tenant onboarding through lead-to-cash, project delivery, service, and closure.

Workflows are described **user-to-user** using CRM roles (Sales Executive, Sales Manager, Pre-Sales, Project Manager, Finance User, Support Agent, Customer Contact) and CRM object names (Lead, Contact, Customer, Opportunity, Activity, Quotation, Proposal, Sales Order, Work Order, Project, Invoice, Ticket).

It is the process companion to **ELU-STORY-001 – CRM Business Story**, **ELU-BRD-001 – Business Requirements Document**, and **ELU-SAD-001 – Software Architecture Document**.

> **Implementation note:** For database, API, Flutter, workflow engine, and test design, use **ELU-EFS-001 – Enterprise Functional Specification** (Approved). This document (**ELU-WF-001**) is **Deprecated** for implementation and retained as the base narrative source.

### 1.1 Scope

| In Scope | Out of Scope (this version) |
|----------|-----------------------------|
| Platform Foundation workflows | Detailed screen wireframes |
| CRM Lead → Opportunity → Customer | Low-level API payloads |
| Sales Quotation → Order → Work Order | Database DDL scripts |
| Project execution & change control | Celery job schedules |
| Finance invoice → payment → settlement | Third-party connector mapping |
| Service ticket & SLA flows | AI model training specs |
| Cross-cutting engines (workflow, rules, audit, notifications) | |

### 1.2 Conventions

| Term | Meaning |
|------|---------|
| **Actor** | CRM user role or system service that performs a step |
| **CRM Object** | Named business entity (Lead, Opportunity, Customer, etc.) |
| **Trigger** | Event that starts or advances a workflow |
| **State** | Lifecycle status of a CRM / business record |
| **BR-*** | Business rule identifier |
| **WF-*** | Workflow identifier |
| **Tenant** | Example operating tenant: **Euphoria** |
| **Tenant isolation** | Every transaction must carry and enforce `tenant_id` |

### 1.3 Shared Engine Contract

Every module workflow may invoke:

| Engine | Responsibility |
|--------|----------------|
| Workflow Engine (CPS-001) | State transitions & multi-step approvals |
| Rule Engine (CPS-002) | Configurable validations and routing |
| Notification Engine (CPS-003) | Alerts, reminders, escalations |
| Document Engine (CPS-006) | Attachments & version control |
| Audit Service (CPS-005 / PF-010) | Immutable activity trail |
| Reporting & Analytics (CPS-004) | Operational MIS |

---

## 2. Master Lifecycle Overview

```text
WF-PF-001 Tenant Onboarding
    └─► WF-PF-002 Org & User Setup
            └─► WF-CRM-001 Lead Capture & Qualification
                    └─► WF-CRM-002 Opportunity Pipeline
                            └─► WF-SAL-001 Quotation / Proposal
                                    └─► WF-SAL-002 Negotiation & Sales Order
                                            └─► WF-SAL-003 Work Order Release
                                                    └─► WF-PRJ-001 Project Execution
                                                            └─► WF-PRJ-002 Completion & Acceptance
                                                                    └─► WF-FIN-001 Invoicing & Collections
                                                                            └─► WF-FIN-002 Vendor Settlement
                                                                                    └─► WF-PRJ-003 Project Closure & Renewal
                                                                                            └─► WF-SRV-001 Service & Support (ongoing)
```

---

## 3. Platform Foundation Workflows

### 3.1 WF-PF-001 — Tenant Registration & Activation

| Attribute | Detail |
|-----------|--------|
| **Module** | PF-002 Tenant Management |
| **Feature** | PF-002-001-001 Tenant Registration |
| **Priority** | Critical \| v1.0 \| Phase 1 |
| **Primary Actors** | Platform Admin, System |
| **Secondary Actors** | Notification Engine, Audit Service |

#### 3.1.1 Objective

Establish a fully isolated tenant with edition, subscription, default organisation, administrator, and baseline settings.

#### 3.1.2 Process Flow

```text
[Start]
   │
   ▼
Create Tenant Record
   │
   ▼
Validate Company Information ──fail──► Return validation errors
   │ pass
   ▼
Assign Edition (Community / Professional / Enterprise)
   │
   ▼
Assign Subscription (Trial / Paid plan)
   │
   ▼
Create Default Organization (Head Office)
   │
   ▼
Create Administrator User + Assign Admin Role
   │
   ▼
Initialize Defaults
   • Tenant Settings (FY, currency, timezone)
   • Security Policy
   • Localization
   • Branding placeholders
   │
   ▼
Activate Tenant (status = Active / Trial)
   │
   ▼
Notify Admin (welcome + login)
Audit: Tenant Created / Activated
   │
   ▼
[End]
```

#### 3.1.3 Business Rules

| Rule ID | Rule |
|---------|------|
| BR-PF-001 | Every tenant shall have one unique Tenant Code |
| BR-PF-002 | Tenant Name must be unique within the platform |
| BR-PF-003 | Every tenant must belong to one Edition |
| BR-PF-004 | Every tenant must have one active Subscription |
| BR-PF-005 | Tenant cannot be deleted once transactions exist (soft delete / archive only) |
| BR-PF-006 | Suspended tenants cannot access the system |
| BR-PF-007 | Expired subscriptions automatically restrict licensed features |
| BR-PF-008 | All business data must include the tenant identifier |

#### 3.1.4 States

| State | Description |
|-------|-------------|
| Draft | Record created, not ready |
| Trial | Active trial period |
| Active | Fully licensed and operational |
| Suspended | Access blocked by admin / policy |
| Expired | Subscription ended |
| Closed | Permanently closed / archived |

#### 3.1.5 APIs (Initial)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/platform/tenants` | Create tenant |
| GET | `/api/v1/platform/tenants` | List tenants |
| GET | `/api/v1/platform/tenants/{id}` | Tenant details |
| PUT | `/api/v1/platform/tenants/{id}` | Update tenant |
| PATCH | `/api/v1/platform/tenants/{id}/status` | Change status |
| DELETE | `/api/v1/platform/tenants/{id}` | Archive (logical delete) |

#### 3.1.6 Notifications

- Tenant Created  
- Tenant Activated  
- Trial Expiring  
- Subscription Renewal Reminder  
- Subscription Expired  
- Tenant Suspended  

#### 3.1.7 Acceptance Criteria

- [ ] Tenant code uniqueness enforced  
- [ ] Duplicate tenant name rejected  
- [ ] Default organisation + administrator auto-created  
- [ ] Default settings initialised  
- [ ] Audit records written for lifecycle events  
- [ ] Tenant isolation enforced on all business data  

---

### 3.2 WF-PF-002 — Organisation, Users & RBAC Setup

| Attribute | Detail |
|-----------|--------|
| **Modules** | PF-004 Organization, PF-005 Branch, PF-006 Department, PF-007 Business Unit, PF-008 Users, PF-009 RBAC |
| **Actors** | Tenant Admin, System |

#### 3.2.1 Process Flow

```text
Tenant Activated
   │
   ▼
Define Org Hierarchy
  Head Office → Branch → Department / Business Unit
   │
   ▼
Create Users (invite / register)
   │
   ▼
Assign Roles & Permissions
   │
   ▼
Apply Security Policy (password, MFA, session, lockout)
   │
   ▼
Users Login (JWT auth)
   │
   ▼
[Ready for CRM Operations]
```

#### 3.2.2 Key Rules

- User email unique per tenancy policy  
- Every user belongs to one tenant and one organisation unit  
- Permissions are role-based; no direct module access without RBAC grant  
- Soft delete only for users; historical ownership retained  

---

### 3.3 WF-PF-003 — Subscription Lifecycle

| Attribute | Detail |
|-----------|--------|
| **Module** | PF-003 Subscription Management |
| **Actors** | Platform Admin, Billing System, Rule Engine |

#### States

`Trial → Active → Suspended → Expired → Cancelled` (historical rows retained)

#### Key Transitions

| From | To | Trigger |
|------|----|---------|
| Trial | Active | Payment / conversion |
| Active | Suspended | Non-payment / admin action |
| Active / Trial | Expired | End date reached |
| Any active | Cancelled | Explicit cancellation |

Edition feature matrix (Community / Professional / Enterprise) gates module visibility at runtime.

---

## 4. CRM Workflows

### 4.1 WF-CRM-001 — Lead Capture & Qualification

| Attribute | Detail |
|-----------|--------|
| **Module** | CRM-001 Lead Management |
| **Feature** | CRM-001-001-001 Lead Capture |
| **Priority** | Critical \| Phase 2 |
| **Actors** | Sales Executive, Sales Manager, System |

#### 4.1.1 Objective

Capture every potential enquiry, prevent duplicates, qualify fit, and decide convert / nurture / reject.

#### 4.1.2 Process Flow

```text
[Trigger: Web form / Manual / Import / Referral / Tender]
   │
   ▼
Create Lead
   │
   ▼
Duplicate Check (email / phone / company)
   │
   ├── Duplicate found ──► Link to existing Lead/Customer + alert owner
   │
   └── Unique
         │
         ▼
Assign Owner (manual or rule-based)
         │
         ▼
Log Activities (call / email / meeting) ──► Activity Timeline
         │
         ▼
Qualification (BANT / custom score)
         │
         ├── Unqualified ──► Nurture / Disqualified (reason mandatory)
         │
         └── Qualified
               │
               ▼
Optional NDA Workflow (send → sign → attach)
               │
               ▼
Convert to Opportunity (+ optional Customer Master)
               │
               ▼
[End → WF-CRM-002]
```

#### 4.1.3 Suggested States

| State | Meaning |
|-------|---------|
| New | Just captured |
| Contacted | First outreach done |
| Qualifying | Under evaluation |
| Nurture | Not ready now |
| Qualified | Ready to convert |
| Converted | Opportunity created |
| Disqualified | Closed with reason |
| Duplicate | Merged / linked |

#### 4.1.4 Business Rules (Recommended)

| Rule ID | Rule |
|---------|------|
| BR-CRM-001 | Lead must have tenant_id, source, and owner |
| BR-CRM-002 | Duplicate detection required before save/convert |
| BR-CRM-003 | Disqualification requires reason code |
| BR-CRM-004 | Converted leads are read-only except audit fields |
| BR-CRM-005 | All lead communications logged as Activities |

#### 4.1.5 Permissions (Illustrative)

`lead.create`, `lead.read`, `lead.update`, `lead.convert`, `lead.assign`, `lead.disqualify`

---

### 4.2 WF-CRM-002 — Opportunity Pipeline

| Attribute | Detail |
|-----------|--------|
| **Module** | CRM-002 Opportunity Management |
| **Feature** | CRM-002-001-001 Opportunity Pipeline |
| **Actors** | Sales Executive, Sales Manager, Pre-Sales, Finance |

#### 4.2.1 Pipeline Stages

```text
Qualification
   → Technical Evaluation
   → Budget Validation
   → Proposal / Quotation
   → Negotiation
   → Verbal Commitment
   → Closed Won
   → Closed Lost
```

#### 4.2.2 Process Flow

```text
Lead Converted / Manual Opportunity Create
   │
   ▼
Create Opportunity (value, close date, probability, customer)
   │
   ▼
Technical Evaluation ──fail──► Closed Lost (reason) or back to Qualification
   │ pass
   ▼
Budget Validation ──fail──► Negotiate scope / Closed Lost
   │ pass
   ▼
Trigger Quotation/Proposal (WF-SAL-001)
   │
   ▼
Negotiation (commercial + legal + compliance)
   │
   ├── Lost ──► Closed Lost + competitor/reason
   │
   └── Won
         │
         ▼
Closed Won → Create Sales Order (WF-SAL-002)
```

#### 4.2.3 Business Rules

| Rule ID | Rule |
|---------|------|
| BR-CRM-010 | Opportunity must link to a Customer (or create one on convert) |
| BR-CRM-011 | Stage changes may require manager approval above threshold amount |
| BR-CRM-012 | Closed Lost requires reason and optional competitor |
| BR-CRM-013 | Probability auto-updates by stage (configurable via Rule Engine) |
| BR-CRM-014 | Only one primary open opportunity per lead conversion |

---

### 4.3 WF-CRM-003 — Customer Master Lifecycle

| Attribute | Detail |
|-----------|--------|
| **Module** | CRM-003 Customer Management |
| **Actors** | Sales, Finance, Support |

#### Flow

```text
Prospect created from Lead/Opportunity
   → Enrich profile (contacts, addresses, tax IDs)
   → Mark Active Customer on first Sales Order / Invoice
   → Maintain relationship history (activities, deals, projects, tickets)
   → Optional Inactive / Blacklisted with reason
```

#### Rules

- Customer code unique within tenant  
- GSTIN/PAN validated by format where country = India  
- Soft delete only; financial history retained  

---

### 4.4 WF-CRM-004 — Activity Timeline

| Attribute | Detail |
|-----------|--------|
| **Module** | CRM-004 Activity Management |
| **Actors** | Any authorised user |

#### Flow

```text
Create Activity (Call / Email / Meeting / Task / Note)
   → Link to Lead / Opportunity / Customer / Project / Ticket
   → Set due date & assignee
   → Complete / Reschedule / Cancel
   → Appear on unified timeline & reminders
```

Notifications fire for due/overdue activities via Notification Engine.

---

## 5. Sales Workflows

### 5.1 WF-SAL-001 — Quotation & Proposal

| Attribute | Detail |
|-----------|--------|
| **Modules** | SAL-001 Quotation, SAL-002 Proposal |
| **Actors** | Sales Executive, Pre-Sales, Sales Manager, Approvers |

#### 5.1.1 Process Flow

```text
Opportunity at Proposal stage
   │
   ▼
Create Quotation (line items, tax, validity)
   │
   ▼
Create / Attach Proposal Document (scope + commercials)
   │
   ▼
Internal Approval Workflow
   │
   ├── Rejected ──► Revise (new version) ──► Re-submit
   │
   └── Approved
         │
         ▼
Send to Customer (Document Engine + Notification)
         │
         ▼
Customer Response
   ├── Accept ──► Proceed to Sales Order
   ├── Request Changes ──► New Version + Revision Workflow
   └── Reject ──► Update Opportunity (Closed Lost / re-negotiate)
```

#### 5.1.2 Version Control

| Version Event | Behaviour |
|---------------|-----------|
| Create v1 | Baseline |
| Internal revise | Increment version; previous locked |
| Customer change request | New version; link to parent |
| Approved version | Marked as current commercial baseline |

#### 5.1.3 Business Rules

| Rule ID | Rule |
|---------|------|
| BR-SAL-001 | Quotation must reference Opportunity and Customer |
| BR-SAL-002 | Validity date mandatory; expired quotes cannot convert |
| BR-SAL-003 | Discount above threshold requires manager approval |
| BR-SAL-004 | Tax calculation uses tenant tax configuration (FIN-004) |
| BR-SAL-005 | Only approved quotation version can create Sales Order |

---

### 5.2 WF-SAL-002 — Negotiation, Sales Order & Commercial Approval

| Attribute | Detail |
|-----------|--------|
| **Module** | SAL-003 Sales Order Management |
| **Actors** | Sales Manager, Legal, Finance, Compliance |

#### Process Flow

```text
Approved Quotation Accepted by Customer
   │
   ▼
Credit Validation
   │
   ├── Fail ──► Hold / request advance / escalate
   │
   └── Pass
         │
         ▼
Legal & Compliance Review (contracts, terms)
         │
         ▼
Commercial Approval (Workflow Engine)
         │
         ▼
Create Sales Order (confirmed commitment)
         │
         ▼
Notify Delivery / PMO
         │
         ▼
[Next → WF-SAL-003]
```

#### Sales Order States

`Draft → Pending Approval → Approved → Confirmed → Partially Delivered → Completed → Cancelled`

---

### 5.3 WF-SAL-003 — Work Order Generation

| Attribute | Detail |
|-----------|--------|
| **Module** | SAL-004 Work Order Management |
| **Actors** | Delivery Head, Project Manager, Procurement |

#### Process Flow

```text
Confirmed Sales Order
   │
   ▼
Generate Work Order(s)
   • Scope of execution
   • Resource needs
   • Procurement flags
   │
   ▼
Approve Work Order
   │
   ▼
Allocate Resources / Trigger Procurement
   │
   ▼
Create Project (WF-PRJ-001)
```

#### Rules

| Rule ID | Rule |
|---------|------|
| BR-SAL-020 | Work Order requires approved Sales Order |
| BR-SAL-021 | Multiple Work Orders allowed for phased delivery |
| BR-SAL-022 | Cancellation of Work Order requires reason + audit |

---

## 6. Project Workflows

### 6.1 WF-PRJ-001 — Project Planning & Execution

| Attribute | Detail |
|-----------|--------|
| **Modules** | PRJ-001 to PRJ-005 |
| **Actors** | Project Manager, Team Members, Stakeholders |

#### Process Flow

```text
Approved Work Order
   │
   ▼
Create Project
   • Link Customer, SO, WO
   • Budget, dates, PM
   │
   ▼
Plan
   • Milestones
   • Tasks (WBS)
   • Team assignment
   │
   ▼
Execute
   ├── Task progress updates
   ├── Timesheet entry & approval
   ├── Issue logging & resolution
   └── Risk monitoring
   │
   ▼
Monitor (dashboards / RAG status)
   │
   ▼
[Ready for Completion when milestones done]
```

#### Project States

`Initiating → Planning → In Progress → On Hold → Completed → Closed → Cancelled`

#### Sub-flows

**Timesheets**

```text
User logs time → Submit → Manager approve/reject → Billable flag for Finance
```

**Issues**

```text
Raise Issue → Assign → Investigate → Resolve / Defer → Close → Link to knowledge (optional)
```

---

### 6.2 WF-PRJ-002 — Change Request Control

| Attribute | Detail |
|-----------|--------|
| **Module** | PRJ-006 Change Request Management |
| **Actors** | PM, Customer Sponsor, Sales, Finance |

#### Process Flow

```text
Change Identified (scope / schedule / cost)
   │
   ▼
Raise Change Request
   │
   ▼
Impact Analysis (effort, cost, timeline)
   │
   ▼
Internal Approval
   │
   ▼
Customer Approval (if commercial impact)
   │
   ├── Rejected ──► Close CR (no baseline change)
   │
   └── Approved
         │
         ▼
Update Project Baseline
Optionally revise Sales Order / raise Variation Quotation
         │
         ▼
Audit + Notify stakeholders
```

#### Rules

| Rule ID | Rule |
|---------|------|
| BR-PRJ-001 | No baseline change without approved CR |
| BR-PRJ-002 | Cost-impacting CR requires Finance acknowledgement |
| BR-PRJ-003 | Customer-facing CR requires documented acceptance |

---

### 6.3 WF-PRJ-003 — Completion, Closure & Renewal

#### Completion / Acceptance

```text
All critical milestones Done
   │
   ▼
QA Checklist
   │
   ▼
UAT / Customer Acceptance
   │
   ▼
Issue Completion Certificate
   │
   ▼
Trigger Billing Eligibility (WF-FIN-001)
```

#### Closure

```text
Final Invoice status checked
   │
   ▼
Lessons Learned captured
   │
   ▼
Handover to Support / AMC (optional)
   │
   ▼
Create Renewal / Upsell Opportunity (Customer Success)
   │
   ▼
Project Status = Closed
Archive documents + retain audit
```

---

## 7. Finance Workflows

### 7.1 WF-FIN-001 — Customer Invoicing & Collections

| Attribute | Detail |
|-----------|--------|
| **Modules** | FIN-001 Invoice, FIN-002 Payment, FIN-004 Tax |
| **Actors** | Finance User, Sales (credit notes), Customer |

#### Process Flow

```text
Billing Trigger
  • Milestone completion
  • Sales Order schedule
  • Manual finance request
   │
   ▼
Create Draft Invoice
   │
   ▼
GST / Tax Calculation & Validation
   │
   ▼
Invoice Approval Workflow
   │
   ├── Rejected ──► Correct & resubmit
   │
   └── Approved
         │
         ▼
Issue Invoice to Customer
         │
         ▼
Await Payment
   ├── Full Payment ──► Record Receipt → Reconcile → Mark Paid
   ├── Partial Payment ──► Allocate → Remaining Due
   └── Overdue ──► Dunning Automation (reminders / escalation)
         │
         ▼
Collections Complete
```

#### Invoice States

`Draft → Pending Approval → Approved → Issued → Partially Paid → Paid → Overdue → Cancelled / Credited`

#### Business Rules

| Rule ID | Rule |
|---------|------|
| BR-FIN-001 | Invoice must link to Customer and billing source (SO/Project/Milestone) |
| BR-FIN-002 | Tax computed from tenant tax masters; manual override audited |
| BR-FIN-003 | Issued invoices are immutable except via Credit Note |
| BR-FIN-004 | Payments must allocate to one or more open invoices |
| BR-FIN-005 | Dunning schedule configurable per tenant |

---

### 7.2 WF-FIN-002 — Vendor Settlement

| Attribute | Detail |
|-----------|--------|
| **Module** | FIN-003 Vendor Settlement |
| **Actors** | Finance, Procurement, Project Manager |

#### Process Flow

```text
Vendor Invoice / Claim received
   │
   ▼
Match to PO / Work / Project cost
   │
   ▼
Approval
   │
   ▼
Payment / Settlement
   │
   ▼
Reconcile & Archive
```

---

## 8. Service Management Workflows (Phase 3)

### 8.1 WF-SRV-001 — Ticket Lifecycle & SLA

| Attribute | Detail |
|-----------|--------|
| **Modules** | SRV-001 Ticket, SRV-002 SLA, SRV-003 Knowledge |
| **Actors** | Support Agent, Customer Contact, SLA Monitor |

#### Process Flow

```text
Ticket Created (portal / email / phone / internal)
   │
   ▼
Classify (priority, category, customer)
   │
   ▼
Apply SLA Policy (response & resolution timers start)
   │
   ▼
Assign Agent / Queue
   │
   ▼
Investigate & Resolve
   • Optionally link Knowledge Article
   │
   ▼
Customer Confirmation
   │
   ├── Reopen ──► Resume SLA / new cycle per policy
   │
   └── Confirm ──► Close Ticket
         │
         ▼
SLA Met / Breached recorded → Reports & escalations
```

#### Ticket States

`New → Open → In Progress → Waiting on Customer → Resolved → Closed → Reopened`

---

## 9. Cross-Cutting Workflow Patterns

### 9.1 Generic Approval Pattern (used everywhere)

```text
Submit for Approval
   → Identify Approvers (role / amount matrix / rule)
   → Parallel or Sequential approval
   → Approve / Reject / Request Info
   → Notify requester
   → Persist decision in Audit
```

Configurable via **Workflow Designer (CPS-001-001-001)** and **Rule Configuration (CPS-002-001-001)**.

### 9.2 Notification Pattern

| Event Type | Examples |
|------------|----------|
| Lifecycle | Created, Activated, Closed Won, Invoice Issued |
| Reminder | Activity due, Trial expiring, Payment overdue |
| Escalation | SLA breach, Approval pending beyond SLA |
| Security | Account locked, MFA enabled, Tenant suspended |

Channels: in-app, email; SMS/push as edition/phase allows.

### 9.3 Audit Pattern

Every create / update / status change / approval / soft-delete writes:

- Actor (`user_id`)  
- Timestamp  
- Entity type + ID  
- Old / new values (or change summary)  
- Tenant context  

Retention driven by `tenant_security.audit_log_retention_days`.

### 9.4 Document Pattern

```text
Upload → Virus/type validation → Store in MinIO → Version bump → Link to business record → ACL by RBAC
```

---

## 10. Integration Workflows (Phase 4)

| Workflow | Module | Description |
|----------|--------|-------------|
| WF-INT-001 | INT-001 REST API | External systems call authenticated REST services |
| WF-INT-002 | INT-002 Webhooks | E-LinkUp emits event notifications on state changes |
| WF-INT-003 | INT-003 OAuth | Third-party delegated authentication |
| WF-INT-004 | INT-004 Connectors | Packaged connectors to external business systems |

All integration traffic passes API Gateway with tenant-scoped credentials and audit.

---

## 11. CRM User × Workflow Matrix (Euphoria)

Actors use CRM role names. “Sales” below means **Sales Executive** and/or **Sales Manager** as noted in each WF section.

| Workflow | Platform Admin | Tenant Admin | Sales Exec | Sales Mgr | Pre-Sales | PM | Team Member | Finance User | Support Agent |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Tenant Onboarding | ● | ○ | | | | | | | |
| Org / RBAC Setup | ○ | ● | | | | | | | |
| Lead Capture | | ○ | ● | ◐ | | | | | |
| Opportunity Pipeline | | ○ | ● | ● | ◐ | | | | |
| Quotation / Proposal | | | ● | ● | ● | | | ◐ | |
| Sales / Work Order | | | ◐ | ● | | ◐ | | ● | |
| Project Execution | | | ○ | | | ● | ● | ○ | |
| Change Request | | | ◐ | ◐ | | ● | ○ | ● | |
| Invoice & Payment | | | ○ | | | ○ | | ● | |
| Tickets & SLA | | | ○ | | | ○ | | | ● |

● Primary ◐ Contributing ○ View / occasional

---

## 12. Exception & Edge-Case Catalogue

| Scenario | Expected System Behaviour |
|----------|---------------------------|
| Tenant suspended mid-project | Block new transactions; read-only historical access per policy |
| Subscription expired | Restrict features per edition/licence rules; notify admin |
| Duplicate lead on convert | Block convert; force merge/link |
| Quote expired before acceptance | Require revision & re-approval |
| Credit check fails | Hold Sales Order; allow advance-payment path |
| Unapproved change executed | Disallowed; enforce CR workflow |
| Partial payment | Keep invoice Partially Paid; age remaining balance |
| SLA breach | Escalate per SLA matrix; mark breach for MIS |
| Soft-deleted master with children | Prevent hard delete; retain references |

---

## 13. Reporting Touchpoints by Workflow

| Workflow Stage | Key Reports |
|----------------|-------------|
| Foundation | Active/Trial Tenants, Expiring Subscriptions, Edition Distribution |
| CRM | Lead source conversion, Pipeline by stage, Activity compliance |
| Sales | Quote win rate, Discount exceptions, Order backlog |
| Projects | Milestone slip, Utilisation, Open issues/CR ageing |
| Finance | Invoice register, Ageing, Collections vs target, Tax summary |
| Service | Ticket volume, SLA attainment, Knowledge reuse |

---

## 14. Technology Mapping (Execution Layer)

| Concern | Technology |
|---------|------------|
| Workflow & business APIs | Python FastAPI |
| Data | PostgreSQL (tenant-aware model) |
| Auth | JWT + Argon2id (+ SSO/MFA Enterprise) |
| UI | Flutter Web / Android |
| Documents | MinIO |
| Async jobs (Phase 3+) | Celery + Redis |
| Gateway / runtime | Nginx + Docker |
| CI/CD & Hosting | GitHub Actions → Azure / Linux VPS |

---

## 15. Phased Rollout of Workflows

| Phase | Release | Workflows Enabled |
|-------|---------|-------------------|
| **Phase 1** | v1.0 | WF-PF-001…003 (Foundation, Org, Users, RBAC, Audit, Config) |
| **Phase 2** | v1.0 | WF-CRM-*, WF-SAL-*, WF-PRJ-001…003, WF-FIN-001…002 |
| **Phase 3** | v1.5 | WF-SRV-001, advanced Workflow/Rule/Notification/Document engines |
| **Phase 4** | v2.0 | WF-INT-*, Enterprise BI, AI Assistant recommendations |

---

## 16. Traceability Summary

| Story Act (ELU-STORY-001) | Workflow IDs | BRD Feature IDs |
|---------------------------|--------------|-----------------|
| Act I Platform Foundation | WF-PF-001…003 | PF-001…011 |
| Act II Find & Win | WF-CRM-001…004, WF-SAL-001…002 | CRM-001…004, SAL-001…003 |
| Act III Deliver | WF-SAL-003, WF-PRJ-001…002 | SAL-004, PRJ-001…006 |
| Act IV Get Paid | WF-FIN-001…002, WF-PRJ-003 | FIN-001…004 |
| Act V After Sale | WF-SRV-001 | SRV-001…003 |
| Invisible Heroes | Cross-cutting §9 | CPS-001…008, INT-001…004 |

---

## 17. Document Control

| Field | Value |
|-------|-------|
| Status | Draft v1.1 |
| Change | Euphoria as example tenant; CRM user-to-user actor naming aligned with ELU-STORY-001 |
| Reviewers | PMO, Business Analysts, Solution Architecture, Module Owners |
| Next Step | Workshop to confirm stage names, approval matrices, and SLA calendars for Euphoria |

---

*© Euphoria Infotech (I) Limited — E-LinkUp Internal Documentation*
