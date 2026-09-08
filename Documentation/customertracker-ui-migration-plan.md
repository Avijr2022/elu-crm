# CustomerTracker UI Migration Plan

> **Superseded for implementation decisions by** [customertracker-ui-reuse-assessment.md](customertracker-ui-reuse-assessment.md) (2026-09-01). This document remains as historical context.

## Purpose

This document translates the CRM gap analysis into a prioritized UI migration plan for the current Frontend. It uses the existing Flutter Frontend as the implementation foundation and uses the approved CRM documentation as the source of truth. It does not change production code; it defines the intended migration sequence and the frontend areas that should evolve.

---

## 1. Migration Principles

1. Reuse the current Frontend architecture.
   - Keep the existing feature-based Flutter structure and service/controller boundaries.

2. Reuse CustomerTracker only at the UX pattern level.
   - Borrow interaction patterns, information hierarchy, visual rhythm, and form conventions.
   - Do not copy the legacy app as a direct implementation basis.

3. Align every UI effort to the approved CRM documentation.
   - Use the documented routes, modules, roles, and workflow states as the target model.

4. Prefer phased delivery.
   - Start with the core CRM journey (lead → opportunity → customer) before broader reporting and admin surfaces.

5. Keep the migration API-backed.
   - The UI should reflect the current and planned Backend and Database contracts rather than mock-only screens.

---

## 2. Migration Priorities

### Phase 1 — Foundation and core CRM UX

Focus areas:

- authentication experience
- app shell and CRM navigation
- lead list/detail lifecycle
- opportunity pipeline/detail lifecycle

### Phase 2 — Customer and activity experience

Focus areas:

- customer and account management UX
- activity timeline and task flows
- follow-up and calendar-oriented views

### Phase 3 — Admin, reporting, and downstream surfaces

Focus areas:

- CRM settings/admin pages
- dashboard and reporting screens
- quotation/invoice references in later sales/finance integration

---

## 3. Detailed UI Migration Plan

### 1. Authentication experience

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Login experience | Frontend/lib/features/platform/presentation/login_page.dart | login form and recovery concepts | Frontend/lib/features/platform/presentation/login_page.dart | Improve tenant-aware, role-aware sign-in UX | Auth API | user/tenant/platform tables | Modify | High | Medium |

#### Notes

- Reuse the general layout and field structure from CustomerTracker.
- Upgrade the experience to reflect CRM branding, tenant context, and role-based landing behavior.

---

### 2. App shell and CRM navigation

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Main app shell | Frontend/lib/features/platform/presentation/home_page.dart | drawer and shell navigation pattern | Frontend/lib/features/platform/presentation/home_page.dart | Provide first-class CRM navigation to leads, opportunities, customers, activities, and settings | Auth/profile + RBAC context | tenant/user/role tables | Modify | High | Medium |
| Navigation structure | Frontend/lib/features/platform/presentation/home_page.dart | section organization, icon grouping | Frontend/lib/features/platform/presentation/home_page.dart | Align navigation with documented CRM routes and module ownership | profile/RBAC | tenant/user/role tables | Rebuild | High | Medium |

#### Notes

- This is the highest-impact structural change because it affects how users access the CRM experience.
- The navigation should be role-aware and edition-aware rather than a static list.

---

### 3. Dashboard and landing experience

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Home/dashboard | Frontend/lib/features/platform/presentation/home_page.dart | dashboard cards and summary panels | Frontend/lib/features/platform/presentation/home_page.dart | Provide CRM and platform summary views | dashboard/reporting endpoints | CRM and platform entities | Rebuild | Medium | Medium |

#### Notes

- The landing experience should move from a general platform shell to a CRM-ready dashboard with role-based summaries.
- The first dashboard iteration can focus on lead, opportunity, and activity status summaries.

---

### 4. Lead management UX

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Lead list | Frontend/lib/features/crm/presentation/leads_page.dart | lead list and search patterns | Frontend/lib/features/crm/presentation/leads_page.dart | Show lead list with filters, owner, status, and actions | /api/v1/crm/leads | crm_lead, lead_contact | Modify | High | Medium |
| Lead create form | Frontend/lib/features/crm/presentation/lead_form_dialog.dart | create form structure | Frontend/lib/features/crm/presentation/lead_form_dialog.dart | Support documented lead fields and validation | /api/v1/crm/leads | crm_lead, lead_contact | Modify | High | Medium |
| Lead detail experience | New/expanded detail route under CRM | profile/detail and timeline patterns | Frontend/lib/features/crm/presentation/ | Support detailed lead lifecycle and embedded activity timeline | lead detail + activity endpoints | lead, lead_contact, activity_link | Rebuild | High | High |
| Lead qualification/disqualification | Not yet surfaced | action dialog patterns | Frontend/lib/features/crm/presentation/ | Support lead lifecycle transitions | /qualify, /disqualify, /assign | lead state fields | Rebuild | High | High |
| Lead conversion wizard | Current simple conversion flow | wizard and guided action pattern | Frontend/lib/features/crm/presentation/ | Support conversion to customer/opportunity per documentation | /convert | lead, customer, opportunity | Rebuild | High | High |

#### Notes

- The current lead implementation should evolve from a simple list/create experience into a lifecycle-oriented CRM UI.
- The lead detail view should embed an activity timeline and show state-aware actions.

---

### 5. Opportunity management UX

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Opportunity list | Frontend/lib/features/crm/presentation/opportunities_page.dart | card/list and action patterns | Frontend/lib/features/crm/presentation/opportunities_page.dart | Show opportunity records and stage progression | /api/v1/crm/opportunities | crm_opportunity | Modify | High | Medium |
| Opportunity create form | Frontend/lib/features/crm/presentation/opportunity_form_dialog.dart | form composition | Frontend/lib/features/crm/presentation/opportunity_form_dialog.dart | Capture documented opportunity fields | /api/v1/crm/opportunities | crm_opportunity | Modify | High | Medium |
| Opportunity detail | New/expanded detail route under CRM | detail view and action cards | Frontend/lib/features/crm/presentation/ | Support detailed opportunity flow and linked customer/activities | opportunity detail + activities | opportunity, customer, activity_link | Rebuild | High | High |
| Pipeline view | Not yet surfaced | kanban-style pipeline concepts | Frontend/lib/features/crm/presentation/ | Provide pipeline view per CRM documentation | /opportunities/pipeline | crm_opportunity | Rebuild | High | High |
| Close won / lost wizard | Not yet surfaced | action wizard pattern | Frontend/lib/features/crm/presentation/ | Support close lifecycle actions | /close-won, /close-lost | opportunity | Rebuild | Medium | High |

#### Notes

- The current opportunity UI is a good starting point, but it still requires stronger stage and lifecycle UX.
- The pipeline view should be treated as a core migration target rather than a later nice-to-have.

---

### 6. Customer and account management UX

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Customer list | Not yet implemented as CRM customer module | profile list and account patterns | Frontend/lib/features/crm/presentation/ | Provide a customer/account list view | /api/v1/crm/customers | customer tables | Rebuild | High | High |
| Customer detail | Not yet implemented | profile/detail and tabs | Frontend/lib/features/crm/presentation/ | Support customer profile, contacts, addresses, and linked deals | customer detail + 360 endpoints | customer, customer_contact, customer_address | Rebuild | High | High |
| Customer 360 view | Not yet implemented | dashboard and summary panels | Frontend/lib/features/crm/presentation/ | Surface activity, opportunities, quotation references, and account health | /{id}/360 | customer + linked entities | Rebuild | High | High |
| Contact manager | Not yet implemented | contact cards and profile forms | Frontend/lib/features/crm/presentation/ | Manage customer contacts and lead contacts | customer/lead contact endpoints | customer_contact, lead_contact | Rebuild | High | High |
| Address manager | Not yet implemented | profile/address card patterns | Frontend/lib/features/crm/presentation/ | Support registered/billing/shipping addresses | customer address endpoints | customer_address | Rebuild | Medium | High |

#### Notes

- This is one of the largest missing areas compared to the CRC requirements.
- It should be introduced as a new CRM feature package rather than as a thin patch over the existing platform organization page.

---

### 7. Activity timeline and task UX

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Activity timeline widget | Not yet implemented | timeline and event-style patterns | Frontend/lib/features/crm/presentation/ | Embed activity history into lead/opportunity/customer detail | /activities/timeline and entity shortcuts | activity, activity_link | Rebuild | High | High |
| Log activity dialog | Not yet implemented | modal action pattern | Frontend/lib/features/crm/presentation/ | Support logging calls, meetings, tasks, and notes | /api/v1/crm/activities | activity | Rebuild | High | High |
| My activities / upcoming / overdue | Not yet implemented | task and task-list patterns | Frontend/lib/features/crm/presentation/ | Support activity ownership and follow-ups | /activities/my, /upcoming, /overdue | activity | Rebuild | High | High |

#### Notes

- This is core to the documented CRM experience and should be treated as one of the early migration targets.
- The activity timeline should appear as an embedded component on the lead, opportunity, and customer detail screens.

---

### 8. Follow-up and calendar UX

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Follow-up list and reminders | Not yet implemented | follow-up card pattern | Frontend/lib/features/crm/presentation/ | Show overdue and upcoming follow-up items | activity endpoints | activity | Rebuild | Medium | Medium |
| Calendar view | Not yet implemented | calendar/list pattern | Frontend/lib/features/crm/presentation/ | Surface upcoming meetings and tasks | /activities/upcoming | activity | Rebuild | Medium | Medium |

#### Notes

- Follow-up and calendar views should be integrated into the activity experience rather than built as isolated modules.

---

### 9. CRM admin and settings UX

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Lead source admin | Not yet implemented | admin list/form patterns | Frontend/lib/features/crm/presentation/ | Manage lead sources | /api/v1/crm/lead-sources | lead_source tables | Rebuild | Medium | Medium |
| Opportunity stage admin | Not yet implemented | admin list/form patterns | Frontend/lib/features/crm/presentation/ | Manage opportunity stages | /api/v1/crm/opportunity-stages | opportunity_stage tables | Rebuild | Medium | Medium |
| Customer segment admin | Not yet implemented | admin list/form patterns | Frontend/lib/features/crm/presentation/ | Manage customer segments | /api/v1/crm/customer-segments | customer_segment tables | Rebuild | Medium | Medium |
| Activity type admin | Not yet implemented | admin list/form patterns | Frontend/lib/features/crm/presentation/ | Manage activity types and outcomes | /api/v1/crm/activity-types | activity_type tables | Rebuild | Medium | Medium |

#### Notes

- These pages should be routed under the settings area and appear only when the user has the appropriate admin permissions.

---

### 10. Reports and dashboards

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| CRM reports | Not yet implemented | summary cards and analytics panels | Frontend/lib/features/crm/presentation/ | Support lead/opportunity/customer reporting surfaces | reporting endpoints | CRM entities | Rebuild | Medium | High |

#### Notes

- Reporting can be introduced after the core module flows are in place.
- Start with the simplest dashboard-oriented summaries before deeper reporting exports.

---

### 11. User profile and settings

| Area | Current Frontend location | CustomerTracker reference | Proposed Frontend location | Purpose | API dependency | Database dependency | Decision | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|
| Profile/account header | Current shell only | profile card and account header | Frontend/lib/features/platform/presentation/home_page.dart | Surface current user and tenant context | auth/me | user/tenant tables | Modify | Medium | Low |
| Settings section | Not yet implemented | grouped settings UI | Frontend/lib/features/platform/presentation/ | Support CRM-related settings and preferences | settings/profile endpoints | tenant/user tables | Rebuild | Medium | Medium |

#### Notes

- These are important for a polished CRM experience, but they are secondary to the core sales workflow.

---

## 4. Recommended Implementation Sequence

### Sprint 1

1. Refine authentication experience.
2. Rework app shell and CRM navigation.
3. Improve lead list and lead create experience.
4. Add lead detail and state-aware actions.

### Sprint 2

1. Expand opportunity experience with pipeline and detail UI.
2. Introduce activity timeline and log activity flows.
3. Add follow-up and upcoming activity views.

### Sprint 3

1. Build customer/account management screens.
2. Add customer 360 and contact/address management.
3. Introduce CRM settings/admin screens.

### Sprint 4

1. Add dashboard/report surfaces.
2. Introduce quoting and downstream references when the sales/finance modules are available.
3. Polish user profile, settings, and role-based visibility.

---

## 5. Suggested Migration Strategy by Existing Frontend Area

### Existing Frontend areas to evolve

- Frontend/lib/features/platform/presentation/login_page.dart
- Frontend/lib/features/platform/presentation/home_page.dart
- Frontend/lib/features/crm/presentation/leads_page.dart
- Frontend/lib/features/crm/presentation/lead_form_dialog.dart
- Frontend/lib/features/crm/presentation/opportunities_page.dart
- Frontend/lib/features/crm/presentation/opportunity_form_dialog.dart

### New CRM UI areas to add

- customer list/detail/360 screens
- activity timeline and activity list screens
- follow-up and calendar views
- CRM settings/admin pages
- dashboard/report surfaces

---

## 6. Risk Notes

- The largest risk is trying to implement all CRM modules at once instead of sequencing around the lead → opportunity → customer journey.
- The second risk is overusing CustomerTracker as a code source instead of as a UX inspiration layer.
- The third risk is building screens before the required Backend and Database capabilities are ready.

---

## 7. Final Recommendation

The migration should proceed in a layered way:

1. Use the current Frontend as the implementation foundation.
2. Reuse CustomerTracker for UX patterns and information hierarchy.
3. Build the CRM screens to match the documented module routes and workflows.
4. Focus first on leads, opportunities, activities, and customers, because these are the core of the CRM journey.
5. Defer reporting and downstream surfaces until the main CRM modules are stable.
