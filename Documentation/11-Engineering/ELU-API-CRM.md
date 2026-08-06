# E-LinkUp API Specification — CRM
**Document ID:** ELU-API-CRM  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-BFS-CRM, ELU-EFS-001, V1-PF-CRM, ELU-DDD-CRM, ELU-EDM-001, ELU-DEV-001, ELU-DOC-001  
**Base:** `/api/v1/crm` · JWT + RLS (**ADR-015**)  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Tech Lead | CRM API contract for Lead / Opportunity / Customer / Activity |

---

## 1. Cross-Cutting

Same as **ELU-API-PF §1**. Opportunity endpoints require Professional+ (**ELU-EDM-001**).

---

## 2. Leads (REQ-CRM-001…)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/crm/leads` | Create |
| GET | `/api/v1/crm/leads` | List paginated |
| GET | `/api/v1/crm/leads/{id}` | Get |
| PUT / PATCH | `/api/v1/crm/leads/{id}` | Update |
| PATCH | `/api/v1/crm/leads/{id}/status` | Status transition |
| DELETE | `/api/v1/crm/leads/{id}` | Soft delete |
| POST | `/api/v1/crm/leads/{id}/restore` | Restore |
| POST | `/api/v1/crm/leads/{id}/assign` | Assign owner |
| POST | `/api/v1/crm/leads/{id}/qualify` | Qualify |
| POST | `/api/v1/crm/leads/{id}/disqualify` | Disqualify |
| POST | `/api/v1/crm/leads/{id}/convert` | Convert → Customer (+ Opportunity if Professional+) |
| GET | `/api/v1/crm/leads/search` | Advanced search |
| GET | `/api/v1/crm/leads/export` | Export |
| POST | `/api/v1/crm/leads/duplicate-check` | Duplicate preview |
| GET | `/api/v1/crm/leads/{id}/history` | History |
| POST | `/api/v1/crm/leads/{id}/contacts` | Add contact |
| POST | `/api/v1/crm/leads/{id}/attachments` | Upload metadata + MinIO |
| GET | `/api/v1/crm/lead-sources` | Sources |

**Convert modes (ELU-L2C-001 / ELU-EDM-001):**
- **Professional / Enterprise:** `{ create_opportunity: true }` → Customer + Opportunity (default). Response: `{ lead_id, customer_id, opportunity_id }`.
- **Community:** Opportunity creation returns `403 EDITION_FORBIDDEN` if requested; allowed mode creates **Customer only** and sets lead status CONVERTED with `opportunity_id = null`. Response: `{ lead_id, customer_id, opportunity_id: null }`.

---

## 3. Opportunities (Professional+)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST/GET | `/api/v1/crm/opportunities` | Create / list |
| GET/PUT/PATCH | `/api/v1/crm/opportunities/{id}` | CRUD |
| PATCH | `/api/v1/crm/opportunities/{id}/stage` | Stage advance |
| POST | `.../close-won` · `.../close-lost` · `.../reopen` · `.../assign` · `.../hold` | Lifecycle |
| DELETE | `/api/v1/crm/opportunities/{id}` | Soft delete |
| GET | `/api/v1/crm/opportunities/pipeline` | Kanban |
| GET | `/api/v1/crm/opportunities/forecast` | Forecast |
| GET | `/api/v1/crm/opportunities/export` | Export |
| GET | `/api/v1/crm/opportunities/{id}/history` | Stage history |
| POST | `/api/v1/crm/opportunities/{id}/team-members` | Contributors |
| GET | `/api/v1/crm/opportunity-stages` | Stages |

---

## 4. Customers

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST/GET | `/api/v1/crm/customers` | Create / list |
| GET | `/api/v1/crm/customers/{id}` · `/{id}/360` | Detail / 360 |
| PUT/PATCH | `/api/v1/crm/customers/{id}` | Update |
| PATCH | `/api/v1/crm/customers/{id}/status` | Status |
| DELETE / POST restore | `/api/v1/crm/customers/{id}` | Soft delete / restore |
| POST | `.../suspend` · `.../activate` | Credit lifecycle |
| GET | `/api/v1/crm/customers/search` · `/export` | Search / export |
| POST | `/api/v1/crm/customers/duplicate-check` · `/{id}/merge` | Dedupe |
| POST | `/{id}/contacts` · `/{id}/addresses` | Children |
| GET | `/{id}/opportunities` · `/{id}/activities` | Links |

---

## 5. Activities

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST/GET | `/api/v1/crm/activities` | Create / list |
| GET/PUT/PATCH | `/api/v1/crm/activities/{id}` | CRUD |
| PATCH | `.../complete` · `.../cancel` | Lifecycle |
| DELETE | `/api/v1/crm/activities/{id}` | Soft delete (Manager) |
| POST | `.../assign` · `.../links` | Assign / link |
| GET | `/api/v1/crm/activities/timeline` | By entity |
| GET | `/api/v1/crm/{leads\|opportunities\|customers}/{id}/activities` | Shortcuts |
| GET | `/api/v1/crm/activities/upcoming` · `/overdue` | User views |
| GET | `/search` · `/export` | |
| POST | `/api/v1/crm/activities/bulk-complete` | Manager |
| GET | `/api/v1/crm/activity-types` · `/activity-outcomes` | Lookups |

---

*© Euphoria Infotech (I) Limited — ELU-API-CRM*
