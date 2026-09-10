"""Apply PF-001 DDD alignment DDL (idempotent, Python-driven)."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role


def apply_pf001_ddl(db: Session) -> None:
    """Align edition schema to ELU-DDD-PF and ensure audit tables/indexes."""
    with owner_role():
        db.execute(text("RESET ROLE"))
        _apply_pf001_ddl_inner(db)


def _apply_pf001_ddl_inner(db: Session) -> None:
    db.execute(text("CREATE SCHEMA IF NOT EXISTS audit"))
    db.execute(text("CREATE SCHEMA IF NOT EXISTS core"))

    exists = db.execute(
        text(
            """
SELECT EXISTS (
  SELECT 1 FROM information_schema.tables
  WHERE table_schema = 'core' AND table_name = 'edition'
)
"""
        )
    ).scalar()
    if not exists:
        db.commit()
        return

    # Rename scaffold columns → DDD when needed
    db.execute(
        text(
            """
DO $mig$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'core' AND table_name = 'edition' AND column_name = 'edition_id'
  ) THEN
    ALTER TABLE IF EXISTS core.tenant DROP CONSTRAINT IF EXISTS tenant_edition_id_fkey;
    ALTER TABLE IF EXISTS core.subscription DROP CONSTRAINT IF EXISTS subscription_edition_id_fkey;
    ALTER TABLE IF EXISTS core.edition_feature DROP CONSTRAINT IF EXISTS edition_feature_edition_id_fkey;
    ALTER TABLE IF EXISTS core.edition_limit DROP CONSTRAINT IF EXISTS edition_limit_edition_id_fkey;
    ALTER TABLE IF EXISTS core.edition_version DROP CONSTRAINT IF EXISTS edition_version_edition_id_fkey;

    ALTER TABLE core.edition RENAME COLUMN edition_id TO id;
    ALTER TABLE core.edition RENAME COLUMN edition_code TO code;
    ALTER TABLE core.edition RENAME COLUMN edition_name TO name;

    ALTER TABLE core.tenant
      ADD CONSTRAINT tenant_edition_id_fkey
      FOREIGN KEY (edition_id) REFERENCES core.edition(id);

    ALTER TABLE core.subscription
      ADD CONSTRAINT subscription_edition_id_fkey
      FOREIGN KEY (edition_id) REFERENCES core.edition(id);

    IF EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_schema = 'core' AND table_name = 'edition_feature'
    ) THEN
      ALTER TABLE core.edition_feature
        ADD CONSTRAINT edition_feature_edition_id_fkey
        FOREIGN KEY (edition_id) REFERENCES core.edition(id) ON DELETE CASCADE;
    END IF;
    IF EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_schema = 'core' AND table_name = 'edition_limit'
    ) THEN
      ALTER TABLE core.edition_limit
        ADD CONSTRAINT edition_limit_edition_id_fkey
        FOREIGN KEY (edition_id) REFERENCES core.edition(id) ON DELETE CASCADE;
    END IF;
    IF EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_schema = 'core' AND table_name = 'edition_version'
    ) THEN
      ALTER TABLE core.edition_version
        ADD CONSTRAINT edition_version_edition_id_fkey
        FOREIGN KEY (edition_id) REFERENCES core.edition(id);
    END IF;
  END IF;
END
$mig$;
"""
        )
    )

    for stmt in (
        "ALTER TABLE core.edition DROP COLUMN IF EXISTS max_users",
        "ALTER TABLE core.edition DROP COLUMN IF EXISTS is_active",
        "ALTER TABLE core.edition DROP COLUMN IF EXISTS is_deleted",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS effective_from DATE",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS effective_to DATE",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS list_price_monthly NUMERIC(18,2)",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS list_price_annual NUMERIC(18,2)",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS currency_code CHAR(3) DEFAULT 'INR'",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS published_by UUID",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS created_by UUID",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS modified_by UUID",
        "ALTER TABLE core.edition ADD COLUMN IF NOT EXISTS end_of_sale_date DATE",
    ):
        db.execute(text(stmt))

    db.execute(
        text(
            """
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_edition_status') THEN
    ALTER TABLE core.edition
      ADD CONSTRAINT ck_edition_status
      CHECK (status IN ('DRAFT','ACTIVE','DEPRECATED','ARCHIVED','CANCELLED'));
  END IF;
END
$ck$;
"""
        )
    )

    db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uk_edition_code ON core.edition(code)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_edition_status ON core.edition(status)"))

    db.execute(
        text(
            """
CREATE TABLE IF NOT EXISTS core.feature_catalogue (
    id UUID PRIMARY KEY,
    feature_code VARCHAR(64) NOT NULL UNIQUE,
    feature_name VARCHAR(150) NOT NULL,
    module_domain VARCHAR(30) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    version_no INTEGER NOT NULL DEFAULT 1,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ
)
"""
        )
    )
    db.execute(
        text(
            """
CREATE TABLE IF NOT EXISTS core.edition_feature (
    id UUID PRIMARY KEY,
    edition_id UUID NOT NULL REFERENCES core.edition(id) ON DELETE CASCADE,
    feature_code VARCHAR(64) NOT NULL REFERENCES core.feature_catalogue(feature_code),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ,
    UNIQUE (edition_id, feature_code)
)
"""
        )
    )
    db.execute(
        text(
            """
CREATE TABLE IF NOT EXISTS core.edition_limit (
    id UUID PRIMARY KEY,
    edition_id UUID NOT NULL REFERENCES core.edition(id) ON DELETE CASCADE,
    limit_code VARCHAR(64) NOT NULL,
    limit_name VARCHAR(150) NOT NULL,
    limit_value NUMERIC(18,2) NOT NULL,
    limit_unit VARCHAR(32),
    is_hard_limit BOOLEAN NOT NULL DEFAULT TRUE,
    grace_percent NUMERIC(5,2) DEFAULT 0,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on TIMESTAMPTZ,
    UNIQUE (edition_id, limit_code)
)
"""
        )
    )
    db.execute(
        text(
            """
CREATE TABLE IF NOT EXISTS core.edition_version (
    id UUID PRIMARY KEY,
    edition_id UUID NOT NULL REFERENCES core.edition(id),
    version_no INTEGER NOT NULL,
    snapshot_json TEXT NOT NULL,
    change_summary VARCHAR(500),
    actor_id UUID,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (edition_id, version_no)
)
"""
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_edition_feature_edition ON core.edition_feature(edition_id)"
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_edition_limit_edition ON core.edition_limit(edition_id)"
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_edition_version_edition ON core.edition_version(edition_id)"
        )
    )

    db.execute(
        text(
            """
CREATE TABLE IF NOT EXISTS audit.audit_event (
    id UUID PRIMARY KEY,
    tenant_id UUID NULL,
    event_type VARCHAR(64) NOT NULL,
    event_category VARCHAR(64) NOT NULL,
    actor_id UUID,
    actor_email VARCHAR(255),
    entity_type VARCHAR(64) NOT NULL,
    entity_id UUID,
    ip_address VARCHAR(64),
    user_agent VARCHAR(512),
    session_id UUID,
    payload_json TEXT,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_audit_event_entity ON audit.audit_event(entity_type, entity_id)"
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit.audit_event(event_type)"
        )
    )
    db.commit()
