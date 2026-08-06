# E-LinkUp EFS Source-of-Truth Control
**Document ID:** ELU-EFS-SOT-001  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-EFS-001, ELU-ADR-011, ELU-RTM-001, ELU-DOC-001, ELU-DF-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / PMO | Declare single SoT and companion roles for EFS fragments |

---

## 1. Binding Rule (ADR-011)

| Artefact | Path | Role |
|----------|------|------|
| **ELU-EFS-001** | `ProjectStartupfiles/ELU-EFS-001-Enterprise-Functional-Specification.md` | **Implementation source of truth** for all workflows |
| Enrichment extracts | `Documentation/09-EFS-Enrichments/*.md` | Historical/companion extracts — **do not edit independently** |
| V1 Ready packs | `Documentation/10-EFS-V1-Ready/V1-*.md` | Authoritative for **REQ / RTM / CRUD / NFR / UI / API summary rows**; must stay aligned with EFS-001 |
| ELU-RTM-001 | `Documentation/10-EFS-V1-Ready/ELU-RTM-001-Master-Requirements-Index.md` | Index + v1.0 coverage checklist |
| ELU-WF-001 | `ProjectStartupfiles/ELU-Workflow-Documentation.md` | **Deprecated** for implementation |

---

## 2. Change Control

1. Propose workflow change → update **ELU-EFS-001** first.  
2. If V1 artefact rows change → update matching `V1-*.md` section in the same PR/change set.  
3. Refresh `09-EFS-Enrichments/` only when regenerating extracts (optional).  
4. Never ship conflicting state machines across the three locations.

---

## 3. Conflict Resolution

If texts disagree: **ELU-EFS-001 wins** for narrative/process; **V1 packs win** for numbered REQ/RTM rows **only if** they were updated after EFS — otherwise treat as drift and reconcile to EFS-001.

---

*© Euphoria Infotech (I) Limited — ELU-EFS-SOT-001*
