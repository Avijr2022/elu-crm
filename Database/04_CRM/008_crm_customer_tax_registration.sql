CREATE TABLE IF NOT EXISTS crm.customer_tax_registration (
    customer_tax_registration_id UUID PRIMARY KEY,
    tenant_id                    UUID NOT NULL REFERENCES core.tenant (tenant_id),
    customer_id                  UUID NOT NULL REFERENCES crm.customer (customer_id) ON DELETE CASCADE,
    tax_type                     VARCHAR(20) NOT NULL,
    tax_number                   VARCHAR(30) NOT NULL,
    state_code                   VARCHAR(10),
    created_on                   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on                  TIMESTAMPTZ,
    is_active                    BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted                   BOOLEAN NOT NULL DEFAULT FALSE,
    version_no                   INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT ck_cust_tax_type_nonempty CHECK (char_length(trim(tax_type)) > 0),
    CONSTRAINT ck_cust_tax_number_nonempty CHECK (char_length(trim(tax_number)) > 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_cust_tax_tenant_type_number_active
    ON crm.customer_tax_registration (tenant_id, tax_type, tax_number)
    WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS ix_cust_tax_tenant_customer
    ON crm.customer_tax_registration (tenant_id, customer_id)
    WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS ix_cust_tax_tenant_number
    ON crm.customer_tax_registration (tenant_id, tax_number)
    WHERE is_deleted = FALSE;
