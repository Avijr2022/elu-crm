# E-LinkUp ERD — Projects
**Document ID:** ELU-ERD-PRJ  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-DDD-PRJ, ELU-BFS-PRJ, ELU-ERD-SAL, ELU-ADR-015  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | PRJ logical ERD |

---

## 1. Logical ERD

```mermaid
erDiagram
    work_order ||--o{ project : initiates
    customer ||--o{ project : owns
    sales_order ||--o{ project : commercial
    project ||--o{ milestone : has
    project ||--o{ task : has
    milestone ||--o{ task : groups
    project ||--o{ timesheet : has
    task ||--o{ timesheet_entry : logs
    project ||--o{ issue : tracks
    project ||--o{ change_request : controls
    change_request ||--o| project_baseline : revises
    project ||--o| project_completion_certificate : closes
```

---

## 2. Delete policy

Restrict from commercial parents (WO/SO/Customer); Cascade team/checklist children; Restrict milestones/tasks with timesheets.

---

*© Euphoria Infotech (I) Limited — ELU-ERD-PRJ*
