from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.crm import Opportunity


class OpportunityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        stage: str | None = None,
        status: str | None = None,
        search: str | None = None,
        customer_id: UUID | None = None,
    ) -> tuple[list[Opportunity], int]:
        filters = [
            Opportunity.tenant_id == tenant_id,
            Opportunity.is_deleted.is_(False),
        ]
        if customer_id:
            filters.append(Opportunity.customer_id == customer_id)
        if stage:
            filters.append(Opportunity.stage == stage.upper())
        if status:
            filters.append(Opportunity.status == status.upper())
        if search:
            like = f"%{search.strip()}%"
            filters.append(
                or_(
                    Opportunity.name.ilike(like),
                    Opportunity.company_name.ilike(like),
                    Opportunity.opportunity_number.ilike(like),
                )
            )

        total = self.db.scalar(
            select(func.count()).select_from(Opportunity).where(*filters)
        ) or 0
        stmt = (
            select(Opportunity)
            .where(*filters)
            .order_by(Opportunity.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).all()), int(total)

    def list_open_pipeline(self, tenant_id: UUID) -> list[Opportunity]:
        stmt = (
            select(Opportunity)
            .where(
                Opportunity.tenant_id == tenant_id,
                Opportunity.is_deleted.is_(False),
                Opportunity.status.in_(("OPEN", "REOPENED", "ON_HOLD")),
            )
            .order_by(Opportunity.created_on.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, tenant_id: UUID, opportunity_id: UUID) -> Opportunity | None:
        stmt = select(Opportunity).where(
            Opportunity.tenant_id == tenant_id,
            Opportunity.opportunity_id == opportunity_id,
            Opportunity.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def next_sequence(self, tenant_id: UUID, year: int) -> int:
        prefix = f"%-OPP-{year}-%"
        stmt = select(func.count()).select_from(Opportunity).where(
            Opportunity.tenant_id == tenant_id,
            Opportunity.opportunity_number.like(prefix),
        )
        return int(self.db.scalar(stmt) or 0) + 1

    def add(self, opportunity: Opportunity) -> Opportunity:
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    def save(self, opportunity: Opportunity) -> Opportunity:
        opportunity.modified_on = datetime.now(timezone.utc)
        opportunity.version_no = int(opportunity.version_no or 1) + 1
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity
