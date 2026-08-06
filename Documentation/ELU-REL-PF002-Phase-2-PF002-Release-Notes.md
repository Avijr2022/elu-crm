# Release Notes — PF-002 Tenant Management
**Document ID:** ELU-REL-PF002  
**Release:** Phase-2-PF002  
**Status:** **RELEASE APPROVED**  
**Date:** 2026-08-06  
**Prior baseline:** Phase-2-PF001 (RELEASE APPROVED)  
**Git tag:** `Phase-2-PF002`

---

## Summary

PF-002 delivers Platform Admin Tenant Management: registration with atomic provisioning (PRIMARY contact, REGISTERED address, root organization, TRIAL subscription stub, tenant settings), list/search/export, approve → ACTIVE, suspend / reactivate, soft-close, own-tenant profile read, and Flutter Tenants UI.

## Delivered

### API
- `POST/GET/PUT/PATCH/DELETE /api/v1/platform/tenants`
- `GET /api/v1/platform/tenants/search`
- `GET /api/v1/platform/tenants/export`
- `POST .../approve|suspend|reactivate`
- `GET /api/v1/tenant/profile`
- `Idempotency-Key` on register

### Data
- `010_tenant_pf002.sql` / `migrate_pf002.py`
- `tenant_contact`, `tenant_address`, `tenant_status_history`, `idempotency_key`
- Status CHECK; legal_name unique index

### Flutter
- Platform Admin **Tenants** tab (List / Search / Register / View / Approve / Suspend / Reactivate)

### Tests
- `Backend/tests/test_pf002_tenants.py` — **11/11** (repeatable)

### Auth
- BR-PF-014: SUSPENDED tenants cannot obtain new JWT (login + refresh)
- Case-insensitive tenant code lookup

## Explicit non-goals this slice
- Branding upload UI/API (BR-PF-017)
- Self-registration domain verification (BR-PF-018)
- Full PF-003 subscription engine (TRIAL row created as provisioning stub only)

## Freeze
- **PF-001** frozen (`Phase-2-PF001`) — change only on defect.
- **PF-002** frozen (`Phase-2-PF002`) — change only on defect or approved CR.
- Next module: **PF-003 Subscription Management**.

## Approval
- [x] Human **RELEASE APPROVED**
- [x] Git tag `Phase-2-PF002`
- [x] MSL / CHANGELOG / RTM / QA updated

---

*© Euphoria Infotech (I) Limited — ELU-REL-PF002*
