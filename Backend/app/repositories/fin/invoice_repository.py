from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.fin import Invoice


class InvoiceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, row: Invoice) -> Invoice:
        self.db.add(row)
        self.db.flush()
        return row

    def get_by_sales_order(self, tenant_id: UUID, sales_order_id: UUID) -> Invoice | None:
        return self.db.scalars(
            select(Invoice).where(
                Invoice.tenant_id == tenant_id,
                Invoice.sales_order_id == sales_order_id,
                Invoice.is_deleted.is_(False),
            )
        ).first()

    def get_by_id(self, tenant_id: UUID, invoice_id: UUID) -> Invoice | None:
        return self.db.scalars(
            select(Invoice).where(
                Invoice.tenant_id == tenant_id,
                Invoice.invoice_id == invoice_id,
                Invoice.is_deleted.is_(False),
            )
        ).first()

    def next_sequence(self, tenant_id: UUID, year: int) -> int:
        prefix = f"INV-{year}-%"
        return int(
            self.db.scalar(
                select(func.count()).select_from(Invoice).where(
                    Invoice.tenant_id == tenant_id,
                    Invoice.invoice_number.like(prefix),
                )
            )
            or 0
        ) + 1
