# E-LinkUp Technical Debt Register
**Document ID:** ELU-TD-001  
**Version:** 1.1  
**Status:** Approved  
**Owner:** Engineering / Architecture  
**Related:** ELU-RSK-001, ELU-QA-REG-001, ELU-MSL-001  

| ID | Module | Debt Item | Severity | Status | Notes |
|----|--------|-----------|----------|--------|-------|
| TD-PF-003-01 | PF-003 | Hourly expire scheduler job (BR-PF-024 “within 1 hour”) | Med | Open | Manual `POST .../expire` enforces cascade |
| TD-PF-003-02 | PF-003 | Permission-grain RBAC (`subscription.*`) beyond Platform Admin role gate | Low | Open | Role gate sufficient for Phase-2 |
| TD-PF-003-03 | PF-003 | BR-PF-022 seat check on user create | Med | Deferred | PF-008 Users |
| TD-PF-003-04 | PF-003 | Subscription notification emails (NTF-PF-003-*) | Low | Deferred | CPS Notification Engine |
| TD-PF-002-01 | PF-002 | Branding upload (BR-PF-017) / self-reg (BR-PF-018) | Low | **Partial — logo upload closed**, self-reg still deferred | Logo/favicon upload implemented (`PUT /api/v1/tenant/branding/logo`, 2 MB cap). Root-caused + fixed the `VARCHAR(2048)` overflow that broke uploads (ELU-MSL-002 v4.69). |

**Rule:** Debt does not unlock locked modules without CR/ADR.

---

*© Euphoria Infotech (I) Limited — ELU-TD-001*
