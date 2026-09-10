from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import CRM_OPPORTUNITY, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.crm.customer import (
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerContactCreate,
    CustomerContactResponse,
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.schemas.crm.opportunity import OpportunityListResponse
from app.services.crm.customer_service import CustomerService
from app.services.crm.opportunity_service import OpportunityService

router = APIRouter(prefix="/crm/customers", tags=["CRM Customers"])


@router.get("", response_model=CustomerListResponse)
def list_customers(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> CustomerListResponse:
    require_permission(current, "customer.read")
    try:
        return CustomerService(db).list_customers(
            current.tenant_id,
            page=page,
            page_size=page_size,
            search=search,
            status=status,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CustomerResponse:
    require_permission(current, "customer.create")
    try:
        return CustomerService(db).create_customer(current.tenant_id, current.user_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CustomerResponse:
    require_permission(current, "customer.read")
    try:
        return CustomerService(db).get_customer(current.tenant_id, customer_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{customer_id}", response_model=CustomerResponse)
def patch_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CustomerResponse:
    require_permission(current, "customer.update")
    try:
        return CustomerService(db).update_customer(current.tenant_id, customer_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{customer_id}/opportunities", response_model=OpportunityListResponse)
def list_customer_opportunities(
    customer_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
) -> OpportunityListResponse:
    require_feature(db, current.tenant_id, CRM_OPPORTUNITY)
    require_permission(current, "opportunity.read")
    try:
        CustomerService(db).get_customer(current.tenant_id, customer_id)
        return OpportunityService(db).list_opportunities(
            current.tenant_id,
            page=page,
            page_size=page_size,
            customer_id=customer_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/{customer_id}/contacts",
    response_model=CustomerContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_contact(
    customer_id: UUID,
    payload: CustomerContactCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CustomerContactResponse:
    require_permission(current, "customer.update")
    try:
        return CustomerService(db).add_contact(current.tenant_id, customer_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/{customer_id}/addresses",
    response_model=CustomerAddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_address(
    customer_id: UUID,
    payload: CustomerAddressCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CustomerAddressResponse:
    require_permission(current, "customer.update")
    try:
        return CustomerService(db).add_address(current.tenant_id, customer_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
