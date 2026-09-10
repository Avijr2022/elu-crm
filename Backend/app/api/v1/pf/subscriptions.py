from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.schemas.pf.subscription import (
    SubscriptionCancelRequest,
    SubscriptionCreate,
    SubscriptionHistoryOut,
    SubscriptionListResponse,
    SubscriptionRenewRequest,
    SubscriptionResponse,
    SubscriptionUpdate,
    SubscriptionUpgradeRequest,
    SubscriptionUsageResponse,
    SubscriptionVersionAction,
)
from app.services.pf.subscription_service import (
    SubscriptionService,
    require_platform_admin,
)

router = APIRouter(tags=["PF-003 Subscriptions"])


@router.get(
    "/platform/subscriptions",
    response_model=SubscriptionListResponse,
    summary="List subscriptions",
)
def list_subscriptions(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
) -> SubscriptionListResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).list_subscriptions(
            page=page, page_size=page_size, status=status_filter, search=search
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/subscriptions/search",
    response_model=SubscriptionListResponse,
    summary="Search subscriptions",
)
def search_subscriptions(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> SubscriptionListResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).list_subscriptions(
            page=page, page_size=page_size, search=q
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/subscriptions/export",
    summary="Export subscription register",
)
def export_subscriptions(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).export_rows()
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/subscriptions",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create subscription",
)
def create_subscription(
    payload: SubscriptionCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).create(payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/subscriptions/{subscription_id}",
    response_model=SubscriptionResponse,
    summary="Get subscription detail",
)
def get_subscription(
    subscription_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).get(subscription_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put(
    "/platform/subscriptions/{subscription_id}",
    response_model=SubscriptionResponse,
    summary="Update subscription",
)
def put_subscription(
    subscription_id: UUID,
    payload: SubscriptionUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).update(subscription_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch(
    "/platform/subscriptions/{subscription_id}",
    response_model=SubscriptionResponse,
    summary="Activate trial (TRIAL→ACTIVE) or partial update",
)
def patch_subscription(
    subscription_id: UUID,
    payload: SubscriptionVersionAction,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).convert_trial_to_active(
            subscription_id, current.user_id, payload.version_no
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete(
    "/platform/subscriptions/{subscription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel subscription",
)
def delete_subscription(
    subscription_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    reason: str = Query(..., min_length=3, max_length=500),
    version_no: int = Query(...),
) -> Response:
    require_platform_admin(current.role_code)
    try:
        SubscriptionService(db).cancel(
            subscription_id,
            SubscriptionCancelRequest(version_no=version_no, reason=reason),
            current.user_id,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/subscriptions/{subscription_id}/renew",
    response_model=SubscriptionResponse,
    summary="Renew subscription",
)
def renew_subscription(
    subscription_id: UUID,
    payload: SubscriptionRenewRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).renew(subscription_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/subscriptions/{subscription_id}/upgrade",
    response_model=SubscriptionResponse,
    summary="Upgrade subscription edition",
)
def upgrade_subscription(
    subscription_id: UUID,
    payload: SubscriptionUpgradeRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).upgrade(
            subscription_id, payload, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/subscriptions/{subscription_id}/reactivate",
    response_model=SubscriptionResponse,
    summary="Reactivate expired/suspended subscription",
)
def reactivate_subscription(
    subscription_id: UUID,
    payload: SubscriptionVersionAction,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).reactivate(
            subscription_id, current.user_id, payload.version_no
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/subscriptions/{subscription_id}/expire",
    response_model=SubscriptionResponse,
    summary="Expire subscription and suspend tenant (BR-PF-024)",
)
def expire_subscription(
    subscription_id: UUID,
    payload: SubscriptionVersionAction,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).expire(
            subscription_id, current.user_id, payload.version_no
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/subscriptions/{subscription_id}/history",
    response_model=list[SubscriptionHistoryOut],
    summary="Subscription history",
)
def subscription_history(
    subscription_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[SubscriptionHistoryOut]:
    require_platform_admin(current.role_code)
    try:
        return SubscriptionService(db).history(subscription_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/tenant/subscription",
    response_model=SubscriptionResponse,
    summary="Current tenant subscription",
)
def tenant_subscription(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionResponse:
    try:
        return SubscriptionService(db).tenant_current(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/tenant/subscription/usage",
    response_model=SubscriptionUsageResponse,
    summary="Current tenant subscription usage",
)
def tenant_subscription_usage(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionUsageResponse:
    try:
        svc = SubscriptionService(db)
        current_sub = svc.tenant_current(current.tenant_id)
        return svc.usage(current_sub.id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
