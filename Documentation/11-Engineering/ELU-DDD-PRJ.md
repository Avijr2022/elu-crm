# E-LinkUp Data Dictionary — Projects
**Document ID:** ELU-DDD-PRJ  
**Version:** 1.0  
**Status:** Approved  
**Domain:** PRJ  
**Related Documents:** ELU-BFS-PRJ, ELU-ERD-PRJ, V1-SAL-PRJ, ELU-DDD-SAL, ELU-ADR-015, ELU-L2C-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | PRJ field dictionary for Lead-to-Cash |

---

## 1. Rules

Tenant-scoped + common columns (**ELU-DDD-PF §2**) + RLS (**ADR-015**). Professional+.  
Note: V1 RTM sometimes uses `project_milestone` / `project_task` aliases — **canonical table names** below match **ELU-BFS-PRJ** (`milestone`, `task`).

---

## 2. Tables

| Table | Key fields |
|-------|------------|
| project | project_number UK, customer_id, sales_order_id, work_order_id, pm_user_id, status, health_rag, planned/actual dates, budget, billing_eligible + common |
| project_baseline | project_id, version_no, scope_json, schedule_json, cost_json, locked_on |
| project_team_member | project_id, user_id, role_code |
| project_type | code, name |
| project_status_history | project_id, from_status, to_status, actor_id |
| project_qa_checklist | project_id, status |
| project_qa_checklist_item | checklist_id, item_text, is_passed |
| project_uat_signoff | project_id, signed_by_contact_id, signed_on, outcome |
| project_completion_certificate | project_id, certificate_number, issued_on, issued_by |
| milestone | project_id, name, sequence_no, planned/actual dates, pct_complete, invoice_trigger, status + common |
| milestone_type | code, name |
| task | project_id, milestone_id N, name, assignee_id, status, priority, estimate_hours, billable + common |
| task_assignment | task_id, from_user_id, to_user_id, assigned_on |
| task_category | code, name |
| timesheet | project_id, user_id, period_start, period_end, status, total_hours + common |
| timesheet_entry | timesheet_id, task_id, work_date, hours, billable |
| timesheet_approval | timesheet_id, approver_id, decision |
| issue | project_id, task_id N, title, severity, status, assignee_id, reporter_id + common |
| issue_comment | issue_id, body, author_id |
| issue_severity / issue_root_cause | lookups |
| change_request | project_id, cr_number, type, status, cost_impact, schedule_impact + common |
| change_request_impact | change_request_id, impact_type, amount, days |
| change_request_approval | change_request_id, approver_id, decision |
| change_request_type | code, name |

---

## 3. Indexes

UK(tenant_id, project_number|cr_number) WHERE NOT is_deleted; IDX(tenant_id, pm_user_id, status); IDX(tenant_id, customer_id).

---

*© Euphoria Infotech (I) Limited — ELU-DDD-PRJ*
