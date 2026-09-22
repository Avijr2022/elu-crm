"""PF-008 User & Identity Management schemas (ELU-BFS-PF-008 §9/§10).

Conventions follow ``app/schemas/pf/department.py`` (PF-006): distinct PUT / PATCH models,
``version_no`` optimistic locking on mutations, ``field_validator`` normalisation.

Scope notes (Documentation/PF008_CORE_IMPLEMENTATION_MAP.md):
  * ``account_status`` is limited to the six approved lifecycle values of `ELU-BFS-PF-008` §5
    (``INVITED``, ``ACTIVE``, ``INACTIVE``, ``LOCKED``, ``EXPIRED``, ``CANCELLED``). No status is
    ever accepted as "arbitrary": transitions are validated in the service.
  * ``tenant_id`` is **never** accepted on input — it always comes from the authenticated
    context (`BR-PF-059` / ADR-015).
  * Passwords: minimum length 8 mirrors the existing login contract. The configurable
    ``tenant_security`` policy of `BR-PF-053` has no source (no such table exists) and is
    therefore **not** implemented (D10).
  * MFA fields (`ELU-BFS-PF-008` §9 ``user_mfa``) are deliberately absent — MFA is out of
    CORE scope (`BR-PF-058` deferred).
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# ELU-BFS-PF-008 §5 business states.
USER_STATUSES = (
    "INVITED",
    "ACTIVE",
    "INACTIVE",
    "LOCKED",
    "EXPIRED",
    "CANCELLED",
)

# D10 — no tenant_security policy source exists; mirror the existing login contract.
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

_ROLE_CODE_RE = re.compile(r"[A-Z0-9_]{2,30}")
_EMPLOYEE_CODE_RE = re.compile(r"[A-Za-z0-9_-]{1,30}")


def normalize_status(value: str, field: str = "account_status") -> str:
    normalized = value.strip().upper()
    if normalized not in USER_STATUSES:
        raise ValueError(f"{field} must be one of {', '.join(USER_STATUSES)}")
    return normalized


class UserInviteCreate(BaseModel):
    """POST /users — invite *or* create a user (ELU-BFS-PF-008 §10 "Invite/create user").

    When ``password`` is supplied the account is created ``ACTIVE`` (admin-created account);
    otherwise the account is created ``INVITED`` together with a 72-hour invitation
    (`BR-PF-054`) and the invitation token is returned once.
    """

    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=150)
    employee_code: Optional[str] = Field(default=None, max_length=30)
    mobile: Optional[str] = Field(default=None, max_length=20)
    designation: Optional[str] = Field(default=None, max_length=100)
    role_code: Optional[str] = Field(default=None, max_length=30)
    role_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    business_unit_id: Optional[UUID] = None
    password: Optional[str] = Field(
        default=None, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )

    @field_validator("first_name", "last_name", "display_name", "designation")
    @classmethod
    def _strip_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped

    @field_validator("role_code")
    @classmethod
    def _validate_role_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        code = v.strip().upper()
        if not _ROLE_CODE_RE.fullmatch(code):
            raise ValueError("role_code must be 2-30 chars A-Z0-9_")
        return code

    @field_validator("employee_code")
    @classmethod
    def _validate_employee_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        code = v.strip()
        if not _EMPLOYEE_CODE_RE.fullmatch(code):
            raise ValueError("employee_code must be 1-30 chars A-Za-z0-9_-")
        return code


class UserUpdate(BaseModel):
    """PUT /users/{id} — full update (`user.update`).

    ``email`` is updatable subject to the per-tenant uniqueness of `BR-PF-051`;
    ``account_status`` is **not** accepted here (lifecycle changes go through PATCH, so the
    state machine and the "last active Tenant Admin" guard of `BR-PF-060` stay in one place).
    """

    first_name: str = Field(min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=150)
    email: Optional[EmailStr] = None
    employee_code: Optional[str] = Field(default=None, max_length=30)
    mobile: Optional[str] = Field(default=None, max_length=20)
    designation: Optional[str] = Field(default=None, max_length=100)
    role_code: Optional[str] = Field(default=None, max_length=30)
    role_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    business_unit_id: Optional[UUID] = None
    version_no: int = Field(ge=1)

    @field_validator("first_name")
    @classmethod
    def _validate_first_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("first_name must not be blank")
        return stripped

    @field_validator("role_code")
    @classmethod
    def _validate_role_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        code = v.strip().upper()
        if not _ROLE_CODE_RE.fullmatch(code):
            raise ValueError("role_code must be 2-30 chars A-Z0-9_")
        return code


class UserPatch(BaseModel):
    """PATCH /users/{id} — partial update incl. status transitions (`user.update`)."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=150)
    employee_code: Optional[str] = Field(default=None, max_length=30)
    mobile: Optional[str] = Field(default=None, max_length=20)
    designation: Optional[str] = Field(default=None, max_length=100)
    role_code: Optional[str] = Field(default=None, max_length=30)
    role_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    business_unit_id: Optional[UUID] = None
    account_status: Optional[str] = None
    version_no: int = Field(ge=1)

    @field_validator("first_name")
    @classmethod
    def _validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("first_name must not be blank")
        return stripped

    @field_validator("role_code")
    @classmethod
    def _validate_role_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        code = v.strip().upper()
        if not _ROLE_CODE_RE.fullmatch(code):
            raise ValueError("role_code must be 2-30 chars A-Z0-9_")
        return code

    @field_validator("account_status")
    @classmethod
    def _validate_status(cls, v: Optional[str]) -> Optional[str]:
        return normalize_status(v) if v is not None else v


class UserSelfUpdate(BaseModel):
    """PUT /users/me — update own profile (no role / organization / status change)."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=150)
    mobile: Optional[str] = Field(default=None, max_length=20)
    designation: Optional[str] = Field(default=None, max_length=100)

    @field_validator("first_name")
    @classmethod
    def _validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("first_name must not be blank")
        return stripped


class UserResponse(BaseModel):
    """User profile projection (no credential material is ever exposed)."""

    user_id: UUID
    tenant_id: UUID
    employee_code: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    display_name: str
    email: EmailStr
    mobile: Optional[str] = None
    designation: Optional[str] = None
    account_status: str

    organization_id: UUID
    organization_name: Optional[str] = None
    role_id: UUID
    role_code: Optional[str] = None
    role_name: Optional[str] = None

    branch_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    business_unit_id: Optional[UUID] = None

    invited_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    created_on: Optional[datetime] = None
    modified_on: Optional[datetime] = None
    version_no: int

    model_config = {"from_attributes": True}


class UserCreateResponse(UserResponse):
    """POST /users result; ``invite_token`` is returned **once** and never stored in clear."""

    invite_token: Optional[str] = None
    invite_expires_on: Optional[datetime] = None


class UserListResponse(BaseModel):
    items: list[UserResponse] = Field(default_factory=list)
    page: int
    page_size: int
    total: int
