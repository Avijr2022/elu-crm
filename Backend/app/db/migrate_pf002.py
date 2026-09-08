"""PF-002 tenant DDL applicator (idempotent)."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role


def apply_pf002_ddl(db: Session) -> None:
    with owner_role():
        db.execute(text("RESET ROLE"))
        _apply_pf002_ddl_inner(db)


def _apply_pf002_ddl_inner(db: Session) -> None:
    stmts = [
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS industry VARCHAR(100)",
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS company_size VARCHAR(50)",
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS provision_source VARCHAR(32)",
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS activated_on TIMESTAMPTZ",
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS suspended_on TIMESTAMPTZ",
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS created_by UUID",
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS modified_by UUID",
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS trade_name VARCHAR(255)",
        "UPDATE core.tenant SET trade_name = tenant_name WHERE trade_name IS NULL",
        "CREATE UNIQUE INDEX IF NOT EXISTS uk_tenant_legal_name ON core.tenant (lower(legal_name)) WHERE is_deleted = false",
        "CREATE INDEX IF NOT EXISTS idx_tenant_status ON core.tenant(status)",
        "CREATE INDEX IF NOT EXISTS idx_tenant_edition_id ON core.tenant(edition_id)",
        """
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_tenant_status') THEN
    ALTER TABLE core.tenant
      ADD CONSTRAINT ck_tenant_status
      CHECK (status IN (
        'DRAFT','PENDING_ACTIVATION','TRIAL','ACTIVE','SUSPENDED',
        'OFFBOARDING','CLOSED','ARCHIVED','CANCELLED'
      ));
  END IF;
END
$ck$;
""",
        """
CREATE TABLE IF NOT EXISTS core.tenant_contact (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id) ON DELETE CASCADE,
    contact_type VARCHAR(32) NOT NULL,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    mobile VARCHAR(30),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    version_no INTEGER NOT NULL DEFAULT 1,
    created_by UUID,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_by UUID,
    modified_on TIMESTAMPTZ
)
""",
        """
CREATE UNIQUE INDEX IF NOT EXISTS uk_tenant_one_primary_contact
  ON core.tenant_contact (tenant_id)
  WHERE is_primary = true AND is_deleted = false AND contact_type = 'PRIMARY'
""",
        """
CREATE TABLE IF NOT EXISTS core.tenant_address (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id) ON DELETE CASCADE,
    address_type VARCHAR(32) NOT NULL,
    line1 VARCHAR(255) NOT NULL,
    line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    postal_code VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    version_no INTEGER NOT NULL DEFAULT 1,
    created_by UUID,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_by UUID,
    modified_on TIMESTAMPTZ
)
""",
        """
CREATE UNIQUE INDEX IF NOT EXISTS uk_tenant_one_registered_address
  ON core.tenant_address (tenant_id)
  WHERE address_type = 'REGISTERED' AND is_deleted = false
""",
        """
CREATE TABLE IF NOT EXISTS core.tenant_status_history (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id) ON DELETE CASCADE,
    from_status VARCHAR(32),
    to_status VARCHAR(32) NOT NULL,
    reason VARCHAR(500),
    actor_id UUID,
    changed_on TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
""",
        "CREATE INDEX IF NOT EXISTS idx_tenant_contact_tenant ON core.tenant_contact(tenant_id)",
        "CREATE INDEX IF NOT EXISTS idx_tenant_address_tenant ON core.tenant_address(tenant_id)",
        "CREATE INDEX IF NOT EXISTS idx_tenant_status_history_tenant ON core.tenant_status_history(tenant_id)",
        """
CREATE TABLE IF NOT EXISTS core.tenant_branding (
    branding_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL UNIQUE REFERENCES core.tenant(tenant_id) ON DELETE CASCADE,
    logo_url VARCHAR(2048),
    primary_color VARCHAR(16),
    secondary_color VARCHAR(16),
    favicon_url VARCHAR(2048),
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    version_no INTEGER NOT NULL DEFAULT 1
)
""",
        "CREATE INDEX IF NOT EXISTS ix_tenant_branding_tenant ON core.tenant_branding(tenant_id)",
        """
CREATE TABLE IF NOT EXISTS core.idempotency_key (
    key VARCHAR(128) PRIMARY KEY,
    tenant_id UUID,
    request_path VARCHAR(255) NOT NULL,
    response_status INTEGER NOT NULL,
    response_body TEXT NOT NULL,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
""",
    ]
    for stmt in stmts:
        db.execute(text(stmt))
    db.commit()
