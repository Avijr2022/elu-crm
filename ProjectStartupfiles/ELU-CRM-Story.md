# E-LinkUp CRM Story
**Document ID:** ELU-STORY-001  
**Document Name:** Complete CRM Business Story (User-to-User)  
**Version:** 1.1  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Euphoria Infotech (I) Limited  
**Document Owner:** Product Management Office (PMO)  
**Tagline:** *"Connecting Business. Streamlining Growth."*  
**Related Documents:** ELU-DOC-001, ELU-CHR-001, ELU-HLD-001, ELU-BRD-001, ELU-EFS-001, ELU-WF-001, ELU-SAD-001

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-30 | EIIP | Initial CRM Story with dummy tenant removed
| 1.1 | 2026-07-30 | EIIP | Euphoria tenant; user-to-user CRM narrative
| 1.1a | 2026-07-31 | EIIP / PMO | Added Status, Version History; cross-refs to ELU-DOC-001 / ELU-EFS-001 |

> Catalogue entry: **ELU-DOC-001 – Documentation Master Index**. Cross-references must cite Document IDs (see **ELU-DF-001 – Documentation Framework**).

## 1. The Story in One Line

E-LinkUp is how **Euphoria** users move together from a Lead to cash and customer success — Sales to Pre-Sales to Delivery to Finance to Support — on one multi-tenant SaaS platform.

---

## 2. Why This Story Exists

Growing organisations often split work across inboxes, spreadsheets, and disconnected tools. A Lead sits with one user; a Quotation with another; a Project and an Invoice with someone else. Handoffs fail because the CRM is not the system of record for the full lifecycle.

**E-LinkUp unifies the user-to-user journey:**

> **Lead → Opportunity → Quotation / Proposal → Sales Order → Work Order → Project → Invoice → Collection → Closure → Customer Success**

This story is told **user to user** inside tenant **Euphoria** (Euphoria Infotech), using standard CRM names: Lead, Contact, Customer (Account), Opportunity, Activity, Quotation, Proposal, Sales Order, Work Order, Project, Invoice, Ticket.

---

## 3. CRM Users (Cast)

| CRM User Role | CRM Responsibility | Primary Objects |
|---------------|--------------------|-----------------|
| **Platform Admin** | Onboard tenants, editions, subscriptions | Tenant, Edition, Subscription |
| **Tenant Admin** | Org structure, users, RBAC, branding, security | Organization, User, Role, Settings |
| **Sales Executive** | Capture Leads, log Activities, own Opportunities, draft Quotations | Lead, Contact, Opportunity, Activity, Quotation |
| **Sales Manager** | Qualify pipeline, approve commercials, forecast | Opportunity, Quotation, Sales Order |
| **Pre-Sales / Solution Architect** | Technical fit, Proposal content | Opportunity, Proposal, Document |
| **Project Manager** | Plan and deliver after Work Order | Project, Milestone, Task, Change Request |
| **Team Member** | Execute Tasks, Timesheets, Issues | Task, Timesheet, Issue |
| **Finance User** | Invoice, Payment, Tax, Vendor Settlement | Invoice, Payment, Settlement |
| **Support Agent** | Tickets, SLA, Knowledge | Ticket, SLA, Knowledge Article |
| **Customer Contact** | External party on Customer record | Customer, Contact, Proposal, Invoice, Ticket |

---

## 4. Act I — Platform Foundation (Tenant Admin & Platform Admin)

### Scene 1: Euphoria Becomes a Tenant

**Platform Admin** registers tenant **Euphoria**:

1. Validate company profile (legal name, contacts, addresses, tax IDs where applicable)  
2. Assign **Edition** (Community / Professional / Enterprise)  
3. Assign **Subscription**  
4. Create default **Organization** (Head Office)  
5. Create **Tenant Admin** user  
6. Initialise Settings, Security, Localisation, Branding  
7. **Activate** the tenant  

Every Lead, Opportunity, Invoice, and Timesheet for Euphoria carries `tenant_id`. Isolation is absolute between tenants.

### Scene 2: Tenant Admin Prepares the CRM Team

**Tenant Admin** configures Euphoria for day-to-day CRM use:

- Organizations, Branches, Departments, Business Units  
- Users and **Roles & Permissions (RBAC)**  
- Security (password policy, MFA on Enterprise, session rules)  
- Currency, timezone, financial year, document prefixes  
- Branding on Flutter Web / Android  

**Story beat:** *Before the first Lead, users, access, and audit are ready.*

---

## 5. Act II — Find & Win (Sales Executive → Sales Manager → Pre-Sales)

### Scene 3: Sales Executive Captures a Lead

**Sales Executive** creates a **Lead** (CRM-001):

- Source, Contact, organisation details, interest, estimated value  
- Owner = Sales Executive  
- **Duplicate check** on email / phone / company  
- Activities on the **Activity Timeline** (CRM-004): call, email, meeting  

**Sales Manager** reviews qualification (budget, authority, need, timeline). Optional **NDA** before sharing sensitive material.

| Outcome | Next CRM Action |
|---------|-----------------|
| Qualified | Convert Lead → Opportunity (+ Customer if needed) |
| Not ready | Nurture |
| Unfit | Disqualify (reason mandatory) |

### Scene 4: Opportunity Pipeline (User Handoff)

On conversion:

- **Lead** → read-only / Converted  
- **Opportunity** (CRM-002) opened with stage, value, close date, probability  
- **Customer** profile (CRM-003) maintained as the Account master  
- **Contact** linked for the buying party  

Pipeline moves user-to-user:

| Stage | Owning / Contributing Users |
|-------|-----------------------------|
| Qualification | Sales Executive, Sales Manager |
| Technical Evaluation | Pre-Sales / Solution Architect |
| Budget Validation | Sales Manager, Finance User (advisory) |
| Proposal / Quotation | Sales Executive, Pre-Sales |
| Negotiation | Sales Manager, Legal / Compliance (via approval) |
| Closed Won / Lost | Sales Manager |

**Story beat:** *CRM names stay stable; ownership moves cleanly between users.*

### Scene 5: Quotation & Proposal

**Sales Executive** creates **Quotation** (SAL-001). **Pre-Sales** authors **Proposal** (SAL-002) with version control.

- Internal approval via **Workflow Engine** (Sales Manager and above by amount rules)  
- Documents in **Document Engine**  
- Customer Contact receives the approved version  

Revisions create new versions; only an **approved Quotation** can become a Sales Order.

### Scene 6: Sales Order & Work Order

After acceptance and credit / commercial approval:

1. **Sales Manager / Finance** confirm **Sales Order** (SAL-003)  
2. Delivery receives **Work Order** (SAL-004)  
3. Hand-off to **Project Manager**  

**Story beat:** *Closed Won is a user handoff from Sales to Delivery — not just a stage label.*

---

## 6. Act III — Deliver (Project Manager ↔ Team Member)

### Scene 7: Project from Work Order

**Project Manager** opens a **Project** (PRJ-001) linked to Customer, Sales Order, and Work Order.

| Object | User Action |
|--------|-------------|
| **Milestone** | Plan checkpoints (design, UAT, go-live) |
| **Task** | Assign to Team Members |
| **Timesheet** | Team Member logs; PM approves |
| **Issue** | Raise and resolve blockers |
| **Change Request** | Scope / schedule / cost — PM + Sales + Finance + Customer Contact as needed |

Workflow, Rule, and Notification engines keep assignees and approvers in sync.

### Scene 8: Completion Certificate

QA → UAT → Customer Contact acceptance → **Completion Certificate** → billing eligibility for Finance.

**Story beat:** *Delivery truth becomes the source for Invoice.*

---

## 7. Act IV — Get Paid (Finance User ↔ Customer Contact)

### Scene 9: Invoice & Payment

**Finance User** raises **Customer Invoice** (FIN-001) from milestone / Sales Order schedule, with **GST & Tax** (FIN-004) and approval.

**Customer Contact** pays. **Finance User** records **Payment** (FIN-002), reconciles, and runs dunning if overdue.

**Vendor Settlement** (FIN-003) closes supplier costs for the same Project.

### Scene 10: Closure & Next Opportunity

Project closure: lessons learned, optional AMC, **Sales Executive / Customer Success** opens a renewal **Opportunity** on the same **Customer**.

---

## 8. Act V — Stay Connected (Support Agent ↔ Customer Contact)

### Scene 11: Ticket & SLA

**Support Agent** manages **Ticket** lifecycle (SRV-001), watched by **SLA** (SRV-002), aided by **Knowledge Articles** (SRV-003). Activities continue on the same Customer timeline Sales and Projects already use.

### Scene 12: Insight for Every User

Managers use dashboards (pipeline, utilisation, receivables, SLA) instead of personal spreadsheets. Later, **AI Assistant** suggests next actions — still under RBAC and Audit.

---

## 9. Shared Engines (Every User, Every Object)

```text
Workflow Engine      → Approvals & state transitions between users
Rule Engine          → Routing, thresholds, auto-probability
Notification Engine  → User alerts & escalations
Document Engine      → Versioned files on CRM/Sales/Project records
Reporting Engine     → Role-based MIS
Audit Engine         → Who changed which CRM object, when
API Gateway          → External systems under tenant scope
```

---

## 10. Editions (Same Users, Different Depth)

| Edition | Typical Euphoria Deployment | CRM / Suite Depth |
|---------|----------------------------|-------------------|
| **Community** | Learning & demo | Core CRM, basic Sales & Reports |
| **Professional** | SME operations | CRM + Sales + Projects + Finance + Help Desk |
| **Enterprise** | Full SaaS governance | Full suite + SSO/MFA, advanced workflow/rules, API, AI |

---

## 11. End-to-End User-to-User Map

```text
Platform Admin → Tenant (Euphoria) Active
       ↓
Tenant Admin → Users, Roles, Org ready
       ↓
Sales Executive → Lead → Activity
       ↓
Sales Manager → Qualify → convert
       ↓
Sales Executive + Pre-Sales → Opportunity → Quotation / Proposal
       ↓
Sales Manager + Finance → Sales Order → Work Order
       ↓
Project Manager + Team Member → Project → Milestone / Task / Timesheet
       ↓
Project Manager + Customer Contact → Completion Certificate
       ↓
Finance User + Customer Contact → Invoice → Payment
       ↓
Support Agent + Customer Contact → Ticket / SLA / Renewal Opportunity
```

---

## 12. Success for Euphoria Users

Euphoria users can answer, in minutes:

1. Which **Leads** became revenue this quarter?  
2. Which **Opportunities** lack owner **Activity**?  
3. Which **Projects** miss **Milestones** or burn budget?  
4. Which **Invoices** are overdue and who owns follow-up?  
5. Who approved the last commercial exception on a **Quotation** / **Sales Order**?  
6. Is tenant isolation and audit ready for a customer or auditor review?

That is the complete CRM story: **user-to-user continuity on named CRM objects**, for tenant Euphoria, on E-LinkUp.

---

## 13. Document Control

| Field | Value |
|-------|-------|
| Status | Draft v1.1 |
| Change | Removed dummy tenant names; Euphoria + CRM user-to-user narrative |
| Downstream | ELU-WF-001, ELU-SAD-001 |

---

*© Euphoria Infotech (I) Limited — E-LinkUp Internal Documentation*
