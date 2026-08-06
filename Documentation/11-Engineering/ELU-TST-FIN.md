# E-LinkUp Test Specification — Finance
**Document ID:** ELU-TST-FIN  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-RTM-001, ELU-API-FIN, V1-FIN-SRV-INT, ELU-SEC-001, ELU-CMP-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / QA | FIN tests + isolation + immutability |

---

## Samples

| TC | Scenario | Expected |
|----|----------|----------|
| TC-FIN-001 | Create + issue invoice | ISSUED; number assigned |
| TC-FIN-002 | Edit amount on ISSUED invoice | 422 immutable |
| TC-FIN-003 | Allocate payment to invoice | balances update |
| TC-FIN-004 | Idempotent issue with same key | no duplicate |
| TC-FIN-010 | Vendor payment Professional | 201 |
| TC-FIN-EDN-01 | Community invoice create | 403 |

## Isolation

| TC | Scenario | Expected |
|----|----------|----------|
| TC-FIN-ISO-01 | Cross-tenant GET invoice | 404 |
| TC-FIN-ISO-02 | Allocate payment to other-tenant invoice | 404 |
| TC-FIN-ISO-03 | Soft-voided payment excluded | excluded |

---

*© Euphoria Infotech (I) Limited — ELU-TST-FIN*
