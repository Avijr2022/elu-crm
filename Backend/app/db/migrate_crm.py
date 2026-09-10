"""CRM DDL applicator (idempotent)."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role

_CRM_DIR = Path(__file__).resolve().parents[3] / "Database" / "04_CRM"
_CRM_SCRIPTS = (
    "003_crm_customer.sql",
    "004_crm_activity.sql",
    "005_crm_customer_contact_address.sql",
    "006_crm_lookup.sql",
    "007_crm_activity_outcome.sql",
)


def apply_crm_ddl(db: Session) -> None:
    with owner_role():
        db.execute(text("RESET ROLE"))
        for name in _CRM_SCRIPTS:
            sql = (_CRM_DIR / name).read_text(encoding="utf-8")
            db.execute(text(sql))
        db.commit()
