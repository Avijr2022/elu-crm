# E-LinkUp Technical Debt — PF-004 Mid-Phase
**Document ID:** ELU-TD-003  
**Version:** 1.0  
**Date:** 2026-08-06  
**Extends:** ELU-TD-002  
**Related:** ELU-MPR-PF004, ELU-GAP-PF004  

---

## Critical
None open for PF-004 after mid-phase corrections.

## High

| ID | Item | Action |
|----|------|--------|
| TD-PF004-H01 | `address_id` not on organization | Add column + API per DDD/BFS |
| TD-PF004-H02 | Flutter Create + History screens missing | Implement before QA audit |

## Medium

| ID | Item | Action |
|----|------|--------|
| TD-PF004-M01 | Permission-grain RBAC for organization.* | Seed + enforce (or PF-009 waiver) |
| TD-PF004-M02 | PUT ≠ full replace | Align OpenAPI or implement replace |
| TD-PF004-M03 | Tax identifiers in audit payloads | Mask GSTIN/PAN |
| TD-PF004-M04 | No Flutter automated tests for org UI | Widget smoke |

## Low

| ID | Item | Action |
|----|------|--------|
| TD-PF004-L01 | Rollback SQL pack | Add paired rollback |
| TD-PF004-L02 | Export 500-row cap / no CSV headers | Stream or raise limit with filter |
| TD-PF004-L03 | NTF-PF-004-* unwired | CPS notification engine |

## Closed this review
- Soft-delete UK for org code  
- Platform Admin write violation vs BFS  
- Missing list sort  
- Missing parent index  

---

## PF-004 Approved Corrections — 2026-09-11 (HD-01…HD-11)

| Item | Status |
|------|--------|
| **TD-PF004-M01** Permission-grain RBAC for `organization.*` | **PARTIAL** — seeded map corrected to BFS-PF-004 §12 (`ORG_PERMISSION_MATRIX`); **runtime enforcement still deferred to PF-009** (HD-01) |
| **TD-PF004-M04** No Flutter automated tests for org UI | **CLOSED** — `Frontend/test/organization_nav_test.dart` (nav visibility, route guard, page load) |
| Export authorization (new) | **CLOSED** — `require_org_export()`: Tenant Admin + Finance User only (HD-02) |
| Export tax masking (new) | **CLOSED** — GSTIN/PAN masked `***` in the exported representation; stored values unchanged (HD-03) |
| Nav/route authorization (new) | **CLOSED** — organization nav + `/organizations` route are Tenant-Admin-only (HD-11) |
| **TD-PF004-L02** Export 500-row cap / no CSV headers | **OPEN — accepted** for v1.0: JSON retained (HD-04); cap unchanged |
| **TD-PF004-L03** NTF-PF-004-* unwired | **OPEN — deferred to CPS-003** (HD-08) |
| AC-PF-004-04 / BR-PF-032 PDF name propagation (G-12) | **OPEN — deferred to Document Engine** (HD-05) |
| RPT-PF-004-01 / -02 | **DEFERRED out of PF-004 v1.0** (HD-06) |
| RPT-PF-004-03 / -04 | **NOT LOCATED / NOT IMPLEMENTED** — undefined in every source (HD-07) |
| `Phase-2-PF004` tag governance | **RECORDED (HD-10, 2026-09-11)** — existing Phase-2-PF004 / Phase-2-PF004-MidReview tags preserved unchanged as historical artefacts; neither is the approved PF-004 release tag; no tag created or moved while Human RELEASE APPROVED was PENDING (historical HD-10 status, retained). **RECONCILED (2026-09-11):** Human RELEASE APPROVED recorded, and the approved **annotated** release tag **`Phase-2-PF004-R1`** created and pushed, targeting `3f30159a3ba73be1f09be791164982ec74ff8044` (see ELU-REL-PF004 § Tag disposition) |
| Alembic baseline | **OPEN** — platform-wide backlog |

**Note:** PLATFORM_ADMIN retains a universal bypass in `app/core/rbac.has_permission`; any future PF-009 grain enforcement must special-case read-only modules, otherwise Platform Admin would regain create/update/delete/export.

---

*© Euphoria Infotech (I) Limited — ELU-TD-003*
