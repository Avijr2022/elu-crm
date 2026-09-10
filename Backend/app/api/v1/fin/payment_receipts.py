from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import SAL_QUOTE, FIN_INVOICE, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.fin.payment_receipt import (
    PaymentAllocationResponse,
    PaymentReceiptDetailResponse,
    PaymentReceiptListResponse,
)
from app.services.fin.payment_receipt_service import PaymentReceiptService
from uuid import UUID
from pydantic import BaseModel

router = APIRouter(prefix="/fin/payment-receipts", tags=["FIN Payment Receipts"])


class AllocateRequest(BaseModel):
    invoice_id: UUID
    allocated_amount: Optional[float] = None


@router.post("/{payment_receipt_id}/allocate", response_model=PaymentAllocationResponse)
def allocate_receipt(
    payment_receipt_id: UUID,
    body: AllocateRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    require_feature(db, current.tenant_id, FIN_INVOICE)
    require_permission(current, "quotation.update")
    try:
        # Pass optional allocated_amount to the service to support partial allocations
        alloc = PaymentReceiptService(db).allocate_to_invoice(
            current.tenant_id, payment_receipt_id, body.invoice_id, current.permissions, body.allocated_amount
        )
        return alloc
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("", response_model=PaymentReceiptListResponse)
def list_payment_receipts(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    sales_order_id: Optional[UUID] = Query(None),
) -> PaymentReceiptListResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.read")
    try:
        return PaymentReceiptService(db).list_payment_receipts(
            current.tenant_id,
            page=page,
            page_size=page_size,
            sales_order_id=sales_order_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{payment_receipt_id}", response_model=PaymentReceiptDetailResponse)
def get_payment_receipt(
    payment_receipt_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PaymentReceiptDetailResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.read")
    try:
        return PaymentReceiptService(db).get_payment_receipt(
            current.tenant_id, payment_receipt_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc
