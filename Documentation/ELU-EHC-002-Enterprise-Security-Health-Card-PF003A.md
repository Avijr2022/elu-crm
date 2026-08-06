# Enterprise Security Health Card — PF-003A Tenant Isolation (Published)
**Document ID:** ELU-EHC-002  
**Version:** 1.1  
**Date:** 2026-08-06  
**Module:** PF-003A — Enterprise Tenant Isolation  
**Status:** **RELEASE APPROVED**  
**Baseline:** `Phase-2-PF003A`  
**Related:** ELU-QA-PF003A, ELU-REL-PF003A, ADR-015, ADR-016, ELU-SEC-001, ELU-PGR-001  

---

## Traffic Light

### 🟢 Green — RELEASE APPROVED

Dual RLS (CON §3 / ADR-015) is baselined. Platform security posture upgraded for Phase-2 PF slice.

---

## RLS Metrics

| Metric | Value |
|--------|-------|
| Tenant-scoped tables with FORCE RLS | **15** |
| Policies (`tenant_isolation`) | **15** |
| Platform-global tables without RLS | edition*, feature_catalogue, permission |
| App role | `elu_app` (NOSUPERUSER, NOBYPASSRLS) |
| Session GUCs | `app.tenant_id`, `app.platform_context` |
| Rebind strategy | `Session.info` + `after_begin` (survives commit) |
| Platform Admin bypass | `app.platform_context=true` (policy path) |

### Tables under RLS
`core.tenant`, `tenant_contact`, `tenant_address`, `tenant_status_history`, `tenant_settings`, `organization`, `users`, `subscription`, `subscription_history`, `subscription_usage`, `role`, `idempotency_key`, `audit.audit_event`, `crm.lead`, `crm.opportunity`

---

## Isolation Test Results

| Suite | Result |
|-------|--------|
| Isolation (`tests/isolation/`) | **11/11 PASS** |
| PF-001…003 regression | **32/32 PASS** |
| Combined consecutive runs | **43/43 × 2** |

| TC | Result |
|----|--------|
| TC-PF-ISO-01 Cross-tenant IDOR | PASS |
| TC-PF-ISO-02 Foreign tenant_id ignored | PASS |
| TC-PF-ISO-03 Soft-deleted user | PASS |
| TC-PF-ISO-04 Platform Admin list | PASS |
| Fail-closed empty GUC | PASS |
| JWT tenant spoof | PASS |
| SET LOCAL GUC visible | PASS |

---

## Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Constitution Compliance (CON §3) | **A** | Dual repo + RLS enforced |
| ADR-015 / ADR-016 | **A** | Implemented and baselined |
| Database RLS | **A** | FORCE + policies |
| Session binding | **A** | LOCAL GUCs + role |
| Platform Admin bypass | **A** | Audited GUC path |
| Isolation coverage | **A** | Automated suite |
| Regression | **A** | Locked modules green |
| Prod DB login hardening | **B+** | Prefer non-superuser (TD-MAJ-07) |
| **Overall Security Health** | **A-** | **RELEASE APPROVED** |

---

## Platform Security Status (Phase-2 PF slice)

| Layer | Status |
|-------|--------|
| PF-001 Editions (platform-global) | 🟢 RELEASE APPROVED |
| PF-002 Tenants | 🟢 RELEASE APPROVED + RLS on children |
| PF-003 Subscriptions | 🟢 RELEASE APPROVED + RLS |
| PF-003A Isolation | 🟢 **RELEASE APPROVED** |
| Auth JWT + Argon2 | 🟢 Active |
| Permission-grain RBAC | 🟡 Role-code gate (PF-009) |
| NTF / expire scheduler | 🟡 Deferred debt |

---

## Debt Closed

| ID | Status |
|----|--------|
| TD-CRIT-01 RLS + SET LOCAL | **Closed** — tag `Phase-2-PF003A` |
| TD-CRIT-02 Isolation tests | **Closed** — tag `Phase-2-PF003A` |

---

## Sign-off

| Role | Decision |
|------|----------|
| QA | **PASS** |
| Security | **PASS** |
| Human Release Authority | **RELEASE APPROVED: YES** |

```text
PF-003A ENTERPRISE TENANT ISOLATION — RELEASE APPROVED: YES
BASELINE: Phase-2-PF003A
NEXT: PF-004 Organization Management (approved to start)
```

---

*© Euphoria Infotech (I) Limited — ELU-EHC-002 v1.1*
