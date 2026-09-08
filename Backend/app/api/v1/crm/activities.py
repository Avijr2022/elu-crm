from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.crm.activity import ActivityCreate, ActivityListResponse, ActivityResponse
from app.services.crm.activity_service import ActivityService

router = APIRouter(prefix="/crm/activities", tags=["CRM Activities"])


@router.get("", response_model=ActivityListResponse)
def list_activities(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    view: str = Query("my", pattern="^(my|overdue|upcoming)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> ActivityListResponse:
    require_permission(current, "activity.read")
    try:
        return ActivityService(db).list_for_owner(
            current.tenant_id,
            current.user_id,
            view=view,
            page=page,
            page_size=page_size,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/timeline", response_model=ActivityListResponse)
def list_timeline(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    entity_type: str = Query(...),
    entity_id: UUID = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> ActivityListResponse:
    require_permission(current, "activity.read")
    try:
        return ActivityService(db).list_for_entity(
            current.tenant_id, entity_type, entity_id, page=page, page_size=page_size
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ActivityResponse:
    require_permission(current, "activity.create")
    try:
        return ActivityService(db).create(current.tenant_id, current.user_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
