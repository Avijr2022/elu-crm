-- E-LinkUp CRM Lead (REQ-CRM-001 / WF-CRM-001)
-- Runtime tables are also created by SQLAlchemy create_all.

CREATE SCHEMA IF NOT EXISTS crm;

CREATE TABLE IF NOT EXISTS crm.lead (
    lead_id              UUID PRIMARY KEY,
    tenant_id            UUID NOT NULL REFERENCES core.tenant (tenant_id),
    lead_number          VARCHAR(40) NOT NULL,
    full_name            VARCHAR(200) NOT NULL,
    company_name         VARCHAR(200),
    email                VARCHAR(150),
    phone                VARCHAR(30),
    status               VARCHAR(40) NOT NULL DEFAULT 'NEW',
    estimated_value      NUMERIC(18, 2) NOT NULL DEFAULT 0,
    currency_code        VARCHAR(3) NOT NULL DEFAULT 'INR',
    owner_id             UUID REFERENCES core.users (user_id),
    notes                TEXT,
    created_on           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on          TIMESTAMPTZ,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted           BOOLEAN NOT NULL DEFAULT FALSE,
    version_no           INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_lead_tenant_number UNIQUE (tenant_id, lead_number)
);

CREATE INDEX IF NOT EXISTS ix_lead_tenant_status ON crm.lead (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_lead_tenant_email ON crm.lead (tenant_id, email);
CREATE INDEX IF NOT EXISTS ix_lead_tenant_owner ON crm.lead (tenant_id, owner_id);
