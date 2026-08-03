-- Reference DDL for core.tenant (authoritative model: Backend SQLAlchemy + create_all)
-- Defaults: INR, Asia/Kolkata, FY Apr–Mar applied via tenant_settings seed.

CREATE TABLE IF NOT EXISTS core.edition (
    edition_id UUID PRIMARY KEY,
    edition_code VARCHAR(30) NOT NULL UNIQUE,
    edition_name VARCHAR(100) NOT NULL,
    description TEXT,
    max_users INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    version_no INTEGER NOT NULL DEFAULT 1,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS core.tenant (
    tenant_id UUID PRIMARY KEY,
    tenant_code VARCHAR(20) NOT NULL UNIQUE,
    tenant_name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(250) NOT NULL,
    edition_id UUID NOT NULL REFERENCES core.edition(edition_id),
    organization_type VARCHAR(50) NOT NULL,
    registration_number VARCHAR(100),
    gstin VARCHAR(15),
    pan VARCHAR(10),
    website VARCHAR(255),
    email VARCHAR(150) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    activation_date DATE,
    remarks TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    version_no INTEGER NOT NULL DEFAULT 1,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_tenant_status ON core.tenant(status);
