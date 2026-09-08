from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sal import QuotationStatusHistory


class QuotationStatusHistoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(
        self,
        tenant_id: UUID,
        quotation_id: UUID,
        from_status: str,
        to_status: str,
        actor_id: UUID | None,
        reason: str | None = None,
    ) -> QuotationStatusHistory:
        row = QuotationStatusHistory(
            quotation_status_history_id=uuid4(),
            tenant_id=tenant_id,
            quotation_id=quotation_id,
            from_status=from_status,
            to_status=to_status,
            actor_id=actor_id,
            reason=reason,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_for_quotation(self, tenant_id: UUID, quotation_id: UUID) -> list[QuotationStatusHistory]:
        stmt = (
            select(QuotationStatusHistory)
            .where(
                QuotationStatusHistory.tenant_id == tenant_id,
                QuotationStatusHistory.quotation_id == quotation_id,
                QuotationStatusHistory.is_deleted.is_(False),
            )
            .order_by(QuotationStatusHistory.changed_on.desc())
        )
        return list(self.db.scalars(stmt).all())
