CREATE TABLE IF NOT EXISTS finance.payment_receipt (
    payment_receipt_id   UUID PRIMARY KEY,
    tenant_id            UUID NOT NULL REFERENCES core.tenant (tenant_id),
    receipt_number       VARCHAR(40) NOT NULL,
    customer_id          UUID REFERENCES crm.customer (customer_id),
    sales_order_id       UUID REFERENCES sales.sales_order (sales_order_id),
    amount               NUMERIC(18, 2) NOT NULL,
    currency_code        VARCHAR(3) NOT NULL,
    received_on          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status               VARCHAR(40) NOT NULL DEFAULT 'RECORDED',
    method               VARCHAR(40) NOT NULL DEFAULT 'STUB',
    created_on           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on          TIMESTAMPTZ,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted           BOOLEAN NOT NULL DEFAULT FALSE,
    version_no           INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_receipt_tenant_number UNIQUE (tenant_id, receipt_number)
);

CREATE INDEX IF NOT EXISTS ix_payment_receipt_tenant_so
    ON finance.payment_receipt (tenant_id, sales_order_id);

GRANT USAGE ON SCHEMA finance TO elu_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON finance.payment_receipt TO elu_app;

DO $fin_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE finance.payment_receipt ENABLE ROW LEVEL SECURITY;
  ALTER TABLE finance.payment_receipt FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON finance.payment_receipt;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON finance.payment_receipt FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$fin_rls$;
