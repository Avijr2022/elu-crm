# E-LinkUp Business Functional Specification — Service Domain Pack
**Document ID:** ELU-BFS-SRV  
**Document Name:** Service Domain BFS Pack (Help Desk)  
**Version:** 1.0  
**Status:** Approved
**Related Documents:** ELU-DOC-001, ELU-DF-001, ELU-BRD-001, ELU-EFS-001, ELU-RTM-001
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Senior BA / Enterprise Solution Architect / Product Owner  
**Document Owner:** PMO  
**Example Tenant:** Euphoria  
**Stack:** Flutter (Web + Android) · Python FastAPI · PostgreSQL · JWT + Refresh Token · Docker · MinIO · Celery/Redis (Phase 3+)  
**Related Documents:** ELU-DF-001, ELU-BRD-001, ELU-SAD-001, ELU-WF-001, ELU-STORY-001

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP | Initial BFS pack (seventeen sections) |
| 1.0a | 2026-07-31 | EIIP / PMO | Status Approved; registered in ELU-DOC-001; Related Documents standardized |

## Pack Index

| Module ID | Module / Sub Module / Feature | Priority | Phase / Release | BFS Section |
|-----------|-------------------------------|----------|-----------------|-------------|
| SRV-001 | Ticket Management / Ticket Lifecycle | High | v1.5 Phase 3 | [§ Module SRV-001](#module-srv-001--ticket-management--ticket-lifecycle) |
| SRV-002 | SLA Management / SLA Monitoring | High | v1.5 Phase 3 | [§ Module SRV-002](#module-srv-002--sla-management--sla-monitoring) |
| SRV-003 | Knowledge Management / Knowledge Articles | Medium | v1.5 Phase 3 | [§ Module SRV-003](#module-srv-003--knowledge-management--knowledge-articles) |

**API Prefix:** `/api/v1/service/`  
**Business Rule Prefix:** `BR-SRV-xxx`  
**Workflow Reference:** `WF-SRV-001`  
**Minimum Edition:** Professional (Community: read-only Knowledge portal deferred)

### Downstream Artefact Index

| Artefact | Document ID Pattern |
|----------|---------------------|
| Field Dictionary | ELU-FD-SRV-001 … ELU-FD-SRV-003 |
| ERD Pack | ELU-ERD-SRV |
| API Specification | ELU-API-SRV |
| Flutter Screen Spec | ELU-UI-SRV |
| Workflow Pack | ELU-WF-SRV-001 |
| RBAC Matrix | ELU-RBAC-SRV |
| Notification Catalogue | ELU-NTF-SRV |
| Report Catalogue | ELU-RPT-SRV |
| Test Case Pack | ELU-TC-SRV |

### Shared Engine Dependencies

| Engine | Module | Usage in SRV Pack |
|--------|--------|-------------------|
| Workflow Engine | CPS-001 | Ticket escalation, approval for severity override |
| Rule Engine | CPS-002 | Auto-assignment, priority routing, SLA policy selection |
| Notification Engine | CPS-003 | Ticket events, SLA breach alerts |
| Reporting & Analytics | CPS-004 | Help desk MIS, SLA dashboards |
| Audit Service | CPS-005 | Full ticket/SLA/KB audit trail |
| Document Management | CPS-006 | Ticket attachments, KB article assets |

---

# Module SRV-001 — Ticket Management / Ticket Lifecycle

**Document ID:** ELU-BFS-SRV-001  
**Module:** SRV-001 — Ticket Management  
**Sub Module:** SRV-001-001 — Ticket  
**Feature:** SRV-001-001-001 — Ticket Lifecycle  
**Domain:** SRV (Service / Help Desk)  
**Priority / Phase / Release:** High · v1.5 · Phase 3  
**Example Tenant:** Euphoria  
**Workflow:** WF-SRV-001

---

## 1. Business Objective

### 1.1 Why this module exists
Euphoria delivers IT services, software projects, and AMC contracts. After Sales Order closure and Project handover, **Customer Contacts** require a structured channel to report incidents, request changes, and track resolution. Without a central **Ticket** object tied to **Customer**, **Contact**, **Project**, and **Sales Order**, Support Agents work from email threads with no SLA accountability, no audit trail, and no linkage to the CRM timeline.

### 1.2 Business value
| Metric | Expected Impact |
|--------|-----------------|
| First-response time | Measurable via SLA timers (SRV-002) |
| Resolution visibility | Customer and internal users see unified status |
| Customer satisfaction | Portal + notifications reduce follow-up calls |
| Revenue protection | AMC/contract tickets linked to entitlement |
| Audit & compliance | Immutable history for dispute resolution |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Ticket CRUD, assignment, queues | Full ITIL CMDB (v3.0) |
| Internal + customer portal creation | Email-to-ticket ingestion (v2.0) |
| Link to Customer, Contact, Project, SO | Chatbot deflection (CPS-007 v2.0) |
| Status lifecycle, reopen, merge | Asset discovery auto-ticketing |
| Comments (public/internal), attachments | Multi-language KB translation |
| Escalation via Workflow Engine | |

### 1.4 Users involved
Support Agent, Support Manager, Customer Contact, Tenant Admin, Sales Executive (read), Project Manager (read/link), System (Rule Engine, Notification Engine, SLA Monitor).

### 1.5 Module reference

| Attribute | Value |
|-----------|-------|
| Domain | SRV |
| Module ID | SRV-001 |
| Sub Module | SRV-001-001 Ticket |
| Feature | SRV-001-001-001 Ticket Lifecycle |
| Priority | High |
| Phase | 3 |
| Release | v1.5 |
| Edition | Professional minimum |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Support Agent | Internal | Create, update, assign, resolve, comment | View Customer/Project context |
| Support Manager | Internal | Reassign, escalate, override priority, approve reopen | Queue configuration, reports |
| Customer Contact | External | Create ticket (portal), add comment, confirm/reopen | View own tickets |
| Tenant Admin | Internal | Configure categories, queues, numbering | — |
| Sales Executive | Internal | — | View tickets for owned Customers |
| Project Manager | Internal | Link ticket to Project/Issue | View delivery-related tickets |
| System (Rule Engine) | System | Auto-assign, route by category | — |
| System (SLA Monitor) | System | Start/pause/resume SLA clocks | Breach escalation |
| System (Notification Engine) | System | Send alerts on lifecycle events | — |

---

## 3. Business Story

After Euphoria completes a **Project** for a **Customer**, the **Customer Contact** logs into the E-LinkUp customer portal and raises a **Ticket**: *"Production API timeout after last deployment."* The ticket captures subject, description, category (*Application Support*), priority (*High*), and links to the **Customer** record and related **Project**.

The **Rule Engine** evaluates Euphoria's routing rules: category = Application Support AND priority = High → assign to *L2 Application Queue* and notify on-call **Support Agent** Raj. **SLA Policy** *Enterprise AMC — 4h response / 24h resolution* attaches automatically because the Customer has an active AMC entitlement on the linked **Sales Order**.

**Support Agent** Raj accepts the ticket (status → *In Progress*), adds an internal note requesting logs, and attaches a diagnostic checklist from **Document Management**. He links **Knowledge Article** KA-1042 (*API Gateway Timeout Troubleshooting*) to the ticket. The **Customer Contact** receives an email notification with the public comment asking for log files.

The Customer uploads logs via the portal comment thread. Raj identifies a misconfigured timeout in the deployment manifest, applies the fix, and sets status to *Resolved* with resolution notes. The Customer receives a resolution notification and confirms closure. Status moves to *Closed*; SLA outcome is recorded as *Met*. If the Customer had rejected the fix, they could *Reopen* within the configured window (30 days), reactivating SLA per policy.

**Support Manager** Priya reviews the weekly ticket backlog report. A ticket breaching SLA triggers an escalation notification to her queue; she reassigns workload and documents the breach reason for the management dashboard.

Exception paths:
- **Waiting on Customer:** SLA resolution clock pauses (SRV-002).
- **Duplicate:** Agent merges Ticket B into Ticket A; B becomes *Merged* (read-only).
- **Invalid request:** Agent cancels with mandatory reason before resolution effort.

---

## 4. Business Workflow

### 4.1 Process Flow

```text
[Start] Ticket Created (portal / internal / API)
   │
   ▼
Validate Customer + Contact + mandatory fields (BR-SRV-001)
   │
   ▼
Classify: Category, Sub-category, Priority, Type (Incident/Request/Problem)
   │
   ▼
Apply SLA Policy (SRV-002) ──► Start response timer
   │
   ▼
Auto-assign (Rule Engine) or Manual Queue
   │
   ▼
Notify Assignee + Customer (acknowledgement)
   │
   ▼
Agent Works Ticket (comments, attachments, KB links)
   ├── Waiting on Customer ──► Pause resolution SLA
   └── Escalation (WF-SRV-001-E1) ──► Manager notified
   │
   ▼
Resolve ──► Notify Customer for confirmation
   │
   ├── Customer Reopens ──► Reopen + SLA cycle per policy
   └── Customer Confirms / Auto-close window ──► Closed
   │
   ▼
Record SLA outcome + Audit + MIS feed
[End]
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Customer Contact / Agent | Create ticket | Form / API payload | Ticket (New) | API, Rule Engine |
| 2 | System | Validate & number | Ticket draft | Ticket (validated) | Rule Engine |
| 3 | System | Attach SLA | Customer entitlement | SLA instance | SRV-002, Celery |
| 4 | System | Route & assign | Category, priority | Assignment record | Rule Engine |
| 5 | Support Agent | Accept / work | Ticket | Ticket (In Progress) | Workflow |
| 6 | Agent / Customer | Communicate | Comments, files | ticket_comment, documents | CPS-006 |
| 7 | Agent | Resolve | Resolution notes | Ticket (Resolved) | Notification |
| 8 | Customer | Confirm / reopen | Feedback | Closed / Reopened | SLA Monitor |
| 9 | System | Finalise SLA | Timestamps | sla_outcome | SRV-002 |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next | Entry Actors | System Effects |
|------------|-------------|-------------|--------------|--------------|----------------|
| NEW | New | Created, not yet picked up | OPEN, CANCELLED | All creators | Response SLA running |
| OPEN | Open | Acknowledged in queue | IN_PROGRESS, CANCELLED | Agent, Manager | — |
| IN_PROGRESS | In Progress | Active work | WAITING_CUSTOMER, RESOLVED, ESCALATED | Agent | — |
| WAITING_CUSTOMER | Waiting on Customer | Blocked on customer input | IN_PROGRESS, RESOLVED | Agent | Pause resolution SLA |
| ESCALATED | Escalated | Manager attention | IN_PROGRESS, RESOLVED | Manager, Workflow | Escalation notification |
| RESOLVED | Resolved | Fix delivered, pending confirmation | CLOSED, REOPENED | Agent | Resolution SLA stop |
| CLOSED | Closed | Confirmed complete | REOPENED (window) | Customer, System auto | SLA finalised |
| REOPENED | Reopened | Customer rejected resolution | IN_PROGRESS, RESOLVED | Customer, Manager | New SLA cycle optional |
| CANCELLED | Cancelled | Invalid/duplicate withdrawn | — | Agent, Manager | SLA voided |
| MERGED | Merged | Absorbed into parent ticket | — | Agent | Read-only, link to parent |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-SRV-001 | Every Ticket shall belong to exactly one Customer and one Tenant | Validation | Error | API, DB |
| BR-SRV-002 | Subject and Description are mandatory on create | Validation | Error | UI, API |
| BR-SRV-003 | Priority shall be one of: Low, Medium, High, Critical | Validation | Error | API, DB |
| BR-SRV-004 | Ticket Number shall be unique per tenant (auto-generated prefix `TKT-`) | Calculation | Error | API, DB |
| BR-SRV-005 | Only Support Agent or Support Manager may change assignment | Security | Error | API, RBAC |
| BR-SRV-006 | Customer Contact may only read/update own Customer's tickets | Security | Error | API |
| BR-SRV-007 | Internal comments shall not be visible to Customer Contact | Security | Error | API, UI |
| BR-SRV-008 | Resolved status requires resolution notes (min 20 characters) | Validation | Error | UI, API |
| BR-SRV-009 | Reopen allowed within `tenant_settings.ticket_reopen_days` (default 30) | Lifecycle | Error | API, Rule Engine |
| BR-SRV-010 | Merge requires parent ticket in non-terminal state | Lifecycle | Error | API |
| BR-SRV-011 | Cancelled tickets cannot transition except archive | Lifecycle | Error | API |
| BR-SRV-012 | Critical priority requires Support Manager notification | Notification | Warning | Notification Engine |
| BR-SRV-013 | Soft-deleted tickets are excluded from default lists | Lifecycle | Info | API |
| BR-SRV-014 | Ticket linking to Project requires Project.status ∈ {Active, On Hold} | Validation | Error | API |
| BR-SRV-015 | Auto-close Resolved tickets after `auto_close_days` (default 7) if no customer action | Lifecycle | Info | Celery scheduler |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| ticket | Transaction | Primary ticket header | Yes |
| ticket_comment | Transaction | Public and internal thread | Yes |
| ticket_assignment | Transaction | Assignment history | Yes |
| ticket_link | Link | Links to Project, SO, Issue, parent ticket | Yes |
| ticket_category | Master | Category hierarchy | Yes |
| ticket_queue | Master | Support queues | Yes |
| ticket_priority | Lookup | Priority definitions | Yes |
| ticket_status_history | Audit | State transition log | Yes |
| ticket_sla_instance | Transaction | FK to SLA module (SRV-002) | Yes |
| ticket_tag | Link | Optional tags | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| customer | ticket | 1:N | Restrict | Mandatory FK |
| contact | ticket | 1:N | Set Null | Primary reporter |
| project | ticket_link | 1:N | Restrict | Optional link |
| sales_order | ticket_link | 1:N | Restrict | AMC entitlement |
| issue (PRJ) | ticket_link | 1:N | Set Null | Delivery defect link |
| ticket | ticket_comment | 1:N | Cascade | Soft-delete comments |
| ticket | ticket_assignment | 1:N | Restrict | History preserved |
| ticket | ticket (parent) | 1:N | Restrict | Merge parent-child |
| sla_policy | ticket_sla_instance | 1:N | Restrict | Via SRV-002 |
| knowledge_article | ticket_kb_link | N:M | Restrict | Via SRV-003 |

---

## 9. Field Groups

### ticket
| Group | Logical Fields |
|-------|----------------|
| General Information | ticket_number, subject, description, type, channel |
| Classification | category_id, sub_category_id, priority_id, tags |
| Customer Context | customer_id, contact_id, contract_id |
| Assignment | queue_id, owner_id, team_id |
| Status | status, resolution_notes, cancellation_reason |
| SLA Summary | sla_policy_id, response_due, resolution_due, sla_status |
| Attachments | document_ids (via CPS-006) |
| Audit | tenant_id, is_deleted, version_no, created/modified |

### ticket_comment
| Group | Logical Fields |
|-------|----------------|
| Content | body, is_internal, channel |
| Author | author_user_id, author_contact_id |
| Audit | created_on, tenant_id |

---

## 10. REST APIs

**Base path:** `/api/v1/service/tickets`

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/service/tickets` | Create ticket | `ticket.create` |
| GET | `/api/v1/service/tickets` | List with filters | `ticket.read` |
| GET | `/api/v1/service/tickets/{id}` | Get by ID | `ticket.read` |
| PUT | `/api/v1/service/tickets/{id}` | Full update (draft fields) | `ticket.update` |
| PATCH | `/api/v1/service/tickets/{id}/status` | Status transition | `ticket.update` |
| PATCH | `/api/v1/service/tickets/{id}/assign` | Assign / reassign | `ticket.assign` |
| POST | `/api/v1/service/tickets/{id}/comments` | Add comment | `ticket.update` |
| GET | `/api/v1/service/tickets/{id}/comments` | List comments | `ticket.read` |
| POST | `/api/v1/service/tickets/{id}/merge` | Merge child into this | `ticket.assign` |
| POST | `/api/v1/service/tickets/{id}/links` | Link Project/SO/Issue | `ticket.update` |
| DELETE | `/api/v1/service/tickets/{id}` | Soft delete | `ticket.delete` |
| GET | `/api/v1/service/tickets/search` | Advanced search | `ticket.read` |
| GET | `/api/v1/service/tickets/export` | Export CSV/XLSX | `ticket.export` |
| GET | `/api/v1/service/tickets/my` | Customer portal: own tickets | `ticket.read` (scoped) |

**Supporting endpoints:**

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| GET | `/api/v1/service/categories` | Category tree | `ticket.read` |
| GET | `/api/v1/service/queues` | Queue list | `ticket.read` |
| CRUD | `/api/v1/service/queues` | Queue admin | `ticket.configure` |

---

## 11. Flutter Screens

| Screen ID | Screen | Type | Primary Actor | Route (Web) |
|-----------|--------|------|---------------|-------------|
| UI-SRV-001-L | Ticket List | List | Support Agent | `/service/tickets` |
| UI-SRV-001-C | Ticket Create | Create | Agent, Customer | `/service/tickets/new` |
| UI-SRV-001-E | Ticket Edit | Edit | Support Agent | `/service/tickets/{id}/edit` |
| UI-SRV-001-V | Ticket Detail | View | All authorised | `/service/tickets/{id}` |
| UI-SRV-001-S | Ticket Search | Search | Agent, Manager | `/service/tickets/search` |
| UI-SRV-001-Q | Queue Board | Kanban | Agent, Manager | `/service/queues/{id}/board` |
| UI-SRV-001-H | Ticket History | History | Agent, Manager | `/service/tickets/{id}/history` |
| UI-SRV-001-P | Portal My Tickets | List | Customer Contact | `/portal/tickets` |
| UI-SRV-001-PC | Portal Create Ticket | Create | Customer Contact | `/portal/tickets/new` |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `ticket.create` | Create tickets |
| `ticket.read` | View tickets (scoped by role) |
| `ticket.update` | Edit fields, comment, resolve |
| `ticket.delete` | Soft delete |
| `ticket.assign` | Assign, reassign, merge, escalate |
| `ticket.configure` | Categories, queues, numbering |
| `ticket.export` | Export lists |

| Actor | create | read | update | delete | assign | configure | export |
|-------|--------|------|--------|--------|--------|-----------|--------|
| Support Agent | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| Support Manager | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Customer Contact | ✓ (own) | ✓ (own) | ✓ (comment) | — | — | — | — |
| Tenant Admin | — | ✓ | — | — | — | ✓ | ✓ |
| Sales Executive | — | ✓ (customer) | — | — | — | — | — |
| Project Manager | — | ✓ (linked) | — | — | — | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Ticket Created | Email, In-app, Push* | Assignee, Customer | NTF-SRV-001 |
| Ticket Assigned | Email, In-app | Assignee | NTF-SRV-002 |
| Comment Added (public) | Email, In-app | Other party | NTF-SRV-003 |
| Status → Resolved | Email, In-app | Customer | NTF-SRV-004 |
| Ticket Closed | Email, In-app | Customer, Agent | NTF-SRV-005 |
| Ticket Reopened | Email, In-app | Assignee, Manager | NTF-SRV-006 |
| Escalation | Email, In-app | Support Manager | NTF-SRV-007 |
| SLA Warning (80%) | In-app, Email | Agent, Manager | NTF-SRV-008 |

*Push = Phase 3+ where enabled.

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-SRV-001 | Open Ticket Backlog | Operational | Agent, Manager | Ticket | Queue, priority, age | CSV, PDF |
| RPT-SRV-002 | Ticket Volume Trend | Management | Manager | Daily/weekly | Category, channel | CSV, XLSX |
| RPT-SRV-003 | Agent Workload | Operational | Manager | Agent | Date range | CSV |
| RPT-SRV-004 | Resolution Time Analysis | Management | Manager | Ticket | Priority, category | CSV, PDF |
| RPT-SRV-005 | Customer Ticket Summary | Operational | Sales Executive | Customer | Customer, period | CSV |
| KPI-SRV-001 | First Response Time | KPI Dashboard | Executive | Tenant | Period | Widget |
| KPI-SRV-002 | CSAT Proxy (reopen rate) | KPI Dashboard | Executive | Tenant | Period | Widget |

---

## 15. Audit Requirements

| Event | Captured Data | Retention |
|-------|---------------|-----------|
| ticket.created | Full payload snapshot | Per tenant policy |
| ticket.updated | Field-level diff | Per tenant policy |
| ticket.status_changed | Old/new status, actor | Per tenant policy |
| ticket.assigned | Old/new assignee, queue | Per tenant policy |
| ticket.comment_added | Comment ID, internal flag | Per tenant policy |
| ticket.merged | Parent/child IDs | Per tenant policy |
| ticket.deleted | Soft-delete actor | Per tenant policy |
| ticket.exported | Export scope, actor | Per tenant policy |

---

## 16. Acceptance Criteria

1. **Given** a Customer Contact on Euphoria portal **When** they create a ticket with valid fields **Then** ticket is created with status New, unique TKT number, and acknowledgement notification sent.
2. **Given** a ticket with High priority **When** created **Then** SLA policy attaches and response due datetime is persisted.
3. **Given** Support Agent **When** adding internal comment **Then** Customer Contact API returns 403 or omits comment from response.
4. **Given** ticket in Resolved **When** customer does not act for 7 days **Then** Celery job auto-closes ticket.
5. **Given** tenant B user **When** accessing tenant A ticket ID **Then** API returns 404 (isolation).
6. **Given** merge request **When** child merged into parent **Then** child status = Merged and audit records both IDs.
7. **Given** Agent resolves ticket **When** resolution notes &lt; 20 chars **Then** API returns 422.
8. **Given** Support Manager **When** exporting backlog **Then** CSV contains only tenant-scoped records.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Email-to-ticket ingestion (IMAP/Graph), AI-suggested categorisation (CPS-007) |
| v2.0 | Omnichannel (WhatsApp ticket creation via INT connectors) |
| v2.5 | Problem Management linkage, known-error database |
| v3.0 | Full ITIL-aligned CMDB, change advisory board integration |

---

# Module SRV-002 — SLA Management / SLA Monitoring

**Document ID:** ELU-BFS-SRV-002  
**Module:** SRV-002 — SLA Management  
**Sub Module:** SRV-002-001 — SLA Policy  
**Feature:** SRV-002-001-001 — SLA Monitoring  
**Domain:** SRV  
**Priority / Phase / Release:** High · v1.5 · Phase 3  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Tickets without enforceable **SLA Policies** cannot guarantee contractual response and resolution commitments for Euphoria's AMC and enterprise support agreements. Manual tracking in spreadsheets fails at scale and cannot drive real-time escalations.

### 1.2 Business value
- Contract compliance visibility for Finance and Account Management  
- Automated breach detection and escalation  
- Business-hours-aware timers reduce false breaches  
- Executive SLA dashboards for QBRs with Customers  

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| SLA policy definition (response, resolution) | Penalty invoicing automation |
| Business calendars, holidays | Multi-region failover SLA |
| Per-ticket SLA instance & clocks | Legal e-signature on SLA |
| Pause/resume (waiting on customer) | |
| Breach/warning thresholds | |
| Celery-based SLA monitor jobs | |

### 1.4 Users involved
Tenant Admin, Support Manager, System (SLA Monitor, Celery), Support Agent (read SLA on ticket).

### 1.5 Module reference
SRV-002 · SLA Management · SLA Monitoring · High · Phase 3 · v1.5 · Professional+

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Define policies, calendars | — |
| Support Manager | Internal | View breaches, configure escalations | Override pause |
| Support Agent | Internal | — | View SLA on ticket |
| System (SLA Monitor) | System | Evaluate clocks, fire breaches | Celery/Redis |
| System (Notification Engine) | System | Warnings, breaches | — |

---

## 3. Business Story

**Tenant Admin** at Euphoria configures three **SLA Policies**:

1. *Standard Support* — 8 business hours response, 48 business hours resolution  
2. *Enterprise AMC* — 4h response, 24h resolution (24×7 clock)  
3. *Critical Incident* — 1h response, 8h resolution  

Each policy references **Business Calendar** *Euphoria India* (Mon–Sat 09:00–18:00 IST, public holidays from tenant holiday table).

When a **Ticket** is created for a Customer with an active AMC on **Sales Order** SO-2024-089, **Rule Engine** selects *Enterprise AMC* policy. **SLA Monitor** creates `ticket_sla_instance` with `response_due` and `resolution_due` timestamps.

At 75% of response window, Agent receives in-app warning. If response is not logged (first public/agent comment or status change to In Progress), breach flag sets at due time and **Support Manager** receives escalation.

When Agent sets *Waiting on Customer*, resolution clock **pauses** (BR-SRV-022). Customer reply resumes clock. On *Resolved*, resolution timer stops. Outcome: *Met*, *Breached*, or *Met with Escalation* stored for MIS.

---

## 4. Business Workflow

```text
[Policy Setup]
Tenant Admin defines SLA Policy + Calendar + Escalation rules
   │
[Runtime — per Ticket]
Ticket Created
   ▼
Select SLA Policy (rule or manual)
   ▼
Create ticket_sla_instance; compute due dates
   ▼
Celery beat (every 1 min): SLA Monitor evaluates
   ├── Warning threshold ──► Notify Agent/Manager
   ├── Response breach ──► Flag + escalate
   ├── Resolution pause event ──► Skip resolution tick
   └── Resolution breach ──► Flag + escalate
   ▼
Ticket Closed ──► Finalise outcome (Met/Breached)
```

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Tenant Admin | Create policy | Policy form | sla_policy | API |
| 2 | System | Bind to ticket | Ticket + rules | sla_instance | Rule Engine |
| 3 | System | Compute dues | Calendar, priorities | due timestamps | SLA Monitor |
| 4 | Celery | Poll instances | Active tickets | breach events | Celery/Redis |
| 5 | System | Notify | Breach/warning | Notifications | CPS-003 |

---

## 5. Business States

### SLA Policy (configuration)
| State Code | Label | Next States |
|------------|-------|-------------|
| DRAFT | Draft | ACTIVE, ARCHIVED |
| ACTIVE | Active | ARCHIVED |
| ARCHIVED | Archived | — |

### SLA Instance (per ticket)
| State Code | Label | Description | Next |
|------------|-------|-------------|------|
| RUNNING | Running | Clocks active | PAUSED, COMPLETED, BREACHED |
| PAUSED | Paused | Waiting on customer | RUNNING |
| BREACHED | Breached | One or both targets missed | COMPLETED |
| COMPLETED | Completed | Ticket terminal; outcome set | — |

### SLA Outcome (final)
`MET` · `BREACHED` · `MET_WITH_WARNING` · `VOID` (cancelled ticket)

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-SRV-021 | SLA Policy name unique per tenant | Validation | Error | DB |
| BR-SRV-022 | Resolution SLA pauses when ticket status = WAITING_CUSTOMER | Lifecycle | — | SLA Monitor |
| BR-SRV-023 | Response SLA stops on first agent response (comment or In Progress) | Calculation | — | SLA Monitor |
| BR-SRV-024 | Business hours calculated per linked calendar | Calculation | — | SLA Monitor |
| BR-SRV-025 | Only one active SLA instance per ticket | Validation | Error | DB |
| BR-SRV-026 | Critical priority may override with shorter policy via Rule Engine | Approval | Warning | Rule Engine |
| BR-SRV-027 | Breach escalation shall notify Support Manager within 60 seconds | Notification | Error | Celery |
| BR-SRV-028 | Archived policies cannot attach to new tickets | Lifecycle | Error | API |
| BR-SRV-029 | SLA warning threshold default 75% (tenant configurable) | Calculation | Info | Config |
| BR-SRV-030 | Void SLA on Cancelled/Merged child tickets | Lifecycle | Info | API |

---

## 7. Database Impact

| Table | Type | Purpose | Tenant Scoped |
|-------|------|---------|---------------|
| sla_policy | Master | Policy definitions | Yes |
| sla_policy_target | Master | Response/resolution durations | Yes |
| sla_business_calendar | Master | Working hours | Yes |
| sla_holiday | Master | Non-working days | Yes |
| sla_escalation_rule | Master | Breach actions | Yes |
| ticket_sla_instance | Transaction | Per-ticket runtime | Yes |
| sla_clock_event | Audit | Pause/resume/breach events | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| sla_policy | sla_policy_target | 1:N | Cascade |
| sla_business_calendar | sla_policy | 1:N | Restrict |
| ticket | ticket_sla_instance | 1:1 | Restrict |
| sla_policy | ticket_sla_instance | 1:N | Restrict |
| ticket_sla_instance | sla_clock_event | 1:N | Cascade |

---

## 9. Field Groups

### sla_policy
General Information, Targets (response/resolution), Calendar Reference, Escalation, Priority Mapping, Status, Audit

### ticket_sla_instance
Policy Reference, Ticket Reference, Clocks (start, response_due, resolution_due, paused_at), Outcome, Breach Flags, Audit

---

## 10. REST APIs

**Base:** `/api/v1/service/sla`

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/service/sla/policies` | Create policy | `sla.configure` |
| GET | `/api/v1/service/sla/policies` | List policies | `sla.read` |
| GET | `/api/v1/service/sla/policies/{id}` | Get policy | `sla.read` |
| PUT | `/api/v1/service/sla/policies/{id}` | Update policy | `sla.configure` |
| PATCH | `/api/v1/service/sla/policies/{id}/status` | Activate/archive | `sla.configure` |
| GET | `/api/v1/service/sla/instances` | List active instances | `sla.read` |
| GET | `/api/v1/service/sla/instances/{ticket_id}` | Ticket SLA detail | `sla.read` |
| POST | `/api/v1/service/sla/calendars` | Create calendar | `sla.configure` |
| GET | `/api/v1/service/sla/calendars` | List calendars | `sla.read` |
| GET | `/api/v1/service/sla/breaches` | Breach report feed | `sla.read` |

---

## 11. Flutter Screens

| Screen ID | Screen | Type | Actor |
|-----------|--------|------|-------|
| UI-SRV-002-PL | SLA Policy List | List | Tenant Admin |
| UI-SRV-002-PC | SLA Policy Configure | Create/Edit | Tenant Admin |
| UI-SRV-002-CAL | Business Calendar | Configure | Tenant Admin |
| UI-SRV-002-MON | SLA Monitor Dashboard | Dashboard | Support Manager |
| UI-SRV-002-TKT | Ticket SLA Widget | Embedded | Agent (on ticket detail) |

---

## 12. RBAC Permissions

| Permission | Tenant Admin | Support Manager | Support Agent |
|------------|--------------|-----------------|---------------|
| `sla.configure` | ✓ | — | — |
| `sla.read` | ✓ | ✓ | ✓ |
| `sla.override` | — | ✓ | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template |
|-------|----------|------------|----------|
| SLA Warning 75% | In-app, Email | Agent | NTF-SRV-010 |
| Response Breach | In-app, Email | Agent, Manager | NTF-SRV-011 |
| Resolution Breach | In-app, Email | Manager | NTF-SRV-012 |
| SLA Policy Activated | In-app | Tenant Admin | NTF-SRV-013 |

---

## 14. Reports

| Report ID | Name | Audience |
|-----------|------|----------|
| RPT-SRV-010 | SLA Compliance Summary | Manager, Executive |
| RPT-SRV-011 | Breach Detail Log | Manager |
| RPT-SRV-012 | Policy Effectiveness | Tenant Admin |
| KPI-SRV-003 | SLA Met % | Executive Dashboard |

---

## 15. Audit Requirements
Policy create/update/archive; instance create; pause/resume; breach marked; manual override by Manager — all via CPS-005.

---

## 16. Acceptance Criteria

1. Business-hours SLA due date skips weekends and holidays on Euphoria calendar.  
2. Waiting on Customer pauses resolution clock; resume restores remaining time.  
3. Celery job marks breach within 2 minutes of due expiry.  
4. Archived policy cannot be assigned to new ticket (422).  
5. Multi-tenant: policy from tenant A not visible to tenant B.

---

## 17. Future Enhancements

| Version | Idea |
|---------|------|
| v2.0 | SLA credit tracking for contractual penalties |
| v2.5 | Multi-clock (vendor + customer SLA) |
| v3.0 | Predictive breach ML (CPS-007) |

---

# Module SRV-003 — Knowledge Management / Knowledge Articles

**Document ID:** ELU-BFS-SRV-003  
**Module:** SRV-003 — Knowledge Management  
**Sub Module:** SRV-003-001 — Knowledge Article  
**Feature:** SRV-003-001-001 — Knowledge Articles  
**Domain:** SRV  
**Priority / Phase / Release:** Medium · v1.5 · Phase 3  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Support Agents repeatedly solve the same problems without a governed **Knowledge Article** repository. Resolution times increase, quality varies, and onboarding new Agents is slow. A tenant-scoped KB integrated with Tickets reduces repeat effort and enables customer self-service.

### 1.2 Business value
- Faster mean time to resolve  
- Self-service deflection on customer portal  
- Governed publish workflow for accurate content  
- Search analytics to identify documentation gaps  

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Article CRUD, versioning, publish workflow | External public SEO site |
| Categories, tags, full-text search | AI auto-authoring (v2.0) |
| Link articles to tickets | Video hosting (embed links only) |
| Customer-visible vs internal articles | |
| Attachments via MinIO | |

### 1.4 Users involved
Support Agent, Support Manager, Tenant Admin, Customer Contact (published external articles), Technical Author (Agent role extension).

### 1.5 Module reference
SRV-003 · Knowledge Management · Knowledge Articles · Medium · Phase 3 · v1.5 · Professional+

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Support Agent | Internal | Draft articles, suggest from ticket | Search, link |
| Support Manager | Internal | Review, publish, archive | Approve workflow |
| Tenant Admin | Internal | Configure categories, templates | — |
| Customer Contact | External | Search published articles | — |
| System (Workflow Engine) | System | Publish approval | — |

---

## 3. Business Story

**Support Agent** Ananya resolves a complex PostgreSQL connection pooling issue for Euphoria Customer *Acme Corp*. She clicks *Promote to Knowledge* on the resolved **Ticket**, pre-filling a draft **Knowledge Article** with symptom, root cause, and resolution steps.

Article enters *Under Review*. **Support Manager** Vikram edits for clarity, sets visibility *Internal + Customer Portal*, assigns category *Database*, and submits for publish. **Workflow Engine** routes approval (single-step Manager publish in v1.5). On *Published*, article KA-1089 is searchable by Agents and Customer Contacts.

Future tickets tagged *Database* show suggested articles. Ananya links KA-1089 to a new ticket in one click. Portal search on *connection pool* returns the article; Customer self-resolves without a new ticket — deflection metric increments.

When product changes, Vikram creates version 2 (draft); version 1 remains in history until v2 is published and v1 is *Archived*.

---

## 4. Business Workflow

```text
Draft Article (manual / from ticket)
   ▼
Edit content + metadata + attachments
   ▼
Submit for Review
   ▼
Manager Review ──reject──► Back to Draft
   │ approve
   ▼
Publish ──► Index for search
   ▼
[Optional] Archive / supersede by new version
```

| Step | Actor | Action | Engine |
|------|-------|--------|--------|
| 1 | Agent | Create draft | API |
| 2 | Agent | Submit review | Workflow |
| 3 | Manager | Approve/reject | Workflow |
| 4 | System | Publish + index | Search (PostgreSQL FTS) |
| 5 | Agent | Link to ticket | SRV-001 |

---

## 5. Business States

| State Code | Label | Next States | Entry Actors |
|------------|-------|-------------|--------------|
| DRAFT | Draft | UNDER_REVIEW, ARCHIVED | Agent |
| UNDER_REVIEW | Under Review | DRAFT, PUBLISHED, REJECTED | Agent submit |
| REJECTED | Rejected | DRAFT | Manager |
| PUBLISHED | Published | ARCHIVED, DRAFT (new version) | Manager |
| ARCHIVED | Archived | — | Manager, Admin |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-SRV-041 | Article title unique per tenant per major version | Validation | Error | DB |
| BR-SRV-042 | Published articles must have category and summary | Validation | Error | API |
| BR-SRV-043 | Customer-visible articles exclude internal-only attachments | Security | Error | API |
| BR-SRV-044 | Only Support Manager may publish | Approval | Error | RBAC, Workflow |
| BR-SRV-045 | Archiving published article removes from portal search index | Lifecycle | — | API |
| BR-SRV-046 | Version increment on substantive body change | Lifecycle | Info | API |
| BR-SRV-047 | Full-text search respects visibility (internal vs external) | Security | Error | API |
| BR-SRV-048 | Promote-from-ticket copies resolution notes as draft body | Calculation | Info | API |
| BR-SRV-049 | Minimum title length 10 characters | Validation | Error | UI, API |
| BR-SRV-050 | Soft-delete only; hard delete prohibited if linked to tickets | Lifecycle | Error | DB |

---

## 7. Database Impact

| Table | Type | Purpose | Tenant Scoped |
|-------|------|---------|---------------|
| knowledge_article | Transaction | Article header + current version pointer | Yes |
| knowledge_article_version | Transaction | Version history | Yes |
| knowledge_category | Master | Category tree | Yes |
| knowledge_article_tag | Link | Tags | Yes |
| ticket_kb_link | Link | Ticket ↔ Article | Yes |
| knowledge_search_log | Audit | Search analytics | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| knowledge_category | knowledge_article | 1:N | Restrict |
| knowledge_article | knowledge_article_version | 1:N | Restrict |
| ticket | ticket_kb_link | 1:N | Restrict |
| knowledge_article | ticket_kb_link | 1:N | Restrict |
| knowledge_article | document (CPS-006) | N:M | Restrict |

---

## 9. Field Groups

### knowledge_article
General (title, slug, summary), Content (body rich text), Classification (category, tags), Visibility (internal, portal, role scope), Version Pointer, Status, SEO (slug, keywords), Audit

### knowledge_article_version
Version Number, Body Snapshot, Change Notes, Author, Published At, Audit

---

## 10. REST APIs

**Base:** `/api/v1/service/knowledge`

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/service/knowledge/articles` | Create draft | `kb.create` |
| GET | `/api/v1/service/knowledge/articles` | List | `kb.read` |
| GET | `/api/v1/service/knowledge/articles/{id}` | Get detail | `kb.read` |
| PUT | `/api/v1/service/knowledge/articles/{id}` | Update draft | `kb.update` |
| POST | `/api/v1/service/knowledge/articles/{id}/submit` | Submit review | `kb.submit` |
| POST | `/api/v1/service/knowledge/articles/{id}/publish` | Publish | `kb.publish` |
| POST | `/api/v1/service/knowledge/articles/{id}/archive` | Archive | `kb.publish` |
| GET | `/api/v1/service/knowledge/articles/search` | Full-text search | `kb.read` |
| POST | `/api/v1/service/knowledge/articles/from-ticket/{ticket_id}` | Promote from ticket | `kb.create` |
| GET | `/api/v1/service/knowledge/categories` | Categories | `kb.read` |
| GET | `/api/v1/service/knowledge/articles/export` | Export | `kb.export` |

**Portal:** `GET /api/v1/service/knowledge/portal/search` — scoped to `visibility=portal`, Customer Contact token.

---

## 11. Flutter Screens

| Screen ID | Screen | Type | Actor |
|-----------|--------|------|-------|
| UI-SRV-003-L | Article List | List | Agent, Manager |
| UI-SRV-003-C | Article Editor | Create/Edit | Agent |
| UI-SRV-003-V | Article Viewer | View | All |
| UI-SRV-003-R | Review Queue | Approval | Manager |
| UI-SRV-003-S | Knowledge Search | Search | Agent, Customer |
| UI-SRV-003-P | Portal KB Home | List/Search | Customer |
| UI-SRV-003-H | Version History | History | Manager |

---

## 12. RBAC Permissions

| Permission | Agent | Manager | Customer | Admin |
|------------|-------|---------|----------|-------|
| `kb.create` | ✓ | ✓ | — | — |
| `kb.read` | ✓ | ✓ | portal only | ✓ |
| `kb.update` | ✓ | ✓ | — | — |
| `kb.submit` | ✓ | ✓ | — | — |
| `kb.publish` | — | ✓ | — | — |
| `kb.configure` | — | — | — | ✓ |
| `kb.export` | — | ✓ | — | ✓ |

---

## 13. Notifications

| Event | Channels | Recipients | Template |
|-------|----------|------------|----------|
| Submitted for Review | In-app | Manager | NTF-SRV-020 |
| Published | In-app | Agents | NTF-SRV-021 |
| Rejected | In-app, Email | Author | NTF-SRV-022 |

---

## 14. Reports

| Report ID | Name | Audience |
|-----------|------|----------|
| RPT-SRV-020 | Top Articles by Views | Manager |
| RPT-SRV-021 | Search Terms No Results | Manager |
| RPT-SRV-022 | Deflection Rate (portal) | Executive |
| RPT-SRV-023 | Article Aging (stale content) | Manager |

---

## 15. Audit Requirements
Create, update, submit, publish, archive, version create, visibility change, export — CPS-005 with article ID and version.

---

## 16. Acceptance Criteria

1. Promote-from-ticket creates draft with ticket resolution text.  
2. Customer search never returns internal-only articles.  
3. Publish requires Manager role (403 for Agent).  
4. Version history shows diff between v1 and v2.  
5. Archived article excluded from portal search.  
6. Tenant isolation on all KB endpoints.

---

## 17. Future Enhancements

| Version | Idea |
|---------|------|
| v2.0 | AI summary and duplicate detection (CPS-007) |
| v2.0 | Multi-language articles |
| v2.5 | Article effectiveness score (ticket deflection linkage) |
| v3.0 | Federated search across MinIO attachments |

---

## Document Control

| Field | Value |
|-------|-------|
| Status | Ready for Field Dictionary authoring |
| Version | 1.0 |
| Owner | PMO / Product Owner |
| Next Action | ELU-FD-SRV, ELU-API-SRV, ELU-UI-SRV |

---

*© Euphoria Infotech (I) Limited — E-LinkUp Service Domain BFS Pack*
