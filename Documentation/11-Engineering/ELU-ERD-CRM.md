# E-LinkUp Entity Relationship Diagram — CRM
**Document ID:** ELU-ERD-CRM  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-DDD-CRM, ELU-BFS-CRM, ELU-ERD-PF, ELU-ADR-015, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | Initial CRM logical ERD |

---

## 1. Logical ERD

```mermaid
erDiagram
    tenant ||--o{ lead : owns
    tenant ||--o{ opportunity : owns
    tenant ||--o{ customer : owns
    tenant ||--o{ activity : owns
    lead_source ||--o{ lead : sources
    lead ||--o{ lead_contact : has
    lead ||--o{ lead_attachment : has
    lead ||--o{ lead_assignment_history : tracks
    lead ||--o| lead_conversion_log : converts
    lead ||--o| opportunity : becomes
    lead ||--o| customer : becomes
    customer ||--o{ opportunity : parent
    customer ||--o{ customer_contact : has
    customer ||--o{ customer_address : has
    opportunity ||--o{ opportunity_stage_history : tracks
    opportunity ||--o{ opportunity_team_member : team
    opportunity_stage ||--o{ opportunity : stage
    activity ||--o{ activity_link : links
    activity ||--o{ activity_attendee : has
    activity ||--o{ activity_reminder : has
    lead ||--o{ activity_link : linked
    opportunity ||--o{ activity_link : linked
    customer ||--o{ activity_link : linked
```

---

## 2. Conversion Spine

```text
lead ──convert──► customer (find or create)
              └──► opportunity (source_lead_id, customer_id)
```

On convert: write `lead_conversion_log`; set lead.status = CONVERTED; lock lead for commercial edits.

---

## 3. Cardinality & Delete Policy

| Parent | Child | Card | On Delete |
|--------|-------|------|-----------|
| tenant | lead / opportunity / customer / activity | 1:N | Restrict |
| lead | lead_contact | 1:N | Cascade |
| lead | opportunity | 0..1 | Restrict |
| customer | opportunity | 1:N | Restrict |
| opportunity | opportunity_stage_history | 1:N | Cascade |
| activity | activity_link | 1:N | Cascade |
| customer | customer_contact | 1:N | Cascade |

Polymorphic `activity_link`: enforce same `tenant_id` as parent activity and target entity in service layer.

---

## 4. RLS

All CRM tables: RLS + repository filters (**ADR-015**).

---

*© Euphoria Infotech (I) Limited — ELU-ERD-CRM*
