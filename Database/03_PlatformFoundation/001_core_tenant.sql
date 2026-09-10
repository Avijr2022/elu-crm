-- Reference DDL for core.edition aligned to ELU-DDD-PF §3.1 (PF-001)
-- Authoritative runtime: SQLAlchemy models + migrate_pf001 / 009_edition_ddd_align_pf001.sql

CREATE TABLE IF NOT EXISTS core.edition (
    id UUID PRIMARY KEY,
    code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    version_no INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT','ACTIVE','DEPRECATED','ARCHIVED','CANCELLED')),
    effective_from DATE,
    effective_to DATE,
    list_price_monthly NUMERIC(18,2),
    list_price_annual NUMERIC(18,2),
    currency_code CHAR(3) DEFAULT 'INR',
    display_order INTEGER DEFAULT 0,
    published_at TIMESTAMPTZ,
    published_by UUID,
    created_by UUID,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_by UUID,
    modified_on TIMESTAMPTZ,
    end_of_sale_date DATE
);

CREATE INDEX IF NOT EXISTS idx_edition_status ON core.edition(status);

CREATE TABLE IF NOT EXISTS core.tenant (
    tenant_id UUID PRIMARY KEY,
    tenant_code VARCHAR(20) NOT NULL UNIQUE,
    tenant_name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(250) NOT NULL,
    edition_id UUID NOT NULL REFERENCES core.edition(id),
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
