"""PF-006 Department Management APIs (ELU-BFS-PF-006 §10).

The ten approved BFS-PF-006 §10 endpoints are exposed: ``POST /``, ``GET /``,
``GET /search``, ``GET /export``, ``GET /hierarchy``, ``GET /{id}``, ``PUT /{id}``,
``PATCH /{id}``, ``DELETE /{id}`` and ``PATCH /{id}/move``.

``GET /{id}/history`` is additionally exposed: BFS-PF-006 §15 defines the audit events and
§11 the Department History screen, and the established PF-004 convention provides a typed
history endpoint for a hierarchy resource (PF-005 chose service-only because its own §10
omits the path). No other path is registered.

Static segments (``/search``, ``/export``, ``/hierarchy``) and the ``/{id}/...`` sub-routes
are declared before ``/{department_id}`` so they are not shadowed by the path parameter.

Authorization uses the role gates of ``department_service`` only — no second mechanism:
read = TENANT_ADMIN / SALES_MANAGER / PROJECT_MANAGER, write/export = TENANT_ADMIN. There
is no PF-006 edition gate (ELU-EDM-001: multi-department is available in every edition).
All business rules live in the service; the router only maps HTTP to it.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.schemas.pf.department import (
    DepartmentCreate,
    DepartmentHierarchyResponse,
    DepartmentHistoryResponse,
    DepartmentListResponse,
    DepartmentMove,
    DepartmentReplace,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.pf.department_service import (
    DepartmentService,
    require_department_export,
    require_department_read,
    require_department_write,
)

router = APIRouter(prefix="/org/departments", tags=["PF-006 Departments"])


@router.get("", response_model=DepartmentListResponse, summary="List departments")
def list_departments(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    organization_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(
        None, description="name|code|status|type|created_on; prefix - for desc"
    ),
) -> DepartmentListResponse:
    require_department_read(current)
    try:
        return DepartmentService(db).list_departments(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
            organization_id=organization_id,
            search=search,
            sort=sort,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/search", response_model=DepartmentListResponse, summary="Search departments")
def search_departments(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> DepartmentListResponse:
    require_department_read(current)
    try:
        return DepartmentService(db).list_departments(
            current.tenant_id, page=page, page_size=page_size, search=q
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/export", summary="Export departments")
def export_departments(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    require_department_export(current)
    try:
        return DepartmentService(db).export_rows(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/hierarchy",
    response_model=DepartmentHierarchyResponse,
    summary="Department hierarchy tree",
)
def get_department_hierarchy(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DepartmentHierarchyResponse:
    require_department_read(current)
    try:
        return DepartmentService(db).hierarchy(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create department",
)
def create_department(
    payload: DepartmentCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DepartmentResponse:
    try:
        require_department_write(current)
        return DepartmentService(db).create(current.tenant_id, payload, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/{department_id}/history",
    response_model=DepartmentHistoryResponse,
    summary="Department audit history",
)
def get_department_history(
    department_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
) -> DepartmentHistoryResponse:
    require_department_read(current)
    try:
        return DepartmentService(db).history(
            current.tenant_id, department_id, limit=limit
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch(
    "/{department_id}/move",
    response_model=DepartmentResponse,
    summary="Reparent department",
)
def move_department(
    department_id: UUID,
    payload: DepartmentMove,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DepartmentResponse:
    require_department_write(current)
    try:
        return DepartmentService(db).move(
            current.tenant_id,
            department_id,
            payload.parent_department_id,
            payload.version_no,
            current.user_id,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/{department_id}", response_model=DepartmentResponse, summary="Get department"
)
def get_department(
    department_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DepartmentResponse:
    require_department_read(current)
    try:
        return DepartmentService(db).get(current.tenant_id, department_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put(
    "/{department_id}", response_model=DepartmentResponse, summary="Replace department"
)
def replace_department(
    department_id: UUID,
    payload: DepartmentReplace,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DepartmentResponse:
    require_department_write(current)
    try:
        return DepartmentService(db).update(
            current.tenant_id, department_id, payload, current.user_id, replace=True
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch(
    "/{department_id}", response_model=DepartmentResponse, summary="Update department"
)
def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DepartmentResponse:
    require_department_write(current)
    try:
        return DepartmentService(db).update(
            current.tenant_id, department_id, payload, current.user_id, replace=False
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete department",
)
def delete_department(
    department_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    require_department_write(current)
    try:
        DepartmentService(db).soft_delete(
            current.tenant_id, department_id, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc
