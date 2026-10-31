from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


CUSTOMER_TYPES = ("ACCOUNT", "PERSON")
CUSTOMER_STATUSES = (
    "PROSPECT",
    "ACTIVE",
    "INACTIVE",
    "ON_HOLD",
    "SUSPENDED",
    "CANCELLED",
)
ADDRESS_TYPES = ("REGISTERED", "BILLING", "SHIPPING", "OTHER")


class CustomerContactCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    job_title: Optional[str] = Field(default=None, max_length=120)
    email: Optional[str] = Field(default=None, max_length=150)
    phone_mobile: Optional[str] = Field(default=None, max_length=30)
    phone_work: Optional[str] = Field(default=None, max_length=30)
    contact_role: Optional[str] = Field(default=None, max_length=40)
    is_primary: bool = False
    is_decision_maker: bool = False


class CustomerContactResponse(BaseModel):
    customer_contact_id: UUID
    first_name: str
    last_name: Optional[str]
    job_title: Optional[str]
    email: Optional[str]
    phone_mobile: Optional[str]
    phone_work: Optional[str]
    contact_role: Optional[str]
    is_primary: bool
    is_decision_maker: bool

    model_config = {"from_attributes": True}


class CustomerAddressCreate(BaseModel):
    address_type: str = Field(default="REGISTERED", max_length=20)
    address_line1: str = Field(min_length=1, max_length=250)
    address_line2: Optional[str] = Field(default=None, max_length=250)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    is_default_billing: bool = False
    is_default_shipping: bool = False


class CustomerAddressResponse(BaseModel):
    customer_address_id: UUID
    address_type: str
    address_line1: str
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    is_default_billing: bool
    is_default_shipping: bool

    model_config = {"from_attributes": True}


class CustomerCreate(BaseModel):
    legal_name: str = Field(min_length=1, max_length=250)
    trade_name: Optional[str] = Field(default=None, max_length=200)
    customer_type: str = Field(default="ACCOUNT", max_length=20)
    status: str = Field(default="PROSPECT", max_length=40)
    notes: Optional[str] = None
    source_opportunity_id: Optional[UUID] = None
    tax_type: Optional[str] = Field(default=None, max_length=20)
    tax_number: Optional[str] = Field(default=None, max_length=30)
    state_code: Optional[str] = Field(default=None, max_length=10)

    @field_validator("tax_type")
    @classmethod
    def normalize_tax_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None

    @field_validator("tax_number")
    @classmethod
    def normalize_tax_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().upper().replace(" ", "")
        return normalized or None

    @field_validator("state_code")
    @classmethod
    def normalize_state_code(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CustomerUpdate(BaseModel):
    legal_name: Optional[str] = Field(default=None, min_length=1, max_length=250)
    trade_name: Optional[str] = Field(default=None, max_length=200)
    status: Optional[str] = Field(default=None, max_length=40)
    notes: Optional[str] = None


class CustomerSuspendRequest(BaseModel):
    """REQ-CRM-028 / BR-CRM-055: suspension requires a reason code and a comment.

    Both are mandatory and must contain non-whitespace content; ``min_length=1`` alone
    would accept a blank string, so the validators strip first and then reject.
    """

    reason_code: str = Field(min_length=1, max_length=50)
    comment: str = Field(min_length=1, max_length=2000)

    @field_validator("reason_code")
    @classmethod
    def normalize_reason_code(cls, value: str) -> str:
        normalized = (value or "").strip()
        if not normalized:
            raise ValueError("reason_code must not be blank (BR-CRM-055)")
        return normalized.upper()

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, value: str) -> str:
        normalized = (value or "").strip()
        if not normalized:
            raise ValueError("comment must not be blank (BR-CRM-055)")
        return normalized


class CustomerResponse(BaseModel):
    customer_id: UUID
    tenant_id: UUID
    customer_number: str
    legal_name: str
    trade_name: Optional[str]
    customer_type: str
    status: str
    owner_id: Optional[UUID]
    source_opportunity_id: Optional[UUID]
    notes: Optional[str]
    contacts: list[CustomerContactResponse] = Field(default_factory=list)
    addresses: list[CustomerAddressResponse] = Field(default_factory=list)
    created_on: datetime
    modified_on: Optional[datetime]

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
