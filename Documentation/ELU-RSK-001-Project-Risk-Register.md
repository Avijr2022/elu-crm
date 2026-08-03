# E-LinkUp Project Risk Register
**Document ID:** ELU-RSK-001  
**Document Name:** Project Risk Register  
**Version:** 1.0  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** PMO / Solution Architecture  
**Document Owner:** PMO  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-DOC-001, ELU-RDM-001, ELU-MSL-001, ELU-ADR-001, ELU-EFS-001, ELU-SAD-001, ELU-CHR-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP / PMO | Initial risk register for documentation-complete / build-ready phase |

---

## 1. Purpose

**ELU-RSK-001** records project, product, technical, and commercial risks that could affect delivery of E-LinkUp.

Audience: Product Owner, PMO, Solution Architecture, Tech Leads, investors/clients (as appropriate under NDA), and the wider development team.

Catalogue: **ELU-DOC-001 – Documentation Master Index**.

---

## 2. Risk Scoring Model

| Rating | Probability | Impact |
|--------|-------------|--------|
| **H** High | Likely within release window | Major delay, security incident, or commercial loss |
| **M** Medium | Possible | Noticeable rework or partial scope slip |
| **L** Low | Unlikely | Minor inconvenience; workaround exists |

**Priority score** = combination of Probability × Impact (HH > HM/MH > MM > ML/LM > LL).

| Status | Meaning |
|--------|---------|
| Open | Active risk |
| Mitigating | Actions underway |
| Accepted | Consciously retained |
| Closed | No longer applicable |

---

## 3. Risk Register

| Risk ID | Risk | Category | Probability | Impact | Priority | Mitigation | Owner | Status | Related |
|---------|------|----------|-------------|--------|----------|------------|-------|--------|---------|
| RSK-001 | Tenant data isolation defect (cross-tenant leak) | Security | M | H | HM | Mandatory `tenant_id` filters + automated isolation tests; code review checklist; see **ADR-001** | Solution Architecture / Tech Lead | Open | ELU-SAD-001, ELU-EFS-001 |
| RSK-002 | Scope creep from v1.1/v2.0 features into v1.0 | Delivery | H | H | HH | Freeze v1.0 module list via **ELU-RDM-001**; change control through PO | Product Owner | Mitigating | ELU-RDM-001, ELU-MSL-001 |
| RSK-003 | Documentation / implementation drift (build without REQ) | Quality | M | H | HM | No sprint story without `REQ-*` from **ELU-RTM-001** / **ELU-EFS-001**; Definition of Done | BA / QA Lead | Open | ADR-010, ADR-011 |
| RSK-004 | Delayed Data Dictionary / ERD blocks coding start | Delivery | M | H | HM | Prioritise **ELU-DDD-PF** + **ELU-DDD-CRM** first; parallel API stubs | Data Architect / BA | Open | ELU-MSL-001 |
| RSK-005 | Flutter Web performance on complex CRM lists | Technical | M | M | MM | Pagination standards in **ELU-DEV-001**; virtualised lists; NFR targets in EFS | Frontend Lead | Open | ELU-DEV-001, NFR-* |
| RSK-006 | GST/TDS edge cases cause finance go-live delay | Functional | M | H | HM | Early FIN-004 workshop with tax SME; UAT scenarios in **ELU-TST-FIN** | BA / Finance SME | Open | ELU-BFS-FIN, ELU-EFS-001 |
| RSK-007 | Key-person dependency (architecture knowledge in few people) | Team | M | H | HM | Decision Log **ELU-ADR-001**; pair reviews; SEH/DEV standards | PMO | Mitigating | ELU-ADR-001, ELU-DEV-001 |
| RSK-008 | Edition feature gating implemented UI-only (security bypass) | Security | M | H | HM | Server-side edition checks (**ADR-009**); API contract tests | Tech Lead | Open | ADR-009 |
| RSK-009 | Celery/Redis deferred too late for SLA/dunning demos | Delivery | M | M | MM | Define v1.0 sync fallbacks; schedule Redis/Celery in v1.1 per **ADR-008** | Solution Architecture | Accepted | ADR-008, ELU-RDM-001 |
| RSK-010 | Third-party MinIO / storage outage loses attachments | Ops | L | H | LH | Backups; health checks; document metadata in PostgreSQL (**ADR-005**) | DevOps | Open | ADR-005 |
| RSK-011 | Investor/client demo fails due to incomplete happy path | Commercial | M | H | HM | Maintain Euphoria demo script Lead→Payment; milestone gate in **ELU-MSL-001** | Product Owner | Open | ELU-STORY-001, ELU-MSL-001 |
| RSK-012 | Underestimated integration effort in v2.0 | Delivery | M | M | MM | Spike INT-001 early; API consumer design in v1.0 auth model | Solution Architecture | Open | ELU-RDM-001, ELU-BFS-INT |
| RSK-013 | Password / token handling weaknesses | Security | L | H | LH | Argon2id; refresh rotation; security review before external pilot (**ADR-004**) | Security / Tech Lead | Open | ADR-004 |
| RSK-014 | Ambiguous ownership between BFS and EFS updates | Process | M | M | MM | EFS = workflow SoT (**ADR-011**); BFS for module depth; PMO mediates conflicts | PMO / BA | Mitigating | ADR-011 |
| RSK-015 | Hosting cost overrun on Azure vs VPS assumptions | Commercial | L | M | LM | Keep Docker portability (**ADR-014**); capacity review each quarter | DevOps / PO | Open | ADR-014 |
| RSK-016 | Test debt accumulates (no ELU-TST packs) | Quality | H | M | HM | Generate **ELU-TST-*** from RTM as soon as DDD/API start; CI smoke tests | QA Lead | Open | ELU-RTM-001 |
| RSK-017 | Change Request / billing disputes without audit evidence | Compliance | L | H | LH | Enforce audit events from EFS Audit sections; retention policy | BA / Compliance | Open | PF-010, CPS-005 |
| RSK-018 | AI features over-promised before CPS-007 maturity | Commercial | M | M | MM | Keep AI in v2.0+ only; label as assistive not authoritative | Product Owner | Mitigating | ELU-RDM-001 |

---

## 4. Top Risks Heat Summary

| Priority Band | Risk IDs |
|---------------|----------|
| **Critical attention** | RSK-002 (scope creep), RSK-001 (isolation), RSK-003 (REQ drift), RSK-004 (DDD delay), RSK-016 (test debt) |
| **Watch** | RSK-005, RSK-006, RSK-008, RSK-011, RSK-012 |
| **Accepted / monitored** | RSK-009, RSK-015 |

---

## 5. Risk Review Cadence

| Forum | Frequency | Action |
|-------|-----------|--------|
| PMO standup | Weekly | Update Status / Mitigation progress |
| Architecture review | Bi-weekly | Technical & security risks |
| Release gate | Per **ELU-RDM-001** release | Confirm no HH risks unmitigated for go-live |

---

## 6. How to Add a Risk

1. Allocate next `RSK-NNN`.  
2. Complete all columns in §3.  
3. Link Related Document IDs / ADRs.  
4. Assign Owner and Status.  
5. Reflect blockers on **ELU-MSL-001 – Milestone Tracker** when delivery is impacted.

---

*© Euphoria Infotech (I) Limited — ELU-RSK-001 Project Risk Register*
