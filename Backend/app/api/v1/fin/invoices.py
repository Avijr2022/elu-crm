from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import FIN_INVOICE, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.fin.invoice import (
    InvoiceDetail,
    InvoiceIssueResponse,
    InvoiceListResponse,
)
from app.services.fin.invoice_service import InvoiceService

router = APIRouter(prefix="/fin/invoices", tags=["FIN Invoices"])


@router.get("", response_model=InvoiceListResponse)
def list_invoices(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    sales_order_id: Optional[UUID] = Query(None),
) -> InvoiceListResponse:
    require_feature(db, current.tenant_id, FIN_INVOICE)
    require_permission(current, "quotation.read")
    try:
        return InvoiceService(db).list_invoices(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status,
            customer_id=customer_id,
            sales_order_id=sales_order_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{invoice_id}", response_model=InvoiceDetail)
def get_invoice(
    invoice_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> InvoiceDetail:
    require_feature(db, current.tenant_id, FIN_INVOICE)
    require_permission(current, "quotation.read")
    try:
        return InvoiceService(db).get_invoice(current.tenant_id, invoice_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/{invoice_id}/issue", response_model=InvoiceIssueResponse)
def issue_invoice(
    invoice_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> InvoiceIssueResponse:
    require_feature(db, current.tenant_id, FIN_INVOICE)
    require_permission(current, "quotation.update")
    try:
        return InvoiceService(db).issue_invoice(current.tenant_id, invoice_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
