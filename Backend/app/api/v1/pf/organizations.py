"""PF-004 Organization Management APIs (ELU-BFS-PF-004 §10)."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.schemas.pf.organization import (
    OrganizationCreate,
    OrganizationHierarchyNode,
    OrganizationHistoryResponse,
    OrganizationListResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.pf.organization_service import (
    OrganizationService,
    require_org_export,
    require_org_read,
    require_org_write,
)

router = APIRouter(prefix="/org/organizations", tags=["PF-004 Organizations"])


@router.get("", response_model=OrganizationListResponse, summary="List organizations")
def list_organizations(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None, description="name|code|status|created_on; prefix - for desc"),
) -> OrganizationListResponse:
    require_org_read(current.role_code)
    try:
        return OrganizationService(db).list_orgs(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
            search=search,
            sort=sort,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/search", response_model=OrganizationListResponse, summary="Search organizations")
def search_organizations(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> OrganizationListResponse:
    require_org_read(current.role_code)
    try:
        return OrganizationService(db).list_orgs(
            current.tenant_id, page=page, page_size=page_size, search=q
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/export", summary="Export organizations")
def export_organizations(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    require_org_export(current.role_code)
    try:
        return OrganizationService(db).export_rows(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/root", response_model=OrganizationResponse, summary="Get root organization")
def get_root_organization(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationResponse:
    require_org_read(current.role_code)
    try:
        return OrganizationService(db).get_root(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/{org_id}/hierarchy",
    response_model=OrganizationHierarchyNode,
    summary="Organization hierarchy tree",
)
def get_hierarchy(
    org_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationHierarchyNode:
    require_org_read(current.role_code)
    try:
        return OrganizationService(db).hierarchy(current.tenant_id, org_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/{org_id}/history",
    response_model=OrganizationHistoryResponse,
    summary="Organization audit history",
)
def get_organization_history(
    org_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationHistoryResponse:
    require_org_read(current.role_code)
    try:
        return OrganizationService(db).history(current.tenant_id, org_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{org_id}", response_model=OrganizationResponse, summary="Get organization")
def get_organization(
    org_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationResponse:
    require_org_read(current.role_code)
    try:
        return OrganizationService(db).get(current.tenant_id, org_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create child organization",
)
def create_organization(
    payload: OrganizationCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationResponse:
    require_org_write(current.role_code)
    try:
        return OrganizationService(db).create(
            current.tenant_id, payload, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/{org_id}", response_model=OrganizationResponse, summary="Replace organization")
def replace_organization(
    org_id: UUID,
    payload: OrganizationUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationResponse:
    require_org_write(current.role_code)
    try:
        return OrganizationService(db).update(
            current.tenant_id, org_id, payload, current.user_id, replace=True
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{org_id}", response_model=OrganizationResponse, summary="Update organization")
def update_organization(
    org_id: UUID,
    payload: OrganizationUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationResponse:
    require_org_write(current.role_code)
    try:
        return OrganizationService(db).update(
            current.tenant_id, org_id, payload, current.user_id, replace=False
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete organization",
)
def delete_organization(
    org_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    require_org_write(current.role_code)
    try:
        OrganizationService(db).soft_delete(current.tenant_id, org_id, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
