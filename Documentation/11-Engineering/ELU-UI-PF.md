# E-LinkUp UI Specification — Platform Foundation (Flutter)
**Document ID:** ELU-UI-PF  
**Version:** 1.2
**Status:** Approved  
**Related Documents:** ELU-BFS-PF, ELU-EFS-001, ELU-API-PF, ELU-EDM-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Frontend Lead | PF Flutter screen inventory for v1.0 |
| 1.1 | 2026-09-11 | EIIP / Frontend Lead | HD-11: Organization route/screen aligned to implemented `/organizations` → `OrganizationsPage` (Tenant Admin only) |
| 1.2 | 2026-09-29 | EIIP / Engineering | PF-011 System Configuration UI reconciliation |

---

## 1. Routes

| Route | Screen | Actor | Notes |
|-------|--------|-------|-------|
| `/login` | LoginPage | All | JWT login |
| `/activate` | ActivationPage | Invitee | Token + password |
| `/platform/tenants` | TenantListPage | Platform Admin | |
| `/platform/tenants/new` | TenantRegisterWizard | Platform Admin | Multi-step |
| `/platform/tenants/:id` | TenantViewPage | Platform Admin | Actions: suspend, resend |
| `/platform/editions` | EditionListPage | Platform Admin | |
| `/platform/subscriptions` | SubscriptionListPage | Platform Admin | |
| `/organizations` | OrganizationsPage | Tenant Admin (nav + route hidden for other roles) | HD-11 alignment |
| `/org/branches` | BranchListPage | Tenant Admin | Professional+ |
| `/org/departments` | DepartmentListPage | Tenant Admin | |
| `/org/business-units` | BusinessUnitListPage | Tenant Admin | Professional+ |
| `/users` | UserListPage | Tenant Admin | |
| `/users/invite` | UserInvitePage | Tenant Admin | |
| `/roles` | RoleListPage | Tenant Admin | |
| `/settings` | TenantSettingsPage | Tenant Admin | |
| `/settings/security` | TenantSecurityPage | Tenant Admin | MFA/SSO per edition |
| `/settings/branding` | TenantBrandingPage | Tenant Admin | Edition-gated |
| `/settings/preferences` | BusinessPreferencesPage | Tenant Admin | `settings.read`; configuration requires `settings.configure` |
| `/settings/notifications` | NotificationPreferencesPage | Tenant Admin | Configuration requires `settings.configure` |
| `/settings/module-defaults` | ModuleDefaultsPage | Tenant Admin | Configuration requires `settings.configure` |
| `/settings/holidays` | HolidayCalendarPage | Tenant Admin | Configuration requires `settings.configure` |
| `/settings/catalogue` | SettingsCataloguePage | Platform Admin | Settings catalogue |
| `/platform/settings` | PlatformSettingsPage | Platform Admin | `platform_settings.read` / `platform_settings.configure` |
| `/audit` | AuditEventListPage | Tenant Admin | Retention banner |

**PF-011 System Configuration:** Business Preferences, Notification Preferences, Module Defaults, Holiday Calendar, Settings Catalogue, Platform Settings, and Feature Toggles within `TenantSettingsPage`. Feature Toggles are edition-gated and do not introduce a separate feature-toggle API route.

**PF-011 behavior:** Use `settings.read` / `settings.configure` for tenant settings and `platform_settings.read` / `platform_settings.configure` for platform settings. `is_editable=false` is Platform Admin-only; no separate `lock_state` is introduced. Edition-forbidden controls remain unavailable and API `403` responses are handled gracefully. Reset-to-defaults requires explicit Tenant Admin confirmation. Settings changes provide success/error feedback and are audited with before/after field differences. The existing API cache contract uses a 300-second TTL with successful-write invalidation; the UI does not implement a separate cache.
**PF-005 Branch screens (specified — NOT implemented; ELU-BFS-PF-005 §11):** Branch List · Branch Create · Branch Edit · Branch View · Branch Search · Branch Hierarchy · Branch History — Tenant Admin, Professional+ (BR-PF-034). The `/org/branches` → `BranchListPage` route above is **specification only**; no branch pages exist under `Frontend/lib/` yet.

---

## 2. UX Rules

- Hide edition-gated nav items **and** handle API 403 gracefully.
- Lists: server pagination, search, empty/error states.
- Wizards: validate per step; show Idempotency errors on retry for tenant create.
- Web + Android share routes unless noted.

---

*© Euphoria Infotech (I) Limited — ELU-UI-PF*
