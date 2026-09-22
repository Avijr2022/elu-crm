from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError, ValidationAppError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_opaque_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.db.rls_context import bind_rls_context
from app.models.pf import User
from app.repositories.pf.permission_repository import permissions_for_role
from app.repositories.pf.user_repository import (
    TenantRepository,
    UserInviteRepository,
    UserRepository,
)
from app.schemas.pf.auth import MessageResponse, TokenResponse, UserMeResponse
from app.services.pf.audit_service import write_audit_event
from app.services.pf.user_service import (
    LOCKOUT_MINUTES,
    LOCKOUT_THRESHOLD,
    RESET_TTL_MINUTES,
    utcnow,
)


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.invites = UserInviteRepository(db)
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
        if user is None:
            raise UnauthorizedError("Invalid tenant or credentials", req_id="REQ-PF-051")

        # PF-008 D6/D7 — lazy invitation expiry (BR-PF-054) and lock release (BR-PF-055).
        self._settle_account_state(user)
        if user.account_status == "LOCKED":
            raise ForbiddenError(
                "Account is locked after repeated failed logins; try again later",
                req_id="BR-PF-055",
            )

        if not verify_password(password, user.password_hash):
            self._register_failed_attempt(user, tenant.tenant_id)
            raise UnauthorizedError("Invalid tenant or credentials", req_id="REQ-PF-051")
        self._reset_failed_attempts(user)

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

        # PF-008 D4 / BR-PF-057 — deactivation and password changes revoke refresh tokens.
        issued_at = payload.get("iat")
        if user.sessions_invalid_before is not None and issued_at is not None:
            issued = datetime.fromtimestamp(int(issued_at), tz=timezone.utc)
            if issued < user.sessions_invalid_before:
                raise UnauthorizedError(
                    "Refresh token has been revoked", req_id="BR-PF-057"
                )

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

    # ------------------------------------------------------ PF-008 (ELU-BFS-PF-008)
    def _settle_account_state(self, user: User) -> None:
        """D6/D7 — lazy invitation expiry (BR-PF-054) and lock release (BR-PF-055)."""
        now = utcnow()
        changed = False
        if user.account_status == "INVITED":
            invite = self.invites.get_active_for_user(user.user_id)
            if invite is not None and invite.expires_on <= now:
                invite.status = "EXPIRED"
                user.account_status = "EXPIRED"
                self.db.add(invite)
                changed = True
        elif user.account_status == "LOCKED":
            if user.locked_until is None or user.locked_until <= now:
                user.account_status = "ACTIVE"
                user.failed_login_count = 0
                user.locked_until = None
                changed = True
        if changed:
            self.db.add(user)
            self.db.commit()

    def _register_failed_attempt(self, user: User, tenant_id: UUID) -> None:
        """BR-PF-055 — five consecutive failures lock the account for 30 minutes."""
        user.failed_login_count = (user.failed_login_count or 0) + 1
        if user.failed_login_count >= LOCKOUT_THRESHOLD:
            user.account_status = "LOCKED"
            user.locked_until = utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            write_audit_event(
                self.db,
                event_type="ACCOUNT_LOCKED",
                event_category="USER",
                entity_type="user",
                entity_id=user.user_id,
                actor_email=user.email,
                tenant_id=tenant_id,
                payload={
                    "failed_login_count": user.failed_login_count,
                    "locked_until": user.locked_until,
                    "reason": "BR-PF-055",
                },
            )
        else:
            write_audit_event(
                self.db,
                event_type="LOGIN_FAILURE",
                event_category="USER",
                entity_type="user",
                entity_id=user.user_id,
                actor_email=user.email,
                tenant_id=tenant_id,
                payload={"failed_login_count": user.failed_login_count},
            )
        self.db.add(user)
        self.db.commit()

    @staticmethod
    def _reset_failed_attempts(user: User) -> None:
        """Successful authentication clears the BR-PF-055 counter (committed by caller)."""
        if user.failed_login_count:
            user.failed_login_count = 0
            user.locked_until = None

    def register(self, token: str, password: str) -> TokenResponse:
        """POST /auth/register — activate an invited user (AC-PF-008-01)."""
        bind_rls_context(self.db, platform=True)
        invite = self.invites.get_by_token_hash(hash_token(token))
        if invite is None:
            raise UnauthorizedError("Invalid invitation token", req_id="BR-PF-054")
        user = self.db.get(User, invite.user_id)
        if user is None or user.is_deleted:
            raise UnauthorizedError("Invalid invitation token", req_id="BR-PF-054")

        now = utcnow()
        if invite.status != "ACTIVE":
            # Superseded (CANCELLED) or already-used invitations never touch the account:
            # a newer ACTIVE invitation may exist (re-invite).
            raise UnauthorizedError(
                "Invitation token has expired or was already used", req_id="BR-PF-054"
            )
        if invite.expires_on <= now:
            invite.status = "EXPIRED"
            if user.account_status == "INVITED":
                user.account_status = "EXPIRED"
            self.db.add_all([invite, user])
            self.db.commit()
            raise UnauthorizedError(
                "Invitation token has expired or was already used", req_id="BR-PF-054"
            )
        if user.account_status != "INVITED":
            raise ForbiddenError(
                "Account is not awaiting activation", req_id="REQ-PF-008"
            )

        user.password_hash = hash_password(password)
        user.account_status = "ACTIVE"
        user.activated_at = now
        user.password_changed_at = now
        user.failed_login_count = 0
        user.locked_until = None
        user.version_no += 1
        invite.status = "USED"
        invite.used_on = now
        self.db.add_all([user, invite])
        write_audit_event(
            self.db,
            event_type="USER_ACTIVATED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=user.user_id,
            actor_email=user.email,
            tenant_id=user.tenant_id,
            payload={"account_status": "ACTIVE", "activated_at": now},
        )
        self.db.commit()

        return TokenResponse(
            access_token=create_access_token(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                email=user.email,
                role_code=user.role.role_code,
            ),
            refresh_token=create_refresh_token(user.user_id, user.tenant_id),
            expires_in_minutes=self.settings.access_token_expire_minutes,
        )

    def forgot_password(self, tenant_code: str, email: str) -> MessageResponse:
        """POST /auth/forgot-password — public, tenant-scoped, non-enumerable (D11)."""
        bind_rls_context(self.db, platform=True)
        generic = MessageResponse(
            message="If the account exists, a password reset challenge has been issued"
        )
        tenant = self.tenants.get_by_code(tenant_code)
        if tenant is None:
            return generic
        user = self.users.get_by_email(email=email.lower(), tenant_id=tenant.tenant_id)
        if user is None or user.account_status != "ACTIVE":
            return generic
        user.reset_token_hash = hash_token(generate_opaque_token())
        user.reset_token_expires_at = utcnow() + timedelta(minutes=RESET_TTL_MINUTES)
        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_PASSWORD_RESET_REQUESTED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_email=user.email,
            tenant_id=tenant.tenant_id,
            payload={"delivery": "NTF-PF-008-03 deferred"},
        )
        self.db.commit()
        return generic

    def reset_password(self, token: str, password: str) -> MessageResponse:
        """POST /auth/reset-password — consume a single-use reset challenge."""
        bind_rls_context(self.db, platform=True)
        user = self.db.scalars(
            select(User).where(
                User.reset_token_hash == hash_token(token),
                User.is_deleted.is_(False),
            )
        ).first()
        if user is None or user.reset_token_expires_at is None:
            raise ValidationAppError(
                "Invalid or expired reset token", req_id="REQ-PF-008"
            )
        if user.reset_token_expires_at <= utcnow():
            user.reset_token_hash = None
            user.reset_token_expires_at = None
            self.db.add(user)
            self.db.commit()
            raise ValidationAppError(
                "Invalid or expired reset token", req_id="REQ-PF-008"
            )

        now = utcnow()
        user.password_hash = hash_password(password)
        user.password_changed_at = now
        user.sessions_invalid_before = now  # BR-PF-057
        user.reset_token_hash = None
        user.reset_token_expires_at = None
        user.failed_login_count = 0
        user.locked_until = None
        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_PASSWORD_RESET",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_email=user.email,
            tenant_id=user.tenant_id,
            payload={"account_status": user.account_status},
        )
        self.db.commit()
        return MessageResponse(message="Password has been reset; sign in with the new password")

    def change_password(
        self,
        user_id: UUID,
        tenant_id: UUID,
        current_password: str,
        new_password: str,
    ) -> MessageResponse:
        """POST /auth/change-password — authenticated self-service change."""
        bind_rls_context(self.db, tenant_id=tenant_id, platform=False)
        user = self.users.get_by_id(user_id, tenant_id)
        if user is None:
            raise UnauthorizedError("User not found", req_id="REQ-PF-051")
        if not verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect", req_id="REQ-PF-051")

        now = utcnow()
        user.password_hash = hash_password(new_password)
        user.password_changed_at = now
        user.sessions_invalid_before = now  # BR-PF-057
        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_PASSWORD_CHANGED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=user_id,
            actor_email=user.email,
            tenant_id=tenant_id,
            payload={"self_service": True},
        )
        self.db.commit()
        return MessageResponse(message="Password changed")

    def logout(self, user_id: UUID, tenant_id: UUID) -> MessageResponse:
        """POST /auth/logout — revoke outstanding refresh tokens (D4)."""
        bind_rls_context(self.db, tenant_id=tenant_id, platform=False)
        user = self.users.get_by_id(user_id, tenant_id)
        if user is None:
            raise UnauthorizedError("User not found", req_id="REQ-PF-051")
        user.sessions_invalid_before = utcnow()
        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_LOGOUT",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=user_id,
            actor_email=user.email,
            tenant_id=tenant_id,
            payload={},
        )
        self.db.commit()
        return MessageResponse(message="Signed out")
