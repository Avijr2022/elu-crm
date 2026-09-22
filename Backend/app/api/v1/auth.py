from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import AppError, http_error_from_app
from app.db.session import get_db
from app.repositories.pf.user_repository import TenantRepository
from app.schemas.pf.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TenantSummary,
    TokenResponse,
    UserMeResponse,
)
from app.services.pf.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    try:
        return AuthService(db).login(
            email=str(payload.email),
            password=payload.password,
            tenant_code=payload.tenant_code,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest, db: Annotated[Session, Depends(get_db)]
) -> TokenResponse:
    try:
        return AuthService(db).refresh(payload.refresh_token)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


# --- PF-008 CORE authentication endpoints (ELU-BFS-PF-008 §10) -------------------
# POST /auth/mfa/enroll and POST /auth/mfa/verify are deliberately NOT registered
# (MFA out of CORE scope, BR-PF-058 deferred).


@router.post("/register", response_model=TokenResponse)
def register(
    payload: RegisterRequest, db: Annotated[Session, Depends(get_db)]
) -> TokenResponse:
    """Activate an INVITED user with the 72-hour invitation token (AC-PF-008-01)."""
    try:
        return AuthService(db).register(payload.token, payload.password)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/logout", response_model=MessageResponse)
def logout(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    try:
        return AuthService(db).logout(current.user_id, current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    payload: ForgotPasswordRequest, db: Annotated[Session, Depends(get_db)]
) -> MessageResponse:
    """Public, tenant-scoped, non-enumerable (D11)."""
    try:
        return AuthService(db).forgot_password(
            payload.tenant_code, str(payload.email)
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    payload: ResetPasswordRequest, db: Annotated[Session, Depends(get_db)]
) -> MessageResponse:
    try:
        return AuthService(db).reset_password(payload.token, payload.password)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    try:
        return AuthService(db).change_password(
            current.user_id,
            current.tenant_id,
            payload.current_password,
            payload.new_password,
        )
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/me", response_model=UserMeResponse)
def me(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserMeResponse:
    try:
        return AuthService(db).me(current.user_id, current.tenant_id)
    except AppError as exc:
        raise http_error_from_app(exc) from exc


@router.get("/tenant", response_model=TenantSummary)
def current_tenant(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantSummary:
    tenant = TenantRepository(db).get_by_id(current.tenant_id)
    if tenant is None:
        raise http_error_from_app(AppError("NOT_FOUND", "Tenant not found", 404))
    return TenantSummary(
        tenant_id=tenant.tenant_id,
        tenant_code=tenant.tenant_code,
        tenant_name=tenant.tenant_name,
        status=tenant.status,
        edition_code=tenant.edition.code,
        currency_code=tenant.settings.currency_code if tenant.settings else "INR",
        time_zone=tenant.settings.time_zone if tenant.settings else "Asia/Kolkata",
    )
