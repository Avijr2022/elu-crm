# Changelog

All notable E-LinkUp implementation milestones.

## [Phase Gate] — 2026-08-06 — AWAITING HUMAN APPROVAL

### Added
- ELU-PGR-001 Phase Gate Review (PF-001…003)
- ELU-TD-002 Technical Debt Register (Critical RLS / isolation)
- ELU-EHC-001 Enterprise Health Card v2.0
- ELU-MSL-001 §3.3 Progress Dashboard
- Risk updates RSK-021…023

### Notes
- **PF-004 Organization** blocked until Phase-Gate Approval
- P0: ADR-015 dual RLS + isolation tests
- No baselined PF-001…003 code modified in this gate

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
