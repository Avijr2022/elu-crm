# E-LinkUp QA Release Audit — PF-006 Department Management

**Document ID:** ELU-QA-PF006
**Version:** 1.0 — **RELEASED (2026-09-16)**
**Module:** PF-006 — Department Management (`PF-006-001` Department Structure / `PF-006-001-001` Department Profile), per `ELU-BFS-PF` §PF-006 (Document ID `ELU-BFS-PF-006`)
**Audit Date:** 2026-09-16 (evidence compiled from repository evidence and recorded test results; **no new test execution was performed while preparing this document**)
**Auditor:** **PENDING** — independent-reviewer name/role not recorded in the authorising instruction (ELU-AI-001: no AI-originated approval; the human decision below is transcribed verbatim)
**Related Documents:** ELU-CON-001, ELU-BFS-PF-006, ELU-API-PF §4 (v1.2), ELU-TST-PF §2.3 (v1.5), ELU-MSL-001 (1.24, 1.25), ELU-MSL-002 (4.88, 4.89), ELU-QA-REG-001 (v1.11), ELU-REL-PF006, ADR-015, ELU-EDM-001
**Content / implementation commit:** `b3a2b1f0252340737cae7fc9cd719718adf7ffdd` — `feat(pf): PF-006 Department Management` (20 files, +2984 / −7); **not** the tag target
**Release baseline / tag target:** `12b24543286b7c79b6145c40dc8a94ffda489021` — the governance merge commit of **PR #23** (parents `404c90f` + `b3a2b1f`)
**Release decision:** **`PF-006 RELEASE APPROVED: YES`** — human decision recorded **2026-09-16** (approver Human Project Owner; personal name/role **PENDING** record — role recorded as Project Owner / Authorized Decision Maker)
**Release status:** **RELEASED (2026-09-16)** — backend scope only
**Release tag:** **`Phase-2-PF006`** (annotated) — **created and pushed 2026-09-16**; tag object `f6aefd1442da7772c5fb9d9942bb9fae5cededb5` → target `12b24543286b7c79b6145c40dc8a94ffda489021`
**Verdict:** **PASS — RELEASE APPROVED**

---

## 1. Executive verdict

| Gate | Result at this baseline |
|------|-------------------------|
| PF-006 backend scope implemented | **VERIFIED** — Batches 1–5 incl. 3-C (DDL/rollback/RLS/bootstrap, ORM + schemas, service, Batch 3-C organization-change correction, RBAC catalogue + matrix, API + tests) |
| Implementation integrated into `master` | **VERIFIED** — content commit `b3a2b1f`; merged by **PR #23** as `12b24543…` |
| Endpoint surface exists and is auth-protected | **VERIFIED** — **11 operations on 7 paths** under `/api/v1/org/departments` in `app/api/v1/pf/departments.py`; router registered in `app/api/v1/router.py` |
| Automated test evidence | **VERIFIED AS RECORDED** — **36/36** PF-006 tests (`Backend/tests/test_pf006_departments.py`) + **35/35** PF-004/PF-005 regression tests; **0 failed, 0 skipped, 0 errors** (2026-09-16 QA run); earlier implementation validation run recorded **71 passed**; not re-executed for this document |
| Tenant-isolation evidence | **VERIFIED AS RECORDED** — `test_tenant_isolation_read_write_delete`, `test_tenant_isolation_foreign_references` (PF-006 suite); `core.department` under the PF-003A `tenant_isolation` policy (ADR-015) |
| Database / schema state | **VERIFIED** — `core.department` **19 columns / 7 constraints / 6 indexes**; RLS **enabled + forced**; single PF-003A `tenant_isolation` policy; `Database/03_PlatformFoundation/015_department_pf006.sql` (+ rollback); `RLS_TABLES` = 18 entries |
| RBAC / permission matrix | **VERIFIED** — 5 `department.*` permissions; matrix as adopted (`ELU-BFS-PF` §12) |
| Specified-only / deferred items | **NOT IN RELEASE SCOPE — not claimed** (see §4) |
| Human **RELEASE APPROVED** | **YES** — `PF-006 RELEASE APPROVED: YES`, 2026-09-16 |
| Release tag | **`Phase-2-PF006`** (annotated) — **created and pushed 2026-09-16**; object `f6aefd1442da7772c5fb9d9942bb9fae5cededb5` → target `12b24543286b7c79b6145c40dc8a94ffda489021` |

**Approval provenance:** the human decision `PF-006 RELEASE APPROVED: YES` (2026-09-16) was human-supplied and is transcribed verbatim; the assistant originated no approval (ELU-AI-001). The independent-reviewer signature remains **PENDING** and is recorded as such rather than fabricated.

---

## 2. Mandatory checklist evidence (as applicable to a backend-scope release)

| Item | Evidence | Status |
|------|----------|--------|
| Business specification | `ELU-BFS-PF` §PF-006 (`ELU-BFS-PF-006`) — §10 endpoint list (10), §12 permission matrix; corroborated by `ELU-EFS-001` / `EFS-PF` / `ELU-RTM-001` REQ-PF-014 / REQ-PF-015 | ✓ VERIFIED |
| Database schema / migration | `Database/03_PlatformFoundation/015_department_pf006.sql` (+ `015_department_pf006_rollback.sql`) — idempotent creation of `core.department`; PK, `ck_department_status`, `ck_department_no_self_parent`, FKs tenant / organization (RESTRICT) / parent self-FK (RESTRICT) / branch (**ON DELETE SET NULL**), partial UK `uk_department_tenant_code_active`, four partial indexes | ✓ VERIFIED |
| RLS / tenant isolation | `012_rls_pf003a.sql` loop + `Backend/app/db/migrate_pf003a.py::RLS_TABLES` (18 entries) include `core.department`; ENABLE + FORCE with the existing `tenant_isolation` policy (ADR-015) | ✓ VERIFIED |
| Bootstrap wiring | `Backend/app/db/migrate_pf006.py` (`apply_pf006_ddl`) registered in `Backend/app/main.py` lifespan | ✓ VERIFIED |
| ORM models | `Backend/app/models/pf/entities.py` (`Department`); exports in `Backend/app/models/pf/__init__.py` | ✓ VERIFIED |
| Pydantic schemas | `Backend/app/schemas/pf/department.py` — incl. `DepartmentMove`, `DepartmentHistoryItem`, `DepartmentHistoryResponse` | ✓ VERIFIED |
| Service / business rules | `Backend/app/services/pf/department_service.py` — hierarchy depth (`BR-PF-041`, max 5), active-code uniqueness (`BR-PF-040`), lifecycle transitions, optimistic locking, soft delete, audit, batch 3-C organization-change policy | ✓ VERIFIED |
| Seed / permissions | `Backend/app/db/seed.py` — `department.create/read/update/delete/export`, `DEPARTMENT_PERMISSION_MATRIX` + `_sync_department_permission_matrix`, invoked from all three seed entry points | ✓ VERIFIED |
| FastAPI / OpenAPI surface | `Backend/app/api/v1/pf/departments.py` (static routes before `/{department_id}`); `ELU-API-PF` v1.2 §4 | ✓ VERIFIED |
| API operation count | **11 operations** = the 10 authoritative §10 endpoints **+ 1 human-approved additional history endpoint** `GET /{id}/history` (recorded, approved 2026-09-15; not removed/redesigned) | ✓ VERIFIED |
| Role gate / RBAC behaviour | Read = TENANT_ADMIN / SALES_MANAGER / PROJECT_MANAGER; write + export = TENANT_ADMIN; FINANCE_USER and Support Agent hold no `department.*` grant; **PLATFORM_ADMIN denied by the PF-006 gate** (matrix deliberately unchanged) | ✓ VERIFIED |
| Automated unit/integration tests | `Backend/tests/test_pf006_departments.py` — 36 tests; `Backend/tests/test_pf005_branches.py` deferred-scope assertion updated to assert `core.department` **exists** | ✓ VERIFIED AS RECORDED |
| Tenant isolation tests | PF-006 isolation tests within the suite (cross-tenant read/write/delete; foreign references) | ✓ VERIFIED AS RECORDED |
| Regression against baselined modules | **35/35** PF-004/PF-005 regression tests passed; **no PF-001…PF-005 regression identified** | ✓ VERIFIED AS RECORDED |
| Flutter UI / responsive / accessibility | No department screens implemented (`ELU-UI-PF`: specification only) | ✗ NOT IN SCOPE — not claimed |
| Notifications / reports | `NTF-PF-006-*`, `RPT-PF-006-01/02` deferred | ✗ NOT IN SCOPE — not claimed |
| Workflow / approval routing | `AC-PF-006-04` requires CPS-001 approval workflow | ✗ NOT IN SCOPE — **NON-DEMONSTRABLE** |
| QA release audit (this document) | Created 2026-09-16 under the PF-001…PF-005 document pattern; **independent review outstanding** | ⏳ PENDING (reviewer identity) |
| Release notes | `ELU-REL-PF006-Phase-2-PF006-Release-Notes.md` — created 2026-09-16 | ✓ RECORDED |
| Human release approval | **`PF-006 RELEASE APPROVED: YES`** — 2026-09-16 (approver personal name **PENDING**) | ✓ RECORDED |
| Release tag | **`Phase-2-PF006`** — annotated, created and pushed 2026-09-16 | ✓ RECORDED |

---

## 3. Business-rule and acceptance-criteria status at this baseline

| Ref | Statement / rule | Status at this baseline |
|-----|------------------|-------------------------|
| `BR-PF-041` | Maximum department depth **5** (root depth 1) | Implemented and automated (`TC-PF-DEP-13`) |
| `BR-PF-040` | Active department code unique per tenant | Implemented (partial unique index `uk_department_code_tenant_code_active`) |
| `C-N11` | Parent and child must belong to the same organization | Implemented and automated (`TC-PF-DEP-18`) |
| `C-N1` | `department_type` has no CHECK/enum/API value validation | Implemented as approved (no value list exists in the specification) |
| `C-N2` | No persisted `level` / `path` (derived at read time) | Implemented and asserted (`TC-PF-DEP-36`) |
| `C-N3` | `status` ACTIVE / INACTIVE / ARCHIVED, default ACTIVE; ARCHIVED terminal | Implemented and automated (`TC-PF-DEP-30`) |
| `C-N4` | `department.export` = Tenant Admin only (implementation decision — §12 has no export column) | Implemented and automated (`TC-PF-DEP-12`) |
| `C-N5` / `C-N6` | `description` VARCHAR(500) / `cost_centre_code` VARCHAR(32); **no** address structures | Implemented as approved |
| Batch 3-C policy | Organization change: effective parent `NULL`, no non-deleted children, no cascade, no silent reparenting, combined detach + change allowed, invalid/foreign/deleted organization → 404 | Implemented and automated (`TC-PF-DEP-19` … `TC-PF-DEP-26`) |
| `AC-PF-006-04` | Approval-workflow routing to the department head | **NON-DEMONSTRABLE at this baseline** — requires CPS-001; recorded deferral |

---

## 4. Deferred / non-demonstrable — recorded, not claimed as delivered

| Item | Disposition |
|------|-------------|
| `users.department_id`, user↔department assignment, `department` → `users` linkage | **PF-008 Users & Identity** — not implemented in PF-006 (`core.users` has **no** `department_id`) |
| `BR-PF-043` department head must be an ACTIVE user in the same tenant | **DEFERRED to PF-008** — `department_head_user_id` is a plain nullable UUID with **no FK and no validation** → **non-demonstrable** |
| `AC-PF-006-04` approval-workflow routing (CPS-001) | **NON-DEMONSTRABLE** |
| Flutter UI (BFS §11 screens) | Excluded from this release; specification only |
| `NTF-PF-006-01..03` notifications, `RPT-PF-006-01/02` reports | Deferred |
| CSV/XLSX export | Deferred — JSON export only |
| Department address structures | Excluded by approved decision (C-N6) |
| Runtime permission-grain enforcement | **PF-009** — role gates only at this baseline |
| Edition gating | **None** — `ELU-EDM-001`: Multi-Department available in Community, Professional and Enterprise |
| Open specification gap (recorded, not invented) | `department_type` has no value list anywhere in the approved specification → no CHECK/enum/value validation (C-N1) |

---

## 5. Recorded advisory — outside this release's scope (not fixed by PF-006)

| # | Advisory | Scope status |
|---|----------|--------------|
| A1 | Generic `app/core/rbac.py::has_permission` returns `True` for PLATFORM_ADMIN (universal bypass), while the PF-006 gate denies PLATFORM_ADMIN | **Recorded technical debt (PF-009)**. The PF-006 matrix is deliberately unchanged; **no PF-009 implementation exists** and **no technical-debt register entry was added** |

**No claim is made that PF-006 fixes or depends on A1.**

---

## 6. Approval

- [x] Independent QA release audit recorded (this document, v1.0 — **PASS — RELEASE APPROVED**; reviewer identity remains **PENDING**)
- [x] Human **RELEASE APPROVED** recorded — **`PF-006 RELEASE APPROVED: YES`** (2026-09-16; approver personal name **PENDING**)
- [x] `ELU-QA-REG-001` (v1.11) / `ELU-MSL-001` (1.24, 1.25) / `ELU-MSL-002` (4.88, 4.89) / `Documentation/CHANGELOG.md` release entries recorded
- [x] Release baseline / tag target recorded — `12b24543286b7c79b6145c40dc8a94ffda489021`
- [x] Annotated release tag recorded — `Phase-2-PF006`, object `f6aefd1442da7772c5fb9d9942bb9fae5cededb5` → `12b24543286b7c79b6145c40dc8a94ffda489021`
- [ ] Independent reviewer name / role — **PENDING (not invented)**

---

*© Euphoria Infotech (I) Limited — ELU-QA-PF006*
