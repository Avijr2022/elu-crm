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

**PF-001 implementation (2026-08-06):** Live OpenAPI at `/openapi.json`; exported snapshot `Backend/openapi/openapi.json` and edition path extract `Backend/openapi/pf001-editions-paths.json`. Edition endpoints implemented per BFS-PF §10.

---

## 5. Sample DTOs

**TenantCreate (POST):** `code`, `legal_name`, `trade_name`, `edition_code`, primary contact, address — **no** `tenant_id`.

**TenantRead:** includes `id`, `status`, `edition`, `subscription` summary, `version_no`.

---

*© Euphoria Infotech (I) Limited — ELU-API-PF*
