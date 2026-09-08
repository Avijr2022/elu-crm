from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sal import SalesOrderLine


class SalesOrderLineRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_order(self, tenant_id: UUID, sales_order_id: UUID) -> list[SalesOrderLine]:
        stmt = (
            select(SalesOrderLine)
            .where(
                SalesOrderLine.tenant_id == tenant_id,
                SalesOrderLine.sales_order_id == sales_order_id,
                SalesOrderLine.is_deleted.is_(False),
            )
            .order_by(SalesOrderLine.line_no)
        )
        return list(self.db.scalars(stmt).all())

    def add(self, row: SalesOrderLine) -> SalesOrderLine:
        self.db.add(row)
        self.db.flush()
        return row
