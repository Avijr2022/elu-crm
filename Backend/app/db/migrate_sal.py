"""SAL DDL applicator (idempotent)."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role

_SAL_DIR = Path(__file__).resolve().parents[3] / "Database" / "05_SAL"
_SAL_SCRIPTS = (
    "001_sal_quotation.sql",
    "002_sal_quotation_line.sql",
    "003_sal_rls.sql",
    "004_sal_quotation_status_history.sql",
    "005_sal_quotation_customer_response.sql",
    "006_sal_sales_order.sql",
    "007_sal_sales_order_line.sql",
    "008_sal_sales_order_payment_stub.sql",
    "009_sal_payment_stub_receipt_link.sql",
)


def apply_sal_ddl(db: Session) -> None:
    with owner_role():
        db.execute(text("RESET ROLE"))
        for name in _SAL_SCRIPTS:
            sql = (_SAL_DIR / name).read_text(encoding="utf-8")
            db.execute(text(sql))
        db.commit()
