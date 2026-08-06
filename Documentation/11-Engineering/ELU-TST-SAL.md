# E-LinkUp Test Specification — Sales
**Document ID:** ELU-TST-SAL  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-RTM-001, ELU-API-SAL, V1-SAL-PRJ, ELU-SEC-001, ELU-EDM-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / QA | SAL tests + isolation |

---

## Functional (samples)

| TC | REQ | Scenario | Expected |
|----|-----|----------|----------|
| TC-SAL-001 | REQ-SAL-001 | Create quotation | 201 |
| TC-SAL-004 | REQ-SAL-004 | Submit for approval | status Under Review |
| TC-SAL-009 | REQ-SAL-009 | SO from accepted quotation | 201 |
| TC-SAL-016 | REQ-SAL-016 | WO from confirmed SO | 201 |
| TC-SAL-EDN-01 | — | Community POST quotation | 403 |

## Isolation (mandatory)

| TC | Scenario | Expected |
|----|----------|----------|
| TC-SAL-ISO-01 | Cross-tenant GET quotation | 404 |
| TC-SAL-ISO-02 | Body tenant_id spoof | ignored |
| TC-SAL-ISO-03 | Soft-deleted excluded from list | excluded |
| TC-SAL-ISO-04 | Link quotation to other-tenant opportunity | 404 |

---

*© Euphoria Infotech (I) Limited — ELU-TST-SAL*
