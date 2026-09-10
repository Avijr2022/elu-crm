CREATE TABLE IF NOT EXISTS crm.activity_outcome (
    activity_outcome_id UUID PRIMARY KEY,
    tenant_id           UUID NOT NULL REFERENCES core.tenant (tenant_id),
    activity_type_code  VARCHAR(40) NOT NULL,
    code                VARCHAR(40) NOT NULL,
    name                VARCHAR(100) NOT NULL,
    is_positive         BOOLEAN NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_on          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on         TIMESTAMPTZ,
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uk_activity_outcome_tenant_type_code UNIQUE (tenant_id, activity_type_code, code)
);

CREATE INDEX IF NOT EXISTS ix_activity_outcome_tenant_type
    ON crm.activity_outcome (tenant_id, activity_type_code)
    WHERE NOT is_deleted;

ALTER TABLE crm.activity
    ADD COLUMN IF NOT EXISTS outcome_code VARCHAR(40);
