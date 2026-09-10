CREATE TABLE IF NOT EXISTS crm.customer_contact (
    customer_contact_id UUID PRIMARY KEY,
    tenant_id           UUID NOT NULL REFERENCES core.tenant (tenant_id),
    customer_id         UUID NOT NULL REFERENCES crm.customer (customer_id),
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100),
    job_title           VARCHAR(120),
    email               VARCHAR(150),
    phone_mobile        VARCHAR(30),
    phone_work          VARCHAR(30),
    contact_role        VARCHAR(40),
    is_primary          BOOLEAN NOT NULL DEFAULT FALSE,
    is_decision_maker   BOOLEAN NOT NULL DEFAULT FALSE,
    created_on          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on         TIMESTAMPTZ,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    version_no          INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_cust_contact_customer
    ON crm.customer_contact (tenant_id, customer_id);

CREATE TABLE IF NOT EXISTS crm.customer_address (
    customer_address_id UUID PRIMARY KEY,
    tenant_id           UUID NOT NULL REFERENCES core.tenant (tenant_id),
    customer_id         UUID NOT NULL REFERENCES crm.customer (customer_id),
    address_type        VARCHAR(20) NOT NULL DEFAULT 'REGISTERED',
    address_line1       VARCHAR(250) NOT NULL,
    address_line2       VARCHAR(250),
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100),
    postal_code         VARCHAR(20),
    is_default_billing  BOOLEAN NOT NULL DEFAULT FALSE,
    is_default_shipping BOOLEAN NOT NULL DEFAULT FALSE,
    created_on          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on         TIMESTAMPTZ,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    version_no          INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_cust_address_customer
    ON crm.customer_address (tenant_id, customer_id);
