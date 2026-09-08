"""PRJ DDL applicator (idempotent)."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role

_PRJ_DIR = Path(__file__).resolve().parents[3] / "Database" / "06_PRJ"
_PRJ_SCRIPTS = ("001_prj_work_order.sql", "002_prj_work_order_sales_order.sql")


def apply_prj_ddl(db: Session) -> None:
    with owner_role():
        db.execute(text("RESET ROLE"))
        for name in _PRJ_SCRIPTS:
            sql = (_PRJ_DIR / name).read_text(encoding="utf-8")
            db.execute(text(sql))
        db.commit()
