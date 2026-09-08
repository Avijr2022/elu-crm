from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sal import QuotationLine


class QuotationLineRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_quotation(self, tenant_id: UUID, quotation_id: UUID) -> list[QuotationLine]:
        stmt = (
            select(QuotationLine)
            .where(
                QuotationLine.tenant_id == tenant_id,
                QuotationLine.quotation_id == quotation_id,
                QuotationLine.is_deleted.is_(False),
            )
            .order_by(QuotationLine.line_no)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(
        self, tenant_id: UUID, quotation_id: UUID, line_id: UUID
    ) -> QuotationLine | None:
        return self.db.scalars(
            select(QuotationLine).where(
                QuotationLine.tenant_id == tenant_id,
                QuotationLine.quotation_id == quotation_id,
                QuotationLine.quotation_line_id == line_id,
                QuotationLine.is_deleted.is_(False),
            )
        ).first()

    def next_line_no(self, tenant_id: UUID, quotation_id: UUID) -> int:
        current = self.db.scalar(
            select(func.max(QuotationLine.line_no)).where(
                QuotationLine.tenant_id == tenant_id,
                QuotationLine.quotation_id == quotation_id,
            )
        )
        return int(current or 0) + 1

    def add(self, row: QuotationLine) -> QuotationLine:
        self.db.add(row)
        self.db.flush()
        return row

    def soft_delete(self, row: QuotationLine) -> None:
        row.is_deleted = True
        row.is_active = False
        self.db.flush()
