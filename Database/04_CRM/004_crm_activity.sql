CREATE SCHEMA IF NOT EXISTS crm;

CREATE TABLE IF NOT EXISTS crm.activity (
    activity_id        UUID PRIMARY KEY,
    tenant_id          UUID NOT NULL REFERENCES core.tenant (tenant_id),
    activity_type_code VARCHAR(40) NOT NULL DEFAULT 'NOTE',
    subject            VARCHAR(250) NOT NULL,
    description        TEXT,
    status             VARCHAR(40) NOT NULL DEFAULT 'COMPLETED',
    priority           VARCHAR(20),
    owner_id           UUID NOT NULL REFERENCES core.users (user_id),
    due_on             TIMESTAMPTZ,
    completed_on       TIMESTAMPTZ,
    created_on         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on        TIMESTAMPTZ,
    is_active          BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted         BOOLEAN NOT NULL DEFAULT FALSE,
    version_no         INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS crm.activity_link (
    activity_link_id UUID PRIMARY KEY,
    tenant_id        UUID NOT NULL REFERENCES core.tenant (tenant_id),
    activity_id      UUID NOT NULL REFERENCES crm.activity (activity_id),
    entity_type      VARCHAR(40) NOT NULL,
    entity_id        UUID NOT NULL,
    CONSTRAINT uk_activity_entity UNIQUE (activity_id, entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS ix_activity_tenant_owner ON crm.activity (tenant_id, owner_id, due_on);
CREATE INDEX IF NOT EXISTS ix_activity_link_entity ON crm.activity_link (tenant_id, entity_type, entity_id);
