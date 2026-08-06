from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    tenant_id: UUID
    edition_code: str = Field(min_length=2, max_length=32)
    seat_count: int = Field(ge=1, le=100000)
    billing_cycle: str = Field(default="MONTHLY")
    plan_type: str = Field(default="Paid", max_length=30)
    start_date: date
    end_date: date
    amount: str = Field(default="0", max_length=30)
    currency_code: str = Field(default="INR", min_length=3, max_length=10)
    status: str = Field(default="ACTIVE")  # ACTIVE or TRIAL


class SubscriptionUpdate(BaseModel):
    seat_count: Optional[int] = Field(default=None, ge=1, le=100000)
    billing_cycle: Optional[str] = None
    end_date: Optional[date] = None
    amount: Optional[str] = None
    version_no: int


class SubscriptionRenewRequest(BaseModel):
    version_no: int
    end_date: date
    seat_count: Optional[int] = Field(default=None, ge=1, le=100000)
    billing_cycle: Optional[str] = None


class SubscriptionUpgradeRequest(BaseModel):
    version_no: int
    edition_code: str = Field(min_length=2, max_length=32)
    seat_count: Optional[int] = Field(default=None, ge=1, le=100000)


class SubscriptionCancelRequest(BaseModel):
    version_no: int
    reason: str = Field(min_length=3, max_length=500)


class SubscriptionVersionAction(BaseModel):
    version_no: int


class SubscriptionHistoryOut(BaseModel):
    id: UUID
    change_type: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    from_edition_id: Optional[UUID] = None
    to_edition_id: Optional[UUID] = None
    from_seat_count: Optional[int] = None
    to_seat_count: Optional[int] = None
    reason: Optional[str] = None
    changed_on: datetime


class SubscriptionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    tenant_code: Optional[str] = None
    subscription_number: str
    edition_id: UUID
    edition_code: str
    status: str
    plan_type: str
    billing_cycle: str
    seat_count: int
    seat_count_used: int = 0
    start_date: date
    end_date: Optional[date] = None
    trial_end_date: Optional[date] = None
    amount: str
    currency_code: str
    payment_status: str
    version_no: int
    cancellation_reason: Optional[str] = None


class SubscriptionListResponse(BaseModel):
    items: list[SubscriptionResponse]
    page: int
    page_size: int
    total: int


class SubscriptionUsageResponse(BaseModel):
    subscription_id: UUID
    seat_count: int
    seat_count_used: int
    seats_remaining: int
    edition_code: str
    status: str
    metrics: list[dict] = []
