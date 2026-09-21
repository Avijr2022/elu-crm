# Changelog

All notable E-LinkUp implementation milestones.

### 2026-09-21
- Governance: split PF-007 Business Unit and PF-008 Users & Identity in MSL-001.
- Preserved PF-007 Correction-A release facts and corrected PF progress arithmetic to 7 / 11 (64%), with 4 remaining.
- PF-008 remains NOT STARTED; this change authorizes no implementation.

## [PF-007] — 2026-09-16 — Scope Decisions Approved

PF-007 human scope decisions D1–D11 approved. Governance boundaries are recorded before implementation.

- 8 BFS-defined endpoints; no history API.
- Tenant Admin-only Business Unit export.
- Project Manager read-only boundary.
- ACTIVE same-tenant BU-manager validation.
- Professional limit 20; Enterprise unlimited.
- Opportunity-to-BU linkage authorized; project/invoice linkage deferred.
- `organization_id` immutable after creation.
- Minimum AC-PF-007-03 reporting scope; no general reporting engine.
- Field typing/validation to follow established PF conventions and be documented.
- Backend-only release; Flutter UI deferred.
- `core.business_unit` + tenant RLS + partial unique active-code constraint authorized.
- **PF-007 SCOPE DECISION GOVERNANCE RECORDED: YES**

## [PF-007] — 2026-09-16 — START AUTHORIZATION RECORDED AND GOVERNANCE SCOPE RECONCILED (GOVERNANCE ONLY — NO IMPLEMENTATION)

> **Governance recording only.** No code, schema, DDL, migration, seed, test, frontend, PF-008 or PF-009 change; **no release approval, no QA/CD record and no release tag** is created or implied by this entry.

### Human decision (recorded verbatim)
- **`PF-007 START AUTHORIZED: YES`** — 2026-09-16. Approver identity **PENDING** (not supplied in the authorising instruction; **not invented** — ELU-AI-001).

### Authoritative scope
- Module per `ELU-BFS-PF` §PF-007: **PF-007 Business Unit Management** / sub-module **PF-007-001 Business Unit** / feature **PF-007-001-001 Business Unit Profile**.
- **Edition:** **Professional + Enterprise; Community excluded** (`BR-PF-046`).
- **Included scope:** Business Unit management, opportunity → Business Unit tagging, and demonstrable BU revenue-report capability required by the approved PF-007 acceptance criteria.
- **`RPT-PF-007-02` constraint:** Revenue by Business Unit (PDF+XLSX) is included only to the extent required to demonstrate the approved PF-007 acceptance criteria; no broader reporting scope is authorized.
- **Deferred / excluded:** PF-008-owned user ↔ Business Unit and BU-manager linkage; PF-009-owned runtime permission grain; `NTF-PF-007-01..03` notifications; Flutter UI; any scope not listed above.

### Reconciliation recorded in this entry
- `ELU-MSL-001` — §3.1 tracker row aligned to **START AUTHORIZED — IN PROGRESS**; the PF-007 authorization record moved **inside** the document body (before the footer); the `RPT-PF-007-02` constraint added; **Version History row 1.26** added.
- `ELU-MSL-002` — change-log row **4.90**.
- The original human decision text is preserved unchanged; no approver identity, date or decision was invented.

### Not done
- No PF-007 implementation (no DDL/ORM/service/API/seed/tests), **no `ELU-QA-PF007`**, **no `ELU-REL-PF007`**, no RTM/API/TST PF-007 sections, no release approval, no release tag, no tag operation of any kind.
  - **Supersede note — 2026-09-18 (documentation correction only; no new decision, no approval):** the PF-007 statement above was correct when recorded and is preserved unchanged. **Superseded** by subsequent posted repository state: the PF-007 implementation (Batch 1, commit `1cd4997f`, PR #26 → merge `d752eb7bba535b56377ed2e66240de28dd47db9a`); `ELU-REL-PF007-Phase-2-PF007-Release-Notes.md`; the `ELU-RTM-001` PF-007 release-traceability record and the `ELU-API-PF.md` PF-007 endpoint section; the PF-007 human release approval (recorded in the PF-007 Release Governance Record at the end of this file); and the annotated release tag `Phase-2-PF007` (tag object `bde87e9ee31d2f4c9a25ffdd7169cc9f90607a68` → release commit `80ae94e1dd071f62198571a7592cf81246ee591e`). **Still current / NOT superseded:** no `ELU-QA-PF007` exists — no QA verdict, reviewer, date or test result is recorded anywhere; and no PF-007 section exists in `ELU-TST-PF.md`.
- **PF-006 remains RELEASED and frozen** — `Phase-2-PF006` (object `f6aefd1442da7772c5fb9d9942bb9fae5cededb5` → target `12b24543286b7c79b6145c40dc8a94ffda489021`) unchanged.

### Idempotency marker
- PF-007 RECONCILIATION RECORDED: YES

PF-007 Batch 1 merge recorded: PR #26 -> d752eb7bba535b56377ed2e66240de28dd47db9a

## [PF-006] — 2026-09-16 — POST-TAG GOVERNANCE RECONCILIATION (ANNOTATED TAG CREATED AND PUSHED)

> **Governance recording only.** No code, schema, API, database, migration, seed, test, frontend or PF-008/PF-009 change. **This entry creates no release artefact:** the annotated tag, its target, the release baseline and the release-approval decision are **recorded as already existing** — nothing is created, moved, re-pointed or deleted by this reconciliation.

### Authorization
- **`PF-006 POST-TAG GOVERNANCE RECONCILIATION AUTHORIZED: YES`** — human authorization. Operator identity **PENDING** (not supplied; not invented — ELU-AI-001).

### Authoritative PF-006 release state (recorded as current)

| Item | Value |
|---|---|
| Human release approval | **`PF-006 RELEASE APPROVED: YES`** — 2026-09-16; approver **Human Project Owner** (personal name not supplied — **PENDING**, not invented), role **Project Owner / Authorized Decision Maker** |
| **Release baseline (declared)** | **`12b24543286b7c79b6145c40dc8a94ffda489021`** — declared by the human authorization for this reconciliation; **supersedes** the earlier `404c90f…` *candidate only* statement |
| Implementation / content commit | `b3a2b1f0252340737cae7fc9cd719718adf7ffdd` — `feat(pf): PF-006 Department Management` (20 files, +2984 / −7) |
| Governance merge (tag target) | `12b24543286b7c79b6145c40dc8a94ffda489021` — "Merge pull request #23 from Avijr2022/cursor/pf006-start-authorization-governance"; parents `404c90f` + `b3a2b1f` |
| **Annotated release tag** | **`Phase-2-PF006`** — **created and pushed 2026-09-16**; tag object **`f6aefd1442da7772c5fb9d9942bb9fae5cededb5`** → target **`12b24543286b7c79b6145c40dc8a94ffda489021`** |
| Remote verification | `refs/tags/Phase-2-PF006` = `f6aefd14…`; `refs/tags/Phase-2-PF006^{}` = `12b24543…`; `origin/master` = `12b24543…`; total tags 11; all pre-existing tags unchanged |
| Release status | **PF-006 Department Management — RELEASED** (backend scope only) — same model as the PF-005 precedent: the implementation/content commit is **not** the tag target; the governance merge commit is |

### Reconciliation performed in this change set
- Corrected the stale **current-state** statements in this file, `ELU-MSL-001`, `ELU-MSL-002` and `ELU-QA-REG-001` that asserted the PF-006 tag was absent / not authorized, or that `404c90f…` was the current `HEAD` / `origin/master` / candidate-only baseline.
- Appended concise **supersede notes** to the historical PF-006 records (this file's earlier PF-006 entries, `ELU-MSL-001` history row **1.22**, `ELU-MSL-002` change-log **4.86**). Their original statements are **preserved** and remain accurate as at their own dates; they were valid at the time and were subsequently superseded by the PR #23 merge (`12b24543…`) and the `Phase-2-PF006` release.
- **Created** `Documentation/ELU-QA-PF006-Department-Management-Release-Audit.md` and `Documentation/ELU-REL-PF006-Phase-2-PF006-Release-Notes.md`, following the established PF-001…PF-005 naming/structure, using verified PF-006 facts only.
- **Updated** `11-Engineering/ELU-TST-PF.md` to **v1.5** with a PF-006 test-specification section (**§2.3**) recording the PF-006 test-spec decision/status (36 automated PF-006 tests).

### Still PENDING (reported, not invented)
- Approver **personal name** for the PF-006 release approval (role recorded; name never supplied).
- **Independent-reviewer / auditor identity** on `ELU-QA-PF006` (document now created; reviewer **PENDING**).
- Deferred/excluded and unchanged: Flutter UI, workflow/approval engine (CPS-001), `NTF-PF-006-*`, `RPT-PF-006-01/02`, PF-009 runtime permission grain, department address structures; `users.department_id`, user↔department assignment and department-head FK/active-user validation remain **PF-008-owned**.

### Not done by this reconciliation
- **No tag** was created, moved, re-pointed, deleted or force-updated. `Phase-2-PF006` and `Phase-2-PF005` are **unchanged by this change set**.
- No change to `origin/master` (`12b24543…`), no merge, no release certification, no PF-006 scope change.
- No application code, schema, API, ORM, service, router, database, migration/DDL, seed, test, frontend, PF-008 or PF-009 change.
- The optional **PF-009 technical-debt register entry was NOT added** — it is outside this authorization.

## [PF-006] — 2026-09-16 — RELEASE APPROVED BY HUMAN DECISION (NO TAG CREATED AT THAT TIME) — SUPERSEDED IN PART

> Governance recording of an **explicit human decision**. No code, schema, API, database, migration, seed, test, frontend or PF-008/PF-009 change; **at the time of this entry no release tag had been created** and **no tag creation had been authorized**. **Superseded 2026-09-16 — see the POST-TAG GOVERNANCE RECONCILIATION entry above:** the release baseline is now declared and the annotated tag `Phase-2-PF006` (object `f6aefd1442da7772c5fb9d9942bb9fae5cededb5` → target `12b24543286b7c79b6145c40dc8a94ffda489021`) has been created and pushed.

### Human decision (recorded verbatim)
- **`PF-006 RELEASE APPROVED: YES`** — Human Project Owner (personal name not supplied — **PENDING**, not invented; ELU-AI-001 — no AI-originated approval). **Approver role:** Project Owner / Authorized Decision Maker. **Decision date:** 2026-09-16.
- Approved scope: **PF-006 Department Management** (PF-006-001 Department Structure / PF-006-001-001 Department Profile), **backend scope only**.

### QA result reconciled (authoritative facts, unchanged)
- **PF-006 QA: PASSED** — no release blockers identified by the formal QA audit (2026-09-16).
- **36/36** PF-006 tests passed; **35/35** PF-004/PF-005 regression tests passed (0 failed, 0 skipped, 0 errors; exit 0).
- In approved scope: the **additional human-approved history endpoint** `GET /org/departments/{department_id}/history` (10 authoritative `ELU-BFS-PF` §PF-006 §10 endpoints **+ 1** approved = **11** operations) and the **human-approved effective-parent-`NULL` organization-change policy**.
- Schema on record: `core.department` 19 columns / 7 constraints / 6 indexes / RLS enabled + forced / single PF-003A `tenant_isolation` policy; `core.users` has no `department_id`; no persisted `level`/`path`; no `department_type` value constraint.

### Release baseline — CANDIDATE ONLY at the time of this entry (NOW SUPERSEDED)
- Evidence / **baseline candidate (as recorded then):** `404c90f27d54ddc1ff9ae03580d24e49f195467d` — then-current `HEAD`, equal to `origin/master`. **That SHA was recorded as a candidate only**; the final release baseline/SHA decision remained a separate human decision (the PF-005 precedent required an explicit baseline decision rather than automatic adoption of the current `HEAD`).
- **At the time of this entry no PF-006 release tag existed** and **tag creation was not authorized**; `Phase-2-PF005` and every other existing tag were unchanged.
- **Superseded 2026-09-16 (POST-TAG GOVERNANCE RECONCILIATION):** the release baseline is **declared as `12b24543286b7c79b6145c40dc8a94ffda489021`**, implementing/content commit `b3a2b1f0252340737cae7fc9cd719718adf7ffdd`, and the annotated tag **`Phase-2-PF006`** (object `f6aefd1442da7772c5fb9d9942bb9fae5cededb5` → target `12b24543286b7c79b6145c40dc8a94ffda489021`) has been **created and pushed**. `404c90f…` is **no longer** current `HEAD`/`origin/master`; `origin/master` is `12b24543…`.

### Deferred / excluded (unchanged)
- Flutter UI, workflow/approval engine (CPS-001), notifications (`NTF-PF-006-*`), reports (`RPT-PF-006-01/02`), PF-009 runtime permission grain, department address structures.
- `users.department_id`, user↔department assignment and department-head FK/active-user validation remain **PF-008-owned**.
- **PF-009 technical debt (recorded, unchanged and NOT added to any register):** generic `app.core.rbac.has_permission` PLATFORM_ADMIN universal bypass versus the PF-006 gate denial.

### Governance records — recorded here, then reconciled 2026-09-16
- `ELU-QA-PF006` QA release-audit document — **QA-Director-owned.** *As recorded at the time of this entry:* not created (the completed QA result was recorded in `ELU-QA-REG-001` v1.10, `ELU-MSL-001` 1.24, `ELU-MSL-002` 4.88 and this entry). **Created 2026-09-16:** `Documentation/ELU-QA-PF006-Department-Management-Release-Audit.md` (v1.0 — **PASS — RELEASE APPROVED**); the independent-reviewer identity remains **PENDING**.
- `ELU-REL-PF006` release notes — *As recorded at the time of this entry:* not created (pending the release tag / baseline decision — now resolved). **Created 2026-09-16:** `Documentation/ELU-REL-PF006-Phase-2-PF006-Release-Notes.md`.
- `ELU-TST-PF` PF-006 test-specification section — *As recorded at the time of this entry:* pending governance decision. **Recorded 2026-09-16:** `11-Engineering/ELU-TST-PF.md` **v1.5 §2.3**.

### Not done (at the time of this entry) — subsequently completed
- No commit, no push, no PR, no merge, **no tag**, no release certification at the time of this entry.
- **Superseded 2026-09-16:** the PF-006 change set was subsequently committed (`b3a2b1f0252340737cae7fc9cd719718adf7ffdd`), pushed, opened and merged as **PR #23** (merge commit `12b24543286b7c79b6145c40dc8a94ffda489021`), and the annotated tag **`Phase-2-PF006`** was created and pushed. **PF-006 is now RELEASED** (backend scope only). See the POST-TAG GOVERNANCE RECONCILIATION entry above.

## [PF-006] — 2026-09-15 — HUMAN SCOPE DECISIONS RECORDED (HISTORY ENDPOINT + ORGANIZATION-CHANGE POLICY) — NO RELEASE ACTION

> Governance-only record of **two explicit human approvals** by the Human Project Owner. No code, schema, API, database, migration, seed, test, frontend, PF-008 or PF-009 change. **PF-006 RELEASE APPROVAL remains PENDING**, and no release baseline, tag or certification is recorded.

### Decision 1 — PF-006 history endpoint: **APPROVED AND RETAINED**
- `GET /api/v1/org/departments/{department_id}/history` is **HUMAN-APPROVED PF-006 SCOPE** — retained as an **additional** PF-006 audit-history endpoint.
- Recorded honestly: it is **not** part of the authoritative `ELU-BFS-PF` §PF-006 §10 endpoint list, which contains **10** endpoints. Counts: **§10 = 10**, **+ 1 human-approved history endpoint**, **total implemented PF-006 API operations = 11**.
- It was already implemented and tested in Batch 5 (typed `DepartmentHistoryResponse`, `DepartmentService.history()`); it must **not** be removed, redesigned or reimplemented.
- **Approved by:** Human Project Owner — **personal name not supplied in the authorising instruction (PENDING; not invented — ELU-AI-001)**. **Approver role:** Project Owner / Authorized Decision Maker. **Decision date:** 2026-09-15.

### Decision 2 — PF-006 organization-change policy: **APPROVED (effective-parent-NULL interpretation)**
- Recorded verdict verbatim: *"Human Project Owner approved the effective-parent-NULL interpretation for PF-006 organization changes."*
- Approved behaviour (already implemented in **Batch 3-C** — **no implementation change in this batch**):
  1. organization **unchanged** → allowed;
  2. organization change + effective parent `NULL` + **no non-deleted children** → allowed;
  3. organization change + effective parent **non-`NULL`** → rejected;
  4. organization change + one or more **non-deleted children** → rejected;
  5. a **single** update (PATCH or PUT) may **simultaneously detach the parent and change `organization_id`** when there are no non-deleted children → allowed;
  6. **no cascade** of the organization change — ever;
  7. **no silent reparenting** — ever;
  8. the **parent/child same-organization rule (C-N11) remains enforced**; invalid, foreign-tenant or soft-deleted organizations remain **404**.
- This **closes** the previously recorded items 1-vs-6 scope question in favour of the **stricter effective-parent-`NULL` reading**.
- **Approved by:** Human Project Owner (personal name not supplied — **PENDING**, not invented). **Decision date:** 2026-09-15.

### Still pending (NOT approved by this record)
- **PF-006 RELEASE APPROVAL — PENDING** (separate human decision). Release baseline/SHA decision and release tag also remain pending.
- `ELU-QA-REG-001` PF-006 row (**QA-Director-owned**), `ELU-QA-PF006` release audit, `ELU-REL-PF006` release notes and the `ELU-TST-PF` PF-006 test-spec decision remain outstanding — none is created or approved here.
- **PF-009 technical debt (recorded, unchanged):** the generic `app.core.rbac.has_permission` PLATFORM_ADMIN universal bypass versus the PF-006 gate denial. The PF-006 permission matrix is deliberately unchanged and no PF-009 implementation is created.

### Not done (explicitly out of scope)
- No application code, schema, ORM, service, router, database, migration/DDL, seed, test, frontend, PF-008 or PF-009 change.
- No commit, no push, no PR, no merge, no tag, no release approval and no release certification.
- Deferred scope remains deferred: Flutter UI, workflow/approval engine, notifications, reports, PF-009 runtime permission grain, department address structures; `users.department_id`, user↔department assignment and department-head FK/active-user validation remain **PF-008-owned**.
- **PF-005 Branch Management remains RELEASED and frozen** — annotation/tag `Phase-2-PF005` unchanged.

## [PF-006] — 2026-09-15 — GOVERNANCE RECONCILIATION (BATCHES 2, 3, 3-C AND 5 RECORDED) — NO RELEASE ACTION

> **Governance-only reconciliation.** This entry records implementation work that is **already complete and audited**. It adds no code, no schema/API behaviour, no database change and **records no release approval**. Authored by EIIP / Engineering — **approver identity PENDING (not supplied in the authorising instruction; not invented — ELU-AI-001)**.

### Implementation record (all batches complete and audited)

| Batch | Scope delivered | Audit verdict | Artefacts |
|---|---|---|---|
| **Batch 1** | DDL + rollback + RLS enrolment + bootstrap wiring | **PASS** | `Database/03_PlatformFoundation/015_department_pf006[_rollback].sql`, `Database/03_PlatformFoundation/012_rls_pf003a.sql`, `Backend/app/db/migrate_pf006.py`, `Backend/app/main.py` |
| **Batch 2** | `Department` ORM model + Pydantic schemas | **PASS** | `Backend/app/models/pf/entities.py`, `Backend/app/models/pf/__init__.py`, `Backend/app/schemas/pf/department.py` |
| **Batch 3** | Department service: business rules, hierarchy, organisation/branch resolution, status lifecycle, optimistic locking, soft delete, audit events | **PASS WITH NON-BLOCKING NOTES** | `Backend/app/services/pf/department_service.py` |
| **Batch 3-C** | Organization-change correction — effective parent `NULL`, no non-deleted children, no cascade, no silent reparenting, combined detach + change allowed, C-N11 enforced | **PASS WITH NON-BLOCKING NOTES** | `Backend/app/services/pf/department_service.py` |
| **Batch 4** | PF-006 permission catalogue (`department.create/read/update/delete/export`) + seeded role–permission matrix | **PASS** | `Backend/app/db/seed.py` |
| **Batch 5** | Department API router + route wiring + move/history schemas + typed history response + PF-006 tests + PF-005 deferred-scope test correction | **PASS WITH NON-BLOCKING NOTES** | `Backend/app/api/v1/pf/departments.py`, `Backend/app/api/v1/router.py`, `Backend/app/schemas/pf/department.py`, `Backend/app/services/pf/department_service.py`, `Backend/tests/test_pf006_departments.py`, `Backend/tests/test_pf005_branches.py` |

### Verified Batch-5 surface (release candidate — NOT released)
- **Endpoints** (`app/api/v1/pf/departments.py`, prefix `/api/v1/org/departments`): `GET ""`, `GET /search`, `GET /export`, `GET /hierarchy`, `POST ""`, `GET /{id}`, `PUT /{id}`, `PATCH /{id}`, `PATCH /{id}/move`, `DELETE /{id}` — exactly `ELU-BFS-PF` §PF-006 §10 — **plus** `GET /{id}/history` (see the scope note below).
- **Authorization:** read = TENANT_ADMIN / SALES_MANAGER / PROJECT_MANAGER; write = TENANT_ADMIN; export = TENANT_ADMIN. FINANCE_USER and SUPPORT_AGENT hold no PF-006 grant; PLATFORM_ADMIN is denied by the PF-006 role gate.
- **Validation on record:** `core.department` 19 columns / 7 constraints / 6 indexes, RLS `true/true` with the single PF-003A `tenant_isolation` policy; 36 PF-006 tests and 35 PF-004/PF-005 regression tests collected; implementation validation run recorded **71 passed**; `git diff --check` clean; all changed Python files compile.

### Open items (NOT decided here)
- ~~‍**Human scope decision required — extra PF-006 history endpoint.**~~ **CLOSED — APPROVED 2026-09-15:** the endpoint is **HUMAN-APPROVED PF-006 SCOPE**, retained as an additional endpoint beyond the 10 in §10 (see the *HUMAN SCOPE DECISIONS RECORDED* section above). Not removed, not changed.
- ~~‍**Human clarification required — PF-006 scope items 1 vs 6.**~~ **CLOSED — APPROVED 2026-09-15:** the Human Project Owner approved the effective-parent-`NULL` interpretation (the stricter reading); see the section above.
- **PF-009 technical debt (recorded, unchanged):** the generic `app.core.rbac.has_permission` returns `True` for PLATFORM_ADMIN (universal bypass) while the PF-006 gate denies PLATFORM_ADMIN. The PF-006 permission matrix is deliberately unchanged and no technical-debt-register entry exists yet.
- **QA/environment note:** PF-006 test rows exist only in generated test tenants; no PF-006 rows exist in the main/reference tenants. Nothing was deleted, truncated or reset.
- **Missing governance records (reported, not invented):** `ELU-QA-REG-001` has **no PF-006 row**; there is **no `ELU-QA-PF006` release audit**, **no `ELU-REL-PF006` release notes** and **no PF-006 entry in `ELU-TST-PF`**.

### Not done (explicitly out of scope of this reconciliation)
- No release approval, no release certification, no tag, no commit, no push, no PR, no merge.
- No change to application code, schemas, API behaviour, database structure, migrations/DDL, tests, seed or the PF-006 permission matrix as part of the reconciliation.
- No Flutter UI, workflow/approval-engine integration, notifications, reports, PF-009 runtime permission grain or department address structures (all remain deferred).
- `users.department_id`, user↔department assignment and department-head FK/active-user validation remain **PF-008-owned**.
- **PF-005 Branch Management remains RELEASED and frozen** — `Phase-2-PF005` (object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495`) unchanged; no PF-005 functional behaviour changed.

## [PF-006] — 2026-09-15 — BATCH 4 DELIVERED (PERMISSION CATALOGUE / RBAC SEED / ACTOR MATRIX)

### Decision (human, recorded) — PF-006 organization-change policy ADOPTED
- **Adopted by:** Human Project Owner — **personal name not supplied in the authorising instruction** (recorded as PENDING; not invented — ELU-AI-001, no AI-originated approval).
- **Approver role:** Project Owner / Authorized Decision Maker. **Decision date:** 2026-09-15.
- **Adopted policy (transcribed from the authorising instruction — not originated by the assistant):**
  1. `organization_id` may be changed **only when the department is a root department and has no non-deleted children**.
  2. Organisation changes are **never cascaded**.
  3. Departments are **never silently reparented**.
  4. A single update **may** simultaneously set `parent_department_id = NULL` and change `organization_id`, provided there are no non-deleted children.
  5. **C-N11** (parent and child must belong to the same organisation) **remains mandatory**.
  6. If the current parent belongs to the old organisation and the request changes organisation **without detaching the parent**, the operation is **rejected**.
- **Implementation status (corrected 2026-09-15 — superseded by the Batch 3-C note below):** the policy is **adopted and recorded here**. Batch 4 itself did not modify the service (strict file scope); the service alignment was delivered separately by **PF-006 Batch 3-C**.
- **PF-006 Batch 3-C — Department Service aligned with the adopted policy (2026-09-15; `Backend/app/services/pf/department_service.py` only):**
  1. an organisation change is allowed **only when the effective `parent_department_id` after the request is `NULL`** — the effective parent is evaluated up front, so a detach requested in the same call is honoured and a retained parent is rejected (items 1 and 6);
  2. the department must have **no non-deleted children** (item 2);
  3. the change is **never cascaded** to children and **never silently reparents** anything (items 3 and 4);
  4. **one update may combine `parent_department_id = NULL` with an `organization_id` change** — accepted for PATCH and for PUT replacement — provided there are no non-deleted children (item 5);
  5. **C-N11** (parent and child in the same organisation) **remains enforced** (item 7);
  6. invalid, foreign-tenant or soft-deleted organisations keep the existing **404** behaviour, and tenant consistency, branch validation, soft delete, optimistic locking, audit events and hierarchy rules are unchanged (item 8). No new audit event was introduced and no DDL/schema change was required.
- **Specification question (recorded, not decided):** the adopted items 1 and 6 differ in scope (item 1 requires the department to *be* a root; item 6 rejects only a retained parent belonging to the *old* organisation). Batch 3-C implements the stricter, unambiguous reading required by the authorising instruction — effective parent `NULL` after the request.

### Batch 4 delivered (RBAC permission catalogue + seed only)
- **`Backend/app/db/seed.py`** — five `department.*` permissions added to the `PERMISSIONS` catalogue (`department.create`, `department.read`, `department.update`, `department.delete`, `department.export`; module `PF`), and the PF-006 actor matrix added as `DEPARTMENT_PERMISSION_MATRIX` + idempotent `_sync_department_permission_matrix` (HD-01 pattern, mirroring PF-004/PF-005), invoked from all three existing seed entry points (`seed_platform`, `_ensure_platform_admin`, `provision_tenant_roles`).
- **Naming note:** the requested action `department.view` is realised as **`department.read`** — the authoritative permission list (`ELU-BFS-PF` §PF-006 §12) and the established project convention (`organization.read`, `branch.read`) use `read`; no parallel `department.view` code was created.
- **Seeded actor matrix (`ELU-BFS-PF` §12):** TENANT_ADMIN `create/read/update/delete/export`; SALES_MANAGER `read`; PROJECT_MANAGER `read`; FINANCE_USER **no grant**; PLATFORM_ADMIN **no grant** (recorded as an explicit empty tuple so the seeded map matches the enforced PF-006 role gate — the generic platform seeding would otherwise leave the whole `department.*` catalogue granted to PLATFORM_ADMIN). Support Agent is not granted (appears in BFS §2 but not in the §12 matrix).
- **Not done (explicitly out of scope for Batch 4):** no service/ORM/schema change, no API router or endpoint, no Flutter, no PF-006 tests, no `users.department_id` or other PF-008 scope, no workflow/notifications/reports/CSV-XLSX/address structures/persisted level-path, no migration or DDL change, no commit/push/PR/merge/tag/release approval.
- **PF-005 Branch Management remains RELEASED and frozen** — no PF-005 permission or grant was removed or changed; the annotated tag `Phase-2-PF005` (object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495`) is unchanged.
- **Governance note (updated 2026-09-15):** PF-006 Batches 2, 3 and 3-C originally had no CHANGELOG entries — that gap is now closed by the **PF-006 governance reconciliation** section above (which also records Batch 5). Remaining governance gap: `ELU-QA-REG-001` carries **no PF-006 row** (QA-owned; to be created at the QA/release gate). This entry records **Batch 4 only**.

## [PF-006] — 2026-09-15 — IMPLEMENTATION AUTHORIZED — BATCH 1 DELIVERED (DDL + ROLLBACK + RLS)

### Decision (human, recorded)
- **PF-006 IMPLEMENTATION AUTHORIZED** — explicit human authorization for **PF-006 Department Management, Batch 1 only** (DDL, rollback, RLS enrolment and required bootstrap wiring).
- **Approved by:** Human Project Owner — **personal name not supplied in the authorising instruction** (recorded as PENDING; not invented — ELU-AI-001, no AI-originated approval).
- **Approver role:** Project Owner / Authorized Decision Maker.
- **Decision date:** 2026-09-15.
- **Authorized scope:** PF-006 Batch 1 only — DDL, rollback, RLS enrolment and required bootstrap wiring.
- Values were human-supplied and transcribed verbatim.

### Approved implementation decisions (C-N1…C-N6)
| Decision | Recorded outcome |
|---|---|
| **C-N1** `department_type` | **No CHECK constraint, no enum, no API value validation** — the supplied value is stored as-is; no business values invented (the approved specification names the field but defines **no** value list) |
| **C-N2** `level` / `path` | **No persisted columns**; hierarchy depth/path information is derived at read/query time; maximum depth = **5** remains the rule (`BR-PF-041`, service layer) |
| **C-N3** `status` | Allowed `ACTIVE`, `INACTIVE`, `ARCHIVED`; **default `ACTIVE`** (`ck_department_status`, per `ELU-BFS-PF-006` §5) |
| **C-N4** `department.export` | **Tenant Admin only** for this release — recorded as an **implementation decision** because the authoritative permission matrix (`ELU-BFS-PF` §12) carries no export column |
| **C-N5** Specification-silent fields | `description` `VARCHAR(500)` NULL; `cost_centre_code` `VARCHAR(32)` NULL |
| **C-N6** Address | **No** `department_address` table, **no** `address_id`, no department-specific address structure |

### Batch 1 delivered (database only)
- **New** `Database/03_PlatformFoundation/015_department_pf006.sql` — `core.department` (idempotent): 19 columns, PK `department_pkey`, checks `ck_department_status` and `ck_department_no_self_parent` (self-parenting rejected), FKs `fk_department_tenant` (no action), `fk_department_organization` (**RESTRICT**), `fk_department_parent` (**RESTRICT**, self-FK), `fk_department_branch` (**ON DELETE SET NULL** — C-N3/§8), partial UK `uk_department_tenant_code_active (tenant_id, department_code) WHERE is_deleted = FALSE` (`BR-PF-040`), and partial indexes `idx_department_tenant_status`, `idx_department_organization`, `idx_department_parent`, `idx_department_branch`.
- **New** `Database/03_PlatformFoundation/015_department_pf006_rollback.sql` — reverse-order rollback (indexes → constraints → table last); no PF-003A/PF-005 object touched.
- **RLS enrolment (ADR-015 / PF-003A):** `core.department` added to `Database/03_PlatformFoundation/012_rls_pf003a.sql` and to `Backend/app/db/migrate_pf003a.py::RLS_TABLES` (now 18 entries); **ENABLE + FORCE** RLS with the existing `tenant_isolation` policy (USING/WITH CHECK on `app.tenant_id` / `app.platform_context`). No second RLS mechanism; no existing isolation changed.
- **Bootstrap wiring:** new `Backend/app/db/migrate_pf006.py` (`apply_pf006_ddl`, mirrors `migrate_pf005.py`) registered in `Backend/app/main.py` lifespan.
- **Validated:** columns/constraints/indexes confirmed; `rls=true`, `forced=true`; `tenant_isolation` policy present; **idempotent re-apply** leaves constraint count at 7 and RLS at true/true; `import app.main` valid; no previously-RLS-enabled table lost RLS.

### Deferred / non-demonstrable (recorded)
- `users.department_id` and the `department → users` linkage (**BFS §7/§8**) → **PF-008 Users & Identity** — not implemented in PF-006.
- **BR-PF-043** (department head must be an ACTIVE user in the same tenant) → **DEFERRED to PF-008**; `department_head_user_id` is a plain nullable UUID with **no FK and no validation** → **non-demonstrable in PF-006**.
- **AC-PF-006-04** (approval workflow routing to the department head) → **DEFERRED / NON-DEMONSTRABLE** pending CPS-001.
- `NTF-PF-006-01..03` notifications and `RPT-PF-006-01/02` reports → deferred; CSV/XLSX export deferred (JSON only, later batch); Flutter UI (BFS §11 screens) excluded from the first release.
- **Edition gating → none** (`ELU-EDM-001`: Multi-Department available in Community, Professional and Enterprise).
- **Open specification gap recorded (not invented):** `department_type` has no value list anywhere in the approved specification — the column therefore carries **no** CHECK/enum and no value validation (C-N1).

### Not done (explicitly out of scope for Batch 1)
- No ORM model, Pydantic schemas, repository/service, router/API, RBAC seeding or `department.*` permissions, tests, PF-005 guard update, frontend, QA audit, release approval, release certification or tag.
- **PF-005 Branch Management remains RELEASED and frozen** — annotated tag `Phase-2-PF005` (object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495`) **unchanged**; no PF-005 file modified.
- Not committed, not pushed, no PR — Batch 1 is a working-tree change awaiting review/approval before Batch 2.

## [PF-006] — 2026-09-15 — START AUTHORIZATION RECORD PREPARED (GOVERNANCE ONLY — NOT AUTHORIZED)

> **This entry is NOT an authorization.** It records that the **PF-006 START AUTHORIZATION** documentation has been **prepared and is awaiting explicit human authorization**. No PF-006 decision has been taken and no PF-006 implementation exists. The assistant originated nothing (ELU-AI-001 — no AI-originated approval).

### Module (per approved specifications — unchanged)
- **PF-006 — Department Management** · sub-module **PF-006-001 Department Structure** · feature **PF-006-001-001 Department Profile** (authoritative specification `ELU-BFS-PF` §PF-006, Document ID `ELU-BFS-PF-006`; corroborated by `ELU-EFS-001`, `EFS-PF`, `ELU-RTM-001` / `V1-PF-CRM` REQ-PF-014 / REQ-PF-015).
- **Not to be confused with PF-005:** *Branch Structure* is sub-module **PF-005-001** and *Branch Hierarchy* is a **PF-005** capability (`GET /api/v1/org/branches/hierarchy`). PF-005 Branch Management is **RELEASED (2026-09-14)** and frozen; PF-006 Department Management is a separate module that has not started.

### Authorization fields (PENDING — human input required; nothing invented)
- **Decision:** PENDING — HUMAN AUTHORIZATION REQUIRED (no `PF-006 START AUTHORIZED` record exists; none is created here).
- **Approver:** PENDING — HUMAN DECISION REQUIRED.
- **Role:** PENDING — HUMAN DECISION REQUIRED.
- **Authorization date:** PENDING — HUMAN DECISION REQUIRED.
- These values must be human-supplied and transcribed verbatim; the assistant must not originate the decision, the identity, the role or the date (ELU-AI-001).

### Status recorded (existing facts only — no status change implied)
- **Implementation status: NOT STARTED (0%).** No `department` table in any schema; no RLS enrolment and no rollback DDL; no `department.*` permissions; no backend model / schema / service / router; no Flutter screen / route / service; no PF-006 tests.
- **Governance status:** `ELU-MSL-001` §3.1 lists `PF-006…011 — Not Started` and §3.3 shows `PF-006 Department … 0%`; **no PF-006 row exists in `ELU-QA-REG-001`**; `ELU-RTM-001` has no PF-006 implementation section; `ELU-TST-PF` has no PF-006 test cases.
- Requirements and specification coverage already exists and is Approved (BFS, EFS, EDM, DDD, ERD, API, UI). This entry changes none of those documents.

### Pending scope decisions (NOT decided and NOT approved by this entry)
- `NTF-PF-006-01..03` notifications — scope undecided.
- `RPT-PF-006-01/02` reports — scope undecided.
- `AC-PF-006-04` approval-workflow dependency (CPS-001 workflow engine) — undecided.
- `users.department_id` — **PF-008 Users & Identity dependency** — undecided.
- `department.branch_id` linkage (Set Null) — undecided.
- Department-head linkage (`department_head_user_id`, BR-PF-043) — undecided.
- Edition gating (`ELU-EDM-001` / BFS show Multi-Department in Community, Professional and Enterprise; whether a `DEPARTMENT` feature or limit is required) — undecided.
- DDL numbering and placement (`Database/03_PlatformFoundation/015_department_pf006.sql` plus rollback; RLS loop update) — undecided.
- PF-005 scope-guard update (`Backend/tests/test_pf005_branches.py::test_deferred_scope_not_implemented` asserts `core.department` absence) — undecided.
- Flutter UI scope (following the PF-005 "Batch 3 excluded" precedent) — undecided.

### Changed (documentation only)
- `ELU-MSL-001` — version-history row **1.20** added (PF-006 authorization record prepared; PENDING fields). The §3.1 PF-006 row and the §3.3 dashboard are **deliberately unchanged** (status remains Not Started / 0% — no authorization exists).
- `ELU-MSL-002` — "Next jobs" P1 row added (PF-006 authorization pending) and change-log **4.84** added.
- `Documentation/CHANGELOG.md` — this entry.

### Not done / explicitly out of scope
- **No PF-006 implementation of any kind** — no DDL/SQL, no migration or seed, no backend code, no frontend code, no tests.
- No `PF-006 START AUTHORIZED` record; no QA audit; no release notes; no release approval; no tag.
- **PF-005 protection:** `Phase-2-PF005` — tag object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495` — **unchanged**. PF-005 Branch Management remains RELEASED and frozen; no PF-005 file, DDL, code, test or documentation was modified.
- No commit, no push, no PR, no branch change: this preparation is an uncommitted working-tree change awaiting human authorization.

## [Option B — PostgreSQL Host Port Infrastructure] — 2026-09-15 — MERGED (PR #21)

### Change (infrastructure only — NOT part of any module release)
- **Option B — PostgreSQL host port infrastructure change.** Host-published PostgreSQL port moved **55432 → 15432**; Compose API database URLs pinned to the Compose service (`postgres:5432`). Exactly **five** approved files: `.env.example`, `README.md`, `docker-compose.yml`, `Scripts/start-api-host.bat`, `Scripts/start-infra.bat`. No PF-005 functional, Backend, Frontend, Database or Documentation file was part of Option B.
- **Feature commit:** `713f8021bc2b238d151722276e8eafe193593f34` — `chore(infra): move PostgreSQL host port to 15432`.
- **PR:** **#21** · **Merge commit:** `44f9906f6f105adfb49eeb2ba7da905e8890ae9a` (normal merge into `master`) · merged **2026-09-15** · `master` = `origin/master` = `44f9906…`.
- **No release tag** was created for Option B — infrastructure changes are not release-tagged (consistent with prior practice: the 2026-09-10 Flutter dependency pin and the FIN v4.13 / PR #6 merge were recorded without tags).
- **PF-005 remains separate and unchanged:** annotated tag `Phase-2-PF005` (object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495`) is untouched. The PF-005 release predates the Option B merge (`bdc188c8…` is an ancestor of `44f9906…`), so the released PF-005 tree correctly does not contain Option B.

### Runtime verification (completed 2026-09-15)
- PostgreSQL host mapping **`0.0.0.0:15432 -> 5432/tcp`**; container internal port **5432**; database **elinkup**; `SELECT 1` succeeded; **`core.tenant` = 666** (unchanged).
- Host API started from the **merged configuration with no overrides**; effective host DSN resolved to **`…@localhost:15432/elinkup`**; `GET /health` → **200**; `GET /openapi.json` → **200**; PF-005 GET routes → **401** (authentication required — not a defect).
- Containerised API: **not startup-verified** — the pre-existing PF-003A SQL/mount defect remains (see below).

### Changed (documentation only)
- `ELU-MSL-001` — history row **1.19** added.
- `ELU-MSL-002` — change log **4.83** added.

### Superseded wording (historical entries retained)
- The PF-005 entries below (RELEASED 2026-09-14 and RELEASE APPROVED 2026-09-14) state that Option B infrastructure "remains **excluded and uncommitted**" and that its "disposition — uncommitted; requires its own authorisation". Those statements described the **pre-merge state at that time** and are now superseded: authorisation was subsequently granted, Option B was implemented in `713f802`, merged via PR #21 as `44f9906`, and **no release tag** was created.

### Known limitations / pre-existing issues (NOT fixed by Option B)
- Docker API container startup defect: `FileNotFoundError: '/Database/03_PlatformFoundation/012_rls_pf003a.sql'` (the Compose `api` service mounts only `./Backend:/app`) — pre-existing, outside Option B scope.
- `Backend/app/core/config.py` still defaults to `localhost:55432` (latent only; overridden by environment/dotenv).
- `elinkup-redis` container not running.
- Authentication smoke test **not performed** — `AuthService.login` writes `users.last_login`.

## [PF-005] — 2026-09-14 — RELEASED (ANNOTATED TAG `Phase-2-PF005` CREATED AND PUSHED)

### Release event (human-authorised tag operation)
- **PF-005 is RELEASED.** Annotated tag **`Phase-2-PF005`** created and pushed **2026-09-14**.
- **Tag object SHA:** `8f0502ce507da62de25f8105c06ac3185da83c97` · **type:** annotated (`git cat-file -t` → `tag`).
- **Tag target (peeled commit):** `bdc188c8ff1c89c3e0578830ef73c9934536b495` — the PF-005 governance merge commit ("Merge pull request #18 from Avijr2022/cursor/pf005-release-approved"); `master` = `origin/master` at tag time.
- **Content / implementation baseline (unchanged):** `219bb6c8b026797fef56e3c3a46f6a17c0218787` — **not** tagged; no dedicated no-change baseline commit.
- **Human approval (pre-existing):** `PF-005 RELEASE APPROVED: YES` (2026-09-14). Tag creation was a separate authorised step.
- **Scope:** backend functional layer only. **Excluded:** Flutter UI (Batch 3), `NTF-PF-005-*`, `RPT-PF-005-*`. **`AC-PF-005-02` / `AC-PF-005-04` remain NON-DEMONSTRABLE.**
- **Option B infrastructure** (`.env.example`, `README.md`, `docker-compose.yml`, `Scripts/start-api-host.bat`, `Scripts/start-infra.bat`) remains **excluded and uncommitted** at the time of this entry. **Superseded 2026-09-15:** authorisation was subsequently granted, Option B was implemented in `713f802` and merged via PR #21 as `44f9906`; **no release tag** was created — see the Option B entry above.
- No tag was recreated, moved, deleted or force-updated; no additional tag was created; no history was rewritten.

### Changed (documentation only — post-tag reconciliation)
- `ELU-REL-PF005` — status `RELEASED`; tag object, target commit and created/pushed date recorded; tag-creation checklist items closed.
- `ELU-QA-REG-001` v1.8 → **v1.9** — PF-005 `Release Tag` finalised: `Phase-2-PF005` (annotated), tag object `8f0502ce…` → target `bdc188c8…`, created/pushed 2026-09-14 (`Locked = Yes` retained).
- `ELU-MSL-001` — history **1.18** added; §3 PF-005 row → **RELEASED**; §3.1 row, §3.2 baselines line and health, §3.3 dashboard updated.
- `ELU-MSL-002` — P1 job 12 closed; change log **4.82** added.

### Still outstanding (not part of this reconciliation)
- Option B infrastructure disposition — uncommitted and requiring its own authorisation **at the time of this entry**. **Superseded 2026-09-15:** authorised, committed (`713f802`) and merged (PR #21 / `44f9906`) — see the Option B entry above.
- Flutter UI (Batch 3) release decision.
- Approver name/role and independent reviewer identity remain recorded as PENDING (nothing fabricated).
- Pre-existing advisories, unchanged and NOT fixed by PF-005: Docker `/Database` mount defect; `Backend/app/core/config.py` `localhost:55432` fallback; Redis container not running.

## [PF-005] — 2026-09-14 — RELEASE APPROVED (ANNOTATED TAG `Phase-2-PF005` NOT YET CREATED)

> **Superseded 2026-09-14:** the annotated tag was subsequently created and pushed — see the RELEASED entry above. The wording below is retained as the historical record of the approval step.

### Decision (human, recorded)
- **`PF-005 RELEASE APPROVED: YES`** — explicit human release approval for **PF-005 Branch Management, backend functional layer only** (2026-09-14).
- **Content / implementation baseline:** `219bb6c8b026797fef56e3c3a46f6a17c0218787`.
- **Final release-tag target:** the **PF-005 governance merge commit created by this change set** — SHA **pending**; **no dedicated no-change baseline commit** (the PF-004 dedicated-baseline-commit pattern is not applied).
- **Proposed annotated tag `Phase-2-PF005`: NOT YET CREATED and NOT PUSHED at the time of this entry** — no tag object SHA existed then; tag creation was a separate authorised step. **Superseded 2026-09-14: the tag was subsequently created and pushed (tag object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495`) — see the RELEASED entry above.**
- **Scope:** backend functional layer only. **Excluded:** Flutter UI (Batch 3), `NTF-PF-005-*`, `RPT-PF-005-*`.
- **`AC-PF-005-02` and `AC-PF-005-04` remain NON-DEMONSTRABLE** at this baseline — release approval does not convert them to verified.
- **Approver:** PENDING — name/role not recorded in the authorising instruction; the decision string is transcribed verbatim (ELU-AI-001 — no AI-originated approval).
- **Option B infrastructure** (`.env.example`, `README.md`, `docker-compose.yml`, `Scripts/start-api-host.bat`, `Scripts/start-infra.bat`) remains **excluded from PF-005** and was uncommitted at the time of this entry. **Superseded 2026-09-15:** subsequently authorised, committed (`713f802`) and merged (PR #21 / `44f9906`); Option B remained excluded from PF-005.

### Changed (documentation only)
- `ELU-QA-PF005` v0.1 draft → **v1.0** (`PASS — RELEASE APPROVED`; reviewer identity PENDING).
- `ELU-REL-PF005` — release notes finalised: approval recorded, tag line `APPROVED, NOT YET CREATED`, checkout updated.
- `ELU-QA-REG-001` v1.7 → **v1.8** — PF-005 row: audit doc `ELU-QA-PF005 v1.0`, verdict **RELEASE APPROVED**, Release Tag `Phase-2-PF005` (approved, not yet created), Locked **Yes** (recorded at approval, per the PF-004 precedent).
- `ELU-MSL-001` — history row **1.17** added; §3 PF-005 row; §3.1 PF-005 row → **RELEASE APPROVED**; §3.2 baselines line; §3.3 dashboard.
- `ELU-MSL-002` — P1 job 11 updated; new P1 job 12 (tag step); change log **4.81**.

### Not done / NOT tag-created (requires separate authorisation)
- Annotated tag `Phase-2-PF005` — **not created, not pushed at the time of this entry**. **Superseded 2026-09-14:** created and pushed — see the RELEASED entry above.
- Post-tag reconciliation (tag object SHA, peeled commit, created/pushed date; register Release Tag finalisation) — **was pending**; **completed 2026-09-14** — see the RELEASED entry above.
- Flutter UI (Batch 3) — outstanding.
- **Pre-existing advisories, unchanged and NOT fixed by PF-005:** Docker `/Database` mount defect; `Backend/app/core/config.py` `localhost:55432` fallback; Redis container not running.

## [PF-005] — 2026-09-12 — IMPLEMENTED (BACKEND FUNCTIONAL LAYER) — NOT RELEASED

### Decision (human, recorded)
- **PF-005 Branch Management — START AUTHORIZED**; approver **Avijit**, role **Project Coordinator**, date **2026-09-12**.
- **AC-PF-005-04 / BR-PF-038** user branch assignment (`user.branch_id`; branch head must be an ACTIVE user in the same tenant) → **DEFERRED** to **PF-008 Users & Identity**.
- **NTF-PF-005-01..03** notifications → **DEFERRED**.
- **RPT-PF-005-01/02** reports → **DEFERRED**.
- Values were human-supplied and transcribed verbatim; the assistant originated nothing (ELU-AI-001). This is a **start authorisation / scope decision**, not a QA sign-off or release approval.

### Implementation (delivered — NOT released)

1. **Start authorization / governance — 2026-09-12.** Human start authorisation recorded (approver **Avijit / Project Coordinator**) with the scope decisions above. Governance records only — no code at that point. **Not a release, QA-approval or sign-off event.**
2. **Batch 1 — groundwork (docs + DDL + RLS + ORM + seed).** `Database/03_PlatformFoundation/014_branch_pf005.sql` (+ `_rollback.sql`) creating `core.branch` / `core.branch_address` idempotently (organization FK RESTRICT, nullable parent self-FK RESTRICT, `branch_head_user_id` nullable with **no FK**, `branch_address` → branch CASCADE, branch → address SET NULL, partial UK `uk_branch_tenant_code_active`, `ck_branch_status`, `ck_branch_type`, partial indexes); `Backend/app/db/migrate_pf005.py`; RLS **enable + force** for both tables (ADR-015 loop in `012_rls_pf003a.sql` / `migrate_pf003a.py::RLS_TABLES`); `Branch` / `BranchAddress` ORM models; seed `branch.create/read/update/delete/export` + `BRANCH_PERMISSION_MATRIX` + `MAX_BRANCHES` (Professional 10 / Enterprise 999999); `BRANCH` edition feature already present. **Implementation only — no API, service or UI.**
3. **Batch 2 — backend functional layer, delivered to `master` at `4430f9d2b9eedc51dede1ca1cf6183508a756dac`.** `app/schemas/pf/branch.py`, `app/services/pf/branch_service.py`, `app/api/v1/pf/branches.py` (+ router registration), `app/core/edition_gating.py` (`BRANCH` constant), `app/models/pf/__init__.py` exports, `Backend/tests/test_pf005_branches.py`, `TC-PF-ISO-05`. Scope: branch CRUD / PUT / PATCH / soft delete; lifecycle transitions (BFS-PF-005 §5); hierarchy + cycle protection; address 1:1 upsert; search; JSON export; **BR-PF-034** edition gate (Community → 403); **BR-PF-039** `MAX_BRANCHES` enforced on create (counts **non-deleted** branches, retained `ARCHIVED`/`CANCELLED` rows included); **BR-PF-036** advisory HEAD_OFFICE warning (non-blocking); role gates; audit events; exactly the 9 approved endpoints (**hierarchy = `GET /api/v1/org/branches/hierarchy`**); branch history is **service-only** (no API endpoint). **Verified:** PF-005 tests **15 passed**; tenant isolation **13 passed**; full backend suite **141 passed, 1 skipped**; no PF-001…PF-004 regression. **Implementation only — NOT a release.**

### Changed (documentation only)
- `ELU-MSL-001` — history row **1.15** added; §3.1 module row PF-005 → **START AUTHORIZED — IN PROGRESS** (PF-006…011 remain Not Started); §3.2 one-line health and §3.3 dashboard updated.
- `ELU-MSL-002` — P1 next-job added (PF-005 start; documentation/DDL groundwork first); change-log **4.78** added.
- `ELU-QA-REG-001` v1.5 → **v1.6** — PF-005 row added: `START AUTHORIZED — IN PROGRESS`, no audit, no tag.
- `ELU-PGR-001` — **§16 PF-005 Start Authorization — 2026-09-12** added (scope-decision table).
- `ELU-RDM-001` — PF-005 roadmap row notes the authorisation and deferrals.
- Later status reconciliations (documentation only): `ELU-RTM-001` §11, `ELU-API-PF` §4, `ELU-TST-PF` **v1.4**, `ELU-QA-REG-001` **v1.7**, `ELU-MSL-001` history **1.16** + §3.1/§3.2/§3.3, `ELU-MSL-002` **4.80** — PF-005 status recorded as **IMPLEMENTED — NOT RELEASED**; `ELU-RDM-001` roadmap row reconciled in this change.

### Not done / NOT released
- **Status: IMPLEMENTED — NOT RELEASED.** No QA release audit, **no release approval**, **no phase-gate approval for PF-005**, **no human sign-off**, **no release baseline**.
- **No release tag** created, moved, or modified; PF-005 has **no tag**, and no tag points at `4430f9d` or `56f201e8`.
- **Not implemented (deferred by approved decision):** Flutter/UI screens (**Batch 3 — UI release scope remains a governance decision**); **NTF-PF-005-\*** notifications; **RPT-PF-005-\*** reports; branch-head assignment + `users.branch_id` (**→ PF-008**); department linkage (**→ PF-006**); **BR-PF-037** project→branch enforcement; runtime permission-grain enforcement (**→ PF-009**); branch history API (service-only).

## [Phase Gate PF-001…003] — 2026-09-12 — GATE APPROVED — OPTION (c) UNCONDITIONAL

### Decision (human, recorded)
- **Reference:** `ELU-PGR-001` v1.2 §15.1 — sign-off block completed by the named human approver.
- `DECISION: APPROVED` · `OPTION: (c) unconditional` · `APPROVER: Avijit` · `ROLE: Project Coordinator` · `DATE: 2026-09-12` · `CONDITIONS: None`.
- **Retrospective deviation: Accepted** — PF-004 Organization Management was delivered, corrected, human release-approved (2026-09-11) and release-tagged (`Phase-2-PF004-R1`) before the gate block was completed, notwithstanding the §0/§14 directive *"Do not start PF-004 until Human Phase-Gate Approval"*. No remediation required.
- Values were **human-supplied** and transcribed verbatim; the assistant did not originate the decision, option, approver identity, role, or date (ELU-AI-001).

### Changed (documentation only)
- `ELU-PGR-001` v1.1 → **v1.2**; status `AWAITING HUMAN PHASE-GATE APPROVAL` → **`APPROVED`**; §14 request marked *Resolved*; §15.1 block completed; decision provenance + retrospective-deviation record added.
- `ELU-QA-REG-001` v1.4 → **v1.5**; phase-gate row → **APPROVED** (option (c), 2026-09-12); stale trailing cell corrected to PF-004 `RELEASE APPROVED` — tag `Phase-2-PF004-R1`.
- `ELU-MSL-001` — history row **1.14** added; §3 PF-004 row, §3.1 PF-004 release tag (`Phase-2-PF004-R1`), §3.2 baselines line updated.
- `ELU-MSL-002` — P1 next-jobs 1 & 2 closed; change-log **4.77** added.

### Not done (requires separate authorisation)
- Gate tag **`Phase-Gate-PF001-003`** — **not created**.
- **PF-005 Branch Management** — not started; no PF-005 start instruction issued.

## [PF-004] — 2026-09-11 — APPROVED CORRECTIONS IMPLEMENTED (NOT RELEASED)

### Changed (IMPLEMENTED)
- **HD-01** Seeded `organization.*` grants corrected to the BFS-PF-004 §12 matrix via `ORG_PERMISSION_MATRIX` + `_sync_org_permission_matrix()` in `Backend/app/db/seed.py` (applied in all three tenant role-provisioning paths); Tenant Admin all 5, Finance User read+export, Sales Manager read, Platform Admin read, Project Manager none. Runtime grain enforcement remains deferred to PF-009.
- **HD-02** `GET /api/v1/org/organizations/export` now gated by `require_org_export()` — Tenant Admin + Finance User only (403 for Platform Admin, Sales Manager, Project Manager).
- **HD-03** Export masks GSTIN/PAN using the existing audit convention (`***`); stored database values are untouched.
- **HD-11** Organization navigation and route are Tenant-Admin-only (`CrmRbac.canManageOrganizations`, nav item + router `redirect` guard); `ELU-UI-PF` route row aligned to `/organizations` / `OrganizationsPage`.

### Deferred (recorded)
- **HD-05** AC-PF-004-04 / BR-PF-032 PDF organization-name propagation → Document Engine
- **HD-06 / HD-07** RPT-PF-004-01/02 out of PF-004 v1.0; RPT-PF-004-03/04 undefined and not implemented
- **HD-08** NTF-PF-004-01..03 → CPS-003
- **HD-04** JSON export retained (no CSV/XLSX)
- Platform-wide: PF-009 runtime permission-grain enforcement; Alembic baseline

### Verification
- `pytest tests/test_pf004_org_export.py` → 7 passed; with `test_pf004_organizations.py` → 20 passed
- `flutter analyze` → no issues; `flutter test test/organization_nav_test.dart` → 6 passed

### Notes
- **Status reconciled (HD-09, 2026-09-11):** PF-004 records now read **QA PASS — PENDING HUMAN RELEASE APPROVAL**; corrections merged to `master` via PR #7 (merge commit `67b48c1`). **HUMAN APPROVAL REQUIRED:** PF-004 release decision (ELU-QA-PF004 §5 blank) and the PF-001…003 phase gate (ELU-PGR-001 §15.1 blank). PF-004 is NOT released.
- **HD-10** `Phase-2-PF004` tag left unchanged pending human decision.

---
## [PF-004 Mid-Phase] — 2026-08-06 — REVIEW COMPLETE

### Added
- ELU-MPR-PF004 Mid-Phase Architecture & Quality Review (CONDITIONAL PASS, grade B+)
- ELU-EHC-003 Executive Health Card; ELU-GAP-PF004; ELU-TD-003
- Risk RSK-024 / RSK-025; PF-004 corrections (soft UK, Tenant Admin write, sort, UI a11y)

### Notes
- **No QA Release Audit** yet — close High gaps first
- Baselined PF-001…PF-003A untouched

---

## [PF-004] — 2026-08-06 — IN PROGRESS

### Added
- PF-004 Organization Management (BFS-PF-004): org profile fields, ROOT UK, GSTIN/PAN validation, hierarchy API, Flutter Organizations tab
- SQL: `013_organization_pf004.sql` / `migrate_pf004.py`
- Tests: `tests/test_pf004_organizations.py` (AC-PF-004-01…03)

### Notes
- Started after **Phase-2-PF003A** RELEASE APPROVED
- PF-001…PF-003A remain frozen

---

## [Phase-2-PF003A] — 2026-08-06 — RELEASE APPROVED

### Added
- PF-003A Enterprise Tenant Isolation (ADR-015 / ADR-016): PostgreSQL FORCE RLS, `elu_app` role, session GUCs (`app.tenant_id`, `app.platform_context`)
- Isolation pytest pack (`tests/isolation/`) — TC-PF-ISO-01…04 + SQL / JWT spoof
- Docs: ELU-QA-PF003A, ELU-REL-PF003A, ELU-EHC-002 Security Health Card, ADR-016, SEC/RTM/TST updates

### Notes
- Git tag: `Phase-2-PF003A`
- **PF-001 / PF-002 / PF-003 / PF-003A** frozen — change only on bug, approved CR, or ADR
- TD-CRIT-01 / TD-CRIT-02 closed; RSK-021 Closed
- Next: **PF-004 Organization Management** (human-approved start)

---

## [Phase Gate] — 2026-08-06 — CONDITION CLOSED (PF-003A RELEASE APPROVED)

### Added
- ELU-PGR-001 Phase Gate Review (PF-001…003)
- ELU-TD-002 Technical Debt Register (Critical RLS / isolation)
- ELU-EHC-001 Enterprise Health Card v2.0
- ELU-MSL-001 §3.3 Progress Dashboard
- Risk updates RSK-021…023

### Notes
- Phase Gate architectural condition closed by PF-003A baseline
- P0 RLS + isolation tests delivered and RELEASE APPROVED

---

## [Phase-2-PF003] — 2026-08-06 — RELEASE APPROVED

### Added
- PF-003 Subscription Management (BFS-PF-003): APIs, history/usage tables, Flutter Subscriptions UI, pytest suite
- Expire cascade to tenant SUSPENDED (BR-PF-024); cancel cascade to OFFBOARDING
- DB: `uk_subscription_one_current`, `fk_tenant_current_subscription`, seat CHECK, NOT NULL commercial columns
- Flutter: Create / Edit / History / My Subscription (responsive)
- Release audit: ELU-QA-PF003 **v2.1 PASS — RELEASE APPROVED**

### Notes
- Git tag: `Phase-2-PF003`
- PF-001 / PF-002 / PF-003 frozen — change only on bug, approved CR, or ADR
- Execution under Enterprise Engineering Constitution (CON)
- Next module requires explicit human start + GAP analysis

---

## [Phase-2-PF002] — 2026-08-06 — RELEASE APPROVED

### Added
- PF-002 Tenant Management (BFS-PF-002): platform tenant APIs, child tables, Flutter Tenants UI, audit, pytest suite
- Auth: BR-PF-014 suspended-tenant login/refresh block; case-insensitive tenant code lookup
- Release audit: ELU-QA-PF002 v1.1 PASS — RELEASE APPROVED

### Notes
- Git tag: `Phase-2-PF002`
- PF-002 frozen — change only on defect or approved CR
- Next module: PF-003 Subscription Management

---

## [Phase-2-PF001] — 2026-08-06 — RELEASE APPROVED

### Added
- PF-001 Edition Management (BFS-PF-001): APIs, DDD schema, Flutter Editions UI, audit events, pytest suite
- Governance baseline artefacts referenced by Constitution (CON / AI / GOV-VAL) from prior docs wave
- Release audit: ELU-QA-PF001 v2.0 PASS

### Fixed
- Edition physical columns aligned to ELU-DDD-PF (`id`/`code`/`name`)
- Repeatable edition tests (unique codes)
- Status CHECK + `idx_edition_status`

### Notes
- Git tag: `Phase-2-PF001`
- Next module: PF-002 Tenant Management (separate release)

---

## [Pre-Phase-2] — 2026-08

- CRM Lead / Opportunity vertical slices
- Local FastAPI + Flutter + Docker scaffold
## PF-007 Release Governance Record

- PF-007 RELEASE APPROVED: YES
- Release tag: `Phase-2-PF007`
- Release commit: `80ae94e1dd071f62198571a7592cf81246ee591e`
- Annotated tag object: `bde87e9ee31d2f4c9a25ffdd7169cc9f90607a68`
