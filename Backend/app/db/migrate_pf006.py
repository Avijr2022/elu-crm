"""PF-006 department DDL applicator (idempotent)."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role

_SQL_PATH = (
    Path(__file__).resolve().parents[3]
    / "Database"
    / "03_PlatformFoundation"
    / "015_department_pf006.sql"
)


def apply_pf006_ddl(db: Session) -> None:
    sql = _SQL_PATH.read_text(encoding="utf-8")
    with owner_role():
        db.execute(text("RESET ROLE"))
        db.execute(text(sql))
        db.commit()
