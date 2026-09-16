-- PF-007 Business Unit Management rollback (reverses ONLY what 016_business_unit_pf007.sql creates)
--
-- Drops, in reverse dependency order:
--   * core.business_unit indexes + FKs/CHECKs added by 016
--   * core.business_unit
--
-- It does NOT touch any pre-existing table, and it does NOT include seed/permission data.
-- No PF-003A / PF-004 / PF-005 / PF-006 object is modified.
--
-- IMPORTANT: RLS coverage for this table is registered in 012_rls_pf003a.sql and in
-- Backend/app/db/migrate_pf003a.py::RLS_TABLES. If this rollback is executed, those two
-- entries must also be removed BEFORE 012 is re-applied, otherwise the RLS loop will fail
-- because the table no longer exists (intentional fail-loud behaviour — no silent skip).

DROP INDEX IF EXISTS core.uk_business_unit_tenant_code_active;
DROP INDEX IF EXISTS core.idx_business_unit_tenant_status;
DROP INDEX IF EXISTS core.idx_business_unit_organization;

ALTER TABLE IF EXISTS core.business_unit DROP CONSTRAINT IF EXISTS fk_business_unit_organization;
ALTER TABLE IF EXISTS core.business_unit DROP CONSTRAINT IF EXISTS fk_business_unit_tenant;
ALTER TABLE IF EXISTS core.business_unit DROP CONSTRAINT IF EXISTS ck_business_unit_status;
-- Auto-named variants (only present if the table was created by an ORM create_all)
ALTER TABLE IF EXISTS core.business_unit DROP CONSTRAINT IF EXISTS business_unit_tenant_id_fkey;
ALTER TABLE IF EXISTS core.business_unit DROP CONSTRAINT IF EXISTS business_unit_organization_id_fkey;

DROP TABLE IF EXISTS core.business_unit;
