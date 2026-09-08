from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ActivityTypeCreate(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=100)


class ActivityTypeUpdate(BaseModel):
    is_active: Optional[bool] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class ActivityTypeResponse(BaseModel):
    activity_type_id: UUID
    tenant_id: UUID
    code: str
    name: str
    is_active: bool
    created_on: datetime

    model_config = {"from_attributes": True}


class ActivityTypeListResponse(BaseModel):
    items: list[ActivityTypeResponse]


class ActivityOutcomeResponse(BaseModel):
    activity_outcome_id: UUID
    activity_type_code: str
    code: str
    name: str
    is_positive: bool
    is_active: bool

    model_config = {"from_attributes": True}


class ActivityOutcomeListResponse(BaseModel):
    items: list[ActivityOutcomeResponse]


class ActivityOutcomeCreate(BaseModel):
    activity_type_code: str = Field(min_length=1, max_length=40)
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=100)
    is_positive: bool = False


class ActivityOutcomeUpdate(BaseModel):
    is_active: Optional[bool] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    is_positive: Optional[bool] = None


class OpportunityStageResponse(BaseModel):
    opportunity_stage_id: UUID
    code: str
    name: str
    sequence_no: int
    default_probability: int
    is_closed: bool
    is_active: bool

    model_config = {"from_attributes": True}


class OpportunityStageListResponse(BaseModel):
    items: list[OpportunityStageResponse]


class OpportunityStageCreate(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=100)
    default_probability: int = Field(default=0, ge=0, le=100)
    is_closed: bool = False


class OpportunityStageUpdate(BaseModel):
    is_active: Optional[bool] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    sequence_no: Optional[int] = Field(default=None, ge=0)


class OpportunityStageReorder(BaseModel):
    stage_ids: list[UUID] = Field(min_length=1)


class CrmLookupsResponse(BaseModel):
    pipeline_stages: list[str]
    opportunity_statuses: list[str]
    lead_statuses: list[str]
    activity_types: list[str]
    activity_statuses: list[str]
    activity_outcomes: list[str] = []
    activity_type_details: list[ActivityTypeResponse] = []
    activity_outcome_details: list[ActivityOutcomeResponse] = []
    pipeline_stage_details: list[OpportunityStageResponse] = []
