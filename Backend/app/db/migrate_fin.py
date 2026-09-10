"""FIN DDL applicator (idempotent)."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role

_FIN_DIR = Path(__file__).resolve().parents[3] / "Database" / "07_FIN"
_FIN_SCRIPTS = (
    "001_fin_payment_receipt.sql",
    "002_fin_invoice.sql",
    "003_fin_payment_allocation.sql",
)


def apply_fin_ddl(db: Session) -> None:
    with owner_role():
        db.execute(text("RESET ROLE"))
        for name in _FIN_SCRIPTS:
            sql = (_FIN_DIR / name).read_text(encoding="utf-8")
            db.execute(text(sql))
        db.commit()
