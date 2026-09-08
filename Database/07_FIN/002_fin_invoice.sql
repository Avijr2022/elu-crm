CREATE TABLE IF NOT EXISTS finance.invoice (
    invoice_id       UUID PRIMARY KEY,
    tenant_id        UUID NOT NULL REFERENCES core.tenant (tenant_id),
    invoice_number   VARCHAR(40) NOT NULL,
    customer_id      UUID REFERENCES crm.customer (customer_id),
    sales_order_id   UUID REFERENCES sales.sales_order (sales_order_id),
    status           VARCHAR(40) NOT NULL DEFAULT 'DRAFT',
    invoice_date     DATE NOT NULL DEFAULT CURRENT_DATE,
    currency_code    VARCHAR(3) NOT NULL DEFAULT 'INR',
    subtotal         NUMERIC(18, 2) NOT NULL DEFAULT 0,
    tax_total        NUMERIC(18, 2) NOT NULL DEFAULT 0,
    grand_total      NUMERIC(18, 2) NOT NULL DEFAULT 0,
    issued_on        TIMESTAMPTZ,
    created_on       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on      TIMESTAMPTZ,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted       BOOLEAN NOT NULL DEFAULT FALSE,
    version_no       INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_invoice_tenant_number UNIQUE (tenant_id, invoice_number)
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_invoice_tenant_so
    ON finance.invoice (tenant_id, sales_order_id)
    WHERE is_deleted = FALSE AND sales_order_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_invoice_tenant_status ON finance.invoice (tenant_id, status);

GRANT SELECT, INSERT, UPDATE, DELETE ON finance.invoice TO elu_app;

DO $inv_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE finance.invoice ENABLE ROW LEVEL SECURITY;
  ALTER TABLE finance.invoice FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON finance.invoice;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON finance.invoice FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$inv_rls$;
