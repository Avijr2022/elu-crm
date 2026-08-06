# E-LinkUp Enterprise Engineering Constitution
**Document ID:** ELU-CON-001  
**Document Name:** Enterprise Engineering Constitution  
**Version:** 1.0  
**Status:** Frozen  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** Enterprise Architecture / PMO / AI Governance  
**Document Owner:** PMO / Solution Architecture  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-DOC-001, ELU-ADR-001, ELU-AI-001, ELU-DF-001, ELU-DEV-001, ELU-EFS-001, ELU-SAD-001, ELU-EDM-001, ELU-GOV-VAL-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Enterprise Architecture | Initial Frozen Constitution — Governance Baseline |

---

## 0. Authority & Freeze

**ELU-CON-001** is the **supreme governing document** for E-LinkUp engineering and AI-assisted delivery.

| Rule | Binding |
|------|---------|
| Precedence | CON → ADR → EFS / EDM / DEV / SEC → domain packs (BFS, DDD, API, UI, TST) |
| Status | **Frozen** — change only via PMO + Architecture Review and a new Version History row |
| AI agents | Must read this document (or `Documentation/00_Project_Constitution.md`) **before** generating production code |
| Conflict | If any document contradicts CON or an **Accepted** ADR, **CON/ADR win**; raise a Proposed ADR — do not silently “fix” in code |
| Implementation gate | No Phase 1+ application feature code until human approval after **ELU-GOV-VAL-001** |

This Constitution **does not** rewrite business stories, BFS, or EFS. It **points** to Approved sources of truth.

---

## 1. Product & Stack (Immutable unless ADR supersedes)

| Element | Binding source |
|---------|----------------|
| Product | E-LinkUp — multi-tenant CRM/ERP SaaS |
| Example tenant | Euphoria |
| Clients | Flutter Web + Android (**ADR-003**) |
| API | Python FastAPI (**ADR-002**) |
| Data | PostgreSQL shared DB + `tenant_id` (**ADR-001**) + dual RLS (**ADR-015**) |
| Auth | JWT + Refresh; SSO/MFA Enterprise-only (**ADR-004**) |
| Files | MinIO — not DB BLOBs (**ADR-005**) |
| Soft delete / optimistic lock | `is_deleted`, `version_no` (**ADR-006**) |
| Shared engines | CPS over per-module duplicates (**ADR-007**); v1.0 stubs per **ELU-CPS-STUB-001** |
| Async | Redis + Celery deferred (**ADR-008**) |
| Packaging | Community / Professional / Enterprise via **ELU-EDM-001** (**ADR-009**, **ADR-013**) |
| Hosting | Docker + Azure / Linux VPS (**ADR-014**) |
| Workflow SoT | **ELU-EFS-001** (**ADR-011**); fragment control **ELU-EFS-SOT-001** |
| Traceability | REQ-* anchors (**ADR-010**); catalogue **ELU-DOC-001** (**ADR-012**) |

---

## 2. Documentation Hierarchy

```text
ELU-CON-001     Constitution (this document) — Frozen
ELU-AI-001      Cursor AI Governance + Cursor_Rules / .cursor/rules
ELU-ADR-001     Architecture Decision Log (Accepted = binding)
ELU-DOC-001     Documentation Master Index
ELU-DF-001      Documentation Framework
ELU-SAD-001     Software Architecture
ELU-EFS-001     Workflow implementation SoT
ELU-EDM-001     Edition × Module packaging SoT
ELU-DEV-001     Day-to-day coding standards (incl. §6A RLS)
ELU-SEC/OPS/CMP Security, Backup/DR, Data Protection
ELU-BFS-*       Functional depth by domain
ELU-DDD/ERD/API/UI/TST-*  Engineering packs (Lead-to-Cash: PF→FIN Approved)
```

**Catalogue rule:** Every controlled document is registered in **ELU-DOC-001**. Do not invent Document IDs.

---

## 3. Tenancy & Security (Non-negotiable)

1. Every tenant-scoped table and API enforces **tenant isolation** per **ADR-015**: repository filters **and** PostgreSQL RLS with `SET LOCAL app.tenant_id`.  
2. Never trust client-supplied `tenant_id`.  
3. Edition gates are **server-side** (**ELU-EDM-001**). Community Lead convert = **Customer only** (no Opportunity).  
4. Isolation tests in **ELU-TST-*** are mandatory for tenant APIs.  
5. Threat model: **ELU-SEC-001**. Retention/backup: **ELU-CMP-001**, **ELU-OPS-001**.

---

## 4. Engineering Discipline

| Domain | Follow |
|--------|--------|
| Naming / structure | **ELU-DEV-001**, **ELU-DF-001** |
| Fields / DDL | **ELU-DDD-*** — do not invent or rename columns |
| APIs | **ELU-API-*** — align paths, errors, edition codes |
| UI | **ELU-UI-*** Flutter specs |
| QA / DoD | **ELU-TST-***; RTM **ELU-RTM-001** |
| Workflows | **ELU-EFS-001** only (not Deprecated **ELU-WF-001**) |
| Decisions | New significant choice → new **ADR-NNN** in **ELU-ADR-001** |

**Lead-to-Cash v1.0 path:** Lead → Quotation → Order → Work Order → Project → Invoice → Payment (tenant Euphoria). Proof: **ELU-GAP-001**, route **ELU-L2C-001**.

---

## 5. AI & Human Governance

1. Cursor / AI must obey **ELU-AI-001** and **Cursor_Rules.md**.  
2. **Accepted ADRs are immutable** in agent sessions — see **ELU-ADR-001 §7**. Supersession requires a new ADR, not code comments.  
3. Do not generate application code when Governance Validation has not been approved for the implementation phase.  
4. Do not duplicate BFS/EFS/DDD content into new “shadow” specs.  
5. Prefer strengthen-in-place over new parallel documents.

---

## 6. Definition of Ready (Documentation)

A feature may enter implementation only when:

- [ ] BFS section complete for the feature (seventeen-section template where applicable)  
- [ ] EFS workflow / REQ mapped (**ELU-RTM-001**)  
- [ ] DDD + ERD + API + UI + TST Approved for that domain (L2C: PF→FIN)  
- [ ] Edition row clear in **ELU-EDM-001**  
- [ ] No conflict with CON or Accepted ADRs  
- [ ] Human PO / Tech Lead authorization for the sprint  

---

## 7. Change Control

| Change type | Process |
|-------------|---------|
| Editorial (typos, broken links) | Document Owner; Version History bump |
| Behavioural / architectural | Proposed ADR → Architecture Review → Accepted; update CON Related only if needed |
| Constitution principles | PMO + Architecture; new CON version; **not** silent AI edit |
| Freeze lift | Explicit human approval recorded in **ELU-MSL-001** / change note |

---

## 8. Pointers (Do Not Duplicate)

| Need | Document |
|------|----------|
| Catalogue | ELU-DOC-001 |
| Workflows | ELU-EFS-001 + ELU-EFS-SOT-001 |
| Architecture | ELU-SAD-001 |
| Decisions | ELU-ADR-001 |
| Coding | ELU-DEV-001 |
| Packaging | ELU-EDM-001 |
| AI rules | ELU-AI-001, Cursor_Rules.md |
| Validation report | ELU-GOV-VAL-001 |

---

*© Euphoria Infotech (I) Limited — ELU-CON-001 Enterprise Engineering Constitution (Frozen)*
