-- PF-006 Department Management rollback (reverses ONLY what 015_department_pf006.sql creates)
--
-- Drops, in reverse dependency order:
--   * core.department indexes + FKs/CHECKs added by 015
--   * core.department
--
-- It does NOT touch any pre-existing table, and it does NOT include seed/permission data.
-- No PF-003A or PF-005 object is modified.
--
-- IMPORTANT: RLS coverage for this table is registered in 012_rls_pf003a.sql and in
-- Backend/app/db/migrate_pf003a.py::RLS_TABLES. If this rollback is executed, those two
-- entries must also be removed BEFORE 012 is re-applied, otherwise the RLS loop will fail
-- because the table no longer exists (intentional fail-loud behaviour — no silent skip).

DROP INDEX IF EXISTS core.uk_department_tenant_code_active;
DROP INDEX IF EXISTS core.idx_department_tenant_status;
DROP INDEX IF EXISTS core.idx_department_organization;
DROP INDEX IF EXISTS core.idx_department_parent;
DROP INDEX IF EXISTS core.idx_department_branch;

ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS fk_department_branch;
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS fk_department_parent;
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS fk_department_organization;
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS fk_department_tenant;
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS ck_department_status;
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS ck_department_no_self_parent;
-- Auto-named variants (only present if the table was created by an ORM create_all)
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS department_tenant_id_fkey;
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS department_organization_id_fkey;
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS department_parent_department_id_fkey;
ALTER TABLE IF EXISTS core.department DROP CONSTRAINT IF EXISTS department_branch_id_fkey;

DROP TABLE IF EXISTS core.department;
