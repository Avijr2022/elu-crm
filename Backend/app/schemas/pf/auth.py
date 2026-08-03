from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    tenant_code: Optional[str] = Field(
        default=None,
        description="Optional tenant code; defaults to Euphoria seed tenant when omitted",
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class RefreshRequest(BaseModel):
    refresh_token: str


class UserMeResponse(BaseModel):
    user_id: UUID
    tenant_id: UUID
    tenant_code: str
    tenant_name: str
    email: EmailStr
    display_name: str
    role_code: str
    role_name: str
    organization_name: str
    currency_code: str
    time_zone: str
    financial_year_start: datetime | str

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str


class TenantSummary(BaseModel):
    tenant_id: UUID
    tenant_code: str
    tenant_name: str
    status: str
    edition_code: str
    currency_code: str
    time_zone: str
