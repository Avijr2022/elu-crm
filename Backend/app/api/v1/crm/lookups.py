from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.crm.lookup import (
    ActivityTypeCreate,
    ActivityTypeListResponse,
    ActivityTypeResponse,
    ActivityTypeUpdate,
    ActivityOutcomeListResponse,
    ActivityOutcomeCreate,
    ActivityOutcomeUpdate,
    ActivityOutcomeResponse,
    CrmLookupsResponse,
    OpportunityStageListResponse,
    OpportunityStageCreate,
    OpportunityStageReorder,
    OpportunityStageResponse,
    OpportunityStageUpdate,
)
from app.services.crm.lookup_service import CrmLookupService

router = APIRouter(prefix="/crm", tags=["CRM Lookups"])


@router.get("/lookups", response_model=CrmLookupsResponse)
def get_crm_lookups(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CrmLookupsResponse:
    require_permission(current, "activity.read")
    try:
        return CrmLookupService(db).get_lookups(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/activity-types", response_model=ActivityTypeListResponse)
def list_activity_types(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    include_inactive: bool = False,
) -> ActivityTypeListResponse:
    require_permission(current, "activity.read")
    try:
        return CrmLookupService(db).list_activity_types(
            current.tenant_id, include_inactive=include_inactive
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/activity-types",
    response_model=ActivityTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity_type(
    payload: ActivityTypeCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ActivityTypeResponse:
    require_permission(current, "activity.create")
    try:
        return CrmLookupService(db).create_activity_type(
            current.tenant_id, current, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/activity-types/{activity_type_id}", response_model=ActivityTypeResponse)
def update_activity_type(
    activity_type_id: UUID,
    payload: ActivityTypeUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ActivityTypeResponse:
    require_permission(current, "activity.create")
    try:
        return CrmLookupService(db).update_activity_type(
            current.tenant_id, current, activity_type_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/activity-outcomes", response_model=ActivityOutcomeListResponse)
def list_activity_outcomes(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    activity_type_code: str | None = None,
    include_inactive: bool = False,
) -> ActivityOutcomeListResponse:
    require_permission(current, "activity.read")
    try:
        return CrmLookupService(db).list_activity_outcomes(
            current.tenant_id,
            activity_type_code=activity_type_code,
            include_inactive=include_inactive,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/activity-outcomes",
    response_model=ActivityOutcomeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity_outcome(
    payload: ActivityOutcomeCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ActivityOutcomeResponse:
    require_permission(current, "activity.create")
    try:
        return CrmLookupService(db).create_activity_outcome(
            current.tenant_id, current, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/activity-outcomes/{outcome_id}", response_model=ActivityOutcomeResponse)
def update_activity_outcome(
    outcome_id: UUID,
    payload: ActivityOutcomeUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ActivityOutcomeResponse:
    require_permission(current, "activity.create")
    try:
        return CrmLookupService(db).update_activity_outcome(
            current.tenant_id, current, outcome_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/opportunity-stages", response_model=OpportunityStageListResponse)
def list_opportunity_stages(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    include_inactive: bool = False,
) -> OpportunityStageListResponse:
    require_permission(current, "opportunity.read")
    try:
        return CrmLookupService(db).list_opportunity_stages(
            current.tenant_id, include_inactive=include_inactive
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/opportunity-stages",
    response_model=OpportunityStageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_opportunity_stage(
    payload: OpportunityStageCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityStageResponse:
    require_permission(current, "opportunity.update")
    try:
        return CrmLookupService(db).create_opportunity_stage(
            current.tenant_id, current, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/opportunity-stages/reorder", response_model=OpportunityStageListResponse)
def reorder_opportunity_stages(
    payload: OpportunityStageReorder,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityStageListResponse:
    require_permission(current, "opportunity.update")
    try:
        return CrmLookupService(db).reorder_opportunity_stages(
            current.tenant_id, current, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/opportunity-stages/{stage_id}", response_model=OpportunityStageResponse)
def update_opportunity_stage(
    stage_id: UUID,
    payload: OpportunityStageUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityStageResponse:
    require_permission(current, "opportunity.update")
    try:
        return CrmLookupService(db).update_opportunity_stage(
            current.tenant_id, current, stage_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc
