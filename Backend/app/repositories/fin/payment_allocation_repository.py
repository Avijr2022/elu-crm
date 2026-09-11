from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.fin import PaymentAllocation, PaymentReceipt


class PaymentAllocationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, row: PaymentAllocation) -> PaymentAllocation:
        self.db.add(row)
        self.db.flush()
        return row

    def list_for_receipt(self, tenant_id: UUID, payment_receipt_id: UUID) -> list[PaymentAllocation]:
        return list(
            self.db.scalars(
                select(PaymentAllocation).where(
                    PaymentAllocation.tenant_id == tenant_id,
                    PaymentAllocation.payment_receipt_id == payment_receipt_id,
                    PaymentAllocation.is_deleted.is_(False),
                )
            ).all()
        )

    def list_for_invoice(
        self, tenant_id: UUID, invoice_id: UUID
    ) -> list[tuple[PaymentAllocation, str | None]]:
        """Allocations for one invoice, each paired with its receipt number."""
        stmt = (
            select(PaymentAllocation, PaymentReceipt.receipt_number)
            .outerjoin(
                PaymentReceipt,
                (PaymentAllocation.payment_receipt_id == PaymentReceipt.payment_receipt_id)
                & (PaymentReceipt.tenant_id == tenant_id)
                & PaymentReceipt.is_deleted.is_(False),
            )
            .where(
                PaymentAllocation.tenant_id == tenant_id,
                PaymentAllocation.invoice_id == invoice_id,
                PaymentAllocation.is_deleted.is_(False),
            )
            .order_by(PaymentAllocation.created_on.asc())
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]

    def allocated_totals_for_invoices(
        self, tenant_id: UUID, invoice_ids: list[UUID]
    ) -> dict[UUID, Decimal]:
        """Grouped allocation totals for a page of invoices (avoids N+1 queries)."""
        if not invoice_ids:
            return {}
        rows = self.db.execute(
            select(
                PaymentAllocation.invoice_id,
                func.coalesce(func.sum(PaymentAllocation.allocated_amount), 0),
            )
            .where(
                PaymentAllocation.tenant_id == tenant_id,
                PaymentAllocation.invoice_id.in_(invoice_ids),
                PaymentAllocation.is_deleted.is_(False),
            )
            .group_by(PaymentAllocation.invoice_id)
        ).all()
        return {row[0]: Decimal(str(row[1] or 0)) for row in rows}
