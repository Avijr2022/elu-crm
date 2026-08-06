-- PF-001 Edition Management (ELU-DDD-PF section 3.1-3.2, ELU-BFS-PF-001)
-- Extends core.edition and adds feature_catalogue, edition_feature, edition_limit, edition_version
-- Platform-global tables: no tenant_id / no RLS (ADR-015)

-- Extend edition catalogue columns (idempotent)
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS effective_from DATE;
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS effective_to DATE;
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS list_price_monthly NUMERIC(18,2);
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS list_price_annual NUMERIC(18,2);
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS currency_code CHAR(3) DEFAULT 'INR';
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0;
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ;
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS published_by UUID;
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS created_by UUID;
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS modified_by UUID;
ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS end_of_sale_date DATE;

CREATE TABLE IF NOT EXISTS core.feature_catalogue (
    id UUID PRIMARY KEY,
    feature_code VARCHAR(64) NOT NULL UNIQUE,
    feature_name VARCHAR(150) NOT NULL,
    module_domain VARCHAR(30) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    version_no INTEGER NOT NULL DEFAULT 1,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS core.edition_feature (
    id UUID PRIMARY KEY,
    edition_id UUID NOT NULL REFERENCES core.edition(edition_id) ON DELETE CASCADE,
    feature_code VARCHAR(64) NOT NULL REFERENCES core.feature_catalogue(feature_code),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ,
    UNIQUE (edition_id, feature_code)
);

CREATE TABLE IF NOT EXISTS core.edition_limit (
    id UUID PRIMARY KEY,
    edition_id UUID NOT NULL REFERENCES core.edition(edition_id) ON DELETE CASCADE,
    limit_code VARCHAR(64) NOT NULL,
    limit_name VARCHAR(150) NOT NULL,
    limit_value NUMERIC(18,2) NOT NULL,
    limit_unit VARCHAR(32),
    is_hard_limit BOOLEAN NOT NULL DEFAULT TRUE,
    grace_percent NUMERIC(5,2) DEFAULT 0,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ,
    UNIQUE (edition_id, limit_code)
);

CREATE TABLE IF NOT EXISTS core.edition_version (
    id UUID PRIMARY KEY,
    edition_id UUID NOT NULL REFERENCES core.edition(edition_id),
    version_no INTEGER NOT NULL,
    snapshot_json TEXT NOT NULL,
    change_summary VARCHAR(500),
    actor_id UUID,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (edition_id, version_no)
);

CREATE INDEX IF NOT EXISTS idx_edition_status ON core.edition(status);
CREATE INDEX IF NOT EXISTS idx_edition_feature_edition ON core.edition_feature(edition_id);
CREATE INDEX IF NOT EXISTS idx_edition_limit_edition ON core.edition_limit(edition_id);
