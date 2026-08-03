from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
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


@router.get("/pipeline", response_model=PipelineResponse)
def get_pipeline(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PipelineResponse:
    try:
        return OpportunityService(db).pipeline(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("", response_model=OpportunityListResponse)
def list_opportunities(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    stage: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
) -> OpportunityListResponse:
    try:
        return OpportunityService(db).list_opportunities(
            current.tenant_id,
            page=page,
            page_size=page_size,
            stage=stage,
            status=status_filter,
            search=search,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        return OpportunityService(db).create_opportunity(
            current.tenant_id, current.user_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        return OpportunityService(db).get_opportunity(current.tenant_id, opportunity_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
def replace_opportunity(
    opportunity_id: UUID,
    payload: OpportunityUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        return OpportunityService(db).update_opportunity(
            current.tenant_id, opportunity_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def patch_opportunity(
    opportunity_id: UUID,
    payload: OpportunityUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        return OpportunityService(db).update_opportunity(
            current.tenant_id, opportunity_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{opportunity_id}/stage", response_model=OpportunityResponse)
def advance_stage(
    opportunity_id: UUID,
    payload: StageUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OpportunityResponse:
    try:
        return OpportunityService(db).advance_stage(
            current.tenant_id, opportunity_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    opportunity_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    try:
        OpportunityService(db).delete_opportunity(current.tenant_id, opportunity_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
