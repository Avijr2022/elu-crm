-- SAL tenant isolation (ADR-015) — idempotent
GRANT USAGE ON SCHEMA sales TO elu_app;

DO $sal_rls$
DECLARE
  r record;
  pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;

  FOR r IN
    SELECT * FROM (VALUES
      ('sales', 'quotation'),
      ('sales', 'quotation_line')
    ) AS t(schema_name, table_name)
  LOOP
    EXECUTE format(
      'ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY',
      r.schema_name, r.table_name
    );
    EXECUTE format(
      'ALTER TABLE %I.%I FORCE ROW LEVEL SECURITY',
      r.schema_name, r.table_name
    );
    EXECUTE format(
      'DROP POLICY IF EXISTS tenant_isolation ON %I.%I',
      r.schema_name, r.table_name
    );
    EXECUTE format(
      'CREATE POLICY tenant_isolation ON %I.%I FOR ALL USING (%s) WITH CHECK (%s)',
      r.schema_name, r.table_name, pol, pol
    );
  END LOOP;
END
$sal_rls$;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sales TO elu_app;
