# E-LinkUp Data Dictionary — Platform Foundation
**Document ID:** ELU-DDD-PF  
**Version:** 1.0  
**Status:** Approved  
**Classification:** Internal Confidential  
**Domain:** PF (Platform Foundation)  
**Example Tenant:** Euphoria  
**Related Documents:** ELU-BFS-PF, ELU-ERD-PF, ELU-EFS-001, ELU-ADR-001 (ADR-001, ADR-006, ADR-015), ELU-DEV-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | Initial PF field dictionary for v1.0 schema freeze |
| 1.1 | 2026-09-29 | EIIP / Engineering | PF-011 governed specification reconciliation |

---

## 1. Purpose

Field-level definitions for Platform Foundation tables used to generate PostgreSQL DDL and SQLAlchemy models. Logical groups originate from **ELU-BFS-PF**.

**Rules:**
- Tenant-scoped tables include common audit columns (§2) and **RLS** per **ADR-015**.
- Soft delete + `version_no` per **ADR-006**.
- Do not invent columns beyond this dictionary without a BFS/EFS change.

---

## 2. Common Column Pattern (Tenant Business Tables)

| Name | Data Type | Req | Default | Notes |
|------|-----------|-----|---------|-------|
| id | UUID | Y | gen_random_uuid() | PK |
| tenant_id | UUID | Y | — | FK → tenant.id; indexed; RLS |
| is_active | BOOLEAN | Y | true | |
| is_deleted | BOOLEAN | Y | false | Soft delete |
| version_no | INTEGER | Y | 1 | Optimistic lock |
| created_by | UUID | N | — | FK → users.id |
| created_on | TIMESTAMPTZ | Y | now() | |
| modified_by | UUID | N | — | |
| modified_on | TIMESTAMPTZ | N | — | |

Partial unique indexes must exclude `is_deleted = true` rows.

---

## 3. Platform-Global Tables (No tenant_id / No RLS)

### 3.1 edition

| Name | Type | Len | Req | PK/FK/UK | Description |
|------|------|-----|-----|----------|-------------|
| id | UUID | — | Y | PK | |
| code | VARCHAR | 32 | Y | UK | COMMUNITY, PROFESSIONAL, ENTERPRISE |
| name | VARCHAR | 100 | Y | | |
| description | TEXT | — | N | | |
| version_no | INTEGER | — | Y | | Edition catalogue version |
| status | VARCHAR | 32 | Y | | DRAFT, ACTIVE, DEPRECATED, ARCHIVED, CANCELLED |
| effective_from | DATE | — | N | | |
| effective_to | DATE | — | N | | |
| list_price_monthly | NUMERIC | 18,2 | N | | |
| list_price_annual | NUMERIC | 18,2 | N | | |
| currency_code | CHAR | 3 | N | | INR default |
| display_order | INTEGER | — | N | | |
| published_at | TIMESTAMPTZ | — | N | | |
| published_by | UUID | — | N | | Platform user |
| created_by / created_on / modified_by / modified_on | — | — | | Audit (no tenant) |

### 3.2 edition_feature / edition_limit / feature_catalogue / permission / permission_module

| Table | Key columns |
|-------|-------------|
| feature_catalogue | id, feature_code UK, feature_name, module_domain, description |
| edition_feature | id, edition_id FK, feature_code, is_enabled, is_visible |
| edition_limit | id, edition_id FK, limit_code, limit_name, limit_value, limit_unit, is_hard_limit, grace_percent |
| permission | id, code UK (`resource.action`), name, module_domain |
| permission_module | id, module_domain UK, display_name |
| platform_setting | id, key UK, value, description |
| setting_catalogue | id, setting_key UK, value_type, default_value, description |

---

## 4. Tenant Root & Profile

### 4.1 tenant

| Name | Type | Req | Req | Notes |
|------|------|-----|-----|-------|
| id | UUID | Y | PK | Root; **no** tenant_id column (is the tenant) |
| code | VARCHAR | 64 | Y | UK global |
| legal_name | VARCHAR | 255 | Y | |
| trade_name | VARCHAR | 255 | N | |
| edition_id | UUID | Y | FK edition | |
| current_subscription_id | UUID | N | FK subscription | |
| status | VARCHAR | 32 | Y | DRAFT, PENDING_ACTIVATION, TRIAL, ACTIVE, SUSPENDED, OFFBOARDING, CLOSED, ARCHIVED, CANCELLED |
| industry | VARCHAR | 100 | N | |
| company_size | VARCHAR | 50 | N | |
| provision_source | VARCHAR | 32 | N | MANUAL, SALES_DEAL |
| activated_on | TIMESTAMPTZ | N | | |
| suspended_on | TIMESTAMPTZ | N | | |
| is_deleted | BOOLEAN | Y | Soft close | |
| version_no | INTEGER | Y | | |
| created_by / created_on / modified_by / modified_on | | | | |

**RLS:** Platform Admin only for directory; tenant users read own via JWT match on `id` (special policy: `id = app.tenant_id`).

### 4.2 Child profile tables (tenant_scoped = Yes)

| Table | Key fields beyond common |
|-------|--------------------------|
| tenant_contact | tenant_id, contact_type (PRIMARY/BILLING/TECHNICAL), name, email, mobile, is_primary |
| tenant_address | tenant_id, address_type, line1, line2, city, state, country, postal_code |
| tenant_branding | tenant_id UK, logo_url, primary_color, secondary_color, favicon_url |
| tenant_settings | tenant_id UK, fiscal_year_start_month, default_currency, timezone (logical names) — **released ORM columns are preserved; see the §11 compatibility mapping** |
| tenant_security | tenant_id UK, password_min_length, password_expiry_days, mfa_required, session_timeout_minutes, max_login_attempts, lock_duration_minutes, ip_whitelist_enabled, audit_retention_days, encryption_at_rest |
| tenant_localization | tenant_id UK, locale, date_format, number_format, currency_code, timezone |
| tenant_status_history | tenant_id, from_status, to_status, reason, actor_id, changed_on |

---

## 5. Organization Structure

| Table | Key fields |
|-------|------------|
| organization | tenant_id, code, name, legal_name, organization_type, parent_organization_id, gstin, pan, status + common |
| branch | tenant_id, organization_id, parent_branch_id N, branch_code, branch_name, branch_type (HEAD_OFFICE/BRANCH/REGIONAL_OFFICE), branch_head_user_id N †, email, phone, branch_address_id N, timezone_id, working_hours, status (DRAFT/ACTIVE/INACTIVE/ARCHIVED/CANCELLED), opened_date, closed_date + common |
| branch_address | tenant_id, branch_id UK, address_line_1/2, city, state, postal_code, country_code, latitude, longitude + common |
| department | tenant_id, organization_id, branch_id N, code, name, parent_department_id, department_head_user_id + common |
| business_unit | tenant_id, organization_id, code, name, bu_manager_user_id, cost_centre_code + common |

† **PF-005 groundwork note (2026-09-12):** `branch.branch_head_user_id` is created **nullable with no FK and no validation** — branch-head assignment/validation (BR-PF-038 / AC-PF-005-04) is **deferred to PF-008 Users & Identity**. `users.branch_id` (see §7) is **NOT** created — also deferred to PF-008. `department.branch_id` is **documentary only** (**PF-006**, not implemented).

---

## 6. Subscription

| Table | Key fields |
|-------|------------|
| subscription | tenant_id, edition_id, subscription_number, status (TRIAL/ACTIVE/SUSPENDED/EXPIRED/CANCELLED), start_date, end_date, trial_end_date, billing_cycle + common |
| subscription_history | tenant_id, subscription_id, from_status, to_status, from_edition_id, to_edition_id, reason, actor_id, changed_on |
| subscription_usage | tenant_id, subscription_id, metric_code (USERS/STORAGE_GB/ROLES), used_value, measured_on |

---

## 7. Identity & RBAC

| Table | Key fields |
|-------|------------|
| users | tenant_id, email UK(tenant+email active), display_name, status, branch_id, department_id, last_login_on + common |
| user_credentials | tenant_id, user_id UK, password_hash (Argon2id), password_changed_on |
| user_session | tenant_id, user_id, refresh_token_hash, expires_on, revoked_on, ip_address, user_agent |
| user_mfa | tenant_id, user_id UK, totp_secret_encrypted, backup_codes_hash, is_enabled |
| user_invite | tenant_id, email, role_id, token_hash, expires_on, accepted_on, status |
| user_password_history | tenant_id, user_id, password_hash, created_on |
| role | tenant_id, code, name, is_system, status + common |
| role_permission | tenant_id, role_id, permission_id; UK(role_id, permission_id) |
| user_role | tenant_id, user_id, role_id; UK(user_id, role_id) |

---

## 8. Audit & Config

| Table | Key fields |
|-------|------------|
| audit_event | tenant_id, event_type, event_category, actor_id, actor_email, entity_type, entity_id, ip_address, user_agent, session_id, payload_json, created_on |
| audit_event_detail | tenant_id, audit_event_id, field_name, old_value, new_value |
| audit_retention_policy | tenant_id UK, retention_days, cold_storage_enabled |
| audit_export_log | tenant_id, requested_by, from_date, to_date, status, file_key |
| platform_audit_event | (no tenant_id) platform-level events |
| tenant_preference | tenant_id, preference_key, preference_value, preference_type, preference_group, description, is_editable, edition_minimum (BFS §9 — see §11) |
| tenant_notification_preference | tenant_id, event_type, module_code, email_enabled, sms_enabled, whatsapp_enabled, push_enabled, internal_enabled, notify_actor, notify_manager, notify_admin, custom_recipients (BFS §9 — see §11) |
| tenant_module_default | tenant_id, module_code, entity_type, field_name, default_value (BFS §9 — see §11) |
| tenant_holiday_calendar | tenant_id, holiday_name, holiday_date, is_recurring, holiday_type, calendar_year (BFS §9 — see §11) |

---

## 9. Indexes (Minimum)

| Table | Index |
|-------|-------|
| tenant | UK(code); IDX(status); IDX(edition_id) |
| users | UK(tenant_id, email) WHERE is_deleted = false; IDX(tenant_id, status) |
| role | UK(tenant_id, code) WHERE is_deleted = false |
| subscription | IDX(tenant_id, status); IDX(edition_id) |
| audit_event | IDX(tenant_id, created_on); IDX(tenant_id, entity_type, entity_id) |
| organization / branch / department | UK(tenant_id, code) WHERE is_deleted = false |

---

## 10. RLS Checklist

Every table in §§4–8 marked tenant-scoped: `ENABLE ROW LEVEL SECURITY` + policy per **ADR-015** / **ELU-DEV-001 §6A**.

PF-011 tenant-scoped tables also require RLS: `tenant_preference`, `tenant_notification_preference`, `tenant_module_default` and `tenant_holiday_calendar`. `platform_setting` and `setting_catalogue` are platform-global (§3.2) and carry **no** tenant RLS.

---

## 11. PF-011 Reconciliation (ADR-017)

**Authority:** ADR-017 (Accepted, 2026-09-29) governs this reconciliation. The PF-011 BFS §9 is normative for the **new** PF-011 logical shapes; the released `tenant_settings` ORM columns remain authoritative and are **not** renamed.

### 11.1 tenant_settings compatibility mapping

| Released ORM column (authoritative) | PF-011 logical name (BFS §9) | Treatment |
|-------------------------------------|------------------------------|-----------|
| `financial_year_start` (DATE) | `fiscal_year_start_month` (1–12, BR-PF-079) | **Preserved.** No Date→month migration in PF-011 CORE; the month-versus-Date mismatch is recorded as a reconciliation item requiring a separate governance decision. |
| `currency_code` | `default_currency_code` (`default_currency` in the earlier DDD text) | **Preserved**; logical name documented, no rename. |
| `time_zone` | `default_timezone` (`timezone` in the earlier DDD text) | **Preserved**; logical name documented, no rename. |
| `date_format`, `time_format`, `default_language` | same | **Preserved**, no change. |
| `notification_enabled`, `workflow_enabled` | same | **Preserved**, no change. |

Additional PF-011 logical fields (number format, fiscal-year label format, currency decimal places and symbol position, working days/hours, module toggles, feature toggles) are **not** part of PF-011 CORE and are not added to the released entity until an approved contract change says so.

### 11.2 Superseded DDD shapes resolved in favour of BFS §9

| Superseded DDD shape | Resolved shape (BFS §9, normative for new tables) |
|----------------------|---------------------------------------------------|
| `tenant_preference: tenant_id, setting_key, setting_value` | `tenant_id, preference_key, preference_value, preference_type, preference_group, description, is_editable, edition_minimum` |
| `tenant_notification_preference: tenant_id, event_code, channel, is_enabled` (row per channel) | `tenant_id, event_type, module_code, email_enabled, sms_enabled, whatsapp_enabled, push_enabled, internal_enabled, notify_actor, notify_manager, notify_admin, custom_recipients` (column per channel) |
| `tenant_module_default: tenant_id, module_domain, defaults_json` | `tenant_id, module_code, entity_type, field_name, default_value` |
| `tenant_holiday_calendar: tenant_id, holiday_date, name, is_working_day` | `tenant_id, holiday_name, holiday_date, is_recurring, holiday_type, calendar_year` |

These shapes are recorded as resolved; the superseded forms are retained here for traceability and must not be used for implementation.

### 11.3 Platform-global tables

`platform_setting` (`id, key UK, value, description`) and `setting_catalogue` (`id, setting_key UK, value_type, default_value, description`) remain **platform-global** in §3.2 with no `tenant_id` and no RLS.

### 11.4 Lock semantics

There is **no** `lock_state` column. Per ADR-017 rule 9, `tenant_preference.is_editable = false` means the preference is Platform Admin only; `true` permits Tenant Admin configuration.

---

*© Euphoria Infotech (I) Limited — ELU-DDD-PF*
