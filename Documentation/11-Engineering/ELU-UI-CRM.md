# E-LinkUp UI Specification — CRM (Flutter)
**Document ID:** ELU-UI-CRM  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-BFS-CRM, ELU-EFS-001, ELU-API-CRM, ELU-EDM-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Frontend Lead | CRM Flutter screen inventory for v1.0 |

---

## 1. Routes

| Route | Screen | Actor | Edition |
|-------|--------|-------|---------|
| `/crm/leads` | LeadListPage | Sales Exec/Mgr | All |
| `/crm/leads/new` | LeadFormPage | Sales Exec | All |
| `/crm/leads/:id` | LeadDetailPage | Sales | All |
| `/crm/leads/:id/convert` | LeadConvertPage | Sales | Pro+ (creates Opp) |
| `/crm/opportunities` | OpportunityListPage | Sales | Professional+ |
| `/crm/opportunities/pipeline` | OpportunityPipelinePage | Sales Mgr | Professional+ |
| `/crm/opportunities/:id` | OpportunityDetailPage | Sales | Professional+ |
| `/crm/customers` | CustomerListPage | Sales | All |
| `/crm/customers/:id` | CustomerDetailPage | Sales | All |
| `/crm/customers/:id/360` | Customer360Page | Sales/Finance | Pro+ full |
| `/crm/activities` | ActivityListPage | Sales | All |
| `/crm/activities/timeline` | ActivityTimelinePage | Sales | All |
| `/crm/activities/new` | ActivityFormPage | Sales | All |

---

## 2. RBAC Hide/Disable

| Action | Hide if missing permission |
|--------|----------------------------|
| Create Lead | `lead.create` |
| Convert | `lead.convert` |
| Export | `lead.export` |
| Suspend Customer | `customer.suspend` |
| Close Won | `opportunity.approve` / close permission |

---

## 3. Validation UX

- Duplicate-check before create (email/phone/company).
- Status transitions only show Allowed Next States from EFS.
- `version_no` conflict → toast + reload.

---

*© Euphoria Infotech (I) Limited — ELU-UI-CRM*
