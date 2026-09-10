from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


LEAD_STATUSES = (
    "NEW",
    "UNDER_QUALIFICATION",
    "NURTURE",
    "ON_HOLD",
    "QUALIFIED",
    "CONVERTED",
    "DISQUALIFIED",
)


class LeadCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    company_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    status: str = Field(default="NEW", max_length=40)
    estimated_value: Decimal = Field(default=Decimal("0"), ge=0)
    currency_code: str = Field(default="INR", min_length=3, max_length=3)
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    company_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    status: Optional[str] = Field(default=None, max_length=40)
    estimated_value: Optional[Decimal] = Field(default=None, ge=0)
    currency_code: Optional[str] = Field(default=None, min_length=3, max_length=3)
    notes: Optional[str] = None


class LeadResponse(BaseModel):
    lead_id: UUID
    tenant_id: UUID
    lead_number: str
    full_name: str
    company_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    status: str
    estimated_value: Decimal
    currency_code: str
    owner_id: Optional[UUID]
    notes: Optional[str]
    created_on: datetime
    modified_on: Optional[datetime]

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int


class LeadDisqualifyRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class LeadConvertResponse(BaseModel):
    convert_type: str
    opportunity: Optional["OpportunityResponse"] = None
    customer: Optional["CustomerResponse"] = None


from app.schemas.crm.customer import CustomerResponse  # noqa: E402
from app.schemas.crm.opportunity import OpportunityResponse  # noqa: E402

LeadConvertResponse.model_rebuild()
