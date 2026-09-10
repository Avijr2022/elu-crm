from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sal import SalesOrderPaymentStub


class SalesOrderPaymentStubRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, row: SalesOrderPaymentStub) -> SalesOrderPaymentStub:
        self.db.add(row)
        self.db.flush()
        return row

    def list_for_order(self, tenant_id: UUID, sales_order_id: UUID) -> list[SalesOrderPaymentStub]:
        return list(
            self.db.scalars(
                select(SalesOrderPaymentStub)
                .where(
                    SalesOrderPaymentStub.tenant_id == tenant_id,
                    SalesOrderPaymentStub.sales_order_id == sales_order_id,
                    SalesOrderPaymentStub.is_deleted.is_(False),
                )
                .order_by(SalesOrderPaymentStub.recorded_on.desc())
            ).all()
        )
