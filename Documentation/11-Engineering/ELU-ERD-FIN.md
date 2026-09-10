# E-LinkUp ERD — Finance
**Document ID:** ELU-ERD-FIN  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-DDD-FIN, ELU-BFS-FIN, ELU-ERD-PRJ, ELU-ADR-015  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | FIN logical ERD |

---

## 1. Logical ERD

```mermaid
erDiagram
    customer ||--o{ invoice : billed
    project ||--o{ invoice : may_bill
    milestone ||--o{ invoice_line : triggers
    invoice ||--o{ invoice_line : has
    invoice ||--o{ payment_allocation : settled_by
    payment_receipt ||--o{ payment_allocation : allocates
    vendor ||--o{ vendor_payment : paid
    project ||--o{ vendor_payment : costs
    invoice ||--o{ credit_note : corrects
```

---

## 2. Immutability

ISSUED/PAID invoices: Restrict updates to non-financial metadata; corrections via credit_note. Payments: soft-void only with audit.

---

*© Euphoria Infotech (I) Limited — ELU-ERD-FIN*
