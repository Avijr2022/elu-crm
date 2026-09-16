# Release Notes — PF-006 Department Management

**Document ID:** ELU-REL-PF006
**Release:** Phase-2-PF006
**Status:** **RELEASED — ANNOTATED TAG `Phase-2-PF006` CREATED AND PUSHED 2026-09-16**
**Date:** 2026-09-16 (release approval recorded; tag created and pushed)
**Human approval:** **`PF-006 RELEASE APPROVED: YES`** (2026-09-16; approver Human Project Owner — personal name/role **pending record**)
**Git tag:** **`Phase-2-PF006`** (annotated) — **created and pushed 2026-09-16**; tag object `f6aefd1442da7772c5fb9d9942bb9fae5cededb5` → target commit `12b24543286b7c79b6145c40dc8a94ffda489021`
**Prior baselines:** Phase-2-PF001, Phase-2-PF002, Phase-2-PF003, Phase-2-PF003A, Phase-2-PF004-R1, Phase-2-PF005
**QA:** ELU-QA-PF006 v1.0 — **PASS — RELEASE APPROVED** (2026-09-16; independent reviewer **PENDING**)

---

## Release baseline

| Item | Value |
|------|-------|
| **Release baseline (declared)** | **`12b24543286b7c79b6145c40dc8a94ffda489021`** — the PF-006 governance merge commit (**PR #23**), which is also the annotated tag target |
| Governance merge commit (tag target) | `12b24543286b7c79b6145c40dc8a94ffda489021` — "Merge pull request #23 from Avijr2022/cursor/pf006-start-authorization-governance" (parents `404c90f` + `b3a2b1f`); `master` = `origin/master` at tag creation time |
| Content / implementation commit | `b3a2b1f0252340737cae7fc9cd719718adf7ffdd` — `feat(pf): PF-006 Department Management` (20 files, +2984 / −7); **not** the tag target; no dedicated no-change baseline commit was created |
| Human release approval | **`PF-006 RELEASE APPROVED: YES`** — 2026-09-16; approver Human Project Owner, role Project Owner / Authorized Decision Maker; **personal name PENDING** (human-supplied decision transcribed verbatim; ELU-AI-001) |
| Release tag | **`Phase-2-PF006`** — **annotated** — **created and pushed 2026-09-16**; tag object `f6aefd1442da7772c5fb9d9942bb9fae5cededb5`; peels to `12b24543286b7c79b6145c40dc8a94ffda489021` |
| Tag verification | `git rev-parse Phase-2-PF006` → `f6aefd14…` · `git rev-parse Phase-2-PF006^{}` → `12b24543…` · remote `refs/tags/Phase-2-PF006` present (verified 2026-09-16) · total tags **11** · all pre-existing tags unchanged |
| Prior tag precedent | PF-005 released with the same model: content baseline `219bb6c` **not** tagged, annotated tag `Phase-2-PF005` on the PF-005 governance merge `bdc188c8…` |

## Implementation summary (what was delivered)

- **Schema / DDL:** `Database/03_PlatformFoundation/015_department_pf006.sql` (+ `015_department_pf006_rollback.sql`) — idempotent `core.department`: **19 columns / 7 constraints / 6 indexes**; PK, `ck_department_status`, `ck_department_no_self_parent`, FKs `fk_department_tenant`, `fk_department_organization` (**RESTRICT**), `fk_department_parent` (**RESTRICT**, self-FK), `fk_department_branch` (**ON DELETE SET NULL**), partial unique key `uk_department_tenant_code_active`, partial indexes `idx_department_tenant_status` / `idx_department_organization` / `idx_department_parent` / `idx_department_branch`. No department address table; no persisted `level`/`path`.
- **RLS:** `core.department` enrolled via `012_rls_pf003a.sql` + `Backend/app/db/migrate_pf003a.py::RLS_TABLES` (**18 entries**) — ENABLE + FORCE with the existing PF-003A `tenant_isolation` policy (ADR-015). No second RLS mechanism.
- **Bootstrap:** `Backend/app/db/migrate_pf006.py` (`apply_pf006_ddl`) registered in the `Backend/app/main.py` lifespan.
- **ORM / schemas:** `Department` in `Backend/app/models/pf/entities.py` (exports in `app/models/pf/__init__.py`); `Backend/app/schemas/pf/department.py` incl. `DepartmentMove`, `DepartmentHistoryItem`, `DepartmentHistoryResponse`.
- **Service / business rules:** `Backend/app/services/pf/department_service.py` — role gates; hierarchy rules (`BR-PF-041` max depth 5, root depth 1); active-code uniqueness (`BR-PF-040`); organisation / branch resolution; status lifecycle (`ACTIVE → INACTIVE`, `INACTIVE → {ACTIVE, ARCHIVED}`, ARCHIVED terminal); optimistic locking; soft delete with child-delete guard; audit events; advisory recommended-department warning (non-blocking).
- **Organization-change policy (Batch 3-C, human-approved effective-parent-`NULL` reading):** organization **unchanged** allowed; change + effective parent `NULL` + no non-deleted children allowed; effective parent non-`NULL` rejected; non-deleted children rejected; a single PATCH/PUT may combine parent detach with an organization change; **no cascade**; **no silent reparenting**; **C-N11** enforced; invalid / foreign-tenant / soft-deleted organization → **404**.
- **RBAC:** `department.create/read/update/delete/export` in `Backend/app/db/seed.py` with `DEPARTMENT_PERMISSION_MATRIX` + idempotent `_sync_department_permission_matrix`, invoked from all three seed entry points. Seeded matrix (`ELU-BFS-PF` §12): TENANT_ADMIN `create/read/update/delete/export`; SALES_MANAGER `read`; PROJECT_MANAGER `read`; FINANCE_USER **no grant**; PLATFORM_ADMIN **no grant** (explicit empty tuple so the seeded map matches the enforced PF-006 role gate); Support Agent not granted. **Naming note:** the requested action `view` is realised as **`read`**, matching the authoritative permission list and the `organization.read` / `branch.read` convention.
- **API:** `Backend/app/api/v1/pf/departments.py` (registered in `app/api/v1/router.py`) — prefix `/api/v1/org/departments`, **11 operations on 7 paths**:

| Method | Path | Purpose | Permission |
|--------|------|---------|------------|
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

**Endpoint-count note (recorded honestly):** the authoritative `ELU-BFS-PF` §PF-006 §10 list contains **10** endpoints; **+ 1** human-approved additional audit-history endpoint = **11** implemented operations. The history endpoint is **human-approved PF-006 scope** (decision 2026-09-15) and must not be removed, redesigned or reimplemented.

## Release scope — PF-006 backend scope only

**In scope (backend):** approved decisions **C-N1…C-N6**; the DDL/rollback, RLS enrolment, bootstrap wiring, ORM, schemas, service (incl. Batch 3-C organization-change correction), RBAC catalogue + seeded matrix and the API + tests listed above; batch/audit verdicts: Batch 1 **PASS**, Batch 2 **PASS**, Batch 3 **PASS WITH NON-BLOCKING NOTES**, Batch 3-C **PASS WITH NON-BLOCKING NOTES**, Batch 4 **PASS**, Batch 5 **PASS WITH NON-BLOCKING NOTES**.

**Explicitly excluded from release scope:**

| Excluded | Reason / disposition |
|----------|----------------------|
| **Flutter UI** — department list / create / edit / view / search / hierarchy / history | **Excluded from PF-006 release scope.** No department pages delivered; `ELU-UI-PF` records them as specification only |
| `users.department_id`, user↔department assignment, `department` → `users` linkage | Deferred to **PF-008 Users & Identity** (`core.users` has no `department_id`) |
| `BR-PF-043` department head = ACTIVE user of the same tenant | **Deferred to PF-008** — `department_head_user_id` has **no FK and no validation** → **non-demonstrable** |
| `AC-PF-006-04` approval-workflow routing to the department head | **NON-DEMONSTRABLE** — requires **CPS-001** workflow engine |
| `NTF-PF-006-01..03` notifications | Deferred |
| `RPT-PF-006-01/02` reports | Deferred |
| CSV/XLSX export | Deferred — JSON export only |
| Department address structures | Excluded by approved decision (C-N6) |
| Runtime permission-grain enforcement | Deferred to **PF-009** (role gates only at this baseline) |
| PF-009 technical-debt register entry (generic `rbac.has_permission` PLATFORM_ADMIN bypass) | **Recorded as technical debt; deliberately NOT added to any register** — outside the authorization for this reconciliation |

## Verification evidence

- **Automated evidence (2026-09-16 QA run, recorded in `ELU-TST-PF` §2.3 v1.5, `ELU-MSL-001` 1.24/1.25 and `ELU-MSL-002` 4.88/4.89):** PF-006 tests **36/36 passed** (`Backend/tests/test_pf006_departments.py`); PF-004/PF-005 regression **35/35 passed**; **0 failed, 0 skipped, 0 errors** (exit 0); **no release blockers identified**. An earlier implementation validation run recorded **71 passed**. `git diff --check` clean; all changed Python files compile.
- **Schema evidence:** `core.department` **19 columns / 7 constraints / 6 indexes**; RLS **enabled + forced**; single PF-003A `tenant_isolation` policy; idempotent re-apply leaves constraints at 7 and RLS true/true; no previously RLS-enabled table lost RLS.
- **Test-data hygiene:** PF-006 test rows exist only in generated test tenants; nothing was deleted, truncated or reset.
- No new test execution was performed while preparing this document; no test result beyond the evidence above is claimed.

## Approval

- [x] Independent QA release audit recorded (ELU-QA-PF006 v1.0 — **PASS — RELEASE APPROVED**; reviewer identity remains **PENDING**)
- [x] Human **RELEASE APPROVED** recorded — **`PF-006 RELEASE APPROVED: YES`** (2026-09-16; approver personal name **PENDING**)
- [x] `ELU-QA-REG-001` v1.11 / `ELU-MSL-001` 1.25 / `ELU-MSL-002` 4.89 / `Documentation/CHANGELOG.md` release entries recorded
- [x] Release baseline declared and annotated tag `Phase-2-PF006` created and pushed (2026-09-16)
- [ ] Independent reviewer name / role — **PENDING (not invented)**

---

*© Euphoria Infotech (I) Limited — ELU-REL-PF006*
