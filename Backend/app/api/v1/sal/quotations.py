from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import SAL_QUOTE, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.sal.quotation import (
    QuotationCreate,
    QuotationCustomerResponseCreate,
    QuotationDetailResponse,
    QuotationLineCreate,
    QuotationLineResponse,
    QuotationLineUpdate,
    QuotationListResponse,
    QuotationResponse,
    QuotationStatusHistoryResponse,
    QuotationStatusUpdate,
    SalesOrderConvertResponse,
)
from app.services.sal.quotation_service import QuotationService

router = APIRouter(prefix="/sal/quotations", tags=["SAL Quotations"])


@router.get("", response_model=QuotationListResponse)
def list_quotations(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    opportunity_id: Optional[UUID] = None,
) -> QuotationListResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.read")
    try:
        return QuotationService(db).list_quotations(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
            opportunity_id=opportunity_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
def create_quotation(
    payload: QuotationCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> QuotationResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.create")
    try:
        return QuotationService(db).create_quotation(
            current.tenant_id, current.user_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{quotation_id}", response_model=QuotationDetailResponse)
def get_quotation(
    quotation_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> QuotationDetailResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.read")
    try:
        return QuotationService(db).get_quotation(current.tenant_id, quotation_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{quotation_id}/export")
def export_quotation_pdf(
    quotation_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.read")
    try:
        pdf, filename = QuotationService(db).export_pdf(current.tenant_id, quotation_id)
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/{quotation_id}/convert-to-order",
    response_model=SalesOrderConvertResponse,
    status_code=status.HTTP_201_CREATED,
)
def convert_quotation_to_sales_order(
    quotation_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SalesOrderConvertResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    try:
        return QuotationService(db).convert_to_sales_order(
            current.tenant_id, quotation_id, current.permissions
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{quotation_id}/status", response_model=QuotationResponse)
def update_quotation_status(
    quotation_id: UUID,
    payload: QuotationStatusUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> QuotationResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    try:
        return QuotationService(db).transition_status(
            current.tenant_id,
            quotation_id,
            payload,
            current.permissions,
            current.user_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{quotation_id}/history", response_model=list[QuotationStatusHistoryResponse])
def list_quotation_history(
    quotation_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[QuotationStatusHistoryResponse]:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.read")
    try:
        return QuotationService(db).list_status_history(current.tenant_id, quotation_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/{quotation_id}/customer-response", response_model=QuotationResponse)
def record_customer_response(
    quotation_id: UUID,
    payload: QuotationCustomerResponseCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> QuotationResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.update")
    try:
        return QuotationService(db).record_customer_response(
            current.tenant_id,
            quotation_id,
            payload,
            current.permissions,
            current.user_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/{quotation_id}/lines",
    response_model=QuotationLineResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_quotation_line(
    quotation_id: UUID,
    payload: QuotationLineCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> QuotationLineResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.update")
    try:
        return QuotationService(db).add_line(current.tenant_id, quotation_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/{quotation_id}/lines/{line_id}", response_model=QuotationLineResponse)
def update_quotation_line(
    quotation_id: UUID,
    line_id: UUID,
    payload: QuotationLineUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> QuotationLineResponse:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.update")
    try:
        return QuotationService(db).update_line(
            current.tenant_id, quotation_id, line_id, payload
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete("/{quotation_id}/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quotation_line(
    quotation_id: UUID,
    line_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    require_feature(db, current.tenant_id, SAL_QUOTE)
    require_permission(current, "quotation.update")
    try:
        QuotationService(db).delete_line(current.tenant_id, quotation_id, line_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
