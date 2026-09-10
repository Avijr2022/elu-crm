# E-LinkUp CPS v1.0 Stub Contract
**Document ID:** ELU-CPS-STUB-001  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-RDM-001, ELU-BFS-CPS, ELU-ADR-007, ELU-ADR-008, ELU-L2C-001, ELU-EFS-001  
**Applies to:** v1.0 Lead-to-Cash only (replaced by full CPS engines in v1.1)  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Solution Architecture | Define allowed stub behaviour so domains do not fork engines |

---

## 1. Purpose

v1.0 ships **before** full Workflow / Rule / Notification / Document engine depth (**ELU-RDM-001**).  
This contract defines **what stubs must do** so CRM/SAL/PRJ/FIN do **not** invent per-module approval engines (**ADR-007**).

---

## 2. Stub Matrix (v1.0)

| Engine | v1.0 behaviour | Forbidden |
|--------|----------------|-----------|
| **CPS-001 Workflow** | Fixed state transitions from EFS; single-step or static multi-step approver from role code (e.g. Sales Manager); no designer UI | Custom workflow graphs per tenant; per-module workflow tables |
| **CPS-002 Rules** | Hardcoded BR-* in services matching BFS/EFS | Separate rule DSL / per-module rule engines |
| **CPS-003 Notification** | Email + in-app for critical events; sync send acceptable (**ADR-008**) | SMS/WhatsApp/Push required; Celery mandatory |
| **CPS-005 Audit** | Write `audit_event` on lifecycle actions (PF-010 baseline) | Skipping audit on approve/issue/pay |
| **CPS-006 Documents** | MinIO upload + metadata tables | Storing BLOBs in PostgreSQL |
| **CPS-004 / 007 / 008** | Out of v1.0 | Partial fake BI/AI/integration |

---

## 3. Approval Stub API (shared)

```text
POST /api/v1/platform/approvals/{object_type}/{id}/submit
POST /api/v1/platform/approvals/{object_type}/{id}/decide   # APPROVE | REJECT
GET  /api/v1/platform/approvals/inbox
```

`object_type`: `quotation` | `proposal_version` | `sales_order` | `work_order` | `timesheet` | `change_request` | `vendor_payment` | …

Implementation may live under `services/cps/approval_stub.py` and be swapped for CPS-001 in v1.1 without changing domain routers’ public contracts.

---

## 4. Migration to v1.1

When CPS-001 designer ships: keep the same public approval endpoints; replace stub internals with workflow instances. Domain packs (**ELU-API-SAL/PRJ/FIN**) must not hardcode stub-only URLs beyond the shared approval surface.

---

*© Euphoria Infotech (I) Limited — ELU-CPS-STUB-001*
