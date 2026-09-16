# E-LinkUp Master Requirements & Traceability Index
**Document ID:** ELU-RTM-001  
**Version:** 1.2  
**Status:** Approved
**Document Owner:** BA / QA
**Related Documents:** ELU-DOC-001, ELU-EFS-001, ELU-DF-001, ELU-TST-*, ELU-BFS-*, ELU-QA-PF001
**Parent:** ELU-EFS-001  
**Example Tenant:** Euphoria  

> This index summarises the Requirement ID ranges and RTM pattern. **Authoritative row-level RTM** lives inside each workflow’s **V1.0 Enterprise Ready Pack** in **ELU-EFS-001 – Enterprise Functional Specification**.

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP | Initial master requirements & RTM index |
| 1.0a | 2026-07-31 | EIIP / PMO | Status Approved; registered in ELU-DOC-001 |
| 1.1 | 2026-08-06 | EIIP / Engineering | PF-001 Edition Management implementation traceability |
| 1.2 | 2026-08-06 | EIIP / QA | PF-001 RELEASE APPROVED — RTM 100% after remediation |
| 1.3 | 2026-08-06 | EIIP / QA | PF-002 Tenant Management implementation traceability (QA PASS) |
| 1.4 | 2026-08-06 | EIIP / PMO | PF-002 RELEASE APPROVED — baseline Phase-2-PF002 |
| 1.5 | 2026-08-06 | EIIP / QA | PF-003 Subscription Management implementation traceability (QA PASS) |
| 1.6 | 2026-08-06 | EIIP / PMO | PF-003 RELEASE APPROVED — baseline Phase-2-PF003 |
| 1.7 | 2026-08-06 | EIIP / QA | PF-003A Enterprise Tenant Isolation traceability (QA PASS — await RELEASE APPROVED) |
| 1.8 | 2026-08-06 | EIIP / PMO | PF-003A RELEASE APPROVED — baseline Phase-2-PF003A; start PF-004 |

## 1. Requirement ID Ranges

| Domain | Prefix | Sample Anchors | Workflows |
|--------|--------|----------------|-----------|
| Platform Foundation | `REQ-PF-` | REQ-PF-001 Create Tenant | WF-PF-001…003 |
| CRM | `REQ-CRM-` | REQ-CRM-001 Create Lead · REQ-CRM-002 Convert Lead to Opportunity | WF-CRM-001…004 |
| Sales | `REQ-SAL-` | REQ-SAL-001 Generate Quotation | WF-SAL-001…003 |
| Projects | `REQ-PRJ-` | REQ-PRJ-001 Create Project | WF-PRJ-001…003 |
| Finance | `REQ-FIN-` | REQ-FIN-001 Create Invoice | WF-FIN-001…002 |
| Service | `REQ-SRV-` | REQ-SRV-001 Create Ticket | WF-SRV-001 |
| Integration | `REQ-INT-` | REQ-INT-001 Register API Consumer | WF-INT-001…004 |

## 2. RTM Pattern (Mandatory)

| Requirement | Workflow | Table | API | Flutter Screen | Test Case |
|-------------|----------|-------|-----|----------------|-----------|
| REQ-CRM-001 | WF-CRM-001 | lead | POST /api/v1/crm/leads | Lead Create | TC-CRM-001 |
| REQ-CRM-002 | WF-CRM-001 | lead, opportunity | POST /api/v1/crm/leads/{id}/convert | Lead Convert | TC-CRM-002 |
| REQ-SAL-001 | WF-SAL-001 | quotation | POST /api/v1/sales/quotations | Quotation Create | TC-SAL-001 |

## 3. Companion Artefacts per Workflow

| Artefact | Use |
|----------|-----|
| State Transition Diagram | Allowed / Invalid / Re-open / Rollback |
| CRUD Responsibility Matrix | RBAC implementation |
| NFR-* | Performance, Security, Audit, Scalability, Availability, Retention |
| UI Navigation | Flutter roadmap |
| API Contract Summary | FastAPI router checklist |

## 4. How Teams Use This

| Role | Action |
|------|--------|
| Business Analyst | Own `REQ-*` wording and RTM completeness |
| Developer (Backend) | Implement APIs/tables keyed by `REQ-*` |
| Developer (Flutter) | Implement screens from UI Navigation + RTM |
| QA | Author `TC-*` from RTM; never invent unlinked tests |
| Architect | Enforce NFR and tenant isolation (**ADR-015**) |

---

## 5. v1.0 Coverage Checklist

SoT: **ELU-EFS-001** + companion V1 packs (**ELU-EFS-SOT-001**). Each workflow must have §§16–22 artefacts.

| Workflow | Domain | V1 Pack | REQ/RTM | State | CRUD | NFR | UI Nav | API | Status |
|----------|--------|---------|---------|-------|------|-----|--------|-----|--------|
| WF-PF-001 | PF | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PF-002 | PF | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PF-003 | PF | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-CRM-001 | CRM | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-CRM-002 | CRM | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-CRM-003 | CRM | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-CRM-004 | CRM | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-SAL-001 | SAL | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-SAL-002 | SAL | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-SAL-003 | SAL | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PRJ-001 | PRJ | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PRJ-002 | PRJ | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PRJ-003 | PRJ | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-FIN-001 | FIN | V1-FIN-SRV-INT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-FIN-002 | FIN | V1-FIN-SRV-INT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-SRV-001 | SRV | V1-FIN-SRV-INT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | v1.1 scope |
| WF-INT-001…004 | INT | V1-FIN-SRV-INT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | v2.0 scope |

---

## 6. Implementation Traceability — PF-001 Edition Management (100%)

| Business Rule / Capability | Table(s) | API | Flutter | Automated Test |
|----------------------------|----------|-----|---------|----------------|
| Edition catalogue CRUD (BFS §10) | `core.edition` (`id`,`code`,`name`) | `/api/v1/platform/editions` | List + Create + Edit + View | `test_list_editions`, create flows |
| Feature matrix | `feature_catalogue`, `edition_feature` | create/update `features` | View dialog | publish / create tests |
| Limits (EDM baselines) | `edition_limit` | create/update `limits` | View dialog | `test_limit_below_community_baseline` |
| Publish DRAFT→ACTIVE (BR-PF-008) | `edition`, `edition_version`, `audit.audit_event` | `POST .../publish` | Publish approval dialog | `test_create_publish_deprecate_flow` |
| Deprecate / deactivate (BR-PF-005) | `edition`, audit | `POST .../deprecate` + `assert_assignable` | (API; UI deprecate via future action) | deprecate + audit asserts |
| Search | `edition` | `GET .../search` | Search field | `test_search_and_history` |
| History | `edition_version` | `GET .../history` | History dialog | `test_search_and_history` |
| Tenant read-only edition | `edition` via tenant FK | `GET /api/v1/tenant/edition` | `_TenantEditionView` | `test_get_tenant_edition` |
| DDD schema alignment | `edition` CHECK + indexes | — | — | `test_schema_ddd_columns` |
| OpenAPI | — | `/openapi.json` | — | `test_openapi_includes_editions` |
| Audit logging | `audit.audit_event` | mutations | — | audit asserts in publish flow |

**Coverage:** **100%** of PF-001 BFS §10 APIs and §11 screens (List/Create/Edit/View/Search/Publish/History).  
**QA:** [ELU-QA-PF001 v2.0](../ELU-QA-PF001-Edition-Management-Release-Audit.md) — **RELEASE APPROVED**.  
**Baseline:** Release **Phase-2-PF001** · Git tag `Phase-2-PF001` · Notes [ELU-REL-PF001](../ELU-REL-PF001-Phase-2-PF001-Release-Notes.md) · [CHANGELOG](../CHANGELOG.md).  
**Rule:** Do not modify PF-001 unless a defect is reported.

**Code:** `Backend/app/api/v1/pf/editions.py`, `edition_service.py`, `audit_service.py`  
**SQL:** `009_edition_ddd_align_pf001.sql`, `migrate_pf001.py`  
**OpenAPI:** `Backend/openapi/openapi.json`

---

## 7. Implementation Traceability — PF-002 Tenant Management (100% platform scope)

| Business Rule / Capability | Table(s) | API | Flutter | Automated Test |
|----------------------------|----------|-----|---------|----------------|
| Register tenant (PENDING_ACTIVATION) | `tenant`, contact, address, org, settings, subscription | `POST /platform/tenants` | Register dialog | `test_register_approve_suspend_reactivate` |
| Code format/unique (BR-PF-009) | `tenant.tenant_code` | create validator | Register | `test_br_pf_009_code_validation` |
| legal_name unique (BR-PF-010) | `uk_tenant_legal_name` | create | — | `test_br_pf_010_legal_name_unique` |
| PRIMARY contact (BR-PF-011) | `tenant_contact` + UK | create | Register | create flow asserts contact |
| REGISTERED address (BR-PF-012) | `tenant_address` + UK | create | Register | create flow asserts address |
| ACTIVE edition only (BR-PF-013) | `edition` via `assert_assignable` | create | Register | `test_br_pf_013_deprecated_edition_blocked` |
| Suspended login block (BR-PF-014) | `tenant.status` | `/auth/login`, refresh | — | auth_service + smoke |
| Soft-close (BR-PF-015) | `tenant` CLOSED + soft delete | `DELETE /platform/tenants/{id}` | — | `test_soft_delete_closed` |
| Own profile isolation (BR-PF-016) | `tenant` | `GET /tenant/profile` | — | `test_tenant_profile_own` |
| Approve / Suspend / Reactivate | `tenant`, `tenant_status_history`, audit | `.../approve|suspend|reactivate` | action buttons | lifecycle test |
| List / Search / Export | `tenant` | list/search/export | List + Search | `test_list_tenants`, `test_search_and_export` |
| Idempotency | `idempotency_key` | `Idempotency-Key` header | — | `test_idempotency_key` |
| Audit | `audit.audit_event` | mutations | — | `test_audit_on_create` |
| Migration | PF-002 DDL | — | — | `test_migration_idempotent` |

**Coverage:** **100%** of PF-002 BFS §10 **platform** APIs + core §11 screens (List/Register/View/Search/Approve/Suspend). Branding/self-reg deferred (see ELU-QA-PF002 §3).  
**QA:** [ELU-QA-PF002 v1.1](../ELU-QA-PF002-Tenant-Management-Release-Audit.md) — **RELEASE APPROVED**.  
**Baseline:** Release **Phase-2-PF002** · Git tag `Phase-2-PF002` · Notes [ELU-REL-PF002](../ELU-REL-PF002-Phase-2-PF002-Release-Notes.md) · [CHANGELOG](../CHANGELOG.md).  
**Rule:** Do not modify PF-002 unless a defect or approved CR is raised. Do not start PF-004 until PF-003 is RELEASE APPROVED.

**Code:** `Backend/app/api/v1/pf/tenants.py`, `tenant_service.py`  
**SQL:** `010_tenant_pf002.sql`, `migrate_pf002.py`  
**Flutter:** `tenants_page.dart`, `tenant_service.dart`  
**OpenAPI:** `Backend/openapi/pf002-tenants-paths.json`

---

## 8. Implementation Traceability — PF-003 Subscription Management (100% platform scope)

| Business Rule / Capability | Table(s) | API | Flutter | Automated Test |
|----------------------------|----------|-----|---------|----------------|
| One current ACTIVE/TRIAL (BR-PF-019) | `subscription`, `tenant.current_subscription_id` | create / reactivate | — | `test_br_pf_019_one_current` |
| end_date > start_date (BR-PF-020) | `subscription` | create/update/renew | — | `test_br_pf_020_end_before_start` |
| Seats ≤ edition MAX_USERS (BR-PF-021) | `edition_limit` | create/update/upgrade | — | `test_br_pf_021_seat_over_edition` |
| Seats ≥ active users (BR-PF-022/027) | `users` count | renew/update | — | enforced in service |
| Downgrade guard (BR-PF-023) | edition limits vs users | upgrade | Upgrade dialog | service assert |
| Expire → tenant SUSPENDED (BR-PF-024) | `subscription`, `tenant` | `POST .../expire` | — | `test_expire_cascades_tenant_suspend` |
| Trial max 30 days (BR-PF-025) | `subscription` | create TRIAL | — | service validation |
| History on change (BR-PF-026) | `subscription_history`, audit | history + mutations | View | lifecycle + audit tests |
| Activate trial | `subscription` | `PATCH .../{id}` | Activate | lifecycle test |
| Renew / Upgrade | `subscription` | renew / upgrade | Renew / Upgrade | lifecycle test |
| List / Search / Export | `subscription` | list/search/export | List + Search | list + export tests |
| My subscription / usage | `subscription_usage` | `/tenant/subscription` + usage | — | `test_usage_and_export` |
| Migration | PF-003 DDL | — | — | `test_migration_idempotent` |

**Coverage:** **100%** of PF-003 BFS §10 platform APIs + core §11 screens (List/Search/Create/Edit/View/Activate/Renew/Upgrade/History/My Subscription). Scheduler NTF deferred (ELU-TD-001).  
**QA:** [ELU-QA-PF003 v2.1](../ELU-QA-PF003-Subscription-Management-Release-Audit.md) — **RELEASE APPROVED**.  
**Baseline:** Release **Phase-2-PF003** · Git tag `Phase-2-PF003` · Notes [ELU-REL-PF003](../ELU-REL-PF003-Phase-2-PF003-Release-Notes.md) · [CHANGELOG](../CHANGELOG.md).  
**Rule:** Do not modify PF-003 unless a documented bug, approved CR, or ADR requires it. Next module requires explicit human start + CON GAP analysis.

**Code:** `Backend/app/api/v1/pf/subscriptions.py`, `subscription_service.py`  
**SQL:** `011_subscription_pf003.sql`, `migrate_pf003.py`  
**Flutter:** `subscriptions_page.dart`  
**OpenAPI:** `Backend/openapi/pf003-subscriptions-paths.json`

---

## 9. Implementation Traceability — PF-003A Enterprise Tenant Isolation

| Requirement / Control | Artefact | API / Runtime | Test |
|----------------------|----------|---------------|------|
| ADR-015 dual isolation | ADR-016 | `rls_context` + policies | `tests/isolation/*` |
| FORCE RLS tenant tables | `012_rls_pf003a.sql` | `apply_pf003a_ddl` | `test_migration_idempotent_and_rls_forced` |
| Session `app.tenant_id` | DEV-001 §6A | `bind_rls_context` / after_begin | `test_set_local_guc_visible_in_session` |
| Platform Admin bypass | ADR-015 §4 | `platform_context` on PLATFORM_ADMIN | `test_platform_context_bypass`, TC-PF-ISO-04 |
| Cross-tenant IDOR 404 | T-01 / NFR | CRM lead GET | TC-PF-ISO-01 |
| Body tenant_id ignored | T-02 | LeadCreate | TC-PF-ISO-02 |
| Soft-deleted hidden | T-ISO-03 | Auth + SQL | TC-PF-ISO-03 |
| JWT tenant spoof | T-01 | `get_current_user` | `test_jwt_tenant_spoof_rejected` |
| Fail-closed empty GUC | CON §3 | `elu_app` + FORCE | `test_rls_blocks_without_context` |
| Platform-global no RLS | ADR-015 §5 | edition / permission | `test_edition_tables_have_no_rls` |

**Coverage:** **100%** of ADR-015 mandatory isolation controls for current schema.  
**QA:** [ELU-QA-PF003A](../ELU-QA-PF003A-Enterprise-Tenant-Isolation-Release-Audit.md) — **RELEASE APPROVED**.  
**Baseline:** Release **Phase-2-PF003A** · Git tag `Phase-2-PF003A` · Notes [ELU-REL-PF003A](../ELU-REL-PF003A-Phase-2-PF003A-Release-Notes.md) · [ELU-EHC-002](../ELU-EHC-002-Enterprise-Security-Health-Card-PF003A.md).  
**Rule:** PF-001…003A frozen. PF-004 Organization Management started under CON after RELEASE APPROVED.

**Code:** `Backend/app/db/rls_context.py`, `migrate_pf003a.py`, `deps.py`, `auth_service.py`  
**SQL:** `012_rls_pf003a.sql`  
**Tests:** `Backend/tests/isolation/test_tenant_isolation.py`

---

## 10. Implementation Traceability — PF-004 Organization Management (RELEASE APPROVED — tag `Phase-2-PF004-R1`)

| Requirement | Artefact | API | Test |
|-------------|----------|-----|------|
| BR-PF-028 one ROOT | `uk_organization_one_root` | `GET /org/organizations/root` | `test_ac_pf_004_01_one_root` |
| BR-PF-029 code UK | `uk_org_tenant_code` | POST create | create child test |
| BR-PF-030 GSTIN | schema validator | PATCH | `test_ac_pf_004_02_invalid_gstin` |
| BR-PF-031 no delete ROOT | service | DELETE | `test_ac_pf_004_03_root_cannot_delete` |
| BR-PF-033 FY month | CHECK + schema | PATCH | profile update test |
| List/Search/Export/Hierarchy | BFS §10 | `/api/v1/org/organizations*` | list + hierarchy tests |
| Flutter §11 | Organizations tab | — | manual / analyze |

**Status:** Implemented and **RELEASE APPROVED** — human release decision recorded 2026-09-11 (`ELU-QA-PF004` §5); approved corrections merged in `67b48c1`, approval recorded via PR #10 (`ad039ea`); released as annotated tag **`Phase-2-PF004-R1`** → target commit `3f30159a3ba73be1f09be791164982ec74ff8044`. *(Superseded wording: this line previously read "QA PASS — PENDING HUMAN RELEASE APPROVAL … human RELEASE APPROVED outstanding".)*  
**Code:** `organizations.py`, `organization_service.py`, `migrate_pf004.py`  
**SQL:** `013_organization_pf004.sql`  
**Flutter:** `organizations_page.dart`  
**Tests:** `tests/test_pf004_organizations.py`

---

## 11. Implementation Traceability — PF-005 Branch Management (IMPLEMENTED — NOT RELEASED)

Specification: `ELU-BFS-PF-005` §7/§9/§10/§16 · Schema: `014_branch_pf005.sql` · RLS: `012_rls_pf003a.sql` (ADR-015) · Test spec: `ELU-TST-PF` §2.2.

| Requirement | Artefact | API (implemented) | Test (implemented) |
|-------------|----------|-------------------|--------------------|
| BR-PF-034 edition gate (Professional+) | edition feature `BRANCH` (seeded; Community blocked) | all 9 endpoints (edition gate) | TC-PF-BR-01 |
| BR-PF-035 branch code unique per tenant | `uk_branch_tenant_code_active` (partial) | POST create | TC-PF-BR-02 |
| BR-PF-036 at least one HEAD_OFFICE (warning) | Advisory `warnings[]` in the response — **never blocks** | POST create | TC-PF-BR-03 |
| BR-PF-037 no delete with active projects | **DEFERRED** — needs project → branch linkage | DELETE | *(deferred)* |
| BR-PF-038 branch head must be ACTIVE user | **DEFERRED to PF-008** — `branch_head_user_id` nullable, **no FK, no assignment logic** | — | *(deferred)* |
| BR-PF-039 max branches per edition | `MAX_BRANCHES` limit (Professional 10 / Enterprise 999999); counts **non-deleted** branches, including retained terminal-state (`ARCHIVED`/`CANCELLED`) rows | POST create | TC-PF-BR-04 |
| AC-PF-005-04 user branch assignment | **DEFERRED to PF-008** — no `users.branch_id` | — | *(deferred)* |
| Hierarchy (parent/child, Restrict) | `fk_branch_parent`; self-parenting and circular ancestry rejected | `GET /api/v1/org/branches/hierarchy` | TC-PF-BR-05 |
| Address 1:1 | `branch_address` (`uk_branch_address_branch`, CASCADE) + `fk_branch_address` (SET NULL) | PUT/PATCH | TC-PF-BR-06 |
| Lifecycle states | BFS-PF-005 §5 transitions (`DRAFT→{ACTIVE,CANCELLED}`, `ACTIVE→INACTIVE`, `INACTIVE→{ACTIVE,ARCHIVED}`, terminal `ARCHIVED`/`CANCELLED`) | PATCH | `test_crud_put_patch_lifecycle_and_audit` |
| Branch history | `BranchService.history()` + schemas — **service-only, no API endpoint** (BFS §10 defines none) | — | service-level assertions |
| Tenant isolation | FORCE RLS + `tenant_isolation` on `core.branch`, `core.branch_address` | — | TC-PF-ISO-05 |

**Status:** **IMPLEMENTED — NOT RELEASED.** Groundwork Batch 1 (specification, schema, RLS, ORM, seed) **plus Batch 2 — backend functional layer**, delivered directly to `master` at `4430f9d2b9eedc51dede1ca1cf6183508a756dac` (2026-09-12): `app/schemas/pf/branch.py`, `app/services/pf/branch_service.py`, `app/api/v1/pf/branches.py` (+ router registration), `tests/test_pf005_branches.py`, `TC-PF-ISO-05`. No Flutter/UI, notifications or reports.
**SQL:** `014_branch_pf005.sql`, `014_branch_pf005_rollback.sql`  
**RLS:** `012_rls_pf003a.sql` (tables added to the PF-003A loop), `migrate_pf003a.py::RLS_TABLES`  
**ORM:** `app/models/pf/entities.py` — `Branch`, `BranchAddress`  
**Seed:** `BRANCH_PERMISSION_MATRIX`, `branch.*` permissions, `MAX_BRANCHES` limits  
**API:** 9 endpoints under `/api/v1/org/branches` (create, list, detail, PUT, PATCH, soft delete, search, export, hierarchy) — see `ELU-API-PF` §4.

**Tests:** implemented — `Backend/tests/test_pf005_branches.py` (15) + `TC-PF-ISO-05` in `Backend/tests/isolation/test_tenant_isolation.py` (13 isolation tests); full backend suite **141 passed, 1 skipped**; no PF-001…PF-004 regression. See `ELU-TST-PF` §2.2.

**Baseline:** **none — PF-005 is NOT released**: no release approval, no QA release audit, no tag.

**Deferred (recorded):** AC-PF-005-04 / BR-PF-038 and `users.branch_id` and branch-head assignment/validation → **PF-008**; `department` linkage → **PF-006**; BR-PF-037 project→branch enforcement → deferred until a project→branch linkage exists; **NTF-PF-005-\*** and **RPT-PF-005-\*** → deferred; runtime permission-grain enforcement → **PF-009** (role gates only for now); branch audit history → service-only, no API endpoint.

---

*© Euphoria Infotech (I) Limited — ELU-RTM-001*
### PF-007 Release Traceability Record

| Module | Release | Release Commit | Release Tag | Approval |
|---|---|---|---|---|
| PF-007 Business Unit Management | Phase 2 | `80ae94e1dd071f62198571a7592cf81246ee591e` | `Phase-2-PF007` | PF-007 RELEASE APPROVED: YES |
