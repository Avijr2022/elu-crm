# E-LinkUp Data Dictionary — CRM
**Document ID:** ELU-DDD-CRM  
**Version:** 1.0  
**Status:** Approved  
**Classification:** Internal Confidential  
**Domain:** CRM  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-BFS-CRM, ELU-ERD-CRM, ELU-EFS-001, ELU-RTM-001, ELU-ADR-001 (ADR-006, ADR-015), ELU-DDD-PF, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | Initial CRM field dictionary for v1.0 schema freeze |

---

## 1. Purpose

Field-level definitions for CRM tables (Lead, Opportunity, Customer, Activity). All tables are **tenant-scoped** with common columns from **ELU-DDD-PF §2** and RLS per **ADR-015**.

---

## 2. Lead (CRM-001)

### 2.1 lead

| Name | Type | Len | Req | Notes |
|------|------|-----|-----|-------|
| id | UUID | — | Y | PK |
| tenant_id | UUID | — | Y | RLS |
| lead_number | VARCHAR | 32 | Y | UK per tenant (active) |
| external_reference | VARCHAR | 64 | N | |
| source_campaign | VARCHAR | 128 | N | |
| company_name | VARCHAR | 255 | Y | |
| industry_id | UUID | — | N | |
| lead_type | VARCHAR | 16 | Y | B2B / B2C |
| description | TEXT | — | N | |
| primary_email | VARCHAR | 255 | N | Denormalised |
| primary_phone | VARCHAR | 32 | N | |
| estimated_value | NUMERIC | 18,2 | N | |
| currency_code | CHAR | 3 | N | |
| expected_close_date | DATE | — | N | |
| budget_confirmed | BOOLEAN | — | N | BANT |
| authority_contact | BOOLEAN | — | N | |
| need_summary | TEXT | — | N | |
| timeline_date | DATE | — | N | |
| owner_id | UUID | — | Y | FK users |
| team_id | UUID | — | N | |
| branch_id | UUID | — | N | FK branch |
| organization_id | UUID | — | N | |
| status | VARCHAR | 32 | Y | DRAFT, NEW, CONTACTED, QUALIFIED, NURTURE, DISQUALIFIED, CONVERTED, CANCELLED |
| status_reason | VARCHAR | 255 | N | |
| next_follow_up_date | DATE | — | N | |
| lead_source_id | UUID | — | N | FK lead_source |
| referrer_customer_id | UUID | — | N | FK customer |
| converted_at | TIMESTAMPTZ | — | N | |
| converted_by | UUID | — | N | |
| opportunity_id | UUID | — | N | After convert |
| customer_id | UUID | — | N | After convert |
| + common columns | | | | is_active, is_deleted, version_no, audit |

### 2.2 lead_contact

| Name | Type | Req | Notes |
|------|------|-----|-------|
| id, tenant_id | UUID | Y | |
| lead_id | UUID | Y | FK lead CASCADE |
| salutation, first_name, last_name | VARCHAR | Y (names) | |
| job_title, department | VARCHAR | N | |
| email, phone_mobile, phone_work | VARCHAR | N | |
| preferred_channel | VARCHAR | N | EMAIL/PHONE/WHATSAPP |
| is_primary | BOOLEAN | Y | Exactly one primary per lead |
| is_decision_maker | BOOLEAN | N | |
| address fields | VARCHAR | N | |
| + common | | | |

### 2.3 Supporting lead tables

| Table | Key fields |
|-------|------------|
| lead_source | tenant_id, code UK, name, description, default_owner_id, is_active + common |
| lead_disqualification_reason | tenant_id, code UK, name, is_active |
| lead_assignment_history | tenant_id, lead_id, from_owner_id, to_owner_id, reason, changed_by, changed_on |
| lead_conversion_log | tenant_id, lead_id UK, opportunity_id, customer_id, converted_by, converted_on, snapshot_json |
| lead_note | tenant_id, lead_id, body, created_by, created_on |
| lead_attachment | tenant_id, lead_id, file_name, file_size, mime_type, storage_key, document_type, uploaded_by, uploaded_at |

---

## 3. Opportunity (CRM-002)

### 3.1 opportunity

| Name | Type | Req | Notes |
|------|------|-----|-------|
| id, tenant_id | UUID | Y | |
| opportunity_number | VARCHAR | Y | UK per tenant active |
| name | VARCHAR | Y | |
| customer_id | UUID | Y | FK customer |
| source_lead_id | UUID | N | FK lead |
| owner_id | UUID | Y | FK users |
| branch_id / business_unit_id | UUID | N | |
| stage_code | VARCHAR | Y | OPEN stages / CLOSED_WON / CLOSED_LOST / ON_HOLD / CANCELLED |
| probability_pct | INTEGER | Y | 0–100 |
| amount | NUMERIC | Y | |
| currency_code | CHAR | Y | |
| expected_close_date | DATE | N | |
| status | VARCHAR | Y | OPEN, ON_HOLD, CLOSED_WON, CLOSED_LOST, CANCELLED |
| loss_reason_id | UUID | N | |
| competitor_notes | TEXT | N | |
| + common | | | |

### 3.2 Supporting opportunity tables

| Table | Key fields |
|-------|------------|
| opportunity_stage | tenant_id, code UK, name, sequence_no, default_probability, is_closed |
| opportunity_stage_history | tenant_id, opportunity_id, from_stage, to_stage, changed_by, changed_on, comment |
| opportunity_contact | tenant_id, opportunity_id, customer_contact_id, role_on_deal |
| opportunity_competitor | tenant_id, opportunity_id, competitor_name, strength, weakness |
| opportunity_loss_reason | tenant_id, code UK, name |
| opportunity_team_member | tenant_id, opportunity_id, user_id, role_code (PRE_SALES etc.) |
| opportunity_note | tenant_id, opportunity_id, body, created_by, created_on |
| opportunity_forecast_snapshot | tenant_id, period_yyyymm, opportunity_id, amount, probability_pct, category |

---

## 4. Customer (CRM-003)

### 4.1 customer

| Name | Type | Req | Notes |
|------|------|-----|-------|
| id, tenant_id | UUID | Y | |
| customer_number | VARCHAR | Y | UK per tenant active |
| legal_name | VARCHAR | Y | |
| trade_name | VARCHAR | N | |
| customer_type | VARCHAR | Y | ACCOUNT / PERSON |
| status | VARCHAR | Y | PROSPECT, ACTIVE, INACTIVE, ON_HOLD, SUSPENDED, CANCELLED |
| segment_id / industry_id / credit_class_id | UUID | N | |
| owner_id | UUID | N | Account owner |
| gstin / pan / tan | VARCHAR | N | Tax IDs |
| website | VARCHAR | N | |
| parent_customer_id | UUID | N | Hierarchy |
| + common | | | |

### 4.2 Supporting customer tables

| Table | Key fields |
|-------|------------|
| customer_contact | tenant_id, customer_id, name fields, email, phones, is_primary, is_decision_maker |
| customer_address | tenant_id, customer_id, address_type, lines, city, state, country, postal_code, is_default_billing, is_default_shipping |
| customer_segment / customer_industry / customer_credit_class | tenant_id, code UK, name |
| customer_note | tenant_id, customer_id, body |
| customer_relationship | tenant_id, parent_customer_id, child_customer_id, relation_type |
| customer_tax_registration | tenant_id, customer_id, tax_type, tax_number, state_code |
| customer_status_history | tenant_id, customer_id, from_status, to_status, reason, actor_id, changed_on |

---

## 5. Activity (CRM-004)

### 5.1 activity

| Name | Type | Req | Notes |
|------|------|-----|-------|
| id, tenant_id | UUID | Y | |
| activity_type_id | UUID | Y | |
| subject | VARCHAR | Y | |
| description | TEXT | N | PII-sensitive |
| status | VARCHAR | Y | PLANNED, IN_PROGRESS, COMPLETED, CANCELLED, OVERDUE |
| priority | VARCHAR | N | LOW/MEDIUM/HIGH |
| owner_id | UUID | Y | |
| due_on / completed_on | TIMESTAMPTZ | N | |
| outcome_id | UUID | N | |
| + common | | | |

### 5.2 Supporting activity tables

| Table | Key fields |
|-------|------------|
| activity_link | tenant_id, activity_id, entity_type (LEAD/OPPORTUNITY/CUSTOMER/…), entity_id; UK(activity_id, entity_type, entity_id) |
| activity_type | tenant_id, code UK, name, is_active |
| activity_outcome | tenant_id, activity_type_id, code, name |
| activity_attendee | tenant_id, activity_id, user_id N, contact_email N, attendee_name |
| activity_reminder | tenant_id, activity_id, remind_at, channel, sent_on |
| activity_attachment | tenant_id, activity_id, storage_key, file_name |

---

## 6. Indexes (Minimum)

| Table | Index |
|-------|-------|
| lead | UK(tenant_id, lead_number) WHERE NOT is_deleted; IDX(tenant_id, owner_id, status); IDX(tenant_id, primary_email) |
| opportunity | UK(tenant_id, opportunity_number) WHERE NOT is_deleted; IDX(tenant_id, stage_code); IDX(tenant_id, customer_id) |
| customer | UK(tenant_id, customer_number) WHERE NOT is_deleted; IDX(tenant_id, legal_name); IDX(tenant_id, gstin) |
| activity | IDX(tenant_id, owner_id, due_on); IDX(tenant_id, status) |
| activity_link | IDX(tenant_id, entity_type, entity_id) |

---

## 7. RLS

All CRM tables: RLS enabled + policy per **ADR-015**. Cross-tenant access returns **404** at API layer.

---

*© Euphoria Infotech (I) Limited — ELU-DDD-CRM*
