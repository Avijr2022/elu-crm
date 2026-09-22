-- PF-009 Roles & Permissions (RBAC) — Batch 1 DDL (idempotent)
-- ELU-BFS-PF-009 §7/§9 + ELU-DDD-PF §5.
--
-- Scope (PF-009 Batch 1 — foundation only):
--   * core.user_role M2M user<->role assignment table
--   * RBAC tenant-isolation RLS for core.role_permission
--   * guarded unique constraint + indexes for core.user_role
--
-- EXPLICITLY DEFERRED — NOT implemented here:
--   * RBAC API surface (/api/v1/rbac/*)            -> later authorised batch
--   * multi-role JWT/auth resolution               -> later authorised batch
--   * permission-grain rollout on released modules -> later authorised batch
--   * reports / notifications (RPT/NTF-PF-009-*)   -> deferred
--   * frontend (RoleListScreen etc.)               -> not authorised
--
-- IMPORTANT — this repository's authoritative DDL path is SQLAlchemy
-- `Base.metadata.create_all` (app/main.py). core.role / core.permission /
-- core.role_permission are created by the ORM, NOT by SQL here. The guarded
-- blocks below only add what create_all cannot express idempotently, and the
-- CREATE TABLE IF NOT EXISTS is a safety net that is a no-op in the normal
-- bootstrap order (create_all runs first).
--
-- core.role_permission deliberately has NO tenant_id column (verified
-- architecture decision — see ELU-DDD-PF §5 vs the ORM in
-- app/models/pf/entities.py). Its RLS policy therefore derives tenant scope by
-- joining core.role; no tenant_id is added to that table by this batch.
--
-- core.permission stays OUT of RLS: it is a platform-global catalogue
-- (permission_code is globally UNIQUE, no tenant_id) and is intentionally
-- omitted by 012_rls_pf003a.sql.
--
-- RLS for core.user_role is enrolled via the PF-003A loop in
-- 012_rls_pf003a.sql and app/db/migrate_pf003a.py::RLS_TABLES, mirroring
-- PF-005/PF-006/PF-007/PF-008.
--
-- The core.user_role backfill from core.users.role_id is executed by
-- app/db/migrate_pf009.py (idempotent, does not delete or rewrite users rows).

-- ---------------------------------------------------------------------------
-- 1. core.user_role — PF-009 M2M foundation (safety net; ORM is authoritative)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.user_role (
    user_role_id uuid        PRIMARY KEY,
    tenant_id    uuid        NOT NULL REFERENCES core.tenant (tenant_id),
    user_id      uuid        NOT NULL REFERENCES core.users (user_id),
    role_id      uuid        NOT NULL REFERENCES core.role (role_id),
    is_primary   boolean     NOT NULL DEFAULT true,
    created_on   timestamptz NOT NULL DEFAULT now(),
    modified_on  timestamptz
);

-- Column-level safety for pre-existing/partial tables (mirrors PF-005..PF-008).
ALTER TABLE core.user_role ADD COLUMN IF NOT EXISTS tenant_id   uuid;
ALTER TABLE core.user_role ADD COLUMN IF NOT EXISTS user_id     uuid;
ALTER TABLE core.user_role ADD COLUMN IF NOT EXISTS role_id     uuid;
ALTER TABLE core.user_role ADD COLUMN IF NOT EXISTS is_primary  boolean NOT NULL DEFAULT true;
ALTER TABLE core.user_role ADD COLUMN IF NOT EXISTS created_on  timestamptz NOT NULL DEFAULT now();
ALTER TABLE core.user_role ADD COLUMN IF NOT EXISTS modified_on timestamptz;

-- Unique assignment: a user holds a given role at most once.
DO $pf009_uk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_user_role') THEN
    ALTER TABLE core.user_role
      ADD CONSTRAINT uk_user_role UNIQUE (user_id, role_id);
  END IF;
END
$pf009_uk$;

CREATE INDEX IF NOT EXISTS idx_user_role_tenant ON core.user_role (tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_role_user   ON core.user_role (user_id);
CREATE INDEX IF NOT EXISTS idx_user_role_role   ON core.user_role (role_id);

-- ---------------------------------------------------------------------------
-- 2. RBAC tenant isolation — core.role_permission
--    No tenant_id column on this table, so the tenant scope is derived through
--    core.role. core.role is already RLS-enrolled (nullable-tenant policy), so
--    the correlated EXISTS below is itself evaluated under that policy.
-- ---------------------------------------------------------------------------
DO $pf009_rls$
BEGIN
  IF to_regclass('core.role_permission') IS NOT NULL THEN
    EXECUTE 'ALTER TABLE core.role_permission ENABLE ROW LEVEL SECURITY';
    EXECUTE 'ALTER TABLE core.role_permission FORCE ROW LEVEL SECURITY';
    EXECUTE 'DROP POLICY IF EXISTS tenant_isolation ON core.role_permission';
    EXECUTE $pf009_pol$
      CREATE POLICY tenant_isolation ON core.role_permission FOR ALL
      USING (
        current_setting('app.platform_context', true) = 'true'
        OR EXISTS (
          SELECT 1
          FROM core.role r
          WHERE r.role_id = role_permission.role_id
            AND r.tenant_id IS NOT NULL
            AND r.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
      )
      WITH CHECK (
        current_setting('app.platform_context', true) = 'true'
        OR EXISTS (
          SELECT 1
          FROM core.role r
          WHERE r.role_id = role_permission.role_id
            AND r.tenant_id IS NOT NULL
            AND r.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
      )
    $pf009_pol$;
  END IF;
END
$pf009_rls$;
