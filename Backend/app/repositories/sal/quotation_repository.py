from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sal import Quotation


class QuotationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        opportunity_id: UUID | None = None,
    ) -> tuple[list[Quotation], int]:
        filters = [Quotation.tenant_id == tenant_id, Quotation.is_deleted.is_(False)]
        if status:
            filters.append(Quotation.status == status.upper())
        if opportunity_id:
            filters.append(Quotation.opportunity_id == opportunity_id)
        total = self.db.scalar(select(func.count()).select_from(Quotation).where(*filters)) or 0
        stmt = (
            select(Quotation)
            .where(*filters)
            .order_by(Quotation.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).all()), int(total)

    def get_by_id(self, tenant_id: UUID, quotation_id: UUID) -> Quotation | None:
        return self.db.scalars(
            select(Quotation).where(
                Quotation.tenant_id == tenant_id,
                Quotation.quotation_id == quotation_id,
                Quotation.is_deleted.is_(False),
            )
        ).first()

    def add(self, row: Quotation) -> Quotation:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def next_sequence(self, tenant_id: UUID, year: int) -> int:
        prefix = f"QUO-{year}-%"
        return int(
            self.db.scalar(
                select(func.count()).select_from(Quotation).where(
                    Quotation.tenant_id == tenant_id,
                    Quotation.quotation_number.like(prefix),
                )
            )
            or 0
        ) + 1
