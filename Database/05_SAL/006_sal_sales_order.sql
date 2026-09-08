CREATE TABLE IF NOT EXISTS sales.sales_order (
    sales_order_id   UUID PRIMARY KEY,
    tenant_id        UUID NOT NULL REFERENCES core.tenant (tenant_id),
    so_number        VARCHAR(40) NOT NULL,
    quotation_id     UUID NOT NULL REFERENCES sales.quotation (quotation_id),
    opportunity_id   UUID REFERENCES crm.opportunity (opportunity_id),
    customer_id      UUID REFERENCES crm.customer (customer_id),
    status           VARCHAR(40) NOT NULL DEFAULT 'DRAFT',
    credit_hold      BOOLEAN NOT NULL DEFAULT FALSE,
    currency_code    VARCHAR(3) NOT NULL DEFAULT 'INR',
    subtotal         NUMERIC(18, 2) NOT NULL DEFAULT 0,
    discount_total   NUMERIC(18, 2) NOT NULL DEFAULT 0,
    tax_total        NUMERIC(18, 2) NOT NULL DEFAULT 0,
    grand_total      NUMERIC(18, 2) NOT NULL DEFAULT 0,
    confirmed_on     TIMESTAMPTZ,
    created_on       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on      TIMESTAMPTZ,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted       BOOLEAN NOT NULL DEFAULT FALSE,
    version_no       INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_so_tenant_number UNIQUE (tenant_id, so_number)
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_so_tenant_quotation
    ON sales.sales_order (tenant_id, quotation_id)
    WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS ix_so_tenant_status ON sales.sales_order (tenant_id, status);

GRANT SELECT, INSERT, UPDATE, DELETE ON sales.sales_order TO elu_app;

DO $so_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE sales.sales_order ENABLE ROW LEVEL SECURITY;
  ALTER TABLE sales.sales_order FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON sales.sales_order;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON sales.sales_order FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$so_rls$;
