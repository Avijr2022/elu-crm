from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


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


class CustomerUpdate(BaseModel):
    legal_name: Optional[str] = Field(default=None, min_length=1, max_length=250)
    trade_name: Optional[str] = Field(default=None, max_length=200)
    status: Optional[str] = Field(default=None, max_length=40)
    notes: Optional[str] = None


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
