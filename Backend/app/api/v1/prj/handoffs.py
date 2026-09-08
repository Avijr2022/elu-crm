from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import PRJ_WO, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.prj.handoff import HandoffResponse
from app.services.prj.handoff_service import HandoffService

router = APIRouter(prefix="/prj/handoffs", tags=["PRJ Handoffs"])


@router.post(
    "/from-opportunity/{opportunity_id}",
    response_model=HandoffResponse,
    status_code=status.HTTP_201_CREATED,
)
def handoff_from_opportunity(
    opportunity_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> HandoffResponse:
    require_feature(db, current.tenant_id, PRJ_WO)
    require_permission(current, "opportunity.approve")
    try:
        wo = HandoffService(db).create_from_opportunity(current.tenant_id, opportunity_id)
        return HandoffResponse(
            handoff_id=wo.work_order_id,
            work_order_id=wo.work_order_id,
            wo_number=wo.wo_number,
            opportunity_id=opportunity_id,
            customer_id=wo.customer_id,
            status=wo.status,
            message=f"Work order {wo.wo_number} queued for delivery",
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc
