from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.crm import Activity, ActivityLink
from app.repositories.crm.activity_repository import ActivityRepository
from app.services.crm.lookup_service import CrmLookupService
from app.schemas.crm.activity import (
    OUTCOME_REQUIRED_TYPES,
    ActivityCreate,
    ActivityListResponse,
    ActivityResponse,
)


class ActivityService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ActivityRepository(db)
        self.lookups = CrmLookupService(db)

    def list_for_entity(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> ActivityListResponse:
        rows, total = self.repo.list_for_entity(
            tenant_id, entity_type, entity_id, page=page, page_size=page_size
        )
        items = [
            ActivityResponse(
                activity_id=a.activity_id,
                tenant_id=a.tenant_id,
                activity_type_code=a.activity_type_code,
                outcome_code=a.outcome_code,
                subject=a.subject,
                description=a.description,
                status=a.status,
                priority=a.priority,
                owner_id=a.owner_id,
                due_on=a.due_on,
                completed_on=a.completed_on,
                entity_type=link.entity_type,
                entity_id=link.entity_id,
                created_on=a.created_on,
                modified_on=a.modified_on,
            )
            for a, link in rows
        ]
        return ActivityListResponse(items=items, total=total, page=page, page_size=page_size)

    def list_for_owner(
        self,
        tenant_id: UUID,
        owner_id: UUID,
        *,
        view: str = "my",
        page: int = 1,
        page_size: int = 50,
    ) -> ActivityListResponse:
        rows, total = self.repo.list_by_owner(
            tenant_id, owner_id, view=view, page=page, page_size=page_size
        )
        items = [
            ActivityResponse(
                activity_id=a.activity_id,
                tenant_id=a.tenant_id,
                activity_type_code=a.activity_type_code,
                outcome_code=a.outcome_code,
                subject=a.subject,
                description=a.description,
                status=a.status,
                priority=a.priority,
                owner_id=a.owner_id,
                due_on=a.due_on,
                completed_on=a.completed_on,
                entity_type=link.entity_type,
                entity_id=link.entity_id,
                created_on=a.created_on,
                modified_on=a.modified_on,
            )
            for a, link in rows
        ]
        return ActivityListResponse(items=items, total=total, page=page, page_size=page_size)

    def create(self, tenant_id: UUID, owner_id: UUID, payload: ActivityCreate) -> ActivityResponse:
        now = datetime.now(timezone.utc)
        type_code = payload.activity_type_code.upper()
        status = (payload.status or "COMPLETED").upper()
        outcome_code = payload.outcome_code.upper() if payload.outcome_code else None
        self.lookups.ensure_tenant_defaults(tenant_id)

        if type_code in OUTCOME_REQUIRED_TYPES and status == "COMPLETED" and not outcome_code:
            raise AppError(
                "VALIDATION_ERROR",
                f"Outcome required when completing {type_code} activity (BR-CRM-063)",
                422,
                req_id="REQ-CRM-039",
            )
        if outcome_code:
            valid = {
                o.code
                for o in self.lookups.repo.list_activity_outcomes(
                    tenant_id, activity_type_code=type_code
                )
            }
            if outcome_code not in valid:
                raise AppError(
                    "VALIDATION_ERROR",
                    f"Invalid outcome '{outcome_code}' for activity type {type_code}",
                    422,
                    req_id="REQ-CRM-039",
                )

        activity = Activity(
            activity_id=uuid4(),
            tenant_id=tenant_id,
            activity_type_code=type_code,
            outcome_code=outcome_code,
            subject=payload.subject.strip(),
            description=payload.description,
            status=status,
            priority=payload.priority,
            owner_id=owner_id,
            due_on=payload.due_on,
            completed_on=now if status == "COMPLETED" else None,
        )
        link = ActivityLink(
            activity_link_id=uuid4(),
            tenant_id=tenant_id,
            activity_id=activity.activity_id,
            entity_type=payload.entity_type.upper(),
            entity_id=payload.entity_id,
        )
        saved = self.repo.add(activity, link)
        return ActivityResponse(
            activity_id=saved.activity_id,
            tenant_id=saved.tenant_id,
            activity_type_code=saved.activity_type_code,
            outcome_code=saved.outcome_code,
            subject=saved.subject,
            description=saved.description,
            status=saved.status,
            priority=saved.priority,
            owner_id=saved.owner_id,
            due_on=saved.due_on,
            completed_on=saved.completed_on,
            entity_type=link.entity_type,
            entity_id=link.entity_id,
            created_on=saved.created_on,
            modified_on=saved.modified_on,
        )

    def log_system_event(
        self,
        tenant_id: UUID,
        owner_id: UUID,
        *,
        entity_type: str,
        entity_id: UUID,
        subject: str,
        description: str | None = None,
    ) -> None:
        self.create(
            tenant_id,
            owner_id,
            ActivityCreate(
                activity_type_code="SYSTEM",
                subject=subject,
                description=description,
                status="COMPLETED",
                entity_type=entity_type,
                entity_id=entity_id,
            ),
        )
