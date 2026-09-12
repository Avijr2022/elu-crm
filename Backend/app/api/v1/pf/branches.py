"""PF-005 Branch Management APIs (ELU-BFS-PF-005 §10).

Exactly the nine approved endpoints are exposed. BFS-PF-005 §10 does not list
`/org/branches/{id}/history`, so no history endpoint is registered here even
though the service/schemas support it.

Static segments (`/search`, `/export`, `/hierarchy`) are declared before
`/{branch_id}` so they are not shadowed by the path parameter.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.schemas.pf.branch import (
    BranchCreate,
    BranchHierarchyResponse,
    BranchListResponse,
    BranchReplace,
    BranchResponse,
    BranchUpdate,
)
from app.services.pf.branch_service import (
    BranchService,
    require_branch_export,
    require_branch_read,
    require_branch_write,
)

router = APIRouter(prefix="/org/branches", tags=["PF-005 Branches"])


@router.get("", response_model=BranchListResponse, summary="List branches")
def list_branches(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    branch_type: Optional[str] = Query(None),
    organization_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(
        None, description="name|code|status|type|created_on; prefix - for desc"
    ),
) -> BranchListResponse:
    require_branch_read(current.role_code)
    service = BranchService(db)
    try:
        service.assert_branch_feature(current.tenant_id)
        return service.list_branches(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
            branch_type=branch_type,
            organization_id=organization_id,
            search=search,
            sort=sort,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/search", response_model=BranchListResponse, summary="Search branches")
def search_branches(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> BranchListResponse:
    require_branch_read(current.role_code)
    service = BranchService(db)
    try:
        service.assert_branch_feature(current.tenant_id)
        return service.list_branches(
            current.tenant_id, page=page, page_size=page_size, search=q
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/export", summary="Export branches")
def export_branches(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    require_branch_export(current.role_code)
    service = BranchService(db)
    try:
        service.assert_branch_feature(current.tenant_id)
        return service.export_rows(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/hierarchy",
    response_model=BranchHierarchyResponse,
    summary="Branch hierarchy tree",
)
def get_branch_hierarchy(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BranchHierarchyResponse:
    require_branch_read(current.role_code)
    service = BranchService(db)
    try:
        service.assert_branch_feature(current.tenant_id)
        return service.hierarchy(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create branch",
)
def create_branch(
    payload: BranchCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BranchResponse:
    require_branch_write(current.role_code)
    try:
        return BranchService(db).create(current.tenant_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{branch_id}", response_model=BranchResponse, summary="Get branch")
def get_branch(
    branch_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BranchResponse:
    require_branch_read(current.role_code)
    service = BranchService(db)
    try:
        service.assert_branch_feature(current.tenant_id)
        return service.get(current.tenant_id, branch_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/{branch_id}", response_model=BranchResponse, summary="Replace branch")
def replace_branch(
    branch_id: UUID,
    payload: BranchReplace,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BranchResponse:
    require_branch_write(current.role_code)
    service = BranchService(db)
    try:
        service.assert_branch_feature(current.tenant_id)
        return service.update(
            current.tenant_id, branch_id, payload, current.user_id, replace=True
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{branch_id}", response_model=BranchResponse, summary="Update branch")
def update_branch(
    branch_id: UUID,
    payload: BranchUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BranchResponse:
    require_branch_write(current.role_code)
    service = BranchService(db)
    try:
        service.assert_branch_feature(current.tenant_id)
        return service.update(
            current.tenant_id, branch_id, payload, current.user_id, replace=False
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete(
    "/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete branch",
)
def delete_branch(
    branch_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    require_branch_write(current.role_code)
    service = BranchService(db)
    try:
        service.assert_branch_feature(current.tenant_id)
        service.soft_delete(current.tenant_id, branch_id, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc
