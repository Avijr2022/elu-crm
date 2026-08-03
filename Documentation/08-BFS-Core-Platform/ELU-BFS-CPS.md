# E-LinkUp Business Functional Specification — Core Platform Services Pack
**Document ID:** ELU-BFS-CPS  
**Document Name:** Core Platform Services (CPS) BFS Pack  
**Version:** 1.0  
**Status:** Approved
**Related Documents:** ELU-DOC-001, ELU-DF-001, ELU-BRD-001, ELU-EFS-001, ELU-RTM-001
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Senior BA / Enterprise Solution Architect / Product Owner  
**Document Owner:** PMO  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT + Refresh · Docker · MinIO · Celery/Redis (Phase 3+)  
**Related Documents:** ELU-DF-001, ELU-BRD-001, ELU-SAD-001, ELU-WF-001, ELU-BFS-INT

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP | Initial BFS pack (seventeen sections) |
| 1.0a | 2026-07-31 | EIIP / PMO | Status Approved; registered in ELU-DOC-001; Related Documents standardized |

## Pack Index

| Module ID | Module / Sub Module / Feature | Priority | Phase / Release | Section |
|-----------|-------------------------------|----------|-----------------|---------|
| CPS-001 | Workflow Engine / Workflow Designer | Critical | v1.5 | [§ CPS-001](#module-cps-001--workflow-engine--workflow-designer) |
| CPS-002 | Rule Engine / Rule Configuration | High | v1.5 | [§ CPS-002](#module-cps-002--rule-engine--rule-configuration) |
| CPS-003 | Notification Engine / Multi-Channel Notification | High | v1.5 | [§ CPS-003](#module-cps-003--notification-engine--multi-channel-notification) |
| CPS-004 | Reporting & Analytics / Dashboard & MIS | High | v2.0 | [§ CPS-004](#module-cps-004--reporting--analytics--dashboard--mis) |
| CPS-005 | Audit Service / System Audit | High | v1.5 | [§ CPS-005](#module-cps-005--audit-service--system-audit) |
| CPS-006 | Document Management / Version Control | High | v1.5 | [§ CPS-006](#module-cps-006--document-management--version-control) |
| CPS-007 | AI Assistant / AI Recommendations | Low | v2.0 | [§ CPS-007](#module-cps-007--ai-assistant--ai-recommendations) |
| CPS-008 | Integration Framework / Enterprise Integration | Medium | v2.0 | [§ CPS-008](#module-cps-008--integration-framework--enterprise-integration) |

**API Prefix:** `/api/v1/platform/` (admin/config) · `/api/v1/cps/` (runtime services)  
**Business Rule Prefix:** `BR-CPS-xxx`  
**Note:** CPS modules are **shared engines** consumed by CRM, SAL, PRJ, FIN, SRV, and INT domains.

### Downstream Artefact Index

| Artefact | Document ID |
|----------|-------------|
| Field Dictionary | ELU-FD-CPS-001 … 008 |
| ERD Pack | ELU-ERD-CPS |
| API Specification | ELU-API-CPS |
| Flutter Screen Spec | ELU-UI-CPS |
| Workflow Pack | ELU-WF-CPS |
| Test Case Pack | ELU-TC-CPS |

---

# Module CPS-001 — Workflow Engine / Workflow Designer

**Document ID:** ELU-BFS-CPS-001  
**Module:** CPS-001 — Workflow Engine  
**Sub Module:** CPS-001-001 — Workflow Designer  
**Feature:** CPS-001-001-001 — Workflow Designer  
**Domain:** CPS  
**Priority / Phase / Release:** Critical · v1.5 · Phase 2–3  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Euphoria requires configurable approval and state-transition flows across **Quotation**, **Proposal**, **Invoice**, **Change Request**, **Ticket Escalation**, and **Knowledge Article** publish — without code deployments. The **Workflow Engine** provides tenant-defined definitions, states, transitions, approver resolution, and runtime execution.

### 1.2 Business value
- Business agility: Tenant Admin adjusts flows per policy change  
- Consistent approval pattern platform-wide  
- SLA timers on approval steps (integration with SRV-002 pattern)  
- Audit trail of every transition  

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Visual Workflow Designer (Flutter) | BPMN 2.0 import/export (v3.0) |
| State machine definitions per entity type | Long-running saga compensation |
| Sequential & parallel approval | |
| Approver resolution (role, user, manager) | |
| Runtime workflow instance API | |

### 1.4 Users involved
Tenant Admin, Sales Manager, Finance User, Support Manager, System (Workflow Runtime), all CRM users as approvers.

### 1.5 Module reference
CPS-001 · Workflow Engine · Workflow Designer · Critical · v1.5 · Professional+

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Design/publish workflows | Clone templates |
| Approver (any role) | Internal | Approve/reject/request info | View inbox |
| Requester | Internal | Submit for approval | Track status |
| System (Workflow Runtime) | System | Evaluate transitions, assign tasks | Notify |
| System (Rule Engine) | System | Guard conditions on transitions | — |

---

## 3. Business Story

**Tenant Admin** at Euphoria opens **Workflow Designer** for entity *Quotation*. They define states: Draft → Pending Approval → Approved/Rejected. Transition *Submit* moves Draft to Pending Approval. Approval step resolves approver: **Sales Manager** where `quotation.total_amount` &lt; 500000 INR; else **Sales Manager** + **Finance User** parallel.

**Sales Executive** submits **Quotation** Q-2024-112. Workflow instance WF-INST-8891 starts; tasks appear in Manager and Finance approval inboxes. **Sales Manager** approves; Finance rejects with comment *"Margin below policy"*. Quotation returns to Draft; Notification Engine alerts Executive.

Executive corrects pricing and resubmits. Both approve → Approved. Only then can SAL module convert to **Sales Order** (BR-SAL enforced via workflow completion flag).

---

## 4. Business Workflow

```text
[Design Time]
Tenant Admin: Define workflow_definition (states, transitions, steps)
   ▼
Publish definition (versioned)
   ▼
[Runtime]
Business record event: submit_for_approval
   ▼
Load active workflow for entity_type + tenant
   ▼
Create workflow_instance + approval_tasks
   ▼
Notify approvers (CPS-003)
   ▼
Approver action: approve | reject | request_info
   ▼
Evaluate transition guards (CPS-002)
   ▼
Terminal state OR next step
   ▼
Update business record status + audit (CPS-005)
```

| Step | Actor | Action | Engine |
|------|-------|--------|--------|
| 1 | Tenant Admin | Publish definition | Designer API |
| 2 | Requester | Submit | Domain API → Workflow |
| 3 | Runtime | Create instance | CPS-001 |
| 4 | Approver | Act on task | CPS-001 |
| 5 | System | Complete / reject | CPS-001 + Notification |

---

## 5. Business States

### Workflow Definition
`DRAFT` → `PUBLISHED` → `SUPERSEDED` → `ARCHIVED`

### Workflow Instance
`RUNNING` → `COMPLETED` | `REJECTED` | `CANCELLED`

### Approval Task
`PENDING` → `APPROVED` | `REJECTED` | `DELEGATED` | `EXPIRED`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-CPS-001 | One active published workflow per entity_type per tenant | Validation | Error | DB |
| BR-CPS-002 | Published workflow immutable; changes create new version | Lifecycle | Error | API |
| BR-CPS-003 | Transition requires all parallel approvers when mode=ALL | Approval | Error | Runtime |
| BR-CPS-004 | Reject shall return business record to configured state | Lifecycle | Error | Runtime |
| BR-CPS-005 | Approver cannot approve own submission (segregation) | Security | Error | Runtime |
| BR-CPS-006 | Workflow instance tenant_id must match business record | Security | Error | API |
| BR-CPS-007 | Expired approval task escalates per step config | Lifecycle | Warning | Celery |
| BR-CPS-008 | Cancel instance only by requester or Tenant Admin | Security | Error | API |
| BR-CPS-009 | Entity submit blocked if no published workflow (configurable) | Validation | Warning | Rule Engine |
| BR-CPS-010 | Designer validates graph has single start and ≥1 terminal | Validation | Error | Designer |

---

## 7. Database Impact

| Table | Type | Purpose | Tenant Scoped |
|-------|------|---------|---------------|
| workflow_definition | Master | Definition header | Yes |
| workflow_definition_version | Master | Versioned JSON graph | Yes |
| workflow_state | Master | State catalogue per definition | Yes |
| workflow_transition | Master | Edges + guards | Yes |
| workflow_approval_step | Master | Step config | Yes |
| workflow_instance | Transaction | Runtime instance | Yes |
| workflow_approval_task | Transaction | Per-approver tasks | Yes |
| workflow_instance_history | Audit | Transition log | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| workflow_definition | workflow_definition_version | 1:N | Restrict |
| workflow_instance | workflow_approval_task | 1:N | Cascade |
| workflow_instance | polymorphic business record | N:1 | Restrict |

---

## 9. Field Groups

### workflow_definition
General (name, entity_type), Version Pointer, Status, Description, Audit

### workflow_instance
Definition Version, Business Entity Ref, Current State, Started By, Completed At, Status, Audit

### workflow_approval_task
Instance, Step, Assignee User/Role, Due Date, Action, Comments, Audit

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/platform/workflows/definitions` | Create definition | `workflow.configure` |
| GET | `/api/v1/platform/workflows/definitions` | List | `workflow.read` |
| PUT | `/api/v1/platform/workflows/definitions/{id}` | Save draft graph | `workflow.configure` |
| POST | `/api/v1/platform/workflows/definitions/{id}/publish` | Publish version | `workflow.configure` |
| POST | `/api/v1/cps/workflows/instances` | Start instance (internal) | System / domain |
| GET | `/api/v1/cps/workflows/instances/{id}` | Instance status | `workflow.read` |
| GET | `/api/v1/cps/workflows/tasks/my` | Approval inbox | `workflow.approve` |
| PATCH | `/api/v1/cps/workflows/tasks/{id}` | Approve/reject | `workflow.approve` |
| POST | `/api/v1/cps/workflows/instances/{id}/cancel` | Cancel | `workflow.cancel` |

---

## 11. Flutter Screens

| Screen ID | Screen | Type | Actor |
|-----------|--------|------|-------|
| UI-CPS-001-DES | Workflow Designer | Canvas | Tenant Admin |
| UI-CPS-001-L | Workflow List | List | Tenant Admin |
| UI-CPS-001-INBOX | Approval Inbox | List | Approvers |
| UI-CPS-001-TASK | Approval Task Detail | Action | Approver |
| UI-CPS-001-INST | Instance Timeline | View | Requester |

---

## 12. RBAC Permissions
`workflow.configure`, `workflow.read`, `workflow.approve`, `workflow.cancel` — mapped per role; inbox scoped to assignee.

---

## 13. Notifications

| Event | Channels | Template |
|-------|----------|----------|
| Approval Required | In-app, Email | NTF-CPS-001 |
| Approved | In-app, Email | NTF-CPS-002 |
| Rejected | In-app, Email | NTF-CPS-003 |
| Escalation | In-app, Email | NTF-CPS-004 |

---

## 14. Reports
RPT-CPS-001 Approval Turnaround Time; RPT-CPS-002 Pending Approvals by Role; KPI-CPS-001 Avg Approval Duration.

---

## 15. Audit Requirements
Definition publish, instance start, task action, cancel, delegate — full CPS-005 integration.

---

## 16. Acceptance Criteria

1. Publish workflow blocks invalid graph (no terminal).  
2. Parallel ALL requires both approvers before advance.  
3. Self-approval blocked (403).  
4. Quotation cannot convert to SO until workflow COMPLETED (integration test).  
5. Tenant isolation on definitions and instances.

---

## 17. Future Enhancements

| Version | Idea |
|---------|------|
| v2.0 | Conditional branching on Rule Engine expressions |
| v3.0 | BPMN import, sub-workflows |

---

# Module CPS-002 — Rule Engine / Rule Configuration

**Document ID:** ELU-BFS-CPS-002  
**Module:** CPS-002 — Rule Engine  
**Sub Module:** CPS-002-001 — Rule Configuration  
**Feature:** CPS-002-001-001 — Rule Configuration  
**Domain:** CPS  
**Priority / Phase / Release:** High · v1.5  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Hard-coded business logic (discount limits, ticket routing, tax flags) requires releases for every policy tweak. The **Rule Engine** evaluates tenant-configured rules at runtime for validation, routing, calculations, and workflow guards.

### 1.2 Business value
- Policy changes without deployment  
- Consistent enforcement UI + API + workflow  
- Priority-ordered rule sets with audit  

### 1.3 Business scope
Rule types: Validation, Calculation, Routing, Assignment, Workflow Guard. Expression language: JSON-based conditions (field comparisons, AND/OR). Out of scope: arbitrary Python scripts (v3.0 sandbox).

### 1.4 Users involved
Tenant Admin, System (Rule Evaluator invoked by all domains).

### 1.5 Module reference
CPS-002 · High · v1.5 · Professional+

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Tenant Admin | Internal | Create rule sets, conditions, actions |
| System (Rule Evaluator) | System | Evaluate on API/workflow events |
| Domain Services | System | Invoke evaluator with context payload |

---

## 3. Business Story

Euphoria configures rule *SRV-Ticket-Route-L2*: IF `ticket.category = Application Support` AND `ticket.priority IN (High, Critical)` THEN `assign_queue = L2 Application`. When **Support Agent** creates ticket matching criteria, Rule Engine returns action; ticket API applies assignment before save completes.

Finance rule: IF `quotation.discount_percent > 15` THEN `validation_error = "Manager approval required"`. UI shows warning on save; API returns 422 if workflow not started.

---

## 4. Business Workflow

```text
Tenant Admin defines rule_set (entity, trigger, priority)
   ▼
Add rules: conditions + actions
   ▼
Activate rule_set
   ▼
[Runtime] Domain service calls POST /api/v1/cps/rules/evaluate
   ▼
Evaluator runs rules by priority; first match or accumulate
   ▼
Return actions/errors to caller
```

---

## 5. Business States

Rule Set: `DRAFT` → `ACTIVE` → `ARCHIVED`  
Rule: `ACTIVE` | `INACTIVE`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-CPS-021 | Rule set name unique per tenant per entity | Validation | Error | DB |
| BR-CPS-022 | Active rules evaluated in priority ascending order | Calculation | — | Engine |
| BR-CPS-023 | Validation rules return Error severity block save | Validation | Error | API |
| BR-CPS-024 | Archived rule sets not evaluated | Lifecycle | — | Engine |
| BR-CPS-025 | Rule conditions limited to entity field whitelist | Security | Error | Engine |
| BR-CPS-026 | Evaluation logged when `audit_rules=true` in tenant config | Audit | Info | CPS-005 |
| BR-CPS-027 | Max 200 active rules per entity per tenant | Validation | Warning | Config |
| BR-CPS-028 | Circular rule references prohibited | Validation | Error | Designer |

---

## 7. Database Impact

| Table | Type | Tenant Scoped |
|-------|------|---------------|
| rule_set | Master | Yes |
| rule | Master | Yes |
| rule_condition | Master | Yes |
| rule_action | Master | Yes |
| rule_evaluation_log | Audit | Yes |

---

## 8. Relationships

rule_set 1:N rule 1:N rule_condition/rule_action

---

## 9. Field Groups

rule_set: Entity Type, Trigger Event, Priority, Status, Audit  
rule: Name, Description, Condition Group, Actions JSON, Status

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/platform/rules/sets` | Create set | `rule.configure` |
| GET | `/api/v1/platform/rules/sets` | List | `rule.read` |
| PUT | `/api/v1/platform/rules/sets/{id}` | Update | `rule.configure` |
| POST | `/api/v1/platform/rules/sets/{id}/activate` | Activate | `rule.configure` |
| POST | `/api/v1/cps/rules/evaluate` | Runtime evaluate | Internal JWT |
| GET | `/api/v1/platform/rules/sets/{id}/test` | Test with sample payload | `rule.configure` |

---

## 11. Flutter Screens
UI-CPS-002-L Rule Set List; UI-CPS-002-ED Rule Builder; UI-CPS-002-TEST Rule Tester.

---

## 12. RBAC Permissions
`rule.configure`, `rule.read` — Tenant Admin.

---

## 13. Notifications
NTF-CPS-010 Rule Set Activated (Tenant Admin).

---

## 14. Reports
RPT-CPS-010 Rule Evaluation Volume; RPT-CPS-011 Validation Failures by Rule.

---

## 15. Audit Requirements
Rule set CRUD, activate, archive, evaluation log (optional).

---

## 16. Acceptance Criteria

1. Ticket routing rule assigns correct queue on create.  
2. Discount validation blocks API save.  
3. Inactive rules skipped.  
4. Test endpoint returns expected actions without persisting.  
5. Tenant isolation.

---

## 17. Future Enhancements
v2.0: Visual rule builder; v3.0: Sandboxed script actions.

---

# Module CPS-003 — Notification Engine / Multi-Channel Notification

**Document ID:** ELU-BFS-CPS-003  
**Module:** CPS-003 — Notification Engine  
**Sub Module:** CPS-003-001 — Multi-Channel Notification  
**Feature:** CPS-003-001-001 — Multi-Channel Notification  
**Domain:** CPS  
**Priority / Phase / Release:** High · v1.5  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Every module (CRM, SAL, SRV, Workflow) generates events requiring **Email**, **In-app**, **SMS**, **WhatsApp**, or **Push** delivery. A central **Notification Engine** templates messages, resolves recipients, respects user preferences, and queues delivery via Celery.

### 1.2 Business value
- Single template catalogue (NTF-*)  
- Channel failover and retry  
- User preference compliance  
- Branding per tenant  

### 1.3 Business scope
Template management, event subscription, in-app notification centre, email (SMTP/SendGrid), SMS/WhatsApp (Phase 3+ providers), push (FCM). Out of scope: marketing campaign blast (separate module).

### 1.4 Users involved
Tenant Admin, all CRM Users (recipients), System (Celery dispatchers).

### 1.5 Module reference
CPS-003 · High · v1.5 · All editions (channels edition-gated)

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Tenant Admin | Internal | Configure templates, channels, branding |
| CRM User | Internal | Read/mark notifications | 
| Customer Contact | External | Receive email/SMS (scoped) |
| System (Notification Dispatcher) | System | Queue and send |

---

## 3. Business Story

When **Quotation** is approved, Sales module emits event `quotation.approved` with context. Notification Engine loads template NTF-SAL-003, resolves recipients (Sales Executive owner + Customer Contact if portal enabled), renders variables `{{quotation.number}}`, `{{customer.name}}`.

**Sales Executive** sees in-app bell notification instantly. Email queued via Celery to SMTP. User preference: Executive disabled SMS — SMS skipped (BR-CPS-043). Delivery log records success/failure per channel.

---

## 4. Business Workflow

```text
Domain emits notification event
   ▼
Resolve template + recipients + channels
   ▼
Apply user preferences + quiet hours
   ▼
Render message per channel
   ▼
Celery queue: email | sms | push | in_app
   ▼
Delivery attempt + log
   ▼
Retry on transient failure
```

---

## 5. Business States

Notification: `QUEUED` → `SENT` | `FAILED` | `SKIPPED`  
Template: `DRAFT` → `ACTIVE` → `ARCHIVED`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-CPS-041 | Template key unique per tenant | Validation | Error | DB |
| BR-CPS-042 | Mandatory events cannot be opted out (security) | Security | Error | Engine |
| BR-CPS-043 | User channel preference respected except mandatory | Lifecycle | Info | Engine |
| BR-CPS-044 | Email from address uses tenant branding domain | — | Warning | SMTP |
| BR-CPS-045 | In-app notifications retained 90 days default | Lifecycle | Info | Config |
| BR-CPS-046 | PII in SMS truncated to policy max length | Security | Warning | Template |
| BR-CPS-047 | Quiet hours delay non-critical until window end | Lifecycle | Info | Celery |
| BR-CPS-048 | Failed email retry 3 times | — | — | Celery |

---

## 7. Database Impact

| Table | Type | Tenant Scoped |
|-------|------|---------------|
| notification_template | Master | Yes |
| notification_event_catalogue | Lookup | Platform |
| notification_queue | Transaction | Yes |
| notification_delivery_log | Audit | Yes |
| user_notification_preference | Master | Yes |
| in_app_notification | Transaction | Yes |

---

## 8. Relationships

notification_template linked to event_catalogue; notification_queue → delivery_log

---

## 9. Field Groups

notification_template: Key, Channels, Subject, Body HTML/Text, Variables Schema, Status, Audit

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/platform/notifications/templates` | Create template | `notification.configure` |
| GET | `/api/v1/platform/notifications/templates` | List | `notification.read` |
| POST | `/api/v1/cps/notifications/send` | Internal dispatch | System |
| GET | `/api/v1/cps/notifications/in-app` | User inbox | Authenticated |
| PATCH | `/api/v1/cps/notifications/in-app/{id}/read` | Mark read | Authenticated |
| PUT | `/api/v1/cps/notifications/preferences` | User preferences | Self |
| GET | `/api/v1/platform/notifications/delivery-log` | Admin log | `notification.read` |

---

## 11. Flutter Screens
UI-CPS-003-INBOX Notification Centre; UI-CPS-003-TPL Template Admin; UI-CPS-003-PREF Preferences; UI-CPS-003-LOG Delivery Log.

---

## 12. RBAC Permissions
`notification.configure` (Admin); inbox self-service for all users.

---

## 13. Notifications
Meta: NTF-CPS-050 Delivery Failure Alert to Tenant Admin.

---

## 14. Reports
RPT-CPS-020 Delivery Rate by Channel; RPT-CPS-021 Template Usage.

---

## 15. Audit Requirements
Template changes, preference changes, delivery outcomes.

---

## 16. Acceptance Criteria

1. quotation.approved triggers in-app + email per template.  
2. Disabled SMS channel not sent.  
3. In-app mark-read persists.  
4. Retry on SMTP temporary failure.  
5. Tenant templates isolated.

---

## 17. Future Enhancements
v2.0: WhatsApp Business API; v2.5: A/B template testing.

---

# Module CPS-004 — Reporting & Analytics / Dashboard & MIS

**Document ID:** ELU-BFS-CPS-004  
**Module:** CPS-004 — Reporting & Analytics  
**Sub Module:** CPS-004-001 — Dashboard & MIS  
**Feature:** CPS-004-001-001 — Dashboard & MIS  
**Domain:** CPS  
**Priority / Phase / Release:** High · v2.0  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Module-specific reports (SRV, FIN, CRM) need a unified **Dashboard & MIS** layer: executive KPIs, drill-down, scheduled report delivery, and widget-based home screens for Euphoria leadership.

### 1.2 Business value
- Single pane for pipeline, revenue, projects, SLA  
- Role-based dashboards  
- Export and scheduled email reports  

### 1.3 Business scope
Dashboard designer, widget library, report scheduler, data export. Out of scope: full data warehouse ETL (external BI connector v3.0).

### 1.4 Users involved
Tenant Admin, Sales Manager, Finance User, Support Manager, Executive (read).

### 1.5 Module reference
CPS-004 · High · v2.0 · Professional+ (Executive widgets Enterprise)

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Tenant Admin | Internal | Configure dashboards, schedules |
| Sales Manager | Internal | View sales MIS |
| Executive | Internal | View KPI dashboard |
| System (Report Scheduler) | System | Celery report jobs |

---

## 3. Business Story

**Sales Manager** opens Euphoria home dashboard: widgets for Open Pipeline, Won This Quarter, Quotation Aging. Clicks pipeline widget → drills to Opportunity list filtered by stage. **Tenant Admin** schedules weekly PDF *Executive Summary* emailed Monday 08:00 to leadership distribution list.

---

## 4. Business Workflow

```text
Admin assigns dashboard to role
   ▼
User opens home → widgets load via report queries
   ▼
Drill-down navigates to domain list screens
   ▼
[Scheduled] Celery generates export → email via CPS-003
```

---

## 5. Business States

Dashboard: `DRAFT` → `PUBLISHED`  
Report Schedule: `ACTIVE` | `PAUSED`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-CPS-061 | Widget queries tenant-scoped only | Security | Error | Query layer |
| BR-CPS-062 | Export row limit 100k default | Performance | Warning | API |
| BR-CPS-063 | Scheduled reports require active email template | Validation | Error | API |
| BR-CPS-064 | Dashboard visibility by role assignment | Security | Error | RBAC |
| BR-CPS-065 | Cached widget TTL 5 minutes default | Performance | Info | Redis |

---

## 7. Database Impact

| Table | Type | Tenant Scoped |
|-------|------|---------------|
| dashboard | Master | Yes |
| dashboard_widget | Master | Yes |
| report_definition | Master | Yes |
| report_schedule | Master | Yes |
| report_run_log | Audit | Yes |

---

## 8. Relationships

dashboard 1:N dashboard_widget; report_schedule → report_definition

---

## 9. Field Groups

dashboard: Name, Role Assignments, Layout JSON, Status  
dashboard_widget: Type, Query Ref, Config, Position

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| GET | `/api/v1/platform/dashboards` | List | `dashboard.read` |
| POST | `/api/v1/platform/dashboards` | Create | `dashboard.configure` |
| GET | `/api/v1/cps/dashboards/home` | User home dashboard | Authenticated |
| GET | `/api/v1/cps/reports/{id}/run` | Execute report | `report.run` |
| GET | `/api/v1/cps/reports/{id}/export` | Export | `report.export` |
| POST | `/api/v1/platform/reports/schedules` | Schedule | `report.configure` |

---

## 11. Flutter Screens
UI-CPS-004-HOME Home Dashboard; UI-CPS-004-DES Dashboard Designer; UI-CPS-004-RPT Report Viewer; UI-CPS-004-SCH Schedule Admin.

---

## 12. RBAC Permissions
`dashboard.configure`, `dashboard.read`, `report.run`, `report.export`, `report.configure`

---

## 13. Notifications
NTF-CPS-060 Scheduled Report Ready (email attachment).

---

## 14. Reports
Built-in: KPI-CPS-010 Platform Adoption; domain widgets reference RPT-* catalogues from CRM/SAL/FIN/SRV.

---

## 15. Audit Requirements
Dashboard publish, report run, export, schedule changes.

---

## 16. Acceptance Criteria

1. Sales Manager home shows only assigned widgets.  
2. Drill-down opens filtered Opportunity list.  
3. Scheduled report emails on cron.  
4. Export respects row limit with warning.  
5. No cross-tenant data in widgets.

---

## 17. Future Enhancements
v2.5: Custom SQL reports (read replica); v3.0: Power BI connector.

---

# Module CPS-005 — Audit Service / System Audit

**Document ID:** ELU-BFS-CPS-005  
**Module:** CPS-005 — Audit Service  
**Sub Module:** CPS-005-001 — System Audit  
**Feature:** CPS-005-001-001 — System Audit  
**Domain:** CPS  
**Priority / Phase / Release:** High · v1.5  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Enterprise customers require immutable **audit trails** for compliance, dispute resolution, and security forensics. Central **Audit Service** captures create/update/delete/status/approval/export events from all modules with actor, timestamp, and change detail.

### 1.2 Business value
- SOX-ready activity history  
- Tenant-configurable retention  
- Searchable audit explorer for Tenant Admin  

### 1.3 Business scope
Append-only audit_log, entity history API, export. Out of scope: SIEM streaming (v2.5).

### 1.4 Users involved
Tenant Admin, Platform Admin (aggregate metrics only), System (all modules write audit events).

### 1.5 Module reference
CPS-005 · High · v1.5 · All editions (retention edition-gated)

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Tenant Admin | Internal | Search audit, export |
| Platform Admin | Internal | Platform-level security audit (no tenant PII) |
| Domain Services | System | Emit audit events |
| System (Audit Writer) | System | Persist append-only log |

---

## 3. Business Story

**Finance User** modifies issued **Invoice** via credit note flow — direct edit blocked, but approval audit still required. Every field change on draft entities logs to `audit_log` with JSON diff. **Tenant Admin** searches audit for `entity_type=ticket` and `actor=user:raj` last 30 days for investigation. Retention job archives logs older than 365 days to cold storage (MinIO) per Euphoria policy.

---

## 4. Business Workflow

```text
Domain service completes mutation
   ▼
Build audit_event (actor, entity, action, diff)
   ▼
POST internal /api/v1/cps/audit/events (async)
   ▼
Append to audit_log (no update/delete)
   ▼
[Optional] Archive job per retention policy
```

---

## 5. Business States

Audit records are **immutable** — no state machine. Archive flag: `ACTIVE` → `ARCHIVED`.

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-CPS-081 | Audit log append-only; UPDATE/DELETE prohibited | Security | Error | DB triggers |
| BR-CPS-082 | Every audit record includes tenant_id, actor_id, timestamp UTC | Validation | Error | Writer |
| BR-CPS-083 | Sensitive fields masked in diff (password, secret) | Security | Error | Writer |
| BR-CPS-084 | Export audit requires `audit.export` permission | Security | Error | RBAC |
| BR-CPS-085 | Retention minimum 90 days (tenant override) | Compliance | Error | Config |
| BR-CPS-086 | Platform Admin cannot read tenant business audit PII | Security | Error | RBAC |

---

## 7. Database Impact

| Table | Type | Tenant Scoped |
|-------|------|---------------|
| audit_log | Audit | Yes |
| audit_log_archive | Audit | Yes |
| audit_retention_policy | Master | Yes |

---

## 8. Relationships

Polymorphic: audit_log → any entity via entity_type + entity_id

---

## 9. Field Groups

audit_log: Actor, Action, Entity Ref, Old Values JSON, New Values JSON, IP Address, User Agent, Correlation ID, Timestamp

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/cps/audit/events` | Write event (internal) | System |
| GET | `/api/v1/cps/audit/logs` | Search | `audit.read` |
| GET | `/api/v1/cps/audit/logs/{id}` | Detail | `audit.read` |
| GET | `/api/v1/cps/audit/entities/{type}/{id}` | Entity history | `audit.read` |
| GET | `/api/v1/cps/audit/export` | Export | `audit.export` |

---

## 11. Flutter Screens
UI-CPS-005-SRCH Audit Search; UI-CPS-005-ENT Entity History Tab (embedded); UI-CPS-005-EXP Export.

---

## 12. RBAC Permissions
`audit.read`, `audit.export` — Tenant Admin, compliance roles.

---

## 13. Notifications
NTF-CPS-080 Large Export Ready (async).

---

## 14. Reports
RPT-CPS-050 Audit Volume by Module; RPT-CPS-051 Security Events Summary.

---

## 15. Audit Requirements
Meta-audit: audit export and search actions themselves logged.

---

## 16. Acceptance Criteria

1. Ticket status change creates audit row with old/new status.  
2. audit_log table rejects UPDATE/DELETE.  
3. Secrets never appear in diff JSON.  
4. Entity history returns chronological list.  
5. Tenant isolation on search.

---

## 17. Future Enhancements
v2.5: SIEM webhook streaming; v3.0: Blockchain anchoring (optional).

---

# Module CPS-006 — Document Management / Version Control

**Document ID:** ELU-BFS-CPS-006  
**Module:** CPS-006 — Document Management  
**Sub Module:** CPS-006-001 — Version Control  
**Feature:** CPS-006-001-001 — Version Control  
**Domain:** CPS  
**Priority / Phase / Release:** High · v1.5  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
**Proposal**, **Contract**, **Ticket attachment**, and **Project deliverable** files require secure storage, versioning, and access control. **Document Management** uses **MinIO** object storage with PostgreSQL metadata and version history.

### 1.2 Business value
- Single attachment service for all modules  
- Version rollback and compare metadata  
- Virus scan hook (Phase 3+)  
- Presigned URL secure download  

### 1.3 Business scope
Upload, download, version, link to business entities, folder taxonomy. Out of scope: In-browser collaborative editing (v3.0).

### 1.4 Users involved
All CRM users (scoped), Customer Contact (portal attachments), System (MinIO).

### 1.5 Module reference
CPS-006 · High · v1.5 · All editions (quota edition-gated)

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Sales Executive | Internal | Upload proposal documents |
| Project Manager | Internal | Deliverable versions |
| Support Agent | Internal | Ticket attachments |
| Customer Contact | External | Portal upload/download |
| System (MinIO) | System | Object storage |

---

## 3. Business Story

**Pre-Sales** uploads Proposal v1 PDF to **Opportunity** OP-445. System stores blob in MinIO bucket `euphoria-tenant-{uuid}`, metadata in `document` + `document_version`. v2 upload creates version 2; v1 retained. **Sales Manager** downloads approved version via presigned URL expiring 15 minutes (BR-CPS-105). Ticket attachment inherits visibility: internal vs customer-visible.

---

## 4. Business Workflow

```text
Client requests upload URL (or multipart POST)
   ▼
API validates size/type/quota
   ▼
Store in MinIO; write document_version
   ▼
Link to business entity (polymorphic)
   ▼
Download via presigned GET
   ▼
New version increments version_no
```

---

## 5. Business States

Document: `ACTIVE` → `ARCHIVED`  
Version: `CURRENT` | `SUPERSEDED`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-CPS-101 | Max file size 50 MB default (tenant config) | Validation | Error | API |
| BR-CPS-102 | Allowed MIME whitelist per tenant | Security | Error | API |
| BR-CPS-103 | Presigned URL TTL max 60 minutes | Security | Error | MinIO |
| BR-CPS-104 | Soft-delete document hides from lists; blob retained until purge job | Lifecycle | Info | API |
| BR-CPS-105 | Customer Contact download only customer-visible documents | Security | Error | RBAC |
| BR-CPS-106 | Storage quota per tenant enforced | Validation | Error | Edition |
| BR-CPS-107 | Version number monotonic per document | Calculation | Error | DB |

---

## 7. Database Impact

| Table | Type | Tenant Scoped |
|-------|------|---------------|
| document | Master | Yes |
| document_version | Transaction | Yes |
| document_link | Link | Yes |
| document_folder | Master | Yes |

---

## 8. Relationships

document 1:N document_version; document_link → polymorphic entity

---

## 9. Field Groups

document: Title, Folder, Visibility, Current Version, Tags, Audit  
document_version: File Name, MIME, Size, Storage Key, Checksum, Uploaded By

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/cps/documents/upload` | Upload | `document.create` |
| GET | `/api/v1/cps/documents/{id}` | Metadata | `document.read` |
| GET | `/api/v1/cps/documents/{id}/download` | Presigned URL | `document.read` |
| POST | `/api/v1/cps/documents/{id}/versions` | New version | `document.update` |
| GET | `/api/v1/cps/documents/{id}/versions` | Version list | `document.read` |
| POST | `/api/v1/cps/documents/link` | Link to entity | `document.update` |
| DELETE | `/api/v1/cps/documents/{id}` | Soft delete | `document.delete` |

---

## 11. Flutter Screens
UI-CPS-006-BRW Document Browser; UI-CPS-006-UPL Upload Widget; UI-CPS-006-VER Version History; embedded tab on Opportunity/Project/Ticket.

---

## 12. RBAC Permissions
`document.create`, `document.read`, `document.update`, `document.delete` — entity-scoped.

---

## 13. Notifications
NTF-CPS-100 Document Shared with Customer.

---

## 14. Reports
RPT-CPS-060 Storage Usage by Tenant; RPT-CPS-061 Upload Activity.

---

## 15. Audit Requirements
Upload, download, version, delete, visibility change — CPS-005.

---

## 16. Acceptance Criteria

1. Upload stores file retrievable via presigned URL.  
2. v2 upload preserves v1.  
3. Oversize file rejected.  
4. Customer cannot download internal-only doc.  
5. Quota exceeded returns 413.

---

## 17. Future Enhancements
v2.0: OCR text index; v3.0: Collaborative editing integration.

---

# Module CPS-007 — AI Assistant / AI Recommendations

**Document ID:** ELU-BFS-CPS-007  
**Module:** CPS-007 — AI Assistant  
**Sub Module:** CPS-007-001 — AI Recommendations  
**Feature:** CPS-007-001-001 — AI Recommendations  
**Domain:** CPS  
**Priority / Phase / Release:** Low · v2.0  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
Optional **AI Assistant** accelerates CRM user productivity: suggest next best action on **Opportunity**, categorise **Ticket**, summarise **Activity** timeline, recommend **Knowledge Articles**. Low priority Phase 4 enhancement — must not block core flows.

### 1.2 Business value
- Reduced time on data entry and search  
- Assisted decision support (human-in-the-loop)  
- Tenant-controlled enable/disable  

### 1.3 Business scope
Recommendation API, chat assistant sidebar, prompt templates, usage metering. Out of scope: autonomous actions without user confirmation.

### 1.4 Users involved
Sales Executive, Support Agent, Tenant Admin (enable/configure), System (LLM provider adapter).

### 1.5 Module reference
CPS-007 · Low · v2.0 · Enterprise optional add-on

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Sales Executive | Internal | Request recommendations, accept/dismiss |
| Support Agent | Internal | KB suggestions, ticket categorisation assist |
| Tenant Admin | Internal | Enable AI, set data boundaries |
| System (AI Provider) | External | LLM inference (Azure OpenAI / configurable) |

---

## 3. Business Story

**Support Agent** opens new **Ticket**; AI panel suggests category *Database* and articles KA-1089, KA-1042 with confidence scores. Agent accepts suggestion — fields pre-filled (editable before save). **Sales Executive** asks assistant *"Summarise Acme Corp opportunities this quarter"* — returns narrative from permitted data only (BR-CPS-125). No auto-send to customer without explicit user action.

---

## 4. Business Workflow

```text
User opens entity / chat panel
   ▼
Check tenant AI enabled + user permission
   ▼
Gather context (scoped fields only)
   ▼
Call LLM adapter with prompt template
   ▼
Return suggestions (not auto-persisted)
   ▼
User accepts → apply to form
   ▼
Log usage + audit prompt hash (not full PII)
```

---

## 5. Business States

AI Feature Toggle: `DISABLED` → `ENABLED`  
Recommendation: `SUGGESTED` → `ACCEPTED` | `DISMISSED`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-CPS-121 | AI disabled by default per tenant | Security | — | Config |
| BR-CPS-122 | No PII sent to LLM without Tenant Admin opt-in | Security | Error | Adapter |
| BR-CPS-123 | AI cannot auto-approve workflows or send notifications | Security | Error | API |
| BR-CPS-124 | User must confirm before AI changes persisted | Lifecycle | Error | UI |
| BR-CPS-125 | Context limited to records user can read (RBAC) | Security | Error | API |
| BR-CPS-126 | Usage metered per tenant monthly token budget | — | Warning | Config |

---

## 7. Database Impact

| Table | Type | Tenant Scoped |
|-------|------|---------------|
| ai_tenant_config | Master | Yes |
| ai_prompt_template | Master | Platform/tenant |
| ai_recommendation_log | Audit | Yes |
| ai_usage_meter | Audit | Yes |

---

## 8. Relationships

ai_recommendation_log → polymorphic entity; optional link to knowledge_article

---

## 9. Field Groups

ai_tenant_config: Enabled Flag, Provider, Model, Token Budget, PII Policy, Audit

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| GET | `/api/v1/platform/ai/config` | Tenant config | `ai.configure` |
| PUT | `/api/v1/platform/ai/config` | Update config | `ai.configure` |
| POST | `/api/v1/cps/ai/recommend` | Get recommendations | `ai.use` |
| POST | `/api/v1/cps/ai/chat` | Assistant chat | `ai.use` |
| POST | `/api/v1/cps/ai/feedback` | Thumbs up/down | `ai.use` |

---

## 11. Flutter Screens
UI-CPS-007-PANEL AI Side Panel; UI-CPS-007-CHAT Assistant Chat; UI-CPS-007-CFG Admin Config.

---

## 12. RBAC Permissions
`ai.configure` (Admin), `ai.use` (licensed roles).

---

## 13. Notifications
NTF-CPS-120 Token Budget 80% Warning (Tenant Admin).

---

## 14. Reports
RPT-CPS-070 AI Usage by Feature; RPT-CPS-071 Recommendation Acceptance Rate.

---

## 15. Audit Requirements
Config change, recommend calls (metadata), accept/dismiss, feedback.

---

## 16. Acceptance Criteria

1. Disabled tenant returns 403 on AI endpoints.  
2. Suggestions not saved until user accepts.  
3. RBAC: user cannot get AI context for inaccessible Opportunity.  
4. No automatic customer emails from AI.  
5. Usage meter increments per call.

---

## 17. Future Enhancements
v2.5: Fine-tuned tenant models; v3.0: Voice assistant on Android.

---

# Module CPS-008 — Integration Framework / Enterprise Integration

**Document ID:** ELU-BFS-CPS-008  
**Module:** CPS-008 — Integration Framework  
**Sub Module:** CPS-008-001 — Enterprise Integration  
**Feature:** CPS-008-001-001 — Enterprise Integration  
**Domain:** CPS  
**Priority / Phase / Release:** Medium · v2.0  
**Example Tenant:** Euphoria

---

## 1. Business Objective

### 1.1 Why this module exists
**INT-004 Connectors**, webhooks, and future sync jobs need shared runtime: HTTP client pooling, retry, circuit breaker, transformation pipeline, and credential injection. **Integration Framework** is the execution layer behind Integration domain features.

### 1.2 Business value
- DRY integration infrastructure  
- Observable sync pipelines  
- Standard error taxonomy for operators  

### 1.3 Business scope
Job orchestration, transform pipeline, connector SDK contract, dead-letter handling. Consumed by INT-* modules.

### 1.4 Users involved
Tenant Admin, System (Celery workers), INT-004 Connector instances.

### 1.5 Module reference
CPS-008 · Medium · v2.0 · Enterprise

---

## 2. Business Actors

| Actor | Type | Primary Actions |
|-------|------|-----------------|
| Tenant Admin | Internal | Monitor integration health |
| System (Integration Runtime) | System | Execute connector/sync jobs |
| Connector Instance | System | INT-004 configured jobs |

---

## 3. Business Story

When Euphoria's Zoho connector runs (INT-004), CPS-008 loads instance config, decrypts credentials, acquires distributed lock, executes Extract-Transform-Load steps, records per-record outcomes, releases lock. On repeated HTTP 503 from Zoho, circuit breaker opens for 5 minutes (BR-CPS-145) preventing cascade failures.

---

## 4. Business Workflow

```text
Trigger (schedule / manual / event)
   ▼
CPS-008 job runner picks job
   ▼
Load connector config + credentials
   ▼
Acquire Redis lock
   ▼
For each record: extract → transform → load
   ▼
Log outcome; update watermark
   ▼
Release lock; emit metrics
   ▼
On failure: retry / circuit breaker / dead letter
```

---

## 5. Business States

Job: `QUEUED` → `RUNNING` → `COMPLETED` | `FAILED`  
Circuit Breaker: `CLOSED` → `OPEN` → `HALF_OPEN`

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-CPS-141 | One concurrent run per connector instance | Concurrency | Error | Redis |
| BR-CPS-142 | HTTP timeout default 30s per external call | Performance | — | Runtime |
| BR-CPS-143 | Retry max 3 with exponential backoff | Lifecycle | — | Runtime |
| BR-CPS-144 | Dead-letter after exhausted retries | Lifecycle | — | Runtime |
| BR-CPS-145 | Circuit breaker opens after 5 failures in 1 min | Performance | Warning | Runtime |
| BR-CPS-146 | All external calls logged with correlation_id | Audit | Info | CPS-005 |
| BR-CPS-147 | Transform errors skip record, continue batch | — | Warning | Runtime |

---

## 7. Database Impact

| Table | Type | Tenant Scoped |
|-------|------|---------------|
| integration_job | Transaction | Yes |
| integration_job_step_log | Audit | Yes |
| integration_circuit_state | Master | Yes |
| integration_dead_letter | Audit | Yes |

---

## 8. Relationships

integration_job → connector_instance (INT-004); integration_job 1:N step_log

---

## 9. Field Groups

integration_job: Connector Ref, Trigger Type, Status, Started/Completed, Records Processed, Error Summary

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| GET | `/api/v1/cps/integration/jobs` | List jobs | `integration.read` |
| GET | `/api/v1/cps/integration/jobs/{id}` | Job detail | `integration.read` |
| POST | `/api/v1/cps/integration/jobs/{id}/retry` | Retry failed | `integration.admin` |
| GET | `/api/v1/cps/integration/health` | Circuit/queue health | `integration.read` |
| GET | `/api/v1/cps/integration/dead-letters` | Dead letter queue | `integration.admin` |

---

## 11. Flutter Screens
UI-CPS-008-MON Integration Monitor; UI-CPS-008-JOB Job Detail; UI-CPS-008-DLQ Dead Letter Queue.

---

## 12. RBAC Permissions
`integration.read`, `integration.admin` — Tenant Admin.

---

## 13. Notifications
NTF-CPS-140 Integration Job Failed; NTF-CPS-141 Circuit Breaker Open.

---

## 14. Reports
RPT-CPS-080 Integration Success Rate; RPT-CPS-081 External API Latency.

---

## 15. Audit Requirements
Job start/complete, retry, dead-letter replay, circuit state changes.

---

## 16. Acceptance Criteria

1. Concurrent manual+scheduled sync blocked by lock.  
2. Retry occurs on 503; circuit opens after threshold.  
3. Dead-letter visible and replayable.  
4. Correlation ID in logs matches INT-004 UI.  
5. Tenant job isolation.

---

## 17. Future Enhancements
v2.5: Visual pipeline designer; v3.0: Event-driven streaming integrations.

---

## Cross-Module Engine Consumption Matrix

| Engine | CRM | SAL | PRJ | FIN | SRV | INT |
|--------|-----|-----|-----|-----|-----|-----|
| CPS-001 Workflow | Opportunity approval | Quotation, Proposal | CR approval | Invoice approval | KB publish, escalation | — |
| CPS-002 Rules | Lead scoring | Discount validation | — | Tax flags | Ticket routing | Webhook filter |
| CPS-003 Notifications | All lifecycle | All lifecycle | Milestone | Invoice/dunning | Ticket/SLA | Failures |
| CPS-004 Reports | Pipeline widgets | Sales MIS | Project health | Revenue | SLA dashboard | API usage |
| CPS-005 Audit | All entities | All entities | All entities | All entities | All entities | All entities |
| CPS-006 Documents | Proposals | Contracts | Deliverables | Invoice PDF | Attachments | — |
| CPS-007 AI | Lead insights | — | — | — | KB suggest | — |
| CPS-008 Integration | — | ERP sync | — | Accounting | — | Connectors |

---

## Document Control

| Field | Value |
|-------|-------|
| Status | Ready for Field Dictionary and API authoring |
| Version | 1.0 |
| Owner | PMO / Solution Architecture |
| Dependencies | PF (Tenant, RBAC), Redis/Celery Phase 3+ |

---

*© Euphoria Infotech (I) Limited — E-LinkUp Core Platform Services BFS Pack*
