# E-LinkUp Test Specification — Platform Foundation
**Document ID:** ELU-TST-PF  
**Version:** 1.1  
**Status:** Approved  
**Related Documents:** ELU-RTM-001, ELU-API-PF, ELU-EFS-001, ELU-SEC-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / QA | PF test pack + isolation suite |
| 1.1 | 2026-08-06 | EIIP / QA | PF-001 edition automated tests mapped |

---

## 1. Mapping Rule

Every `REQ-PF-*` in V1-PF-CRM maps to ≥1 `TC-PF-*`. Isolation tests are mandatory for tenant entities (**ADR-015**).

---

## 2. Functional Samples

| TC ID | REQ | Scenario | Expected |
|-------|-----|----------|----------|
| TC-PF-001-01 | REQ-PF-001 | Create tenant with unique code | 201; tenant PENDING_ACTIVATION |
| TC-PF-001-02 | REQ-PF-002 | Atomic provision | org + subscription + settings exist |
| TC-PF-001-03 | REQ-PF-003 | DEPRECATED edition | 422 |
| TC-PF-001-05 | REQ-PF-005 | Activate with token | ACTIVE; login works |
| TC-PF-001-06 | REQ-PF-006 | Suspend | login blocked |
| TC-PF-001-08 | REQ-PF-008 | Replay Idempotency-Key | same tenant; no duplicate |
| TC-PF-001-12 | REQ-PF-012 | DELETE tenant | soft close; row remains |

### 2.1 PF-001 Edition Management (implemented)

| TC ID | Rule | Scenario | Automated test | Expected |
|-------|------|----------|----------------|----------|
| TC-PF-ED-01 | BFS §10 | List editions as Platform Admin | `test_list_editions` | 200; COMMUNITY/PROFESSIONAL/ENTERPRISE |
| TC-PF-ED-02 | BR-PF-008 | Publish requires feature+limit | `test_publish_requires_feature_and_limit` | 422 |
| TC-PF-ED-03 | BR-PF-006 | Limit below Community baseline | `test_limit_below_community_baseline` | 422 |
| TC-PF-ED-04 | BR-PF-005 | Create → publish → deprecate | `test_create_publish_deprecate_flow` | ACTIVE then DEPRECATED |
| TC-PF-ED-05 | RBAC | Tenant current edition read | `test_get_tenant_edition` | 200 PROFESSIONAL |
| TC-PF-ED-06 | API SoT | OpenAPI includes edition paths | `test_openapi_includes_editions` | paths present |

---

## 3. Isolation Suite (Mandatory)

| TC ID | Scenario | Expected |
|-------|----------|----------|
| TC-PF-ISO-01 | Tenant Admin A reads Tenant B profile by id | 404 |
| TC-PF-ISO-02 | Body contains foreign tenant_id on user create | ignored / 422; user in JWT tenant |
| TC-PF-ISO-03 | Soft-deleted user not in list | excluded |
| TC-PF-ISO-04 | Platform Admin list tenants | allowed; audited |
| TC-PF-EDN-01 | Community calls Business Unit API | 403 EDITION_FORBIDDEN |

---

## 4. Locations

`backend/tests/unit/pf/`, `backend/tests/integration/pf/`, `backend/tests/isolation/pf/`

---

*© Euphoria Infotech (I) Limited — ELU-TST-PF*
