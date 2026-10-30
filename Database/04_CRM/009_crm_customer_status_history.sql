CREATE SCHEMA IF NOT EXISTS crm;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'crm.customer'::regclass
          AND conname = 'uq_crm_customer_tenant_customer_id'
    ) THEN
        ALTER TABLE crm.customer
            ADD CONSTRAINT uq_crm_customer_tenant_customer_id
            UNIQUE (tenant_id, customer_id);
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS crm.customer_status_history (
    customer_status_history_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES core.tenant (tenant_id),
    customer_id UUID NOT NULL,
    from_status VARCHAR(40) NOT NULL,
    to_status VARCHAR(40) NOT NULL,
    reason TEXT NOT NULL,
    actor_id UUID NOT NULL REFERENCES core.users (user_id),
    changed_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_crm_customer_status_history_tenant_customer
        FOREIGN KEY (tenant_id, customer_id)
        REFERENCES crm.customer (tenant_id, customer_id)
);

CREATE INDEX IF NOT EXISTS ix_cust_status_hist_tenant_customer
    ON crm.customer_status_history (tenant_id, customer_id, changed_on);
