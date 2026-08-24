# CustomerTracker → CRM Frontend Gap Analysis

## Purpose

This document compares the legacy CustomerTracker reference application with the existing E-LinkUp CRM Frontend, Backend, Database, and approved CRM documentation. It identifies what can be reused visually, what must be adapted, what should be rebuilt in the existing Frontend, and what should not be carried forward.

This analysis is grounded in the authoritative CRM documentation in the Documentation folder, especially the CRM business functional specification pack and the platform architecture documents. It does not invent requirements.

---

## 1. Scope and Method

### Source domains

- CustomerTracker: UI/UX reference only
- Frontend: current production Flutter CRM client
- Backend: current FastAPI CRM API
- Database: current PostgreSQL CRM data model and approved schema direction
- Documentation: authoritative CRM architecture, roadmap, and business requirements

### Principle

CustomerTracker is not the implementation source of truth. The CRM Frontend should absorb only the relevant UI/UX patterns and convert them into screens and interactions that align with the approved CRM architecture, API contracts, and database model.

---

## 2. Overall Assessment

### What CustomerTracker provides

CustomerTracker provides useful UI/UX patterns for:

- authentication entry flows
- app shell and drawer navigation
- lead-centric list/detail experiences
- profile and settings screens
- follow-up and calendar-oriented interactions
- forms and search/filter entry patterns
- activity-oriented UI patterns such as timeline and action cards

### What the current Frontend already provides

The current Frontend already contains the beginning of a production-oriented CRM UI for:

- authentication/login
- application home shell
- lead list and create flows
- opportunity list and create flows
- platform foundation pages (tenants, organizations, subscriptions, editions)

### What the current Backend already provides

The current Backend already includes a working API layer for:

- authentication and session handling
- CRM leads and opportunities
- platform foundation capabilities such as tenant and organization management

### What the Database already provides

The current Database has the earliest CRM persistence foundation for:

- lead records
- opportunity records
- tenant-aware CRM tables

### What the Documentation requires

The approved CRM documentation requires a broader and more structured CRM experience than the current Frontend currently exposes. In particular, the approved CRM specification calls for:

- customer/account management
- activity timeline and task flows
- lead conversion to customer/opportunity
- follow-up and overdue activity handling
- more complete navigation and screen routes for CRM modules
- role-aware and edition-aware UX behavior

---

## 3. Area-by-Area Gap Analysis

### A. Authentication

#### What CustomerTracker provides

- login form patterns
- OTP-style alternative flow concept
- password recovery flow concept
- registration entry pattern

#### What Frontend already provides

- a login page using tenant, email, and password fields
- auth controller and auth service
- session bootstrap and sign-out handling

#### What Backend already provides

- JWT login endpoint
- `/api/v1/auth/login`
- `/api/v1/auth/me`

#### What Database already provides

- user, tenant, organization, and authentication-related foundation through the platform schema

#### What the CRM documentation requires

- tenant-aware sign-in
- role-aware navigation after login
- edition-aware access to modules
- platform and CRM entry depending on role

#### What is missing

- stronger tenant-aware onboarding experience
- clearer role-based entry experience after login
- better error handling and form states that align with the CRM experience

#### Reuse visually

- the general login card layout, spacing, and field grouping

#### Modify

- the current login experience to better reflect the CRM product and tenant context

#### Rebuild

- the surrounding experience around sign-in state, role-based redirect, and product branding

#### Should NOT be carried forward

- OTP or registration UX as a direct implementation copy from CustomerTracker

#### Priority

High

#### Dependencies

- Backend auth endpoints
- platform tenant/user model
- Frontend auth controller

---

### B. App shell / navigation

#### What CustomerTracker provides

- drawer-based navigation structure
- user account header
- app shell concept with a sidebar or drawer menu
- menu items for leads, profile, settings, and reports

#### What Frontend already provides

- a home page with a navigation rail / navigation bar
- a basic dashboard shell
- platform module navigation
- CRM lead and opportunity pages embedded in the shell

#### What Backend already provides

- role and permission structure through platform services and RBAC expectations

#### What Database already provides

- tenant, organization, user, and role-related platform structures

#### What the CRM documentation requires

- CRM-centric navigation for leads, opportunities, customers, activities, and later settings/admin screens
- role-based visibility
- route structure consistent with the documented CRM screen inventory

#### What is missing

- full CRM navigation tree for leads, opportunities, customers, activities, calendar, tasks, and settings
- clear route structure for detail pages and embedded timeline actions

#### Reuse visually

- drawer and app-shell conventions, user header, section grouping, and icon usage

#### Modify

- the current shell to make CRM areas first-class navigation targets instead of only a general platform shell

#### Rebuild

- the item hierarchy and route-based navigation patterns to align with CRM modules

#### Should NOT be carried forward

- a simple old side-menu structure copied directly without role or module logic

#### Priority

High

#### Dependencies

- documented CRM screen routes
- RBAC and edition gating expectations
- Frontend app shell and navigation infrastructure

---

### C. Dashboard

#### What CustomerTracker provides

- dashboard-style sections and cards
- summary panels and status-driven visual grouping
- search and action bar patterns

#### What Frontend already provides

- a basic dashboard view on the home page
- welcome text and tenant info

#### What Backend already provides

- platform profile and tenant context
- some basic data endpoints for platform entities

#### What Database already provides

- tenant, organization, and user metadata for contextual dashboards

#### What the CRM documentation requires

- CRM dashboards for pipeline, lead conversion, activity compliance, and customer summaries
- role-based dashboard views for sales managers and tenant admins

#### What is missing

- CRM-specific dashboard widgets and KPI views
- lead/opportunity pipeline summaries
- overdue and upcoming activity views

#### Reuse visually

- card-based dashboard layout, summary tiles, and compact information panels

#### Modify

- the current landing experience to support CRM-oriented KPIs and contextual modules

#### Rebuild

- the actual dashboard content and analytics experience based on documented reports and CRM workflows

#### Should NOT be carried forward

- generic dashboard content that is not tied to CRM business needs

#### Priority

Medium

#### Dependencies

- documented reporting requirements
- Backend reporting endpoints if available
- future CRM dashboard APIs

---

### D. Tenant / platform administration

#### What CustomerTracker provides

- profile and settings-style screens
- form-heavy administration concepts
- user/admin-like screen patterns

#### What Frontend already provides

- tenants, organizations, subscriptions, editions pages
- platform administration shell

#### What Backend already provides

- platform APIs for tenants, organizations, subscriptions, and editions

#### What Database already provides

- platform foundation schemas and tenant-aware tables

#### What the CRM documentation requires

- tenant admin screens for CRM-specific settings such as lead sources, opportunity stages, customer segments, and activity types
- edition-aware visibility of admin modules

#### What is missing

- explicit CRM admin pages for lead sources, opportunity stages, customer segments, activity types, and related settings

#### Reuse visually

- settings and admin form layout patterns

#### Modify

- the current platform admin experience to include CRM-specific settings sections in the proper shell

#### Rebuild

- the CRM admin sub-pages and their navigation according to the documented admin routes

#### Should NOT be carried forward

- any CustomerTracker admin pattern that assumes a simpler app structure or a non-tenant platform model

#### Priority

Medium

#### Dependencies

- platform RBAC and tenant admin roles
- Backend settings/admin endpoints once available
- documentation for CRM administration modules

---

### E. Contacts

#### What CustomerTracker provides

- contact list and contact profile patterns
- person-centric cards and forms
- follow-up/contact-related interaction patterns

#### What Frontend already provides

- no dedicated CRM contact management experience yet

#### What Backend already provides

- no dedicated CRM contact management endpoints in the current implementation

#### What Database already provides

- the current database does not yet expose a dedicated CRM contact module in the same way the documentation describes for lead contacts and customer contacts

#### What the CRM documentation requires

- lead-contact and customer-contact handling
- contact collection linked to leads and customers
- primary-contact semantics
- contact-based follow-up and activity linkage

#### What is missing

- dedicated contact management UI for leads and customers
- contact forms and relationship handling

#### Reuse visually

- card-based person/profile layouts and form field organization

#### Modify

- none yet; this area is mostly missing in the current Frontend

#### Rebuild

- the contact manager views and their placement inside lead and customer detail experiences

#### Should NOT be carried forward

- any old contact screen implementation that is not connected to the CRM data model

#### Priority

High

#### Dependencies

- CRM documentation for lead and customer contacts
- Backend endpoints for contact management once added
- database model for lead contact / customer contact records

---

### F. Accounts / customers

#### What CustomerTracker provides

- profile experience for entities and users
- account-like detail screen concepts
- contact and address organization ideas

#### What Frontend already provides

- no customer/account management UI yet beyond a platform organization view

#### What Backend already provides

- platform organization resources, but not yet a full CRM customer module

#### What Database already provides

- the current database includes only the early CRM lead and opportunity tables; it does not yet expose the full customer schema described in the CRM documentation

#### What the CRM documentation requires

- customer/account master screens
- customer 360 view
- contact and address management
- customer status, credit, and relationship handling
- customer search and duplicate management

#### What is missing

- customer list/create/edit/detail screens
- customer 360 experience
- customer contact/address management

#### Reuse visually

- profile layout, tabbed detail sections, and contact/address card styling from CustomerTracker

#### Modify

- the current app shell and detail pattern to support account-like entities

#### Rebuild

- the customer module UI and its relationship to leads/opportunities

#### Should NOT be carried forward

- old account/organization screens that are not aligned with CRM customer semantics

#### Priority

High

#### Dependencies

- approved CRM customer documentation
- backend customer endpoints and database schema

---

### G. Leads

#### What CustomerTracker provides

- lead creation flow
- lead list and detail patterns
- lead profile layout
- search and filter patterns
- follow-up awareness concepts

#### What Frontend already provides

- a lead list page
- lead create dialog
- basic lead model/service/controller
- lead conversion to opportunity

#### What Backend already provides

- lead list/create/get/update/delete endpoints
- lead conversion endpoint

#### What Database already provides

- lead table with tenant isolation and business fields

#### What the CRM documentation requires

- full lead lifecycle: create, qualify, nurture, disqualify, assign, convert, history, duplicate review
- lead-contact handling
- lead detail screen with embedded activity timeline
- advanced search and export
- state-aware UI behavior

#### What is missing

- full lead detail experience
- qualification/disqualification actions
- assignment views and history
- duplicate-check and lead-source admin screens
- richer state-driven UI

#### Reuse visually

- lead list and detail layout patterns, search field patterns, and summary card styling

#### Modify

- the current lead experience to align with the documented lead lifecycle and UI screen inventory

#### Rebuild

- the richer lead workflow screens and modal interactions

#### Should NOT be carried forward

- simple create-only lead dialogs as the full lead experience

#### Priority

High

#### Dependencies

- Backend lead APIs and future lead-state actions
- documentation for lead lifecycle states and rules

---

### H. Opportunities

#### What CustomerTracker provides

- deal/opportunity-style list and summary concepts
- follow-up and pipeline-like card patterns
- action-oriented UI concepts

#### What Frontend already provides

- opportunity list and create page
- opportunity service/controller
- stage advancement flow

#### What Backend already provides

- opportunity list/create/advance endpoints
- pipeline endpoint

#### What Database already provides

- opportunity table with stage and status fields

#### What the CRM documentation requires

- full opportunity pipeline view
- close won / close lost wizard
- forecast view
- team / stage history support
- stage configuration admin screens

#### What is missing

- richer pipeline experience, especially the documented kanban and close-wizard flows
- stage history / team views
- forecast and pipeline analytics screens

#### Reuse visually

- pipeline and action-oriented card layout patterns

#### Modify

- the current opportunity pages to better align with the documented CRM journey and screen structure

#### Rebuild

- the pipeline UI and close-stage interaction experience

#### Should NOT be carried forward

- a simple list-only opportunity page as if it were the complete CRM opportunity experience

#### Priority

High

#### Dependencies

- opportunity API endpoints and documented stage workflow
- backend support for close-won/close-lost and history data

---

### I. Activities

#### What CustomerTracker provides

- calendar and follow-up interaction patterns
- event and task visual concepts
- timeline-style activity arrangements

#### What Frontend already provides

- no dedicated activity timeline UI yet in the current CRM frontend

#### What Backend already provides

- no dedicated CRM activity module in the current implementation

#### What Database already provides

- only the earliest CRM tables; no full activity model yet in the current implementation

#### What the CRM documentation requires

- activity timeline widget embedded on lead/opportunity/customer detail screens
- log activity dialog
- create task and meeting flows
- my activities / team activities / overdue activities / upcoming calendar views
- activity search and admin configuration

#### What is missing

- activity module UI
- embedded timeline components on detail screens
- task and follow-up experience

#### Reuse visually

- calendar, task, and timeline concepts from CustomerTracker

#### Modify

- none yet; this is mostly a new experience to be integrated into the existing CRM shell

#### Rebuild

- the activity module and its embeds into lead/opportunity/customer experiences

#### Should NOT be carried forward

- any simplistic calendar view that does not reflect activity-related workflow requirements

#### Priority

High

#### Dependencies

- CRM activity API and database model
- documented activity screen routes and lifecycle rules

---

### J. Tasks

#### What CustomerTracker provides

- task-like cards, action buttons, and follow-up oriented layouts

#### What Frontend already provides

- no dedicated task list experience

#### What Backend already provides

- no dedicated task module in the current implementation

#### What Database already provides

- no task-specific CRM schema exposed yet

#### What the CRM documentation requires

- task creation and completion flows as part of the activity module
- overdue and upcoming task awareness
- task assignment and completion semantics

#### What is missing

- task-focused UI entry points
- completion and overdue task states in the CRM shell

#### Reuse visually

- compact action-card patterns and follow-up task list concepts

#### Modify

- none yet; this requires integration into the activity experience

#### Rebuild

- task interaction patterns within the activity module and dashboard views

#### Should NOT be carried forward

- any separate task screen that is not tied to activity lifecycle rules

#### Priority

Medium

#### Dependencies

- activity module implementation
- backend activity/task API contract

---

### K. Follow-ups

#### What CustomerTracker provides

- explicit follow-up style UI concepts
- reminder and scheduling patterns
- calendar-oriented follow-up concepts

#### What Frontend already provides

- no dedicated follow-up UI yet

#### What Backend already provides

- no dedicated follow-up module yet

#### What Database already provides

- no follow-up module in the current CRM schema

#### What the CRM documentation requires

- follow-up date handling for leads and activities
- overdue reminders and activity compliance
- nurturing and reminder-driven user interaction

#### What is missing

- follow-up scheduling UI and reminder-aware views

#### Reuse visually

- follow-up card layout, scheduling, and reminder presentation concepts

#### Modify

- none yet; this should be integrated with activity and lead workflows

#### Rebuild

- the follow-up experience as part of lead and activity modules

#### Should NOT be carried forward

- isolated follow-up screens that are not tied to lead state or activity rules

#### Priority

Medium

#### Dependencies

- lead status rules
- activity and notification requirements

---

### L. Calendar

#### What CustomerTracker provides

- calendar UI concepts and event-listing patterns
- monthly and weekly calendar organization

#### What Frontend already provides

- no CRM calendar experience yet

#### What Backend already provides

- no calendar module in the current implementation

#### What Database already provides

- no calendar-specific CRM schema yet

#### What the CRM documentation requires

- calendar-like views for upcoming activities and meetings
- integration with activities and follow-ups

#### What is missing

- activities-upcoming calendar experience
- calendar integration into the shell

#### Reuse visually

- calendar layout and event card concepts

#### Modify

- none yet; this should be integrated into the CRM activity experience

#### Rebuild

- the calendar-oriented activity views and entry points in the current Frontend

#### Should NOT be carried forward

- old calendar widget implementations disconnected from CRM workflows

#### Priority

Medium

#### Dependencies

- activity module and backend scheduling data

---

### M. Quotations

#### What CustomerTracker provides

- quote/invoice-style visual patterns and summary panels
- list/detail concepts for commercial documents

#### What Frontend already provides

- no CRM quotation UI yet

#### What Backend already provides

- no CRM quotation module in the current implementation

#### What Database already provides

- the documented CRM architecture expects downstream quotation integration but the current database does not yet expose the sales quotation module

#### What the CRM documentation requires

- quotations are downstream of opportunities and should be accessible from the opportunity journey
- the CRM UI should support linking or launching the sales quotation flow

#### What is missing

- quotation entry points in the opportunity workflow and customer workflow

#### Reuse visually

- document summary cards and form structure concepts

#### Modify

- none yet; this is a future integration point

#### Rebuild

- the opportunity-to-quotation entry point and related UI conceptually when the sales module becomes available

#### Should NOT be carried forward

- old quote/invoice screens as an isolated CRM implementation

#### Priority

Low to Medium

#### Dependencies

- downstream sales module and API availability

---

### N. Invoices

#### What CustomerTracker provides

- invoice-related UI concepts and document summary visuals

#### What Frontend already provides

- no CRM invoice UI yet

#### What Backend already provides

- no finance invoice CRM integration yet

#### What Database already provides

- no invoice module in the current CRM schema

#### What the CRM documentation requires

- invoices are downstream of the lead → opportunity → quotation → order → project → invoice flow
- customer and opportunity views may need to surface invoice-related relationships later

#### What is missing

- invoice UI references and downstream relationship surfaces

#### Reuse visually

- document overview and summary-card concepts

#### Modify

- none yet; this belongs to the finance domain later

#### Rebuild

- invoice-related surfaces only after the finance domain is implemented

#### Should NOT be carried forward

- ad-hoc invoice views not tied to the approved sales/finance architecture

#### Priority

Low

#### Dependencies

- finance module and API availability

---

### O. Reports

#### What CustomerTracker provides

- report and analytics-style screens
- chart-like summaries and status-based lists

#### What Frontend already provides

- no CRM reporting UI yet beyond the basic home dashboard

#### What Backend already provides

- limited platform support and no CRM reporting endpoints yet in the current implementation

#### What Database already provides

- the data foundation for CRM entities, but reporting screens are not yet implemented

#### What the CRM documentation requires

- operational and executive reports for leads, opportunities, customers, and activities
- dashboard-based report surfaces

#### What is missing

- lead and opportunity reports, pipeline reports, customer summary reports, and activity compliance views

#### Reuse visually

- report cards, summary panels, and dashboard composition from CustomerTracker

#### Modify

- none yet; this should be designed around documented CRM reporting needs

#### Rebuild

- the report surfaces and navigation entry points in the CRM shell

#### Should NOT be carried forward

- old report screens not aligned with CRM reporting requirements

#### Priority

Medium

#### Dependencies

- reporting API and reporting modules in later roadmap phases

---

### P. User / profile

#### What CustomerTracker provides

- profile fields, avatar, account header, settings layout

#### What Frontend already provides

- a basic profile experience in the old reference app, but not in the current CRM frontend

#### What Backend already provides

- auth/me profile data and user context

#### What Database already provides

- user and tenant information for profile rendering

#### What the CRM documentation requires

- user profile and role-aware display in the CRM shell
- tenant and organization context in the UI

#### What is missing

- a CRM-aligned profile and account header experience

#### Reuse visually

- avatar and profile-card layouts

#### Modify

- the current shell profile representation to be more CRM-oriented

#### Rebuild

- profile experience in the current frontend shell if needed

#### Should NOT be carried forward

- old user-profile screens unrelated to the current role-based CRM experience

#### Priority

Medium

#### Dependencies

- auth profile payload and tenant context

---

### Q. Settings

#### What CustomerTracker provides

- settings page concepts and grouped preference items

#### What Frontend already provides

- only a basic platform settings concept in the old reference app; the current CRM frontend does not yet expose comprehensive settings

#### What Backend already provides

- platform settings capability through organization/tenant configuration services

#### What Database already provides

- tenant and platform configuration tables

#### What the CRM documentation requires

- CRM-specific settings areas for lead sources, opportunity stages, customer segments, activity types, and related admin screens

#### What is missing

- a structured settings section in the CRM app shell for admin-driven configuration

#### Reuse visually

- grouped settings and admin form layout patterns

#### Modify

- the current app shell to incorporate dedicated settings sections driven by CRM documentation

#### Rebuild

- the CRM settings pages and their navigation flow

#### Should NOT be carried forward

- a generic settings page that does not map to documented CRM admin capabilities

#### Priority

Medium

#### Dependencies

- documented CRM admin modules
- backend configuration endpoints

---

## 4. Summary of What Should Be Reused Visually

The following CustomerTracker UI patterns should be reused visually in the existing Frontend:

- login card layout and field grouping
- drawer/sidebar navigation patterns
- user header and profile presentation
- list/detail page composition
- search and filter entry styling
- card-based summaries and status chips
- follow-up / calendar visual structure
- settings and admin form layout style
- profile and information panel layout

## 5. Summary of What Should Be Modified

The following should be modified to fit the current CRM architecture:

- authentication entry flow
- app shell and navigation model
- dashboard content and structure
- CRM module navigation and page hierarchy
- lead and opportunity screens to align with API-backed and state-aware behavior
- any screen that must obey tenant, role, edition, and documentation requirements

## 6. Summary of What Should Be Rebuilt

The following should be rebuilt in the current Frontend using the existing architecture:

- customer/account management experience
- activity timeline and task workflow experience
- follow-up and calendar-oriented UI views
- CRM admin/settings pages
- dashboard and reporting surfaces aligned with the approved CRM spec
- rich lead and opportunity detail experiences

## 7. Summary of What Should Not Be Carried Forward

The following should not be brought forward from CustomerTracker:

- direct code copying
- old hard-coded/mock UI screens as if they were production CRM pages
- navigation patterns that ignore role, tenant, and edition rules
- old monolithic screen implementations that are not aligned with the current feature-based Flutter architecture
- any UI that assumes a single-user or single-tenant prototype model

---

## 8. Priority Summary

### Priority 1 — Must be addressed first

- authentication experience
- app shell / CRM navigation
- lead detail and lead lifecycle UX
- opportunity pipeline and opportunity detail UX

### Priority 2 — Should follow soon after

- customer/account management UX
- activity timeline and activity/task UX
- dashboard and summary views
- follow-up and calendar experiences

### Priority 3 — Later phase work

- reports and analytics UI
- quotations/invoice surfaces
- deeper CRM admin/settings UX

---

## 9. Architectural Notes

The current Frontend should not be treated as a blank slate. It already contains the right architecture foundation for a production CRM app:

- feature-based folder structure
- service and controller separation
- provider-based state management
- API-backed flows

The CustomerTracker reference should be applied selectively at the UX and interaction-design level, not as a source for direct implementation or product logic.
