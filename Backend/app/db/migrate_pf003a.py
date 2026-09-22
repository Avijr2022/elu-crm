"""PF-003A — Enterprise Tenant Isolation RLS applicator (idempotent)."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role

_SQL_PATH = (
    Path(__file__).resolve().parents[3]
    / "Database"
    / "03_PlatformFoundation"
    / "012_rls_pf003a.sql"
)

# Tenant-scoped tables covered by PF-003A (ADR-015).
RLS_TABLES: tuple[tuple[str, str], ...] = (
    ("core", "tenant"),
    ("core", "tenant_contact"),
    ("core", "tenant_address"),
    ("core", "tenant_status_history"),
    ("core", "tenant_settings"),
    ("core", "organization"),
    ("core", "branch"),
    ("core", "branch_address"),
    ("core", "department"),
    ("core", "business_unit"),
    ("core", "users"),
    ("core", "user_invite"),
    ("core", "subscription"),
    ("core", "subscription_history"),
    ("core", "subscription_usage"),
    ("core", "role"),
    ("core", "idempotency_key"),
    ("audit", "audit_event"),
    ("crm", "lead"),
    ("crm", "opportunity"),
)


def apply_pf003a_ddl(db: Session) -> None:
    sql = _SQL_PATH.read_text(encoding="utf-8")
    with owner_role():
        db.execute(text("RESET ROLE"))
        db.execute(text(sql))
        db.commit()


def rls_enabled(db: Session, schema: str, table: str) -> bool:
    row = db.execute(
        text(
            """
            SELECT c.relrowsecurity AND c.relforcerowsecurity
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = :schema AND c.relname = :table
            """
        ),
        {"schema": schema, "table": table},
    ).first()
    return bool(row and row[0])
