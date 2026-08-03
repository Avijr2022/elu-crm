# E-LinkUp Development Standards
**Document ID:** ELU-DEV-001  
**Document Name:** Development Standards  
**Version:** 1.0  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Tech Lead / Solution Architecture  
**Document Owner:** Tech Lead  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-DOC-001, ELU-SEH-001, ELU-DF-001, ELU-SAD-001, ELU-ADR-001, ELU-EFS-001, ELU-API-*, ELU-UI-*, ELU-DDD-*  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP / Tech Lead | Initial implementation standards for FastAPI + Flutter + PostgreSQL |

---

## 1. Purpose

**ELU-DEV-001** is the **day-to-day coding guide** for E-LinkUp engineers.

It complements:

| Document | Focus |
|----------|-------|
| **ELU-SEH-001 – Software Engineering Handbook** | Lifecycle, quality gates, engineering process *(planned / overarching)* |
| **ELU-DF-001 – Documentation Framework** | How specifications are written |
| **ELU-SAD-001 – Software Architecture Document** | System architecture |
| **ELU-ADR-001 – Architecture Decision Log** | Why stack choices exist |
| **ELU-DEV-001** *(this document)* | How to structure and write code daily |

**Rule:** Implementation stories reference `REQ-*` from **ELU-EFS-001** / **ELU-RTM-001** (**ADR-010**, **ADR-011**).

---

## 2. Technology Baseline (Binding)

| Layer | Standard | ADR |
|-------|----------|-----|
| Backend | Python 3.11+ · FastAPI | ADR-002 |
| ORM | SQLAlchemy 2.x | ADR-002 |
| Database | PostgreSQL 15+ | ADR-002 |
| Auth | JWT + Refresh Token · Argon2id | ADR-004 |
| Frontend | Flutter (Web + Android) | ADR-003 |
| Files | MinIO (S3 API) | ADR-005 |
| Containers | Docker · Nginx | ADR-014 |
| Async (v1.1+) | Celery · Redis | ADR-008 |

---

## 3. FastAPI Project Structure

Recommended repository layout (backend):

```text
backend/
  app/
    main.py                 # FastAPI app factory
    core/
      config.py             # Settings (env)
      security.py           # JWT, password hashing
      deps.py               # Dependency injection providers
      logging.py
      exceptions.py         # Domain error types
    db/
      session.py            # Engine / SessionLocal
      base.py               # Declarative Base
    models/                 # SQLAlchemy models (by domain)
      pf/
      crm/
      sales/
      ...
    schemas/                # Pydantic DTOs (by domain)
      crm/
        lead.py             # LeadCreate, LeadUpdate, LeadRead
    repositories/           # Persistence only
      crm/
        lead_repository.py
    services/               # Business logic / use-cases
      crm/
        lead_service.py
    api/
      v1/
        router.py
        crm/
          leads.py          # Route handlers (thin)
        deps_tenant.py      # tenant_id from JWT
    middleware/
      tenant.py
      request_id.py
    workers/                # Celery tasks (Phase 3+)
  tests/
    unit/
    integration/
    isolation/              # Cross-tenant tests (mandatory)
  alembic/
  pyproject.toml / requirements.txt
  Dockerfile
```

### 3.1 Layering Rules

| Layer | May call | Must not |
|-------|----------|----------|
| API router | Services, deps | SQLAlchemy queries directly |
| Service | Repositories, other services, engines | HTTP concerns |
| Repository | DB session, models | Business workflow branching |
| Schema (DTO) | — | Business logic |

---

## 4. Flutter Folder Conventions

Recommended layout (client):

```text
frontend/
  lib/
    main.dart
    app.dart
    core/
      theme/
      network/          # Dio/http client, interceptors (JWT refresh)
      auth/
      errors/
      widgets/          # Shared UI
    features/
      crm/
        leads/
          data/         # API DTOs, data sources
          domain/       # entities, repositories (interfaces)
          presentation/ # pages, controllers/cubits, widgets
            lead_list_page.dart
            lead_detail_page.dart
            lead_form_page.dart
      sales/
      projects/
      finance/
      platform/
    l10n/
    routing/
  test/
  integration_test/
```

### 4.1 Flutter Rules

- One **feature folder** per business capability aligned to EFS UI Navigation.  
- Do not call APIs from widgets — use controllers/cubits/view-models.  
- Enforce edition/RBAC hide **and** assume API will reject unauthorized calls.  
- List screens: server-side pagination + search (NFR).  

---

## 5. Naming Conventions

### 5.1 Backend

| Artefact | Convention | Example |
|----------|------------|---------|
| Module package | domain short name | `crm`, `sales` |
| Model class | PascalCase singular | `Lead`, `SalesOrder` |
| Table name | snake_case | `lead`, `sales_order` |
| API path | plural kebab/noun | `/api/v1/crm/leads` |
| Permission | `resource.action` | `lead.create` |
| Service method | verb_noun | `convert_lead_to_opportunity` |
| REQ reference in code/comments | `REQ-CRM-001` | docstring / OpenAPI tag |

### 5.2 Flutter

| Artefact | Convention | Example |
|----------|------------|---------|
| Page | `*_page.dart` | `lead_list_page.dart` |
| Widget | descriptive | `lead_status_chip.dart` |
| DTO | `*_dto.dart` / freezed | `lead_dto.dart` |
| Route name | snake or path | `/crm/leads/:id` |

### 5.3 Database

- PK: `id` UUID (or `{entity}_id` if clearer)  
- Always: `tenant_id`, `is_active`, `is_deleted`, `version_no`, `created_by`, `created_on`, `modified_by`, `modified_on` on tenant business tables (**ADR-006**)  
- FK names: `{referenced}_id`  

---

## 6. DTO Rules (Pydantic)

| DTO Type | Purpose | Example |
|----------|---------|---------|
| `*Create` | POST body | `LeadCreate` |
| `*Update` | PUT full update | `LeadUpdate` |
| `*Patch` | PATCH partial / status | `LeadStatusPatch` |
| `*Read` | Response model | `LeadRead` |
| `*ListItem` | List row (lighter) | `LeadListItem` |
| `*SearchParams` | Query filters | `LeadSearchParams` |

**Rules:**

1. Never expose `password_hash` or secrets in `*Read`.  
2. Never trust client-supplied `tenant_id` — take from JWT (**ADR-001**).  
3. Map DTOs ↔ models in service or dedicated mapper — not in router sprawl.  
4. Validate enums/states against EFS Allowed Transitions.  
5. Document OpenAPI `operation_id` and link `REQ-*` in description.  

---

## 7. Repository Pattern

```text
LeadService.convert(lead_id)
    → LeadRepository.get_for_tenant(tenant_id, lead_id)  # enforces tenant
    → validations / BR-CRM-*
    → OpportunityRepository.create(...)
    → LeadRepository.mark_converted(...)
    → AuditService.record(...)
    → NotificationService.enqueue(...)
```

**Repository obligations:**

- Every query filters `tenant_id` + `is_deleted = false` unless explicit admin/platform context.  
- Optimistic lock: update `WHERE version_no = :expected` then increment.  
- Soft delete only.  

---

## 8. Exception Handling

### 8.1 Domain Exceptions (examples)

| Exception | HTTP | When |
|-----------|------|------|
| `NotFoundError` | 404 | Entity missing in tenant |
| `ConflictError` | 409 | Duplicate lead, unique violation |
| `ValidationError` | 422 | Business validation / BR failure |
| `ForbiddenError` | 403 | RBAC or edition gate |
| `UnauthorizedError` | 401 | Auth failure |
| `ConflictVersionError` | 409 | Stale `version_no` |
| `ServiceUnavailableError` | 503 | Dependency down |

### 8.2 API Error Envelope (standard)

```json
{
  "error": {
    "code": "LEAD_DUPLICATE",
    "message": "A lead with this email already exists.",
    "req_id": "REQ-CRM-001",
    "details": {},
    "request_id": "uuid"
  }
}
```

Map exceptions in a FastAPI exception handler — routers should not invent ad hoc JSON shapes.

---

## 9. Logging

| Requirement | Standard |
|-------------|----------|
| Format | Structured JSON logs |
| Correlation | `request_id` on every request |
| Tenant context | `tenant_id`, `user_id` when authenticated |
| PII | Do not log passwords, tokens, full card data; mask GSTIN/PAN where required |
| Levels | INFO business events; WARN recoverable; ERROR failures; DEBUG local only |
| Audit vs log | Security/business audit → Audit tables/service; ops diagnostics → logs |

---

## 10. Dependency Injection

Use FastAPI `Depends()` for:

- DB session  
- Current user / JWT claims  
- Tenant context  
- Service instances  

```text
get_db → get_current_user → get_tenant_context → get_lead_service
```

**Rules:**

- Services constructed via deps (testable doubles in unit tests).  
- No global mutable singletons for request state.  
- Config via pydantic `BaseSettings` / env — never hardcode secrets.  

---

## 11. Security Coding Checklist (Every PR)

- [ ] Tenant filter present on read/write  
- [ ] Permission checked (`lead.create`, etc.)  
- [ ] Edition gate for paid modules (**ADR-009**)  
- [ ] Soft delete; no hard delete of transactional data  
- [ ] Secrets not committed  
- [ ] Isolation test added/updated for new tenant-scoped entity  

---

## 12. Testing Standards

| Type | Location | Minimum |
|------|----------|---------|
| Unit | `tests/unit` | Service rules / BR logic |
| API | `tests/integration` | Router + auth + status codes |
| Isolation | `tests/isolation` | Cross-tenant negative tests |
| Contract | CI | OpenAPI snapshot / schemathesis optional |

Test IDs align to **ELU-TST-*** / `TC-*` from **ELU-RTM-001**.

---

## 13. Git & PR Conventions

| Item | Standard |
|------|----------|
| Branch | `feature/REQ-CRM-001-lead-create` |
| Commit | Imperative; reference REQ when applicable |
| PR description | REQ IDs, screenshots for Flutter, test evidence |
| Review | At least one approval; security checklist for tenant entities |

---

## 14. Alignment to Documentation

| When coding… | Read first |
|--------------|------------|
| Workflow / states / APIs | **ELU-EFS-001** |
| Module field groups | **ELU-BFS-*** → then **ELU-DDD-*** |
| Why stack choice | **ELU-ADR-001** |
| Release scope | **ELU-RDM-001** |
| Progress | **ELU-MSL-001** |

---

*© Euphoria Infotech (I) Limited — ELU-DEV-001 Development Standards*
