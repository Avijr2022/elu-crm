-- PF-009 Roles & Permissions (RBAC) — Batch 1 rollback
-- Reverses 018_user_role_pf009.sql.
--
-- Does NOT drop core.role / core.permission / core.role_permission: those tables
-- are owned by SQLAlchemy Base.metadata.create_all (this repo's authoritative
-- DDL path), not by PF-009. Dropping core.user_role discards M2M assignments,
-- which is the intended effect of a rollback — core.users.role_id (the
-- transitional authoritative single role) is untouched, so no role is lost.

-- 1. Remove the RBAC RLS policy added to core.role_permission.
DO $pf009_rb$
BEGIN
  IF to_regclass('core.role_permission') IS NOT NULL THEN
    EXECUTE 'DROP POLICY IF EXISTS tenant_isolation ON core.role_permission';
    EXECUTE 'ALTER TABLE core.role_permission NO FORCE ROW LEVEL SECURITY';
    EXECUTE 'ALTER TABLE core.role_permission DISABLE ROW LEVEL SECURITY';
  END IF;
END
$pf009_rb$;

-- 2. Drop the PF-009 M2M table (core.user_role RLS enrolment lives in the
--    PF-003A loop in 012_rls_pf003a.sql; remove the row there too).
DROP TABLE IF EXISTS core.user_role CASCADE;
