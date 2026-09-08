CREATE TABLE IF NOT EXISTS sales.quotation_status_history (
    quotation_status_history_id UUID PRIMARY KEY,
    tenant_id                   UUID NOT NULL REFERENCES core.tenant (tenant_id),
    quotation_id                UUID NOT NULL REFERENCES sales.quotation (quotation_id),
    from_status                 VARCHAR(40) NOT NULL,
    to_status                   VARCHAR(40) NOT NULL,
    actor_id                    UUID REFERENCES core.users (user_id),
    reason                      TEXT,
    changed_on                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted                  BOOLEAN NOT NULL DEFAULT FALSE,
    version_no                  INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_quotation_status_hist
    ON sales.quotation_status_history (tenant_id, quotation_id, changed_on DESC);

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sales TO elu_app;

DO $sal_hist_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE sales.quotation_status_history ENABLE ROW LEVEL SECURITY;
  ALTER TABLE sales.quotation_status_history FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON sales.quotation_status_history;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON sales.quotation_status_history FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$sal_hist_rls$;
