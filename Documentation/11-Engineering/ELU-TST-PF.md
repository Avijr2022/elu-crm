# E-LinkUp Test Specification — Platform Foundation
**Document ID:** ELU-TST-PF  
**Version:** 1.5  
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
| 1.4 | 2026-09-12 | EIIP / QA | PF-005 branch functional layer implemented — §2.2 cases automated (15 PF-005 + 13 isolation; full suite 141 passed, 1 skipped; no PF-001…PF-004 regression) |
| 1.5 | 2026-09-16 | EIIP / QA | **PF-006 Department Management test-spec decision/status recorded — §2.3 added.** Batch 5 API implemented; **36** PF-006 tests automated (`Backend/tests/test_pf006_departments.py`) and 35 PF-004/PF-005 regression tests; implementation validation run recorded **71 passed** (2026-09-16 QA run: 36/36 + 35/35, 0 failed / 0 skipped / 0 errors). PF-006 **RELEASED** 2026-09-16 (annotated tag `Phase-2-PF006`); deferred/absent scope asserted by `test_deferred_scope_absent` |

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

### 2.2 PF-005 Branch Management (implemented — Batch 2; automated)

Implementation status: specification, schema (`014_branch_pf005.sql`), RLS, ORM models and seed (**groundwork Batch 1**) plus the backend functional layer — schemas, service, the 9-endpoint API and tests (**Batch 2**, delivered directly to `master` at `4430f9d2b9eedc51dede1ca1cf6183508a756dac`). The branch audit history is **service-only** (no API endpoint); no Flutter/UI, notifications or reports. Automation: `Backend/tests/test_pf005_branches.py` and `Backend/tests/isolation/test_tenant_isolation.py`.

| TC ID | Rule | Scenario | Automated test | Expected |
|-------|------|----------|----------------|----------|
| TC-PF-BR-01 | BR-PF-034 | Community edition calls branch create | `test_tc_pf_br_01_community_forbidden` | 403 (edition gate; error code `FORBIDDEN`) |
| TC-PF-BR-02 | BR-PF-035 | Duplicate branch code (non-deleted) in same tenant | `test_tc_pf_br_02_duplicate_code` | 409 (BR-PF-035) |
| TC-PF-BR-03 | BR-PF-036 | No HEAD_OFFICE branch present | `test_tc_pf_br_03_head_office_warning` | 201 + advisory warning (non-blocking) |
| TC-PF-BR-04 | BR-PF-039 | Professional tenant creates 11th branch | `test_tc_pf_br_04_branch_limit` | 422 (BR-PF-039) |
| TC-PF-BR-05 | BFS §8 | Parent/child hierarchy; cycle rejected | `test_tc_pf_br_05_hierarchy` | 200 / 422 |
| TC-PF-BR-06 | BFS §7/§9 | Address 1:1 create / update / cascade on delete | `test_tc_pf_br_06_address` | 200; address soft-deleted with the branch |
| TC-PF-BR-07 | BR-PF-037 | Delete branch with open projects | *(deferred — no project→branch linkage)* | — |
| TC-PF-BR-08 | RBAC | Sales Manager / Project Manager write attempt | `test_tc_pf_br_08_readonly_roles` | 403 |
| TC-PF-ISO-05 | ADR-015 | Cross-tenant branch / branch_address read | `test_tc_pf_iso_05_branch_cross_tenant` | 404 / 0 rows |

**Batch 2 verification (executed 2026-09-12):** PF-005 tests **15 passed** (`test_pf005_branches.py`); tenant isolation **13 passed** (`tests/isolation/test_tenant_isolation.py`, incl. TC-PF-ISO-05); full backend suite **141 passed, 1 skipped**; **no PF-001…PF-004 regression identified**.

**Deferred test scope (recorded deferrals — not implemented):** AC-PF-005-04 / BR-PF-038 branch-head assignment and `users.branch_id` (**PF-008**); department linkage (**PF-006**); BR-PF-037 project→branch delete restriction (no project→branch linkage yet, so TC-PF-BR-07 stays deferred); NTF-PF-005-* notifications; RPT-PF-005-* reports; runtime permission-grain enforcement (**PF-009**).

### 2.3 PF-006 Department Management (implemented — Batch 5; automated)

**Decision/status recorded 2026-09-16:** the PF-006 test specification for the delivered **backend scope** is **the automated suite `Backend/tests/test_pf006_departments.py` (36 tests)**; no separate manual/manual-script PF-006 pack is defined, and no PF-006 test case is claimed as run outside the commands below. Implementation status: schema (`015_department_pf006.sql` + rollback), RLS enrolment, ORM, schemas, service (incl. Batch 3-C organization-change correction), `department.*` RBAC catalogue/matrix and the **11-operation** API (`app/api/v1/pf/departments.py`) — released 2026-09-16 (annotated tag `Phase-2-PF006`; release baseline `12b24543286b7c79b6145c40dc8a94ffda489021`). Excluded from scope: Flutter UI, workflow/CPS-001, notifications, reports, PF-009 runtime permission grain, department address structures, `users.department_id` (PF-008).

| TC ID | Rule / ref | Scenario | Automated test | Expected |
|-------|-----------|----------|----------------|----------|
| TC-PF-DEP-01 | BFS §10 | Create / detail / list | `test_create_get_and_list` | 201 / 200 |
| TC-PF-DEP-02 | BFS §10 | Search | `test_search_endpoint` | 200 |
| TC-PF-DEP-03 | BFS §10 | PATCH and PUT replacement | `test_patch_and_put` | 200 |
| TC-PF-DEP-04 | BFS §10 | Hierarchy / export / history | `test_hierarchy_export_and_history` | 200 |
| TC-PF-DEP-05 | BFS §10 | Soft delete via API | `test_soft_delete_endpoint` | 200/204; row retained |
| TC-PF-DEP-06 | BFS §10 (±1 approved) | Approved endpoint set present | `test_approved_endpoint_set` | all approved paths present |
| TC-PF-DEP-07 | ADR-015 | Cross-tenant read / write / delete | `test_tenant_isolation_read_write_delete` | 404 / no rows |
| TC-PF-DEP-08 | ADR-015 | Foreign-tenant references | `test_tenant_isolation_foreign_references` | rejected |
| TC-PF-DEP-09 | BFS §12 | Read-only roles (Sales Manager / Project Manager) | `test_permission_matrix_read_only_roles` | read allowed; write 403 |
| TC-PF-DEP-10 | BFS §12 | Denied roles (FINANCE_USER / Support Agent) | `test_permission_matrix_denied_roles` | 403 |
| TC-PF-DEP-11 | BFS §12 | PLATFORM_ADMIN is not a PF-006 actor | `test_platform_admin_not_a_pf006_actor` | denied by the PF-006 gate |
| TC-PF-DEP-12 | C-N4 | Export restricted to Tenant Admin | `test_export_requires_tenant_admin` | 403 for others |
| TC-PF-DEP-13 | BR-PF-041 | Root depth and 6th level | `test_root_depth_and_sixth_level_rejected` | 422 |
| TC-PF-DEP-14 | hierarchy | Self-parent rejected | `test_self_parent_rejected` | 422 |
| TC-PF-DEP-15 | hierarchy | Circular parent rejected | `test_circular_parent_rejected` | 422 |
| TC-PF-DEP-16 | hierarchy | Deleted parent rejected | `test_deleted_parent_rejected` | 422/404 |
| TC-PF-DEP-17 | hierarchy | ACTIVE/INACTIVE/ARCHIVED parent allowed | `test_active_inactive_archived_parent_allowed` | 200/201 |
| TC-PF-DEP-18 | C-N11 | Parent/child same organization enforced | `test_same_organization_parent_enforced` | 422 |
| TC-PF-DEP-19 | Batch 3-C policy | Organization unchanged still works | `test_organization_unchanged_still_works` | 200 |
| TC-PF-DEP-20 | Batch 3-C policy | Root without children may change organization | `test_root_without_children_can_change_organization` | 200 |
| TC-PF-DEP-21 | Batch 3-C policy | Change with retained parent rejected | `test_organization_change_with_retained_parent_rejected` | 422 |
| TC-PF-DEP-22 | Batch 3-C policy | Change with children rejected; no cascade | `test_organization_change_with_children_rejected_and_no_cascade` | 422; children unchanged |
| TC-PF-DEP-23 | Batch 3-C policy | PATCH: detach + organization change allowed | `test_patch_detach_plus_organization_change_allowed` | 200 |
| TC-PF-DEP-24 | Batch 3-C policy | PUT: detach + organization change allowed | `test_put_replacement_detach_plus_organization_change_allowed` | 200 |
| TC-PF-DEP-25 | Batch 3-C policy | Invalid organization → 404 | `test_organization_change_invalid_org_returns_404` | 404 |
| TC-PF-DEP-26 | Batch 3-C policy | No silent reparenting (move + update) | `test_no_silent_reparenting_on_move_and_update` | parent unchanged |
| TC-PF-DEP-27 | branch link | Branch nullable and same-tenant enforced | `test_branch_nullable_and_same_tenant` | 200/201 |
| TC-PF-DEP-28 | branch link | Deleted/foreign branch rejected | `test_branch_deleted_or_foreign_rejected` | 404 |
| TC-PF-DEP-29 | branch link | Branch/organization mismatch allowed (recorded) | `test_branch_organization_mismatch_allowed` | 200/201 |
| TC-PF-DEP-30 | BFS §5 | Status lifecycle transitions | `test_status_lifecycle` | per `STATUS_TRANSITIONS` |
| TC-PF-DEP-31 | locking | Optimistic locking (`version_no`) | `test_optimistic_locking` | 409 |
| TC-PF-DEP-32 | delete guard | Children block delete; no hard delete | `test_child_delete_guard_and_no_hard_delete` | 409; row retained |
| TC-PF-DEP-33 | delete guard | Deleted department untouchable | `test_deleted_department_becomes_untouchable` | 404 |
| TC-PF-DEP-34 | export | Export excludes deleted; JSON only | `test_export_excludes_deleted_and_is_json` | 200 |
| TC-PF-DEP-35 | advisory | Recommended-department advisory (non-blocking) | `test_recommended_department_warning_advisory` | 200/201 + advisory |
| TC-PF-DEP-36 | deferred scope | Deferred scope absent (no `level`/`path`, no `users.department_id`, no address structure) | `test_deferred_scope_absent` | absent |

**Verification (2026-09-16 QA run):** PF-006 tests **36/36 passed**; PF-004/PF-005 regression **35/35 passed**; **0 failed, 0 skipped, 0 errors** (exit 0). Earlier implementation validation run recorded **71 passed**. Test rows are created only in generated test tenants — nothing deleted, truncated or reset.

**Deferred test scope (recorded — not implemented):** Flutter UI acceptance criteria (no PF-006 screens); workflow/approval routing `AC-PF-006-04` (CPS-001 — **non-demonstrable**); `NTF-PF-006-*` notifications; `RPT-PF-006-01/02` reports; CSV/XLSX export; `users.department_id` / user↔department assignment / `department_head_user_id` `BR-PF-043` active-user validation (**PF-008** — **non-demonstrable**, no FK and no validation); runtime permission-grain enforcement (**PF-009**).

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
