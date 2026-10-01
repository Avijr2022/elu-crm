-- PF-011 System Configuration CORE DDL
-- Idempotent migration.

CREATE TABLE IF NOT EXISTS core.setting_catalogue (
    id UUID PRIMARY KEY,
    setting_key VARCHAR NOT NULL UNIQUE,
    value_type VARCHAR NOT NULL,
    default_value TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS core.platform_setting (
    id UUID PRIMARY KEY,
    key VARCHAR NOT NULL UNIQUE,
    value TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS core.tenant_preference (
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id) ON DELETE CASCADE,
    preference_key VARCHAR NOT NULL REFERENCES core.setting_catalogue(setting_key) ON DELETE RESTRICT,
    preference_value TEXT,
    preference_type VARCHAR,
    preference_group VARCHAR,
    description TEXT,
    is_editable BOOLEAN NOT NULL DEFAULT TRUE,
    edition_minimum VARCHAR
);

CREATE TABLE IF NOT EXISTS core.tenant_notification_preference (
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id) ON DELETE CASCADE,
    event_type VARCHAR NOT NULL,
    module_code VARCHAR NOT NULL,
    email_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    sms_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    whatsapp_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    push_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    internal_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    notify_actor BOOLEAN NOT NULL DEFAULT FALSE,
    notify_manager BOOLEAN NOT NULL DEFAULT FALSE,
    notify_admin BOOLEAN NOT NULL DEFAULT FALSE,
    custom_recipients TEXT
);

CREATE TABLE IF NOT EXISTS core.tenant_module_default (
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id) ON DELETE CASCADE,
    module_code VARCHAR NOT NULL,
    entity_type VARCHAR NOT NULL,
    field_name VARCHAR NOT NULL,
    default_value TEXT
);

CREATE TABLE IF NOT EXISTS core.tenant_holiday_calendar (
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id) ON DELETE CASCADE,
    holiday_name VARCHAR NOT NULL,
    holiday_date DATE NOT NULL,
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    holiday_type VARCHAR,
    calendar_year INTEGER
);

CREATE INDEX IF NOT EXISTS idx_tenant_preference_tenant
    ON core.tenant_preference(tenant_id);

CREATE INDEX IF NOT EXISTS idx_tenant_notification_preference_tenant
    ON core.tenant_notification_preference(tenant_id);

CREATE INDEX IF NOT EXISTS idx_tenant_module_default_tenant
    ON core.tenant_module_default(tenant_id);

CREATE INDEX IF NOT EXISTS idx_tenant_holiday_calendar_tenant
    ON core.tenant_holiday_calendar(tenant_id);
