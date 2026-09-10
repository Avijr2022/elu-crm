-- Rollback helper for PF-004 organization extensions (non-destructive of core.organization table).
-- Does NOT drop the organization table (seeded by platform). Safe to re-run.

DROP INDEX IF EXISTS core.idx_organization_address;
ALTER TABLE core.organization DROP CONSTRAINT IF EXISTS fk_organization_address;
ALTER TABLE core.organization DROP COLUMN IF EXISTS address_id;

DROP INDEX IF EXISTS core.idx_organization_parent;
DROP INDEX IF EXISTS core.idx_organization_tenant_status;
DROP INDEX IF EXISTS core.uk_organization_tenant_code_active;
DROP INDEX IF EXISTS core.uk_organization_one_root;

ALTER TABLE core.organization DROP CONSTRAINT IF EXISTS ck_organization_fy_month;
ALTER TABLE core.organization DROP CONSTRAINT IF EXISTS ck_organization_status;

ALTER TABLE core.organization DROP COLUMN IF EXISTS legal_name;
ALTER TABLE core.organization DROP COLUMN IF EXISTS short_name;
ALTER TABLE core.organization DROP COLUMN IF EXISTS registration_number;
ALTER TABLE core.organization DROP COLUMN IF EXISTS cin;
ALTER TABLE core.organization DROP COLUMN IF EXISTS date_of_incorporation;
ALTER TABLE core.organization DROP COLUMN IF EXISTS gstin;
ALTER TABLE core.organization DROP COLUMN IF EXISTS pan;
ALTER TABLE core.organization DROP COLUMN IF EXISTS tan;
ALTER TABLE core.organization DROP COLUMN IF EXISTS tax_registration_type;
ALTER TABLE core.organization DROP COLUMN IF EXISTS is_root;
ALTER TABLE core.organization DROP COLUMN IF EXISTS level;
ALTER TABLE core.organization DROP COLUMN IF EXISTS default_currency_code;
ALTER TABLE core.organization DROP COLUMN IF EXISTS fiscal_year_start_month;
ALTER TABLE core.organization DROP COLUMN IF EXISTS website;
ALTER TABLE core.organization DROP COLUMN IF EXISTS created_by;
ALTER TABLE core.organization DROP COLUMN IF EXISTS modified_by;
