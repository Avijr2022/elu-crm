# E-LinkUp Technical Debt Register — Phase Gate (PF-001…003)
**Document ID:** ELU-TD-002  
**Version:** 1.1  
**Status:** Approved (Phase Gate artefact; PF-003A update)  
**Date:** 2026-08-06  
**Supersedes/Extends:** ELU-TD-001  
**Related:** ELU-PGR-001, ELU-RSK-001, ELU-CON-001, ELU-QA-PF003A  

---

## 1. Critical Debt

| ID | Item | Module | Impact | Action | Status |
|----|------|--------|--------|--------|--------|
| TD-CRIT-01 | PostgreSQL RLS + `SET LOCAL app.tenant_id` (ADR-015 / CON §3) | Cross-PF | Tenant isolation | Delivered as **PF-003A** | **Closed** — tag `Phase-2-PF003A` |
| TD-CRIT-02 | Automated tenant isolation test suite (`TC-PF-ISO-*`) | Cross-PF / QA | Prove dual isolation | `tests/isolation/` | **Closed** — tag `Phase-2-PF003A` |

### New hardening (Major)

| ID | Item | Action |
|----|------|--------|
| TD-MAJ-07 | App DB login still superuser; relies on `SET ROLE elu_app` | Prefer dedicated non-superuser connection in prod |

---

## 2. Major Debt

| ID | Item | Module | Action |
|----|------|--------|--------|
| TD-MAJ-01 | Permission-grain RBAC not seeded (`*.create/read/...`) | PF-009 | Role-code gate interim |
| TD-MAJ-02 | Notification engine not wired (NTF-PF-*) | CPS | Stub until CPS-003 |
| TD-MAJ-03 | Subscription expire scheduler (BR-PF-024 SLA) | PF-003 / CPS | Manual expire exists |
| TD-MAJ-04 | BR-PF-022 on user create | PF-008 | Bind at Users |
| TD-MAJ-05 | No Flutter automated tests | Frontend | Widget smoke suite |
| TD-MAJ-06 | Governance packs uncommitted / unsynced in git working tree | Docs | Commit under CON |

---

## 3. Minor Debt

| ID | Item | Action |
|----|------|--------|
| TD-MIN-01 | List API client-driven sort params | Add when UI needs |
| TD-MIN-02 | Idempotency-Key only on tenant POST | Extend to other POSTs |
| TD-MIN-03 | Dark mode ThemeData | Add dark ColorScheme |
| TD-MIN-04 | Accessibility Semantics labels | Audit primary actions |
| TD-MIN-05 | Dedicated SQL rollback packs | Pair with migrate_* |
| TD-MIN-06 | Edition deprecate Flutter control | Optional UI |
| TD-MIN-07 | HTTP_422 deprecation warnings (Starlette) | Upgrade exception constants |

---

## 4. Future Enhancements

- Graphify architecture visualisation (if mandated)
- Separate Desktop/Mobile BFF only if ADR revises single-API model
- Full branding / localization / security policy CRUD (PF-002 deferred + PF-011)
- Report packs RPT-PF-001…003
- Celery/Redis async (ADR-008)

## 5. Refactoring Suggestions

- Extract shared `require_platform_admin` / pagination helpers
- Unify list/search/export router patterns via base factory
- Centralise status CHECK enum constants in Python + SQL

## 6. Performance Improvements

- Composite indexes already present for tenant/status; review EXPLAIN on large tenant lists at scale
- Flutter list virtualization when catalogues exceed hundreds of rows

## 7. Security Improvements

- Implement RLS policies (critical)
- Rotate seed/default secrets out of compose for non-local
- Permission checks beyond role_code
- Security headers / rate limit at gateway

## 8. Maintainability Improvements

- Commit Documentation packs into repo baseline
- OpenAPI export in CI
- Migration checksum verification job

---

**Debt Score (Phase Gate):** **MEDIUM** (two Critical items dominate)  
**Rule:** Critical debt does not unlock locked PF-001…003 code without CR/ADR.

---

*© Euphoria Infotech (I) Limited — ELU-TD-002*
