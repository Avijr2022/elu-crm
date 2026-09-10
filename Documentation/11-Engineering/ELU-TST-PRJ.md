# E-LinkUp Test Specification — Projects
**Document ID:** ELU-TST-PRJ  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-RTM-001, ELU-API-PRJ, V1-SAL-PRJ, ELU-SEC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / QA | PRJ tests + isolation |

---

## Samples

| TC | REQ | Scenario | Expected |
|----|-----|----------|----------|
| TC-PRJ-001 | REQ-PRJ-001 | Create from WO | 201; links SO/WO/Customer |
| TC-PRJ-009 | REQ-PRJ-009 | Raise CR | 201 |
| TC-PRJ-018 | REQ-PRJ-018 | Completion certificate | issued; project closable |
| TC-PRJ-EDN-01 | — | Community create project | 403 |

## Isolation

| TC | Scenario | Expected |
|----|----------|----------|
| TC-PRJ-ISO-01 | Cross-tenant GET project | 404 |
| TC-PRJ-ISO-02 | Timesheet on other-tenant task | 404 |
| TC-PRJ-ISO-03 | Soft-deleted project hidden | excluded |

---

*© Euphoria Infotech (I) Limited — ELU-TST-PRJ*
