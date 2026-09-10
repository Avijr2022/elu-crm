# E-LinkUp Cursor Rules (Always-On)

**Authority:** [ELU-CON-001](00-Framework/ELU-CON-001-Enterprise-Engineering-Constitution.md) (Frozen) · Detail: [ELU-AI-001](ELU-AI-001-Cursor-AI-Governance.md) · Decisions: [ELU-ADR-001](ELU-ADR-001-Architecture-Decision-Log.md)

## Before any production code

1. Read `Documentation/00_Project_Constitution.md` → ELU-CON-001.  
2. Check **Accepted** ADRs — especially **ADR-001**, **ADR-006**, **ADR-011**, **ADR-015**. Do not reverse them.  
3. Implement from **ELU-EFS-001** + domain **ELU-DDD / API / UI / TST** — never from Deprecated ELU-WF-001.  
4. Never invent or rename DDD fields.  
5. Tenant isolation: JWT `tenant_id` + repository filter + PostgreSQL RLS (`SET LOCAL app.tenant_id`) per ADR-015 / ELU-DEV-001 §6A.  
6. Edition gates: **ELU-EDM-001** (Community Lead convert = Customer only).  
7. Soft delete + `version_no` (ADR-006).  
8. No duplicate governance/BFS/EFS documents; strengthen in place.  
9. No application feature implementation until human approval after **ELU-GOV-VAL-001**.  
10. Cite Document IDs in plans and PRs.

## Stop and ask

- Spec contradicts CON or an Accepted ADR  
- Edition packaging unclear  
- Cross-tenant Platform Admin path without audit design  

---

*© Euphoria Infotech (I) Limited*
