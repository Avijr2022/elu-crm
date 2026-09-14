# Release Notes — PF-005 Branch Management

**Document ID:** ELU-REL-PF005
**Release:** Phase-2-PF005
**Status:** **RELEASE APPROVED — ANNOTATED TAG `Phase-2-PF005` NOT YET CREATED**
**Date:** 2026-09-14 (release approval recorded)
**Human approval:** **`PF-005 RELEASE APPROVED: YES`** (2026-09-14; approver name/role pending record)
**Git tag:** `Phase-2-PF005` (annotated) — **APPROVED, NOT YET CREATED**; no tag object SHA exists and no push has been performed. Final tag target = the PF-005 governance merge commit (SHA pending)
**Prior baselines:** Phase-2-PF001 … Phase-2-PF003A, Phase-2-PF004-R1
**QA:** ELU-QA-PF005 v1.0 — **PASS — RELEASE APPROVED** (2026-09-14)

---

## Release baseline

| Item | Value |
|------|-------|
| Content / implementation baseline | `219bb6c8b026797fef56e3c3a46f6a17c0218787` (declared content baseline; **not** the tag target) |
| Commit identity | Merge commit — "Merge pull request #17 from Avijr2022/cursor/pf005-doc-status-reconciliation" |
| Branch state | `master` = `origin/master` = `219bb6c8b026797fef56e3c3a46f6a17c0218787` |
| Final release-tag target | **The PF-005 governance merge commit created by this approval change set — SHA PENDING** (no dedicated no-change baseline commit) |
| Human release approval | **`PF-005 RELEASE APPROVED: YES`** — 2026-09-14; approver name/role **PENDING** (human-supplied decision transcribed verbatim; ELU-AI-001) |
| Proposed tag | `Phase-2-PF005` — **annotated** — **APPROVED, NOT YET CREATED** (no tag object, no push) |
| Tag existence check | No tag points at `219bb6c`, `4430f9d` or `56f201e` (verified 2026-09-14) |
| Prior tag precedent | PF-004 release tag `Phase-2-PF004-R1` targets a dedicated no-change baseline commit (`3f30159a…`); recorded here for information only — the baseline for this release is the commit designated above. **Confirmed 2026-09-14: the existing `master`/`origin/master` commit is the release baseline; no dedicated no-change baseline commit will be created and the baseline SHA must not be altered.** |

## Implementation commits

| SHA | Message | Content |
|-----|---------|---------|
| `a8c2e06` | `feat(pf): PF-005 branch management groundwork` (merged via PR #15, merge commit `88fc636`) | Batch 1 — specification, DDL `Database/03_PlatformFoundation/014_branch_pf005.sql` (+ `014_branch_pf005_rollback.sql`), RLS loop `012_rls_pf003a.sql` + `migrate_pf003a.py::RLS_TABLES`, ORM `app/models/pf/entities.py` (`Branch`, `BranchAddress`), seed `BRANCH_PERMISSION_MATRIX` / `branch.*` permissions / `MAX_BRANCHES` limits |
| `4430f9d` | `feat(pf): implement PF-005 branch management` | Batch 2 — `app/schemas/pf/branch.py`, `app/services/pf/branch_service.py`, `app/api/v1/pf/branches.py`, router registration, `app/core/edition_gating.py` (`BRANCH`), `app/models/pf/__init__.py`, `tests/test_pf005_branches.py`, `tests/isolation/test_tenant_isolation.py` (`TC-PF-ISO-05`) — 8 files, +2230 / −1 |

Both commits are verified ancestors of the baseline commit and of `master` (verified 2026-09-14).

## Documentation reconciliation merges

| Merge | PR | Content |
|-------|----|---------|
| `56f201e` | #16 (branch `ff22425`) | 6 documentation files, +45 / −34 — `10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md` (§11 implementation traceability), `11-Engineering/ELU-API-PF.md` (§4), `11-Engineering/ELU-TST-PF.md` (v1.4), `ELU-MSL-001-Milestone-Tracker.md`, `ELU-MSL-002-CRM-Build-Tracker.md`, `ELU-QA-REG-001-QA-Register.md` |
| `219bb6c` | #17 (branch `ec29b22`) | 2 files, +13 / −5 — `Documentation/CHANGELOG.md`, `Documentation/ELU-RDM-001-Product-Roadmap.md` |

## Release scope — PF-005 backend functional layer only

**In scope (backend):**

- Schema: `core.branch`, `core.branch_address` (`014_branch_pf005.sql`, idempotent, + rollback SQL)
- RLS: `core.branch`, `core.branch_address` under the PF-003A FORCE RLS regime (ADR-015)
- ORM: `Branch`, `BranchAddress`
- Seed: `branch.*` permissions, `BRANCH_PERMISSION_MATRIX`, `MAX_BRANCHES` limits
- API: **9 endpoints** under `/api/v1/org/branches` — create, list, detail, PUT, PATCH, soft delete, search, export, hierarchy
- Behaviour: edition gate (`BRANCH` feature, Professional+), active-code uniqueness, HEAD_OFFICE advisory warning (non-blocking), parent/child hierarchy with cycle and self-parent rejection, address 1:1, lifecycle transitions (`DRAFT→{ACTIVE,CANCELLED}`, `ACTIVE→INACTIVE`, `INACTIVE→{ACTIVE,ARCHIVED}`, terminal `ARCHIVED`/`CANCELLED`), branch audit history **service-only** (`BranchService.history()`; BFS-PF-005 §10 defines no endpoint)
- Tests: `Backend/tests/test_pf005_branches.py`, `Backend/tests/isolation/test_tenant_isolation.py` (`TC-PF-ISO-05`)

**Explicitly excluded from release scope:**

| Excluded | Reason / disposition |
|----------|----------------------|
| **Flutter UI (Batch 3)** — Branch List / Create / Edit / View / Search / Hierarchy / History | **Excluded from PF-005 release scope.** No branch pages exist under `Frontend/lib/`; `ELU-UI-PF` records them as specification only |
| `NTF-PF-005-01..03` notifications | Deferred by approved scope decision (2026-09-12) |
| `RPT-PF-005-01/02` reports | Deferred by approved scope decision (2026-09-12) |
| `AC-PF-005-04` / `BR-PF-038` branch-head assignment and `users.branch_id` | Deferred to **PF-008 Users & Identity** |
| `department` linkage | Deferred to **PF-006** |
| `BR-PF-037` project→branch delete restriction | Deferred — no project→branch linkage exists yet |
| Runtime permission-grain enforcement | Deferred to **PF-009** (role gates only at this baseline) |

## Acceptance criteria status at this baseline

| AC | Statement (ELU-BFS-PF-005 §16) | Status at this baseline |
|----|-------------------------------|-------------------------|
| AC-PF-005-01 | Community edition tenant → branch create rejected (`BR-PF-034`) | Implemented and automated (`TC-PF-BR-01`) |
| AC-PF-005-02 | Branch with open projects → delete rejected (`BR-PF-037`) | **NON-DEMONSTRABLE at this baseline** — requires a project→branch linkage that does not exist; recorded deferral |
| AC-PF-005-03 | Professional tenant with 10 branches → 11th branch create rejected (`BR-PF-039`) | Implemented and automated (`TC-PF-BR-04`) |
| AC-PF-005-04 | Active branch + user assignment → `user.branch_id` updated and visible in profile | **NON-DEMONSTRABLE at this baseline** — `users.branch_id` is not created; deferred to PF-008 |

## Verification evidence

- **Documented automated evidence (executed 2026-09-12, recorded in `ELU-TST-PF` §2.2 v1.4 and `ELU-RTM-001` §11):** PF-005 tests **15 passed**; tenant isolation **13 passed** (including `TC-PF-ISO-05`); full backend suite **141 passed, 1 skipped**; **no PF-001…PF-004 regression identified**.
- **Runtime endpoint evidence (observed 2026-09-14, host-run API against the unchanged baseline application code):** `GET /health` → 200; `POST /api/v1/auth/login` → 200 with JWT issued; `GET /api/v1/org/branches` → 200 with `total = 0` (no branch rows seeded for the tenant used); unauthenticated `GET /api/v1/org/branches` → 401 (route mounted and auth-protected); OpenAPI exposes `/api/v1/org/branches`, `/search`, `/export`, `/hierarchy`, `/{branch_id}`.
- No new test run was executed while preparing this draft; no test result beyond the evidence above is claimed.

## Excluded from this release baseline — Option B infrastructure files

The following **5 working-tree-modified files are explicitly excluded** from the Phase-2-PF005 release and must not form part of any PF-005 release artefact, commit or tag:

| File | State |
|------|-------|
| `.env.example` | Modified, **uncommitted** — excluded |
| `README.md` | Modified, **uncommitted** — excluded |
| `docker-compose.yml` | Modified, **uncommitted** — excluded |
| `Scripts/start-api-host.bat` | Modified, **uncommitted** — excluded |
| `Scripts/start-infra.bat` | Modified, **uncommitted** — excluded |

These are local infrastructure-remediation changes (host PostgreSQL port migration 55432 → 15432 and Compose API `DATABASE_URL_HOST` pinning). They are **not** PF-005 implementation, are **not** covered by this release, and require their own separate commit / PR / governance record.

## Pre-existing advisories — recorded as OUTSIDE PF-005 scope

| # | Advisory | Scope status |
|---|----------|--------------|
| A1 | Docker API container cannot start: the Compose `api` service mounts only `./Backend:/app`, while `Backend/app/db/migrate_pf003a.py` reads `/Database/03_PlatformFoundation/012_rls_pf003a.sql` → `FileNotFoundError` → `Application startup failed. Exiting.` | **Pre-existing, outside PF-005 scope. Not fixed by PF-005.** Blocks `docker compose up api` only; PF-005 endpoints were exercised via the host-run API |
| A2 | `Backend/app/core/config.py` default `database_url` still `postgresql+psycopg://elinkup:elinkup_local@localhost:55432/elinkup` with a stale comment | **Pre-existing, outside PF-005 scope. Not fixed by PF-005.** Inert while an environment source supplies `DATABASE_URL` |
| A3 | `elinkup-redis` defined in Compose but not running | **Outside PF-005 scope. Not fixed by PF-005.** Unrelated to PF-005 functionality |

**No claim is made that PF-005 fixes, mitigates or depends on A1, A2 or A3.** No infrastructure, configuration, Compose or `.env` change is part of this release.

## Approval

- [x] Independent QA release audit recorded (ELU-QA-PF005 v1.0 — **PASS — RELEASE APPROVED**; reviewer identity remains PENDING)
- [x] Human **RELEASE APPROVED** recorded — **`PF-005 RELEASE APPROVED: YES`** (2026-09-14)
- [x] `ELU-QA-REG-001` / `ELU-MSL-001` / `ELU-MSL-002` / `Documentation/CHANGELOG.md` release entries recorded in this change set (register v1.7 → v1.8)
- [ ] Annotated tag `Phase-2-PF005` created on the PF-005 governance merge commit — **NOT YET CREATED** (separate authorised step; target SHA pending)
- [ ] Post-tag reconciliation — tag object SHA, peeled commit SHA and created/pushed date recorded — **PENDING**
- [ ] Flutter UI (Batch 3) release decision — **PENDING** (out of this release scope)

## Open items for the human release decision

**Confirmed by human decision (2026-09-14):**

1. Tag name and type — **CONFIRMED:** `Phase-2-PF005`, **annotated** (only the annotation message text remains open).
2. Baseline commit — **CONFIRMED:** the release baseline is the existing `master`/`origin/master` commit `219bb6c8b026797fef56e3c3a46f6a17c0218787`; **no dedicated no-change baseline commit is to be created** (PF-004 precedent not applied) and the baseline SHA is not to be altered.

**Completed by this change set (2026-09-14):**

3. Governance-record updates — **DONE:** `ELU-QA-PF005` (v1.0, `PASS — RELEASE APPROVED`), `ELU-REL-PF005` (approval recorded, tag pending), `ELU-QA-REG-001` (v1.7 → **v1.8**, PF-005 row), `ELU-MSL-001` (history **1.17**), `ELU-MSL-002` (change log **4.81**), `Documentation/CHANGELOG.md`. **Not committed at the time of writing.**

**Still pending human decision:**
4. Confirm disposition of the 5 uncommitted Option B infrastructure files (recommended: separate commit/PR, never inside the PF-005 tag).
5. Confirm handling of the two non-demonstrable acceptance criteria (AC-PF-005-02, AC-PF-005-04) in the release record.

---

*© Euphoria Infotech (I) Limited — ELU-REL-PF005 (RELEASE APPROVED 2026-09-14 — annotated tag Phase-2-PF005 not yet created)*
