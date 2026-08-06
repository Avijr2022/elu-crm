from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class EditionFeatureIn(BaseModel):
    feature_code: str = Field(min_length=2, max_length=64)
    is_enabled: bool = True
    is_visible: bool = True


class EditionLimitIn(BaseModel):
    limit_code: str = Field(min_length=2, max_length=64)
    limit_name: str = Field(min_length=2, max_length=150)
    limit_value: Decimal
    limit_unit: Optional[str] = Field(default=None, max_length=32)
    is_hard_limit: bool = True
    grace_percent: Optional[Decimal] = Decimal("0")


class EditionFeatureOut(EditionFeatureIn):
    id: UUID
    feature_name: Optional[str] = None
    module_domain: Optional[str] = None

    model_config = {"from_attributes": True}


class EditionLimitOut(EditionLimitIn):
    id: UUID

    model_config = {"from_attributes": True}


class EditionCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32, description="COMMUNITY|PROFESSIONAL|ENTERPRISE")
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = 0
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    list_price_monthly: Optional[Decimal] = None
    list_price_annual: Optional[Decimal] = None
    currency_code: Optional[str] = Field(default="INR", min_length=3, max_length=3)
    features: list[EditionFeatureIn] = Field(default_factory=list)
    limits: list[EditionLimitIn] = Field(default_factory=list)

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        code = v.strip().upper()
        if not code.replace("_", "").isalnum():
            raise ValueError("Edition code must be alphanumeric/underscore")
        return code


class EditionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    list_price_monthly: Optional[Decimal] = None
    list_price_annual: Optional[Decimal] = None
    currency_code: Optional[str] = Field(default=None, min_length=3, max_length=3)
    version_no: int = Field(description="Optimistic lock (ADR-006)")
    features: Optional[list[EditionFeatureIn]] = None
    limits: Optional[list[EditionLimitIn]] = None


class EditionPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    status: Optional[str] = None
    version_no: int
    end_of_sale_date: Optional[date] = None


class EditionResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    status: str
    version_no: int
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    list_price_monthly: Optional[Decimal] = None
    list_price_annual: Optional[Decimal] = None
    currency_code: Optional[str] = None
    display_order: Optional[int] = None
    published_at: Optional[datetime] = None
    published_by: Optional[UUID] = None
    end_of_sale_date: Optional[date] = None
    features: list[EditionFeatureOut] = Field(default_factory=list)
    limits: list[EditionLimitOut] = Field(default_factory=list)
    created_on: Optional[datetime] = None
    modified_on: Optional[datetime] = None


class EditionListResponse(BaseModel):
    items: list[EditionResponse]
    page: int
    page_size: int
    total: int


class EditionVersionOut(BaseModel):
    id: UUID
    edition_id: UUID
    version_no: int
    change_summary: Optional[str] = None
    actor_id: Optional[UUID] = None
    created_on: datetime

    model_config = {"from_attributes": True}


class EditionDeprecateRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)
    version_no: int
    end_of_sale_date: Optional[date] = None


class EditionPublishRequest(BaseModel):
    version_no: int
