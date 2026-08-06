# E-LinkUp ERD — Sales
**Document ID:** ELU-ERD-SAL  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-DDD-SAL, ELU-BFS-SAL, ELU-ERD-CRM, ELU-ADR-015, ELU-L2C-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | SAL logical ERD |

---

## 1. Logical ERD

```mermaid
erDiagram
    opportunity ||--o{ quotation : quotes
    customer ||--o{ quotation : billed
    quotation ||--o{ quotation_line : has
    quotation ||--o{ quotation_approval : has
    quotation ||--o{ quotation_version : versions
    quotation ||--o| sales_order : converts
    quotation ||--o{ quotation_proposal_link : links
    proposal ||--o{ quotation_proposal_link : links
    proposal ||--o{ proposal_version : versions
    proposal_version ||--o{ proposal_section : sections
    sales_order ||--o{ sales_order_line : has
    sales_order ||--o{ work_order : releases
    work_order ||--o{ work_order_line : has
    work_order ||--o{ work_order_project_link : starts
```

---

## 2. Spine

```text
Opportunity → Quotation (+ Proposal) → Sales Order → Work Order → Project (PRJ)
```

On Delete: Restrict across commercial spine; Cascade on owned lines/approvals.

---

## 3. RLS

All SAL tables: dual isolation **ADR-015**. Professional+ only.

---

*© Euphoria Infotech (I) Limited — ELU-ERD-SAL*
