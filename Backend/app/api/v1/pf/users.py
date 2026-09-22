"""PF-008 User & Identity Management APIs (ELU-BFS-PF-008 §10).

The twelve approved BFS-PF-008 §10 user endpoints are exposed: ``POST /``, ``GET /``,
``GET /search``, ``GET /export``, ``GET /me``, ``PUT /me``, ``GET /{id}``, ``PUT /{id}``,
``PATCH /{id}``, ``DELETE /{id}``, ``POST /{id}/reinvite`` and ``POST /{id}/reset-password``.

The remaining BFS-PF-008 §10 operations live on the existing ``/auth`` router
(``register``, ``logout``, ``forgot-password``, ``reset-password``, ``change-password``);
``POST /auth/mfa/enroll`` and ``POST /auth/mfa/verify`` are **not** registered — MFA is out
of CORE scope (``BR-PF-058`` deferred).

Static segments (``/search``, ``/export``, ``/me``) are declared before ``/{user_id}`` so they
are not shadowed by the path parameter.

Authorization uses the role gates of ``user_service`` only (BFS-PF-008 §12 actor matrix) — no
second mechanism. All business rules live in the service; the router only maps HTTP to it.
``tenant_id`` is always taken from the authenticated context, never from the request body
(``BR-PF-059``).
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.schemas.pf.auth import PasswordActionResponse
from app.schemas.pf.user import (
    UserCreateResponse,
    UserInviteCreate,
    UserListResponse,
    UserPatch,
    UserResponse,
    UserSelfUpdate,
    UserUpdate,
)
from app.services.pf.user_service import (
    UserService,
    require_user_export,
    require_user_read,
    require_user_write,
)

router = APIRouter(prefix="/users", tags=["PF-008 Users"])


@router.get("", response_model=UserListResponse, summary="List users")
def list_users(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    role_id: Optional[UUID] = Query(None),
    organization_id: Optional[UUID] = Query(None),
    branch_id: Optional[UUID] = Query(None),
    department_id: Optional[UUID] = Query(None),
    business_unit_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(
        None, description="name|display_name|email|status|employee_code|last_login|created_on"
    ),
) -> UserListResponse:
    require_user_read(current.role_code)
    try:
        return UserService(db).list_users(
            current.tenant_id,
            page=page,
            page_size=page_size,
            status=status_filter,
            role_id=role_id,
            organization_id=organization_id,
            branch_id=branch_id,
            department_id=department_id,
            business_unit_id=business_unit_id,
            search=search,
            sort=sort,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/search", response_model=UserListResponse, summary="Search users")
def search_users(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    require_user_read(current.role_code)
    try:
        return UserService(db).list_users(
            current.tenant_id, page=page, page_size=page_size, search=q
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/export", summary="Export users")
def export_users(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: Optional[str] = Query(None, alias="status"),
    role_id: Optional[UUID] = Query(None),
    branch_id: Optional[UUID] = Query(None),
    department_id: Optional[UUID] = Query(None),
    business_unit_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
) -> list[dict]:
    require_user_export(current.role_code)
    try:
        return UserService(db).export_rows(
            current.tenant_id,
            status=status_filter,
            role_id=role_id,
            branch_id=branch_id,
            department_id=department_id,
            business_unit_id=business_unit_id,
            search=search,
            sort=sort,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/me", response_model=UserResponse, summary="Current user profile")
def get_me(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    try:
        return UserService(db).self_profile(current.tenant_id, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/me", response_model=UserResponse, summary="Update own profile")
def update_me(
    payload: UserSelfUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    try:
        return UserService(db).self_update(current.tenant_id, current.user_id, payload)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite or create user",
)
def create_user(
    payload: UserInviteCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserCreateResponse:
    require_user_write(current.role_code)
    try:
        return UserService(db).invite_or_create(
            current.tenant_id, payload, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/{user_id}", response_model=UserResponse, summary="Get user detail")
def get_user(
    user_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    require_user_read(current.role_code)
    try:
        return UserService(db).get_user(current.tenant_id, user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.put("/{user_id}", response_model=UserResponse, summary="Full user update")
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    require_user_write(current.role_code)
    try:
        return UserService(db).update_user(
            current.tenant_id, user_id, payload, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.patch("/{user_id}", response_model=UserResponse, summary="Partial user update")
def patch_user(
    user_id: UUID,
    payload: UserPatch,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    require_user_write(current.role_code)
    try:
        return UserService(db).patch_user(
            current.tenant_id, user_id, payload, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.delete("/{user_id}", response_model=UserResponse, summary="Deactivate user")
def deactivate_user(
    user_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    require_user_write(current.role_code)
    try:
        return UserService(db).deactivate(current.tenant_id, user_id, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/{user_id}/reinvite",
    response_model=UserCreateResponse,
    summary="Resend invitation",
)
def reinvite_user(
    user_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserCreateResponse:
    require_user_write(current.role_code)
    try:
        return UserService(db).reinvite(current.tenant_id, user_id, current.user_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post(
    "/{user_id}/reset-password",
    response_model=PasswordActionResponse,
    summary="Admin password reset",
)
def admin_reset_password(
    user_id: UUID,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PasswordActionResponse:
    require_user_write(current.role_code)
    try:
        return UserService(db).admin_reset_password(
            current.tenant_id, user_id, current.user_id
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc
