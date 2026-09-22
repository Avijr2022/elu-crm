"""PF-009 Roles & Permissions (RBAC) — Batch 1 DDL + backfill applicator.

Foundation only (PF-009 Batch 1). Applies the guarded DDL in
``Database/03_PlatformFoundation/018_user_role_pf009.sql`` and performs the
idempotent ``core.users.role_id`` -> ``core.user_role`` backfill.

``core.users.role_id`` stays authoritative during the transition: this module
never updates, deletes or rewrites ``core.users`` rows.
"""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role

_SQL_PATH = (
    Path(__file__).resolve().parents[3]
    / "Database"
    / "03_PlatformFoundation"
    / "018_user_role_pf009.sql"
)

# Idempotent mirror of the transitional single role into the M2M table.
# NOT EXISTS + uk_user_role make repeated bootstraps safe.
_BACKFILL_SQL = text(
    """
    INSERT INTO core.user_role (user_role_id, tenant_id, user_id, role_id, is_primary)
    SELECT gen_random_uuid(), u.tenant_id, u.user_id, u.role_id, true
    FROM core.users u
    WHERE u.role_id IS NOT NULL
      AND u.tenant_id IS NOT NULL
      AND u.is_deleted = FALSE
      AND NOT EXISTS (
            SELECT 1
            FROM core.user_role ur
            WHERE ur.user_id = u.user_id
              AND ur.role_id = u.role_id
      )
    """
)


def apply_pf009_ddl(db: Session) -> None:
    """Apply the PF-009 Batch 1 guarded DDL (idempotent)."""
    sql = _SQL_PATH.read_text(encoding="utf-8")
    with owner_role():
        db.execute(text("RESET ROLE"))
        db.execute(text(sql))
        db.commit()


def backfill_user_role(db: Session) -> int:
    """Mirror ``core.users.role_id`` into ``core.user_role``; returns rows added.

    Idempotent and non-destructive: users are never modified, and rows already
    present are skipped.
    """
    with owner_role():
        db.execute(text("RESET ROLE"))
        result = db.execute(_BACKFILL_SQL)
        db.commit()
    return result.rowcount if result.rowcount and result.rowcount > 0 else 0
