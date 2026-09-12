# E-LinkUp Test Specification — Platform Foundation
**Document ID:** ELU-TST-PF  
**Version:** 1.3  
**Status:** Approved  
**Related Documents:** ELU-RTM-001, ELU-API-PF, ELU-EFS-001, ELU-SEC-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / QA | PF test pack + isolation suite |
| 1.1 | 2026-08-06 | EIIP / QA | PF-001 edition automated tests mapped |
| 1.2 | 2026-08-06 | EIIP / QA | PF-003A isolation suite automated (`tests/isolation/`) |
| 1.3 | 2026-09-12 | EIIP / QA | PF-005 branch groundwork test structure (§2.2, planned cases — not implemented) |

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

### 2.2 PF-005 Branch Management (authorised — NOT implemented; planned cases)

Groundwork status: specification, schema (`014_branch_pf005.sql`), RLS, ORM models and seed only. **No API, service, repository or UI code exists yet**, so every case below is **planned** and has no automated test. Automation targets: `Backend/tests/test_pf005_branches.py` and `Backend/tests/isolation/test_tenant_isolation.py`.

| TC ID | Rule | Scenario | Planned automated test | Expected |
|-------|------|----------|------------------------|----------|
| TC-PF-BR-01 | BR-PF-034 | Community edition calls branch create | `test_tc_pf_br_01_community_forbidden` | 403 EDITION_FORBIDDEN |
| TC-PF-BR-02 | BR-PF-035 | Duplicate branch code (non-deleted) in same tenant | `test_tc_pf_br_02_duplicate_code` | 409 / 422 |
| TC-PF-BR-03 | BR-PF-036 | No HEAD_OFFICE branch present | `test_tc_pf_br_03_head_office_warning` | 201 + warning |
| TC-PF-BR-04 | BR-PF-039 | Professional tenant creates 11th branch | `test_tc_pf_br_04_branch_limit` | 403 / 422 (limit) |
| TC-PF-BR-05 | BFS §8 | Parent/child hierarchy; cycle rejected | `test_tc_pf_br_05_hierarchy` | 200 / 422 |
| TC-PF-BR-06 | BFS §7/§9 | Address 1:1 create / update / cascade on delete | `test_tc_pf_br_06_address` | 200; address cascades |
| TC-PF-BR-07 | BR-PF-037 | Delete branch with open projects | *(deferred — no project→branch linkage)* | — |
| TC-PF-BR-08 | RBAC | Sales Manager / Project Manager write attempt | `test_tc_pf_br_08_readonly_roles` | 403 |
| TC-PF-ISO-05 | ADR-015 | Cross-tenant branch / branch_address read | `test_tc_pf_iso_05_branch_cross_tenant` | 404 / 0 rows |

**Deferred test scope (must NOT be implemented now):** AC-PF-005-04 / BR-PF-038 branch-head assignment and `users.branch_id` (**PF-008**); department linkage (**PF-006**); NTF-PF-005-* notifications; RPT-PF-005-* reports.

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
