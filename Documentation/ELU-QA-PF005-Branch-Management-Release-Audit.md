# E-LinkUp QA Release Audit — PF-005 Branch Management

**Document ID:** ELU-QA-PF005
**Version:** 1.0 — **RELEASED (2026-09-14)**
**Module:** PF-005 — Branch Management
**Audit Date:** 2026-09-14 (evidence compiled from repository evidence and recorded runtime observations; no new test execution performed)
**Auditor:** **PENDING** — independent reviewer name/role not recorded in the authorising instruction (ELU-AI-001: no AI-originated approval; the human decision below is transcribed verbatim)
**Related Documents:** ELU-CON-001, ELU-BFS-PF-005, ELU-RTM-001 §11, ELU-API-PF §4, ELU-TST-PF §2.2 (v1.4), ELU-DDD-PF, ELU-ERD-PF, ELU-UI-PF, ELU-MSL-001, ELU-MSL-002, ELU-QA-REG-001, ELU-QA-PF003A, ADR-015
**Content / implementation baseline:** `219bb6c8b026797fef56e3c3a46f6a17c0218787` — declared content baseline, **not** the tag target; unchanged
**Release decision:** **`PF-005 RELEASE APPROVED: YES`** — human decision recorded **2026-09-14** (approver name/role pending record)
**Release status:** **RELEASED** (2026-09-14)
**Release tag:** **`Phase-2-PF005`** (annotated) — **created and pushed 2026-09-14**; tag object `8f0502ce507da62de25f8105c06ac3185da83c97`
**Release-tag target:** `bdc188c8ff1c89c3e0578830ef73c9934536b495` — the PF-005 governance merge commit ("Merge pull request #18"); no dedicated no-change baseline commit
**Verdict:** **PASS — RELEASE APPROVED**

---

## 1. Executive verdict

| Gate | Result at this baseline |
|------|-------------------------|
| PF-005 backend functional layer implemented | **VERIFIED** — `a8c2e06` (Batch 1), `4430f9d` (Batch 2) |
| Implementation integrated into `master` | **VERIFIED** — both commits are ancestors of `master` |
| PF-005 documentation reconciliation | **VERIFIED** — `56f201e` (PR #16), `219bb6c` (PR #17) |
| Endpoint surface exists and is auth-protected | **VERIFIED** — 9 endpoints under `/api/v1/org/branches`; unauthenticated access returns 401 |
| Automated test evidence | **VERIFIED AS DOCUMENTED** — recorded in `ELU-TST-PF` §2.2 v1.4 (executed 2026-09-12); not re-executed for this audit |
| Tenant-isolation evidence | **VERIFIED AS DOCUMENTED** — `TC-PF-ISO-05` within the isolation suite (13 tests) |
| AC-PF-005-01, AC-PF-005-03 | **VERIFIED AS IMPLEMENTED AND AUTOMATED** |
| AC-PF-005-02, AC-PF-005-04 | **NON-DEMONSTRABLE AT THIS BASELINE** (recorded deferrals) |
| Flutter UI acceptance criteria | **NOT IN RELEASE SCOPE** — no UI delivered |
| Human **RELEASE APPROVED** | **YES** — `PF-005 RELEASE APPROVED: YES`, 2026-09-14 (approver name/role pending record) |
| Release status | **RELEASED** — PF-005 backend functional layer (2026-09-14) |
| Release tag | **`Phase-2-PF005`** (annotated) — **created and pushed 2026-09-14**; tag object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495` |
| Governance change set | Merged via PR #18 at governance merge `bdc188c8ff1c89c3e0578830ef73c9934536b495`; post-tag reconciliation records updated 2026-09-14 (`ELU-REL-PF005`, `ELU-QA-REG-001` v1.9, `ELU-MSL-001` 1.18, `ELU-MSL-002` 4.82, `Documentation/CHANGELOG.md`) |

**Approval provenance:** the human decision `PF-005 RELEASE APPROVED: YES` (2026-09-14) was human-supplied and is transcribed verbatim; the assistant originated no approval (ELU-AI-001). The independent-reviewer signature remains **PENDING** and is recorded as such rather than fabricated. **AC-PF-005-02 and AC-PF-005-04 remain NON-DEMONSTRABLE** — release approval does not convert them to verified.

---

## 2. Mandatory checklist evidence (as applicable to a backend-scope release)

| Item | Evidence | Status |
|------|----------|--------|
| Business specification | `ELU-BFS-PF-005` §7/§9/§10/§16 (module PF-005-001 Branch Structure / Branch Profile) | ✓ VERIFIED |
| Database schema / migration | `Database/03_PlatformFoundation/014_branch_pf005.sql` (+ `014_branch_pf005_rollback.sql`) — idempotent creation of `core.branch`, `core.branch_address` | ✓ VERIFIED |
| RLS / tenant isolation | `012_rls_pf003a.sql` loop + `migrate_pf003a.py::RLS_TABLES` include `core.branch`, `core.branch_address` (ADR-015); `tenant_isolation` FORCE RLS | ✓ VERIFIED |
| ORM models | `app/models/pf/entities.py` (`Branch`, `BranchAddress`); exports in `app/models/pf/__init__.py` | ✓ VERIFIED |
| Seed / permissions / limits | `BRANCH_PERMISSION_MATRIX`, `branch.*` permissions, `MAX_BRANCHES` limits, `BRANCH` edition feature | ✓ VERIFIED |
| FastAPI / OpenAPI surface | `app/api/v1/pf/branches.py` + router registration; `ELU-API-PF` §4 — 9 endpoints | ✓ VERIFIED |
| Business rules enforcement | `BR-PF-034`, `BR-PF-035`, `BR-PF-036`, `BR-PF-039` implemented (see §3); `BR-PF-037`, `BR-PF-038` deferred | ✓ VERIFIED WITH DEFERRALS |
| Lifecycle state machine | Transitions per BFS-PF-005 §5; covered by `test_crud_put_patch_lifecycle_and_audit` | ✓ VERIFIED AS DOCUMENTED |
| Audit history | `BranchService.history()` — service-only; BFS-PF-005 §10 defines no history endpoint | ✓ VERIFIED (service scope) |
| Tenant isolation tests | `Backend/tests/isolation/test_tenant_isolation.py` (`TC-PF-ISO-05`), suite of 13 | ✓ VERIFIED AS DOCUMENTED |
| Automated unit/integration tests | `Backend/tests/test_pf005_branches.py` (15 tests) | ✓ VERIFIED AS DOCUMENTED |
| Regression against baselined modules | Full backend suite **141 passed, 1 skipped**; no PF-001…PF-004 regression identified | ✓ VERIFIED AS DOCUMENTED |
| Flutter UI / responsive / accessibility | No branch screens implemented (`ELU-UI-PF`: specification only) | ✗ NOT IN SCOPE — not claimed |
| Notifications / reports | `NTF-PF-005-*`, `RPT-PF-005-*` deferred by approved decision | ✗ NOT IN SCOPE — not claimed |
| QA release audit (this document) | Draft only; independent review outstanding | ⏳ PENDING |
| Release notes | `ELU-REL-PF005` draft prepared | ⏳ DRAFT |
| Human release approval | Not recorded | ⏳ PENDING |
| Release tag | Not created; no tag points at the baseline | ⏳ PENDING |

---

## 3. Business-rule coverage and evidence

| Rule | Requirement | Implementation evidence | Test evidence | Status |
|------|-------------|-------------------------|---------------|--------|
| BR-PF-034 | Edition gate — branch management requires Professional+ (`BRANCH` feature) | Edition gate on all 9 endpoints; `BRANCH` feature seeded; Community blocked | `TC-PF-BR-01` | VERIFIED |
| BR-PF-035 | Branch code unique per tenant | `uk_branch_tenant_code_active` (partial unique index) | `TC-PF-BR-02` | VERIFIED |
| BR-PF-036 | At least one HEAD_OFFICE (advisory) | `warnings[]` in the response — never blocks creation | `TC-PF-BR-03` | VERIFIED |
| BR-PF-037 | No delete with active projects | — | — | **DEFERRED** — requires project→branch linkage; **non-demonstrable at this baseline** |
| BR-PF-038 | Branch head must be an ACTIVE user | `branch_head_user_id` nullable, no FK and no assignment logic | — | **DEFERRED to PF-008** — **non-demonstrable at this baseline** |
| BR-PF-039 | Max branches per edition | `MAX_BRANCHES` limit (Professional 10 / Enterprise 999999), counting non-deleted branches including retained terminal-state rows | `TC-PF-BR-04` | VERIFIED |
| Hierarchy | Parent/child with restrict, self-parent and cycle rejection | `fk_branch_parent`; validation in service layer | `TC-PF-BR-05` | VERIFIED |
| Address 1:1 | `branch_address` linkage | `uk_branch_address_branch` (CASCADE), `fk_branch_address` (SET NULL) | `TC-PF-BR-06` | VERIFIED |
| Lifecycle | State transitions per BFS-PF-005 §5 | PATCH transitions; terminal states | `test_crud_put_patch_lifecycle_and_audit` | VERIFIED AS DOCUMENTED |
| Tenant isolation | Cross-tenant access denied | FORCE RLS on `core.branch`, `core.branch_address` | `TC-PF-ISO-05` | VERIFIED AS DOCUMENTED |

"VERIFIED" for `TC-PF-BR-*` and lifecycle items denotes automation recorded in `ELU-TST-PF` §2.2 and `ELU-RTM-001` §11 as passing on 2026-09-12. Those results were **not** re-executed while compiling this draft.

---

## 4. Acceptance criteria — verified vs non-demonstrable

| AC | Requirement | Verification route | Status |
|----|-------------|--------------------|--------|
| AC-PF-005-01 | Community edition tenant → branch create rejected (`BR-PF-034`) | Automated (`TC-PF-BR-01`); edition-gate behaviour | **VERIFIED** |
| AC-PF-005-02 | Branch with open projects → delete rejected (`BR-PF-037`) | Requires a project→branch linkage that does not exist at this baseline | **NON-DEMONSTRABLE** — not claimed as delivered; deferral recorded in `ELU-RTM-001` §11, `ELU-TST-PF` §2.2 |
| AC-PF-005-03 | Professional tenant with 10 branches → 11th create rejected (`BR-PF-039`) | Automated (`TC-PF-BR-04`); `MAX_BRANCHES` limit | **VERIFIED** |
| AC-PF-005-04 | Active branch + user assignment → `user.branch_id` updated and visible in profile | `users.branch_id` not created; assignment/validation deferred to PF-008 | **NON-DEMONSTRABLE** — not claimed as delivered; deferral recorded in `ELU-RTM-001` §11, `ELU-BFS-PF-005`, `ELU-PGR-001` §16 |

No Flutter/UI acceptance criterion is assessed: the UI is excluded from PF-005 release scope.

---

## 5. Automated test evidence (as documented — not re-executed for this draft)

| Evidence | Result | Source |
|----------|--------|--------|
| `Backend/tests/test_pf005_branches.py` | **15 passed** | `ELU-TST-PF` §2.2 v1.4 (executed 2026-09-12); `ELU-RTM-001` §11 |
| `Backend/tests/isolation/test_tenant_isolation.py` (incl. `TC-PF-ISO-05`) | **13 passed** | Same |
| Full backend suite | **141 passed, 1 skipped** | Same |
| PF-001…PF-004 regression | **none identified** | Same |

A previously observed artefact of running the suite concurrently (a `DeadlockDetected` on the startup RLS DDL path) was attributed to concurrent execution, not to a PF-005 defect; it is recorded here as context only and is not presented as a test result.

---

## 6. Runtime / endpoint evidence (observed 2026-09-14)

| Observation | Result |
|-------------|--------|
| `GET /health` (host-run API, port 8000) | **200** — `{"status":"ok","app":"E-LinkUp","env":"local"}` |
| `POST /api/v1/auth/login` | **200** — JWT issued |
| `GET /api/v1/org/branches` (authenticated) | **200** — `total = 0` (no branch rows present for the tenant used) |
| `GET /api/v1/org/branches` (unauthenticated) | **401** — route mounted and auth-protected |
| OpenAPI paths | `/api/v1/org/branches`, `/search`, `/export`, `/hierarchy`, `/{branch_id}` |
| Database baseline | `pgdata` volume created `2026-08-26T07:31:20Z` (not recreated); `core.tenant` = 666 |

Runtime evidence was obtained against application code identical to the intended baseline; the only working-tree modifications present were five configuration/documentation files that are excluded from this release (see §7) and do not alter application code.

**Limitation:** the containerised API could not be used for this evidence because of pre-existing advisory A1 (§7). Endpoint evidence was therefore obtained from the host-run API only.

---

## 7. Advisories — outside PF-005 scope, not fixed by PF-005

| ID | Advisory | Determination |
|----|----------|---------------|
| A1 | Docker `api` service cannot start: Compose mounts only `./Backend:/app`, while `Backend/app/db/migrate_pf003a.py` reads `/Database/03_PlatformFoundation/012_rls_pf003a.sql` → `FileNotFoundError: No such file or directory` → `ERROR: Application startup failed. Exiting.` | **Pre-existing defect, outside PF-005 scope. NOT fixed by PF-005.** Blocks `docker compose up api` for the whole stack, not PF-005 specifically |
| A2 | `Backend/app/core/config.py` `database_url` default remains `postgresql+psycopg://elinkup:elinkup_local@localhost:55432/elinkup` with a stale comment | **Pre-existing, outside PF-005 scope. NOT fixed by PF-005.** Latent only; overridden whenever an environment source supplies `DATABASE_URL` |
| A3 | `elinkup-redis` container defined but not running; in-container `REDIS_URL` unresolvable | **Outside PF-005 scope. NOT fixed by PF-005.** Unrelated to PF-005 functionality |

**No PF-005 fix, mitigation, dependency or acceptance claim is associated with A1, A2 or A3.** No infrastructure, Compose, `.env` or application-code change is included in this release.

### 7.1 Excluded working-tree changes

The following five configuration/documentation files (**Option B** infrastructure remediation) are modified in the working tree and are **excluded** from this release and from the PF-005 governance change set: `.env.example`, `README.md`, `docker-compose.yml`, `Scripts/start-api-host.bat`, `Scripts/start-infra.bat`. They are infrastructure remediation for a local host port constraint (55432 → 15432) plus Compose API database-URL pinning, are not PF-005 implementation, and are not covered by this audit.

---

## 8. Residual / deferred (non-blocking for a backend-scope release)

| Item | Severity | Track |
|------|----------|-------|
| AC-PF-005-04 / BR-PF-038 branch-head assignment and `users.branch_id` | Recorded deferral | PF-008 Users & Identity |
| BR-PF-037 project→branch delete restriction (AC-PF-005-02) | Recorded deferral | Pending project→branch linkage |
| `department` linkage | Recorded deferral | PF-006 |
| Runtime permission-grain enforcement (role gates only) | Med | PF-009 |
| `NTF-PF-005-*` notifications, `RPT-PF-005-*` reports | Recorded deferral | Deferred by 2026-09-12 decision |
| Branch audit history API | Service-only by specification | No endpoint defined in BFS-PF-005 §10 |
| Container API startup (A1), stale config fallback (A2), Redis (A3) | See §7 | Outside PF-005 scope |

---

## 9. Release decision (Human) — RECORDED; RELEASED 2026-09-14

```text
PF-005 BRANCH MANAGEMENT — RELEASE APPROVED: YES
STATUS: RELEASED — ANNOTATED TAG Phase-2-PF005 CREATED AND PUSHED 2026-09-14
CONTENT BASELINE: 219bb6c8b026797fef56e3c3a46f6a17c0218787
TAG OBJECT SHA: 8f0502ce507da62de25f8105c06ac3185da83c97
FINAL TAG TARGET: bdc188c8ff1c89c3e0578830ef73c9934536b495
APPROVAL DATE: 2026-09-14
APPROVER: PENDING — name/role not recorded in the authorising instruction
SCOPE: PF-005 backend functional layer only
EXCLUDED: Flutter UI (Batch 3); NTF-*; RPT-*; AC-PF-005-02; AC-PF-005-04
NOT CLAIMED: Docker /Database mount defect, config.py fallback, Redis (pre-existing, out of scope)
```

Approval recorded from the human decision transcribed above (values human-supplied; ELU-AI-001 — no AI-originated approval). **Historical note (pre-tag state at the approval step): no tag had been created or pushed and no tag object SHA existed then.** The annotated tag was subsequently created and pushed on 2026-09-14 — tag object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495`. AC-PF-005-02 and AC-PF-005-04 remain **NON-DEMONSTRABLE** at this baseline.

---

## 10. Governance fields — recording state

| Record | Field | State |
|--------|-------|-------|
| ELU-QA-PF005 (this document) | Auditor / reviewer identity | **PENDING** — not recorded in the authorising instruction |
| ELU-QA-PF005 (this document) | Verdict | **RECORDED** — `PASS — RELEASE APPROVED` |
| ELU-QA-PF005 (this document) | Human RELEASE APPROVED | **RECORDED** — `PF-005 RELEASE APPROVED: YES`, 2026-09-14 |
| `ELU-QA-REG-001` PF-005 row | Audit Doc reference | **RECORDED** — `ELU-QA-PF005 v1.0` (register v1.7 → v1.9) |
| `ELU-QA-REG-001` PF-005 row | Verdict | **RECORDED** — `RELEASE APPROVED` |
| `ELU-QA-REG-001` PF-005 row | Release Tag | **RECORDED** — `Phase-2-PF005` (annotated), tag object `8f0502ce507da62de25f8105c06ac3185da83c97` → target `bdc188c8ff1c89c3e0578830ef73c9934536b495`, created/pushed 2026-09-14 (register v1.8 → v1.9) |
| `ELU-QA-REG-001` PF-005 row | Locked | **RECORDED** — `Yes` (recorded at approval per the PF-004 convention; the PF-004 register showed `Locked = Yes` with the tag cell marked pending before the tag existed) |
| `ELU-REL-PF005` | Git tag line | **RECORDED** — `RELEASED — ANNOTATED TAG Phase-2-PF005 CREATED AND PUSHED 2026-09-14`; tag object and target recorded |
| `ELU-REL-PF005` | Approval checklist | Approval items checked; tag-creation and post-tag reconciliation items now closed |
| `ELU-MSL-001` / `ELU-MSL-002` / `Documentation/CHANGELOG.md` | PF-005 release history rows | **RECORDED** — MSL-001 history 1.17 (approval) and **1.18** (tag created/pushed); MSL-002 change log 4.81 (approval) and **4.82** (post-tag reconciliation) |
| Post-tag reconciliation | Tag object SHA, peeled commit SHA, final tag target SHA, created/pushed date | **RECORDED 2026-09-14** — tag object `8f0502ce507da62de25f8105c06ac3185da83c97`, target `bdc188c8ff1c89c3e0578830ef73c9934536b495` |

---

*© Euphoria Infotech (I) Limited — ELU-QA-PF005 v1.0 (RELEASED 2026-09-14 — annotated tag Phase-2-PF005, tag object 8f0502ce507da62de25f8105c06ac3185da83c97, target bdc188c8ff1c89c3e0578830ef73c9934536b495)*
