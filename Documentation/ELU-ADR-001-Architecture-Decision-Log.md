# E-LinkUp Architecture Decision Log
**Document ID:** ELU-ADR-001  
**Document Name:** Architecture Decision Log (ADL)  
**Version:** 1.3  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Enterprise Solution Architecture  
**Document Owner:** Solution Architecture / PMO  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-CON-001, ELU-AI-001, ELU-DOC-001, ELU-DF-001, ELU-SAD-001, ELU-EFS-001, ELU-CHR-001, ELU-SEH-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP / Solution Architecture | Initial Decision Log; expanded ADR-001…009 from ELU-SAD-001; added ADR-010…014 |
| 1.1 | 2026-08-06 | EIIP / Solution Architecture | ADR-015 dual tenant isolation (app filter + PostgreSQL RLS); ADR-001 clarified |
| 1.2 | 2026-08-06 | EIIP / Solution Architecture | §7 AI immutability; CON / Cursor AI cross-links |
| 1.3 | 2026-08-06 | EIIP / Solution Architecture | ADR-016 PF-003A implements ADR-015 (RLS + SET LOCAL + elu_app) |

---

## 1. Purpose

The **Architecture Decision Log** records every significant architectural or product-engineering decision for E-LinkUp.

Months or years later, anyone joining the programme can answer:

> *Why was this approach chosen — and what was rejected?*

**Rule:** No significant architecture, stack, tenancy, security, or documentation-structure decision is final until it has a **Decision ID** in this log.

Catalogue entry: **ELU-DOC-001 – Documentation Master Index**.

---

## 2. Decision Record Template (Mandatory)

Every new decision must use this structure:

| Field | Description |
|-------|-------------|
| **Decision ID** | `ADR-NNN` (sequential in this log) |
| **Title** | Short decision name |
| **Date** | Decision date (YYYY-MM-DD) |
| **Status** | Proposed / Accepted / Superseded / Deprecated |
| **Deciders** | Roles / names accountable |
| **Related Documents** | ELU-* Document IDs |
| **Context** | Problem / force that required a decision |
| **Reason** | Why a decision was needed now |
| **Alternatives Considered** | Options evaluated (with brief pros/cons) |
| **Final Decision** | What was chosen |
| **Impact** | Consequences for design, cost, ops, product, team |
| **Consequences / Follow-ups** | Work items, constraints, revisit triggers |

### 2.1 Status Values

| Status | Meaning |
|--------|---------|
| Proposed | Under discussion |
| Accepted | Binding for current versions |
| Superseded | Replaced by a newer ADR (cite successor) |
| Deprecated | No longer applicable |

---

## 3. Decision Index

| Decision ID | Title | Date | Status |
|-------------|-------|------|--------|
| ADR-001 | Shared database with `tenant_id` isolation | 2026-07-30 | Accepted |
| ADR-002 | FastAPI + PostgreSQL + SQLAlchemy stack | 2026-07-30 | Accepted |
| ADR-003 | Flutter for Web and Android clients | 2026-07-30 | Accepted |
| ADR-004 | JWT + Refresh Token; SSO/MFA Enterprise-only | 2026-07-30 | Accepted |
| ADR-005 | MinIO for documents (not DB BLOBs) | 2026-07-30 | Accepted |
| ADR-006 | Soft delete + `version_no` optimistic locking | 2026-07-30 | Accepted |
| ADR-007 | Shared platform engines over per-module duplicates | 2026-07-30 | Accepted |
| ADR-008 | Redis + Celery deferred to Phase 3 | 2026-07-30 | Accepted |
| ADR-009 | Edition matrix drives module visibility | 2026-07-30 | Accepted |
| ADR-010 | REQ-* as project-wide traceability anchor | 2026-07-31 | Accepted |
| ADR-011 | EFS as implementation source of truth for workflows | 2026-07-31 | Accepted |
| ADR-012 | Document numbering & status governance (ELU-DOC-001) | 2026-07-31 | Accepted |
| ADR-013 | Community / Professional / Enterprise packaging | 2026-07-30 | Accepted |
| ADR-014 | Docker + Azure / Linux VPS hosting model | 2026-07-30 | Accepted |
| ADR-015 | Dual tenant isolation: repository filters + PostgreSQL RLS | 2026-08-06 | Accepted |
| ADR-016 | PF-003A implements ADR-015 (elu_app role + session GUCs) | 2026-08-06 | Accepted |
| ADR-018 | PLATFORM_ADMIN CRM permission policy | PENDING (date to be supplied before acceptance) | Proposed |

---

## 4. Decision Records

---

### ADR-001 — Shared Database with `tenant_id` Isolation

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-001 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture, Product Owner |
| **Related Documents** | ELU-SAD-001, ELU-EFS-001, ELU-BFS-PF, ELU-CHR-001 |

**Context**  
E-LinkUp is a commercial multi-tenant SaaS. Tenant **Euphoria** (and peers) must never see each other’s data, while the product must remain operable on a single deployment for early phases.

**Reason**  
A tenancy model must be chosen before table design and API middleware are built.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Shared DB + `tenant_id` on all business tables | Lower ops cost; simpler migrations; fits v1 hosting | Requires rigorous query filters / RLS discipline |
| B. Database-per-tenant | Strong physical isolation | High ops cost; hard on VPS/early Azure; slow provisioning |
| C. Schema-per-tenant | Medium isolation | Migration complexity; tooling friction |

**Final Decision**  
**Alternative A** — Shared PostgreSQL database with mandatory `tenant_id` on tenant-scoped tables. **Enforcement detail is binding in ADR-015** (application repository/middleware filters **plus** PostgreSQL Row Level Security as defense-in-depth). Platform-global masters (e.g. `edition`, `permission`) may omit tenant scope.

**Impact**  
- Every BFS/EFS/DDD artefact must mark tenant scope.  
- Isolation tests are mandatory Acceptance Criteria.  
- Revisit if a regulated customer requires physical isolation (possible Enterprise add-on later).  
- See **ADR-015** for RLS session variable, bypass role, and migration rules.

---

### ADR-002 — FastAPI + PostgreSQL + SQLAlchemy Core Stack

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-002 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture, Tech Lead |
| **Related Documents** | ELU-SAD-001, ELU-CHR-001, ELU-API-* (planned) |

**Context**  
Backend runtime and persistence stack must be fixed for hiring, scaffolding, and CI/CD.

**Reason**  
Avoid mixed backend paradigms that fragment the codebase.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Python FastAPI + PostgreSQL + SQLAlchemy | Fast to build; strong typing/OpenAPI; team-friendly | Python concurrency model needs care at extreme scale |
| B. Node.js / NestJS + PostgreSQL | Large talent pool | Split from existing Python preference |
| C. .NET / Java Spring | Enterprise familiarity | Heavier for early SaaS velocity on VPS |

**Final Decision**  
**Alternative A** — Python **FastAPI**, **PostgreSQL**, **SQLAlchemy**.

**Impact**  
- API packs (**ELU-API-***) target OpenAPI from FastAPI.  
- Celery workers (Phase 3) stay in Python ecosystem (**ADR-008**).

---

### ADR-003 — Flutter for Web and Android Clients

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-003 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Product Owner, Solution Architecture |
| **Related Documents** | ELU-SAD-001, ELU-UI-* (planned), ELU-EFS-001 |

**Context**  
CRM/ERP users need Web (desktop) and Android field access with one UX language.

**Reason**  
Dual native Web + Android codebases would double UI cost.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Flutter Web + Android | Single codebase; consistent UI | iOS later; Web nuances |
| B. React Web + Flutter/React Native mobile | Best-of-breed web | Two UI stacks |
| C. Progressive Web App only | Fastest web delivery | Weaker mobile UX offline |

**Final Decision**  
**Alternative A** — **Flutter** for Web and Android; shared information architecture from **ELU-EFS-001** UI Navigation / Flutter Mapping.

**Impact**  
- **ELU-UI-*** packs describe Flutter routes/widgets.  
- iOS may be a future ADR.

---

### ADR-004 — JWT + Refresh Token; SSO/MFA Enterprise-Only

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-004 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Security / Solution Architecture |
| **Related Documents** | ELU-SAD-001, ELU-BFS-PF (PF-008), ELU-EFS-001 WF-PF-* |

**Context**  
Authentication must work for Community demos through Enterprise customers.

**Reason**  
Balance time-to-market with enterprise security packaging.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. JWT + Refresh for all; SSO/MFA in Enterprise | Clear edition differentiation | MFA not default on lower editions |
| B. MFA mandatory for all editions | Stronger default security | Friction for Community/SME |
| C. Session cookies only | Simple browser model | Weaker for Flutter mobile / APIs |

**Final Decision**  
**Alternative A** — **JWT + Refresh Token** baseline; **SSO/MFA** enabled for **Enterprise** (and optionally Professional later). Password hashing: Argon2id.

**Impact**  
- Edition matrix (**ADR-009**) gates SSO/MFA.  
- Refresh rotation and lockout policies live in `tenant_security`.

---

### ADR-005 — MinIO for Document Storage (Not Database BLOBs)

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-005 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture |
| **Related Documents** | ELU-SAD-001, ELU-BFS-CPS (CPS-006), ELU-EFS-001 |

**Context**  
Quotations, proposals, invoices, and attachments require versioned file storage.

**Reason**  
Storing binaries in PostgreSQL harms backup size and performance.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. MinIO (S3-compatible) | Portable; works on VPS and Azure | Ops component to run |
| B. PostgreSQL BYTEA/BLOB | Single system | DB bloat; poor streaming |
| C. Cloud-only Azure Blob | Managed | Couples early VPS deployments |

**Final Decision**  
**Alternative A** — **MinIO** with tenant-prefixed object keys; metadata/versions in PostgreSQL.

**Impact**  
- Document Engine (**CPS-006**) depends on MinIO.  
- Virus/type validation before store.

---

### ADR-006 — Soft Delete + `version_no` Optimistic Locking

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-006 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture, BA |
| **Related Documents** | ELU-DF-001, ELU-EFS-001, ELU-DDD-* (planned) |

**Context**  
CRM/ERP records participate in audit, finance, and legal retention.

**Reason**  
Hard deletes break history and referential integrity.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Soft delete (`is_deleted`) + `version_no` | Audit-friendly; concurrency-safe | Queries must filter deleted rows |
| B. Hard delete only | Simpler tables | Unacceptable for invoices/customers |
| C. Temporal tables only | Strong history | Higher PostgreSQL complexity for v1 |

**Final Decision**  
**Alternative A** — Soft delete + optimistic locking via `version_no`; retain `created_*` / `modified_*` audit columns.

**Impact**  
- Unique constraints must consider active rows.  
- DELETE APIs mean logical archive unless explicitly justified.

---

### ADR-007 — Shared Platform Engines Over Per-Module Duplicates

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-007 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture, Product Owner |
| **Related Documents** | ELU-SAD-001, ELU-BFS-CPS, ELU-EFS-001 |

**Context**  
Approvals, rules, notifications, audit, and documents repeat across CRM, Sales, Projects, Finance, Service.

**Reason**  
Duplicating engines per module creates inconsistent behaviour and higher cost.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Shared engines (Workflow, Rule, Notification, Document, Audit, Report) | Consistency; one place to improve | Requires clear contracts |
| B. Module-local implementations | Faster first screen | Divergent UX/rules; rewrite later |

**Final Decision**  
**Alternative A** — Shared **CPS** engines consumed by all domains.

**Impact**  
- EFS workflows declare engine usage.  
- CPS modules are Phase 3 priority for depth (**ADR-008** related).

---

### ADR-008 — Redis + Celery Deferred to Phase 3

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-008 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture, Product Owner |
| **Related Documents** | ELU-SAD-001, ELU-BRD-001 (phase plan), ELU-BFS-CPS |

**Context**  
Background jobs (SLA timers, dunning, notifications) are needed but not Day-1 blockers for Foundation + CRM core.

**Reason**  
Reduce Phase 1/2 operational surface on VPS.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Defer Redis/Celery to Phase 3 (v1.5) | Faster Phase 1–2 | Limited async until then |
| B. Introduce Redis/Celery in Phase 1 | Ready for jobs early | Extra ops before needed |

**Final Decision**  
**Alternative A** — **Redis + Celery in Phase 3**; synchronous or lightweight scheduling acceptable until then for critical paths.

**Impact**  
- Service SLA monitor and advanced notifications target Phase 3.  
- Design APIs so jobs can be extracted without contract breaks.

---

### ADR-009 — Edition Matrix Drives Module Visibility

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-009 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Product Owner, Solution Architecture |
| **Related Documents** | ELU-BRD-001, ELU-BFS-PF (PF-001), ELU-EFS-001 WF-PF-003 |

**Context**  
Product must sell Community, Professional, and Enterprise differently.

**Reason**  
Feature gating must be server-enforced, not UI-only.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Edition + Subscription feature flags at runtime | Clear packaging; upgradable | Requires careful matrix maintenance |
| B. Separate codebases per edition | Hard isolation | Unmaintainable |
| C. UI hiding only | Fast | Security hole |

**Final Decision**  
**Alternative A** — Runtime **edition matrix** (Community / Professional / Enterprise) gates modules and capabilities; enforce on API and UI.

**Impact**  
- BFSs state minimum edition.  
- Subscription expiry restricts licensed features (**BR-PF-***).

---

### ADR-010 — `REQ-*` as Project-Wide Traceability Anchor

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-010 |
| **Date** | 2026-07-31 |
| **Status** | Accepted |
| **Deciders** | Product Owner, BA, QA Lead, Solution Architecture |
| **Related Documents** | ELU-EFS-001, ELU-RTM-001, ELU-DF-001, ELU-TST-* (planned) |

**Context**  
BA, Development, and QA need one ID that ties requirements to tables, APIs, screens, and tests.

**Reason**  
Without REQ IDs, RTM and test coverage drift.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. `REQ-{DOM}-{nnn}` mandatory on every EFS workflow | Single anchor; industry-standard RTM | Authoring overhead |
| B. Trace only by Workflow ID | Less writing | Ambiguous for multi-req workflows |
| C. Trace only by BR-* rules | Good for validation | Misses positive functional asks |

**Final Decision**  
**Alternative A** — Mandatory **Requirement IDs** and **RTM** (REQ → WF → Table → API → Screen → TC) per **ELU-EFS-001** V1.0 Completeness Criteria; index in **ELU-RTM-001**.

**Impact**  
- QA writes `TC-*` from RTM, not ad hoc.  
- No feature is “done” without REQ coverage.

---

### ADR-011 — EFS as Implementation Source of Truth for Workflows

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-011 |
| **Date** | 2026-07-31 |
| **Status** | Accepted |
| **Deciders** | PMO, Solution Architecture, Product Owner |
| **Related Documents** | ELU-EFS-001, ELU-WF-001, ELU-DOC-001 |

**Context**  
Both a narrative workflow doc and a deep EFS exist.

**Reason**  
Developers must know which document is binding for build.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. ELU-EFS-001 Approved = implementation SoT; ELU-WF-001 Deprecated for build | Clear | Must keep EFS updated |
| B. Keep both equally binding | — | Conflict risk |
| C. BFS only | Good module depth | Weaker cross-module workflow engine view |

**Final Decision**  
**Alternative A** — **ELU-EFS-001** is the implementation source of truth for workflows; **ELU-WF-001** retained as Deprecated narrative base.

**Impact**  
- Sprint planning references EFS workflow IDs + REQ IDs.  
- Changes to process go into EFS first, then BFS if module depth changes.

---

### ADR-012 — Document Numbering & Status Governance

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-012 |
| **Date** | 2026-07-31 |
| **Status** | Accepted |
| **Deciders** | PMO |
| **Related Documents** | ELU-DOC-001, ELU-DF-001 |

**Context**  
Documentation set grew (BFS, EFS, RTM, SAD, Story). Risk of teams using outdated drafts.

**Reason**  
Need catalogue, status, version history, and consistent prefixes.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. ELU-DOC-001 master index + status model + prefixes (CHR/SEH/BRD/BFS/EFS/DDD/ERD/API/UI/RTM/TST/ADR) | Navigable; audit-friendly | Discipline required |
| B. Ad hoc filenames only | Fast | Unscalable |

**Final Decision**  
**Alternative A** — Govern via **ELU-DOC-001** and **ELU-DF-001**; statuses Draft / In Review / Approved / Deprecated; mandatory Version History; Document ID cross-references.

**Impact**  
- New docs must be registered in **ELU-DOC-001** before use.  
- Field Dictionary renamed conceptually to **ELU-DDD**; tests to **ELU-TST**.

---

### ADR-013 — Community / Professional / Enterprise Packaging

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-013 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Product Owner |
| **Related Documents** | ELU-CHR-001, ELU-BRD-001, ELU-BFS-PF (PF-001), ADR-009 |

**Context**  
Commercial packaging must match market segments (learning, SME, enterprise).

**Reason**  
Edition strategy drives roadmap and licensing.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Three editions: Community, Professional, Enterprise | Clear ladder | Matrix maintenance |
| B. Single edition + à la carte modules only | Flexible quoting | Harder product marketing |
| C. Two editions only | Simpler | Leaves SME/enterprise gap |

**Final Decision**  
**Alternative A** — **Community / Professional / Enterprise** with feature matrix enforced per **ADR-009**.

**Impact**  
- Sales and onboarding (WF-PF-001/003) assign edition + subscription.  
- AI/API Gateway primarily Enterprise (Phase 4).

---

### ADR-014 — Docker + Azure / Linux VPS Hosting Model

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-014 |
| **Date** | 2026-07-30 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture, DevOps |
| **Related Documents** | ELU-SAD-001, ELU-CHR-001 |

**Context**  
Need portable deployment for early customers and later cloud scale.

**Reason**  
Avoid lock-in while supporting Azure growth path.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. Docker + Nginx; host on Linux VPS or Azure | Portable; cost-flexible | Self-managed ops on VPS |
| B. Azure App Service only | Managed | Harder local/VPS parity |
| C. Kubernetes from day one | Scale-ready | Overkill for v1 |

**Final Decision**  
**Alternative A** — **Docker** containers behind **Nginx**; deploy to **Linux VPS** and/or **Azure**; CI/CD via **GitHub Actions**. Kubernetes deferred until scale justifies a new ADR.

**Impact**  
- Same images promote across environments.  
- Secrets and TLS terminate at Nginx / platform edge.

---

### ADR-015 — Dual Tenant Isolation: Repository Filters + PostgreSQL RLS

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-015 |
| **Date** | 2026-08-06 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture, Tech Lead, Security |
| **Related Documents** | ELU-ADR-001 (ADR-001), ELU-SAD-001, ELU-DEV-001, ELU-EFS-001, ELU-DDD-*, ELU-TST-*, ELU-SEC-001 |

**Context**  
ADR-001 chose shared-DB + `tenant_id` but left PostgreSQL RLS as “where adopted.” EFS NFRs (e.g. NFR-SAL-004, NFR-FIN-005) already require RLS. Ambiguity would cause inconsistent implementations and isolation defects (**RSK-001**).

**Reason**  
Enterprise multi-tenant SaaS needs a single, binding isolation contract before schema freeze and coding sprints.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. App/repo filters only | Faster to ship | One missed filter = cross-tenant leak |
| B. PostgreSQL RLS only | Strong DB guarantee | Easy to forget SET LOCAL; harder to debug; Platform Admin paths awkward |
| C. Dual enforcement (repo filters + RLS) | Defense-in-depth; matches EFS NFRs | Slightly more migration/ops discipline |

**Final Decision**  
**Alternative C — Dual enforcement (mandatory for all tenant-scoped tables):**

1. **Application layer (primary):** Every repository query filters `tenant_id` from the JWT claim (never from client body). Platform Admin cross-tenant APIs use an explicit platform context and are audited.  
2. **Database layer (defense-in-depth):** Enable PostgreSQL **RLS** on every tenant-scoped table. Policies compare `tenant_id` to `current_setting('app.tenant_id', true)::uuid`.  
3. **Session binding:** FastAPI middleware / DB session begin sets `SET LOCAL app.tenant_id = '<uuid>'` for tenant requests.  
4. **Bypass role:** A dedicated DB role (e.g. `elu_platform_admin`) may use `BYPASSRLS` **or** policies that allow when `current_setting('app.platform_context', true) = 'true'`. Bypass is only for Platform Admin jobs and migrations; every use is audited.  
5. **Platform-global tables** (`edition`, `permission`, `feature_catalogue`, etc.): no RLS; no `tenant_id`.  
6. **Isolation tests:** Mandatory in **ELU-TST-*** (`tests/isolation/`) — cross-tenant GET returns 404; JWT spoof rejected; Platform Admin boundary verified.

**Impact**  
- Alembic migrations must enable RLS + create policies when adding tenant tables (**ELU-DDD-*** / **ELU-ERD-***).  
- **ELU-DEV-001**, **ELU-SAD-001**, and EFS NFR wording align to this ADR.  
- CI fails if isolation suite is skipped for a tenant entity API.

---

### ADR-016 — PF-003A Implements Dual Tenant Isolation (ADR-015)

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-016 |
| **Date** | 2026-08-06 |
| **Status** | Accepted |
| **Deciders** | Solution Architecture, Security, Tech Lead |
| **Related Documents** | ADR-015, ELU-DEV-001 §6A, ELU-SEC-001, ELU-TST-PF, ELU-PGR-001 |

**Context**  
Phase Gate ELU-PGR-001 found ADR-015 unimplemented in runtime (no RLS / no `SET LOCAL`). PF-004 Organization Management must not begin until dual isolation is delivered as **PF-003A**.

**Reason**  
Close CON §3 / ADR-015 P0 without redesigning baselined PF-001…003 business modules.

**Alternatives Considered**

| Alternative | Pros | Cons |
|-------------|------|------|
| A. App filters only (waive RLS) | Fast | Violates CON / ADR-015 |
| B. BYPASSRLS superuser app login | Simple | RLS never enforced |
| C. Non-bypass `elu_app` + GUC policies + Session.info rebind | Matches ADR-015; works with FORCE RLS | Requires SET ROLE + owner DDL path |

**Final Decision**  
**Alternative C — PF-003A delivery of ADR-015:**

1. Role `elu_app` (NOSUPERUSER, NOBYPASSRLS); request sessions `SET LOCAL ROLE elu_app`.
2. `ENABLE` + `FORCE ROW LEVEL SECURITY` + `tenant_isolation` policies on all tenant-scoped tables listed in `012_rls_pf003a.sql`.
3. Session GUCs: `app.tenant_id`, `app.platform_context` via `set_config(..., is_local=true)`; rebound on every `Session.after_begin` from `Session.info` (survives commit / FastAPI threadpool).
4. Platform Admin and auth bootstrap set `app.platform_context=true` (audited at API layer).
5. Platform-global tables (`edition*`, `feature_catalogue`, `permission`) remain without RLS.
6. Isolation suite in `tests/isolation/` is mandatory for release (`TC-PF-ISO-*`).
7. DDL applicators run under owner role (`owner_role()`), not `elu_app`.

**Impact**  
- PF-004 blocked until PF-003A RELEASE APPROVED.  
- TD-CRIT-01 / TD-CRIT-02 closed on release.  
- Does not reverse ADR-015; implements it.

---

### ADR-018 — PLATFORM_ADMIN CRM Permission Policy (PROPOSED — PENDING PRODUCT-OWNER DECISION)

| Field | Value |
|-------|-------|
| **Decision ID** | ADR-018 |
| **Date** | **PENDING** — record prepared 2026-11-12. The actual decision date must be supplied before acceptance and is deliberately not inferred. |
| **Status** | **Proposed** — draft; pending product-owner decision. Not Accepted; authorises no implementation. |
| **Deciders** | **PENDING** — product owner not supplied (not invented); human Architecture Review required per §5. |
| **Related Documents** | ADR-015, ADR-016, ELU-BFS-CRM, EFS-CRM, V1-PF-CRM, ELU-BFS-CPS, ELU-BFS-PF, ELU-SEC-001, ELU-DOC-001, ELU-AI-001, Cursor_Rules |

**Status of this record**
This is a **PROPOSED** governance record. It selects **no** option, authorises **no** implementation, and invents **no** authorizer, approval date, requirement ID or expiry date. Per §5 and the accepted-ADR immutability rule (`Documentation/Cursor_Rules.md:8`), only a human Architecture Review may move it to `Accepted`.

**Context**

1. PLATFORM_ADMIN holds **49 permissions, 14 of them CRM**. The 49-grain figure is **derived from seed code and corroborated once by a runtime `/auth/me` response (49 permissions)**; per-tenant runtime grant state remains **UNVERIFIED**. Derivation: 68-code catalogue (`Backend/app/db/seed.py:465-533`; CRM block `:512-530` = 15 codes) → provisioning grants the whole catalogue minus `customer.suspend` (`seed.py:1462-1464`; `FINANCE_ONLY_PERMISSIONS` `:1015`) → six PF matrices revoke unapproved PF grains (`seed.py:57, 79, 191, 259, 277-284, 388-393`). No CRM matrix exists, so the **14** CRM grains survive: `lead.create/read/update/convert/qualify/disqualify`, `customer.read/create/update`, `activity.read/create`, `opportunity.read/update/approve`.
2. The same 14 are re-granted on every startup: `_upgrade_crm_permissions` rebuilds them at `seed.py:1522-1527` and grants them to `PLATFORM_ADMIN`/`TENANT_ADMIN` at `seed.py:1535-1536`. Any revocation must also change this healing path or it is undone at next boot.
3. All four CRM CRUD matrices contradict the grant, stating Platform Admin = `✘ | ✔ (audit) | ✘ | ✘ | ✘` over `Create | Read | Update | Approve | Delete` — `Documentation/10-EFS-V1-Ready/V1-PF-CRM.md:812` (leads), `:1020` (opportunities), `:1230` (customers), `:1443` (activities); headers `:807, :1015, :1225, :1438`. Duplicated verbatim at `ProjectStartupfiles/ELU-EFS-001-Enterprise-Functional-Specification.md:2437, 2968, 3457, 3952`.
4. `Read ✔ (audit)` is undefined. The parenthetical is the only qualifier; no legend exists in any document (8 occurrences, all the identical cell). Candidate readings: (i) audit-trail only, (ii) audited business-record read.
5. Neither requirement baseline grants anything either way: `ELU-BFS-CRM.md` contains zero "Platform Admin" matches, and `EFS-CRM.md:103-115` (Ownership Matrix) gives Platform Admin no CRM role — its only appearance is "Escalation Owner" for Tenant Admin.
6. Platform policy leans restrictive: `ELU-BFS-CPS.md:879` (BR-CPS-086 "Platform Admin cannot read tenant business audit PII"); `ELU-BFS-PF-Platform-Foundation.md:2896` (cross-tenant audit viewed "in a separate platform audit store"); `ELU-ADR-001` ADR-015/ADR-016 (platform bypass "audited at API layer"); `ELU-SEC-001-Threat-Model.md:56,66` (T-13, audited `platform_context`).
7. No CRM read is audited today: the only CRM audit call is `customer.suspended` (`Backend/app/services/crm/customer_service.py:414-431`); no audit-read API exists (`Backend/app/api/v1/router.py:28-51`); `write_audit_event` only stages the row (`db.add(event)` at `Backend/app/services/pf/audit_service.py:40`, no `commit()` in `:16-46`); `audit_event` has no `request_id` column (`Backend/app/models/pf/entities.py:227-262`).
8. Isolation reality: the current application-level tenant boundary is the repository filter (26 `tenant_id ==` predicates across `Backend/app/repositories/crm/*.py`). `Backend/app/core/deps.py:55-58` binds `app.platform_context=true` for PLATFORM_ADMIN, bypassing the RLS policy at the database layer. Database-enforced isolation for platform-admin sessions must therefore be independently verified and tested; nothing in this record asserts that it is currently effective.
9. Role-level side doors exist — seven lookup mutation gates and an approval-role set (below).

**CRM permission surface enforced by routes**

40 operations across 26 paths (40 route decorators in `Backend/app/api/v1/crm/{leads,opportunities,customers,activities,lookups}.py`):

| Grant | Operations enabled | Evidence |
|---|---|---|
| `lead.read` | 2 GETs | `leads.py:29, 61` |
| `lead.create` | create | `leads.py:48` |
| `lead.update` | PUT, PATCH, DELETE | `leads.py:75, 89, 160` |
| `lead.convert` / `lead.qualify` / `lead.disqualify` | transitions | `leads.py:102, 131, 145` |
| `opportunity.read` | list, detail, stages list | `opportunities.py:60, 96`; `lookups.py:153` |
| `opportunity.update` | create, PUT, PATCH, stage, DELETE, stage admin | `opportunities.py:81, 110, 130, 150, 165`; `lookups.py:172, 187, 203` |
| `opportunity.approve` | close-won via PATCH (`can_close_won`) | `opportunities.py:116, 136`; `rbac.py:67-70` |
| `customer.read` | list, detail | `customers.py:44, 93` |
| `customer.create` | create, duplicate-check (read-shaped) | `customers.py:63, 80` |
| `customer.update` | PATCH, contacts, addresses | `customers.py:107, 187, 205` |
| `activity.read` | activities, timeline, `/crm/lookups`, activity-types, activity-outcomes | `activities.py:25, 47`; `lookups.py:37, 50, 101` |
| `activity.create` | log activity + lookup mutations | `activities.py:62`; `lookups.py:69, 85, 122, 138` |
| `customer.suspend` | suspend (also requires FINANCE_USER) | `customers.py:145`; `rbac.py:36-48` |

Seven lookup mutation role gates (`Backend/app/services/crm/lookup_service.py:112, 140, 178, 209, 243, 277, 300`) admit only roles `("TENANT_ADMIN", "PLATFORM_ADMIN", "SALES_MANAGER")` — PLATFORM_ADMIN is admitted by role name above and beyond any grain; all seven are CRM-only.

Approval-role set: `SALES_MANAGER_ROLES = {"SALES_MANAGER", "TENANT_ADMIN", "PLATFORM_ADMIN"}` (`Backend/app/core/rbac.py:13-15`). Consumers: `can_close_won` (`:67-70`, used at `opportunities.py:116, 136`) and `can_view_pipeline` (`:73-77`, used at `opportunities.py:39`). `require_sales` (`rbac.py:54-57`) and `require_sales_manager` (`:59-64`) have no call sites or imports anywhere in `Backend/app/`, as is `SALES_ROLES` (`:10-12`), used only by the dead `require_sales`. Removing PLATFORM_ADMIN from these sets therefore changes CRM only (pipeline visibility and close-won), with no non-CRM effect.

**Reason**
An Accepted ADR (ADR-015/ADR-016) mandates audited platform-context access that has never been implemented, while the four EFS matrices and the seeded grants disagree about what Platform Admin may do in CRM. The deviation is ungoverned and untested, and the platform tenant's authority over CRM data is an artefact of generic whole-catalogue seeding rather than a recorded decision.

**Alternatives Considered**

| Alternative | Definition | Security | Tests / demo | Seed or matrix changes | Audit | Requirement wording |
|---|---|---|---|---|---|---|
| A — Audit-trail only | No CRM business-record reads; no CRM mutations; only a separately specified, audited cross-tenant audit-trail capability | Strictest; consistent with BR-CPS-086 and EFS-CRM's no-role matrix; removes the `platform_context` path for CRM data | **42 files reference `platform_admin_select` (95 occurrences): 41 test modules plus `conftest.py`** (total fixture usage, not a CRM-specific subset); CRM suites use the platform admin as the author (`tests/isolation/test_crm_tenant_isolation.py:33-51`, `tests/test_l2c_crm_slice.py:26-42`); `tests/test_crm_customer_suspend_grants.py:147` asserts PLATFORM_ADMIN holds `customer.read`; EIIP001 demo loses CRM | New `CRM_PERMISSION_MATRIX` with an empty platform tuple, wired into `seed.py:1467-1477`, `:934-946`, `:1630-1641`; healing path `seed.py:1522-1527, 1535-1536`; remove PLATFORM_ADMIN from the seven lookup role gates and from `SALES_MANAGER_ROLES` | Platform audit-trail read surface does not exist (`router.py:28-51`) and would have to be built, with tenant-independent retention | Audit-trail capability has **no requirement ID**; a new requirement would be needed (not allocated) |
| B — Tenant-scoped audited read | CRM reads within the JWT-bound tenant only; every qualifying read audited; no create/update/approve/convert/qualify/disqualify/delete | Repository filtering is the current application-level boundary; **audit logging provides accountability and detection, not access prevention**; database-enforced isolation must be independently verified and tested | Read paths stay green (incl. `tests/isolation/test_crm_platform_admin_isolation.py`); writer paths (`test_l2c_crm_slice.py`, `test_crm_close_won_activity.py`, isolation author fixtures) and the duplicate-check call must migrate to `TENANT_ADMIN` | Matrix with the four read grains; revoke the 10 mutation grains; fix `seed.py:1522-1527, 1535-1536`; remove PLATFORM_ADMIN from the seven lookup role gates | Router-level dependency that no-ops unless `platform_context`; must write and **commit** (writer only stages, `audit_service.py:40`) and carry `request.state.request_id` (`app/middleware/request_id.py:10-14`); needs tenant-attribution and fail-open/fail-closed decisions | Requires a formal requirement change: matrix cell wording plus a new audit obligation (ID not allocated) |
| C — Explicit governed exception | Retain current CRM access; document an approved exception to all four matrices with scope, authorizer, audit obligation and review/expiry | Weakest; converts accidental drift into governed risk; residual exposure includes customer/opportunity mutation, lead conversion and close-won via the role set | Zero breakage; EIIP001 workflows unchanged | None | If adopted: existing commits make integration less invasive, but audit-event creation, transaction consistency (event and mutation committing or rolling back together) and failure behaviour still require implementation and testing | Requires an explicit superseding decision record; matrix cells may remain byte-identical |

**Option A — expected route impact (post-implementation, not measured).** The expected result is that all 40 CRM operations across 26 paths return 403; every route currently carries a grain gate. This is a prediction subject to regression verification **after** the permission matrix, the startup healing path (`seed.py:1522-1527, 1535-1536`) and the role-based exceptions (`lookup_service.py:112,140,178,209,243,277,300`; `rbac.py:13-15`) are changed. Unaffected by design (verified): authentication (`auth.py`); platform tenant/subscription/edition APIs (role-based `require_platform_admin`, e.g. `services/pf/tenant_service.py:494`, `subscription_service.py:745`, `edition_service.py:498`); PF organization/branch/user/settings routes (`seed.py:57, 79, 277-284, 388-393`); SAL/FIN/PRJ routes (`router.py:43-50`). There is no audit-trail API to exempt; any future audit-trail requirement, authorization model and retention are **UNVERIFIED**.

**Option B — boundary exceptions that must be stated in any implementation.**

1. `GET /crm/opportunities/pipeline` is conditional: `can_view_pipeline` requires `opportunity.read` **and** (`opportunity.approve` **or** role in `SALES_MANAGER_ROLES`) — `rbac.py:73-77`, called at `opportunities.py:39`. B revokes `opportunity.approve`, so pipeline access survives only while PLATFORM_ADMIN remains in `SALES_MANAGER_ROLES`; if D5 removes it, pipeline becomes 403.
2. `POST /crm/customers/duplicate-check` is read-shaped but gated by `customer.create` (`customers.py:80`), so it is **expected to return 403** under B's four read grains although it writes nothing. This is a derived prediction from the gate, **not an executed test result**.
3. Opportunity endpoints additionally require the `CRM_OPPORTUNITY` edition feature (`opportunities.py:29`; `customers.py:162`). The runtime feature state of the platform tenant is **UNVERIFIED**.

**Option C — exception scope must be complete.** Any approved exception must explicitly cover all three privilege surfaces: (1) all **14** seeded CRM permission grains (`seed.py:1462-1464`; healed at `:1522-1527, 1535-1536`); (2) all **seven** CRM lookup role gates (`lookup_service.py:112, 140, 178, 209, 243, 277, 300`); (3) PLATFORM_ADMIN's inclusion in `SALES_MANAGER_ROLES` (`rbac.py:13-15`). Describing the exception as covering only the 14 grains would leave two undocumented privileges outside governance.

**Final Decision**
**PENDING — NOT DECIDED.** No option is selected by this record. Selection requires the product owner to resolve D1–D5 and to supply the fields in D6–D8. Per §5 this record cannot move to `Accepted` without human Architecture Review, and per §7 no agent may change its Status or Final Decision. No application-feature implementation may begin until human approval after `ELU-GOV-VAL-001` (`Documentation/Cursor_Rules.md:15`).

**Decisions required (D1–D8)**

| ID | Decision required | Owner |
|---|---|---|
| D1 (was Q1) | What does `Read ✔ (audit)` mean — audit-trail only, audited business-record read, or other? | Product Owner (+ Architecture) |
| D2 (was Q2) | Are the four EFS CRM CRUD matrices authoritative over the implementation? | Product Owner / BA |
| D3 (was Q3) | Is PLATFORM_ADMIN intended to have CRM business-record access (none / read / read+write)? | Product Owner |
| D4 (was Q4a) | Are the seven lookup-mutation role gates (`lookup_service.py:112,140,178,209,243,277,300`) intentional? | Product Owner / Architecture |
| D5 (was Q4b) | Is PLATFORM_ADMIN's inclusion in `SALES_MANAGER_ROLES` (`rbac.py:13-15`) intentional? | Product Owner / Architecture |
| D6 | Option selection: A, B or C — not selected by this record | Product Owner |
| D7 | Named authorizer and actual decision date — not supplied, not inferred | Product Owner |
| D8 | Requirement ID for the audit obligation (only if A or B) — not allocated | Product Owner / PMO |

**Impact**
- Undecided (status quo): the seeded 14 CRM grains, the seven role gates and the `SALES_MANAGER_ROLES` membership stand ungoverned against four EFS matrices; the "audited platform context" obligation of ADR-015/ADR-016 is unmet; no test pins either behaviour; the only effective tenant boundary for platform-admin CRM reads is the application repository filter.
- A or B: requires changes to both the provisioning path (`seed.py:1462-1464`) and the healing path (`seed.py:1522-1527, 1535-1536`), plus test-fixture migration and a new audit requirement; expected 403/read behaviour must be confirmed by regression after those changes.
- C: no code change; requires a reviewable, time-bound exception covering all three privilege surfaces above (note: `core.role_permission` has no validity columns, so "expiry" is a review obligation, not an enforced control).

**Risks**
- Selecting no option preserves a contradiction between seeded grants and four approved-looking matrices.
- Options A and B touch a startup healing path that re-grants on every boot; a partial change would silently revert.
- Removing PLATFORM_ADMIN from `SALES_MANAGER_ROLES` also withdraws pipeline visibility and close-won semantics, which is a behaviour change beyond permission counts.
- Audit logging is accountability only; treating it as a substitute for database-enforced isolation would misstate the control.
- Any change to the four matrix cells must also consider the four duplicated copies in `ProjectStartupfiles/ELU-EFS-001-Enterprise-Functional-Specification.md`.

**Consequences / Follow-ups**
1. Register the outcome in §3 and set Status per §5 once decided; resolve the separate PMO follow-ups F-1 and F-2 below.
2. Record the selected option, named authorizer and decision date — none are invented in this record.
3. If A or B is selected, allocate a requirement ID for the audit obligation and specify the audit-trail surface (currently non-existent, `router.py:28-51`).
4. Implement the matrix + healing-path change and the regression tests enumerated per option; verify actual route responses after implementation rather than assuming them.
5. If C is selected, record scope over all 14 grains, all seven role gates and the `SALES_MANAGER_ROLES` membership, plus audit obligation, review and expiry conditions.
6. Independently verify and test database-level tenant isolation for platform-admin sessions — audit logging cannot substitute for it.
7. Confirm the runtime `CRM_OPPORTUNITY` edition state for each tenant that relies on CRM opportunity routes (currently UNVERIFIED).

**Separate PMO follow-ups (not part of this decision)**

| ID | Finding | Evidence |
|---|---|---|
| F-1 | ADR-017 exists only as a standalone file and is **not registered** in this log's §3 index or version history | `Documentation/ADR-017-PF011-Specification-Reconciliation.md:1-8`; this log contains no `ADR-017` reference |
| F-2 | Version drift: `ELU-DOC-001` registers `ELU-ADR-001` at v1.2 while this document's header states v1.3 | `Documentation/ELU-DOC-001-Documentation-Master-Index.md:124` vs header `**Version:** 1.3` |

---

## 5. How to Add a New Decision

1. Allocate next **ADR-NNN** in §3 Index.  
2. Copy the template in §2; fill all fields.  
3. Set Status = `Proposed` until Architecture Review accepts it.  
4. On acceptance, set Status = `Accepted` and update **ELU-DOC-001** / **ELU-SAD-001** summary if needed.  
5. If replacing an old decision, mark old ADR `Superseded` and link the new ID.

---

## 6. Cross-Reference from Other Documents

When a design choice is explained elsewhere, cite the Decision ID:

> Tenancy uses shared DB isolation per **ADR-001** (see **ELU-ADR-001 – Architecture Decision Log**).

Authority chain: **ELU-CON-001** (Frozen) → this Decision Log → domain specs. AI assistants: **ELU-AI-001**, **Cursor_Rules.md**.

---

## 7. AI Immutability & Supersession (Binding)

**Purpose:** Prevent Cursor / other AI sessions from silently reversing **Accepted** decisions.

| Rule | Binding |
|------|---------|
| **Accepted = law** | An Accepted ADR may not be “reinterpreted,” weakened, or ignored in generated code or docs |
| **No silent reversal** | Agents must not change Status, Final Decision, or enforcement wording without human Architecture Review |
| **Supersession only** | To change course: allocate next **ADR-NNN**, Status = Proposed → Accepted; mark prior ADR **Superseded** with successor ID |
| **Clarify vs reverse** | Editorial clarification (e.g. ADR-001 pointing to ADR-015) is allowed; removing dual RLS or shared-DB tenancy without a new ADR is **forbidden** |
| **Conflict handling** | If a BFS/EFS fragment conflicts with an Accepted ADR, **ADR wins**; open a BA/Architecture ticket — do not “fix” by inventing a third behaviour |
| **Mandatory citations** | Plans and PRs that touch tenancy, auth, packaging, soft-delete, or workflow SoT must cite the Decision ID |

### 7.1 High-sensitivity Accepted decisions (do not weaken)

| Decision ID | Must not silently drop |
|-------------|------------------------|
| ADR-001 / ADR-015 | Shared DB + `tenant_id` **and** dual repo + RLS enforcement |
| ADR-004 | JWT + Refresh model; SSO/MFA edition gating |
| ADR-006 | Soft delete + `version_no` |
| ADR-009 / ADR-013 | Edition matrix packaging |
| ADR-011 | EFS as workflow implementation SoT |

Governance validation: **ELU-GOV-VAL-001**.

---

*© Euphoria Infotech (I) Limited — ELU-ADR-001 Architecture Decision Log*
