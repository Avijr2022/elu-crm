-- PF tenant branding (ELU-DDD-PF tenant_branding) — idempotent
CREATE TABLE IF NOT EXISTS core.tenant_branding (
    branding_id   UUID PRIMARY KEY,
    tenant_id     UUID NOT NULL UNIQUE REFERENCES core.tenant (tenant_id) ON DELETE CASCADE,
    logo_url      VARCHAR(2048),
    primary_color VARCHAR(16),
    secondary_color VARCHAR(16),
    favicon_url   VARCHAR(2048),
    created_on    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on   TIMESTAMPTZ,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted    BOOLEAN NOT NULL DEFAULT FALSE,
    version_no    INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_tenant_branding_tenant
    ON core.tenant_branding (tenant_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON core.tenant_branding TO elu_app;
