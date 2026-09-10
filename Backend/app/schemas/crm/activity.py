from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


ACTIVITY_STATUSES = ("PLANNED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "OVERDUE")
ENTITY_TYPES = ("LEAD", "OPPORTUNITY", "CUSTOMER")
OUTCOME_REQUIRED_TYPES = frozenset({"CALL", "MEETING", "TASK"})


class ActivityCreate(BaseModel):
    activity_type_code: str = Field(default="NOTE", max_length=40)
    outcome_code: Optional[str] = Field(default=None, max_length=40)
    subject: str = Field(min_length=1, max_length=250)
    description: Optional[str] = None
    status: str = Field(default="COMPLETED", max_length=40)
    priority: Optional[str] = Field(default=None, max_length=20)
    due_on: Optional[datetime] = None
    entity_type: str = Field(min_length=1, max_length=40)
    entity_id: UUID


class ActivityResponse(BaseModel):
    activity_id: UUID
    tenant_id: UUID
    activity_type_code: str
    outcome_code: Optional[str] = None
    subject: str
    description: Optional[str]
    status: str
    priority: Optional[str]
    owner_id: UUID
    due_on: Optional[datetime]
    completed_on: Optional[datetime]
    entity_type: str
    entity_id: UUID
    created_on: datetime
    modified_on: Optional[datetime]

    model_config = {"from_attributes": True}


class ActivityListResponse(BaseModel):
    items: list[ActivityResponse]
    total: int
    page: int
    page_size: int
