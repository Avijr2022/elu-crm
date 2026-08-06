# E-LinkUp UI Specification — Sales (Flutter)
**Document ID:** ELU-UI-SAL  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-API-SAL, ELU-BFS-SAL, V1-SAL-PRJ, ELU-EDM-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Frontend Lead | SAL Flutter inventory |

---

## Routes (Professional+)

| Route | Screen |
|-------|--------|
| `/sales/quotations` | QuotationListPage |
| `/sales/quotations/new` | QuotationCreatePage |
| `/sales/quotations/:id` | QuotationDetailPage |
| `/sales/quotations/:id/approve` | QuotationApprovalInbox |
| `/sales/proposals` | ProposalListPage |
| `/sales/proposals/:id` | ProposalEditorPage |
| `/sales/orders` | SalesOrderListPage |
| `/sales/orders/:id` | SalesOrderDetailPage |
| `/sales/orders/credit-hold` | CreditHoldQueuePage |
| `/sales/work-orders` | WorkOrderListPage |
| `/sales/work-orders/:id` | WorkOrderDetailPage |
| `/sales/work-orders/:id/create-project` | CreateProjectAction |

Hide entire `/sales` nav for Community.

---

*© Euphoria Infotech (I) Limited — ELU-UI-SAL*
