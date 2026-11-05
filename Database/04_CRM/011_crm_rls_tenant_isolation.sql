-- CRM-011 Enterprise Tenant Isolation for the CRM schema (ADR-015)
--
-- Adds RLS to the 10 CRM tables that PF-003A does NOT own.
--
--   crm.customer, crm.customer_contact, crm.customer_address,
--   crm.customer_tax_registration, crm.customer_status_history,
--   crm.activity, crm.activity_link, crm.activity_type,
--   crm.activity_outcome, crm.opportunity_stage
--
-- crm.lead and crm.opportunity are DELIBERATELY ABSENT: they are owned by
-- 03_PlatformFoundation/012_rls_pf003a.sql, which is re-applied on every
-- application startup (migrate_pf011 -> apply_pf003a_ddl) and re-creates their
-- tenant_isolation policies. Writing those two tables here would be silently
-- overwritten and is out of scope.
--
-- Policy semantics are copied VERBATIM from 012_rls_pf003a.sql lines 97-100
-- (the ``nullable_tenant = false`` branch): the same two GUCs, the same
-- fail-closed behaviour, and the same platform-context bypass. No new GUC, role
-- or mechanism is introduced.
--
-- Every target table declares ``tenant_id UUID NOT NULL`` (see 003_crm_customer.sql,
-- 004_crm_activity.sql, 005_crm_customer_contact_address.sql, 006_crm_lookup.sql,
-- 007_crm_activity_outcome.sql, 008_crm_customer_tax_registration.sql and
-- 009_crm_customer_status_history.sql), so only the non-nullable expression applies.
--
-- Idempotent and side-effect free: ENABLE/FORCE are no-ops when already set and the
-- policy is dropped and re-created inside the single transaction opened by
-- ``apply_crm_ddl``. Grants, ownership, foreign keys and indexes are untouched.

DO $crm011$
DECLARE
  r record;
  pol text;
BEGIN
  FOR r IN
    SELECT *
    FROM (VALUES
      ('crm', 'customer'),
      ('crm', 'customer_contact'),
      ('crm', 'customer_address'),
      ('crm', 'customer_tax_registration'),
      ('crm', 'customer_status_history'),
      ('crm', 'activity'),
      ('crm', 'activity_link'),
      ('crm', 'activity_type'),
      ('crm', 'activity_outcome'),
      ('crm', 'opportunity_stage')
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

    pol := $p$
        current_setting('app.platform_context', true) = 'true'
        OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
      $p$;

    EXECUTE format(
      'CREATE POLICY tenant_isolation ON %I.%I FOR ALL USING (%s) WITH CHECK (%s)',
      r.schema_name, r.table_name, pol, pol
    );
  END LOOP;
END
$crm011$;
