-- PF-007 Business Unit Management DDL (idempotent)
-- Creates core.business_unit per ELU-BFS-PF-007 §7/§9 and ELU-DDD-PF §5.
--
-- Scope (approved Batch 1): schema + constraints + indexes ONLY.
-- EXPLICITLY DEFERRED — NOT implemented here:
--   * business_unit -> opportunity (CRM) FK                        -> later controlled PF-007 batch (D6)
--   * business_unit -> project (PRJ) FK                            -> deferred (D6; not authorized in this batch)
--   * business_unit -> invoice (FIN) FK                            -> deferred (D6; not authorized in this batch)
--   * users.business_unit_id / user <-> BU assignment              -> PF-008
--   * NTF-PF-007-01..03 notifications                              -> deferred
--   * RPT-PF-007-01/02 reports and XLSX/PDF export formatting      -> deferred (D8)
--   * Business Unit History UI / history API                       -> deferred (D1)
-- RLS coverage for this table is added in 012_rls_pf003a.sql (ADR-015 / PF-003A).
--
-- Approved human scope decisions applied to this DDL (D1–D11, recorded 2026-09-16):
--   D1  — exactly the 8 BFS §10 endpoints; no history API.
--   D4  — bu_manager_user_id is validated at API level (BR-PF-048); the column is
--          NULLABLE with NO FK, exactly like core.department.department_head_user_id.
--   D5  — edition limits: Professional = 20 business units, Enterprise = unlimited
--           (MAX_BUSINESS_UNITS, seeded in app/db/seed.py — never hard-coded here).
--   D7  — organization_id is assigned on creation and IMMUTABLE afterwards (service layer).
--   D11 — core.business_unit with tenant-scoped RLS and the partial unique key
--           (tenant_id, business_unit_code) WHERE is_deleted = FALSE.
--
-- D9 field resolutions (established project conventions; no new pattern invented):
--   * physical column naming follows PF-004/PF-005/PF-006 (`<entity>_code` /
--     `<entity>_name`); the API exposes them as ``code`` / ``name``
--     (identical to core.branch.branch_code / core.department.department_code).
--   * description             VARCHAR(500) NULL   (PF-006 C-N5 precedent)
--   * cost_centre_code        VARCHAR(32)  NULL   (PF-006 C-N5 precedent)
--   * revenue_target_annual   NUMERIC(18,2) NULL  (monetary convention: crm.opportunity_value)
--   * start_date / end_date   DATE NULL           (lifecycle window; no cross-field rule
--                                                  is defined by the specification, so none is invented)
--   * is_active / is_deleted / version_no / created_on / modified_on / created_by / modified_by
--     follow the shared TimestampMixin + SoftDeleteMixin convention.
--   * status                  ACTIVE | INACTIVE | ARCHIVED, DEFAULT 'ACTIVE'
--     (ELU-BFS-PF-007 §5) — the only CHECK constraint on the table.

CREATE TABLE IF NOT EXISTS core.business_unit (
    business_unit_id       UUID PRIMARY KEY,
    tenant_id              UUID NOT NULL,
    organization_id        UUID NOT NULL,
    business_unit_code     VARCHAR(30)  NOT NULL,
    business_unit_name     VARCHAR(200) NOT NULL,
    description            VARCHAR(500),
    bu_manager_user_id     UUID,                     -- nullable; NO FK (D4); BR-PF-048 validated at API level
    cost_centre_code       VARCHAR(32),
    revenue_target_annual  NUMERIC(18,2),
    start_date             DATE,
    end_date               DATE,
    status                 VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_by             UUID,
    modified_by            UUID,
    created_on             TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified_on            TIMESTAMPTZ,
    is_active              BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted             BOOLEAN NOT NULL DEFAULT FALSE,
    version_no             INTEGER NOT NULL DEFAULT 1
);

-- Check constraint (guarded, mirrors ck_branch_status / ck_department_status)
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_business_unit_status') THEN
    ALTER TABLE core.business_unit
      ADD CONSTRAINT ck_business_unit_status
      CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'));
  END IF;
END
$ck$;

-- Foreign keys (guarded: the table may already exist via ORM create_all).
-- ELU-BFS-PF-007 §8: organization -> business_unit is 1:N with ON DELETE RESTRICT.
DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_business_unit_tenant') THEN
    ALTER TABLE core.business_unit
      ADD CONSTRAINT fk_business_unit_tenant
      FOREIGN KEY (tenant_id)
      REFERENCES core.tenant(tenant_id);
  END IF;
END
$fk$;

DO $fk$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_business_unit_organization') THEN
    ALTER TABLE core.business_unit
      ADD CONSTRAINT fk_business_unit_organization
      FOREIGN KEY (organization_id)
      REFERENCES core.organization(organization_id)
      ON DELETE RESTRICT;
  END IF;
END
$fk$;

-- Soft-delete aware code uniqueness (BR-PF-047; D11): replace a hard UK when present.
DO $uk$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uk_business_unit_tenant_code') THEN
    ALTER TABLE core.business_unit DROP CONSTRAINT uk_business_unit_tenant_code;
  END IF;
END
$uk$;

CREATE UNIQUE INDEX IF NOT EXISTS uk_business_unit_tenant_code_active
  ON core.business_unit (tenant_id, business_unit_code)
  WHERE is_deleted = FALSE;

-- Indexes (partial, soft-delete aware — mirrors idx_branch_* / idx_department_*)
CREATE INDEX IF NOT EXISTS idx_business_unit_tenant_status
  ON core.business_unit (tenant_id, status)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_business_unit_organization
  ON core.business_unit (tenant_id, organization_id)
  WHERE is_deleted = FALSE;
