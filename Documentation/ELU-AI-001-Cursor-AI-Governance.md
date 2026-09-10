# E-LinkUp Cursor AI Governance
**Document ID:** ELU-AI-001  
**Document Name:** Cursor AI Governance  
**Version:** 1.0  
**Status:** Approved  
**Classification:** Internal Confidential  
**Project:** E-LinkUp (By Euphoria Infotech)  
**Prepared By:** AI Governance / Solution Architecture  
**Document Owner:** PMO / Tech Lead  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-CON-001, Cursor_Rules.md, ELU-ADR-001, ELU-DEV-001, ELU-DOC-001, ELU-GOV-VAL-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / AI Governance | Initial Cursor AI Governance Pack |

---

## 1. Purpose

Govern **Cursor and other AI coding assistants** so they cannot reverse Frozen Constitution rules, Accepted ADRs, or Approved specs while generating E-LinkUp work.

**Always-on short rules:** [Cursor_Rules.md](Cursor_Rules.md)  
**IDE enforcement:** `.cursor/rules/elu-enterprise.mdc`  
**Supreme authority:** [ELU-CON-001](00-Framework/ELU-CON-001-Enterprise-Engineering-Constitution.md)

---

## 2. Mandatory Read Order (Before Code)

1. `Documentation/00_Project_Constitution.md` → **ELU-CON-001**  
2. **ELU-ADR-001** Decision Index (especially ADR-001, 006, 009, 011, 015)  
3. Domain pack for the task: BFS → EFS/REQ → DDD → API → UI → TST  
4. **ELU-DEV-001** (incl. §6A RLS)  
5. **ELU-EDM-001** if edition/packaging is involved  

Do **not** invent fields, endpoints, or workflows absent from those sources.

---

## 3. Hard Prohibitions

| Prohibition | Why |
|-------------|-----|
| Reverse or “reinterpret” an **Accepted** ADR in code | Binding law — supersede only via new ADR (**ELU-ADR-001 §7**) |
| Trust client `tenant_id` | ADR-001 / ADR-015 |
| Skip RLS / `SET LOCAL app.tenant_id` on tenant tables | ADR-015 |
| Implement Community Lead → Opportunity | EDM: Customer only |
| Use Deprecated **ELU-WF-001** as implementation SoT | ADR-011 → EFS-001 |
| Duplicate BFS/EFS into new parallel specs | Sprawl / contradiction risk |
| Generate Phase implementation before GOV-VAL human approval | CON freeze gate |
| Write exploit PoCs / attack tooling | Security policy |
| Commit secrets / `.env` credentials | Security |

---

## 4. Standard Workflow (AI Session)

```text
1. Clarify task domain (PF|CRM|SAL|PRJ|FIN|…)
2. Open CON → ADR index → relevant Approved packs
3. Propose plan citing Document IDs (no silent scope creep)
4. Implement only after human approval when gated
5. Match DDD column names exactly; soft-delete + version_no
6. Add/adjust isolation tests for tenant APIs
7. Update DOC-001 / MSL only if a controlled doc was created
```

### 4.1 Prompt Patterns (use)

- “Per **ADR-015** and **ELU-DEV-001 §6A**, implement tenant session binding for …”  
- “Do not rename columns; follow **ELU-DDD-{DOM}**.”  
- “Edition gate per **ELU-EDM-001**; return `403 EDITION_FORBIDDEN` where specified.”  

### 4.2 Anti-patterns (avoid)

- “Simplify tenancy to app filter only.”  
- “Add Opportunity convert for Community to improve UX.”  
- “I’ll update the ADR in prose inside the PR instead of a new ADR.”  

---

## 5. Token Optimization

| Practice | Rule |
|----------|------|
| Prefer Document IDs | Cite `ELU-DDD-CRM` instead of pasting whole dictionaries |
| Slice reads | Open the feature section, not entire BFS when possible |
| One domain per session | Avoid loading PF+FIN+SRV unless cross-cutting |
| Diff-first edits | Strengthen existing files; no duplicate docs |
| Cache order | CON + ADR index + DEV §6A are small — load first |

---

## 6. Quality Gates (AI-assisted PRs)

- [ ] No Accepted ADR contradicted  
- [ ] `tenant_id` from JWT; RLS session set  
- [ ] Soft delete / `version_no` respected  
- [ ] Edition checks match EDM  
- [ ] Isolation test path covered or justified  
- [ ] Spec Document IDs cited in PR description  

---

## 7. Escalation

| Situation | Action |
|-----------|--------|
| Spec conflict | Prefer CON/ADR/EFS; open Proposed ADR or BA ticket — do not pick silently |
| Missing OpenAPI YAML / SEH | Deferred per GAP-001; use markdown API packs |
| Unclear edition | Stop; ask PO — default deny for Community |

---

*© Euphoria Infotech (I) Limited — ELU-AI-001 Cursor AI Governance*
