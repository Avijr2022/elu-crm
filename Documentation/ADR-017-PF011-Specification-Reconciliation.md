# ADR-017 - PF-011 Specification Reconciliation

| Field | Value |
|---|---|
| Decision ID | ADR-017 |
| Title | PF-011 System Configuration specification reconciliation |
| Date | 2026-09-29 |
| Status | Accepted |
| Context | PF-011 implementation is authorized, but the approved BFS and downstream engineering specifications are not aligned. The PF-011 BFS defines six new tenant/platform settings tables and their fields, while ELU-DDD-PF defines materially different schemas for those tables. ELU-ERD-PF, ELU-API-PF, ELU-UI-PF and ELU-TST-PF currently do not contain complete PF-011 contracts. Existing tenant_settings is already implemented and consumed by the platform, so PF-011 must extend that existing entity rather than create a duplicate. |
| Reason | The constitution requires downstream engineering specifications to be authoritative and prohibits silently inventing or renaming columns. Implementation before reconciliation could create schema, API, UI and test contracts that disagree with the approved BFS or existing platform behavior. |
| Final Decision | Proposed: reconcile PF-011 through the governed specification chain before implementation. Preserve the existing tenant_settings entity and extend it deliberately. Reconcile the six new PF-011 tables across BFS, DDD, ERD, API, UI and TST. Preserve existing platform conventions for tenant RLS, platform/global settings, edition gating, audit events and Redis caching. No PF-011 implementation code or database migration is authorized until the reconciled downstream contracts are approved. |
| Impact | PF-011 implementation is temporarily blocked pending specification reconciliation. No existing PF-001 through PF-010 implementation is changed by this proposal. |
| Consequences / Follow-ups | 1. Resolve the BFS versus DDD field/schema differences for tenant_preference, tenant_notification_preference, tenant_module_default and tenant_holiday_calendar. 2. Define the PF-011 extension mapping for existing tenant_settings without renaming existing fields silently. 3. Add complete PF-011 contracts to ELU-ERD-PF, ELU-API-PF, ELU-UI-PF and ELU-TST-PF. 4. Verify permissions, edition gates, audit before/after snapshots, tenant RLS and Redis TTL/invalidation behavior in the reconciled contracts. 5. Obtain human approval of the reconciled specification before implementation. |

## 1. Known Specification Conflict

The PF-011 BFS currently specifies:

- tenant_settings: existing tenant settings plus fiscal, currency, working-time, module-toggle and feature-toggle fields.
- tenant_preference: preference_key, preference_value, preference_type, preference_group, description, is_editable, edition_minimum.
- tenant_notification_preference: event_type, module_code, channel flags and recipient controls.
- tenant_module_default: module_code, entity_type, field_name, default_value.
- tenant_holiday_calendar: holiday_name, holiday_date, is_recurring, holiday_type, calendar_year.
- platform_setting and setting_catalogue as global platform tables.

ELU-DDD-PF currently specifies materially different fields:

- tenant_preference: tenant_id, setting_key, setting_value.
- tenant_notification_preference: tenant_id, event_code, channel, is_enabled.
- tenant_module_default: tenant_id, module_domain, defaults_json.
- tenant_holiday_calendar: tenant_id, holiday_date, name, is_working_day.
- platform_setting: id, key, value, description.
- setting_catalogue: id, setting_key, value_type, default_value, description.

These differences must not be resolved by silently selecting or renaming fields during implementation.

## 2. Existing Platform Constraint

An existing tenant_settings ORM entity is already present and is used by tenant provisioning and authentication flows. PF-011 therefore extends the existing entity. A second tenant_settings table must not be created.

Existing fields include financial_year_start, currency_code, time_zone, date_format, time_format, default_language, notification_enabled and workflow_enabled. Any PF-011 mapping or extension must preserve existing consumers unless a separately approved contract change explicitly changes them.

## 3. Reconciliation Rules

The reconciliation shall:

1. Preserve the constitution and accepted ADRs.
2. Preserve existing PF-001 through PF-010 behavior unless explicitly changed by an approved decision.
3. Use the PF-011 BFS as the business-scope source while resolving its downstream schema contract against DDD/ERD/API/UI/TST.
4. Not invent or silently rename database columns.
5. Preserve the existing tenant RLS and platform/global security patterns.
6. Reuse the existing edition_feature/feature_catalogue mechanism.
7. Reuse write_audit_event() with before/after snapshots.
8. Reuse the existing Redis client with tenant-scoped cache keys, TTL 300 seconds, invalidation after successful writes and database fallback when Redis is unavailable.
9. Use tenant_preference.is_editable for lock semantics: false means Platform Admin only; true permits Tenant Admin configuration.
10. Keep PF-011 implementation blocked until the reconciled specification is explicitly approved.

## 4. Approval Gate

ADR-017 is Accepted following review and approval by the authorized human decision-maker.

No PF-011 implementation commit, migration, API implementation or schema mutation is authorized solely by creation of this proposal.
