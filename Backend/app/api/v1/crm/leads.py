from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import CRM_CUSTOMER, CRM_OPPORTUNITY, has_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.crm.lead import LeadCreate, LeadConvertResponse, LeadDisqualifyRequest, LeadListResponse, LeadResponse, LeadUpdate
from app.services.crm.customer_service import CustomerService
from app.services.crm.lead_service import LeadService
from app.services.crm.opportunity_service import OpportunityService

router = APIRouter(prefix="/crm/leads", tags=["CRM Leads"])


@router.get("", response_model=LeadListResponse)
def list_leads(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
) -> LeadListResponse:
    require_permission(current, "lead.read")
    try:
        return LeadService(db).list_leads(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
            search=search,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    payload: LeadCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LeadResponse:
    require_permission(current, "lead.create")
    try:
        return LeadService(db).create_lead(current.tenant_id, current.user_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LeadResponse:
    require_permission(current, "lead.read")
    try:
        return LeadService(db).get_lead(current.tenant_id, lead_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/{lead_id}", response_model=LeadResponse)
def replace_lead(
    lead_id: UUID,
    payload: LeadUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LeadResponse:
    require_permission(current, "lead.update")
    try:
        return LeadService(db).update_lead(current.tenant_id, lead_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{lead_id}", response_model=LeadResponse)
def patch_lead(
    lead_id: UUID,
    payload: LeadUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LeadResponse:
    require_permission(current, "lead.update")
    try:
        return LeadService(db).update_lead(current.tenant_id, lead_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/{lead_id}/convert", response_model=LeadConvertResponse, status_code=status.HTTP_201_CREATED)
def convert_lead(
    lead_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LeadConvertResponse:
    require_permission(current, "lead.convert")
    try:
        tenant_id = current.tenant_id
        if has_feature(db, tenant_id, CRM_OPPORTUNITY):
            opp = OpportunityService(db).convert_from_lead(
                tenant_id, current.user_id, lead_id
            )
            return LeadConvertResponse(convert_type="OPPORTUNITY", opportunity=opp)
        if has_feature(db, tenant_id, CRM_CUSTOMER):
            customer = CustomerService(db).convert_from_lead(
                tenant_id, current.user_id, lead_id
            )
            return LeadConvertResponse(convert_type="CUSTOMER", customer=customer)
        raise AppError(
            "FORBIDDEN",
            "Lead conversion requires CRM_OPPORTUNITY or CRM_CUSTOMER edition feature",
            403,
            req_id="REQ-EDM-001",
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/{lead_id}/qualify", response_model=LeadResponse)
def qualify_lead(
    lead_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LeadResponse:
    require_permission(current, "lead.qualify")
    try:
        return LeadService(db).qualify_lead(current.tenant_id, lead_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/{lead_id}/disqualify", response_model=LeadResponse)
def disqualify_lead(
    lead_id: UUID,
    payload: LeadDisqualifyRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> LeadResponse:
    require_permission(current, "lead.disqualify")
    try:
        return LeadService(db).disqualify_lead(
            current.tenant_id, lead_id, payload.reason
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    require_permission(current, "lead.update")
    try:
        LeadService(db).delete_lead(current.tenant_id, lead_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
