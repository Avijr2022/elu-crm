# E-LinkUp Project Risk Register
**Document ID:** ELU-RSK-001  
**Document Name:** Project Risk Register  
**Version:** 1.4  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** PMO / Solution Architecture  
**Document Owner:** PMO  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-DOC-001, ELU-RDM-001, ELU-MSL-001, ELU-ADR-001, ELU-EFS-001, ELU-SAD-001, ELU-CHR-001, ELU-CON-001, ELU-TD-001, ELU-TD-002, ELU-PGR-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP / PMO | Initial risk register for documentation-complete / build-ready phase |
| 1.1 | 2026-08-06 | EIIP / PMO | Post Phase-2-PF003 baseline; CON freeze; expire-scheduler risk |
| 1.2 | 2026-08-06 | EIIP / Architecture | Phase Gate PGR-001: RLS gap RSK-021; AI drift RSK-022; docs sync RSK-023 |
| 1.3 | 2026-08-06 | EIIP / PMO | PF-003A RELEASE APPROVED; RSK-021 Closed |
| 1.4 | 2026-08-06 | EIIP / Architecture | PF-004 mid-phase: RSK-024 UI completeness; RSK-025 address_id |

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
| RSK-001 | Tenant data isolation defect (cross-tenant leak) | Security | M | H | HM | Dual enforcement **ADR-015** + isolation tests in ELU-TST-*; code review checklist | Solution Architecture / Tech Lead | Mitigating | ELU-SAD-001, ELU-EFS-001, ADR-015 |
| RSK-002 | Scope creep from v1.1/v2.0 features into v1.0 | Delivery | H | H | HH | Freeze v1.0 module list via **ELU-RDM-001**; change control through PO; track via **ELU-L2C-001** | Product Owner | Mitigating | ELU-RDM-001, ELU-MSL-001 |
| RSK-003 | Documentation / implementation drift (build without REQ) | Quality | M | H | HM | No sprint story without `REQ-*` from **ELU-RTM-001** / **ELU-EFS-001**; Definition of Done | BA / QA Lead | Mitigating | ADR-010, ADR-011 |
| RSK-004 | Delayed Data Dictionary / ERD blocks coding start | Delivery | M | H | HM | **ELU-DDD-PF/CRM** done; SAL→FIN via **ELU-L2C-001** Steps 2–4 | Data Architect / BA | Mitigating | ELU-MSL-001, ELU-L2C-001 |
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
| RSK-016 | Test debt accumulates (no ELU-TST packs) | Quality | H | M | HM | **ELU-TST-PF/CRM** authored; SAL/PRJ/FIN via L2C; CI isolation gate | QA Lead | Mitigating | ELU-RTM-001, ELU-L2C-001 |
| RSK-017 | Change Request / billing disputes without audit evidence | Compliance | L | H | LH | Enforce audit events from EFS Audit sections; retention policy | BA / Compliance | Open | PF-010, CPS-005 |
| RSK-018 | AI features over-promised before CPS-007 maturity | Commercial | M | M | MM | Keep AI in v2.0+ only; label as assistive not authoritative | Product Owner | Mitigating | ELU-RDM-001 |
| RSK-019 | Trial/paid subscriptions expire without timely tenant suspend | Functional | M | M | MM | Manual expire API shipped (PF-003); schedule CPS job for BR-PF-024 SLA; track **ELU-TD-001** | Platform / Ops | Open | ELU-BFS-PF-003, ELU-TD-001 |
| RSK-020 | Drift from Constitution when starting next module without GAP | Process | M | H | HM | Mandatory CON GAP analysis before coding; locked modules require bug/CR/ADR | PMO / Tech Lead | Mitigating | ELU-CON-001, ELU-MSL-001 |
| RSK-021 | Dual RLS (ADR-015) not yet in runtime — isolation relies on app filters only | Security | H | H | HH | Delivered as **PF-003A** (`Phase-2-PF003A`); dual RLS + isolation tests live | Solution Architecture / Tech Lead | **Closed** | ELU-PGR-001, ELU-TD-002, ADR-015, ADR-016, ELU-REL-PF003A |
| RSK-024 | PF-004 Flutter Create/History incomplete → release slip | Delivery | M | H | HM | Close G-02/G-03 before QA audit; track ELU-GAP-PF004 | Flutter / BA | Open | ELU-MPR-PF004, ELU-TD-003 |
| RSK-025 | Missing organization.address_id breaks linked registered address story | Data | M | M | MM | Add FK in next PF-004 sprint (G-01) | Backend | Open | ELU-DDD-PF, ELU-BFS-PF-004 |
| RSK-022 | AI-generated Phase-2 code drift from DDD/CON without gate discipline | Quality | M | H | HM | CON + AI-001 + Phase Gate; freeze locked modules; RTM audits | PMO / QA | Mitigating | ELU-CON-001, ELU-AI-001 |
| RSK-023 | Uncommitted documentation packs cause SoT ambiguity | Process | M | M | MM | Commit/register packs; ELU-DOC-001 sync | PMO / BA | Open | ELU-PGR-001 |

---

## 4. Top Risks Heat Summary

| Priority Band | Risk IDs |
|---------------|----------|
| **Critical attention** | RSK-024 (PF-004 UI), RSK-002 (scope creep), RSK-003 (REQ drift), RSK-016 (test debt) |
| **Watch** | RSK-005, RSK-006, RSK-008, RSK-011, RSK-012, RSK-019, RSK-022, RSK-023, RSK-025 |
| **Closed (Phase-2-PF003A)** | RSK-021 (dual RLS delivered) |
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
