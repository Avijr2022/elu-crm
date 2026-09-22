# PF-008 CORE — Implementation Map

**Status:** IN PROGRESS — implementation started, **NOT released**, **NOT committed**.
**Authorization:** `PF-008 CORE IMPLEMENTATION - AUTHORIZED` (human instruction, 2026-09-21).
**Baseline SHA:** `969d022cd006c4ddc024f8e0a5d08af40a868841`
**Branch:** `cursor/pf008-core-implementation`
**Authoritative specification:** `Documentation/01-BFS-Platform-Foundation/ELU-BFS-PF-Platform-Foundation.md` §PF-008 (Document ID `ELU-BFS-PF-008`).

> This document is the step-B deliverable of the authorization. It records scope, the
> inspected existing architecture, the implementation decisions taken, and the items that
> remain deferred. No governance record (`ELU-MSL-001`, `ELU-MSL-002`, `ELU-QA-REG-001`,
> `Documentation/CHANGELOG.md`) is modified: those require separate human authorization.

---

## 1. Scope implemented (CORE items 1–12 of the authorization)

| # | Authorization item | Implementation |
|---|---|---|
| 1 | User profile CRUD + tenant-scoped directory/list API | `app/api/v1/pf/users.py`, `app/services/pf/user_service.py` |
| 2 | Registration / invitation flow | `POST /users` (invite), `POST /auth/register` (activate), `POST /users/{id}/reinvite` |
| 3 | 72-hour invitation expiry | `core.user_invite.expires_on` + lazy expiry evaluation (`BR-PF-054`) |
| 4 | Lifecycle INVITED / ACTIVE / INACTIVE / LOCKED / EXPIRED / CANCELLED | `core.users.account_status` (+ `ck_users_account_status`) |
| 5 | Password reset / change flow | `POST /auth/forgot-password`, `POST /auth/reset-password`, `POST /auth/change-password`, `POST /users/{id}/reset-password` |
| 6 | Five failed-login lockout, 30-minute lock | `core.users.failed_login_count` + `locked_until` (`BR-PF-055`) |
| 7 | Seat-limit enforcement on create/invite | `user_service._assert_seat_available` (`BR-PF-052`, source: `core.subscription.seat_count` via `Tenant.current_subscription_id`) |
| 8 | JWT/refresh integration, `tenant_id` never from body | `auth_service.login/refresh` extended; all endpoints use `CurrentUser.tenant_id` only |
| 9 | Linkage to PF-005 branch / PF-006 department / PF-007 business unit | `core.users.branch_id/department_id/business_unit_id` (FK, SET NULL) + tenant-ownership and ACTIVE-target validation |
| 10 | `user.create/read/update/delete/export` (+ `user.reset_password`) | `app/db/seed.py` catalogue extension + `USER_PERMISSION_MATRIX` + `_sync_user_permission_matrix` at all three provisioning paths |
| 11 | Automated tests incl. isolation + authorization | `Backend/tests/test_pf008_users.py`, `Backend/tests/isolation/test_pf008_users_isolation.py` |
| 12 | Migration + schemas/routes/services/repositories + focused docs | `Database/03_PlatformFoundation/017_users_pf008.sql` (+ rollback), `app/db/migrate_pf008.py`, `app/schemas/pf/user.py`, this map |

### Explicitly deferred (per authorization)
MFA implementation/challenge (`BR-PF-058`) · SAML/OIDC SSO · SCIM · customer-portal users ·
full `NTF-PF-008-*` notification suite · `RPT-PF-008-*` reports/dashboards/analytics ·
unrelated PF-009 RBAC redesign · frontend implementation · unrelated cleanup/refactoring.

---

## 2. Existing architecture inspected (step A) and reused

| Concern | Existing artefact | Reuse |
|---|---|---|
| Tenant isolation | RLS `tenant_isolation` on `core.users` (`relrowsecurity=t`, `relforcerowsecurity=t`), `RLS_TABLES` in `app/db/migrate_pf003a.py`, `bind_rls_context` (`ADR-015`) | unchanged; new table enrolled in the same loop |
| Auth | `app/services/pf/auth_service.py`, `app/api/v1/auth.py`, `app/core/security.py` (argon2 + JWT), `app/core/deps.py::CurrentUser` | extended additively |
| User model / repo | `app/models/pf/entities.py::User`, `app/repositories/pf/user_repository.py::UserRepository` | extended, not replaced |
| Seat data | `core.subscription.seat_count`, `Tenant.current_subscription_id`, `app/services/pf/subscription_service.py::_active_user_count` (pattern) | re-used as the authoritative seat source |
| Edition limits | `core.edition_limit.MAX_USERS` (`subscription_service._edition_max_users`) | re-used for the edition bound |
| Branch / Department / BusinessUnit | `core.branch` (PF-005, released), `core.department` (PF-006, released), `core.business_unit` (PF-007, released) — all RLS-enforced | referenced by FK only; no released-module code changed |
| Audit | `app/services/pf/audit_service.py::write_audit_event` (`audit.audit_event`) | PF-008 audit events |
| Permission catalogue | `app/db/seed.py::PERMISSIONS`, `*_PERMISSION_MATRIX`, `_sync_*_permission_matrix` (HD-01 pattern) | new PF-008 matrix in the same shape |
| API conventions | `app/api/v1/pf/departments.py` (router shape, `require_*` role gates, `http_error_from_app`), `app/schemas/pf/department.py` (PUT/PATCH split, `version_no` optimistic locking) | mirrored |
| Migrations | `Database/03_PlatformFoundation/NNN_*_pfNNN.sql` + rollback + `app/db/migrate_pfNNN.py` registered in `app/main.py` lifespan | `017_users_pf008.sql` (next free number) |
| Tests | `Backend/tests/conftest.py::platform_session`, `tests/test_pf00N_*.py` fixtures, `tests/isolation/*` | mirrored |

Verified against the live dev database (evidence, 2026-09-21): `core.users` = 19 columns,
indexes `users_pkey` / `uk_users_tenant_email` / `ix_core_users_email` / `ix_core_users_tenant_id`,
`account_status` ∈ {`ACTIVE` 852, `INACTIVE` 6}, `core.user_invite` absent.

---

## 3. Implementation decisions

| ID | Decision | Rationale / status |
|---|---|---|
| **D1** | Password hash **stays inline** on `core.users.password_hash`. No `core.user_credentials` table. | `ELU-BFS-PF-008` §7 lists a separate `user_credentials` table, but the released implementation (seed, `AuthService.login/refresh`, all tests) reads `users.password_hash`. The authorization forbids changing released behaviour and forbids parallel abstractions. **Deviation from §7 — flagged for human decision.** |
| **D2** | Invite state in a dedicated **`core.user_invite`** table (BFS §7-conformant), RLS-enrolled via the PF-003A loop. | Supports 72 h expiry, re-invite, `CANCELLED`, and one active invite per user; keeps `core.users` narrow. Uses the established PF-005/006/007 pattern of enrolling a new table in the PF-003A loop. |
| **D3** | Password-reset challenge stored **on `core.users`** (`reset_token_hash`, `reset_token_expires_at`); no separate reset table. | BFS §7 defines no reset table; token is a transient 1:1 challenge. |
| **D4** | Session revocation via **`core.users.sessions_invalid_before`** (late-bind check in `AuthService.refresh`) instead of a `core.user_session` table. | Satisfies `BR-PF-057` (deactivated user's refresh tokens stop working) with an additive change; no session table (BFS §7's `user_session`) is introduced in CORE. |
| **D5** | Invite and reset tokens are **opaque** (`secrets.token_urlsafe(32)`), stored as **SHA-256 hash**. | Standard pattern; avoids inventing new JWT `type` values that other decode paths would have to reject. |
| **D6** | Invitation expiry is evaluated **lazily** (service-side, on login/read) setting `account_status = EXPIRED`, not by a scheduler. | The scheduler `JOB-PF-008-01` (EFS-PF) is out of CORE scope; lazy evaluation is deterministic and testable. |
| **D7** | Lockout: 5th consecutive failure sets `account_status = LOCKED` + `locked_until = now + 30 min`; the lock **auto-expires lazily** on the next login attempt after `locked_until`. | `BR-PF-055` + `AC-PF-008-04`; no scheduler needed. |
| **D8** | Seat usage for `BR-PF-052` counts **`ACTIVE` + `INVITED` + `LOCKED`** non-deleted users (seats are consumed by invitations too) and requires `usage + 1 <= seat_count`, where the subscription is `Tenant.current_subscription_id` with status `ACTIVE`/`TRIAL`; the edition `MAX_USERS` bound is additionally enforced. | `BR-PF-052` + `AC-PF-008-02`. PF-003's own `BR-PF-027` counter is left untouched. |
| **D9** | Role gates mirror the BFS-PF-008 §12 actor matrix: read/list/search/export = `TENANT_ADMIN` + `PLATFORM_ADMIN`; create/update/delete/reinvite/reset = `TENANT_ADMIN` + `PLATFORM_ADMIN`; `/users/me` = any authenticated user. | Same convention as PF-005/006/007 (`require_*` role gates; runtime permission-grain enforcement remains PF-009). |
| **D10** | `BR-PF-053` (password policy from `tenant_security`) is enforced **only** as a minimum length of 8 characters, mirroring the existing `LoginRequest.password` contract. | **`005_core_tenant_security.sql` is an empty file and no `tenant_security` table/model exists anywhere in the codebase** (verified by grep + DB probe) — there is no policy source, and inventing policy values is not permitted. **Flagged as a blocker/decision for the human.** |
| **D11** | `POST /auth/forgot-password` returns a generic `200` and does **not** return the reset token; `POST /users/{id}/reset-password` (permission-gated `user.reset_password`) returns the newly issued token in the response. | `NTF-PF-008-03` e-mail delivery is deferred, so the admin-initiated path must be demonstrable; the public path stays non-enumerable and is **non-demonstrable** until notifications land. |
| **D12** | `/users/me` re-uses `AuthService.me` (same payload as the existing `GET /auth/me`). | BFS §10 lists both; aliasing avoids a parallel implementation. |
| **D13** | Head/manager validations owned by PF-008 but living in released modules are **not retrofitted**: `BR-PF-038` (branch head) and `BR-PF-043` (department head) remain as released-documented deferrals. `BR-PF-048` is already enforced by PF-007 (`test_inactive_manager_rejected`). | Retrofitting them would alter released PF-005/PF-006 behaviour and contradict released audit statements — an explicit STOP condition. **Flagged for human decision.** |
| **D14** | `PUT /users/{id}` keeps the **current** role and organization when those fields are omitted (linkage columns are replaced, since PUT is a full replace). | An omission must never silently re-scope or re-privilege an account; found by the focused test run and corrected before verification. |
| **D15** | The released PF-005/006/007 deferral guard tests were **reconciled** (flipped to the positive direction with supersede notes) rather than left failing. | Authorization item 9 requires `users.branch_id` / `department_id` / `business_unit_id`, so the guards' "PF-008 not started" premise is superseded — the same treatment PF-006 Batch 5 applied to the PF-005 guard. All still-valid deferral assertions retained. **Flagged for human confirmation.** |

---

## 4. Endpoint surface (17 new operations, BFS-PF-008 §10)

`/api/v1/users` — tag `PF-008 Users` (`app/api/v1/pf/users.py`)

| Method | Path | Permission (gate) |
|---|---|---|
| POST | `/users` | `user.create` (TENANT_ADMIN, PLATFORM_ADMIN) |
| GET | `/users` | `user.read` |
| GET | `/users/search` | `user.read` |
| GET | `/users/export` | `user.export` (TENANT_ADMIN, PLATFORM_ADMIN) |
| GET | `/users/me` | authenticated |
| PUT | `/users/me` | authenticated |
| GET | `/users/{user_id}` | `user.read` |
| PUT | `/users/{user_id}` | `user.update` |
| PATCH | `/users/{user_id}` | `user.update` |
| DELETE | `/users/{user_id}` | `user.delete` (soft deactivate) |
| POST | `/users/{user_id}/reinvite` | `user.create` |
| POST | `/users/{user_id}/reset-password` | `user.reset_password` |

`/api/v1/auth` — additions to the existing router

| Method | Path | Access |
|---|---|---|
| POST | `/auth/register` | public (invite token) |
| POST | `/auth/logout` | authenticated |
| POST | `/auth/forgot-password` | public (non-enumerable) |
| POST | `/auth/reset-password` | public (reset token) |
| POST | `/auth/change-password` | authenticated |

Deferred (not registered): `POST /auth/mfa/enroll`, `POST /auth/mfa/verify`.

---

## 5. Data model changes

`core.users` (additive, existing 19 columns untouched):

`branch_id` (FK `core.branch` SET NULL) · `department_id` (FK `core.department` SET NULL) ·
`business_unit_id` (FK `core.business_unit` SET NULL) · `failed_login_count` (INT NOT NULL DEFAULT 0) ·
`locked_until` · `invited_at` · `activated_at` · `deactivated_at` · `password_changed_at` ·
`reset_token_hash` · `reset_token_expires_at` · `sessions_invalid_before` (all TIMESTAMPTZ unless noted) ·
`ck_users_account_status` CHECK (`INVITED`,`ACTIVE`,`INACTIVE`,`LOCKED`,`EXPIRED`,`CANCELLED`) ·
partial soft-delete-aware indexes on the three linkage columns.

`core.user_invite` (new, RLS-enforced): `invite_id` PK · `tenant_id` FK · `user_id` FK CASCADE ·
`token_hash` (unique) · `status` CHECK (`ACTIVE`,`USED`,`EXPIRED`,`CANCELLED`) · `expires_on` ·
`created_by` · `used_on` · soft-delete + version columns. At most one `ACTIVE` invite per user
(partial unique index).

---

## 6. Rule coverage

| Rule | Status |
|---|---|
| `BR-PF-051` email unique per tenant | Already enforced by `uk_users_tenant_email` |
| `BR-PF-052` seat limit on create/invite | Implemented (D8) |
| `BR-PF-053` password policy | Partial — minimum length only (D10, blocker) |
| `BR-PF-054` invite token 72 h | Implemented |
| `BR-PF-055` 5 failures / 30-min lock | Implemented (D7) |
| `BR-PF-056` access 15 min / refresh 7 days | Already implemented (`app/core/config.py`) |
| `BR-PF-057` deactivation revokes refresh tokens | Implemented via `sessions_invalid_before` (D4) |
| `BR-PF-058` MFA required | **Deferred** (MFA out of CORE scope) |
| `BR-PF-059` user ∈ JWT tenant | Already enforced (`get_current_user` + RLS) + new list endpoints |
| `BR-PF-060` at least one ACTIVE Tenant Admin | Implemented as a guard on deactivate/update/delete |
| `AC-PF-008-01` invite token valid 72 h | Implemented; e-mail delivery deferred (`NTF-PF-008-01`) |
| `AC-PF-008-02` seat-limit rejection | Implemented |
| `AC-PF-008-03` JWT claims carry tenant_id/roles | Pre-existing behaviour, covered by test |
| `AC-PF-008-04` 5 failures ⇒ LOCKED | Implemented |
| `AC-PF-008-05` deactivated cannot log in | Pre-existing behaviour + new deactivate path |
| `AC-PF-008-06` MFA challenge | **Deferred** (non-demonstrable) |
| `AC-PF-008-07` tenant-scoped user list | Implemented |

---

## 7. Remaining deferrals and flags for the human

1. **D1** — `user_credentials` / `user_password_history` separation (BFS §7) not adopted.
2. **D10** — no `tenant_security` table exists (`005_core_tenant_security.sql` is empty), so the
   configurable password policy of `BR-PF-053` cannot be implemented without inventing values.
3. **D13** — `BR-PF-038` / `BR-PF-043` head validations remain as released-documented deferrals.
4. `NTF-PF-008-01…08`, `RPT-PF-008-01…04`, `JOB-PF-008-01`, MFA, SSO, SCIM, impersonation
   (`user.impersonate`, no §10 endpoint), self-scoped `SALES_EXECUTIVE` grains (§12 self-scope is
   realised by `/users/me`), Platform-Admin cross-tenant listing (§12 "read (all tenants)"; no §10
   endpoint provides it).

**NO COMMIT / NO MERGE / NO TAG / NO PUSH.** Working tree left for human review.

> **Implementation complete and verified — see `Documentation/PF008_CORE_EVIDENCE_REPORT.md`
> for the final evidence (files, migration, endpoints, test runs, full-suite result) and the
> blockers B1–B5 requiring human decision. API contract: `Documentation/11-Engineering/ELU-API-PF.md` §4.5.**
