# E-LinkUp API Specification — Sales
**Document ID:** ELU-API-SAL  
**Version:** 1.0  
**Status:** Approved  
**Base:** `/api/v1/sales` · JWT + RLS · Professional+  
**Related Documents:** ELU-BFS-SAL, V1-SAL-PRJ, ELU-DDD-SAL, ELU-EDM-001, ELU-L2C-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Tech Lead | SAL API contract for Lead-to-Cash |

---

## 1. Cross-Cutting

Per **ELU-API-PF §1**. Community → `403 EDITION_FORBIDDEN`. Approvals may use **ELU-CPS-STUB-001** in v1.0.

---

## 2. Quotations

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST/GET | `/api/v1/sales/quotations` | Create / list |
| GET/PUT/PATCH | `/api/v1/sales/quotations/{id}` | CRUD |
| POST | `.../submit` · `.../approve` · `.../reject` | Approval |
| POST | `.../send` · `.../customer-response` | Customer cycle |
| POST | `.../convert` | → Sales Order (or prepare) |
| GET | `.../export` · `.../search` | |
| POST | `.../lines` | Line CRUD helpers |

---

## 3. Proposals

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST/GET | `/api/v1/sales/proposals` | Create / list |
| GET/PUT | `/api/v1/sales/proposals/{id}` | Detail / update |
| POST | `.../versions` · `.../versions/{vid}/approve` | Versioning |
| POST | `/api/v1/sales/quotations/{id}/link-proposal` | Link |

---

## 4. Sales Orders

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/sales/orders/from-quotation/{quotation_id}` | Create from quote |
| GET/PUT/PATCH | `/api/v1/sales/orders/{id}` | CRUD |
| POST | `.../submit` · `.../credit-release` · `.../approve` · `.../confirm` | Lifecycle |
| GET | `/api/v1/sales/orders` · `/export` | List |

---

## 5. Work Orders

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/sales/work-orders/from-order/{sales_order_id}` | Generate |
| GET/PUT | `/api/v1/sales/work-orders/{id}` | CRUD / scope |
| POST | `.../submit` · `.../approve` · `.../cancel` | Lifecycle |
| POST | `.../create-project` | → PRJ (`POST /api/v1/projects/from-work-order/{id}`) |

---

*© Euphoria Infotech (I) Limited — ELU-API-SAL*
