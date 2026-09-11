# E-LinkUp UI Specification — Platform Foundation (Flutter)
**Document ID:** ELU-UI-PF  
**Version:** 1.1  
**Status:** Approved  
**Related Documents:** ELU-BFS-PF, ELU-EFS-001, ELU-API-PF, ELU-EDM-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Frontend Lead | PF Flutter screen inventory for v1.0 |
| 1.1 | 2026-09-11 | EIIP / Frontend Lead | HD-11: Organization route/screen aligned to implemented `/organizations` → `OrganizationsPage` (Tenant Admin only) |

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
| `/audit` | AuditEventListPage | Tenant Admin | Retention banner |

---

## 2. UX Rules

- Hide edition-gated nav items **and** handle API 403 gracefully.
- Lists: server pagination, search, empty/error states.
- Wizards: validate per step; show Idempotency errors on retry for tenant create.
- Web + Android share routes unless noted.

---

*© Euphoria Infotech (I) Limited — ELU-UI-PF*
