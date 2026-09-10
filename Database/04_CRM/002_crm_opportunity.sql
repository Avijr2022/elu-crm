-- E-LinkUp CRM Opportunity (REQ-CRM-013 / WF-CRM-002)
-- Runtime tables are also created by SQLAlchemy create_all.

CREATE SCHEMA IF NOT EXISTS crm;

CREATE TABLE IF NOT EXISTS crm.opportunity (
    opportunity_id       UUID PRIMARY KEY,
    tenant_id            UUID NOT NULL REFERENCES core.tenant (tenant_id),
    opportunity_number   VARCHAR(40) NOT NULL,
    name                 VARCHAR(250) NOT NULL,
    company_name         VARCHAR(200),
    stage                VARCHAR(40) NOT NULL DEFAULT 'QUALIFICATION',
    status               VARCHAR(40) NOT NULL DEFAULT 'OPEN',
    opportunity_value    NUMERIC(18, 2) NOT NULL DEFAULT 0,
    currency_code        VARCHAR(3) NOT NULL DEFAULT 'INR',
    probability          INTEGER NOT NULL DEFAULT 10,
    expected_close_date  DATE,
    source_lead_id       UUID REFERENCES crm.lead (lead_id),
    owner_id             UUID REFERENCES core.users (user_id),
    loss_reason          VARCHAR(250),
    notes                TEXT,
    created_on           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on          TIMESTAMPTZ,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted           BOOLEAN NOT NULL DEFAULT FALSE,
    version_no           INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_opp_tenant_number UNIQUE (tenant_id, opportunity_number)
);

CREATE INDEX IF NOT EXISTS ix_opp_tenant_stage ON crm.opportunity (tenant_id, stage);
CREATE INDEX IF NOT EXISTS ix_opp_tenant_status ON crm.opportunity (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_opp_tenant_owner ON crm.opportunity (tenant_id, owner_id);
CREATE INDEX IF NOT EXISTS ix_opp_source_lead ON crm.opportunity (source_lead_id);
