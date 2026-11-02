# E-LinkUp Test Specification — CRM
**Document ID:** ELU-TST-CRM  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-RTM-001, ELU-API-CRM, ELU-BFS-CRM, ELU-EFS-001, ELU-SEC-001, ELU-EDM-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / QA | CRM test pack + mandatory isolation suite |
| 1.1 | 2026-10-09 | EIIP / Engineering | Record TC-CRM-003-03 (REQ-CRM-027 duplicate-check) in §1 |
| 1.2 | 2026-11-02 | EIIP / Engineering | Record TC-CRM-003-04 (REQ-CRM-028 customer suspension and BR-CRM-049 blocking) in §1; reconcile the ad-hoc TC-CRM-020 probe row |
| 1.3 | 2026-11-02 | EIIP / Engineering | Record TC-CRM-003-13 (REQ-CRM-049 customer credit classification, AC-CRM-CUS-006) in §1 - documented only, NOT EXECUTED |

---

## 1. Functional Samples (Lead / Opp / Customer / Activity)

| TC ID | REQ | Scenario | Expected |
|-------|-----|----------|----------|
| TC-CRM-001 | REQ-CRM-001 | Create lead | 201; lead_number assigned |
| TC-CRM-002 | REQ-CRM-002 | Convert qualified lead | customer + opportunity; lead CONVERTED |
| TC-CRM-003 | — | Duplicate email create | 409 LEAD_DUPLICATE |
| TC-CRM-004 | — | Invalid status transition | 422 |
| TC-CRM-010 | — | Opportunity create as Community | 403 EDITION_FORBIDDEN |
| TC-CRM-011 | — | Close won without quotation (no exception) | 422 per BR-CRM-027 |
| TC-CRM-020 | — | *(superseded by TC-CRM-003-04; retained as historical evidence)* Suspend customer blocks new quotation path | 422/403 when SAL called |
| TC-CRM-030 | — | Activity linked to other-tenant lead id | 404 |
| TC-CRM-003-03 | REQ-CRM-027 | Duplicate-check pre-create: duplicate GSTIN blocks, duplicate name warns, unsupported/missing `tax_type` with a tax number is rejected | 200 `TAX_ID`/`BLOCK` masked; 200 `WARNING`; 422 BR-CRM-045 |
| TC-CRM-003-04 | REQ-CRM-028 | Customer suspension (ACTIVE -> SUSPENDED only, Finance User only, mandatory reason code and comment) and BR-CRM-049 blocking of new SAL transactions — new quotation, quotation-to-order conversion and DRAFT sales-order confirmation; generic PATCH can neither enter nor leave SUSPENDED; each blocked SAL attempt records `customer.suspension.blocked` | 200 SUSPENDED with one `crm.customer_status_history` row and one `customer.suspended` audit event; 409 when already suspended; 422 when not ACTIVE or when the reason is blank; 403 for a non-Finance caller; 404 for an unknown or other-tenant customer; SAL paths 422 BR-CRM-049 with exactly one persisted `customer.suspension.blocked` event; idempotent re-conversion still returns the existing sales order |
| TC-CRM-003-13 | REQ-CRM-049 | Customer credit classification (AC-CRM-CUS-006): per-tenant `customer_credit_class` lookup (code, name) and customer association via `credit_class_id`; Finance User creates, assigns or updates the classification; Sales Executive attempts the same write | Finance-authorised write persists the classification and returns 2xx; Sales Executive write returns **403** (AC-CRM-CUS-006); reads follow the customer read path | **NOT EXECUTED** — REQ-CRM-049 is approved but not implemented (no schema, ORM model, service or API); run only after implementation lands |

TC-CRM-003-04 is exercised by `Backend/tests/test_crm_customer_suspend.py` (suspension lifecycle, RBAC, tenant isolation, SAL blocking, blocked-attempt audit) and `Backend/tests/test_crm_customer_suspend_patch_concurrency.py` (PATCH-vs-suspension serialisation).

TC-CRM-003-13 is documented only: it has **not** been executed, and REQ-CRM-049 currently has no implementation.

Full RTM rows live in **V1-PF-CRM**; QA expands 1:1 before UAT.

---

## 2. Isolation Suite (Mandatory)

| TC ID | Scenario | Expected |
|-------|----------|----------|
| TC-CRM-ISO-01 | Create lead Tenant A; GET as Tenant B | 404 |
| TC-CRM-ISO-02 | PUT lead with body.tenant_id = other | ignored; remains A |
| TC-CRM-ISO-03 | Soft-deleted lead not in list | excluded |
| TC-CRM-ISO-04 | Convert using customer_id from Tenant B | 404 |
| TC-CRM-ISO-05 | activity_link to cross-tenant entity | 404 |
| TC-CRM-RBAC-01 | Sales Exec without lead.delete | 403 |
| TC-CRM-EDN-01 | Community GET /opportunities | 403 |

---

## 3. NFR Smoke

| Check | Target |
|-------|--------|
| Lead create p95 | < 500 ms (local/staging baseline) |
| List page_size=20 | < 500 ms with indexes |

---

## 4. Locations

`backend/tests/isolation/crm/` — **CI gate** for CRM PRs touching tenant entities.

---

*© Euphoria Infotech (I) Limited — ELU-TST-CRM*
