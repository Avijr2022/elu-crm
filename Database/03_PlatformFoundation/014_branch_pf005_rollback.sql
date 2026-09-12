-- PF-005 Branch Management rollback (reverses ONLY what 014_branch_pf005.sql creates)
--
-- Drops, in reverse dependency order:
--   * core.branch indexes + FKs/CHECKs added by 014
--   * core.branch_address (and its FKs/UK/indexes)
--   * core.branch
--
-- It does NOT touch any pre-existing table, and it does NOT include seed/permission data.
--
-- IMPORTANT: RLS coverage for these two tables is registered in 012_rls_pf003a.sql and in
-- Backend/app/db/migrate_pf003a.py::RLS_TABLES. If this rollback is executed, those two
-- entries must also be removed BEFORE 012 is re-applied, otherwise the RLS loop will fail
-- because the tables no longer exist (intentional fail-loud behaviour — no silent skip).

DROP INDEX IF EXISTS core.uk_branch_tenant_code_active;
DROP INDEX IF EXISTS core.idx_branch_tenant_status;
DROP INDEX IF EXISTS core.idx_branch_organization;
DROP INDEX IF EXISTS core.idx_branch_parent;
DROP INDEX IF EXISTS core.idx_branch_address;
DROP INDEX IF EXISTS core.idx_branch_address_branch;

ALTER TABLE IF EXISTS core.branch DROP CONSTRAINT IF EXISTS fk_branch_address;
ALTER TABLE IF EXISTS core.branch DROP CONSTRAINT IF EXISTS fk_branch_parent;
ALTER TABLE IF EXISTS core.branch DROP CONSTRAINT IF EXISTS fk_branch_organization;

DROP TABLE IF EXISTS core.branch_address;
DROP TABLE IF EXISTS core.branch;
