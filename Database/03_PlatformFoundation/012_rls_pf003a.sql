-- PF-003A Enterprise Tenant Isolation (ADR-015)
-- 1) App role without BYPASSRLS (superuser connections must SET ROLE elu_app)
-- 2) ENABLE/FORCE RLS + tenant_isolation policies on tenant-scoped tables
-- Platform-global tables (edition*, feature_catalogue, permission) intentionally omitted.

DO $role$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'elu_app') THEN
    CREATE ROLE elu_app NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOLOGIN;
  END IF;
END
$role$;

-- Allow current login (e.g. elinkup) to assume elu_app for request sessions.
GRANT elu_app TO CURRENT_USER;

GRANT USAGE ON SCHEMA core TO elu_app;
GRANT USAGE ON SCHEMA crm TO elu_app;
GRANT USAGE ON SCHEMA audit TO elu_app;
GRANT USAGE ON SCHEMA master TO elu_app;
GRANT USAGE ON SCHEMA shared TO elu_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA core TO elu_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA crm TO elu_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA audit TO elu_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA master TO elu_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA shared TO elu_app;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA core TO elu_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA crm TO elu_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO elu_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA core
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO elu_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA crm
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO elu_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO elu_app;

DO $pf003a$
DECLARE
  r record;
  pol text;
BEGIN
  FOR r IN
    SELECT *
    FROM (VALUES
      ('core', 'tenant', false),
      ('core', 'tenant_contact', false),
      ('core', 'tenant_address', false),
      ('core', 'tenant_status_history', false),
      ('core', 'tenant_settings', false),
      ('core', 'organization', false),
      ('core', 'branch', false),
      ('core', 'branch_address', false),
      ('core', 'department', false),
      ('core', 'business_unit', false),
      ('core', 'users', false),
      ('core', 'user_invite', false),
      ('core', 'user_role', false),
      ('core', 'subscription', false),
      ('core', 'subscription_history', false),
      ('core', 'subscription_usage', false),
      ('crm', 'lead', false),
      ('crm', 'opportunity', false),
      ('core', 'role', true),
      ('core', 'idempotency_key', true),
      ('audit', 'audit_event', true)
    ) AS t(schema_name, table_name, nullable_tenant)
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

    IF r.nullable_tenant THEN
      pol := $p$
        current_setting('app.platform_context', true) = 'true'
        OR (
          tenant_id IS NOT NULL
          AND tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
      $p$;
    ELSE
      pol := $p$
        current_setting('app.platform_context', true) = 'true'
        OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
      $p$;
    END IF;

    EXECUTE format(
      'CREATE POLICY tenant_isolation ON %I.%I FOR ALL USING (%s) WITH CHECK (%s)',
      r.schema_name, r.table_name, pol, pol
    );
  END LOOP;
END
$pf003a$;
