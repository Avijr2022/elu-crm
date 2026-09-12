"""PF-005 Branch Management schemas (ELU-BFS-PF-005 §9/§10).

Conventions follow ``app/schemas/pf/organization.py`` (PF-004). PUT and PATCH use
distinct models: ``BranchReplace`` (PUT — ``name`` required) and ``BranchUpdate``
(PATCH — all optional); both carry ``version_no`` for optimistic locking.

Scope note: ``branch_head_user_id`` is exposed read-only and is never accepted on
input — branch-head assignment/validation (BR-PF-038 / AC-PF-005-04) is deferred
to PF-008. Department (PF-006) and project→branch (BR-PF-037) linkages are also
out of scope for this module.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

BRANCH_TYPES = ("HEAD_OFFICE", "BRANCH", "REGIONAL_OFFICE")
BRANCH_STATUSES = ("DRAFT", "ACTIVE", "INACTIVE", "ARCHIVED", "CANCELLED")

_CODE_RE = re.compile(r"[A-Z0-9_-]{2,30}")


def _normalize_choice(value: str, allowed: tuple[str, ...], field: str) -> str:
    normalized = value.strip().upper()
    if normalized not in allowed:
        raise ValueError(f"{field} must be one of {', '.join(allowed)}")
    return normalized


class BranchAddressIn(BaseModel):
    """Nested branch address payload (BFS-PF-005 §9 branch_address)."""

    address_line_1: str = Field(min_length=1, max_length=255)
    address_line_2: Optional[str] = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country_code: str = Field(default="IN", min_length=2, max_length=3)
    latitude: Optional[Decimal] = Field(default=None, ge=Decimal("-90"), le=Decimal("90"))
    longitude: Optional[Decimal] = Field(default=None, ge=Decimal("-180"), le=Decimal("180"))

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        return v.strip().upper()


class BranchCreate(BaseModel):
    code: str = Field(min_length=2, max_length=30)
    name: str = Field(min_length=2, max_length=200)
    branch_type: str = Field(default="BRANCH")
    organization_id: UUID
    parent_branch_id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    timezone_id: Optional[str] = Field(default=None, max_length=64)
    working_hours: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="DRAFT")
    opened_date: Optional[date] = None
    closed_date: Optional[date] = None
    address: Optional[BranchAddressIn] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        code = v.strip().upper()
        if not _CODE_RE.fullmatch(code):
            raise ValueError("code must be 2–30 chars A-Z0-9_-")
        return code

    @field_validator("branch_type")
    @classmethod
    def validate_branch_type(cls, v: str) -> str:
        return _normalize_choice(v, BRANCH_TYPES, "branch_type")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        return _normalize_choice(v, BRANCH_STATUSES, "status")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[EmailStr]) -> Optional[str]:
        return str(v).lower() if v else None


class BranchUpdate(BaseModel):
    """PATCH payload — partial update (BFS-PF-005 §10)."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    branch_type: Optional[str] = None
    organization_id: Optional[UUID] = None
    parent_branch_id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    timezone_id: Optional[str] = Field(default=None, max_length=64)
    working_hours: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = None
    opened_date: Optional[date] = None
    closed_date: Optional[date] = None
    address: Optional[BranchAddressIn] = None
    version_no: int

    @field_validator("branch_type")
    @classmethod
    def validate_branch_type(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_choice(v, BRANCH_TYPES, "branch_type") if v else v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_choice(v, BRANCH_STATUSES, "status") if v else v

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[EmailStr]) -> Optional[str]:
        return str(v).lower() if v else None


class BranchReplace(BranchUpdate):
    """PUT payload — full replace (BFS-PF-005 §10 "Full update").

    Mirrors PF-004's PUT rule: ``name`` is mandatory; ``code`` is immutable.
    """

    name: str = Field(min_length=2, max_length=200)


class BranchAddressResponse(BaseModel):
    id: UUID
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    model_config = {"from_attributes": True}


class BranchResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    branch_type: str
    organization_id: UUID
    parent_branch_id: Optional[UUID] = None
    branch_head_user_id: Optional[UUID] = None  # read-only; assignment deferred to PF-008
    email: Optional[str] = None
    phone: Optional[str] = None
    timezone_id: Optional[str] = None
    working_hours: Optional[str] = None
    status: str
    opened_date: Optional[date] = None
    closed_date: Optional[date] = None
    address: Optional[BranchAddressResponse] = None
    warnings: list[str] = []
    version_no: int
    created_on: datetime
    modified_on: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BranchHistoryItem(BaseModel):
    id: UUID
    event_type: str
    event_category: str
    actor_email: Optional[str] = None
    payload_json: Optional[str] = None
    created_on: datetime


class BranchHistoryResponse(BaseModel):
    items: list[BranchHistoryItem]
    total: int


class BranchListResponse(BaseModel):
    items: list[BranchResponse]
    page: int
    page_size: int
    total: int
    warnings: list[str] = []


class BranchHierarchyNode(BaseModel):
    id: UUID
    code: str
    name: str
    branch_type: str
    organization_id: UUID
    parent_branch_id: Optional[UUID] = None
    status: str
    children: list["BranchHierarchyNode"] = []


class BranchHierarchyResponse(BaseModel):
    """Tenant-wide branch tree (BFS-PF-005 §10 ``GET /org/branches/hierarchy``).

    A forest is returned because branches without a parent are valid roots
    (a tenant is not required to have a single top branch).
    """

    items: list[BranchHierarchyNode] = []
    warnings: list[str] = []
