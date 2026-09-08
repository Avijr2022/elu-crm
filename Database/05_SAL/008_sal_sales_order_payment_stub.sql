CREATE TABLE IF NOT EXISTS sales.sales_order_payment_stub (
    payment_stub_id   UUID PRIMARY KEY,
    tenant_id         UUID NOT NULL REFERENCES core.tenant (tenant_id),
    sales_order_id    UUID NOT NULL REFERENCES sales.sales_order (sales_order_id),
    payment_status    VARCHAR(40) NOT NULL DEFAULT 'RECORDED_STUB',
    amount            NUMERIC(18, 2) NOT NULL,
    currency_code     VARCHAR(3) NOT NULL,
    recorded_by       UUID REFERENCES core.users (user_id),
    recorded_on       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted        BOOLEAN NOT NULL DEFAULT FALSE,
    version_no        INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_so_payment_stub_order
    ON sales.sales_order_payment_stub (tenant_id, sales_order_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON sales.sales_order_payment_stub TO elu_app;

DO $stub_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE sales.sales_order_payment_stub ENABLE ROW LEVEL SECURITY;
  ALTER TABLE sales.sales_order_payment_stub FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON sales.sales_order_payment_stub;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON sales.sales_order_payment_stub FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$stub_rls$;
