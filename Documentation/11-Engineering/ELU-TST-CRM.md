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
| TC-CRM-020 | — | Suspend customer blocks new quotation path | 422/403 when SAL called |
| TC-CRM-030 | — | Activity linked to other-tenant lead id | 404 |

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
