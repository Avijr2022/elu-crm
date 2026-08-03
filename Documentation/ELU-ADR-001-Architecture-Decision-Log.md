# E-LinkUp Architecture Decision Log
**Document ID:** ELU-ADR-001  
**Document Name:** Architecture Decision Log (ADL)  
**Version:** 1.0  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Enterprise Solution Architecture  
**Document Owner:** Solution Architecture / PMO  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-DOC-001, ELU-DF-001, ELU-SAD-001, ELU-EFS-001, ELU-CHR-001, ELU-SEH-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP / Solution Architecture | Initial Decision Log; expanded ADR-001…009 from ELU-SAD-001; added ADR-010…014 |

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
**Alternative A** — Shared PostgreSQL database with mandatory `tenant_id` on tenant-scoped tables; enforce isolation in repository/middleware (and RLS where adopted). Platform-global masters (e.g. `edition`) may omit tenant scope.

**Impact**  
- Every BFS/EFS/DDD artefact must mark tenant scope.  
- Isolation tests are mandatory Acceptance Criteria.  
- Revisit if a regulated customer requires physical isolation (possible Enterprise add-on later).

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

---

*© Euphoria Infotech (I) Limited — ELU-ADR-001 Architecture Decision Log*
