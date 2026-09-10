from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


PIPELINE_STAGES = (
    "QUALIFICATION",
    "TECHNICAL_EVAL",
    "BUDGET_VALIDATION",
    "PROPOSAL",
    "QUOTATION_ISSUED",
    "NEGOTIATION",
)

STAGE_PROBABILITY = {
    "QUALIFICATION": 10,
    "TECHNICAL_EVAL": 25,
    "BUDGET_VALIDATION": 40,
    "PROPOSAL": 60,
    "QUOTATION_ISSUED": 75,
    "NEGOTIATION": 90,
}

OPPORTUNITY_STATUSES = (
    "OPEN",
    "ON_HOLD",
    "CLOSED_WON",
    "CLOSED_LOST",
    "REOPENED",
)


class OpportunityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=250)
    company_name: Optional[str] = Field(default=None, max_length=200)
    stage: str = Field(default="QUALIFICATION", max_length=40)
    status: str = Field(default="OPEN", max_length=40)
    opportunity_value: Decimal = Field(default=Decimal("0"), ge=0)
    currency_code: str = Field(default="INR", min_length=3, max_length=3)
    expected_close_date: Optional[date] = None
    source_lead_id: Optional[UUID] = None
    notes: Optional[str] = None


class OpportunityUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=250)
    company_name: Optional[str] = Field(default=None, max_length=200)
    stage: Optional[str] = Field(default=None, max_length=40)
    status: Optional[str] = Field(default=None, max_length=40)
    opportunity_value: Optional[Decimal] = Field(default=None, ge=0)
    currency_code: Optional[str] = Field(default=None, min_length=3, max_length=3)
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None
    loss_reason: Optional[str] = Field(default=None, max_length=250)


class StageUpdate(BaseModel):
    stage: str = Field(min_length=1, max_length=40)


class OpportunityResponse(BaseModel):
    opportunity_id: UUID
    tenant_id: UUID
    opportunity_number: str
    name: str
    company_name: Optional[str]
    stage: str
    status: str
    opportunity_value: Decimal
    currency_code: str
    probability: int
    expected_close_date: Optional[date]
    source_lead_id: Optional[UUID]
    owner_id: Optional[UUID]
    loss_reason: Optional[str]
    notes: Optional[str]
    customer_id: Optional[UUID]
    created_on: datetime
    modified_on: Optional[datetime]
    weighted_value: Decimal = Decimal("0")

    model_config = {"from_attributes": True}


class OpportunityListResponse(BaseModel):
    items: list[OpportunityResponse]
    total: int
    page: int
    page_size: int


class PipelineStageBucket(BaseModel):
    stage: str
    count: int
    total_value: Decimal
    weighted_value: Decimal
    items: list[OpportunityResponse]


class PipelineResponse(BaseModel):
    stages: list[PipelineStageBucket]
