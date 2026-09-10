CREATE TABLE IF NOT EXISTS sales.sales_order_line (
    sales_order_line_id UUID PRIMARY KEY,
    tenant_id           UUID NOT NULL REFERENCES core.tenant (tenant_id),
    sales_order_id      UUID NOT NULL REFERENCES sales.sales_order (sales_order_id),
    quotation_line_id   UUID REFERENCES sales.quotation_line (quotation_line_id),
    line_no             INTEGER NOT NULL,
    product_code        VARCHAR(40),
    description         VARCHAR(500) NOT NULL,
    qty                 NUMERIC(18, 4) NOT NULL DEFAULT 1,
    unit_price          NUMERIC(18, 2) NOT NULL DEFAULT 0,
    discount_pct        NUMERIC(5, 2) NOT NULL DEFAULT 0,
    tax_code            VARCHAR(20),
    line_total          NUMERIC(18, 2) NOT NULL DEFAULT 0,
    created_on          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on         TIMESTAMPTZ,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    version_no          INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_so_line_no UNIQUE (tenant_id, sales_order_id, line_no)
);

CREATE INDEX IF NOT EXISTS ix_so_line_header
    ON sales.sales_order_line (tenant_id, sales_order_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON sales.sales_order_line TO elu_app;

DO $so_line_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE sales.sales_order_line ENABLE ROW LEVEL SECURITY;
  ALTER TABLE sales.sales_order_line FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON sales.sales_order_line;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON sales.sales_order_line FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$so_line_rls$;
