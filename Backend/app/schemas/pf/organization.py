"""PF-004 Organization Management schemas (ELU-BFS-PF-004)."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
import re

from pydantic import BaseModel, EmailStr, Field, field_validator


_GSTIN_RE = re.compile(
    r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
)
_PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")


class OrganizationCreate(BaseModel):
    code: str = Field(min_length=2, max_length=30)
    name: str = Field(min_length=2, max_length=200)
    legal_name: Optional[str] = Field(default=None, max_length=255)
    short_name: Optional[str] = Field(default=None, max_length=100)
    organization_type: str = Field(default="Branch", max_length=50)
    parent_organization_id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=255)
    gstin: Optional[str] = Field(default=None, max_length=20)
    pan: Optional[str] = Field(default=None, max_length=20)
    tan: Optional[str] = Field(default=None, max_length=20)
    cin: Optional[str] = Field(default=None, max_length=30)
    registration_number: Optional[str] = Field(default=None, max_length=100)
    tax_registration_type: Optional[str] = Field(default=None, max_length=50)
    date_of_incorporation: Optional[date] = None
    default_currency_code: str = Field(default="INR", min_length=3, max_length=3)
    fiscal_year_start_month: int = Field(default=4, ge=1, le=12)
    address_id: Optional[UUID] = None
    status: str = Field(default="ACTIVE")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        code = v.strip().upper()
        if not re.fullmatch(r"[A-Z0-9_-]{2,30}", code):
            raise ValueError("code must be 2–30 chars A-Z0-9_-")
        return code

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        g = v.strip().upper()
        if not _GSTIN_RE.fullmatch(g):
            raise ValueError("Invalid GSTIN format (BR-PF-030)")
        return g

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        p = v.strip().upper()
        if not _PAN_RE.fullmatch(p):
            raise ValueError("Invalid PAN format")
        return p


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    legal_name: Optional[str] = Field(default=None, max_length=255)
    short_name: Optional[str] = Field(default=None, max_length=100)
    organization_type: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=255)
    gstin: Optional[str] = Field(default=None, max_length=20)
    pan: Optional[str] = Field(default=None, max_length=20)
    tan: Optional[str] = Field(default=None, max_length=20)
    cin: Optional[str] = Field(default=None, max_length=30)
    registration_number: Optional[str] = Field(default=None, max_length=100)
    tax_registration_type: Optional[str] = Field(default=None, max_length=50)
    date_of_incorporation: Optional[date] = None
    default_currency_code: Optional[str] = Field(default=None, min_length=3, max_length=3)
    fiscal_year_start_month: Optional[int] = Field(default=None, ge=1, le=12)
    address_id: Optional[UUID] = None
    status: Optional[str] = None
    version_no: int

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        g = v.strip().upper()
        if not _GSTIN_RE.fullmatch(g):
            raise ValueError("Invalid GSTIN format (BR-PF-030)")
        return g

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        p = v.strip().upper()
        if not _PAN_RE.fullmatch(p):
            raise ValueError("Invalid PAN format")
        return p


class OrganizationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    legal_name: Optional[str] = None
    short_name: Optional[str] = None
    organization_type: str
    parent_organization_id: Optional[UUID] = None
    is_root: bool
    level: int
    gstin: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    cin: Optional[str] = None
    registration_number: Optional[str] = None
    tax_registration_type: Optional[str] = None
    date_of_incorporation: Optional[date] = None
    default_currency_code: str
    fiscal_year_start_month: int
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_id: Optional[UUID] = None
    status: str
    version_no: int
    created_on: datetime
    modified_on: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrganizationHistoryItem(BaseModel):
    id: UUID
    event_type: str
    event_category: str
    actor_email: Optional[str] = None
    payload_json: Optional[str] = None
    created_on: datetime


class OrganizationHistoryResponse(BaseModel):
    items: list[OrganizationHistoryItem]
    total: int


class OrganizationListResponse(BaseModel):
    items: list[OrganizationResponse]
    page: int
    page_size: int
    total: int


class OrganizationHierarchyNode(BaseModel):
    id: UUID
    code: str
    name: str
    is_root: bool
    level: int
    status: str
    children: list["OrganizationHierarchyNode"] = []
