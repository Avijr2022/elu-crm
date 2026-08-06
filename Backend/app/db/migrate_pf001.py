"""Idempotent PF-001 DDL apply for local bootstrap (alongside create_all)."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

_FALLBACK_STATEMENTS = [
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
]


def apply_pf001_ddl(db: Session) -> None:
    """Apply additive PF-001 ALTER columns. New tables come from SQLAlchemy create_all."""
    for stmt in _FALLBACK_STATEMENTS:
        db.execute(text(stmt))
    db.commit()
