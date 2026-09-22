-- PF-008 User & Identity Management CORE DDL (idempotent)
-- ELU-BFS-PF-008 §7/§9 + ELU-DDD-PF §5. Implementation map + decisions (D1..D13):
--   Documentation/PF008_CORE_IMPLEMENTATION_MAP.md
--
-- Scope (PF-008 CORE): account lifecycle state, invitation table, password-reset
-- challenge, session-invalidation marker and the PF-005/006/007 user linkage columns.
--
-- EXPLICITLY DEFERRED — NOT implemented here:
--   * core.user_credentials / core.user_password_history  -> D1: hash stays on core.users.password_hash
--   * core.user_session (refresh-token table)             -> D4: sessions_invalid_before marker instead
--   * core.user_mfa (TOTP enrolment)                      -> MFA out of CORE scope (BR-PF-058 deferred)
--   * core.user_role (RBAC grain)                          -> PF-009
--   * reporting / notification / scheduler (JOB-PF-008-01) -> deferred
-- RLS coverage for core.user_invite is added in 012_rls_pf003a.sql (PF-003A loop) and
-- app/db/migrate_pf003a.py::RLS_TABLES, mirroring PF-005/PF-006/PF-007.
--
-- Convention note: columns are added with ADD COLUMN IF NOT EXISTS; constraints and indexes
-- are created inside guarded DO blocks (mirrors 015_department_pf006.sql). Existing
-- core.users rows are never rewritten (all new columns are nullable or have defaults).

-- ---------------------------------------------------------------------------
-- 1. core.users — PF-008 CORE additive columns
-- ---------------------------------------------------------------------------
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS branch_id               UUID;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS department_id           UUID;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS business_unit_id        UUID;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS failed_login_count      INTEGER NOT NULL DEFAULT 0;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS locked_until            TIMESTAMPTZ;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS invited_at              TIMESTAMPTZ;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS activated_at            TIMESTAMPTZ;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS deactivated_at          TIMESTAMPTZ;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS password_changed_at     TIMESTAMPTZ;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS reset_token_hash        TEXT;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS reset_token_expires_at  TIMESTAMPTZ;
ALTER TABLE core.users ADD COLUMN IF NOT EXISTS sessions_invalid_before TIMESTAMPTZ;

-- Account lifecycle (ELU-BFS-PF-008 §5). Verified safe before apply: the only existing
-- values in the live database are ACTIVE and INACTIVE.
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_users_account_status') THEN
    ALTER TABLE core.users
      ADD CONSTRAINT ck_users_account_status
      CHECK (account_status IN ('INVITED','ACTIVE','INACTIVE','LOCKED','EXPIRED','CANCELLED'));
  END IF;
END
$ck$;

DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_users_failed_login_count') THEN
    ALTER TABLE core.users
      ADD CONSTRAINT ck_users_failed_login_count CHECK (failed_login_count >= 0);
  END IF;
END
$ck$;

-- Foreign keys (guarded: the columns may already exist from ORM create_all)
DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_users_branch') THEN
    ALTER TABLE core.users
      ADD CONSTRAINT fk_users_branch FOREIGN KEY (branch_id)
      REFERENCES core.branch (branch_id) ON DELETE SET NULL;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_users_department') THEN
    ALTER TABLE core.users
      ADD CONSTRAINT fk_users_department FOREIGN KEY (department_id)
      REFERENCES core.department (department_id) ON DELETE SET NULL;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_users_business_unit') THEN
    ALTER TABLE core.users
      ADD CONSTRAINT fk_users_business_unit FOREIGN KEY (business_unit_id)
      REFERENCES core.business_unit (business_unit_id) ON DELETE SET NULL;
  END IF;
END
$fk$;

-- Partial, soft-delete-aware linkage indexes (PF-005/PF-006 convention)
CREATE INDEX IF NOT EXISTS idx_users_branch
  ON core.users (branch_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_users_department
  ON core.users (department_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_users_business_unit
  ON core.users (business_unit_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_users_tenant_status
  ON core.users (tenant_id, account_status) WHERE is_deleted = FALSE;

-- ---------------------------------------------------------------------------
-- 2. core.user_invite — pending invitations (ELU-BFS-PF-008 §7, D2)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.user_invite (
    invite_id     UUID PRIMARY KEY,
    tenant_id     UUID NOT NULL,
    user_id       UUID NOT NULL,
    token_hash    TEXT NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    expires_on    TIMESTAMPTZ NOT NULL,
    created_by    UUID,
    created_on    TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified_on   TIMESTAMPTZ,
    used_on       TIMESTAMPTZ,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted    BOOLEAN NOT NULL DEFAULT FALSE,
    version_no    INTEGER NOT NULL DEFAULT 1
);

DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_user_invite_status') THEN
    ALTER TABLE core.user_invite
      ADD CONSTRAINT ck_user_invite_status
      CHECK (status IN ('ACTIVE','USED','EXPIRED','CANCELLED'));
  END IF;
END
$ck$;

DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_user_invite_tenant') THEN
    ALTER TABLE core.user_invite
      ADD CONSTRAINT fk_user_invite_tenant FOREIGN KEY (tenant_id)
      REFERENCES core.tenant (tenant_id) ON DELETE CASCADE;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_user_invite_user') THEN
    ALTER TABLE core.user_invite
      ADD CONSTRAINT fk_user_invite_user FOREIGN KEY (user_id)
      REFERENCES core.users (user_id) ON DELETE CASCADE;
  END IF;
END
$fk$;

DO $uk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_user_invite_token_hash') THEN
    ALTER TABLE core.user_invite
      ADD CONSTRAINT uk_user_invite_token_hash UNIQUE (token_hash);
  END IF;
END
$uk$;

-- At most one ACTIVE (pending) invitation per user (BR-PF-054 life-cycle safety).
CREATE UNIQUE INDEX IF NOT EXISTS uk_user_invite_active_user
  ON core.user_invite (user_id) WHERE status = 'ACTIVE';

CREATE INDEX IF NOT EXISTS idx_user_invite_tenant_user
  ON core.user_invite (tenant_id, user_id);
