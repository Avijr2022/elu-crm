from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.schemas.pf.tenant import (
    TenantCreate,
    TenantListResponse,
    TenantResponse,
    TenantSuspendRequest,
    TenantUpdate,
    TenantVersionAction,
)
from app.services.pf.tenant_service import TenantService, require_platform_admin

router = APIRouter(tags=["PF-002 Tenants"])


@router.get(
    "/platform/tenants",
    response_model=TenantListResponse,
    summary="List tenants",
)
def list_tenants(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
) -> TenantListResponse:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).list_tenants(
            page=page, page_size=page_size, status=status_filter, search=search
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/tenants/search",
    response_model=TenantListResponse,
    summary="Search tenants",
)
def search_tenants(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> TenantListResponse:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).list_tenants(
            page=page, page_size=page_size, search=q
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/tenants/export",
    summary="Export tenant directory",
)
def export_tenants(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).export_rows()
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/tenants",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register tenant",
)
def create_tenant(
    payload: TenantCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
) -> TenantResponse:
    require_platform_admin(current.role_code)
    try:
        resp, http_status = TenantService(db).create(
            payload, current.user_id, idempotency_key=idempotency_key
        )
        if http_status != 201:
            # Idempotent replay — FastAPI status_code on decorator is 201; return body only
            return resp
        return resp
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/tenants/{tenant_id}",
    response_model=TenantResponse,
    summary="Get tenant detail",
)
def get_tenant(
    tenant_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).get_tenant(tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put(
    "/platform/tenants/{tenant_id}",
    response_model=TenantResponse,
    summary="Update tenant profile",
)
def put_tenant(
    tenant_id: UUID,
    payload: TenantUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).update(tenant_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch(
    "/platform/tenants/{tenant_id}",
    response_model=TenantResponse,
    summary="Partial update tenant profile",
)
def patch_tenant(
    tenant_id: UUID,
    payload: TenantUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).update(tenant_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete(
    "/platform/tenants/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-close tenant (CLOSED)",
)
def delete_tenant(
    tenant_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    require_platform_admin(current.role_code)
    try:
        TenantService(db).soft_delete(tenant_id, current.user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/tenants/{tenant_id}/approve",
    response_model=TenantResponse,
    summary="Approve pending tenant → ACTIVE",
)
def approve_tenant(
    tenant_id: UUID,
    payload: TenantVersionAction,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).approve(
            tenant_id, current.user_id, payload.version_no
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/tenants/{tenant_id}/suspend",
    response_model=TenantResponse,
    summary="Suspend ACTIVE/TRIAL tenant",
)
def suspend_tenant(
    tenant_id: UUID,
    payload: TenantSuspendRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).suspend(tenant_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/tenants/{tenant_id}/reactivate",
    response_model=TenantResponse,
    summary="Reactivate SUSPENDED tenant",
)
def reactivate_tenant(
    tenant_id: UUID,
    payload: TenantVersionAction,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    require_platform_admin(current.role_code)
    try:
        return TenantService(db).reactivate(
            tenant_id, current.user_id, payload.version_no
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/tenant/profile",
    response_model=TenantResponse,
    summary="Current tenant profile (own tenant only)",
)
def tenant_profile(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    try:
        return TenantService(db).get_tenant(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
