# Changelog

All notable E-LinkUp implementation milestones.

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
