from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.crm import Activity, ActivityLink


class ActivityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_entity(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[tuple[Activity, ActivityLink]], int]:
        filters = [
            ActivityLink.tenant_id == tenant_id,
            ActivityLink.entity_type == entity_type.upper(),
            ActivityLink.entity_id == entity_id,
            Activity.is_deleted.is_(False),
        ]
        base = (
            select(Activity, ActivityLink)
            .join(ActivityLink, ActivityLink.activity_id == Activity.activity_id)
            .where(*filters)
        )
        total = len(
            list(
                self.db.scalars(
                    select(Activity.activity_id)
                    .join(ActivityLink, ActivityLink.activity_id == Activity.activity_id)
                    .where(*filters)
                ).all()
            )
        )
        stmt = base.order_by(Activity.created_on.desc()).offset((page - 1) * page_size).limit(page_size)
        rows = list(self.db.execute(stmt).all())
        return [(r[0], r[1]) for r in rows], int(total)

    def list_by_owner(
        self,
        tenant_id: UUID,
        owner_id: UUID,
        *,
        view: str = "my",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[tuple[Activity, ActivityLink]], int]:
        now = datetime.now(timezone.utc)
        filters = [
            Activity.tenant_id == tenant_id,
            Activity.owner_id == owner_id,
            Activity.is_deleted.is_(False),
        ]
        if view == "overdue":
            filters.extend(
                [
                    Activity.status.notin_(("COMPLETED", "CANCELLED")),
                    Activity.due_on.isnot(None),
                    Activity.due_on < now,
                ]
            )
        elif view == "upcoming":
            filters.extend(
                [
                    Activity.status.notin_(("COMPLETED", "CANCELLED")),
                    Activity.due_on.isnot(None),
                    Activity.due_on >= now,
                ]
            )

        base = (
            select(Activity, ActivityLink)
            .join(ActivityLink, ActivityLink.activity_id == Activity.activity_id)
            .where(*filters)
        )
        total = self.db.scalar(
            select(func.count())
            .select_from(Activity)
            .join(ActivityLink, ActivityLink.activity_id == Activity.activity_id)
            .where(*filters)
        ) or 0
        stmt = (
            base.order_by(Activity.due_on.asc().nullslast(), Activity.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = list(self.db.execute(stmt).all())
        return [(r[0], r[1]) for r in rows], int(total)

    def add(self, activity: Activity, link: ActivityLink) -> Activity:
        self.db.add(activity)
        self.db.add(link)
        self.db.commit()
        self.db.refresh(activity)
        return activity
