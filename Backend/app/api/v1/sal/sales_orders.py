from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import FIN_INVOICE, SAL_QUOTE, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.fin.payment_receipt import InvoiceGenerateResponse
from app.schemas.sal.sales_order import (
    SalesOrderConfirmResponse,
    SalesOrderDetailResponse,
    SalesOrderListResponse,
    SalesOrderPaymentStubResponse,
)
from app.services.fin.invoice_service import InvoiceService
from app.services.sal.sales_order_service import SalesOrderService

router = APIRouter(prefix="/sal/sales-orders", tags=["SAL Sales Orders"])


@router.get("", response_model=SalesOrderListResponse)
def list_sales_orders(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    opportunity_id: Optional[UUID] = Query(None),
    customer_id: Optional[UUID] = Query(None),
) -> SalesOrderListResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.read")
    try:
        return SalesOrderService(db).list_sales_orders(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
            opportunity_id=opportunity_id,
            customer_id=customer_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{sales_order_id}", response_model=SalesOrderDetailResponse)
def get_sales_order(
    sales_order_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SalesOrderDetailResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.read")
    try:
        return SalesOrderService(db).get_sales_order(current.tenant_id, sales_order_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/{sales_order_id}/confirm", response_model=SalesOrderConfirmResponse)
def confirm_sales_order(
    sales_order_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SalesOrderConfirmResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    try:
        return SalesOrderService(db).confirm_sales_order(
            current.tenant_id, sales_order_id, current.permissions
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/{sales_order_id}/record-payment-stub", response_model=SalesOrderPaymentStubResponse)
def record_payment_stub(
    sales_order_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SalesOrderPaymentStubResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    try:
        return SalesOrderService(db).record_payment_stub(
            current.tenant_id,
            sales_order_id,
            current.permissions,
            actor_id=current.user_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/{sales_order_id}/generate-invoice-stub", response_model=InvoiceGenerateResponse)
def generate_invoice_stub(
    sales_order_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> InvoiceGenerateResponse:
    require_feature(db, current.tenant_id, FIN_INVOICE)
    try:
        return InvoiceService(db).generate_from_sales_order(
            current.tenant_id, sales_order_id, current.permissions
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc
