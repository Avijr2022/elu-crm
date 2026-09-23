"""PF-007 Business Unit Management APIs (ELU-BFS-PF-007 §10).

Exactly the eight approved BFS-PF-007 §10 endpoints are exposed: ``POST /``, ``GET /``,
``GET /search``, ``GET /export``, ``GET /{id}``, ``PUT /{id}``, ``PATCH /{id}`` and
``DELETE /{id}``. There is **no history endpoint** (D1 — the BFS §10 list contains no
history path and PF-007 exposes none), no project/invoice linkage, no reporting endpoint
and no export formatting (D6/D8).

Static segments (``/search``, ``/export``) are declared before ``/{business_unit_id}`` so
they are not shadowed by the path parameter.

Authorization uses the role gates of ``business_unit_service`` only — no second mechanism:
read = TENANT_ADMIN / SALES_MANAGER / FINANCE_USER / PROJECT_MANAGER, write/export =
TENANT_ADMIN (D2/D3). The edition gate implements BR-PF-046: the ``BUSINESS_UNIT``
edition feature is required (Professional + Enterprise; Community is excluded), so a
Community tenant cannot create **or use** business units (403).

All business rules live in the service; the router only maps HTTP to it.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.edition_gating import BUSINESS_UNIT, require_feature
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.schemas.pf.business_unit import (
    BusinessUnitCreate,
    BusinessUnitListResponse,
    BusinessUnitReplace,
    BusinessUnitResponse,
    BusinessUnitUpdate,
)
from app.services.pf.business_unit_service import (
    BusinessUnitService,
    require_business_unit_export,
    require_business_unit_read,
    require_business_unit_write,
)

router = APIRouter(prefix="/org/business-units", tags=["PF-007 Business Units"])


@router.get("", response_model=BusinessUnitListResponse, summary="List business units")
def list_business_units(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    organization_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(
        None, description="name|code|status|created_on; prefix - for desc"
    ),
) -> BusinessUnitListResponse:
    require_feature(db, current.tenant_id, BUSINESS_UNIT)
    require_business_unit_read(current)
    try:
        return BusinessUnitService(db).list_business_units(
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


@router.get(
    "/search", response_model=BusinessUnitListResponse, summary="Search business units"
)
def search_business_units(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> BusinessUnitListResponse:
    require_feature(db, current.tenant_id, BUSINESS_UNIT)
    require_business_unit_read(current)
    try:
        return BusinessUnitService(db).list_business_units(
            current.tenant_id, page=page, page_size=page_size, search=q
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/export", summary="Export business units")
def export_business_units(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    require_feature(db, current.tenant_id, BUSINESS_UNIT)
    require_business_unit_export(current)
    try:
        return BusinessUnitService(db).export_rows(current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "",
    response_model=BusinessUnitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create business unit",
)
def create_business_unit(
    payload: BusinessUnitCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BusinessUnitResponse:
    require_feature(db, current.tenant_id, BUSINESS_UNIT)
    try:
        require_business_unit_write(current)
        return BusinessUnitService(db).create(
            current.tenant_id, payload, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get(
    "/{business_unit_id}",
    response_model=BusinessUnitResponse,
    summary="Get business unit",
)
def get_business_unit(
    business_unit_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BusinessUnitResponse:
    require_feature(db, current.tenant_id, BUSINESS_UNIT)
    require_business_unit_read(current)
    try:
        return BusinessUnitService(db).get(current.tenant_id, business_unit_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put(
    "/{business_unit_id}",
    response_model=BusinessUnitResponse,
    summary="Replace business unit",
)
def replace_business_unit(
    business_unit_id: UUID,
    payload: BusinessUnitReplace,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BusinessUnitResponse:
    require_feature(db, current.tenant_id, BUSINESS_UNIT)
    require_business_unit_write(current)
    try:
        return BusinessUnitService(db).update(
            current.tenant_id, business_unit_id, payload, current.user_id, replace=True
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch(
    "/{business_unit_id}",
    response_model=BusinessUnitResponse,
    summary="Update business unit",
)
def update_business_unit(
    business_unit_id: UUID,
    payload: BusinessUnitUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BusinessUnitResponse:
    require_feature(db, current.tenant_id, BUSINESS_UNIT)
    require_business_unit_write(current)
    try:
        return BusinessUnitService(db).update(
            current.tenant_id, business_unit_id, payload, current.user_id, replace=False
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete(
    "/{business_unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete business unit",
)
def delete_business_unit(
    business_unit_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    require_feature(db, current.tenant_id, BUSINESS_UNIT)
    require_business_unit_write(current)
    try:
        BusinessUnitService(db).soft_delete(
            current.tenant_id, business_unit_id, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc
