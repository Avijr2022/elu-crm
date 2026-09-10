# E-LinkUp Threat Model
**Document ID:** ELU-SEC-001  
**Version:** 1.1  
**Status:** Approved  
**Classification:** Internal Confidential  
**Method:** STRIDE (multi-tenant SaaS focus)  
**Related Documents:** ELU-SAD-001, ELU-ADR-001 (ADR-001, ADR-004, ADR-009, ADR-015), ELU-DEV-001, ELU-RSK-001, ELU-TST-*, ELU-DOC-001  
**Example Tenant:** Euphoria  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Security / Solution Architecture | Baseline threat model for build-ready multi-tenant CRM |
| 1.1 | 2026-08-06 | EIIP / Security | PF-003A implements ADR-015/016; residual risks updated |

---

## 1. Scope

In scope: authentication, tenancy isolation, RBAC, edition gating, document storage, CRM/PF APIs, Flutter clients.  
Out of scope (later): full pen-test report, vendor SOC evidence packs, physical facility threats.

---

## 2. Assets

| Asset | Sensitivity |
|-------|-------------|
| Tenant business data (Lead, Customer, Invoice…) | High |
| Credentials / refresh tokens / MFA secrets | Critical |
| Audit trails | High (integrity) |
| Edition / subscription entitlement | Medium–High |
| MinIO documents | High |

---

## 3. STRIDE Summary

| ID | Threat | Category | Likelihood | Impact | Mitigation | Residual |
|----|--------|----------|------------|--------|------------|----------|
| T-01 | Cross-tenant IDOR (guess UUID) | Information Disclosure | L | H | Dual isolation **ADR-015/016** live (RLS FORCE + repo filters); 404; isolation tests | L |
| T-02 | Client sends forged `tenant_id` | Tampering / Elevation | L | H | Strip from DTOs; JWT-only; RLS WITH CHECK | L |
| T-03 | Missed repository filter | Information Disclosure | L | H | RLS defense-in-depth (`elu_app` + GUCs); PR checklist | L |
| T-04 | JWT theft (XSS / device) | Spoofing | M | H | Short access TTL; refresh rotation; secure storage; HTTPS | M |
| T-05 | Refresh token replay | Spoofing | L | H | Rotate on use; revoke on logout; session table | L |
| T-06 | Brute-force login | Denial / Spoofing | M | M | Lockout + Argon2id (**ADR-004**) | L |
| T-07 | Edition bypass via API | Elevation | M | H | Server-side edition gate **ADR-009**; contract tests | L |
| T-08 | Privilege escalation (role assign) | Elevation | M | H | RBAC on role APIs; audit; Tenant Admin cannot grant Platform Admin | L |
| T-09 | Soft-delete unique bypass | Tampering | L | M | Partial unique indexes | L |
| T-10 | MinIO object key guessing | Information Disclosure | M | H | Tenant-prefixed keys; signed URLs; metadata RBAC | L |
| T-11 | Mass assignment of status/owner | Tampering | M | M | Explicit PATCH DTOs; state machine guards | L |
| T-12 | Export PII leakage | Information Disclosure | M | H | `export` / `export.full` permissions; masking **ELU-CMP-001** | M |
| T-13 | Platform Admin misuse | Elevation | L | H | Audited platform_context; break-glass procedure | M |
| T-14 | UI-only security | Elevation | M | H | Never rely on hide; API enforces (**RSK-008**) | L |

---

## 4. Trust Boundaries

```text
Internet → Nginx/TLS → FastAPI → (JWT + tenant context) → PostgreSQL RLS (elu_app)
                                         └→ MinIO (presigned)
Platform Admin path → audited app.platform_context=true (policy bypass, not BYPASSRLS)
```

### 4.1 PF-003A control status (2026-08-06) — **RELEASE APPROVED** (`Phase-2-PF003A`)

| Control | Status |
|---------|--------|
| FORCE RLS on tenant-scoped tables | **Baselined** (ADR-016 / ELU-REL-PF003A) |
| `SET LOCAL` / `set_config` `app.tenant_id` | **Baselined** |
| Platform Admin `app.platform_context` | **Baselined** |
| Isolation suite `tests/isolation/` | **Baselined** (43/43 ×2) |
| Production DB login as non-superuser | **Recommended hardening** (TD-MAJ-07) |

---

## 5. Mandatory Security Tests (link ELU-TST)

| Test theme | TC pattern |
|------------|------------|
| Cross-tenant GET/PUT | TC-*-ISO-01 |
| Body tenant_id ignored | TC-*-ISO-02 |
| Edition 403 | TC-*-EDN-01 |
| RBAC 403 | TC-*-RBAC-01 |
| Soft-deleted hidden | TC-*-ISO-03 |

---

## 6. Review Cadence

Architecture + Security review before each external pilot; update this document when new trust boundaries appear (webhooks, SSO, customer portal).

---

*© Euphoria Infotech (I) Limited — ELU-SEC-001*
