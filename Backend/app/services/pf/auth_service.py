from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.db.rls_context import bind_rls_context
from app.repositories.pf.permission_repository import permissions_for_role
from app.repositories.pf.user_repository import TenantRepository, UserRepository
from app.schemas.pf.auth import TokenResponse, UserMeResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.tenants = TenantRepository(db)
        self.settings = get_settings()

    def login(
        self, email: str, password: str, tenant_code: str
    ) -> TokenResponse:
        # Auth bootstrap: resolve tenant/user before JWT exists (ADR-015).
        bind_rls_context(self.db, platform=True)
        tenant = self.tenants.get_by_code(tenant_code)
        if tenant is None:
            raise UnauthorizedError("Invalid tenant or credentials", req_id="REQ-PF-051")

        user = self.users.get_by_email(
            email=email.lower(),
            tenant_id=tenant.tenant_id,
        )
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid tenant or credentials", req_id="REQ-PF-051")

        if user.account_status != "ACTIVE" or not user.is_active:
            raise ForbiddenError("User account is not active", req_id="REQ-PF-051")

        if user.tenant.status not in {"ACTIVE", "TRIAL"}:
            if user.tenant.status == "SUSPENDED":
                raise ForbiddenError(
                    "Tenant is suspended; login is blocked",
                    req_id="BR-PF-014",
                )
            raise ForbiddenError("Tenant is not active", req_id="REQ-PF-006")

        user.last_login = datetime.now(timezone.utc)
        self.db.add(user)
        self.db.commit()

        access = create_access_token(
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            email=user.email,
            role_code=user.role.role_code,
        )
        refresh = create_refresh_token(user.user_id, user.tenant_id)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in_minutes=self.settings.access_token_expire_minutes,
        )

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except ValueError as exc:
            raise UnauthorizedError(str(exc), req_id="REQ-PF-051") from exc

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token", req_id="REQ-PF-051")

        user_id = UUID(payload["sub"])
        tenant_id = UUID(payload["tenant_id"])
        bind_rls_context(self.db, tenant_id=tenant_id, platform=False)
        user = self.users.get_by_id(user_id, tenant_id)
        if user is None or user.account_status != "ACTIVE":
            raise UnauthorizedError("User not found or inactive", req_id="REQ-PF-051")

        if user.tenant.status not in {"ACTIVE", "TRIAL"}:
            if user.tenant.status == "SUSPENDED":
                raise ForbiddenError(
                    "Tenant is suspended; login is blocked",
                    req_id="BR-PF-014",
                )
            raise ForbiddenError("Tenant is not active", req_id="REQ-PF-006")

        access = create_access_token(
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            email=user.email,
            role_code=user.role.role_code,
        )
        new_refresh = create_refresh_token(user.user_id, user.tenant_id)
        return TokenResponse(
            access_token=access,
            refresh_token=new_refresh,
            expires_in_minutes=self.settings.access_token_expire_minutes,
        )

    def me(self, user_id: UUID, tenant_id: UUID) -> UserMeResponse:
        bind_rls_context(self.db, tenant_id=tenant_id, platform=False)
        user = self.users.get_by_id(user_id, tenant_id)
        if user is None:
            raise UnauthorizedError("User not found", req_id="REQ-PF-051")

        settings = user.tenant.settings
        perms = sorted(permissions_for_role(self.db, user.role_id))
        return UserMeResponse(
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            tenant_code=user.tenant.tenant_code,
            tenant_name=user.tenant.tenant_name,
            email=user.email,
            display_name=user.display_name,
            role_code=user.role.role_code,
            role_name=user.role.role_name,
            permissions=perms,
            organization_name=user.organization.organization_name,
            currency_code=settings.currency_code if settings else "INR",
            time_zone=settings.time_zone if settings else "Asia/Kolkata",
            financial_year_start=(
                settings.financial_year_start.isoformat() if settings else "2026-04-01"
            ),
        )
