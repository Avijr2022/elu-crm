# E-LinkUp API Specification — Finance
**Document ID:** ELU-API-FIN  
**Version:** 1.0  
**Status:** Approved  
**Base:** `/api/v1/finance` · JWT + RLS · Professional+  
**Related Documents:** ELU-BFS-FIN, V1-FIN-SRV-INT, ELU-DDD-FIN, ELU-CMP-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Tech Lead | FIN API contract for Lead-to-Cash |

---

## Endpoints (summary)

| Area | Key endpoints |
|------|----------------|
| Invoices | `POST/GET /api/v1/finance/invoices`, `.../{id}/issue`, `.../{id}/cancel`, `.../from-milestone/{mid}`, `.../from-sales-order/{so_id}` |
| Credit notes | `POST /api/v1/finance/credit-notes` |
| Payments | `POST/GET /api/v1/finance/payments`, `.../{id}/allocate`, `.../{id}/reconcile` |
| Dunning | `GET /api/v1/finance/dunning/cases`, `POST .../run` (may be sync stub until Celery) |
| Vendors | `POST/GET /api/v1/finance/vendors`, `POST/GET /api/v1/finance/vendor-payments`, `.../{id}/approve`, `.../{id}/pay` |
| Tax | `GET/POST /api/v1/finance/tax-rates`, `.../tds-sections`, `POST .../compute` |

Idempotency-Key required on `issue` invoice and `allocate` payment. Community → 403.

---

*© Euphoria Infotech (I) Limited — ELU-API-FIN*
