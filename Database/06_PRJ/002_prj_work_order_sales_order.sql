ALTER TABLE projects.work_order
    ADD COLUMN IF NOT EXISTS sales_order_id UUID REFERENCES sales.sales_order (sales_order_id);

CREATE INDEX IF NOT EXISTS ix_wo_tenant_sales_order
    ON projects.work_order (tenant_id, sales_order_id)
    WHERE sales_order_id IS NOT NULL AND is_deleted = FALSE;
