# E-LinkUp Test Specification — Platform Foundation
**Document ID:** ELU-TST-PF  
**Version:** 1.2  
**Status:** Approved  
**Related Documents:** ELU-RTM-001, ELU-API-PF, ELU-EFS-001, ELU-SEC-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / QA | PF test pack + isolation suite |
| 1.1 | 2026-08-06 | EIIP / QA | PF-001 edition automated tests mapped |
| 1.2 | 2026-08-06 | EIIP / QA | PF-003A isolation suite automated (`tests/isolation/`) |

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

## 3. Isolation Suite (Mandatory) — PF-003A automated

| TC ID | Scenario | Automated test | Expected |
|-------|----------|----------------|----------|
| TC-PF-ISO-01 | Tenant A cannot read Tenant B lead / platform tenant | `test_tc_pf_iso_01_cross_tenant_profile_and_lead` | 404 / 403 |
| TC-PF-ISO-02 | Body contains foreign tenant_id on lead create | `test_tc_pf_iso_02_foreign_tenant_id_ignored_on_lead` | ignored; JWT tenant |
| TC-PF-ISO-03 | Soft-deleted user not loginable / not visible | `test_tc_pf_iso_03_soft_deleted_user_invisible` | 401/403 |
| TC-PF-ISO-04 | Platform Admin list tenants | `test_tc_pf_iso_04_platform_admin_list` | 200 |
| TC-PF-ISO-RLS-01 | Empty GUC fail-closed | `test_rls_blocks_without_context` | 0 rows |
| TC-PF-ISO-RLS-02 | SET LOCAL tenant scope | `test_rls_tenant_scope_sql` | 1 row |
| TC-PF-ISO-JWT-01 | JWT tenant spoof | `test_jwt_tenant_spoof_rejected` | 401 |
| TC-PF-EDN-01 | Community calls Business Unit API | — | 403 EDITION_FORBIDDEN (deferred) |

---

## 4. Locations

`backend/tests/unit/pf/`, `backend/tests/integration/pf/`, `backend/tests/isolation/` (`test_tenant_isolation.py`)

---

*© Euphoria Infotech (I) Limited — ELU-TST-PF*
