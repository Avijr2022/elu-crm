# E-LinkUp Platform Foundation — Business Functional Specification Pack

**Document ID:** ELU-BFS-PF  
**Document Name:** Platform Foundation BFS Pack (PF-001 through PF-011)  
**Version:** 1.0  
**Status:** Approved
**Related Documents:** ELU-DOC-001, ELU-DF-001, ELU-BRD-001, ELU-EFS-001, ELU-RTM-001
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Senior BA / Enterprise Solution Architect / Product Owner  
**Document Owner:** PMO  
**Example Tenant:** Euphoria  
**Stack:** Flutter Web + Android · Python FastAPI · PostgreSQL · JWT + Refresh Token · Docker · Linux VPS / Azure  
**Related Documents:** ELU-DF-001, ELU-BRD-001, ELU-SAD-001, ELU-HLD-001

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP | Initial BFS pack (seventeen sections) |
| 1.0a | 2026-07-31 | EIIP / PMO | Status Approved; registered in ELU-DOC-001; Related Documents standardized |

## Pack Index

| # | Module ID | Module Name | Sub Module | Feature | Anchor |
|---|-----------|-------------|------------|---------|--------|
| 1 | PF-001 | Edition Management | PF-001-001 Product Editions | PF-001-001-001 Edition Definition | [§ PF-001](#pf-001-edition-management) |
| 2 | PF-002 | Tenant Management | PF-002-001 Tenant Profile | PF-002-001-001 Tenant Registration | [§ PF-002](#pf-002-tenant-management) |
| 3 | PF-003 | Subscription Management | PF-003-001 Subscription | PF-003-001-001 Subscription Lifecycle | [§ PF-003](#pf-003-subscription-management) |
| 4 | PF-004 | Organization Management | PF-004-001 Organization Structure | PF-004-001-001 Organization Profile | [§ PF-004](#pf-004-organization-management) |
| 5 | PF-005 | Branch Management | PF-005-001 Branch Structure | PF-005-001-001 Branch Profile | [§ PF-005](#pf-005-branch-management) |
| 6 | PF-006 | Department Management | PF-006-001 Department Structure | PF-006-001-001 Department Profile | [§ PF-006](#pf-006-department-management) |
| 7 | PF-007 | Business Unit Management | PF-007-001 Business Unit | PF-007-001-001 Business Unit Profile | [§ PF-007](#pf-007-business-unit-management) |
| 8 | PF-008 | User & Identity Management | PF-008-001 User Account | PF-008-001-001 User Registration | [§ PF-008](#pf-008-user--identity-management) |
| 9 | PF-009 | Roles & Permissions (RBAC) | PF-009-001 Role Management | PF-009-001-001 Role & Permission Assignment | [§ PF-009](#pf-009-roles--permissions-rbac) |
| 10 | PF-010 | Audit & Compliance | PF-010-001 Audit Trail | PF-010-001-001 Activity Logging | [§ PF-010](#pf-010-audit--compliance) |
| 11 | PF-011 | System Configuration | PF-011-001 Tenant Settings | PF-011-001-001 Business Preferences | [§ PF-011](#pf-011-system-configuration) |

### Edition Feature Matrix (Platform Foundation)

| Capability | Community | Professional | Enterprise |
|------------|:---------:|:------------:|:----------:|
| Single Organization | ✓ | ✓ | ✓ |
| Multi-Branch | — | ✓ | ✓ |
| Multi-Department | ✓ | ✓ | ✓ |
| Business Units | — | ✓ | ✓ |
| Custom Roles (limited) | ✓ (5 roles) | ✓ (25 roles) | ✓ (unlimited) |
| Audit Trail (90 days) | ✓ | ✓ (1 year) | ✓ (7 years) |
| SSO / MFA | — | MFA | SSO + MFA |
| API Access | Read-only | Full REST | Full REST + Webhooks |
| Tenant Self-Registration | — | ✓ | ✓ |
| White-label Branding | — | Partial | Full |

---

# PF-001 Edition Management

**Document ID:** ELU-BFS-PF-001  
**Module:** PF-001 — Edition Management  
**Sub Module:** PF-001-001 — Product Editions  
**Feature:** PF-001-001-001 — Edition Definition  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

E-LinkUp is sold as a multi-edition SaaS product (Community, Professional, Enterprise). Edition Management defines the **product packaging layer** that governs which platform capabilities, modules, limits, and integrations are available to each tenant. Without a canonical edition catalogue, subscription enforcement, feature gating, and upgrade paths cannot be implemented consistently across the stack.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Revenue packaging | Enables tiered pricing aligned to customer maturity |
| Feature gating | Prevents Community tenants from accessing Enterprise-only modules |
| Upgrade path | Clear Community → Professional → Enterprise migration |
| Operational clarity | Platform Admin and Sales teams reference one edition matrix |
| Developer velocity | Edition codes drive server-side guards and UI visibility rules |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Edition master definition (Community, Professional, Enterprise) | Billing/invoicing (FIN domain) |
| Edition feature matrix (module + limit flags) | Payment gateway integration |
| Edition versioning and effective dates | Custom per-tenant pricing negotiation |
| Edition-to-subscription linkage | License key distribution (offline) |
| Platform-global edition catalogue | Tenant-specific edition overrides (v2) |

### 1.4 Users involved

Platform Admin, Tenant Admin (read-only view of own edition), Sales Manager (reference), System (Subscription Engine, Rule Engine).

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-001 |
| Sub Module ID | PF-001-001 |
| Feature ID | PF-001-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Platform (not tenant-scoped) |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Platform Admin | Internal | Create, update, publish editions; manage feature matrix | View edition usage reports |
| Tenant Admin | Internal | View assigned edition and feature limits | Request upgrade (via subscription) |
| Sales Manager | Internal | Reference edition capabilities during pre-sales | — |
| System — Subscription Engine | System | Resolve edition on tenant provisioning | Enforce limits |
| System — Rule Engine | System | Evaluate edition-based business rules | — |

---

## 3. Business Story

The **Platform Admin** at Euphoria Infotech maintains the E-LinkUp product edition catalogue. When a new tenant **Euphoria** is onboarded, the Sales Manager has already agreed on the **Professional** edition. The Platform Admin ensures the `Professional` edition record exists with the correct feature flags: multi-branch enabled, 25 custom roles, 1-year audit retention, MFA available, full REST API.

During tenant registration (PF-002), the provisioning workflow reads the active `edition` record and stamps `edition_id` on the new `tenant` row. The Subscription Engine (PF-003) creates a subscription bound to that edition. When Euphoria's Tenant Admin logs in, the Flutter shell reads the edition context from JWT claims and hides Enterprise-only navigation items (e.g. SSO configuration, API webhooks).

Six months later, Euphoria requests an upgrade to **Enterprise**. The Platform Admin publishes a new edition version (if feature matrix changed) and the Subscription lifecycle (PF-003) transitions the tenant's `subscription.edition_id`. The Rule Engine re-evaluates limits: audit retention extends to 7 years, business units unlock, SSO configuration screens appear. No data migration is required — only feature gates change.

If an edition is deprecated, the Platform Admin sets `status = DEPRECATED` with an `end_of_sale_date`. Existing tenants remain on their subscription; new tenants cannot select deprecated editions. The Platform Admin reviews the Edition Utilisation Report monthly to plan product roadmap.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Platform Admin]
      │
      ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Define Edition  │────►│ Configure Feature │────►│ Publish Edition │
│ (name, code)    │     │ Matrix & Limits   │     │ (ACTIVE)        │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
      ┌───────────────────────────────────────────────────┘
      ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Tenant          │────►│ Subscription     │────►│ Feature Gates   │
│ Registration    │     │ Created (PF-003) │     │ Applied Runtime │
│ (PF-002)        │     │ edition_id set   │     │ (UI + API)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Platform Admin | Create edition draft | Edition form | `edition` (DRAFT) | — |
| 2 | Platform Admin | Configure feature matrix | Edition + features | `edition_feature` rows | Rule Engine |
| 3 | Platform Admin | Set limits (users, storage, roles) | Limit values | `edition_limit` rows | — |
| 4 | Platform Admin | Publish edition | Edition id | `edition` (ACTIVE) | Workflow Engine |
| 5 | System | Bind edition on tenant provision | Tenant + edition code | `tenant.edition_id` | Subscription Engine |
| 6 | System | Enforce gates at runtime | JWT + edition | Allow/Deny | Rule Engine |
| 7 | Platform Admin | Deprecate edition | Edition id | `edition` (DEPRECATED) | Notification Engine |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| DRAFT | Draft | Edition being configured | ACTIVE, CANCELLED | Platform Admin | Not selectable for subscriptions |
| ACTIVE | Active | Available for new subscriptions | DEPRECATED, ARCHIVED | Platform Admin | Selectable; gates enforced |
| DEPRECATED | Deprecated | End-of-sale; existing tenants retained | ARCHIVED | Platform Admin | Hidden from new tenant wizard |
| ARCHIVED | Archived | Historical record only | — | Platform Admin | Read-only; no new bindings |
| CANCELLED | Cancelled | Draft discarded | — | Platform Admin | Hard delete allowed if no FK refs |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-001 | Edition `code` shall be unique, uppercase, immutable after publish (COMMUNITY, PROFESSIONAL, ENTERPRISE) | Validation | Error | DB (UK), API |
| BR-PF-002 | Only one ACTIVE edition per `code` at any time | Validation | Error | DB, API |
| BR-PF-003 | Edition cannot be deleted if referenced by any `subscription` or `tenant` | Lifecycle | Error | DB (Restrict) |
| BR-PF-004 | Feature matrix changes on ACTIVE edition require new `version_no`; prior version retained | Lifecycle | Warning | API, Audit |
| BR-PF-005 | DEPRECATED editions shall not be assignable to new subscriptions | Lifecycle | Error | API, UI |
| BR-PF-006 | Edition limits (max_users, max_storage_gb, max_roles) must be ≥ Community baseline | Validation | Error | API |
| BR-PF-007 | ENTERPRISE edition must include SSO and 7-year audit retention flags | Validation | Error | API |
| BR-PF-008 | Publishing edition requires at least one feature row and one limit row | Approval | Error | Workflow Engine |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| edition | Master | Edition catalogue (Community/Professional/Enterprise) | No |
| edition_feature | Link | Feature flags per edition | No |
| edition_limit | Master | Numeric limits per edition | No |
| edition_version | Transaction | Version history of edition changes | No |
| feature_catalogue | Lookup | Platform feature registry | No |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| edition | edition_feature | 1:N | Cascade | Feature flags |
| edition | edition_limit | 1:N | Cascade | Limit definitions |
| edition | edition_version | 1:N | Restrict | Audit trail |
| edition | tenant | 1:N | Restrict | Current edition on tenant |
| edition | subscription | 1:N | Restrict | Subscription binding |
| feature_catalogue | edition_feature | 1:N | Restrict | FK to catalogue |

---

## 9. Field Groups

### edition
- General Information (code, name, description, display_order)
- Versioning (version_no, effective_from, effective_to)
- Status (status, published_at, published_by)
- Commercial (list_price_monthly, list_price_annual, currency_code)
- Audit (created_by, created_on, modified_by, modified_on)

### edition_feature
- Feature Reference (feature_code, feature_name, module_domain)
- Flag (is_enabled, is_visible)
- Edition Context (edition_id)

### edition_limit
- Limit Definition (limit_code, limit_name, limit_value, limit_unit)
- Enforcement (is_hard_limit, grace_percent)
- Edition Context (edition_id)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/platform/editions` | Create edition | `edition.create` |
| GET | `/api/v1/platform/editions` | List editions | `edition.read` |
| GET | `/api/v1/platform/editions/{id}` | Get edition detail | `edition.read` |
| PUT | `/api/v1/platform/editions/{id}` | Full update (draft only) | `edition.update` |
| PATCH | `/api/v1/platform/editions/{id}` | Partial update / status change | `edition.update` |
| DELETE | `/api/v1/platform/editions/{id}` | Cancel draft / archive | `edition.delete` |
| GET | `/api/v1/platform/editions/search` | Search editions | `edition.read` |
| GET | `/api/v1/platform/editions/export` | Export edition matrix | `edition.export` |
| POST | `/api/v1/platform/editions/{id}/publish` | Publish edition | `edition.publish` |
| POST | `/api/v1/platform/editions/{id}/deprecate` | Deprecate edition | `edition.deprecate` |
| GET | `/api/v1/tenant/edition` | Tenant's current edition (read) | `edition.read` |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Edition List | List | Platform Admin | Filter by status, code |
| Edition Create | Create | Platform Admin | Draft wizard |
| Edition Edit | Edit | Platform Admin | Feature matrix tab, limits tab |
| Edition View | View | Platform Admin, Tenant Admin | Read-only for Tenant Admin |
| Edition Search | Search | Platform Admin | Advanced filter |
| Edition Publish Approval | Approval | Platform Admin | Confirm publish action |
| Edition History | History | Platform Admin | Version timeline |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `edition.create` | Create edition drafts |
| `edition.read` | View editions |
| `edition.update` | Edit draft editions |
| `edition.delete` | Archive/cancel editions |
| `edition.publish` | Publish to ACTIVE |
| `edition.deprecate` | Mark deprecated |
| `edition.export` | Export matrix |

| Actor | create | read | update | delete | publish | deprecate | export |
|-------|:------:|:----:|:------:|:------:|:-------:|:---------:|:------:|
| Platform Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tenant Admin | — | ✓ (own) | — | — | — | — | — |
| Sales Manager | — | ✓ | — | — | — | — | ✓ |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Edition published | Email, Internal | Platform Admin, Sales Manager | NTF-PF-001-01 |
| Edition deprecated | Email, Internal | Platform Admin, affected Tenant Admins | NTF-PF-001-02 |
| Edition upgrade available | Email, Push | Tenant Admin | NTF-PF-001-03 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-001-01 | Edition Utilisation | Management | Platform Admin | Per edition | Status, date range | PDF, XLSX |
| RPT-PF-001-02 | Feature Adoption by Edition | Operational | Product Owner | Per feature flag | Edition, module | XLSX |
| RPT-PF-001-03 | Edition Revenue Forecast | Executive | Leadership | Per edition | Period | PDF |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Edition created | edition_id, code, actor, timestamp | Platform permanent |
| Edition updated | field diff, version_no | Platform permanent |
| Edition published | edition_id, version_no | Platform permanent |
| Edition deprecated | edition_id, reason | Platform permanent |
| Feature matrix changed | feature_code, old/new value | Platform permanent |

---

## 16. Acceptance Criteria

1. **AC-PF-001-01:** Given a Platform Admin, when they create and publish a Professional edition, then it appears in the tenant registration edition dropdown.
2. **AC-PF-001-02:** Given a Community tenant, when they access an Enterprise-only API endpoint, then the API returns HTTP 403 with edition gate error code.
3. **AC-PF-001-03:** Given a DEPRECATED edition, when a new tenant registration is attempted with that edition, then the system rejects with BR-PF-005.
4. **AC-PF-001-04:** Given an ACTIVE edition with 25 max roles, when a Tenant Admin creates role #26 on Professional, then the system blocks with limit exceeded error.
5. **AC-PF-001-05:** Given edition version change, when published, then prior version is retained in `edition_version` and audit log.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Custom edition builder for Enterprise deals; per-tenant feature overrides |
| v2.0 | Edition comparison wizard for Tenant Admin self-service upgrade |
| v3.0 | Usage-based metering (API calls, storage) tied to edition limits |
| v3.0 | Marketplace add-on modules layered on base edition |

---

# PF-002 Tenant Management

**Document ID:** ELU-BFS-PF-002  
**Module:** PF-002 — Tenant Management  
**Sub Module:** PF-002-001 — Tenant Profile  
**Feature:** PF-002-001-001 — Tenant Registration  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

Tenant Management is the **root isolation boundary** of E-LinkUp multi-tenant SaaS. Every business record, user, configuration, and audit event belongs to exactly one tenant. Tenant Registration provisions the complete tenant profile — legal identity, contacts, addresses, branding, security policy, localization, and default organization — so that Euphoria (and future customers) can operate as isolated instances on shared infrastructure.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Multi-tenant isolation | Data, config, and users scoped by `tenant_id` |
| Rapid onboarding | Guided registration reduces time-to-first-login |
| Brand identity | White-label branding per tenant (Professional+) |
| Compliance readiness | Security and localization defaults at provision time |
| Single source of truth | Canonical tenant profile referenced by all domains |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Tenant registration and profile CRUD | DNS custom domain provisioning (v2) |
| Tenant contacts, addresses, branding | Billing account (FIN domain) |
| Tenant security and localization defaults | Infrastructure provisioning (DevOps) |
| Tenant status lifecycle (active, suspended) | Data export/migration tooling (v2) |
| Link to edition and subscription | |

### 1.4 Users involved

Platform Admin, Tenant Admin, Sales Manager, System (Provisioning Engine, Notification Engine).

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-002 |
| Sub Module ID | PF-002-001 |
| Feature ID | PF-002-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Professional (self-registration); Platform Admin can provision any |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Platform Admin | Internal | Register tenant, approve, suspend, reactivate | View all tenants |
| Tenant Admin | Internal | Update tenant profile, branding, contacts | View own tenant |
| Sales Manager | Internal | Initiate registration request | Track onboarding status |
| System — Provisioning Engine | System | Create tenant shell + defaults | Rollback on failure |
| System — Notification Engine | System | Send welcome and status emails | — |

---

## 3. Business Story

A **Sales Manager** at Euphoria Infotech completes a deal with tenant **Euphoria** for the Professional edition. The **Platform Admin** opens Tenant Registration, enters legal name "Euphoria Infotech (I) Limited", trade name "Euphoria", selects edition **Professional**, and provides primary contact details (Tenant Admin designate: name, email, mobile).

The Provisioning Engine creates rows in `tenant`, `tenant_contact` (primary + billing), `tenant_address` (registered + correspondence), `tenant_branding` (logo placeholder, primary colour), `tenant_settings` (defaults), `tenant_security` (password policy, session timeout), `tenant_localization` (timezone Asia/Kolkata, locale en-IN, currency INR), a root `organization` record, and a pending `subscription` (PF-003). Status is set to `PENDING_ACTIVATION`.

The Platform Admin reviews the registration summary and approves. The system sends a welcome email to the designated Tenant Admin with an activation link. The Tenant Admin completes password setup (PF-008), and tenant status moves to `ACTIVE`. The Tenant Admin updates branding (uploads logo), verifies address, and configures business preferences (PF-011).

If Euphoria fails payment verification, the Platform Admin suspends the tenant (`SUSPENDED`). All tenant users receive a login-blocked message. Upon payment resolution, Platform Admin reactivates to `ACTIVE`. If Euphoria requests offboarding, Platform Admin initiates `OFFBOARDING` → data retention period → `CLOSED`.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Sales Manager] ──request──► [Platform Admin]
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ Tenant Register │
                          │ (wizard)        │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              [tenant]    [tenant_contact]  [tenant_address]
                    │              │              │
                    ▼              ▼              ▼
         [tenant_branding] [tenant_settings] [tenant_security]
                    │              │              │
                    ▼              ▼              ▼
         [tenant_localization] [organization] [subscription]
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ PENDING_ACTIVATION│
                          └────────┬────────┘
                                   │ approve
                                   ▼
                          ┌─────────────────┐
                          │ Send Activation │
                          │ Email (PF-008)  │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ ACTIVE          │
                          └─────────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Platform Admin | Initiate registration | Registration form | `tenant` (PENDING_ACTIVATION) | Provisioning Engine |
| 2 | System | Create child profiles | Tenant id | contact, address, branding, settings, security, localization | Provisioning Engine |
| 3 | System | Create root organization | Tenant id | `organization` (root) | Provisioning Engine |
| 4 | System | Create subscription | Tenant + edition | `subscription` (TRIAL/ACTIVE) | Subscription Engine |
| 5 | Platform Admin | Approve registration | Tenant id | Status → PENDING_ACTIVATION confirmed | Workflow Engine |
| 6 | System | Send activation invite | Tenant Admin email | User invite (PF-008) | Notification Engine |
| 7 | Tenant Admin | Activate account | Activation token | `tenant` (ACTIVE), user (ACTIVE) | Auth Service |
| 8 | Platform Admin | Suspend / Reactivate | Tenant id | SUSPENDED / ACTIVE | Workflow Engine |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| DRAFT | Draft | Registration in progress | PENDING_ACTIVATION, CANCELLED | Platform Admin | No users provisioned |
| PENDING_ACTIVATION | Pending Activation | Awaiting admin approval / user activation | ACTIVE, CANCELLED | Platform Admin | Invite sent |
| ACTIVE | Active | Fully operational | SUSPENDED, OFFBOARDING | Platform Admin, System | Full access |
| SUSPENDED | Suspended | Login blocked; read-only API | ACTIVE, OFFBOARDING | Platform Admin | JWT invalidated |
| OFFBOARDING | Offboarding | Data retention countdown | CLOSED | Platform Admin | Write blocked |
| CLOSED | Closed | Tenant terminated | ARCHIVED | Platform Admin | All access denied |
| CANCELLED | Cancelled | Registration abandoned | — | Platform Admin | Cleanup eligible |
| ARCHIVED | Archived | Historical record | — | System | Read-only platform view |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-009 | Tenant `code` shall be unique, lowercase alphanumeric, 3–32 chars | Validation | Error | DB (UK), API |
| BR-PF-010 | Tenant `legal_name` is mandatory and unique across platform | Validation | Error | DB, API |
| BR-PF-011 | Exactly one PRIMARY contact per tenant | Validation | Error | DB, API |
| BR-PF-012 | Exactly one REGISTERED address per tenant | Validation | Error | DB, API |
| BR-PF-013 | Tenant registration must specify valid ACTIVE edition | Validation | Error | API |
| BR-PF-014 | SUSPENDED tenant users cannot obtain new JWT tokens | Security | Error | Auth Service |
| BR-PF-015 | Tenant cannot be hard-deleted; only soft-delete / CLOSED | Lifecycle | Error | DB, API |
| BR-PF-016 | `tenant_id` on all child tables must match parent tenant | Security | Error | DB (FK), API middleware |
| BR-PF-017 | Branding logo max 2 MB; formats PNG, JPG, SVG | Validation | Error | API, UI |
| BR-PF-018 | Self-registration (Professional+) requires email domain verification | Security | Warning | API, Notification |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| tenant | Master | Root tenant record | No (is the tenant root) |
| tenant_contact | Master | Contact persons (primary, billing, technical) | Yes |
| tenant_address | Master | Registered, correspondence, billing addresses | Yes |
| tenant_branding | Master | Logo, colours, favicon, white-label | Yes |
| tenant_settings | Master | General tenant configuration defaults | Yes |
| tenant_security | Master | Password policy, session, MFA defaults | Yes |
| tenant_localization | Master | Timezone, locale, date/number formats, currency | Yes |
| organization | Master | Root organization (created at provision) | Yes |
| edition | Master | FK — assigned edition | No |
| subscription | Transaction | FK — active subscription | Yes |
| users | Master | FK — Tenant Admin created at activation | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| edition | tenant | 1:N | Restrict | Edition assignment |
| tenant | tenant_contact | 1:N | Cascade | Contacts |
| tenant | tenant_address | 1:N | Cascade | Addresses |
| tenant | tenant_branding | 1:1 | Cascade | Branding profile |
| tenant | tenant_settings | 1:1 | Cascade | Settings |
| tenant | tenant_security | 1:1 | Cascade | Security policy |
| tenant | tenant_localization | 1:1 | Cascade | Localization |
| tenant | organization | 1:N | Restrict | Root org at provision |
| tenant | subscription | 1:N | Restrict | Subscription history |
| tenant | users | 1:N | Restrict | Tenant users |

---

## 9. Field Groups

### tenant
- Identity (code, legal_name, trade_name, registration_number, tax_id)
- Classification (industry_code, company_size, tenant_type)
- Edition & Subscription (edition_id, current_subscription_id)
- Status (status, activated_at, suspended_at, closed_at)
- Provisioning (provisioned_by, provision_source)
- Audit (created_by, created_on, modified_by, modified_on, is_deleted)

### tenant_contact
- Contact Identity (contact_type, salutation, first_name, last_name, designation)
- Communication (email, phone, mobile, whatsapp)
- Flags (is_primary, is_billing, is_technical)
- Status (is_active)

### tenant_address
- Address Type (address_type: REGISTERED, CORRESPONDENCE, BILLING)
- Location (address_line_1, address_line_2, city, state, postal_code, country_code)
- Geo (latitude, longitude)
- Status (is_active, is_default)

### tenant_branding
- Visual Identity (logo_url, favicon_url, primary_colour, secondary_colour, accent_colour)
- White-label (app_name, tagline, custom_css_enabled)
- Portal (login_background_url, footer_text)

### tenant_settings
- General (default_language, fiscal_year_start_month)
- Module Defaults (default_currency, default_timezone)
- Feature Toggles (tenant-level overrides within edition limits)

### tenant_security
- Password Policy (min_length, complexity_rules, expiry_days, history_count)
- Session (session_timeout_minutes, max_concurrent_sessions)
- MFA (mfa_required, mfa_methods_allowed)
- IP Restrictions (allowed_ip_ranges — Enterprise)

### tenant_localization
- Locale (locale_code, language_code, country_code)
- Formats (date_format, time_format, number_format, first_day_of_week)
- Currency (default_currency_code, currency_display)
- Timezone (timezone_id)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/platform/tenants` | Register tenant | `tenant.create` |
| GET | `/api/v1/platform/tenants` | List tenants | `tenant.read` |
| GET | `/api/v1/platform/tenants/{id}` | Get tenant detail | `tenant.read` |
| PUT | `/api/v1/platform/tenants/{id}` | Full update | `tenant.update` |
| PATCH | `/api/v1/platform/tenants/{id}` | Partial update / status | `tenant.update` |
| DELETE | `/api/v1/platform/tenants/{id}` | Soft delete / close | `tenant.delete` |
| GET | `/api/v1/platform/tenants/search` | Search tenants | `tenant.read` |
| GET | `/api/v1/platform/tenants/export` | Export tenant list | `tenant.export` |
| POST | `/api/v1/platform/tenants/{id}/approve` | Approve registration | `tenant.approve` |
| POST | `/api/v1/platform/tenants/{id}/suspend` | Suspend tenant | `tenant.suspend` |
| POST | `/api/v1/platform/tenants/{id}/reactivate` | Reactivate tenant | `tenant.reactivate` |
| GET | `/api/v1/tenant/profile` | Current tenant profile | `tenant.read` |
| PUT | `/api/v1/tenant/profile` | Update own profile | `tenant.update` |
| GET | `/api/v1/tenant/contacts` | List tenant contacts | `tenant_contact.read` |
| POST | `/api/v1/tenant/contacts` | Add contact | `tenant_contact.create` |
| GET | `/api/v1/tenant/addresses` | List addresses | `tenant_address.read` |
| PUT | `/api/v1/tenant/branding` | Update branding | `tenant_branding.update` |
| GET | `/api/v1/tenant/settings` | Get settings | `tenant_settings.read` |
| PUT | `/api/v1/tenant/security` | Update security policy | `tenant_security.configure` |
| GET | `/api/v1/tenant/localization` | Get localization | `tenant_localization.read` |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Tenant List | List | Platform Admin | Status filters, edition column |
| Tenant Register | Create | Platform Admin | Multi-step wizard |
| Tenant Edit | Edit | Platform Admin, Tenant Admin | Tabbed: profile, contacts, addresses |
| Tenant View | View | Platform Admin, Tenant Admin | Summary cards |
| Tenant Search | Search | Platform Admin | By name, code, status, edition |
| Tenant Approval | Approval | Platform Admin | Review + approve/reject |
| Tenant Suspend Dialog | Approval | Platform Admin | Reason required |
| Tenant Branding | Edit | Tenant Admin | Logo upload, colour picker |
| Tenant Security Settings | Edit | Tenant Admin | Password policy, MFA |
| Tenant Localization | Edit | Tenant Admin | Timezone, formats |
| Tenant History | History | Platform Admin | Status timeline, audit |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `tenant.create` | Register new tenant |
| `tenant.read` | View tenant profile |
| `tenant.update` | Edit tenant profile |
| `tenant.delete` | Close/archive tenant |
| `tenant.approve` | Approve registration |
| `tenant.suspend` | Suspend tenant |
| `tenant.reactivate` | Reactivate suspended tenant |
| `tenant.export` | Export tenant data |
| `tenant_contact.create` | Add tenant contact |
| `tenant_contact.read` | View contacts |
| `tenant_contact.update` | Edit contact |
| `tenant_contact.delete` | Remove contact |
| `tenant_address.create` | Add address |
| `tenant_address.read` | View addresses |
| `tenant_address.update` | Edit address |
| `tenant_branding.update` | Update branding |
| `tenant_security.configure` | Configure security policy |
| `tenant_localization.read` | View localization |
| `tenant_localization.update` | Update localization |
| `tenant_settings.read` | View settings |
| `tenant_settings.configure` | Update settings |

| Actor | create | read | update | suspend | approve | branding | security |
|-------|:------:|:----:|:------:|:-------:|:-------:|:--------:|:--------:|
| Platform Admin | ✓ | ✓ (all) | ✓ (all) | ✓ | ✓ | ✓ | ✓ |
| Tenant Admin | — | ✓ (own) | ✓ (own) | — | — | ✓ | ✓ |
| Sales Manager | — | ✓ | — | — | — | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Tenant registered | Email, Internal | Platform Admin | NTF-PF-002-01 |
| Tenant approved | Email, SMS | Tenant Admin designate | NTF-PF-002-02 |
| Tenant activated | Email, Push | Tenant Admin | NTF-PF-002-03 |
| Tenant suspended | Email, SMS, Push | All Tenant Admins | NTF-PF-002-04 |
| Tenant reactivated | Email, Push | All Tenant Admins | NTF-PF-002-05 |
| Tenant closing | Email | Tenant Admin, Platform Admin | NTF-PF-002-06 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-002-01 | Tenant Directory | Operational | Platform Admin | Per tenant | Status, edition, date | XLSX, CSV |
| RPT-PF-002-02 | Tenant Onboarding Pipeline | Management | Sales Manager | Per registration stage | Date range | PDF |
| RPT-PF-002-03 | Suspended Tenants | Operational | Platform Admin | Per tenant | Suspension reason | XLSX |
| RPT-PF-002-04 | Tenant Growth Dashboard | Executive | Leadership | Monthly new tenants | Edition, industry | PDF |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Tenant created | tenant_id, code, legal_name, edition_id | Per tenant security policy |
| Tenant profile updated | field diff, actor | Per tenant security policy |
| Tenant status changed | old_status, new_status, reason | Per tenant security policy |
| Branding updated | logo_url changed flag | Per tenant security policy |
| Security policy changed | policy diff | Per tenant security policy |
| Contact added/removed | contact_id, contact_type | Per tenant security policy |

---

## 16. Acceptance Criteria

1. **AC-PF-002-01:** Given Platform Admin completes registration for Euphoria, when approved, then tenant shell with all child tables is created and activation email sent.
2. **AC-PF-002-02:** Given tenant Euphoria is ACTIVE, when API request includes mismatched tenant_id in body vs JWT, then request is rejected (BR-PF-016).
3. **AC-PF-002-03:** Given SUSPENDED tenant, when any user attempts login, then authentication fails with tenant suspended message.
4. **AC-PF-002-04:** Given Tenant Admin uploads branding logo, when file exceeds 2 MB, then upload rejected (BR-PF-017).
5. **AC-PF-002-05:** Given two tenants on platform, when Tenant Admin of Euphoria queries `/api/v1/tenant/profile`, then only Euphoria data is returned (multi-tenant isolation).
6. **AC-PF-002-06:** Given tenant registration, when edition is DEPRECATED, then registration fails (BR-PF-013).

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Custom domain mapping (tenant.elinkup.com → crm.euphoria.co.in) |
| v2.0 | Tenant self-registration portal with email verification |
| v2.0 | Tenant data export (GDPR right-to-portability) |
| v3.0 | Multi-region tenant data residency selection |
| v3.0 | Tenant hierarchy (parent-child tenants for conglomerates) |

---

# PF-003 Subscription Management

**Document ID:** ELU-BFS-PF-003  
**Module:** PF-003 — Subscription Management  
**Sub Module:** PF-003-001 — Subscription  
**Feature:** PF-003-001-001 — Subscription Lifecycle  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

Subscription Management binds each tenant to a **commercial and functional entitlement** — edition, billing cycle, seat count, start/end dates, and lifecycle status. It is the runtime authority for "what Euphoria has paid for and when it expires," driving feature gates, user limits, and renewal workflows.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Entitlement enforcement | Edition features active only with valid subscription |
| Revenue lifecycle | Trial → Active → Renewal → Expired tracking |
| Upgrade/downgrade | Edition transitions without re-provisioning tenant |
| Seat management | User count limits enforced per subscription |
| Renewal visibility | Proactive notifications before expiry |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Subscription CRUD and lifecycle | Payment processing (FIN-003) |
| Edition binding and changes | Invoice generation |
| Seat/user limit tracking | Tax calculation |
| Trial management | Dunning automation (v2) |
| Renewal and expiry | |

### 1.4 Users involved

Platform Admin, Tenant Admin, Finance User (read), System (Subscription Engine, Scheduler, Notification Engine).

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-003 |
| Sub Module ID | PF-003-001 |
| Feature ID | PF-003-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | All (subscription required for any tenant) |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Platform Admin | Internal | Create, upgrade, renew, cancel subscriptions | Override limits |
| Tenant Admin | Internal | View subscription, request upgrade | View usage vs limits |
| Finance User | Internal | View subscription for billing reference | Export |
| System — Scheduler | System | Check expiry, trigger renewal reminders | Auto-expire |
| System — Subscription Engine | System | Enforce limits at runtime | — |

---

## 3. Business Story

When **Euphoria** is provisioned (PF-002), the system auto-creates a **TRIAL** subscription for Professional edition: 30-day trial, 10 seats, start date today. The **Tenant Admin** receives a trial expiry reminder at day 25 via email.

The **Platform Admin** converts the trial to **ACTIVE** annual subscription: 50 seats, billing cycle ANNUAL, start date today, end date +1 year. The `tenant.current_subscription_id` is updated. Euphoria's users continue uninterrupted.

At month 10, the Scheduler sends renewal reminders to Tenant Admin and Finance User. Before expiry, Platform Admin processes renewal: new subscription row created (or current extended), status remains ACTIVE.

Euphoria requests upgrade to **Enterprise**. Platform Admin creates subscription change request: edition_id changes to ENTERPRISE, seat limit increases to 200. On effective date, feature gates update (SSO unlocks, audit retention extends). A subscription_history row captures the transition.

If payment fails (manual flag by Platform Admin), subscription moves to **PAST_DUE** → grace period 15 days → **EXPIRED**. Tenant status cascades to SUSPENDED (PF-002). Upon payment, Platform Admin reactivates subscription to ACTIVE and tenant to ACTIVE.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Tenant Provisioned]
        │
        ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ TRIAL        │────►│ ACTIVE       │────►│ RENEWAL DUE  │
│ (30 days)    │     │ (paid)       │     │ (reminder)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ EXPIRED      │     │ UPGRADED     │     │ RENEWED      │
│ (trial end)  │     │ (edition↑)   │     │ (extended)   │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ CANCELLED    │
                    │ (offboard)   │
                    └──────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | System | Auto-create trial subscription | Tenant + edition | `subscription` (TRIAL) | Provisioning Engine |
| 2 | Platform Admin | Convert trial to active | Subscription id | `subscription` (ACTIVE) | Subscription Engine |
| 3 | System | Send renewal reminder | Days before expiry | Email notification | Scheduler |
| 4 | Platform Admin | Process renewal | Subscription id | Extended end_date | Subscription Engine |
| 5 | Platform Admin | Upgrade edition | New edition_id | New subscription row | Subscription Engine |
| 6 | System | Check expiry daily | Current date | PAST_DUE or EXPIRED | Scheduler |
| 7 | Platform Admin | Cancel subscription | Reason | CANCELLED | Workflow Engine |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| TRIAL | Trial | Evaluation period | ACTIVE, EXPIRED, CANCELLED | System, Platform Admin | Full edition features, time-limited |
| ACTIVE | Active | Paid and current | RENEWAL_PENDING, PAST_DUE, CANCELLED | Platform Admin | Full access |
| RENEWAL_PENDING | Renewal Pending | Within renewal window | ACTIVE, EXPIRED | System | Access continues; reminders sent |
| PAST_DUE | Past Due | Payment overdue, grace period | ACTIVE, EXPIRED | Platform Admin | Warning banners; access continues |
| EXPIRED | Expired | Subscription ended | ACTIVE (reactivate), CANCELLED | System, Platform Admin | Tenant SUSPENDED |
| CANCELLED | Cancelled | Terminated by admin | — | Platform Admin | Tenant OFFBOARDING |
| SUSPENDED | Suspended | Admin hold on subscription | ACTIVE, CANCELLED | Platform Admin | Feature access limited |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-019 | Each tenant must have exactly one current ACTIVE or TRIAL subscription | Validation | Error | DB, API |
| BR-PF-020 | Subscription `end_date` must be > `start_date` | Validation | Error | API |
| BR-PF-021 | Seat count cannot exceed edition max_users limit | Validation | Error | API, Rule Engine |
| BR-PF-022 | Active user count cannot exceed subscription seat_count | Validation | Error | API (on user create) |
| BR-PF-023 | Edition downgrade not allowed if current user count > new edition limit | Lifecycle | Error | API |
| BR-PF-024 | EXPIRED subscription must cascade tenant to SUSPENDED within 1 hour | Lifecycle | Error | Scheduler |
| BR-PF-025 | Trial subscription max duration is 30 days (configurable platform setting) | Validation | Warning | Scheduler |
| BR-PF-026 | Subscription history row created on every status or edition change | Audit | Info | API, Audit Service |
| BR-PF-027 | Renewal cannot reduce seat_count below current active user count | Validation | Error | API |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| subscription | Transaction | Current and historical subscriptions | Yes |
| subscription_history | Audit | Status/edition change log | Yes |
| subscription_usage | Transaction | Seat/storage usage snapshots | Yes |
| tenant | Master | FK current_subscription_id | Yes |
| edition | Master | FK edition_id | No |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| tenant | subscription | 1:N | Restrict | Subscription history |
| edition | subscription | 1:N | Restrict | Edition binding |
| subscription | subscription_history | 1:N | Cascade | Change log |
| subscription | subscription_usage | 1:N | Cascade | Usage tracking |
| tenant | tenant.current_subscription_id | 1:1 | Set Null | Current pointer |

---

## 9. Field Groups

### subscription
- Identity (subscription_number, tenant_id)
- Edition (edition_id, edition_code_snapshot)
- Commercial (billing_cycle, unit_price, currency_code, total_amount)
- Seats (seat_count, seat_count_used)
- Dates (start_date, end_date, trial_end_date, cancelled_at)
- Status (status, cancellation_reason)
- Renewal (auto_renew, renewal_notice_days)
- Audit (created_by, created_on, modified_by, modified_on)

### subscription_history
- Change Context (subscription_id, change_type, changed_by)
- Before/After (old_status, new_status, old_edition_id, new_edition_id, old_seats, new_seats)
- Timestamp (changed_at, effective_date)

### subscription_usage
- Usage Snapshot (subscription_id, active_users, storage_used_gb, api_calls_month)
- Captured At (snapshot_date)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/platform/subscriptions` | Create subscription | `subscription.create` |
| GET | `/api/v1/platform/subscriptions` | List subscriptions | `subscription.read` |
| GET | `/api/v1/platform/subscriptions/{id}` | Get detail | `subscription.read` |
| PUT | `/api/v1/platform/subscriptions/{id}` | Full update | `subscription.update` |
| PATCH | `/api/v1/platform/subscriptions/{id}` | Status change | `subscription.update` |
| DELETE | `/api/v1/platform/subscriptions/{id}` | Cancel subscription | `subscription.cancel` |
| GET | `/api/v1/platform/subscriptions/search` | Search | `subscription.read` |
| GET | `/api/v1/platform/subscriptions/export` | Export | `subscription.export` |
| POST | `/api/v1/platform/subscriptions/{id}/renew` | Renew | `subscription.renew` |
| POST | `/api/v1/platform/subscriptions/{id}/upgrade` | Upgrade edition | `subscription.upgrade` |
| POST | `/api/v1/platform/subscriptions/{id}/reactivate` | Reactivate expired | `subscription.reactivate` |
| GET | `/api/v1/tenant/subscription` | Current tenant subscription | `subscription.read` |
| GET | `/api/v1/tenant/subscription/usage` | Usage vs limits | `subscription.read` |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Subscription List | List | Platform Admin | Filter by status, edition |
| Subscription Create | Create | Platform Admin | Tenant + edition + seats |
| Subscription Edit | Edit | Platform Admin | Dates, seats |
| Subscription View | View | Platform Admin, Tenant Admin | Usage bar, edition details |
| Subscription Search | Search | Platform Admin | |
| Subscription Renew | Approval | Platform Admin | Confirm renewal terms |
| Subscription Upgrade | Approval | Platform Admin, Tenant Admin | Edition comparison |
| Subscription History | History | Platform Admin, Tenant Admin | Change timeline |
| My Subscription | View | Tenant Admin | Self-service view |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `subscription.create` | Create subscription |
| `subscription.read` | View subscriptions |
| `subscription.update` | Edit subscription |
| `subscription.cancel` | Cancel subscription |
| `subscription.renew` | Process renewal |
| `subscription.upgrade` | Upgrade edition |
| `subscription.reactivate` | Reactivate expired |
| `subscription.export` | Export data |

| Actor | create | read | update | cancel | renew | upgrade |
|-------|:------:|:----:|:------:|:------:|:-----:|:-------:|
| Platform Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tenant Admin | — | ✓ (own) | — | — | — | request |
| Finance User | — | ✓ | — | — | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Trial started | Email | Tenant Admin | NTF-PF-003-01 |
| Trial expiring (5 days) | Email, Push | Tenant Admin | NTF-PF-003-02 |
| Subscription activated | Email | Tenant Admin, Finance User | NTF-PF-003-03 |
| Renewal reminder (30/15/7 days) | Email, SMS | Tenant Admin, Finance User | NTF-PF-003-04 |
| Subscription expired | Email, SMS, Push | Tenant Admin, Platform Admin | NTF-PF-003-05 |
| Edition upgraded | Email, Push | Tenant Admin | NTF-PF-003-06 |
| Seat limit approaching (90%) | Email, Internal | Tenant Admin | NTF-PF-003-07 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-003-01 | Subscription Register | Operational | Platform Admin | Per subscription | Status, edition | XLSX |
| RPT-PF-003-02 | Renewal Pipeline | Management | Sales Manager | Per subscription | Expiry window | PDF |
| RPT-PF-003-03 | Seat Utilisation | Operational | Tenant Admin | Per tenant | — | XLSX |
| RPT-PF-003-04 | MRR/ARR Dashboard | Executive | Leadership | Monthly | Edition | PDF |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Subscription created | subscription_id, tenant_id, edition_id, seats | Platform permanent |
| Status changed | old/new status, reason | Platform permanent |
| Edition changed | old/new edition_id | Platform permanent |
| Seats changed | old/new seat_count | Platform permanent |
| Renewal processed | new end_date | Platform permanent |
| Subscription cancelled | reason, cancelled_by | Platform permanent |

---

## 16. Acceptance Criteria

1. **AC-PF-003-01:** Given new tenant Euphoria, when provisioned, then TRIAL subscription created with correct edition and 30-day end date.
2. **AC-PF-003-02:** Given ACTIVE subscription with 50 seats and 50 active users, when admin reduces seats to 40, then operation fails (BR-PF-027).
3. **AC-PF-003-03:** Given subscription expires, when Scheduler runs, then tenant status becomes SUSPENDED within 1 hour (BR-PF-024).
4. **AC-PF-003-04:** Given edition upgrade Professional → Enterprise, when effective, then SSO configuration screens become visible without re-login.
5. **AC-PF-003-05:** Given subscription status change, when completed, then subscription_history row is created (BR-PF-026).

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Automated dunning and payment gateway integration |
| v2.0 | Self-service upgrade/downgrade by Tenant Admin |
| v2.0 | Usage-based billing (API calls, storage overage) |
| v3.0 | Multi-year subscription with milestone billing |
| v3.0 | Partner/reseller subscription management |

---

# PF-004 Organization Management

**Document ID:** ELU-BFS-PF-004  
**Module:** PF-004 — Organization Management  
**Sub Module:** PF-004-001 — Organization Structure  
**Feature:** PF-004-001-001 — Organization Profile  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

Organization Management defines the **top-level legal and operational entity** within a tenant. For Euphoria, the organization profile represents the company identity used across CRM, Sales, Finance, and HR contexts — registration numbers, tax identifiers, default currency, and fiscal calendar. A root organization is auto-created at tenant provisioning and serves as the parent for branches, departments, and business units.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Legal identity | GSTIN, PAN, CIN on invoices and contracts |
| Structural anchor | Parent node for branch/department hierarchy |
| Fiscal defaults | Fiscal year, default currency for transactions |
| Document branding | Organization name on PDF outputs |
| Multi-org readiness | Foundation for Enterprise multi-entity (v2) |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Organization profile CRUD | Multi-organization per tenant (v2 Enterprise) |
| Root organization auto-provision | Legal entity consolidation reporting |
| Tax and registration identifiers | Chart of accounts (FIN domain) |
| Organization hierarchy (parent-child for v2) | |
| Link to tenant | |

### 1.4 Users involved

Tenant Admin, Platform Admin, Finance User, Sales Manager.

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-004 |
| Sub Module ID | PF-004-001 |
| Feature ID | PF-004-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Community |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Create, update organization profile | View hierarchy |
| Platform Admin | Internal | View organization during onboarding | — |
| Finance User | Internal | View tax/registration details | Export |
| Sales Manager | Internal | View organization for proposals | — |
| System — Provisioning Engine | System | Auto-create root organization | — |

---

## 3. Business Story

During Euphoria tenant provisioning (PF-002), the Provisioning Engine creates a root `organization` record mirroring tenant legal details: name "Euphoria Infotech (I) Limited", code "EUPHORIA", type "ROOT". The **Tenant Admin** completes the organization profile: adds GSTIN, PAN, CIN, registered address (linked from tenant_address), default currency INR, fiscal year starting April.

The **Finance User** references organization tax details when configuring invoice templates (FIN domain). The **Sales Manager** sees organization name on quotation PDFs. When Euphoria opens a branch in Bengaluru (PF-005), the branch links to this root organization as parent.

The Tenant Admin updates organization legal name after a corporate rebrand. The system validates uniqueness within tenant and logs the change in audit trail. Organization status remains ACTIVE throughout.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Tenant Provisioned (PF-002)]
        │
        ▼
┌──────────────────┐
│ Auto-create ROOT │
│ organization     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ Tenant Admin     │────►│ Complete Profile │
│ edits profile    │     │ (tax, fiscal)    │
└────────┬─────────┘     └──────────────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ Branches (PF-005)│     │ Departments      │
│ link as children │     │ (PF-006) link    │
└──────────────────┘     └──────────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | System | Auto-create root org | Tenant data | `organization` (ROOT, ACTIVE) | Provisioning Engine |
| 2 | Tenant Admin | Complete profile | Org form | Updated `organization` | — |
| 3 | Tenant Admin | Add tax identifiers | GSTIN, PAN | Tax fields populated | Rule Engine |
| 4 | Tenant Admin | Set fiscal defaults | Currency, FY start | Fiscal config | — |
| 5 | System | Propagate org name to documents | Org name change | PDF template refresh | Notification Engine |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| DRAFT | Draft | Initial auto-created, incomplete | ACTIVE | System, Tenant Admin | Limited downstream use |
| ACTIVE | Active | Fully configured | INACTIVE, MERGED | Tenant Admin | Available for transactions |
| INACTIVE | Inactive | Temporarily disabled | ACTIVE, ARCHIVED | Tenant Admin | Hidden from selectors |
| MERGED | Merged | Absorbed into another org (v2) | — | Tenant Admin | Read-only |
| ARCHIVED | Archived | Historical | — | Tenant Admin | No new links |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-028 | Each tenant must have exactly one ROOT organization | Validation | Error | DB, Provisioning |
| BR-PF-029 | Organization `code` unique within tenant | Validation | Error | DB (UK tenant_id+code) |
| BR-PF-030 | GSTIN format validated per country rules (India: 15-char) | Validation | Error | API, Rule Engine |
| BR-PF-031 | ROOT organization cannot be deleted | Lifecycle | Error | API |
| BR-PF-032 | Organization name change propagates to open documents as of next generation | Calculation | Info | Document Engine |
| BR-PF-033 | Fiscal year start month must be 1–12 | Validation | Error | API |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| organization | Master | Organization profile and hierarchy | Yes |
| tenant | Master | Parent tenant | Yes |
| tenant_address | Master | Linked registered address | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| tenant | organization | 1:N | Restrict | Root org at provision |
| organization | organization | 1:N | Restrict | Parent-child hierarchy (v2) |
| organization | branch | 1:N | Restrict | Branches under org |
| organization | department | 1:N | Restrict | Departments under org |
| tenant_address | organization | N:1 | Set Null | Registered address FK |

---

## 9. Field Groups

### organization
- Identity (code, name, legal_name, short_name, organization_type)
- Registration (registration_number, cin, date_of_incorporation)
- Tax (gstin, pan, tan, tax_registration_type)
- Hierarchy (parent_organization_id, is_root, level)
- Fiscal (default_currency_code, fiscal_year_start_month)
- Contact (phone, email, website)
- Address (address_id FK to tenant_address)
- Status (status, is_active)
- Audit (created_by, created_on, modified_by, modified_on, is_deleted)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/org/organizations` | Create organization | `organization.create` |
| GET | `/api/v1/org/organizations` | List organizations | `organization.read` |
| GET | `/api/v1/org/organizations/{id}` | Get detail | `organization.read` |
| PUT | `/api/v1/org/organizations/{id}` | Full update | `organization.update` |
| PATCH | `/api/v1/org/organizations/{id}` | Partial update | `organization.update` |
| DELETE | `/api/v1/org/organizations/{id}` | Soft delete | `organization.delete` |
| GET | `/api/v1/org/organizations/search` | Search | `organization.read` |
| GET | `/api/v1/org/organizations/export` | Export | `organization.export` |
| GET | `/api/v1/org/organizations/root` | Get root organization | `organization.read` |
| GET | `/api/v1/org/organizations/{id}/hierarchy` | Get org tree | `organization.read` |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Organization List | List | Tenant Admin | Shows root + children |
| Organization Create | Create | Tenant Admin | Enterprise multi-org |
| Organization Edit | Edit | Tenant Admin | Tax, fiscal tabs |
| Organization View | View | All internal users | Summary card |
| Organization Search | Search | Tenant Admin | |
| Organization Hierarchy | View | Tenant Admin | Tree visualisation |
| Organization History | History | Tenant Admin | Audit timeline |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `organization.create` | Create organization |
| `organization.read` | View organizations |
| `organization.update` | Edit organization |
| `organization.delete` | Soft delete organization |
| `organization.export` | Export data |

| Actor | create | read | update | delete | export |
|-------|:------:|:----:|:------:|:------:|:------:|
| Tenant Admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| Finance User | — | ✓ | — | — | ✓ |
| Sales Manager | — | ✓ | — | — | — |
| Platform Admin | — | ✓ | — | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Organization profile completed | Internal | Tenant Admin | NTF-PF-004-01 |
| Organization name changed | Email, Internal | Finance User, Sales Manager | NTF-PF-004-02 |
| Tax identifier updated | Internal | Finance User | NTF-PF-004-03 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-004-01 | Organization Profile Summary | Operational | Tenant Admin | Per org | Status | PDF |
| RPT-PF-004-02 | Organization Hierarchy | Management | Tenant Admin | Tree | — | PDF |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Organization created | organization_id, code, name | Per tenant policy |
| Organization updated | field diff | Per tenant policy |
| Tax identifier changed | gstin/pan old/new (masked) | Per tenant policy |
| Status changed | old/new status | Per tenant policy |

---

## 16. Acceptance Criteria

1. **AC-PF-004-01:** Given tenant Euphoria provisioned, when checked, then exactly one ROOT organization exists (BR-PF-028).
2. **AC-PF-004-02:** Given invalid GSTIN format, when Tenant Admin saves, then validation error displayed (BR-PF-030).
3. **AC-PF-004-03:** Given ROOT organization, when delete attempted, then operation rejected (BR-PF-031).
4. **AC-PF-004-04:** Given organization name updated, when new quotation generated, then new name appears on PDF.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Multi-organization per tenant (Enterprise) |
| v2.0 | Organization-level P&L and consolidation |
| v3.0 | Cross-organization intercompany transactions |

---

# PF-005 Branch Management

**Document ID:** ELU-BFS-PF-005  
**Module:** PF-005 — Branch Management  
**Sub Module:** PF-005-001 — Branch Structure  
**Feature:** PF-005-001-001 — Branch Profile  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P1 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

Branch Management models **geographic and operational subdivisions** of Euphoria — offices in Kolkata, Bengaluru, Mumbai. Branches enable location-based data segregation, branch-scoped reporting, user assignment, and address management for a multi-location IT services company.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Geographic operations | Track leads, projects, invoices by branch |
| User assignment | Users belong to a home branch |
| Branch-level reporting | MIS dashboards filtered by branch |
| Address management | Branch-specific contact and address |
| Edition gating | Professional+ feature |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Branch profile CRUD | Warehouse/location inventory (v3) |
| Branch hierarchy (region → branch) | GPS tracking |
| Branch head assignment | |
| Branch status lifecycle | |
| Link to organization | |

### 1.4 Users involved

Tenant Admin, Sales Manager, Project Manager, Finance User.

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-005 |
| Sub Module ID | PF-005-001 |
| Feature ID | PF-005-001-001 |
| Priority | P1 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Professional |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Create, update, deactivate branches | Assign branch heads |
| Sales Manager | Internal | View branches for territory mapping | Filter reports by branch |
| Project Manager | Internal | View branch for project assignment | — |
| Finance User | Internal | View branch for invoicing | — |
| System | System | Enforce edition gate (Professional+) | — |

---

## 3. Business Story

The **Tenant Admin** at Euphoria creates the headquarters branch: code "HQ-KOL", name "Kolkata Head Office", type "HEAD_OFFICE", linked to root organization. Address details entered; branch head assigned to a Senior Manager user.

Euphoria expands: Tenant Admin creates "BLR-01" Bengaluru Branch and "MUM-01" Mumbai Branch, type "BRANCH", with respective addresses and branch heads. **Sales Manager** assigns leads to Bengaluru branch. **Project Manager** creates projects scoped to Kolkata HQ.

A branch is temporarily closed: Tenant Admin sets status INACTIVE. Users assigned to that branch are prompted to select alternate branch. Reports exclude inactive branches by default. Branch cannot be deleted if open projects exist (Restrict).

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Tenant Admin]
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Create Branch│────►│ Assign Head  │────►│ ACTIVE       │
│ (profile)    │     │ + Address    │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌────────────────────────────┤
                     ▼                            ▼
              ┌──────────────┐            ┌──────────────┐
              │ Users assigned│            │ Transactions │
              │ to branch     │            │ scoped       │
              └──────────────┘            └──────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Tenant Admin | Create branch | Branch form | `branch` (DRAFT) | — |
| 2 | Tenant Admin | Set address and head | Branch id | Updated branch | — |
| 3 | Tenant Admin | Activate branch | Branch id | `branch` (ACTIVE) | — |
| 4 | Tenant Admin | Assign users to branch | User ids | `user.branch_id` updated | — |
| 5 | Tenant Admin | Deactivate branch | Branch id | `branch` (INACTIVE) | Workflow Engine |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| DRAFT | Draft | Being configured | ACTIVE, CANCELLED | Tenant Admin | Not selectable |
| ACTIVE | Active | Operational | INACTIVE | Tenant Admin | Selectable in UI |
| INACTIVE | Inactive | Temporarily closed | ACTIVE, ARCHIVED | Tenant Admin | Hidden from selectors |
| ARCHIVED | Archived | Permanent closure | — | Tenant Admin | Read-only |
| CANCELLED | Cancelled | Draft discarded | — | Tenant Admin | Deletable |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-034 | Branch feature requires Professional or Enterprise edition | Security | Error | Rule Engine |
| BR-PF-035 | Branch `code` unique within tenant | Validation | Error | DB (UK) |
| BR-PF-036 | At least one HEAD_OFFICE branch per tenant recommended | Validation | Warning | API |
| BR-PF-037 | Branch with active projects cannot be deleted | Lifecycle | Error | DB (Restrict) |
| BR-PF-038 | Branch head must be an ACTIVE user in same tenant | Validation | Error | API |
| BR-PF-039 | Maximum branches per edition: Professional=10, Enterprise=unlimited | Validation | Error | Rule Engine |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| branch | Master | Branch profile | Yes |
| branch_address | Master | Branch-specific address | Yes |
| organization | Master | Parent organization FK | Yes |
| users | Master | branch_id FK on users | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| organization | branch | 1:N | Restrict | Org owns branches |
| branch | branch | 1:N | Restrict | Region → branch hierarchy |
| branch | branch_address | 1:1 | Cascade | Address |
| branch | users | 1:N | Set Null | User home branch |
| branch | department | 1:N | Restrict | Depts within branch |

---

## 9. Field Groups

### branch
- Identity (code, name, branch_type: HEAD_OFFICE, BRANCH, REGIONAL_OFFICE)
- Hierarchy (parent_branch_id, organization_id)
- Leadership (branch_head_user_id)
- Contact (phone, email)
- Address (branch_address_id)
- Operational (timezone_id, working_hours)
- Status (status, is_active, opened_date, closed_date)
- Audit (created_by, created_on, modified_by, modified_on, is_deleted)

### branch_address
- Location (address_line_1, address_line_2, city, state, postal_code, country_code)
- Geo (latitude, longitude)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/org/branches` | Create branch | `branch.create` |
| GET | `/api/v1/org/branches` | List branches | `branch.read` |
| GET | `/api/v1/org/branches/{id}` | Get detail | `branch.read` |
| PUT | `/api/v1/org/branches/{id}` | Full update | `branch.update` |
| PATCH | `/api/v1/org/branches/{id}` | Partial/status | `branch.update` |
| DELETE | `/api/v1/org/branches/{id}` | Soft delete | `branch.delete` |
| GET | `/api/v1/org/branches/search` | Search | `branch.read` |
| GET | `/api/v1/org/branches/export` | Export | `branch.export` |
| GET | `/api/v1/org/branches/hierarchy` | Branch tree | `branch.read` |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Branch List | List | Tenant Admin | Status, type filters |
| Branch Create | Create | Tenant Admin | |
| Branch Edit | Edit | Tenant Admin | Address, head assignment |
| Branch View | View | All internal | |
| Branch Search | Search | Tenant Admin | |
| Branch Hierarchy | View | Tenant Admin | Tree view |
| Branch History | History | Tenant Admin | |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `branch.create` | Create branch |
| `branch.read` | View branches |
| `branch.update` | Edit branch |
| `branch.delete` | Delete branch |
| `branch.export` | Export |

| Actor | create | read | update | delete |
|-------|:------:|:----:|:------:|:------:|
| Tenant Admin | ✓ | ✓ | ✓ | ✓ |
| Sales Manager | — | ✓ | — | — |
| Project Manager | — | ✓ | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Branch created | Internal | Tenant Admin, Branch Head | NTF-PF-005-01 |
| Branch deactivated | Email, Internal | Branch Head, assigned users | NTF-PF-005-02 |
| Branch head assigned | Email, Push | New branch head | NTF-PF-005-03 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-005-01 | Branch Directory | Operational | Tenant Admin | Per branch | Status, type | XLSX |
| RPT-PF-005-02 | Branch Performance Summary | Management | Sales Manager | Per branch | Date range | PDF |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Branch created | branch_id, code, name | Per tenant policy |
| Branch updated | field diff | Per tenant policy |
| Branch head changed | old/new user_id | Per tenant policy |
| Status changed | old/new status | Per tenant policy |

---

## 16. Acceptance Criteria

1. **AC-PF-005-01:** Given Community edition tenant, when branch create attempted, then rejected (BR-PF-034).
2. **AC-PF-005-02:** Given branch with open projects, when delete attempted, then rejected (BR-PF-037).
3. **AC-PF-005-03:** Given Professional tenant with 10 branches, when 11th branch created, then rejected (BR-PF-039).
4. **AC-PF-005-04:** Given active branch, when user assigned, then user.branch_id updated and visible in profile.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Branch-level P&L and cost centre mapping |
| v2.0 | Geo-map visualisation of branches |
| v3.0 | Branch operating hours and holiday calendar |

---

# PF-006 Department Management

**Document ID:** ELU-BFS-PF-006  
**Module:** PF-006 — Department Management  
**Sub Module:** PF-006-001 — Department Structure  
**Feature:** PF-006-001-001 — Department Profile  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

Department Management models **functional divisions** within Euphoria — Sales, Delivery, Finance, HR, Support. Departments enable user grouping, approval routing, workload allocation, and departmental reporting across the CRM/ERP platform.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Functional structure | Mirror real org chart |
| Approval routing | Route approvals to department heads |
| Workload management | Assign leads/tickets/projects by department |
| Reporting | Department-level KPIs and dashboards |
| RBAC scoping | Department-scoped data visibility (v2) |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Department CRUD and hierarchy | Full HR org chart / payroll |
| Department head assignment | Employee grade/band management |
| Parent-child department tree | |
| Link to organization and branch | |

### 1.4 Users involved

Tenant Admin, Sales Manager, Project Manager, Support Agent.

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-006 |
| Sub Module ID | PF-006-001 |
| Feature ID | PF-006-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Community |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Create, update, reorganise departments | Assign department heads |
| Sales Manager | Internal | View Sales department structure | Filter by department |
| Project Manager | Internal | View Delivery department | Assign team by dept |
| Support Agent | Internal | View Support department | — |

---

## 3. Business Story

The **Tenant Admin** at Euphoria sets up core departments: SALES, DELIVERY, FINANCE, HR, SUPPORT — each with a unique code, linked to root organization. Department head assigned (e.g. Sales Manager to SALES department). Sub-departments created: SALES → Pre-Sales, Inside Sales.

**Sales Manager** filters lead pipeline by SALES department. **Project Manager** assigns project tasks to DELIVERY sub-teams. When reorganising, Tenant Admin moves "Inside Sales" under a new "Business Development" parent department. Users with `department_id` are unaffected; only hierarchy changes.

Department deactivated when function is outsourced: status INACTIVE, users reassigned. Approval workflows (CPS-001) resolve approvers via department head chain.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Tenant Admin]
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Create Dept  │────►│ Assign Head  │────►│ ACTIVE       │
│ (code, name) │     │ + Parent     │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌────────────────────────────┤
                     ▼                            ▼
              ┌──────────────┐            ┌──────────────┐
              │ Users linked │            │ Approvals    │
              │ (dept_id)    │            │ routed       │
              └──────────────┘            └──────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Tenant Admin | Create department | Dept form | `department` (ACTIVE) | — |
| 2 | Tenant Admin | Set parent and head | Dept id | Hierarchy updated | — |
| 3 | Tenant Admin | Assign users | User ids | `user.department_id` | — |
| 4 | System | Route approval to dept head | Approval request | Approver resolved | Workflow Engine |
| 5 | Tenant Admin | Deactivate department | Dept id | INACTIVE | Workflow Engine |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| ACTIVE | Active | Operational | INACTIVE | Tenant Admin | Selectable |
| INACTIVE | Inactive | Disabled | ACTIVE, ARCHIVED | Tenant Admin | Hidden from selectors |
| ARCHIVED | Archived | Permanent | — | Tenant Admin | Read-only |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-040 | Department `code` unique within tenant | Validation | Error | DB (UK) |
| BR-PF-041 | Department hierarchy max depth = 5 levels | Validation | Error | API |
| BR-PF-042 | Circular parent references prohibited | Validation | Error | API |
| BR-PF-043 | Department head must be ACTIVE user in same tenant | Validation | Error | API |
| BR-PF-044 | Department with assigned users cannot be deleted | Lifecycle | Error | DB (Restrict) |
| BR-PF-045 | At least one department recommended per tenant | Validation | Warning | API |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| department | Master | Department profile and hierarchy | Yes |
| organization | Master | Parent organization FK | Yes |
| branch | Master | Optional branch FK | Yes |
| users | Master | department_id FK | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| organization | department | 1:N | Restrict | |
| branch | department | 1:N | Set Null | Optional branch scope |
| department | department | 1:N | Restrict | Parent-child tree |
| department | users | 1:N | Set Null | User assignment |

---

## 9. Field Groups

### department
- Identity (code, name, description, department_type)
- Hierarchy (parent_department_id, organization_id, branch_id, level, path)
- Leadership (department_head_user_id)
- Operational (cost_centre_code)
- Status (status, is_active)
- Audit (created_by, created_on, modified_by, modified_on, is_deleted)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/org/departments` | Create department | `department.create` |
| GET | `/api/v1/org/departments` | List departments | `department.read` |
| GET | `/api/v1/org/departments/{id}` | Get detail | `department.read` |
| PUT | `/api/v1/org/departments/{id}` | Full update | `department.update` |
| PATCH | `/api/v1/org/departments/{id}` | Partial update | `department.update` |
| DELETE | `/api/v1/org/departments/{id}` | Soft delete | `department.delete` |
| GET | `/api/v1/org/departments/search` | Search | `department.read` |
| GET | `/api/v1/org/departments/export` | Export | `department.export` |
| GET | `/api/v1/org/departments/hierarchy` | Department tree | `department.read` |
| PATCH | `/api/v1/org/departments/{id}/move` | Reparent department | `department.update` |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Department List | List | Tenant Admin | Tree and flat views |
| Department Create | Create | Tenant Admin | Parent selector |
| Department Edit | Edit | Tenant Admin | Head assignment |
| Department View | View | All internal | |
| Department Search | Search | Tenant Admin | |
| Department Hierarchy | View | Tenant Admin | Drag-drop reparent (v2) |
| Department History | History | Tenant Admin | |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `department.create` | Create department |
| `department.read` | View departments |
| `department.update` | Edit department |
| `department.delete` | Delete department |
| `department.export` | Export |

| Actor | create | read | update | delete |
|-------|:------:|:----:|:------:|:------:|
| Tenant Admin | ✓ | ✓ | ✓ | ✓ |
| Sales Manager | — | ✓ | — | — |
| Project Manager | — | ✓ | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Department created | Internal | Tenant Admin | NTF-PF-006-01 |
| Department head assigned | Email, Push | New head | NTF-PF-006-02 |
| Department reorganised | Internal | Affected dept heads | NTF-PF-006-03 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-006-01 | Department Directory | Operational | Tenant Admin | Per dept | Status | XLSX |
| RPT-PF-006-02 | Headcount by Department | Management | Tenant Admin | Per dept | Branch | PDF |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Department created | department_id, code | Per tenant policy |
| Department updated | field diff | Per tenant policy |
| Department reparented | old/new parent_id | Per tenant policy |
| Head changed | old/new user_id | Per tenant policy |

---

## 16. Acceptance Criteria

1. **AC-PF-006-01:** Given department hierarchy 5 levels deep, when 6th level created, then rejected (BR-PF-041).
2. **AC-PF-006-02:** Given circular parent assignment, when saved, then rejected (BR-PF-042).
3. **AC-PF-006-03:** Given department with users, when delete attempted, then rejected (BR-PF-044).
4. **AC-PF-006-04:** Given approval workflow with dept head resolver, when triggered, then correct head receives approval task.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Department-scoped data visibility rules |
| v2.0 | Drag-drop org chart editor |
| v3.0 | Department budget and cost allocation |

---

# PF-007 Business Unit Management

**Document ID:** ELU-BFS-PF-007  
**Module:** PF-007 — Business Unit Management  
**Sub Module:** PF-007-001 — Business Unit  
**Feature:** PF-007-001-001 — Business Unit Profile  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P1 / Phase 2 / R1.1  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

Business Unit Management provides a **cross-functional P&L dimension** for Euphoria — distinct lines of business such as "Software Development", "Managed Services", "Training". Unlike departments (functional), business units represent revenue/cost centres used for opportunity segmentation, project accounting, and executive reporting.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| P&L segmentation | Revenue and cost by business line |
| Sales targeting | Quotas and pipelines per BU |
| Project accounting | Projects tagged to business unit |
| Executive reporting | BU-level dashboards |
| Edition gating | Professional+ feature |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Business unit CRUD | Full GL / chart of accounts |
| BU manager assignment | Automated P&L calculation (FIN v2) |
| Link to organization | |
| BU status lifecycle | |

### 1.4 Users involved

Tenant Admin, Sales Manager, Finance User, Project Manager.

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-007 |
| Sub Module ID | PF-007-001 |
| Feature ID | PF-007-001-001 |
| Priority | P1 |
| Phase | 2 |
| Release | R1.1 |
| Minimum Edition | Professional |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Create, update business units | Assign BU managers |
| Sales Manager | Internal | Tag opportunities to BU | Filter pipeline by BU |
| Finance User | Internal | View BU for invoicing | BU revenue reports |
| Project Manager | Internal | Assign projects to BU | — |

---

## 3. Business Story

The **Tenant Admin** at Euphoria creates business units: "SW-DEV" (Software Development), "MGD-SVC" (Managed Services), "TRAINING" (Corporate Training). Each has a BU Manager assigned from senior leadership.

**Sales Manager** tags a new Opportunity to "SW-DEV" business unit. **Project Manager** creates a project under the same BU. **Finance User** generates invoices with BU code for revenue recognition. Executive dashboard shows revenue split across BUs.

When Euphoria discontinues Training division, Tenant Admin sets BU to INACTIVE. New opportunities cannot select it; historical data retained.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Tenant Admin]
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Create BU    │────►│ Assign       │────►│ ACTIVE       │
│ (code, name) │     │ BU Manager   │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌────────────────────────────┤
                     ▼                            ▼
              ┌──────────────┐            ┌──────────────┐
              │ Opportunities│            │ Projects &   │
              │ tagged to BU │            │ Invoices     │
              └──────────────┘            └──────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Tenant Admin | Create BU | BU form | `business_unit` (ACTIVE) | — |
| 2 | Tenant Admin | Assign BU manager | User id | Manager linked | — |
| 3 | Sales Manager | Tag opportunity to BU | Opportunity + BU | BU FK set | — |
| 4 | Finance User | View BU revenue report | BU id, date range | Report data | Reporting Engine |
| 5 | Tenant Admin | Deactivate BU | BU id | INACTIVE | — |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| ACTIVE | Active | Operational | INACTIVE | Tenant Admin | Selectable |
| INACTIVE | Inactive | Discontinued | ACTIVE, ARCHIVED | Tenant Admin | Hidden from new records |
| ARCHIVED | Archived | Historical | — | Tenant Admin | Read-only |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-046 | Business unit feature requires Professional or Enterprise edition | Security | Error | Rule Engine |
| BR-PF-047 | BU `code` unique within tenant | Validation | Error | DB (UK) |
| BR-PF-048 | BU manager must be ACTIVE user in same tenant | Validation | Error | API |
| BR-PF-049 | INACTIVE BU cannot be assigned to new opportunities/projects | Lifecycle | Error | API |
| BR-PF-050 | Maximum BUs: Professional=20, Enterprise=unlimited | Validation | Error | Rule Engine |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| business_unit | Master | Business unit profile | Yes |
| organization | Master | Parent organization FK | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| organization | business_unit | 1:N | Restrict | |
| business_unit | opportunity | 1:N | Restrict | CRM domain |
| business_unit | project | 1:N | Restrict | PRJ domain |
| business_unit | invoice | 1:N | Set Null | FIN domain |

---

## 9. Field Groups

### business_unit
- Identity (code, name, description)
- Management (bu_manager_user_id, organization_id)
- Financial (cost_centre_code, revenue_target_annual)
- Status (status, is_active, start_date, end_date)
- Audit (created_by, created_on, modified_by, modified_on, is_deleted)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/org/business-units` | Create BU | `business_unit.create` |
| GET | `/api/v1/org/business-units` | List BUs | `business_unit.read` |
| GET | `/api/v1/org/business-units/{id}` | Get detail | `business_unit.read` |
| PUT | `/api/v1/org/business-units/{id}` | Full update | `business_unit.update` |
| PATCH | `/api/v1/org/business-units/{id}` | Partial update | `business_unit.update` |
| DELETE | `/api/v1/org/business-units/{id}` | Soft delete | `business_unit.delete` |
| GET | `/api/v1/org/business-units/search` | Search | `business_unit.read` |
| GET | `/api/v1/org/business-units/export` | Export | `business_unit.export` |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Business Unit List | List | Tenant Admin | |
| Business Unit Create | Create | Tenant Admin | |
| Business Unit Edit | Edit | Tenant Admin | Manager assignment |
| Business Unit View | View | All internal | |
| Business Unit Search | Search | Tenant Admin | |
| Business Unit History | History | Tenant Admin | |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `business_unit.create` | Create BU |
| `business_unit.read` | View BUs |
| `business_unit.update` | Edit BU |
| `business_unit.delete` | Delete BU |
| `business_unit.export` | Export |

| Actor | create | read | update | delete |
|-------|:------:|:----:|:------:|:------:|
| Tenant Admin | ✓ | ✓ | ✓ | ✓ |
| Sales Manager | — | ✓ | — | — |
| Finance User | — | ✓ | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| BU created | Internal | Tenant Admin, BU Manager | NTF-PF-007-01 |
| BU manager assigned | Email, Push | New manager | NTF-PF-007-02 |
| BU deactivated | Internal | BU Manager, Finance User | NTF-PF-007-03 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-007-01 | Business Unit Directory | Operational | Tenant Admin | Per BU | Status | XLSX |
| RPT-PF-007-02 | Revenue by Business Unit | Management | Finance User | Per BU | Period | PDF, XLSX |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| BU created | business_unit_id, code | Per tenant policy |
| BU updated | field diff | Per tenant policy |
| Manager changed | old/new user_id | Per tenant policy |
| Status changed | old/new status | Per tenant policy |

---

## 16. Acceptance Criteria

1. **AC-PF-007-01:** Given Community edition, when BU create attempted, then rejected (BR-PF-046).
2. **AC-PF-007-02:** Given INACTIVE BU, when assigned to new opportunity, then rejected (BR-PF-049).
3. **AC-PF-007-03:** Given opportunity tagged to BU, when BU revenue report run, then opportunity value included.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Automated P&L by business unit |
| v2.0 | BU-level quota and target management |
| v3.0 | Cross-BU resource sharing and transfer pricing |

---

# PF-008 User & Identity Management

**Document ID:** ELU-BFS-PF-008  
**Module:** PF-008 — User & Identity Management  
**Sub Module:** PF-008-001 — User Account  
**Feature:** PF-008-001-001 — User Registration  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

User & Identity Management governs **who can access E-LinkUp** within tenant Euphoria. User Registration provisions accounts, assigns organizational context (branch, department), issues JWT credentials, and enforces authentication policies defined in tenant_security. It is the identity layer upon which RBAC (PF-009) and audit (PF-010) depend.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Secure access | Argon2id passwords, JWT + refresh tokens |
| Seat enforcement | User count bounded by subscription |
| Org context | Users linked to branch, department, BU |
| Self-service | Profile management, password reset |
| Enterprise auth | MFA (Professional+), SSO (Enterprise) |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| User registration (invite and self) | Customer portal users (SRV domain) |
| Authentication (login, logout, refresh) | OAuth social login (v2) |
| Password management (reset, change) | Biometric auth (Android v2) |
| User profile CRUD | SCIM provisioning (v3) |
| User status lifecycle | |
| MFA enrollment (Professional+) | |

### 1.4 Users involved

Tenant Admin, Platform Admin, all CRM users, System (Auth Service, Notification Engine).

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-008 |
| Sub Module ID | PF-008-001 |
| Feature ID | PF-008-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Community |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Invite users, activate, deactivate | Reset passwords |
| Platform Admin | Internal | View users across tenants | Force logout |
| Sales Executive | Internal | Manage own profile | Change password |
| System — Auth Service | System | Issue/validate JWT, refresh tokens | Enforce MFA |
| System — Notification Engine | System | Send invite and reset emails | — |

---

## 3. Business Story

After Euphoria tenant activation (PF-002), the designated **Tenant Admin** receives an activation email. They set password (meeting tenant_security policy: min 12 chars, complexity), complete MFA enrollment (Professional edition), and land on the dashboard.

The Tenant Admin invites a **Sales Executive**: enters email, name, assigns role (PF-009), branch (Kolkata HQ), department (Sales). System checks subscription seat limit (BR-PF-022). Invite email sent with 72-hour token. Sales Executive activates account, sets password, logs in via Flutter Web.

Login flow: credentials → Auth Service validates → issues access JWT (15 min) + refresh token (7 days, httpOnly cookie). JWT claims include: `user_id`, `tenant_id`, `edition`, `roles[]`, `permissions[]`. API middleware extracts tenant_id from JWT, never from request body.

Tenant Admin deactivates a departing employee: user status INACTIVE, all refresh tokens revoked, active sessions invalidated. User cannot login. Audit trail records deactivation.

Enterprise edition: SSO via SAML/OIDC configured in tenant_security. User authenticates via corporate IdP; E-LinkUp JIT-provisions user on first SSO login.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Tenant Admin] ──invite──► [System: Create User (INVITED)]
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ Send Invite     │
                           │ Email           │
                           └────────┬────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ User Activates  │
                           │ (set password)  │
                           └────────┬────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ ACTIVE          │
                           └────────┬────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
       ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
       │ Login       │     │ JWT issued  │     │ Access CRM  │
       │ (email+pwd) │     │ + refresh   │     │ modules     │
       └─────────────┘     └─────────────┘     └─────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Tenant Admin | Invite user | User form + role | `users` (INVITED) | — |
| 2 | System | Check seat limit | Subscription | Pass/Fail | Subscription Engine |
| 3 | System | Send invite email | Email, token | Notification sent | Notification Engine |
| 4 | User | Activate account | Token + password | `users` (ACTIVE) | Auth Service |
| 5 | User | Login | Credentials | JWT + refresh | Auth Service |
| 6 | User | Refresh token | Refresh token | New access JWT | Auth Service |
| 7 | Tenant Admin | Deactivate user | User id | `users` (INACTIVE) | Auth Service |
| 8 | System | Revoke sessions | User id | Tokens invalidated | Auth Service |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| INVITED | Invited | Awaiting activation | ACTIVE, EXPIRED, CANCELLED | Tenant Admin | Invite token valid 72h |
| ACTIVE | Active | Can login | INACTIVE, LOCKED | User, Tenant Admin | Full access per RBAC |
| INACTIVE | Inactive | Deactivated | ACTIVE | Tenant Admin | Login blocked |
| LOCKED | Locked | Too many failed logins | ACTIVE | System, Tenant Admin | Login blocked temporarily |
| EXPIRED | Expired | Invite token expired | INVITED (re-invite) | System | Re-invite required |
| CANCELLED | Cancelled | Invite withdrawn | — | Tenant Admin | — |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-051 | User `email` unique within tenant | Validation | Error | DB (UK tenant_id+email) |
| BR-PF-052 | Active user count cannot exceed subscription seat_count | Validation | Error | API, Subscription Engine |
| BR-PF-053 | Password must meet tenant_security policy | Validation | Error | API, Auth Service |
| BR-PF-054 | Invite token expires after 72 hours | Lifecycle | Error | Auth Service |
| BR-PF-055 | 5 failed login attempts locks account for 30 minutes | Security | Error | Auth Service |
| BR-PF-056 | JWT access token TTL = 15 minutes; refresh = 7 days | Security | Info | Auth Service |
| BR-PF-057 | Deactivated user refresh tokens immediately revoked | Security | Error | Auth Service |
| BR-PF-058 | MFA required when tenant_security.mfa_required = true | Security | Error | Auth Service |
| BR-PF-059 | User must belong to same tenant as JWT tenant_id claim | Security | Error | API middleware |
| BR-PF-060 | At least one ACTIVE Tenant Admin per tenant at all times | Validation | Error | API |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| users | Master | User account profile | Yes |
| user_credentials | Master | Password hash (separate table) | Yes |
| user_session | Transaction | Active sessions / refresh tokens | Yes |
| user_mfa | Master | MFA enrollment (TOTP, backup codes) | Yes |
| user_invite | Transaction | Pending invitations | Yes |
| user_password_history | Audit | Password history for policy | Yes |
| tenant | Master | Parent tenant | Yes |
| branch | Master | FK branch_id | Yes |
| department | Master | FK department_id | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| tenant | users | 1:N | Restrict | |
| branch | users | 1:N | Set Null | Home branch |
| department | users | 1:N | Set Null | Department |
| users | user_credentials | 1:1 | Cascade | Separated for security |
| users | user_session | 1:N | Cascade | Sessions |
| users | user_mfa | 1:1 | Cascade | MFA config |
| users | user_role | 1:N | Cascade | RBAC (PF-009) |

---

## 9. Field Groups

### users
- Identity (email, username, employee_code)
- Personal (salutation, first_name, last_name, display_name, avatar_url)
- Contact (phone, mobile)
- Organizational (branch_id, department_id, business_unit_id, designation, reporting_manager_id)
- Authentication (auth_method: LOCAL, SSO; last_login_at, failed_login_count)
- Status (status, is_active, invited_at, activated_at, deactivated_at)
- Preferences (locale_override, timezone_override, theme)
- Audit (created_by, created_on, modified_by, modified_on, is_deleted)

### user_credentials
- Credential (password_hash, hash_algorithm, password_changed_at)
- Lock (locked_until, failed_attempts)

### user_session
- Session (session_token_hash, refresh_token_hash, device_info, ip_address)
- Timing (created_at, expires_at, last_activity_at)
- Status (is_active, revoked_at)

### user_mfa
- MFA Config (mfa_type: TOTP, method_enabled, secret_encrypted)
- Backup (backup_codes_hash, backup_codes_remaining)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/auth/register` | Activate invited user | Public (token) |
| POST | `/api/v1/auth/login` | Login | Public |
| POST | `/api/v1/auth/logout` | Logout | Authenticated |
| POST | `/api/v1/auth/refresh` | Refresh access token | Refresh token |
| POST | `/api/v1/auth/forgot-password` | Request reset | Public |
| POST | `/api/v1/auth/reset-password` | Reset password | Public (token) |
| POST | `/api/v1/auth/change-password` | Change password | Authenticated |
| POST | `/api/v1/auth/mfa/enroll` | Enroll MFA | Authenticated |
| POST | `/api/v1/auth/mfa/verify` | Verify MFA code | Authenticated |
| POST | `/api/v1/users` | Invite/create user | `user.create` |
| GET | `/api/v1/users` | List users | `user.read` |
| GET | `/api/v1/users/{id}` | Get user detail | `user.read` |
| PUT | `/api/v1/users/{id}` | Full update | `user.update` |
| PATCH | `/api/v1/users/{id}` | Partial update / status | `user.update` |
| DELETE | `/api/v1/users/{id}` | Deactivate user | `user.delete` |
| GET | `/api/v1/users/search` | Search users | `user.read` |
| GET | `/api/v1/users/export` | Export users | `user.export` |
| POST | `/api/v1/users/{id}/reinvite` | Resend invite | `user.create` |
| POST | `/api/v1/users/{id}/reset-password` | Admin reset | `user.reset_password` |
| GET | `/api/v1/users/me` | Current user profile | Authenticated |
| PUT | `/api/v1/users/me` | Update own profile | Authenticated |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Login | View | All users | Email + password + MFA |
| Forgot Password | View | All users | |
| Reset Password | View | All users | Token from email |
| User List | List | Tenant Admin | Status, role, branch filters |
| User Invite | Create | Tenant Admin | Role, branch, dept assignment |
| User Edit | Edit | Tenant Admin | |
| User View | View | Tenant Admin, Self | |
| User Search | Search | Tenant Admin | |
| My Profile | Edit | All users | Avatar, contact, preferences |
| Change Password | Edit | All users | |
| MFA Setup | Edit | All users | QR code for TOTP |
| User Sessions | View | Tenant Admin, Self | Active sessions, revoke |
| User History | History | Tenant Admin | Login and change audit |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `user.create` | Invite/create users |
| `user.read` | View users |
| `user.update` | Edit users |
| `user.delete` | Deactivate users |
| `user.export` | Export user list |
| `user.reset_password` | Admin password reset |
| `user.impersonate` | Login as user (Platform Admin) |

| Actor | create | read | update | delete | reset_password |
|-------|:------:|:----:|:------:|:------:|:--------------:|
| Tenant Admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| Platform Admin | ✓ | ✓ (all tenants) | ✓ | ✓ | ✓ |
| Sales Executive | — | ✓ (self) | ✓ (self) | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| User invited | Email | Invited user | NTF-PF-008-01 |
| Account activated | Email, Push | User, Tenant Admin | NTF-PF-008-02 |
| Password reset requested | Email | User | NTF-PF-008-03 |
| Password changed | Email | User | NTF-PF-008-04 |
| Account locked | Email, SMS | User, Tenant Admin | NTF-PF-008-05 |
| User deactivated | Email | User, Tenant Admin | NTF-PF-008-06 |
| MFA enrolled | Email | User | NTF-PF-008-07 |
| New login from unknown device | Email, Push | User | NTF-PF-008-08 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-008-01 | User Directory | Operational | Tenant Admin | Per user | Status, branch, dept | XLSX |
| RPT-PF-008-02 | Login Activity | Operational | Tenant Admin | Per login event | Date, user | XLSX |
| RPT-PF-008-03 | Seat Utilisation | Management | Tenant Admin | Per tenant | — | PDF |
| RPT-PF-008-04 | Inactive Users | Operational | Tenant Admin | Per user | Days since login | XLSX |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| User created/invited | user_id, email, role | Per tenant policy |
| User activated | user_id, timestamp | Per tenant policy |
| Login success | user_id, ip, device | Per tenant policy |
| Login failure | email, ip, reason | Per tenant policy |
| Password changed | user_id | Per tenant policy |
| User deactivated | user_id, reason, actor | Per tenant policy |
| MFA enrolled/disabled | user_id, mfa_type | Per tenant policy |
| Session revoked | user_id, session_id | Per tenant policy |

---

## 16. Acceptance Criteria

1. **AC-PF-008-01:** Given Tenant Admin invites user within seat limit, when invite sent, then user receives email with valid 72h token.
2. **AC-PF-008-02:** Given seat limit reached, when new user invited, then rejected (BR-PF-052).
3. **AC-PF-008-03:** Given valid credentials, when login, then JWT issued with correct tenant_id and roles in claims.
4. **AC-PF-008-04:** Given 5 failed logins, when 6th attempted, then account LOCKED (BR-PF-055).
5. **AC-PF-008-05:** Given deactivated user, when login attempted, then authentication fails.
6. **AC-PF-008-06:** Given MFA required, when login without MFA, then MFA challenge presented (BR-PF-058).
7. **AC-PF-008-07:** Given two tenants, when user of Euphoria queries user list, then only Euphoria users returned.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | SSO via SAML 2.0 and OIDC (Enterprise) |
| v2.0 | Social login (Google, Microsoft) |
| v2.0 | Biometric authentication on Android |
| v3.0 | SCIM 2.0 user provisioning |
| v3.0 | Adaptive authentication (risk-based MFA) |

---

# PF-009 Roles & Permissions (RBAC)

**Document ID:** ELU-BFS-PF-009  
**Module:** PF-009 — Roles & Permissions (RBAC)  
**Sub Module:** PF-009-001 — Role Management  
**Feature:** PF-009-001-001 — Role & Permission Assignment  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

RBAC controls **what each Euphoria user can see and do** across all E-LinkUp modules. Role Management defines roles (Tenant Admin, Sales Manager, Sales Executive, etc.), maps granular permissions (`lead.create`, `invoice.approve`), and assigns roles to users. Server-side enforcement ensures UI visibility and API access are consistent and secure.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Least privilege | Users access only what their role permits |
| Configurable access | Tenant Admin customises roles within edition limits |
| Consistent enforcement | Same permissions on Flutter UI and FastAPI |
| Compliance | Segregation of duties for finance approvals |
| Scalability | Permission catalogue grows with new modules |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Role CRUD (system + custom) | Attribute-based access control (v3) |
| Permission catalogue management | Row-level security rules (v2) |
| Role-permission mapping | Dynamic policy engine (v3) |
| User-role assignment | |
| Permission check middleware | |
| Edition-based role limits | |

### 1.4 Users involved

Tenant Admin, Platform Admin, all CRM users (permission recipients), System (Auth Service, API middleware).

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-009 |
| Sub Module ID | PF-009-001 |
| Feature ID | PF-009-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Community (5 roles); Professional (25); Enterprise (unlimited) |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Create custom roles, assign permissions, assign roles to users | Clone system roles |
| Platform Admin | Internal | Manage system role templates, seed permission catalogue | View role usage |
| Sales Manager | Internal | Use assigned permissions | — |
| System — Auth Service | System | Embed permissions in JWT | Refresh on role change |
| System — API Middleware | System | Enforce permission checks | Return 403 |

---

## 3. Business Story

At Euphoria provisioning, system roles are seeded: **Tenant Admin** (all permissions), **Sales Manager** (CRM + SAL read/create/approve), **Sales Executive** (CRM read/create), **Finance User** (FIN read/create/approve), **Project Manager** (PRJ full), **Support Agent** (SRV full), **Team Member** (read-only base).

The **Tenant Admin** creates a custom role "Pre-Sales Consultant" by cloning Sales Executive and adding `quotation.create` permission. Role assigned to two users. JWT for those users now includes the new permission set on next login (or immediate if token refresh forced).

**Sales Manager** can approve quotations; **Sales Executive** cannot — API returns 403 if attempted. Flutter hides the Approve button based on same permission check.

Tenant Admin attempts to create role #6 on Community edition (limit 5 custom): rejected (BR-PF-061). On upgrade to Professional, limit increases to 25.

Platform Admin adds new permissions when CRM-002 module ships. Permissions auto-available in role editor; existing roles unaffected until Tenant Admin explicitly grants them.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Platform Admin]                    [Tenant Admin]
      │                                   │
      ▼                                   ▼
┌──────────────┐                 ┌──────────────┐
│ Seed System  │                 │ Create Custom│
│ Roles + Perms│                 │ Role         │
└──────┬───────┘                 └──────┬───────┘
       │                                  │
       └──────────────┬───────────────────┘
                      ▼
              ┌──────────────┐
              │ Map Perms    │
              │ to Role      │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐     ┌──────────────┐
              │ Assign Role  │────►│ JWT updated  │
              │ to User      │     │ (permissions)│
              └──────────────┘     └──────┬───────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │ API + UI     │
                                   │ enforce RBAC │
                                   └──────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Platform Admin | Seed permission catalogue | Module definitions | `permission` rows | Provisioning |
| 2 | System | Seed system roles per tenant | Tenant id | `role` (system) | Provisioning |
| 3 | Tenant Admin | Create custom role | Role form | `role` (custom) | — |
| 4 | Tenant Admin | Assign permissions to role | Permission codes | `role_permission` rows | — |
| 5 | Tenant Admin | Assign role to user | User + role | `user_role` row | — |
| 6 | System | Embed permissions in JWT | User login | JWT claims | Auth Service |
| 7 | System | Enforce on API call | JWT + required permission | 200 or 403 | API Middleware |

---

## 5. Business States

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| ACTIVE | Active | Role in use | INACTIVE | Tenant Admin | Permissions enforced |
| INACTIVE | Inactive | Disabled | ACTIVE, ARCHIVED | Tenant Admin | Users lose permissions |
| ARCHIVED | Archived | Historical | — | Tenant Admin | No assignments allowed |

*Note: System roles cannot be deleted or archived; only custom roles can be deactivated.*

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-061 | Custom role count limited by edition: Community=5, Professional=25, Enterprise=unlimited | Validation | Error | Rule Engine |
| BR-PF-062 | System roles (is_system=true) cannot be deleted or renamed | Lifecycle | Error | API |
| BR-PF-063 | Tenant Admin role must always include `tenant_admin.*` permissions | Security | Error | API |
| BR-PF-064 | User must have at least one role | Validation | Error | API |
| BR-PF-065 | Permission check enforced server-side on every mutating API call | Security | Error | API Middleware |
| BR-PF-066 | Role-permission changes take effect on next JWT refresh (max 15 min) | Security | Info | Auth Service |
| BR-PF-067 | Segregation of duties: same user cannot have both `invoice.create` and `invoice.approve` (configurable) | Security | Warning | Rule Engine |
| BR-PF-068 | Permission code format: `{resource}.{action}` lowercase | Validation | Error | DB, API |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| role | Master | Role definitions (system + custom) | Yes |
| permission | Lookup | Platform permission catalogue | No |
| role_permission | Link | Role-to-permission mapping | Yes |
| user_role | Link | User-to-role assignment | Yes |
| permission_module | Lookup | Permission grouped by module domain | No |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| tenant | role | 1:N | Cascade | Custom roles |
| role | role_permission | 1:N | Cascade | Permission mapping |
| permission | role_permission | 1:N | Restrict | |
| users | user_role | 1:N | Cascade | User assignment |
| role | user_role | 1:N | Restrict | |

---

## 9. Field Groups

### role
- Identity (code, name, description)
- Classification (is_system, role_type: ADMIN, MANAGER, USER, CUSTOM)
- Status (status, is_active)
- Audit (created_by, created_on, modified_by, modified_on)

### permission
- Identity (code, name, description)
- Module (module_domain, module_id, resource)
- Action (action: create, read, update, delete, approve, etc.)
- Metadata (is_system, display_order)

### role_permission
- Mapping (role_id, permission_id, granted_at, granted_by)

### user_role
- Assignment (user_id, role_id, assigned_at, assigned_by, effective_from, effective_to)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/rbac/roles` | Create role | `role.create` |
| GET | `/api/v1/rbac/roles` | List roles | `role.read` |
| GET | `/api/v1/rbac/roles/{id}` | Get role detail | `role.read` |
| PUT | `/api/v1/rbac/roles/{id}` | Full update | `role.update` |
| PATCH | `/api/v1/rbac/roles/{id}` | Partial update | `role.update` |
| DELETE | `/api/v1/rbac/roles/{id}` | Deactivate role | `role.delete` |
| GET | `/api/v1/rbac/roles/search` | Search roles | `role.read` |
| GET | `/api/v1/rbac/roles/export` | Export roles | `role.export` |
| POST | `/api/v1/rbac/roles/{id}/clone` | Clone role | `role.create` |
| GET | `/api/v1/rbac/roles/{id}/permissions` | List role permissions | `role.read` |
| PUT | `/api/v1/rbac/roles/{id}/permissions` | Set role permissions | `role.configure` |
| GET | `/api/v1/rbac/permissions` | List all permissions | `permission.read` |
| GET | `/api/v1/rbac/permissions/search` | Search permissions | `permission.read` |
| POST | `/api/v1/rbac/users/{user_id}/roles` | Assign role to user | `role.assign` |
| DELETE | `/api/v1/rbac/users/{user_id}/roles/{role_id}` | Remove role from user | `role.assign` |
| GET | `/api/v1/rbac/users/{user_id}/permissions` | Effective permissions | `role.read` |
| GET | `/api/v1/rbac/me/permissions` | Current user permissions | Authenticated |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Role List | List | Tenant Admin | System vs custom filter |
| Role Create | Create | Tenant Admin | Clone option |
| Role Edit | Edit | Tenant Admin | Permission matrix checkbox grid |
| Role View | View | Tenant Admin | Permission summary |
| Role Search | Search | Tenant Admin | |
| Permission Catalogue | List | Tenant Admin | Grouped by module |
| User Role Assignment | Edit | Tenant Admin | Multi-select roles per user |
| Role History | History | Tenant Admin | Permission change audit |
| My Permissions | View | All users | Read-only effective permissions |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `role.create` | Create custom roles |
| `role.read` | View roles |
| `role.update` | Edit roles |
| `role.delete` | Deactivate roles |
| `role.configure` | Set role permissions |
| `role.assign` | Assign roles to users |
| `role.export` | Export role matrix |
| `permission.read` | View permission catalogue |

| Actor | create | read | configure | assign | delete |
|-------|:------:|:----:|:---------:|:------:|:------:|
| Tenant Admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| Platform Admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| Sales Manager | — | ✓ (own) | — | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Role assigned to user | Email, Internal | User, Tenant Admin | NTF-PF-009-01 |
| Role permissions changed | Internal | Users with that role | NTF-PF-009-02 |
| Custom role created | Internal | Tenant Admin | NTF-PF-009-03 |
| Role limit approaching | Email | Tenant Admin | NTF-PF-009-04 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-009-01 | Role-Permission Matrix | Operational | Tenant Admin | Per role | Module | XLSX, PDF |
| RPT-PF-009-02 | User-Role Assignment | Operational | Tenant Admin | Per user | Role | XLSX |
| RPT-PF-009-03 | Permission Usage | Management | Tenant Admin | Per permission | — | XLSX |
| RPT-PF-009-04 | Segregation of Duties Violations | Compliance | Tenant Admin | Per user | — | PDF |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Role created | role_id, code, name | Per tenant policy |
| Role permissions changed | role_id, added/removed permissions | Per tenant policy |
| Role assigned to user | user_id, role_id | Per tenant policy |
| Role removed from user | user_id, role_id | Per tenant policy |
| Role deactivated | role_id, reason | Per tenant policy |
| Permission denied (403) | user_id, permission, endpoint | Per tenant policy |

---

## 16. Acceptance Criteria

1. **AC-PF-009-01:** Given Sales Executive role without `quotation.approve`, when approve API called, then HTTP 403 returned.
2. **AC-PF-009-02:** Given Community edition with 5 custom roles, when 6th role created, then rejected (BR-PF-061).
3. **AC-PF-009-03:** Given permission added to role, when affected user refreshes JWT, then new permission in claims.
4. **AC-PF-009-04:** Given system role Tenant Admin, when delete attempted, then rejected (BR-PF-062).
5. **AC-PF-009-05:** Given Flutter UI, when user lacks `lead.create`, then Create Lead button hidden.
6. **AC-PF-009-06:** Given two tenants, when Euphoria Tenant Admin views roles, then only Euphoria roles shown.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Row-level security (own records vs team vs all) |
| v2.0 | Time-bound role assignments (effective_from/to) |
| v2.0 | Field-level permissions |
| v3.0 | Attribute-based access control (ABAC) |
| v3.0 | Permission simulation / "view as" mode |

---

# PF-010 Audit & Compliance

**Document ID:** ELU-BFS-PF-010  
**Module:** PF-010 — Audit & Compliance  
**Sub Module:** PF-010-001 — Audit Trail  
**Feature:** PF-010-001-001 — Activity Logging  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

Audit & Compliance provides an **immutable, searchable record of all significant actions** performed within Euphoria's E-LinkUp instance. Activity Logging captures who did what, when, on which object, with before/after values — enabling forensic investigation, regulatory compliance (ISO 27001, SOC 2), and operational accountability across all platform modules.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Accountability | Every change attributed to a user |
| Compliance | Audit trail for certifications and audits |
| Forensics | Investigate data changes and security incidents |
| Non-repudiation | Immutable log prevents tampering |
| Operational visibility | Who changed what and when |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Centralised audit event capture | SIEM integration (v2) |
| Activity log storage and search | Real-time anomaly detection (v3) |
| Edition-based retention (90d/1yr/7yr) | Legal hold management (v2) |
| Audit log export | |
| Cross-module event standardisation | |

### 1.4 Users involved

Tenant Admin, Platform Admin, Compliance Officer (v2), System (Audit Service — CPS-005), all modules (event producers).

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-010 |
| Sub Module ID | PF-010-001 |
| Feature ID | PF-010-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Community (90 days); Professional (1 year); Enterprise (7 years) |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Search audit logs, export | Configure retention |
| Platform Admin | Internal | View platform-level audit events | Manage retention policies |
| Compliance Officer | Internal | Review audit reports, investigate | Export for auditors |
| System — Audit Service | System | Capture, store, index events | Purge per retention |
| All Module APIs | System | Emit audit events on mutations | — |

---

## 3. Business Story

When a **Sales Executive** at Euphoria updates a Lead status from "New" to "Qualified", the CRM API emits an audit event: `{event: "lead.updated", object_type: "lead", object_id: "...", actor: user_id, changes: {status: {old: "New", new: "Qualified"}}, timestamp, ip, tenant_id}`.

The **Tenant Admin** investigates a data discrepancy: searches audit log filtered by object_type=lead, object_id, date range. Views chronological change history with actor names and field diffs.

During an ISO audit, the **Compliance Officer** exports audit logs for Q1 covering user management, role changes, and financial transactions. Export is CSV with digital signature metadata.

The Scheduler runs nightly: purges audit events older than retention period (Euphoria on Professional = 1 year). Enterprise tenants retain 7 years. Purge itself is audited.

Platform Admin views cross-tenant audit events for platform operations (tenant provisioning, subscription changes) in a separate platform audit store.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Any Module API]
      │
      │ mutation (create/update/delete/status)
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Audit Service│────►│ audit_event  │────►│ Index for    │
│ (CPS-005)    │     │ table        │     │ search       │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌────────────────────────────┤
                     ▼                            ▼
              ┌──────────────┐            ┌──────────────┐
              │ Tenant Admin │            │ Scheduler    │
              │ searches     │            │ purges old   │
              │ audit log    │            │ per retention│
              └──────────────┘            └──────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Module API | Emit audit event on mutation | Event payload | `audit_event` row | Audit Service |
| 2 | Audit Service | Enrich with actor, IP, tenant | Request context | Complete event | Audit Service |
| 3 | Audit Service | Store immutably | Event | Persisted row | DB (append-only) |
| 4 | Tenant Admin | Search audit log | Filters | Result set | Audit Service |
| 5 | Tenant Admin | Export audit log | Date range, filters | CSV/PDF file | Reporting Engine |
| 6 | Scheduler | Purge expired events | Retention policy | Deleted rows | Scheduler |

---

## 5. Business States

*Audit events are immutable — they do not have lifecycle states. Retention status applies at collection level:*

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| ACTIVE | Active | Within retention period | PURGED | System | Searchable |
| PURGED | Purged | Past retention, deleted | — | System (Scheduler) | No longer available |
| ARCHIVED | Archived | Moved to cold storage (v2) | PURGED | System | Searchable (slower) |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-069 | Audit events are append-only; no UPDATE or DELETE by users | Security | Error | DB (no update/delete grants) |
| BR-PF-070 | Every mutating API call must emit audit event | Audit | Error | API Middleware |
| BR-PF-071 | Retention period per edition: Community=90d, Professional=1yr, Enterprise=7yr | Lifecycle | Info | Scheduler |
| BR-PF-072 | Audit event must include: tenant_id, actor_id, event_type, object_type, object_id, timestamp | Validation | Error | Audit Service |
| BR-PF-073 | Sensitive fields (password, MFA secret) must never appear in audit payload | Security | Error | Audit Service |
| BR-PF-074 | Audit log export requires `audit.export` permission | Security | Error | API |
| BR-PF-075 | Platform-level events stored in separate `platform_audit_event` table | Security | Info | Audit Service |
| BR-PF-076 | Audit search results scoped to tenant_id from JWT | Security | Error | API Middleware |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| audit_event | Audit | Tenant-scoped activity log | Yes |
| platform_audit_event | Audit | Platform-level events | No |
| audit_event_detail | Audit | Field-level change details | Yes |
| audit_retention_policy | Master | Retention config per tenant/edition | Yes |
| audit_export_log | Transaction | Export request tracking | Yes |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| tenant | audit_event | 1:N | Cascade (on tenant close after retention) | |
| users | audit_event | 1:N | Set Null | Actor reference |
| audit_event | audit_event_detail | 1:N | Cascade | Field diffs |
| tenant | audit_retention_policy | 1:1 | Cascade | Retention config |

---

## 9. Field Groups

### audit_event
- Event Identity (event_id, event_type, event_category)
- Context (tenant_id, actor_id, actor_email, ip_address, user_agent, session_id)
- Object (object_type, object_id, object_name)
- Action (action: CREATE, UPDATE, DELETE, STATUS_CHANGE, LOGIN, EXPORT, etc.)
- Summary (description, outcome: SUCCESS, FAILURE)
- Timing (event_timestamp, server_timestamp)
- Metadata (module_code, api_endpoint, request_id)

### audit_event_detail
- Change Detail (audit_event_id, field_name, old_value, new_value, data_type)
- Masking (is_sensitive, display_value)

### audit_retention_policy
- Policy (retention_days, edition_code, auto_purge_enabled)
- Schedule (last_purge_at, next_purge_at)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| GET | `/api/v1/audit/events` | List audit events | `audit.read` |
| GET | `/api/v1/audit/events/{id}` | Get event detail | `audit.read` |
| GET | `/api/v1/audit/events/search` | Search audit log | `audit.read` |
| GET | `/api/v1/audit/events/export` | Export audit log | `audit.export` |
| GET | `/api/v1/audit/objects/{type}/{id}/history` | Object change history | `audit.read` |
| GET | `/api/v1/audit/users/{user_id}/activity` | User activity log | `audit.read` |
| GET | `/api/v1/audit/retention` | Get retention policy | `audit.read` |
| PUT | `/api/v1/audit/retention` | Update retention (Enterprise) | `audit.configure` |
| GET | `/api/v1/platform/audit/events` | Platform audit log | `platform_audit.read` |
| GET | `/api/v1/platform/audit/events/search` | Search platform audit | `platform_audit.read` |

*Note: No POST/PUT/PATCH/DELETE on audit events — append-only via Audit Service internal API.*

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Audit Log List | List | Tenant Admin | Filters: date, actor, object, action |
| Audit Log Search | Search | Tenant Admin | Advanced multi-filter |
| Audit Event Detail | View | Tenant Admin | Field-level diff view |
| Object History | History | All (per object permission) | Embedded in entity detail screens |
| User Activity Log | History | Tenant Admin | Per-user timeline |
| Audit Export | View | Tenant Admin | Date range, format selection |
| Retention Settings | Edit | Tenant Admin (Enterprise) | Configure retention |
| Platform Audit Log | List | Platform Admin | Cross-tenant platform events |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `audit.read` | View audit logs |
| `audit.export` | Export audit logs |
| `audit.configure` | Configure retention policy |
| `platform_audit.read` | View platform-level audit |

| Actor | read | export | configure |
|-------|:----:|:------:|:---------:|
| Tenant Admin | ✓ | ✓ | ✓ (Enterprise) |
| Platform Admin | ✓ (all) | ✓ | ✓ |
| Compliance Officer | ✓ | ✓ | — |
| Sales Executive | — | — | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Audit export completed | Email, Internal | Requestor | NTF-PF-010-01 |
| Suspicious activity detected (v2) | Email, SMS | Tenant Admin, Security | NTF-PF-010-02 |
| Retention purge completed | Internal | Tenant Admin | NTF-PF-010-03 |
| Audit log approaching capacity (v2) | Email | Tenant Admin, Platform Admin | NTF-PF-010-04 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-010-01 | User Activity Summary | Operational | Tenant Admin | Per user per day | Date range | XLSX |
| RPT-PF-010-02 | Data Change Log | Compliance | Compliance Officer | Per object type | Date, module | CSV, PDF |
| RPT-PF-010-03 | Login Activity Report | Security | Tenant Admin | Per login event | Date, user | XLSX |
| RPT-PF-010-04 | Permission Change Audit | Compliance | Tenant Admin | Per change | Date range | PDF |
| RPT-PF-010-05 | Failed Action Report | Operational | Tenant Admin | Per failure | Date, module | XLSX |

---

## 15. Audit Requirements

*Meta-audit: the audit system audits itself.*

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Audit log searched | actor_id, filters, result_count | Same as tenant retention |
| Audit log exported | actor_id, date_range, record_count | Same as tenant retention |
| Retention policy changed | old/new retention_days | Platform permanent |
| Audit purge executed | tenant_id, records_purged, date_range | Platform permanent |

---

## 16. Acceptance Criteria

1. **AC-PF-010-01:** Given Sales Executive updates a lead, when change saved, then audit_event row created with correct actor, object, and field diff.
2. **AC-PF-010-02:** Given audit event stored, when direct UPDATE attempted on audit_event table, then operation fails (BR-PF-069).
3. **AC-PF-010-03:** Given Community edition (90-day retention), when Scheduler runs, then events older than 90 days purged.
4. **AC-PF-010-04:** Given Tenant Admin searches audit log, when results returned, then only own tenant events visible (BR-PF-076).
5. **AC-PF-010-05:** Given password change, when audit captured, then password value NOT in audit payload (BR-PF-073).
6. **AC-PF-010-06:** Given object history viewed on Lead detail, then chronological changes with actor names displayed.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | SIEM integration (Splunk, Azure Sentinel) |
| v2.0 | Legal hold — freeze audit records for litigation |
| v2.0 | Cold storage archive for Enterprise long retention |
| v3.0 | AI-powered anomaly detection on audit patterns |
| v3.0 | Real-time audit streaming via webhooks |

---

# PF-011 System Configuration

**Document ID:** ELU-BFS-PF-011  
**Module:** PF-011 — System Configuration  
**Sub Module:** PF-011-001 — Tenant Settings  
**Feature:** PF-011-001-001 — Business Preferences  
**Domain:** PF (Platform Foundation)  
**Priority / Phase / Release:** P0 / Phase 1 / R1.0  
**Example Tenant:** Euphoria  
**Stack:** Flutter · FastAPI · PostgreSQL · JWT+Refresh · Docker · VPS/Azure

---

## 1. Business Objective

### 1.1 Why this module exists

System Configuration centralises **tenant-level business preferences** that govern how E-LinkUp behaves for Euphoria — fiscal calendar, number/date formats, default modules, notification preferences, approval defaults, and feature toggles within edition limits. Business Preferences ensure the platform adapts to Euphoria's operating norms without code changes.

### 1.2 Business value

| Value Driver | Description |
|--------------|-------------|
| Localisation | Date, number, currency formats per tenant |
| Business alignment | Fiscal year, working days, holidays |
| Notification control | Channel preferences per event type |
| Module defaults | Default values for CRM, Sales, Finance modules |
| Self-service | Tenant Admin configures without vendor support |

### 1.3 Business scope

| In Scope | Out of Scope |
|----------|--------------|
| Tenant settings CRUD | Platform-global settings (Platform Admin) |
| Business preferences (fiscal, formats) | Workflow definition (CPS-001) |
| Notification preferences | Business rule configuration (CPS-002) |
| Module default values | Edition feature flags (PF-001) |
| Feature toggles within edition | |

### 1.4 Users involved

Tenant Admin, Platform Admin (platform settings), all CRM users (affected by settings).

### 1.5 Module reference

| Field | Value |
|-------|-------|
| Domain | PF |
| Module ID | PF-011 |
| Sub Module ID | PF-011-001 |
| Feature ID | PF-011-001-001 |
| Priority | P0 |
| Phase | 1 |
| Release | R1.0 |
| Minimum Edition | Community |

---

## 2. Business Actors

| Actor | Type | Primary Actions | Secondary Actions |
|-------|------|-----------------|-------------------|
| Tenant Admin | Internal | Configure all tenant settings | Preview changes |
| Platform Admin | Internal | Configure platform-global defaults | Override tenant settings (support) |
| Finance User | Internal | View fiscal settings | Suggest changes |
| System — Config Service | System | Serve settings to all modules | Cache invalidation |

---

## 3. Business Story

After Euphoria activation, the **Tenant Admin** opens Business Preferences. They set: fiscal year start = April, default currency = INR, date format = DD/MM/YYYY, number format = Indian (lakhs/crores), working days = Mon–Sat, timezone = Asia/Kolkata.

They configure notification preferences: lead assignment → Email + Push; quotation approval → Email + Internal; invoice generated → Email only. SMS and WhatsApp disabled (not configured).

Module defaults: default lead source = "Website", default opportunity stage = "Prospecting", default payment terms = "Net 30". These pre-populate on new record creation across CRM and Sales modules.

Tenant Admin enables "Auto-assign leads by round-robin" (Professional feature). Rule Engine reads this setting at lead creation time.

When Tenant Admin changes fiscal year start from April to January, the system warns that open financial periods may be affected. Change is audited. Reports recalculate fiscal quarters from new start date.

---

## 4. Business Workflow

### 4.1 ASCII Flow

```text
[Tenant Admin]
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Open Settings│────►│ Edit Business│────►│ Save + Audit │
│ Dashboard    │     │ Preferences  │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌────────────────────────────┤
                     ▼                            ▼
              ┌──────────────┐            ┌──────────────┐
              │ Config Cache │            │ All modules  │
              │ invalidated  │            │ read new     │
              │              │            │ settings     │
              └──────────────┘            └──────────────┘
```

### 4.2 Step Table

| Step | Actor | Action | Input | Output | Engine |
|------|-------|--------|-------|--------|--------|
| 1 | Tenant Admin | Open settings dashboard | — | Current settings | Config Service |
| 2 | Tenant Admin | Edit business preferences | Form values | Updated settings | — |
| 3 | System | Validate against edition limits | Settings + edition | Pass/Fail | Rule Engine |
| 4 | System | Save and audit | Settings | `tenant_settings` updated | Audit Service |
| 5 | System | Invalidate config cache | Tenant id | Cache cleared | Config Service |
| 6 | All modules | Read updated settings | Tenant id | New behaviour | Config Service |

---

## 5. Business States

*Settings do not have lifecycle states. Configuration groups have a validity status:*

| State Code | State Label | Description | Allowed Next States | Entry Actors | System Effects |
|------------|-------------|-------------|---------------------|--------------|----------------|
| DEFAULT | Default | Factory defaults from provisioning | CUSTOMISED | System | Platform defaults |
| CUSTOMISED | Customised | Tenant Admin modified | DEFAULT (reset) | Tenant Admin | Tenant-specific behaviour |
| LOCKED | Locked | Platform Admin locked setting | CUSTOMISED | Platform Admin | Tenant cannot change |

---

## 6. Business Rules

| Rule ID | Statement | Type | Severity | Enforcement |
|---------|-----------|------|----------|-------------|
| BR-PF-077 | Settings changes must be audited | Audit | Info | Audit Service |
| BR-PF-078 | Feature toggles cannot enable features beyond edition limits | Security | Error | Rule Engine |
| BR-PF-079 | Fiscal year start month must be 1–12 | Validation | Error | API |
| BR-PF-080 | Reset to defaults requires Tenant Admin confirmation | Lifecycle | Warning | UI |
| BR-PF-081 | Notification channel disabled at platform level cannot be enabled by tenant | Security | Error | API |
| BR-PF-082 | Settings cached per tenant; cache TTL = 5 minutes | Performance | Info | Config Service |
| BR-PF-083 | LOCKED settings can only be changed by Platform Admin | Security | Error | API |
| BR-PF-084 | Date/number format changes apply to new records and reports; not retroactive on existing PDFs | Calculation | Info | Document Engine |

---

## 7. Database Impact

| Table Name | Type | Purpose | Tenant Scoped |
|------------|------|---------|---------------|
| tenant_settings | Master | Core tenant settings (from PF-002) | Yes |
| tenant_preference | Master | Key-value business preferences | Yes |
| tenant_notification_preference | Master | Per-event notification channel config | Yes |
| tenant_module_default | Master | Module-specific default values | Yes |
| tenant_holiday_calendar | Master | Working days and holidays | Yes |
| platform_setting | Master | Platform-global defaults | No |
| setting_catalogue | Lookup | Available settings registry | No |

---

## 8. Relationships

| Parent | Child | Cardinality | On Delete | Notes |
|--------|-------|-------------|-----------|-------|
| tenant | tenant_settings | 1:1 | Cascade | Core settings |
| tenant | tenant_preference | 1:N | Cascade | KV preferences |
| tenant | tenant_notification_preference | 1:N | Cascade | Notification config |
| tenant | tenant_module_default | 1:N | Cascade | Module defaults |
| tenant | tenant_holiday_calendar | 1:N | Cascade | Holidays |
| setting_catalogue | tenant_preference | 1:N | Restrict | Valid keys |

---

## 9. Field Groups

### tenant_settings
- General (default_language, default_timezone, date_format, time_format, number_format)
- Fiscal (fiscal_year_start_month, fiscal_year_label_format)
- Currency (default_currency_code, currency_decimal_places, currency_symbol_position)
- Working Time (working_days, working_hours_start, working_hours_end)
- Module Toggles (crm_enabled, sales_enabled, projects_enabled, finance_enabled, service_enabled)
- Feature Toggles (auto_lead_assignment, round_robin_enabled, duplicate_detection_enabled)

### tenant_preference
- Preference (preference_key, preference_value, preference_type, preference_group)
- Metadata (description, is_editable, edition_minimum)

### tenant_notification_preference
- Event (event_type, module_code)
- Channels (email_enabled, sms_enabled, whatsapp_enabled, push_enabled, internal_enabled)
- Recipients (notify_actor, notify_manager, notify_admin, custom_recipients)

### tenant_module_default
- Module (module_code, entity_type)
- Default (field_name, default_value)

### tenant_holiday_calendar
- Holiday (holiday_name, holiday_date, is_recurring, holiday_type)
- Calendar (calendar_year)

---

## 10. REST APIs

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| GET | `/api/v1/settings` | Get all tenant settings | `settings.read` |
| PUT | `/api/v1/settings` | Update tenant settings | `settings.configure` |
| PATCH | `/api/v1/settings` | Partial update | `settings.configure` |
| GET | `/api/v1/settings/preferences` | List preferences | `settings.read` |
| PUT | `/api/v1/settings/preferences` | Update preferences | `settings.configure` |
| GET | `/api/v1/settings/preferences/{key}` | Get single preference | `settings.read` |
| PUT | `/api/v1/settings/preferences/{key}` | Set single preference | `settings.configure` |
| GET | `/api/v1/settings/notifications` | Get notification preferences | `settings.read` |
| PUT | `/api/v1/settings/notifications` | Update notification prefs | `settings.configure` |
| GET | `/api/v1/settings/module-defaults` | Get module defaults | `settings.read` |
| PUT | `/api/v1/settings/module-defaults` | Update module defaults | `settings.configure` |
| GET | `/api/v1/settings/holidays` | List holidays | `settings.read` |
| POST | `/api/v1/settings/holidays` | Add holiday | `settings.configure` |
| PUT | `/api/v1/settings/holidays/{id}` | Update holiday | `settings.configure` |
| DELETE | `/api/v1/settings/holidays/{id}` | Remove holiday | `settings.configure` |
| POST | `/api/v1/settings/reset` | Reset to defaults | `settings.configure` |
| GET | `/api/v1/settings/catalogue` | Available settings registry | `settings.read` |
| GET | `/api/v1/platform/settings` | Platform-global settings | `platform_settings.read` |
| PUT | `/api/v1/platform/settings` | Update platform settings | `platform_settings.configure` |

---

## 11. Flutter Screens

| Screen | Type | Primary Actor | Notes |
|--------|------|---------------|-------|
| Settings Dashboard | View | Tenant Admin | Navigation hub to all setting groups |
| Business Preferences | Edit | Tenant Admin | Fiscal, formats, currency |
| Notification Preferences | Edit | Tenant Admin | Per-event channel matrix |
| Module Defaults | Edit | Tenant Admin | CRM, Sales, Finance defaults |
| Holiday Calendar | Edit | Tenant Admin | Annual calendar view |
| Working Hours | Edit | Tenant Admin | Days and hours |
| Feature Toggles | Edit | Tenant Admin | Edition-gated toggles |
| Settings History | History | Tenant Admin | Change audit trail |
| Platform Settings | Edit | Platform Admin | Global defaults |

---

## 12. RBAC Permissions

| Permission | Description |
|------------|-------------|
| `settings.read` | View tenant settings |
| `settings.configure` | Modify tenant settings |
| `platform_settings.read` | View platform settings |
| `platform_settings.configure` | Modify platform settings |

| Actor | read | configure |
|-------|:----:|:---------:|
| Tenant Admin | ✓ | ✓ |
| Platform Admin | ✓ (all) | ✓ (all) |
| Finance User | ✓ | — |
| Sales Manager | ✓ (limited) | — |

---

## 13. Notifications

| Event | Channels | Recipients | Template Key |
|-------|----------|------------|--------------|
| Settings changed | Internal | Tenant Admin | NTF-PF-011-01 |
| Fiscal year changed | Email, Internal | Finance User, Tenant Admin | NTF-PF-011-02 |
| Settings reset to defaults | Email, Internal | Tenant Admin | NTF-PF-011-03 |
| Feature toggle enabled | Internal | Tenant Admin | NTF-PF-011-04 |

---

## 14. Reports

| Report ID | Name | Type | Audience | Grain | Filters | Export |
|-----------|------|------|----------|-------|---------|--------|
| RPT-PF-011-01 | Tenant Configuration Summary | Operational | Tenant Admin | Per setting group | — | PDF |
| RPT-PF-011-02 | Settings Change Log | Compliance | Tenant Admin | Per change | Date range | XLSX |
| RPT-PF-011-03 | Notification Configuration Matrix | Operational | Tenant Admin | Per event type | Module | PDF |

---

## 15. Audit Requirements

| Event | Captured Fields | Retention |
|-------|-----------------|-----------|
| Settings updated | setting_group, field diff | Per tenant policy |
| Preferences changed | preference_key, old/new value | Per tenant policy |
| Notification preferences changed | event_type, channel changes | Per tenant policy |
| Module defaults changed | module, field, old/new value | Per tenant policy |
| Holiday added/removed | holiday_name, date | Per tenant policy |
| Settings reset to defaults | actor, timestamp | Per tenant policy |

---

## 16. Acceptance Criteria

1. **AC-PF-011-01:** Given Tenant Admin changes date format to DD/MM/YYYY, when new lead created, then dates display in new format.
2. **AC-PF-011-02:** Given Community edition, when Tenant Admin enables Enterprise-only toggle, then rejected (BR-PF-078).
3. **AC-PF-011-03:** Given settings changed, when audit log checked, then change recorded with field diff (BR-PF-077).
4. **AC-PF-011-04:** Given notification preference set to Email only for lead assignment, when lead assigned, then only email sent (no push/SMS).
5. **AC-PF-011-05:** Given settings cached, when updated, then new values visible within 5 minutes (BR-PF-082).
6. **AC-PF-011-06:** Given fiscal year start changed, when financial report run, then quarters reflect new fiscal calendar.

---

## 17. Future Enhancements

| Version | Enhancement |
|---------|-------------|
| v2.0 | Settings import/export (JSON) for tenant migration |
| v2.0 | Environment-specific settings (dev/staging/prod) |
| v2.0 | Settings approval workflow for critical changes |
| v3.0 | AI-recommended settings based on industry |
| v3.0 | Multi-language settings UI |

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | ELU-BFS-PF |
| Version | 1.0 |
| Status | Approved for Development |
| Total Modules | 11 (PF-001 through PF-011) |
| Total Business Rules | BR-PF-001 through BR-PF-084 |
| Author | Senior BA / Enterprise Solution Architect / Product Owner |
| Reviewed By | Solution Architecture, Tech Lead, QA Lead |
| Next Artefacts | ELU-FD-PF (Field Dictionary), ELU-ERD-PF, ELU-API-PF, ELU-UI-PF |
| Definition of Ready | All §§1–17 complete for each module ✓ |

---

*© Euphoria Infotech (I) Limited — E-LinkUp Platform Foundation Business Functional Specification Pack*

