# E-LinkUp Data Dictionary — Finance
**Document ID:** ELU-DDD-FIN  
**Version:** 1.0  
**Status:** Approved  
**Domain:** FIN  
**Related Documents:** ELU-BFS-FIN, ELU-ERD-FIN, V1-FIN-SRV-INT, ELU-DDD-PRJ, ELU-ADR-015, ELU-L2C-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | FIN field dictionary for Lead-to-Cash |

---

## 1. Rules

Tenant-scoped + common columns + RLS. Professional+.  
**Immutability:** Issued invoices / posted payments — no hard delete; limited field updates; credit notes for corrections (**ELU-CMP-001**).

---

## 2. Invoice (FIN-001)

| Table | Key fields |
|-------|------------|
| invoice | invoice_number UK, customer_id, project_id N, sales_order_id N, status, invoice_date, due_date, currency_code, totals, issued_on + common |
| invoice_line | invoice_id, line_no, description, qty, unit_price, tax_code, line_total, milestone_id N |
| invoice_tax_line | invoice_id, tax_code, tax_amount |
| credit_note / credit_note_line | mirrors invoice; original_invoice_id |
| invoice_billing_source | invoice_id, source_type (SO/MILESTONE/PROJECT), source_id |
| invoice_status_history | invoice_id, from_status, to_status |
| invoice_number_sequence | tenant_id, fiscal_year, next_value |
| billing_eligibility | source_type, source_id, is_eligible, eligible_on |

---

## 3. Payment (FIN-002)

| Table | Key fields |
|-------|------------|
| payment_receipt | receipt_number UK, customer_id, amount, currency_code, received_on, status, method + common |
| payment_allocation | payment_receipt_id, invoice_id, allocated_amount |
| payment_receipt_status_history | receipt_id, from_status, to_status |
| bank_statement_line | statement_date, amount, reference, matched |
| reconciliation_match | bank_statement_line_id, payment_receipt_id |
| dunning_schedule | name, days_after_due, channel |
| dunning_case | invoice_id, status, next_action_on |
| dunning_action_log | dunning_case_id, action, sent_on |

---

## 4. Vendor Settlement (FIN-003) — Professional+

| Table | Key fields |
|-------|------------|
| vendor | vendor_code UK, legal_name, gstin, status + common |
| vendor_payment | payment_number UK, vendor_id, project_id N, amount, status, paid_on + common |
| vendor_payment_line | vendor_payment_id, description, amount, work_order_id N |
| vendor_payment_tax | vendor_payment_id, gst_amount, tds_amount |
| vendor_payment_status_history | vendor_payment_id, from_status, to_status |
| vendor_payment_sequence | tenant_id, fiscal_year, next_value |

---

## 5. Tax (FIN-004)

| Table | Key fields |
|-------|------------|
| tax_rate | tax_code, rate_pct, effective_from/to |
| hsn_sac_code | code, description |
| tds_section / tds_rate | section_code, rate_pct |
| tax_registration | gstin, state_code, is_default |
| party_tax_profile | party_type (CUSTOMER/VENDOR), party_id, gstin, tds_applicable |
| transaction_tax_line | source_type, source_id, tax_code, tax_amount |
| tds_transaction | source_type, source_id, section_code, amount |
| tax_override_log | source_type, source_id, reason, actor_id |

---

*© Euphoria Infotech (I) Limited — ELU-DDD-FIN*
