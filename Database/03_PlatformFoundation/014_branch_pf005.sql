-- PF-005 Branch Management DDL (idempotent)
-- Creates core.branch and core.branch_address per ELU-BFS-PF-005 §7/§9 and ELU-DDD-PF §5.
--
-- Scope (approved groundwork): schema + constraints + indexes only.
-- EXPLICITLY DEFERRED — NOT implemented here:
--   * users.branch_id                     -> PF-008 Users & Identity
--   * branch-head assignment/validation   -> PF-008 (BR-PF-038 / AC-PF-005-04);
--                                           column branch_head_user_id is created NULLABLE,
--                                           with NO FK and NO validation logic
--   * department linkage                  -> PF-006 Department Management
--   * project -> branch linkage           -> deferred (BR-PF-037 cannot be enforced yet)
--   * NTF-PF-005-* notifications          -> deferred
--   * RPT-PF-005-* reports                -> deferred
-- RLS coverage for both tables is added in 012_rls_pf003a.sql (ADR-015).

CREATE TABLE IF NOT EXISTS core.branch (
    branch_id            UUID PRIMARY KEY,
    tenant_id            UUID NOT NULL REFERENCES core.tenant(tenant_id),
    organization_id      UUID NOT NULL REFERENCES core.organization(organization_id) ON DELETE RESTRICT,
    parent_branch_id     UUID REFERENCES core.branch(branch_id) ON DELETE RESTRICT,
    branch_code          VARCHAR(30)  NOT NULL,
    branch_name          VARCHAR(200) NOT NULL,
    branch_type          VARCHAR(32)  NOT NULL,
    branch_head_user_id  UUID,                       -- nullable; assignment/validation deferred to PF-008
    email                VARCHAR(150),
    phone                VARCHAR(20),
    branch_address_id    UUID,                       -- FK added below (SET NULL, mirrors fk_organization_address)
    timezone_id          VARCHAR(64),
    working_hours        VARCHAR(100),
    status               VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    opened_date          DATE,
    closed_date          DATE,
    created_by           UUID,
    modified_by          UUID,
    created_on           TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified_on          TIMESTAMPTZ,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted           BOOLEAN NOT NULL DEFAULT FALSE,
    version_no           INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS core.branch_address (
    branch_address_id    UUID PRIMARY KEY,
    tenant_id            UUID NOT NULL REFERENCES core.tenant(tenant_id),
    branch_id            UUID NOT NULL REFERENCES core.branch(branch_id) ON DELETE CASCADE,
    address_line_1       VARCHAR(255) NOT NULL,
    address_line_2       VARCHAR(255),
    city                 VARCHAR(100) NOT NULL,
    state                VARCHAR(100),
    postal_code          VARCHAR(20),
    country_code         VARCHAR(3) NOT NULL DEFAULT 'IN',
    latitude             NUMERIC(9,6),
    longitude            NUMERIC(9,6),
    created_by           UUID,
    modified_by          UUID,
    created_on           TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified_on          TIMESTAMPTZ,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted           BOOLEAN NOT NULL DEFAULT FALSE,
    version_no           INTEGER NOT NULL DEFAULT 1
);

-- Check constraints (guarded, mirrors ck_organization_* pattern)
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_branch_status') THEN
    ALTER TABLE core.branch
      ADD CONSTRAINT ck_branch_status
      CHECK (status IN ('DRAFT','ACTIVE','INACTIVE','ARCHIVED','CANCELLED'));
  END IF;
END
$ck$;

DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_branch_type') THEN
    ALTER TABLE core.branch
      ADD CONSTRAINT ck_branch_type
      CHECK (branch_type IN ('HEAD_OFFICE','BRANCH','REGIONAL_OFFICE'));
  END IF;
END
$ck$;

-- Foreign keys (guarded: tables may already exist via ORM create_all)
DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_branch_organization') THEN
    ALTER TABLE core.branch
      ADD CONSTRAINT fk_branch_organization
      FOREIGN KEY (organization_id)
      REFERENCES core.organization(organization_id)
      ON DELETE RESTRICT;
  END IF;
END
$fk$;

DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_branch_parent') THEN
    ALTER TABLE core.branch
      ADD CONSTRAINT fk_branch_parent
      FOREIGN KEY (parent_branch_id)
      REFERENCES core.branch(branch_id)
      ON DELETE RESTRICT;
  END IF;
END
$fk$;

DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_branch_address') THEN
    ALTER TABLE core.branch
      ADD CONSTRAINT fk_branch_address
      FOREIGN KEY (branch_address_id)
      REFERENCES core.branch_address(branch_address_id)
      ON DELETE SET NULL;
  END IF;
END
$fk$;

DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_branch_address_branch') THEN
    ALTER TABLE core.branch_address
      ADD CONSTRAINT fk_branch_address_branch
      FOREIGN KEY (branch_id)
      REFERENCES core.branch(branch_id)
      ON DELETE CASCADE;
  END IF;
END
$fk$;

-- One address row per branch (ELU-DDD-PF §5: branch_address.branch_id UK)
DO $uk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_branch_address_branch') THEN
    ALTER TABLE core.branch_address
      ADD CONSTRAINT uk_branch_address_branch UNIQUE (branch_id);
  END IF;
END
$uk$;

-- Soft-delete aware branch-code UK (ELU-DDD-PF §9): replace hard UK when present
DO $uk$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_branch_tenant_code') THEN
    ALTER TABLE core.branch DROP CONSTRAINT uk_branch_tenant_code;
  END IF;
END
$uk$;

CREATE UNIQUE INDEX IF NOT EXISTS uk_branch_tenant_code_active
  ON core.branch (tenant_id, branch_code)
  WHERE is_deleted = FALSE;

-- Indexes (partial, soft-delete aware — mirrors idx_organization_*)
CREATE INDEX IF NOT EXISTS idx_branch_tenant_status
  ON core.branch (tenant_id, status)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_branch_organization
  ON core.branch (tenant_id, organization_id)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_branch_parent
  ON core.branch (tenant_id, parent_branch_id)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_branch_address
  ON core.branch (branch_address_id)
  WHERE branch_address_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_branch_address_branch
  ON core.branch_address (tenant_id, branch_id)
  WHERE is_deleted = FALSE;
