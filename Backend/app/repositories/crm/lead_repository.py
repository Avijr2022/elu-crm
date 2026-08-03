from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.crm import Lead


class LeadRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Lead], int]:
        filters = [
            Lead.tenant_id == tenant_id,
            Lead.is_deleted.is_(False),
        ]
        if status:
            filters.append(Lead.status == status.upper())
        if search:
            like = f"%{search.strip()}%"
            filters.append(
                or_(
                    Lead.full_name.ilike(like),
                    Lead.company_name.ilike(like),
                    Lead.email.ilike(like),
                    Lead.lead_number.ilike(like),
                )
            )

        total = self.db.scalar(
            select(func.count()).select_from(Lead).where(*filters)
        ) or 0

        stmt = (
            select(Lead)
            .where(*filters)
            .order_by(Lead.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).all()), int(total)

    def get_by_id(self, tenant_id: UUID, lead_id: UUID) -> Lead | None:
        stmt = select(Lead).where(
            Lead.tenant_id == tenant_id,
            Lead.lead_id == lead_id,
            Lead.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def next_sequence(self, tenant_id: UUID, year: int) -> int:
        prefix = f"%-LD-{year}-%"
        stmt = select(func.count()).select_from(Lead).where(
            Lead.tenant_id == tenant_id,
            Lead.lead_number.like(prefix),
        )
        return int(self.db.scalar(stmt) or 0) + 1

    def add(self, lead: Lead) -> Lead:
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def save(self, lead: Lead) -> Lead:
        lead.modified_on = datetime.now(timezone.utc)
        lead.version_no = int(lead.version_no or 1) + 1
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
