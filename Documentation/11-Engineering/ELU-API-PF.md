# E-LinkUp API Specification — Platform Foundation
**Document ID:** ELU-API-PF  
**Version:** 1.2
**Status:** Approved  
**Related Documents:** ELU-BFS-PF, ELU-EFS-001, V1-PF-CRM, ELU-DDD-PF, ELU-DEV-001, ELU-SEC-001, ELU-DOC-001  
**Base URL:** `/api/v1` · Auth: Bearer JWT · Tenant: JWT claim (**ADR-015**)  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Tech Lead | PF API contract summary for implementation |
| 1.1 | 2026-09-15 | EIIP / Engineering (governance reconciliation; approver identity PENDING — not supplied in the authorising instruction) | PF-006 Department endpoint surface recorded (implemented and audited, **NOT released**); `GET /{id}/history` flagged as a **human scope decision required** |
| 1.2 | 2026-09-15 | Human Project Owner (personal name not supplied — **PENDING**, not invented; ELU-AI-001) | **PF-006 human scope decisions APPROVED and recorded:** (1) `GET /org/departments/{id}/history` retained as an **additional human-approved** PF-006 endpoint (§10 lists 10; total implemented operations = 11); (2) the **effective-parent-`NULL`** organization-change interpretation approved. **PF-006 RELEASE APPROVAL remains PENDING** |
| 1.3 | 2026-09-16 | EIIP / Engineering (PF-007 implementation Batch 1 — authorized by `PF-007 IMPLEMENTATION BATCH 1 AUTHORIZED: YES`; operator identity PENDING — not supplied in the authorising instruction) | **PF-007 Business Unit endpoint surface recorded** (exactly the **8** `ELU-BFS-PF` §PF-007 §10 endpoints; **no history endpoint** — D1). Implementation Batch 1: `core.business_unit` (+ rollback + RLS enrolment), `migrate_pf007.py` + lifespan, ORM/schemas/service/router, `BUSINESS_UNIT` edition feature gate (BR-PF-046), `business_unit.*` permission catalogue + matrix (D2/D3) and the §12 role gates. **Not implemented in Batch 1:** opportunity/project/invoice linkage (D6), reporting/XLSX-PDF formatting (D8), notifications, history API, `users.business_unit_id` (PF-008), Flutter UI (D10) |

---

## 1. Cross-Cutting

| Concern | Standard |
|---------|----------|
| Error envelope | Per **ELU-DEV-001** (`error.code`, `message`, `request_id`, optional `req_id`) |
| Pagination | `page` (1-based), `page_size` (default 20, max 100) |
| Idempotency | `Idempotency-Key` header required on `POST /platform/tenants` (**REQ-PF-008**) |
| Soft delete | `DELETE` → logical; list excludes `is_deleted` |
| Cross-tenant | 404 |
| Edition gate | 403 `EDITION_FORBIDDEN` |
| Optimistic lock | `If-Match` / body `version_no` → 409 on conflict |

---

## 2. Auth

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/auth/login` | Issue access + refresh |
| POST | `/api/v1/auth/refresh` | Rotate refresh |
| POST | `/api/v1/auth/logout` | Revoke session |
| POST | `/api/v1/auth/activate` | Consume invite/activation token |

---

## 3. Tenants (Platform Admin)

| Method | Endpoint | Purpose | REQ |
|--------|----------|---------|-----|
| POST | `/api/v1/platform/tenants` | Register tenant | REQ-PF-001 |
| GET | `/api/v1/platform/tenants` | List | |
| GET | `/api/v1/platform/tenants/{id}` | Detail | |
| PUT/PATCH | `/api/v1/platform/tenants/{id}` | Update | |
| PATCH | `/api/v1/platform/tenants/{id}/status` | Status transition | |
| DELETE | `/api/v1/platform/tenants/{id}` | Soft close | REQ-PF-012 |
| GET | `/api/v1/platform/tenants/search` | Search | |
| GET | `/api/v1/platform/tenants/export` | Export | REQ-PF-010 |
| POST | `/api/v1/platform/tenants/{id}/approve` | Approve | REQ-PF-005 |
| POST | `/api/v1/platform/tenants/{id}/suspend` | Suspend | REQ-PF-006 |
| POST | `/api/v1/platform/tenants/{id}/reactivate` | Reactivate | |
| POST | `/api/v1/platform/tenants/{id}/resend-activation` | Resend | REQ-PF-011 |
| GET/PUT | `/api/v1/tenant/profile` | Own tenant profile | |

---

## 4. Editions / Subscriptions / Org / Users / Roles

Summaries align to **V1-PF-CRM** and **ELU-BFS-PF §10**:

- `/api/v1/platform/editions/*` — Platform Admin  
- `/api/v1/platform/subscriptions/*` — lifecycle, renew, upgrade, convert-trial  
- `/api/v1/org/organizations|branches|departments|business-units/*`  
- `/api/v1/users/*` — invite, CRUD, search, export  
- `/api/v1/roles/*`, `/api/v1/permissions`  
- `/api/v1/tenant/settings|security|branding|localization`  
- `/api/v1/audit/events` — tenant-scoped query  

OpenAPI YAML to be generated from FastAPI routers; this document is the checklist SoT until YAML is published.

**PF-005 Branch (implemented — ELU-BFS-PF-005 §10; Batch 2, not released):**

| Method | Endpoint | Purpose | Permission |
|--------|----------|---------|------------|
| POST | `/api/v1/org/branches` | Create branch | `branch.create` |
| GET | `/api/v1/org/branches` | List | `branch.read` |
| GET | `/api/v1/org/branches/{id}` | Detail | `branch.read` |
| PUT | `/api/v1/org/branches/{id}` | Full update | `branch.update` |
| PATCH | `/api/v1/org/branches/{id}` | Partial / status | `branch.update` |
| DELETE | `/api/v1/org/branches/{id}` | Soft delete | `branch.delete` |
| GET | `/api/v1/org/branches/search` | Search | `branch.read` |
| GET | `/api/v1/org/branches/export` | Export | `branch.export` |
| GET | `/api/v1/org/branches/hierarchy` | Branch tree | `branch.read` |

Edition gate: Professional+ (feature `BRANCH` — Community is rejected with 403). Limit `MAX_BRANCHES` = 10 (Professional) / 999999 (Enterprise), enforced on branch create and counting **non-deleted** branches (retained `ARCHIVED`/`CANCELLED` rows included). `branch.export` follows the PF-004 precedent of a **role gate** (Tenant Admin) rather than runtime permission-grain enforcement (deferred to PF-009). Implemented in `app/api/v1/pf/branches.py` (router registered in `app/api/v1/router.py`); the branch audit history is **service-only** (`BranchService.history()`) because BFS-PF-005 §10 defines no history endpoint. **PF-005 is not released** — no release baseline and no tag.

**PF-006 Department (implemented — **10** authoritative `ELU-BFS-PF` §PF-006 §10 endpoints **+ 1 human-approved history endpoint** = **11** API operations; Batches 1–5 incl. 3-C, NOT released):**

| Method | Endpoint | Purpose | Permission |
|--------|----------|---------|------------|
| POST | `/api/v1/org/departments` | Create department | `department.create` |
| GET | `/api/v1/org/departments` | List | `department.read` |
| GET | `/api/v1/org/departments/{id}` | Detail | `department.read` |
| PUT | `/api/v1/org/departments/{id}` | Full update | `department.update` |
| PATCH | `/api/v1/org/departments/{id}` | Partial update | `department.update` |
| PATCH | `/api/v1/org/departments/{id}/move` | Reparent | `department.update` |
| DELETE | `/api/v1/org/departments/{id}` | Soft delete | `department.delete` |
| GET | `/api/v1/org/departments/search` | Search | `department.read` |
| GET | `/api/v1/org/departments/export` | Export (JSON) | `department.export` |
| GET | `/api/v1/org/departments/hierarchy` | Department tree | `department.read` |
| GET | `/api/v1/org/departments/{id}/history` | Audit history | `department.read` |

Edition gate: **none** (`ELU-EDM-001` — Multi-Department is available in every edition). Authorization follows the PF-004/PF-005 precedent of **role gates** rather than runtime permission-grain enforcement (deferred to PF-009): read = TENANT_ADMIN / SALES_MANAGER / PROJECT_MANAGER; write = TENANT_ADMIN; export = TENANT_ADMIN. FINANCE_USER and SUPPORT_AGENT hold no PF-006 grant; PLATFORM_ADMIN is denied by the PF-006 gate (the generic `rbac.has_permission` PLATFORM_ADMIN bypass remains **PF-009 technical debt**). Implemented in `app/api/v1/pf/departments.py` (router registered in `app/api/v1/router.py`); all business rules live in `DepartmentService` (`app/services/pf/department_service.py`). Organization change is policy-guarded (**Batch 3-C**): allowed only when the effective `parent_department_id` after the request is `NULL` and there are no non-deleted children — no cascade, no silent reparenting, C-N11 enforced, invalid/foreign/deleted organization → 404. **Endpoint count:** the authoritative `ELU-BFS-PF` §PF-006 §10 list contains **10** endpoints; **1** additional endpoint is **human-approved PF-006 scope** (below) — **total implemented PF-006 API operations = 11**.
**HISTORY ENDPOINT — HUMAN-APPROVED PF-006 SCOPE (Project Owner decision, 2026-09-15):** `GET /{id}/history` is **retained** as an **additional** PF-006 audit-history endpoint. It is **not** part of the original §10 endpoint list — it was added by implementation following the PF-004 typed-history precedent (PF-005 deliberately exposes no such route) and is now **explicitly approved by the Human Project Owner**. It must **not** be removed, redesigned or reimplemented.
**ORGANIZATION-CHANGE POLICY — HUMAN-APPROVED (Project Owner decision, 2026-09-15):** *"Human Project Owner approved the effective-parent-NULL interpretation for PF-006 organization changes."* Approved behaviour (already implemented in **Batch 3-C** — no implementation change): (1) organization unchanged → **allowed**; (2) organization change + effective `parent_department_id` `NULL` + no non-deleted children → **allowed**; (3) organization change + effective parent non-`NULL` → **rejected**; (4) organization change + non-deleted children → **rejected**; (5) simultaneous parent detach + organization change → **allowed** when no non-deleted children exist; (6) **no cascade**; (7) **no silent reparenting**; (8) parent/child **same-organization rule (C-N11) remains enforced** (invalid/foreign/deleted organization → 404). This closes the previously recorded items 1-vs-6 scope question in favour of the stricter reading.
**PF-006 is not released** — no release approval, no certification, no tag.

**PF-007 Business Unit (Batch 1 implemented — **8** authoritative `ELU-BFS-PF` §PF-007 §10 endpoints; **no history endpoint**, D1; NOT released):**

| Method | Endpoint | Purpose | Permission |
|--------|----------|---------|------------|
| POST | `/api/v1/org/business-units` | Create business unit | `business_unit.create` |
| GET | `/api/v1/org/business-units` | List | `business_unit.read` |
| GET | `/api/v1/org/business-units/{id}` | Detail | `business_unit.read` |
| PUT | `/api/v1/org/business-units/{id}` | Full update | `business_unit.update` |
| PATCH | `/api/v1/org/business-units/{id}` | Partial update | `business_unit.update` |
| DELETE | `/api/v1/org/business-units/{id}` | Soft delete | `business_unit.delete` |
| GET | `/api/v1/org/business-units/search` | Search | `business_unit.read` |
| GET | `/api/v1/org/business-units/export` | Export (JSON) | `business_unit.export` |

Edition gate: **`BUSINESS_UNIT` required** (BR-PF-046 / D11 — Professional + Enterprise; **Community is excluded** from creating *and* using business units → 403). Authorization follows the PF-004/PF-005/PF-006 precedent of **role gates** rather than runtime permission-grain enforcement (deferred to PF-009): read = TENANT_ADMIN / SALES_MANAGER / FINANCE_USER / **PROJECT_MANAGER** (D3); write = TENANT_ADMIN; export = TENANT_ADMIN (**D2** — the §12 actor matrix carries no export column). SUPPORT_AGENT holds no PF-007 grant; PLATFORM_ADMIN is denied by the PF-007 gate (the generic `rbac.has_permission` PLATFORM_ADMIN bypass remains **PF-009 technical debt**). Implemented in `app/api/v1/pf/business_units.py` (router registered in `app/api/v1/router.py`); all business rules live in `BusinessUnitService` (`app/services/pf/business_unit_service.py`).
**Approved Batch-1 rules:** `BR-PF-047` code unique within the tenant (partial unique index `uk_business_unit_tenant_code_active` on `(tenant_id, business_unit_code) WHERE is_deleted = FALSE`, D11); `BR-PF-048` `bu_manager_user_id`, **when supplied**, must identify an **ACTIVE user in the same tenant** (D4 — service validation; the column has **no FK** and no `users.business_unit_id` is introduced); `BR-PF-049` only an **ACTIVE** business unit is assignable (domain guard `BusinessUnitService.assert_assignable` — **no opportunity/project path is wired in this batch**, D6); `BR-PF-050` Professional = **20** business units, Enterprise = **unlimited**, read from the existing `core.edition_limit` mechanism (`MAX_BUSINESS_UNITS`); `organization_id` is assigned on creation and **immutable** afterwards (D7 → 422 on any change); lifecycle `ACTIVE → INACTIVE → {ACTIVE, ARCHIVED}`, **ARCHIVED terminal** (`ELU-BFS-PF` §PF-007 §5). Export is **JSON only** (D8 — no XLSX/PDF formatting; the minimum AC-PF-007-03 aggregation belongs to a later batch).
**Not implemented in Batch 1 (deferred):** `business_unit → opportunity` (CRM) / `→ project` (PRJ) / `→ invoice` (FIN) linkage (D6), reporting/XLSX-PDF formatting (D8), `NTF-PF-007-01..03`, any history API/endpoint (D1), `users.business_unit_id` and BU-manager user linkage (PF-008), Flutter UI (D10).

**PF-001 implementation (2026-08-06):** Live OpenAPI at `/openapi.json`; exported snapshot `Backend/openapi/openapi.json` and edition path extract `Backend/openapi/pf001-editions-paths.json`. Edition endpoints implemented per BFS-PF §10.

### 4.5 PF-008 Users & Identity — CORE (implemented 2026-09-21, NOT released)

Authorized by `PF-008 CORE IMPLEMENTATION - AUTHORIZED` (human instruction, 2026-09-21) from baseline `969d022cd006c4ddc024f8e0a5d08af40a868841`; implementation decisions and the full evidence trail are recorded in
`Documentation/PF008_CORE_IMPLEMENTATION_MAP.md` and `Documentation/PF008_CORE_EVIDENCE_REPORT.md`.

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
| POST | `/api/v1/users` | Invite (INVITED + 72 h token) or create (ACTIVE + password) | `user.create` |
| GET | `/api/v1/users` | List (tenant-scoped) | `user.read` |
| GET | `/api/v1/users/search` | Search | `user.read` |
| GET | `/api/v1/users/export` | Export (JSON) | `user.export` |
| GET | `/api/v1/users/me` | Current user profile | authenticated |
| PUT | `/api/v1/users/me` | Update own profile | authenticated |
| GET | `/api/v1/users/{id}` | Detail | `user.read` |
| PUT | `/api/v1/users/{id}` | Full update (optimistic locking) | `user.update` |
| PATCH | `/api/v1/users/{id}` | Partial update / status transition | `user.update` |
| DELETE | `/api/v1/users/{id}` | **Deactivate** (§10 defines DELETE as deactivate) | `user.delete` |
| POST | `/api/v1/users/{id}/reinvite` | New 72 h invitation token | `user.create` |
| POST | `/api/v1/users/{id}/reset-password` | Admin reset challenge | `user.reset_password` |
| POST | `/api/v1/auth/register` | Activate an invited user (public, token) | none |
| POST | `/api/v1/auth/logout` | Revoke outstanding refresh tokens | authenticated |
| POST | `/api/v1/auth/forgot-password` | Request reset (public, non-enumerable) | none |
| POST | `/api/v1/auth/reset-password` | Consume reset challenge (public) | none |
| POST | `/api/v1/auth/change-password` | Self-service change | authenticated |

Authorization follows the PF-004…PF-007 precedent of **role gates** (runtime permission-grain
enforcement stays PF-009): read/search/export and write = `TENANT_ADMIN` + `PLATFORM_ADMIN`
(`ELU-BFS-PF-008` §12); `SALES_EXECUTIVE` self-scope is served by `/users/me`. Implemented in
`app/api/v1/pf/users.py` (+ additions to `app/api/v1/auth.py`), with all business rules in
`UserService` (`app/services/pf/user_service.py`) and the authentication extensions in
`AuthService` (`app/services/pf/auth_service.py`).

**Rules implemented:** `BR-PF-051` email unique per tenant (existing `uk_users_tenant_email`);
`BR-PF-052` seat enforcement on invite/create using `core.subscription.seat_count`
(`Tenant.current_subscription_id`, ACTIVE/TRIAL) plus the edition `MAX_USERS` bound, counting
`ACTIVE`+`INVITED`+`LOCKED` as seat holders (D8); `BR-PF-054` 72-hour invitation expiry (lazy,
D6); `BR-PF-055` five failures ⇒ `LOCKED` for 30 minutes (lazy release, D7); `BR-PF-057`
deactivation/password change revoke refresh tokens via `core.users.sessions_invalid_before`
(D4); `BR-PF-059` tenant from the JWT only; `BR-PF-060` last ACTIVE Tenant Admin guard; user
linkage to PF-005 branch / PF-006 department / PF-007 business unit with same-tenant and
ACTIVE-target validation (D13 scope note); lifecycle
`INVITED→{ACTIVE,EXPIRED,CANCELLED}`, `ACTIVE→{INACTIVE,LOCKED}`, `INACTIVE→ACTIVE`,
`LOCKED→ACTIVE`, `EXPIRED→INVITED`.

**Not implemented (deferred):** MFA enrolment/verification (`BR-PF-058`), SAML/OIDC SSO, SCIM,
customer-portal users, `NTF-PF-008-01..08`, `RPT-PF-008-01..04` incl. dashboard/analytics,
`JOB-PF-008-01` scheduler, `user.impersonate`, `core.user_credentials` / `core.user_session` /
`core.user_mfa` tables (D1/D4), the configurable password policy of `BR-PF-053` (**no
`tenant_security` table exists** — `005_core_tenant_security.sql` is empty; only the 8-character
minimum mirroring the existing login contract is enforced, D10), `BR-PF-038` branch-head and
`BR-PF-043` department-head validations (still released-documented PF-008 deferrals, D13) and the
Flutter screens of §11.

**Scope-guard reconciliation (requires human confirmation):** the delivered columns make the
released deferral guards `tests/test_pf005_branches.py::test_deferred_scope_not_implemented`,
`tests/test_pf006_departments.py::test_deferred_scope_absent` and
`tests/test_pf007_business_units.py::test_deferred_scope_absent` fail by design. They were
flipped to the **positive** direction with supersede notes — the same treatment PF-006 Batch 5
applied to the PF-005 guard — while every still-valid deferral assertion (BR-PF-038 / BR-PF-043
absence of FK and validation, `crm.opportunity.business_unit_id` absence, no reporting surface)
is retained.

---

## 5. Sample DTOs

**TenantCreate (POST):** `code`, `legal_name`, `trade_name`, `edition_code`, primary contact, address — **no** `tenant_id`.

**TenantRead:** includes `id`, `status`, `edition`, `subscription` summary, `version_no`.

---

*© Euphoria Infotech (I) Limited — ELU-API-PF*
