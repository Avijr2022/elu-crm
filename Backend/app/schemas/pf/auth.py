from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    tenant_code: str = Field(
        min_length=1,
        description="Required tenant code; login is always tenant-scoped.",
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class RefreshRequest(BaseModel):
    refresh_token: str


class UserMeResponse(BaseModel):
    user_id: UUID
    tenant_id: UUID
    tenant_code: str
    tenant_name: str
    email: EmailStr
    display_name: str
    role_code: str
    role_name: str
    permissions: list[str] = Field(default_factory=list)
    organization_name: str
    currency_code: str
    time_zone: str
    financial_year_start: datetime | str

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str


class TenantSummary(BaseModel):
    tenant_id: UUID
    tenant_code: str
    tenant_name: str
    status: str
    edition_code: str
    currency_code: str
    time_zone: str


# --- PF-008 CORE authentication contracts (ELU-BFS-PF-008 §10) -------------------
# Passwords: minimum length 8 mirrors the existing login contract — the configurable
# tenant_security policy of BR-PF-053 has no source and is not implemented (D10).
# MFA endpoints (BR-PF-058) are out of CORE scope and are not declared here.


class RegisterRequest(BaseModel):
    """POST /auth/register — activate an INVITED user with the 72-hour invitation token."""

    token: str = Field(min_length=16)
    password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    """POST /auth/forgot-password — public, tenant-scoped, non-enumerable."""

    tenant_code: str = Field(min_length=1)
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """POST /auth/reset-password — public, consumes a single-use reset token."""

    token: str = Field(min_length=16)
    password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    """POST /auth/change-password — authenticated self-service change."""

    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str


class PasswordActionResponse(BaseModel):
    """Result of an issued password challenge.

    ``reset_token`` is populated **only** for the permission-gated
    ``POST /users/{id}/reset-password`` path (`user.reset_password`), because the
    ``NTF-PF-008-03`` e-mail delivery is deferred (D11). The public
    ``POST /auth/forgot-password`` path never returns a token.
    """

    message: str
    user_id: UUID
    reset_token: str | None = None
    expires_in_minutes: int | None = None
