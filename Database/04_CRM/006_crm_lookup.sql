CREATE TABLE IF NOT EXISTS crm.activity_type (
    activity_type_id UUID PRIMARY KEY,
    tenant_id        UUID NOT NULL REFERENCES core.tenant (tenant_id),
    code             VARCHAR(40) NOT NULL,
    name             VARCHAR(100) NOT NULL,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    created_on       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on      TIMESTAMPTZ,
    is_deleted       BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uk_activity_type_tenant_code UNIQUE (tenant_id, code)
);

CREATE INDEX IF NOT EXISTS ix_activity_type_tenant
    ON crm.activity_type (tenant_id)
    WHERE NOT is_deleted;

CREATE TABLE IF NOT EXISTS crm.opportunity_stage (
    opportunity_stage_id UUID PRIMARY KEY,
    tenant_id            UUID NOT NULL REFERENCES core.tenant (tenant_id),
    code                 VARCHAR(40) NOT NULL,
    name                 VARCHAR(100) NOT NULL,
    sequence_no          INTEGER NOT NULL DEFAULT 0,
    default_probability  INTEGER NOT NULL DEFAULT 0,
    is_closed            BOOLEAN NOT NULL DEFAULT FALSE,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    created_on           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on          TIMESTAMPTZ,
    is_deleted           BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uk_opportunity_stage_tenant_code UNIQUE (tenant_id, code)
);

CREATE INDEX IF NOT EXISTS ix_opportunity_stage_tenant
    ON crm.opportunity_stage (tenant_id)
    WHERE NOT is_deleted;
