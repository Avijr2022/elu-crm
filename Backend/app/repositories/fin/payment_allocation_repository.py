from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fin import PaymentAllocation


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
