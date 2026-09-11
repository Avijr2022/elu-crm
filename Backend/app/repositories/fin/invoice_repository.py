from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.crm import Customer
from app.models.fin import Invoice
from app.models.sal import SalesOrder


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

    def list_invoices(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        customer_id: UUID | None = None,
        sales_order_id: UUID | None = None,
    ) -> tuple[list[tuple[Invoice, str | None, str | None]], int]:
        filters = [
            Invoice.tenant_id == tenant_id,
            Invoice.is_deleted.is_(False),
        ]
        if status is not None:
            filters.append(Invoice.status == status)
        if customer_id is not None:
            filters.append(Invoice.customer_id == customer_id)
        if sales_order_id is not None:
            filters.append(Invoice.sales_order_id == sales_order_id)
        total = (
            self.db.scalar(select(func.count()).select_from(Invoice).where(*filters)) or 0
        )
        stmt = (
            select(Invoice, Customer.legal_name, SalesOrder.so_number)
            .outerjoin(
                Customer,
                (Invoice.customer_id == Customer.customer_id)
                & (Customer.tenant_id == tenant_id)
                & Customer.is_deleted.is_(False),
            )
            .outerjoin(
                SalesOrder,
                (Invoice.sales_order_id == SalesOrder.sales_order_id)
                & (SalesOrder.tenant_id == tenant_id)
                & SalesOrder.is_deleted.is_(False),
            )
            .where(*filters)
            .order_by(Invoice.created_on.desc(), Invoice.invoice_number.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self.db.execute(stmt).all()
        return [(row[0], row[1], row[2]) for row in rows], int(total)
