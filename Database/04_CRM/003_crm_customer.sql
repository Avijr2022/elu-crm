CREATE SCHEMA IF NOT EXISTS crm;

CREATE TABLE IF NOT EXISTS crm.customer (
    customer_id       UUID PRIMARY KEY,
    tenant_id         UUID NOT NULL REFERENCES core.tenant (tenant_id),
    customer_number   VARCHAR(40) NOT NULL,
    legal_name        VARCHAR(250) NOT NULL,
    trade_name        VARCHAR(200),
    customer_type     VARCHAR(20) NOT NULL DEFAULT 'ACCOUNT',
    status            VARCHAR(40) NOT NULL DEFAULT 'PROSPECT',
    owner_id          UUID REFERENCES core.users (user_id),
    source_opportunity_id UUID REFERENCES crm.opportunity (opportunity_id),
    notes             TEXT,
    created_on        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on       TIMESTAMPTZ,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted        BOOLEAN NOT NULL DEFAULT FALSE,
    version_no        INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_cust_tenant_number UNIQUE (tenant_id, customer_number)
);

CREATE INDEX IF NOT EXISTS ix_cust_tenant_status ON crm.customer (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_cust_tenant_name ON crm.customer (tenant_id, legal_name);

ALTER TABLE crm.opportunity
    ADD COLUMN IF NOT EXISTS customer_id UUID REFERENCES crm.customer (customer_id);

CREATE INDEX IF NOT EXISTS ix_opp_customer ON crm.opportunity (tenant_id, customer_id);
