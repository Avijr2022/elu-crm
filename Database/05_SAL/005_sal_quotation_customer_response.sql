CREATE TABLE IF NOT EXISTS sales.quotation_customer_response (
    quotation_customer_response_id UUID PRIMARY KEY,
    tenant_id                      UUID NOT NULL REFERENCES core.tenant (tenant_id),
    quotation_id                   UUID NOT NULL REFERENCES sales.quotation (quotation_id),
    response_type                  VARCHAR(20) NOT NULL,
    responded_on                   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    comment                        TEXT,
    recorded_by                    UUID REFERENCES core.users (user_id),
    created_on                     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active                      BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted                     BOOLEAN NOT NULL DEFAULT FALSE,
    version_no                     INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_quotation_cust_resp
    ON sales.quotation_customer_response (tenant_id, quotation_id, responded_on DESC);

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sales TO elu_app;

DO $sal_cust_resp_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE sales.quotation_customer_response ENABLE ROW LEVEL SECURITY;
  ALTER TABLE sales.quotation_customer_response FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON sales.quotation_customer_response;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON sales.quotation_customer_response FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$sal_cust_resp_rls$;
