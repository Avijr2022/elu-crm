from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.crm import Customer
from app.models.fin import PaymentReceipt
from app.models.sal import SalesOrder


class PaymentReceiptRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, row: PaymentReceipt) -> PaymentReceipt:
        self.db.add(row)
        self.db.flush()
        return row

    def get_by_id(self, tenant_id: UUID, payment_receipt_id: UUID) -> PaymentReceipt | None:
        return self.db.scalars(
            select(PaymentReceipt).where(
                PaymentReceipt.tenant_id == tenant_id,
                PaymentReceipt.payment_receipt_id == payment_receipt_id,
                PaymentReceipt.is_deleted.is_(False),
            )
        ).first()

    def list_for_sales_order(self, tenant_id: UUID, sales_order_id: UUID) -> list[PaymentReceipt]:
        return list(
            self.db.scalars(
                select(PaymentReceipt).where(
                    PaymentReceipt.tenant_id == tenant_id,
                    PaymentReceipt.sales_order_id == sales_order_id,
                    PaymentReceipt.is_deleted.is_(False),
                )
            ).all()
        )

    def list(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        sales_order_id: UUID | None = None,
    ) -> tuple[list[tuple[PaymentReceipt, str | None, str | None]], int]:
        filters = [
            PaymentReceipt.tenant_id == tenant_id,
            PaymentReceipt.is_deleted.is_(False),
        ]
        if sales_order_id is not None:
            filters.append(PaymentReceipt.sales_order_id == sales_order_id)
        total = self.db.scalar(select(func.count()).select_from(PaymentReceipt).where(*filters)) or 0
        stmt = (
            select(PaymentReceipt, Customer.legal_name, SalesOrder.so_number)
            .outerjoin(
                Customer,
                (PaymentReceipt.customer_id == Customer.customer_id)
                & (Customer.tenant_id == tenant_id)
                & Customer.is_deleted.is_(False),
            )
            .outerjoin(
                SalesOrder,
                (PaymentReceipt.sales_order_id == SalesOrder.sales_order_id)
                & (SalesOrder.tenant_id == tenant_id)
                & SalesOrder.is_deleted.is_(False),
            )
            .where(*filters)
            .order_by(PaymentReceipt.received_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self.db.execute(stmt).all()
        return [(row[0], row[1], row[2]) for row in rows], int(total)

    def next_sequence(self, tenant_id: UUID, year: int) -> int:
        prefix = f"PR-{year}-%"
        return int(
            self.db.scalar(
                select(func.count()).select_from(PaymentReceipt).where(
                    PaymentReceipt.tenant_id == tenant_id,
                    PaymentReceipt.receipt_number.like(prefix),
                )
            )
            or 0
        ) + 1
