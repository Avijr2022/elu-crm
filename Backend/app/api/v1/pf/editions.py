from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.repositories.pf.user_repository import TenantRepository
from app.schemas.pf.edition import (
    EditionCreate,
    EditionDeprecateRequest,
    EditionListResponse,
    EditionPatch,
    EditionPublishRequest,
    EditionResponse,
    EditionUpdate,
    EditionVersionOut,
)
from app.services.pf.edition_service import EditionService, require_platform_admin

router = APIRouter(tags=["PF-001 Editions"])


@router.get(
    "/platform/editions",
    response_model=EditionListResponse,
    summary="List editions",
)
def list_editions(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
) -> EditionListResponse:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).list_editions(
            page=page, page_size=page_size, status=status_filter, search=search
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/editions/search",
    response_model=EditionListResponse,
    summary="Search editions",
)
def search_editions(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> EditionListResponse:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).list_editions(
            page=page, page_size=page_size, search=q
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/editions/export",
    summary="Export edition feature matrix",
)
def export_editions(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).export_matrix()
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/editions",
    response_model=EditionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create edition draft",
)
def create_edition(
    payload: EditionCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EditionResponse:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).create(payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/editions/{edition_id}",
    response_model=EditionResponse,
    summary="Get edition detail",
)
def get_edition(
    edition_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EditionResponse:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).get_edition(edition_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put(
    "/platform/editions/{edition_id}",
    response_model=EditionResponse,
    summary="Full update edition (draft or ACTIVE matrix bump)",
)
def put_edition(
    edition_id: UUID,
    payload: EditionUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EditionResponse:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).update(edition_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch(
    "/platform/editions/{edition_id}",
    response_model=EditionResponse,
    summary="Partial update edition",
)
def patch_edition(
    edition_id: UUID,
    payload: EditionPatch,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EditionResponse:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).patch(edition_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete(
    "/platform/editions/{edition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel draft or archive edition",
)
def delete_edition(
    edition_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    require_platform_admin(current.role_code)
    try:
        EditionService(db).delete(edition_id, current.user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/editions/{edition_id}/publish",
    response_model=EditionResponse,
    summary="Publish draft edition to ACTIVE",
)
def publish_edition(
    edition_id: UUID,
    payload: EditionPublishRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EditionResponse:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).publish(edition_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/platform/editions/{edition_id}/deprecate",
    response_model=EditionResponse,
    summary="Deprecate ACTIVE edition",
)
def deprecate_edition(
    edition_id: UUID,
    payload: EditionDeprecateRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EditionResponse:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).deprecate(edition_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/platform/editions/{edition_id}/history",
    response_model=list[EditionVersionOut],
    summary="Edition version history",
)
def edition_history(
    edition_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[EditionVersionOut]:
    require_platform_admin(current.role_code)
    try:
        return EditionService(db).history(edition_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/tenant/edition",
    response_model=EditionResponse,
    summary="Tenant current edition (read-only)",
)
def tenant_edition(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EditionResponse:
    try:
        tenant = TenantRepository(db).get_by_id(current.tenant_id)
        if tenant is None:
            raise AppError("NOT_FOUND", "Tenant not found", 404)
        return EditionService(db).tenant_edition(tenant.edition_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
