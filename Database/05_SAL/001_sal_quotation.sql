CREATE SCHEMA IF NOT EXISTS sales;

CREATE TABLE IF NOT EXISTS sales.quotation (
    quotation_id      UUID PRIMARY KEY,
    tenant_id         UUID NOT NULL REFERENCES core.tenant (tenant_id),
    quotation_number  VARCHAR(40) NOT NULL,
    opportunity_id    UUID REFERENCES crm.opportunity (opportunity_id),
    customer_id       UUID REFERENCES crm.customer (customer_id),
    owner_id          UUID REFERENCES core.users (user_id),
    status            VARCHAR(40) NOT NULL DEFAULT 'DRAFT',
    currency_code     VARCHAR(3) NOT NULL DEFAULT 'INR',
    subtotal          NUMERIC(18, 2) NOT NULL DEFAULT 0,
    discount_total    NUMERIC(18, 2) NOT NULL DEFAULT 0,
    tax_total         NUMERIC(18, 2) NOT NULL DEFAULT 0,
    grand_total       NUMERIC(18, 2) NOT NULL DEFAULT 0,
    valid_until       DATE,
    version_no_doc    INTEGER NOT NULL DEFAULT 1,
    is_current        BOOLEAN NOT NULL DEFAULT TRUE,
    notes             TEXT,
    created_on        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on       TIMESTAMPTZ,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted        BOOLEAN NOT NULL DEFAULT FALSE,
    version_no        INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_quotation_tenant_number UNIQUE (tenant_id, quotation_number)
);

CREATE INDEX IF NOT EXISTS ix_quotation_tenant_status ON sales.quotation (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_quotation_tenant_opp ON sales.quotation (tenant_id, opportunity_id);
CREATE INDEX IF NOT EXISTS ix_quotation_tenant_customer ON sales.quotation (tenant_id, customer_id);

GRANT USAGE ON SCHEMA sales TO elu_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sales TO elu_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA sales
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO elu_app;
