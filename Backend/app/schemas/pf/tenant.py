from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class TenantContactIn(BaseModel):
    contact_type: str = Field(default="PRIMARY")
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    mobile: Optional[str] = Field(default=None, max_length=30)
    is_primary: bool = True


class TenantAddressIn(BaseModel):
    address_type: str = Field(default="REGISTERED")
    line1: str = Field(min_length=2, max_length=255)
    line2: Optional[str] = None
    city: str = Field(min_length=2, max_length=100)
    state: Optional[str] = None
    country: str = Field(default="India", max_length=100)
    postal_code: Optional[str] = None


class TenantCreate(BaseModel):
    code: str = Field(min_length=3, max_length=32)
    legal_name: str = Field(min_length=2, max_length=255)
    trade_name: Optional[str] = Field(default=None, max_length=255)
    edition_code: str = Field(min_length=2, max_length=32)
    organization_type: str = Field(default="Pvt Ltd", max_length=50)
    email: EmailStr
    mobile: str = Field(min_length=8, max_length=20)
    industry: Optional[str] = None
    company_size: Optional[str] = None
    primary_contact: TenantContactIn
    registered_address: TenantAddressIn

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        code = v.strip().lower()
        if not re.fullmatch(r"[a-z0-9]{3,32}", code):
            raise ValueError("code must be lowercase alphanumeric, 3–32 chars (BR-PF-009)")
        return code


class TenantUpdate(BaseModel):
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    version_no: int


class TenantSuspendRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)
    version_no: int


class TenantVersionAction(BaseModel):
    version_no: int


class TenantContactOut(BaseModel):
    id: UUID
    contact_type: str
    name: str
    email: EmailStr
    mobile: Optional[str] = None
    is_primary: bool


class TenantAddressOut(BaseModel):
    id: UUID
    address_type: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None


class TenantResponse(BaseModel):
    id: UUID
    code: str
    legal_name: str
    trade_name: Optional[str] = None
    status: str
    edition_code: str
    edition_id: UUID
    email: EmailStr
    mobile: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    version_no: int
    activated_on: Optional[datetime] = None
    suspended_on: Optional[datetime] = None
    contacts: list[TenantContactOut] = []
    addresses: list[TenantAddressOut] = []
    organization_code: Optional[str] = None
    subscription_number: Optional[str] = None
    subscription_status: Optional[str] = None


class TenantListResponse(BaseModel):
    items: list[TenantResponse]
    page: int
    page_size: int
    total: int
