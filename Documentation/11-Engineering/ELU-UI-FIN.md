# E-LinkUp UI Specification — Finance (Flutter)
**Document ID:** ELU-UI-FIN  
**Version:** 1.0  
**Status:** Approved  
**Related Documents:** ELU-API-FIN, ELU-BFS-FIN, V1-FIN-SRV-INT  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Frontend Lead | FIN Flutter inventory |

---

## Routes (Professional+)

| Route | Screen |
|-------|--------|
| `/finance/invoices` | InvoiceListPage |
| `/finance/invoices/:id` | InvoiceDetailPage |
| `/finance/invoices/new` | InvoiceCreateWizard |
| `/finance/payments` | PaymentListPage |
| `/finance/payments/:id` | PaymentAllocationPage |
| `/finance/dunning` | DunningCaseListPage |
| `/finance/vendors` | VendorListPage |
| `/finance/vendor-payments` | VendorPaymentListPage |
| `/finance/tax` | TaxConfigPage |
| `/finance/receivables` | ReceivablesAgeingDashboard |

Issued invoices: read-only banner; Credit Note action only.

---

*© Euphoria Infotech (I) Limited — ELU-UI-FIN*
