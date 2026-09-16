-- PF-006 Department Management DDL (idempotent)
-- Creates core.department per ELU-BFS-PF-006 §7/§9 and ELU-DDD-PF §5.
--
-- Scope (approved Batch 1): schema + constraints + indexes ONLY.
-- EXPLICITLY DEFERRED — NOT implemented here:
--   * users.department_id and the department -> users linkage  -> PF-008 Users & Identity
--   * department-head assignment/validation (BR-PF-043)        -> PF-008;
--                                           column department_head_user_id is created NULLABLE,
--                                           with NO FK and NO validation logic
--   * hierarchy depth (BR-PF-041) / circular-parent rule (BR-PF-042) -> API/service layer (later batch)
--   * persisted hierarchy level/path columns                   -> NOT created (C-N2: derived at read time)
--   * department address structures                            -> NOT in the specification (C-N6)
--   * NTF-PF-006-* notifications                               -> deferred
--   * RPT-PF-006-01/02 reports                                 -> deferred
--   * AC-PF-006-04 approval workflow (CPS-001)                 -> deferred / non-demonstrable
--   * edition gating / feature / limit                         -> NOT required (ELU-EDM-001: all editions)
-- RLS coverage for this table is added in 012_rls_pf003a.sql (ADR-015 / PF-003A).
--
-- Approved implementation decisions recorded with this DDL:
--   C-N1 department_type  — VARCHAR(32) NOT NULL with NO CHECK constraint, NO enum and
--                            NO API value validation; the supplied value is stored as-is.
--                            (The approved specification names the field only — ELU-BFS-PF §9 —
--                            and defines no value list; no business values are invented.)
--   C-N2 level/path       — NOT persisted; hierarchy information is derived at read/query time.
--   C-N3 status           — ACTIVE | INACTIVE | ARCHIVED, DEFAULT 'ACTIVE' (ELU-BFS-PF-006 §5).
--   C-N5 silent fields    — description VARCHAR(500) NULL, cost_centre_code VARCHAR(32) NULL.
--   C-N6 address          — no department address table/column.
--
-- Convention note: unlike 014_branch_pf005.sql (which declared tenant/organization/parent FKs
-- inline AND again in the guarded blocks, leaving duplicate constraints in the released schema),
-- the FKs below are declared exactly once inside the guarded blocks.

CREATE TABLE IF NOT EXISTS core.department (
    department_id           UUID PRIMARY KEY,
    tenant_id               UUID NOT NULL,
    organization_id         UUID NOT NULL,
    parent_department_id    UUID,
    branch_id               UUID,
    department_code         VARCHAR(30)  NOT NULL,
    department_name         VARCHAR(200) NOT NULL,
    description             VARCHAR(500),
    department_type         VARCHAR(32)  NOT NULL,
    department_head_user_id UUID,                       -- nullable; NO FK, validation deferred to PF-008
    cost_centre_code        VARCHAR(32),
    status                  VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_by              UUID,
    modified_by             UUID,
    created_on              TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified_on             TIMESTAMPTZ,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    version_no              INTEGER NOT NULL DEFAULT 1
);

-- Check constraints (guarded, mirrors the ck_branch_* / ck_organization_* pattern)
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_department_status') THEN
    ALTER TABLE core.department
      ADD CONSTRAINT ck_department_status
      CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'));
  END IF;
END
$ck$;

-- Self-parenting guard (ELU-BFS-PF-006 §6 BR-PF-042 basis; circular ancestry is enforced
-- in the API/service layer — this constraint only rejects the direct self-parent case).
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_department_no_self_parent') THEN
    ALTER TABLE core.department
      ADD CONSTRAINT ck_department_no_self_parent
      CHECK (parent_department_id IS NULL OR parent_department_id <> department_id);
  END IF;
END
$ck$;

-- Foreign keys (guarded: the table may already exist via ORM create_all)
DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_department_tenant') THEN
    ALTER TABLE core.department
      ADD CONSTRAINT fk_department_tenant
      FOREIGN KEY (tenant_id)
      REFERENCES core.tenant(tenant_id);
  END IF;
END
$fk$;

DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_department_organization') THEN
    ALTER TABLE core.department
      ADD CONSTRAINT fk_department_organization
      FOREIGN KEY (organization_id)
      REFERENCES core.organization(organization_id)
      ON DELETE RESTRICT;
  END IF;
END
$fk$;

DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_department_parent') THEN
    ALTER TABLE core.department
      ADD CONSTRAINT fk_department_parent
      FOREIGN KEY (parent_department_id)
      REFERENCES core.department(department_id)
      ON DELETE RESTRICT;
  END IF;
END
$fk$;

-- C-N3 / ELU-BFS-PF-006 §8: branch -> department is 1:N with ON DELETE SET NULL
DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_department_branch') THEN
    ALTER TABLE core.department
      ADD CONSTRAINT fk_department_branch
      FOREIGN KEY (branch_id)
      REFERENCES core.branch(branch_id)
      ON DELETE SET NULL;
  END IF;
END
$fk$;

-- Soft-delete aware department-code UK (BR-PF-040; ELU-DDD-PF §9): replace hard UK when present
DO $uk$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_department_tenant_code') THEN
    ALTER TABLE core.department DROP CONSTRAINT uk_department_tenant_code;
  END IF;
END
$uk$;

CREATE UNIQUE INDEX IF NOT EXISTS uk_department_tenant_code_active
  ON core.department (tenant_id, department_code)
  WHERE is_deleted = FALSE;

-- Indexes (partial, soft-delete aware — mirrors idx_branch_* / idx_organization_*)
CREATE INDEX IF NOT EXISTS idx_department_tenant_status
  ON core.department (tenant_id, status)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_department_organization
  ON core.department (tenant_id, organization_id)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_department_parent
  ON core.department (tenant_id, parent_department_id)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_department_branch
  ON core.department (tenant_id, branch_id)
  WHERE branch_id IS NOT NULL;
