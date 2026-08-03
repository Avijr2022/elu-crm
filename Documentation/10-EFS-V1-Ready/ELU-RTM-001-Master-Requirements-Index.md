# E-LinkUp Master Requirements & Traceability Index
**Document ID:** ELU-RTM-001  
**Version:** 1.0 Enterprise Ready  
**Status:** Approved
**Document Owner:** BA / QA
**Related Documents:** ELU-DOC-001, ELU-EFS-001, ELU-DF-001, ELU-TST-*, ELU-BFS-*
**Parent:** ELU-EFS-001  
**Example Tenant:** Euphoria  

> This index summarises the Requirement ID ranges and RTM pattern. **Authoritative row-level RTM** lives inside each workflow’s **V1.0 Enterprise Ready Pack** in **ELU-EFS-001 – Enterprise Functional Specification**.

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP | Initial master requirements & RTM index |
| 1.0a | 2026-07-31 | EIIP / PMO | Status Approved; registered in ELU-DOC-001 |

## 1. Requirement ID Ranges

| Domain | Prefix | Sample Anchors | Workflows |
|--------|--------|----------------|-----------|
| Platform Foundation | `REQ-PF-` | REQ-PF-001 Create Tenant | WF-PF-001…003 |
| CRM | `REQ-CRM-` | REQ-CRM-001 Create Lead · REQ-CRM-002 Convert Lead to Opportunity | WF-CRM-001…004 |
| Sales | `REQ-SAL-` | REQ-SAL-001 Generate Quotation | WF-SAL-001…003 |
| Projects | `REQ-PRJ-` | REQ-PRJ-001 Create Project | WF-PRJ-001…003 |
| Finance | `REQ-FIN-` | REQ-FIN-001 Create Invoice | WF-FIN-001…002 |
| Service | `REQ-SRV-` | REQ-SRV-001 Create Ticket | WF-SRV-001 |
| Integration | `REQ-INT-` | REQ-INT-001 Register API Consumer | WF-INT-001…004 |

## 2. RTM Pattern (Mandatory)

| Requirement | Workflow | Table | API | Flutter Screen | Test Case |
|-------------|----------|-------|-----|----------------|-----------|
| REQ-CRM-001 | WF-CRM-001 | lead | POST /api/v1/crm/leads | Lead Create | TC-CRM-001 |
| REQ-CRM-002 | WF-CRM-001 | lead, opportunity | POST /api/v1/crm/leads/{id}/convert | Lead Convert | TC-CRM-002 |
| REQ-SAL-001 | WF-SAL-001 | quotation | POST /api/v1/sales/quotations | Quotation Create | TC-SAL-001 |

## 3. Companion Artefacts per Workflow

| Artefact | Use |
|----------|-----|
| State Transition Diagram | Allowed / Invalid / Re-open / Rollback |
| CRUD Responsibility Matrix | RBAC implementation |
| NFR-* | Performance, Security, Audit, Scalability, Availability, Retention |
| UI Navigation | Flutter roadmap |
| API Contract Summary | FastAPI router checklist |

## 4. How Teams Use This

| Role | Action |
|------|--------|
| Business Analyst | Own `REQ-*` wording and RTM completeness |
| Developer (Backend) | Implement APIs/tables keyed by `REQ-*` |
| Developer (Flutter) | Implement screens from UI Navigation + RTM |
| QA | Author `TC-*` from RTM; never invent unlinked tests |
| Architect | Enforce NFR and tenant isolation |

---

*© Euphoria Infotech (I) Limited — ELU-RTM-001*
