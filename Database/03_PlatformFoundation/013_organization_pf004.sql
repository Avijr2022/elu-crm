-- PF-004 Organization Management DDL (idempotent)

ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS legal_name VARCHAR(255);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS short_name VARCHAR(100);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS registration_number VARCHAR(100);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS cin VARCHAR(30);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS date_of_incorporation DATE;
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS gstin VARCHAR(20);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS pan VARCHAR(20);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS tan VARCHAR(20);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS tax_registration_type VARCHAR(50);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS is_root BOOLEAN DEFAULT FALSE;
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 0;
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS default_currency_code VARCHAR(3) DEFAULT 'INR';
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS fiscal_year_start_month INTEGER DEFAULT 4;
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS website VARCHAR(255);
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS created_by UUID;
ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS modified_by UUID;

UPDATE core.organization
SET is_root = TRUE, level = 0
WHERE parent_organization_id IS NULL AND COALESCE(is_root, FALSE) = FALSE;

UPDATE core.organization
SET legal_name = organization_name
WHERE legal_name IS NULL;

UPDATE core.organization
SET default_currency_code = 'INR'
WHERE default_currency_code IS NULL;

UPDATE core.organization
SET fiscal_year_start_month = 4
WHERE fiscal_year_start_month IS NULL;

ALTER TABLE core.organization ALTER COLUMN is_root SET DEFAULT FALSE;
ALTER TABLE core.organization ALTER COLUMN level SET DEFAULT 0;
ALTER TABLE core.organization ALTER COLUMN default_currency_code SET DEFAULT 'INR';
ALTER TABLE core.organization ALTER COLUMN fiscal_year_start_month SET DEFAULT 4;

DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_organization_status') THEN
    ALTER TABLE core.organization
      ADD CONSTRAINT ck_organization_status
      CHECK (status IN ('DRAFT','ACTIVE','INACTIVE','MERGED','ARCHIVED'));
  END IF;
END
$ck$;

DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_organization_fy_month') THEN
    ALTER TABLE core.organization
      ADD CONSTRAINT ck_organization_fy_month
      CHECK (fiscal_year_start_month BETWEEN 1 AND 12);
  END IF;
END
$ck$;

CREATE UNIQUE INDEX IF NOT EXISTS uk_organization_one_root
  ON core.organization (tenant_id)
  WHERE is_root = TRUE AND is_deleted = FALSE;

-- Soft-delete aware UK (DDD): replace hard UK when present
DO $uk$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'uk_org_tenant_code'
  ) THEN
    ALTER TABLE core.organization DROP CONSTRAINT uk_org_tenant_code;
  END IF;
END
$uk$;

CREATE UNIQUE INDEX IF NOT EXISTS uk_organization_tenant_code_active
  ON core.organization (tenant_id, organization_code)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_organization_tenant_status
  ON core.organization (tenant_id, status)
  WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_organization_parent
  ON core.organization (tenant_id, parent_organization_id)
  WHERE is_deleted = FALSE;

ALTER TABLE core.organization ALTER COLUMN is_root SET NOT NULL;
ALTER TABLE core.organization ALTER COLUMN level SET NOT NULL;
ALTER TABLE core.organization ALTER COLUMN default_currency_code SET NOT NULL;
ALTER TABLE core.organization ALTER COLUMN fiscal_year_start_month SET NOT NULL;

ALTER TABLE core.organization ADD COLUMN IF NOT EXISTS address_id UUID;

DO $fk$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_organization_address'
  ) THEN
    ALTER TABLE core.organization
      ADD CONSTRAINT fk_organization_address
      FOREIGN KEY (address_id)
      REFERENCES core.tenant_address(id)
      ON DELETE SET NULL;
  END IF;
END
$fk$;

CREATE INDEX IF NOT EXISTS idx_organization_address
  ON core.organization (address_id)
  WHERE address_id IS NOT NULL;
