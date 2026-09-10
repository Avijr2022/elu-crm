# E-LinkUp Entity Relationship Diagram — Platform Foundation
**Document ID:** ELU-ERD-PF  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-DDD-PF, ELU-BFS-PF, ELU-ADR-001 (ADR-001, ADR-015), ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | Initial PF logical ERD |

---

## 1. Logical ERD

```mermaid
erDiagram
    edition ||--o{ edition_feature : has
    edition ||--o{ edition_limit : has
    edition ||--o{ tenant : assigned
    edition ||--o{ subscription : binds
    tenant ||--o{ tenant_contact : has
    tenant ||--o| tenant_branding : has
    tenant ||--o| tenant_settings : has
    tenant ||--o| tenant_security : has
    tenant ||--o| tenant_localization : has
    tenant ||--o{ tenant_address : has
    tenant ||--o{ organization : owns
    tenant ||--o{ subscription : has
    tenant ||--o{ users : has
    tenant ||--o{ role : has
    tenant ||--o{ audit_event : logs
    organization ||--o{ branch : has
    organization ||--o{ department : has
    organization ||--o{ business_unit : has
    branch ||--o{ users : home
    department ||--o{ users : assigns
    users ||--o| user_credentials : has
    users ||--o{ user_session : has
    users ||--o{ user_role : has
    role ||--o{ user_role : grants
    role ||--o{ role_permission : maps
    permission ||--o{ role_permission : used
    subscription ||--o{ subscription_history : tracks
    subscription ||--o{ subscription_usage : meters
    audit_event ||--o{ audit_event_detail : details
```

---

## 2. Physical Notes

| Rule | Implementation |
|------|----------------|
| Tenant scope | All business tables except edition/permission/feature_catalogue/platform_* |
| FK delete | Restrict on masters with children; Cascade on owned children (contacts, sessions) |
| Soft delete | `is_deleted`; unique constraints are partial |
| RLS | All tenant-scoped tables — **ADR-015** |
| Special | `tenant` table RLS: `id = current_setting('app.tenant_id')::uuid` OR platform context |

---

## 3. Cardinality Summary

| Parent | Child | Card | On Delete |
|--------|-------|------|-----------|
| edition | tenant | 1:N | Restrict |
| tenant | organization | 1:N | Restrict |
| organization | branch | 1:N | Restrict |
| organization | department | 1:N | Restrict |
| tenant | users | 1:N | Restrict |
| users | user_credentials | 1:1 | Cascade |
| role | role_permission | 1:N | Cascade |
| tenant | subscription | 1:N | Restrict |
| tenant | audit_event | 1:N | Restrict (purge via retention job) |

---

*© Euphoria Infotech (I) Limited — ELU-ERD-PF*
