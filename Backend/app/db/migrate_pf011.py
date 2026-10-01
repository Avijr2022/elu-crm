"""PF-011 System Configuration CORE DDL applicator (idempotent)."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role
from app.db.migrate_pf003a import apply_pf003a_ddl

_SQL_PATH = (
    Path(__file__).resolve().parents[3]
    / "Database"
    / "03_PlatformFoundation"
    / "020_settings_pf011.sql"
)


def apply_pf011_ddl(db: Session) -> None:
    sql = _SQL_PATH.read_text(encoding="utf-8")
    with owner_role():
        db.execute(text("RESET ROLE"))
        db.execute(text(sql))
        db.commit()
    apply_pf003a_ddl(db)
