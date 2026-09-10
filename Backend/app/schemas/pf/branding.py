from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TenantBrandingResponse(BaseModel):
    tenant_id: UUID
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    favicon_url: Optional[str] = None

    model_config = {"from_attributes": True}


class TenantLogoUpload(BaseModel):
    logo_data_url: str = Field(min_length=32, max_length=2_800_000)


class TenantPrimaryColorUpdate(BaseModel):
    primary_color: str = Field(min_length=4, max_length=16)
