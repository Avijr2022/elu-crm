# PF-008 CORE — Final Evidence Report

**Status:** implementation COMPLETE, verified, **NOT released, NOT committed**.
**Authorization:** `PF-008 CORE IMPLEMENTATION - AUTHORIZED` (human instruction, 2026-09-21).
**Baseline SHA:** `969d022cd006c4ddc024f8e0a5d08af40a868841`
**Branch:** `cursor/pf008-core-implementation` (created from the baseline; no commit made)
**Companion documents:** `Documentation/PF008_CORE_IMPLEMENTATION_MAP.md` (scope + decisions
D1–D14), `Documentation/PF008_CORE_CURSOR_INSTRUCTIONS.md` (the authorizing instruction),
`Documentation/11-Engineering/ELU-API-PF.md` §4.5 (API contract).

---

## 1. Files changed

### Modified (16)

| File | +/- |
|---|---|
| `Backend/app/models/pf/entities.py` | +94 (12 PF-008 columns on `User`, new `UserInvite` entity) |
| `Backend/app/repositories/pf/user_repository.py` | +210 / −2 (directory queries, seat/role counters, `UserInviteRepository`, `RoleRepository.get_by_id`) |
| `Backend/app/services/pf/auth_service.py` | +304 / −5 (lockout, session revocation, register/forgot/reset/change/logout) |
| `Backend/app/db/seed.py` | +82 (3 catalogue entries, `USER_PERMISSION_MATRIX`, `_sync_user_permission_matrix`, 3 call sites) |
| `Backend/app/api/v1/auth.py` | +72 (5 PF-008 auth endpoints) |
| `Backend/app/schemas/pf/auth.py` | +53 (register / forgot / reset / change / message contracts) |
| `Backend/app/core/security.py` | +17 (`generate_opaque_token`, `hash_token`) |
| `Backend/app/models/pf/__init__.py` | +2 (`UserInvite` export) |
| `Backend/app/main.py` | +2 (`apply_pf008_ddl` in the lifespan) |
| `Backend/app/api/v1/router.py` | +2 (PF-008 users router) |
| `Backend/app/db/migrate_pf003a.py` | +1 (`core.user_invite` in `RLS_TABLES`) |
| `Database/03_PlatformFoundation/012_rls_pf003a.sql` | +1 (`core.user_invite` in the PF-003A RLS loop) |
| `Backend/tests/test_pf005_branches.py` | scope guard reconciled (see §5) |
| `Backend/tests/test_pf006_departments.py` | scope guard reconciled (see §5) |
| `Backend/tests/test_pf007_business_units.py` | scope guard reconciled (see §5) |
| `Documentation/11-Engineering/ELU-API-PF.md` | +§4.5 PF-008 CORE endpoint contract |

### Added (11)

| File | Purpose |
|---|---|
| `Database/03_PlatformFoundation/017_users_pf008.sql` | PF-008 CORE DDL (idempotent) |
| `Database/03_PlatformFoundation/017_users_pf008_rollback.sql` | Rollback for 017 |
| `Backend/app/db/migrate_pf008.py` | DDL applicator (owner role, idempotent) |
| `Backend/app/services/pf/user_service.py` | `UserService` + role gates |
| `Backend/app/schemas/pf/user.py` | User request/response contracts |
| `Backend/app/api/v1/pf/users.py` | 12 user endpoints |
| `Backend/tests/test_pf008_users.py` | 23 focused tests |
| `Backend/tests/isolation/test_pf008_users_isolation.py` | 5 tenant-isolation tests |
| `Documentation/PF008_CORE_IMPLEMENTATION_MAP.md` | step-B implementation map + decisions |
| `Documentation/PF008_CORE_EVIDENCE_REPORT.md` | this report |

No governance register was modified: `Documentation/CHANGELOG.md`, `ELU-MSL-001`, `ELU-MSL-002`,
`ELU-QA-REG-001` and `ELU-RTM-001` are **untouched** (they require separate human authorization).
No frontend, no `.venv`, no generated/vendor file was modified.

## 2. Migration

`Database/03_PlatformFoundation/017_users_pf008.sql` (next free number after PF-007's 016),
applied idempotently at app startup by `apply_pf008_ddl` registered in the `app/main.py` lifespan
**after** PF-007 and **after** the PF-003A RLS pass.

* `core.users` — 12 additive columns (`branch_id`, `department_id`, `business_unit_id` with named
  FKs `ON DELETE SET NULL`; `failed_login_count`; `locked_until`; `invited_at`; `activated_at`;
  `deactivated_at`; `password_changed_at`; `reset_token_hash`; `reset_token_expires_at`;
  `sessions_invalid_before`), `ck_users_account_status`
  (`INVITED`,`ACTIVE`,`INACTIVE`,`LOCKED`,`EXPIRED`,`CANCELLED`), `ck_users_failed_login_count`,
  4 partial soft-delete-aware indexes. The CHECK was verified safe before apply: the live database
  contained only `ACTIVE` (852) and `INACTIVE` (6).
* `core.user_invite` — new table (`ELU-BFS-PF-008` §7): PK, tenant/user FKs, unique `token_hash`,
  status CHECK, partial unique index enforcing one ACTIVE invitation per user, RLS enrolled
  (ENABLE + FORCE + `tenant_isolation`) through the PF-003A loop.
* Rollback available as `017_users_pf008_rollback.sql` (manual only, not wired to the lifespan).

## 3. Endpoints added (17 operations)

12 on `/api/v1/users` and 5 on `/api/v1/auth` — full table in
`Documentation/11-Engineering/ELU-API-PF.md` §4.5. `POST /auth/mfa/enroll` and
`POST /auth/mfa/verify` are deliberately **not** registered (MFA out of CORE scope).
OpenAPI loads cleanly (`create_app()` verified) and the app boots with the new DDL applied.

## 4. Tests

| Run | Command | Result |
|---|---|---|
| Compile / import | `python -m compileall -q app tests` and `import app.main` | **exit 0**, `APP_OK E-LinkUp` |
| Focused PF-008 (final) | `pytest tests/test_pf008_users.py tests/isolation/test_pf008_users_isolation.py -q` | **28 passed**, exit 0, 27.6 s |
| Released scope guards + PF-008 (final) | `pytest <3 guard tests> <PF-008 modules> -q` | **31 passed**, exit 0, 44.4 s |
| Full backend suite (single sequential run, final) | `pytest -q` | **238 passed, 1 skipped**, exit 0, 223.9 s (3 min 43 s) |

`git diff --check` and `git diff --cached --check`: **clean** (exit 0). The only stderr output is
Git's advisory `LF will be replaced by CRLF` for the two pre-existing LF-only auth files.

Two intermediate runs and their dispositions (full disclosure):
1. First focused run — 6 failures + 4 errors: five failures and all four errors were **test-setup
   capacity/format issues** (`BR-PF-052` seat cap of 10 correctly blocking further fixtures;
   uppercase tenant codes in the isolation fixtures), one was a **real ordering bug**: a
   superseded (CANCELLED) invitation token expired the *account*, breaking re-invite. Fixed in
   `AuthService.register` (status check split from expiry check; a superseded token never mutates
   the account) and re-verified.
2. Second focused run — 1 failure: `PUT /users/{id}` demanded a role. Changed to PUT semantics
   **D14**: an omitted role/organization keeps its current value (an omission must never re-scope
   or re-privilege an account). Re-verified.
3. First full-suite run — 3 failures: the released PF-005/006/007 deferral guards (see §5).

## 5. Scope-guard reconciliation (the one place released test files were touched)

`test_pf005_branches.py::test_deferred_scope_not_implemented`,
`test_pf006_departments.py::test_deferred_scope_absent` and
`test_pf007_business_units.py::test_deferred_scope_absent` encoded "PF-008 not started" by
asserting the absence of `users.branch_id` / `users.department_id` / `users.business_unit_id`.
Authorization item 9 requires exactly those linkages, so the guards now assert the entries
**exist** (with supersede notes) while every still-valid deferral assertion is retained:
`branch_head_user_id` / `department_head_user_id` have **no FK and no validation** (BR-PF-038 /
BR-PF-043 stay deferred), `crm.opportunity.business_unit_id` is still absent (D6), no reporting
surface is registered, and the only FK now referencing `core.business_unit` is
`fk_users_business_unit`. This follows the precedent recorded for PF-006 Batch 5
("PF-005 scope-guard test update"). **Flagged for human confirmation** because it is the only
change to released test files.

## 6. Deferred PF-008 items (unchanged by this work)

MFA implementation/challenge (`BR-PF-058`, `AC-PF-008-06` non-demonstrable) · SAML/OIDC SSO ·
SCIM · customer-portal users · `NTF-PF-008-01..08` (so `AC-PF-008-01` e-mail delivery is
non-demonstrable) · `RPT-PF-008-01..04` + dashboard/analytics · `JOB-PF-008-01` scheduler
(expiry and lock release are evaluated lazily instead — D6/D7) · `user.impersonate` ·
`core.user_credentials` / `core.user_password_history` / `core.user_session` / `core.user_mfa`
tables (D1/D4) · `BR-PF-038` branch-head and `BR-PF-043` department-head validation (D13; note
`BR-PF-048` is already enforced by released PF-007) · Platform-Admin cross-tenant user listing ·
Flutter screens (PF-008 §11) · governance records.

## 7. Blockers / decisions requiring the human

| # | Item |
|---|---|
| B1 | **`BR-PF-053` password policy has no source.** `Database/03_PlatformFoundation/005_core_tenant_security.sql` is an **empty file** and no `tenant_security` table/model exists anywhere (verified by grep across `Backend/` and by a live-DB probe). Only an 8-character minimum mirroring the existing login contract is enforced (D10). No policy values were invented. |
| B2 | **`user_credentials` separation (BFS §7) not adopted** (D1): the hash stays on `core.users.password_hash` to avoid changing released authentication behaviour or creating a parallel abstraction. |
| B3 | **Scope-guard reconciliation** (§5) — released test files were edited; needs confirmation. |
| B4 | **`BR-PF-057` revocation mechanism** (D4) uses `core.users.sessions_invalid_before` rather than the BFS §7 `user_session` table. |
| B5 | `POST /auth/forgot-password` issues a challenge that is never returned (D11) because `NTF-PF-008-03` delivery is deferred — that path is intentionally non-demonstrable until notifications land. |

## 8. Discipline statement

**NO COMMIT / NO MERGE / NO TAG / NO PUSH.** `HEAD` remains the baseline
`969d022cd006c4ddc024f8e0a5d08af40a868841` on branch `cursor/pf008-core-implementation`
(`HEAD...origin/master` = `0 0`, `origin/master` = the same SHA, 0 tags at `HEAD`), and the
working tree holds exactly the 16 modified + 11 added paths listed in §1, available for review.
