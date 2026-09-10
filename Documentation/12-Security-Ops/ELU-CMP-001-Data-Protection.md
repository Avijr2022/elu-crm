# E-LinkUp Data Protection & Retention
**Document ID:** ELU-CMP-001  
**Version:** 1.0  
**Status:** Approved  
**Document Owner:** Compliance / BA  
**Related Documents:** ELU-BFS-PF (PF-010), ELU-EDM-001, ELU-SEC-001, ELU-OPS-001, ELU-EFS-001, ELU-DOC-001  
**Alignment:** DPDP Act (India) principles + GDPR-style portability/erasure concepts  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Compliance | Baseline retention, PII, offboarding for multi-tenant CRM |

---

## 1. Personal Data Categories

| Category | Examples | Systems |
|----------|----------|---------|
| Identity | Name, email, phone on Lead/Contact/User | PostgreSQL |
| Commercial | GSTIN, PAN, addresses | PostgreSQL |
| Auth | Password hashes, MFA secrets | PostgreSQL (restricted) |
| Documents | Attachments | MinIO + metadata |
| Audit | Actor email, IP | audit_event |

---

## 2. Retention by Edition (Audit)

| Edition | Audit retention | Source |
|---------|-----------------|--------|
| Community | 90 days | ELU-EDM-001 / BFS-PF |
| Professional | 1 year | |
| Enterprise | 7 years | |

After retention: purge or cold-archive per `audit_retention_policy`. Legal hold freezes purge (Enterprise future).

---

## 3. Soft Close vs Erasure

| Scenario | Behaviour |
|----------|-----------|
| Tenant OFFBOARDING → CLOSED | Soft-close; no hard delete of masters (**REQ-PF-012**) |
| Retention elapsed → ARCHIVED | Platform read-only historical |
| Right-to-erasure request | Anonymise PII on contacts/users where **no** immutable finance/tax lock; document exceptions |
| Issued invoices / payments | **Immutable**; do not erase amounts/tax IDs required by law |

---

## 4. Export & Masking

| Permission | Behaviour |
|------------|-----------|
| `*.export` | Export with PII masked (email/phone partial) |
| `*.export.full` | Unmasked; audited |
| Portability package | Full tenant export reserved for **v2.0**; API placeholder may exist |

---

## 5. Access Control

- Least privilege RBAC; field-level masking in API serializers where required.
- Logs must not contain passwords, tokens, or full card data (**ELU-DEV-001**).

---

## 6. Offboarding Checklist

1. Suspend logins  
2. Notify Tenant Admin  
3. Export (if contracted)  
4. Retention countdown  
5. Anonymise / archive per policy  
6. Platform audit of offboarding actions  

---

*© Euphoria Infotech (I) Limited — ELU-CMP-001*
