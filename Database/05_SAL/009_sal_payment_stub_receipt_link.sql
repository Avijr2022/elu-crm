ALTER TABLE sales.sales_order_payment_stub
    ADD COLUMN IF NOT EXISTS payment_receipt_id UUID
        REFERENCES finance.payment_receipt (payment_receipt_id);

CREATE INDEX IF NOT EXISTS ix_so_payment_stub_receipt
    ON sales.sales_order_payment_stub (tenant_id, payment_receipt_id);
