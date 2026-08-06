# E-LinkUp API Specification — Platform Foundation
**Document ID:** ELU-API-PF  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-BFS-PF, ELU-EFS-001, V1-PF-CRM, ELU-DDD-PF, ELU-DEV-001, ELU-SEC-001, ELU-DOC-001  
**Base URL:** `/api/v1` · Auth: Bearer JWT · Tenant: JWT claim (**ADR-015**)  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Tech Lead | PF API contract summary for implementation |

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

**PF-001 implementation (2026-08-06):** Live OpenAPI at `/openapi.json`; exported snapshot `Backend/openapi/openapi.json` and edition path extract `Backend/openapi/pf001-editions-paths.json`. Edition endpoints implemented per BFS-PF §10.

---

## 5. Sample DTOs

**TenantCreate (POST):** `code`, `legal_name`, `trade_name`, `edition_code`, primary contact, address — **no** `tenant_id`.

**TenantRead:** includes `id`, `status`, `edition`, `subscription` summary, `version_no`.

---

*© Euphoria Infotech (I) Limited — ELU-API-PF*
