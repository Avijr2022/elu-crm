# E-LinkUp Data Dictionary — Sales
**Document ID:** ELU-DDD-SAL  
**Version:** 1.0  
**Status:** Approved  
**Domain:** SAL  
**Related Documents:** ELU-BFS-SAL, ELU-ERD-SAL, ELU-EFS-001, V1-SAL-PRJ, ELU-DDD-PF, ELU-ADR-015, ELU-L2C-001, ELU-DOC-001  

---

## Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-08-06 | EIIP / Data Architect | SAL field dictionary for Lead-to-Cash |

---

## 1. Rules

All tables tenant-scoped; common columns per **ELU-DDD-PF §2**; RLS **ADR-015**. Edition: Professional+ (**ELU-EDM-001**).

---

## 2. Quotation (SAL-001)

| Table | Key fields |
|-------|------------|
| quotation | quotation_number UK(tenant,active), opportunity_id, customer_id, owner_id, status, currency_code, subtotal, discount_total, tax_total, grand_total, valid_until, version_no_doc, is_current, + common |
| quotation_line | quotation_id, line_no, product_code, description, qty, unit_price, discount_pct, tax_code, line_total |
| quotation_version | quotation_id, version_no, is_current_approved, snapshot_json |
| quotation_approval | quotation_id, step_no, approver_id, decision, decided_on, comment |
| quotation_customer_response | quotation_id, response_type (ACCEPT/REJECT/CHANGE), responded_on, comment |
| quotation_tax_line | quotation_id, tax_code, taxable_amount, tax_amount |
| quotation_attachment_link | quotation_id, storage_key, document_type |
| quotation_status_history | quotation_id, from_status, to_status, actor_id, changed_on |
| quotation_number_sequence | tenant_id, fiscal_year, next_value |

---

## 3. Proposal (SAL-002)

| Table | Key fields |
|-------|------------|
| proposal | proposal_number, opportunity_id, customer_id, status, current_version_id + common |
| proposal_version | proposal_id, version_no, status, body_summary, is_current |
| proposal_section | proposal_version_id, section_code, title, content_md, sequence_no |
| proposal_template | code, name, default_sections_json |
| proposal_version_approval | proposal_version_id, approver_id, decision, decided_on |
| quotation_proposal_link | quotation_id, proposal_id, is_primary |
| proposal_attachment_link | proposal_version_id, storage_key |

---

## 4. Sales Order (SAL-003)

| Table | Key fields |
|-------|------------|
| sales_order | so_number UK, quotation_id, customer_id, opportunity_id, status, credit_hold, currency_code, totals, confirmed_on + common |
| sales_order_line | sales_order_id, line_no, description, qty, unit_price, discount_pct, tax_code, line_total |
| sales_order_approval | sales_order_id, step_no, approver_id, decision |
| sales_order_credit_check | sales_order_id, result (PASS/HOLD/FAIL), checked_by, checked_on, reason |
| sales_order_status_history | sales_order_id, from_status, to_status, actor_id |
| sales_order_tax_line | sales_order_id, tax_code, tax_amount |
| sales_order_number_sequence | tenant_id, fiscal_year, next_value |

---

## 5. Work Order (SAL-004)

| Table | Key fields |
|-------|------------|
| work_order | wo_number UK, sales_order_id, pm_user_id, status, planned_start, planned_end + common |
| work_order_line | work_order_id, sales_order_line_id, description, qty, sequence_no |
| work_order_approval | work_order_id, approver_id, decision |
| work_order_status_history | work_order_id, from_status, to_status |
| work_order_project_link | work_order_id, project_id |
| work_order_number_sequence | tenant_id, fiscal_year, next_value |

---

## 6. Indexes

UK(tenant_id, *_number) WHERE NOT is_deleted; IDX(tenant_id, status); IDX(tenant_id, customer_id); IDX(tenant_id, opportunity_id).

---

*© Euphoria Infotech (I) Limited — ELU-DDD-SAL*
