from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import PRJ_WO, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.prj.work_order import WorkOrderListResponse, WorkOrderResponse
from app.services.prj.work_order_service import WorkOrderService

router = APIRouter(prefix="/prj/work-orders", tags=["PRJ Work Orders"])


@router.get("", response_model=WorkOrderListResponse)
def list_work_orders(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
) -> WorkOrderListResponse:
    require_feature(db, current.tenant_id, PRJ_WO)
    require_permission(current, "opportunity.read")
    try:
        return WorkOrderService(db).list_work_orders(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WorkOrderResponse:
    require_feature(db, current.tenant_id, PRJ_WO)
    require_permission(current, "opportunity.read")
    try:
        return WorkOrderService(db).get_work_order(current.tenant_id, work_order_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
