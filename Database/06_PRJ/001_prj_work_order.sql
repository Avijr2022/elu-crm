CREATE SCHEMA IF NOT EXISTS projects;

CREATE TABLE IF NOT EXISTS projects.work_order (
    work_order_id   UUID PRIMARY KEY,
    tenant_id       UUID NOT NULL REFERENCES core.tenant (tenant_id),
    wo_number       VARCHAR(40) NOT NULL,
    opportunity_id  UUID REFERENCES crm.opportunity (opportunity_id),
    customer_id     UUID REFERENCES crm.customer (customer_id),
    status          VARCHAR(40) NOT NULL DEFAULT 'QUEUED',
    created_on      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on     TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    version_no      INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_wo_tenant_number UNIQUE (tenant_id, wo_number)
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_wo_tenant_opportunity
    ON projects.work_order (tenant_id, opportunity_id)
    WHERE opportunity_id IS NOT NULL AND is_deleted = FALSE;

GRANT USAGE ON SCHEMA projects TO elu_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA projects TO elu_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA projects
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO elu_app;

DO $prj_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE projects.work_order ENABLE ROW LEVEL SECURITY;
  ALTER TABLE projects.work_order FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON projects.work_order;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON projects.work_order FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$prj_rls$;
