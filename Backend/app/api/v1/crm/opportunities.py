from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import CRM_OPPORTUNITY, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import can_close_won, can_view_pipeline, require_permission
from app.db.session import get_db
from app.schemas.crm.opportunity import (
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityUpdate,
    PipelineResponse,
    StageUpdate,
)
from app.services.crm.opportunity_service import OpportunityService

router = APIRouter(prefix="/crm/opportunities", tags=["CRM Opportunities"])


def _opp_edition(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CurrentUser:
    require_feature(db, current.tenant_id, CRM_OPPORTUNITY)
    return current


@router.get("/pipeline", response_model=PipelineResponse)
def get_pipeline(
    current: Annotated[CurrentUser, Depends(_opp_edition)],
    db: Annotated[Session, Depends(get_db)],
) -> PipelineResponse:
    try:
        if not can_view_pipeline(current):
            from app.core.exceptions import ForbiddenError

            raise ForbiddenError("Pipeline access requires opportunity.approve", req_id="REQ-CRM-RBAC")
        return OpportunityService(db).pipeline(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("", response_model=OpportunityListResponse)
def list_opportunities(
    current: Annotated[CurrentUser, Depends(_opp_edition)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    stage: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    customer_id: Optional[UUID] = Query(None),
) -> OpportunityListResponse:
    try:
        require_permission(current, "opportunity.read")
        return OpportunityService(db).list_opportunities(
            current.tenant_id,
            page=page,
            page_size=page_size,
            stage=stage,
            status=status_filter,
            search=search,
            customer_id=customer_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityCreate,
    current: Annotated[CurrentUser, Depends(_opp_edition)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        require_permission(current, "opportunity.update")
        return OpportunityService(db).create_opportunity(
            current.tenant_id, current.user_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: UUID,
    current: Annotated[CurrentUser, Depends(_opp_edition)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        require_permission(current, "opportunity.read")
        return OpportunityService(db).get_opportunity(current.tenant_id, opportunity_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
def replace_opportunity(
    opportunity_id: UUID,
    payload: OpportunityUpdate,
    current: Annotated[CurrentUser, Depends(_opp_edition)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        require_permission(current, "opportunity.update")
        return OpportunityService(db).update_opportunity(
            current.tenant_id,
            opportunity_id,
            payload,
            actor_id=current.user_id,
            can_approve=can_close_won(current),
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def patch_opportunity(
    opportunity_id: UUID,
    payload: OpportunityUpdate,
    current: Annotated[CurrentUser, Depends(_opp_edition)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        require_permission(current, "opportunity.update")
        return OpportunityService(db).update_opportunity(
            current.tenant_id,
            opportunity_id,
            payload,
            actor_id=current.user_id,
            can_approve=can_close_won(current),
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{opportunity_id}/stage", response_model=OpportunityResponse)
def advance_stage(
    opportunity_id: UUID,
    payload: StageUpdate,
    current: Annotated[CurrentUser, Depends(_opp_edition)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        require_permission(current, "opportunity.update")
        return OpportunityService(db).advance_stage(
            current.tenant_id, opportunity_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    opportunity_id: UUID,
    current: Annotated[CurrentUser, Depends(_opp_edition)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    try:
        require_permission(current, "opportunity.update")
        OpportunityService(db).delete_opportunity(current.tenant_id, opportunity_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
