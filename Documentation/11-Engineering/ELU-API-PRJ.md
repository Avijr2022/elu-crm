# E-LinkUp API Specification — Projects
**Document ID:** ELU-API-PRJ  
**Version:** 1.0  
**Status:** Approved  
**Base:** `/api/v1/projects` · JWT + RLS · Professional+  
**Related Documents:** ELU-BFS-PRJ, V1-SAL-PRJ, ELU-DDD-PRJ, ELU-CPS-STUB-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Tech Lead | PRJ API contract |

---

## Endpoints (summary)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/projects/from-work-order/{work_order_id}` | Create project |
| GET/PUT/PATCH | `/api/v1/projects/{id}` | CRUD / status |
| POST | `.../baseline/lock` | Lock baseline |
| POST/GET | `.../milestones` · `/milestones/{mid}` | Milestone plan |
| POST/GET | `.../tasks` · `/tasks/{tid}` | Task board |
| POST/GET | `.../timesheets` · `.../timesheets/{id}/submit` · `/approve` | Time |
| POST/GET | `.../issues` | Issues |
| POST/GET | `.../change-requests` · `.../change-requests/{id}/submit` · `/approve` | CR |
| POST | `.../qa-checklist` · `.../uat-signoff` · `.../completion-certificate` | Closure |
| GET | `/api/v1/projects` · `/export` · `/search` | List |

Community → 403. Approvals → **ELU-CPS-STUB-001** in v1.0.

---

*© Euphoria Infotech (I) Limited — ELU-API-PRJ*
