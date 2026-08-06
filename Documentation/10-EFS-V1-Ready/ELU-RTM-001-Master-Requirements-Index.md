# E-LinkUp Master Requirements & Traceability Index
**Document ID:** ELU-RTM-001  
**Version:** 1.2  
**Status:** Approved
**Document Owner:** BA / QA
**Related Documents:** ELU-DOC-001, ELU-EFS-001, ELU-DF-001, ELU-TST-*, ELU-BFS-*, ELU-QA-PF001
**Parent:** ELU-EFS-001  
**Example Tenant:** Euphoria  

> This index summarises the Requirement ID ranges and RTM pattern. **Authoritative row-level RTM** lives inside each workflow’s **V1.0 Enterprise Ready Pack** in **ELU-EFS-001 – Enterprise Functional Specification**.

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-07-31 | EIIP | Initial master requirements & RTM index |
| 1.0a | 2026-07-31 | EIIP / PMO | Status Approved; registered in ELU-DOC-001 |
| 1.1 | 2026-08-06 | EIIP / Engineering | PF-001 Edition Management implementation traceability |
| 1.2 | 2026-08-06 | EIIP / QA | PF-001 RELEASE APPROVED — RTM 100% after remediation |

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
| Architect | Enforce NFR and tenant isolation (**ADR-015**) |

---

## 5. v1.0 Coverage Checklist

SoT: **ELU-EFS-001** + companion V1 packs (**ELU-EFS-SOT-001**). Each workflow must have §§16–22 artefacts.

| Workflow | Domain | V1 Pack | REQ/RTM | State | CRUD | NFR | UI Nav | API | Status |
|----------|--------|---------|---------|-------|------|-----|--------|-----|--------|
| WF-PF-001 | PF | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PF-002 | PF | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PF-003 | PF | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-CRM-001 | CRM | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-CRM-002 | CRM | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-CRM-003 | CRM | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-CRM-004 | CRM | V1-PF-CRM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-SAL-001 | SAL | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-SAL-002 | SAL | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-SAL-003 | SAL | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PRJ-001 | PRJ | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PRJ-002 | PRJ | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-PRJ-003 | PRJ | V1-SAL-PRJ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-FIN-001 | FIN | V1-FIN-SRV-INT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-FIN-002 | FIN | V1-FIN-SRV-INT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Complete |
| WF-SRV-001 | SRV | V1-FIN-SRV-INT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | v1.1 scope |
| WF-INT-001…004 | INT | V1-FIN-SRV-INT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | v2.0 scope |

---

## 6. Implementation Traceability — PF-001 Edition Management (100%)

| Business Rule / Capability | Table(s) | API | Flutter | Automated Test |
|----------------------------|----------|-----|---------|----------------|
| Edition catalogue CRUD (BFS §10) | `core.edition` (`id`,`code`,`name`) | `/api/v1/platform/editions` | List + Create + Edit + View | `test_list_editions`, create flows |
| Feature matrix | `feature_catalogue`, `edition_feature` | create/update `features` | View dialog | publish / create tests |
| Limits (EDM baselines) | `edition_limit` | create/update `limits` | View dialog | `test_limit_below_community_baseline` |
| Publish DRAFT→ACTIVE (BR-PF-008) | `edition`, `edition_version`, `audit.audit_event` | `POST .../publish` | Publish approval dialog | `test_create_publish_deprecate_flow` |
| Deprecate / deactivate (BR-PF-005) | `edition`, audit | `POST .../deprecate` + `assert_assignable` | (API; UI deprecate via future action) | deprecate + audit asserts |
| Search | `edition` | `GET .../search` | Search field | `test_search_and_history` |
| History | `edition_version` | `GET .../history` | History dialog | `test_search_and_history` |
| Tenant read-only edition | `edition` via tenant FK | `GET /api/v1/tenant/edition` | `_TenantEditionView` | `test_get_tenant_edition` |
| DDD schema alignment | `edition` CHECK + indexes | — | — | `test_schema_ddd_columns` |
| OpenAPI | — | `/openapi.json` | — | `test_openapi_includes_editions` |
| Audit logging | `audit.audit_event` | mutations | — | audit asserts in publish flow |

**Coverage:** **100%** of PF-001 BFS §10 APIs and §11 screens (List/Create/Edit/View/Search/Publish/History).  
**QA:** [ELU-QA-PF001 v2.0](../ELU-QA-PF001-Edition-Management-Release-Audit.md) — **RELEASE APPROVED**.  
**Baseline:** Release **Phase-2-PF001** · Git tag `Phase-2-PF001` · Notes [ELU-REL-PF001](../ELU-REL-PF001-Phase-2-PF001-Release-Notes.md) · [CHANGELOG](../CHANGELOG.md).  
**Rule:** Do not modify PF-001 unless a defect is reported.

**Code:** `Backend/app/api/v1/pf/editions.py`, `edition_service.py`, `audit_service.py`  
**SQL:** `009_edition_ddd_align_pf001.sql`, `migrate_pf001.py`  
**OpenAPI:** `Backend/openapi/openapi.json`

---

*© Euphoria Infotech (I) Limited — ELU-RTM-001*
