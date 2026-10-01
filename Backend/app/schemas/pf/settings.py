"""PF-011 System Configuration — Pydantic DTOs.

Shapes follow the reconciled PF-011 contracts (BFS §PF-011 §9, ADR-017, ELU-DDD-PF §11,
ELU-API-PF §4.6) and the authoritative DDL in
``Database/03_PlatformFoundation/020_settings_pf011.sql``.

The released ``core.tenant_settings`` ORM column names are used verbatim and are not renamed
(ADR-017 rule 3 / ELU-DDD-PF §11.1).
"""

from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TenantSettingsResponse(BaseModel):
    """``core.tenant_settings`` read model — released column names preserved."""

    setting_id: UUID
    tenant_id: UUID
    financial_year_start: Optional[date] = None
    currency_code: Optional[str] = None
    time_zone: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    default_language: Optional[str] = None
    notification_enabled: Optional[bool] = None
    workflow_enabled: Optional[bool] = None


class TenantSettingsUpdate(BaseModel):
    """Partial update payload — only the released, editable tenant_settings columns."""

    financial_year_start: Optional[date] = None
    currency_code: Optional[str] = Field(default=None, max_length=10)
    time_zone: Optional[str] = Field(default=None, max_length=100)
    date_format: Optional[str] = Field(default=None, max_length=30)
    time_format: Optional[str] = Field(default=None, max_length=20)
    default_language: Optional[str] = Field(default=None, max_length=20)
    notification_enabled: Optional[bool] = None
    workflow_enabled: Optional[bool] = None


class SettingsResetRequest(BaseModel):
    """``POST /settings/reset`` — explicit confirmation is mandatory (BR-PF-080)."""

    confirmed: bool = False


class TenantPreferenceResponse(BaseModel):
    tenant_id: UUID
    preference_key: str
    preference_value: Optional[str] = None
    preference_type: Optional[str] = None
    preference_group: Optional[str] = None
    description: Optional[str] = None
    is_editable: bool = True
    edition_minimum: Optional[str] = None


class TenantPreferenceUpdate(BaseModel):
    preference_value: Optional[str] = None
    preference_type: Optional[str] = None
    preference_group: Optional[str] = None
    description: Optional[str] = None
    is_editable: Optional[bool] = None
    edition_minimum: Optional[str] = None


class TenantPreferenceUpsert(TenantPreferenceUpdate):
    """Bulk ``PUT /settings/preferences`` item — carries the key to upsert."""

    preference_key: str


class TenantPreferenceListResponse(BaseModel):
    items: list[TenantPreferenceResponse]
    total: int


class NotificationPreferenceResponse(BaseModel):
    tenant_id: UUID
    event_type: str
    module_code: str
    email_enabled: bool = False
    sms_enabled: bool = False
    whatsapp_enabled: bool = False
    push_enabled: bool = False
    internal_enabled: bool = False
    notify_actor: bool = False
    notify_manager: bool = False
    notify_admin: bool = False
    custom_recipients: Optional[str] = None


class NotificationPreferenceUpdate(BaseModel):
    """One row per (event_type, module_code) — channel flags are columns (BFS §9)."""

    event_type: str
    module_code: str
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    internal_enabled: Optional[bool] = None
    notify_actor: Optional[bool] = None
    notify_manager: Optional[bool] = None
    notify_admin: Optional[bool] = None
    custom_recipients: Optional[str] = None


class NotificationPreferenceListResponse(BaseModel):
    items: list[NotificationPreferenceResponse]
    total: int


class ModuleDefaultResponse(BaseModel):
    tenant_id: UUID
    module_code: str
    entity_type: str
    field_name: str
    default_value: Optional[str] = None


class ModuleDefaultUpdate(BaseModel):
    module_code: str
    entity_type: str
    field_name: str
    default_value: Optional[str] = None


class ModuleDefaultListResponse(BaseModel):
    items: list[ModuleDefaultResponse]
    total: int


class HolidayResponse(BaseModel):
    """``core.tenant_holiday_calendar`` — no surrogate id column exists.

    ``PUT``/``DELETE /settings/holidays/{id}`` have no authoritative identity to bind to;
    see the router module docstring.
    """

    tenant_id: UUID
    holiday_name: str
    holiday_date: date
    is_recurring: bool = False
    holiday_type: Optional[str] = None
    calendar_year: Optional[int] = None


class HolidayCreate(BaseModel):
    holiday_name: str = Field(max_length=255)
    holiday_date: date
    is_recurring: bool = False
    holiday_type: Optional[str] = Field(default=None, max_length=50)
    calendar_year: Optional[int] = None


class HolidayListResponse(BaseModel):
    items: list[HolidayResponse]
    total: int


class PlatformSettingResponse(BaseModel):
    """``core.platform_setting`` — platform-global: no ``tenant_id``, no RLS."""

    id: UUID
    key: str
    value: Optional[str] = None
    description: Optional[str] = None


class PlatformSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


class PlatformSettingUpsert(PlatformSettingUpdate):
    """Bulk ``PUT /platform/settings`` item — carries the platform-global key."""

    key: str


class PlatformSettingListResponse(BaseModel):
    items: list[PlatformSettingResponse]
    total: int


class SettingCatalogueResponse(BaseModel):
    """``core.setting_catalogue`` — platform-global lookup for valid preference keys."""

    id: UUID
    setting_key: str
    value_type: str
    default_value: Optional[str] = None
    description: Optional[str] = None


class SettingCatalogueListResponse(BaseModel):
    items: list[SettingCatalogueResponse]
    total: int
