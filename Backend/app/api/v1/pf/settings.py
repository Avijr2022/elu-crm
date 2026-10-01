"""PF-011 System Configuration API — tenant settings and preferences.

Contracts: ``ELU-API-PF.md`` §4.6 (19 operations), ``ELU-DDD-PF.md`` §11 (ADR-017),
BFS Platform Foundation §PF-011 §9, DDL ``Database/03_PlatformFoundation/020_settings_pf011.sql``.

Tenant isolation is inherited from the request's tenant context: every call constructs
``SettingsService(db, current.tenant_id)`` and the service scopes all SQL by ``tenant_id``
(the four tenant tables are RLS-protected by ``012_rls_pf003a.sql``).

IMPLEMENTED (17 of the 19 contracted operations)
    1  GET    /settings                              settings.read
    2  PUT    /settings                              settings.configure
    3  PATCH  /settings                              settings.configure
    4  GET    /settings/preferences                  settings.read
    5  PUT    /settings/preferences                  settings.configure
    6  GET    /settings/preferences/{key}            settings.read
    7  PUT    /settings/preferences/{key}            settings.configure
    8  GET    /settings/notifications                settings.read
    9  PUT    /settings/notifications                settings.configure
   10  GET    /settings/module-defaults              settings.read
   11  PUT    /settings/module-defaults              settings.configure
   12  GET    /settings/holidays                     settings.read
   13  POST   /settings/holidays                     settings.configure
   16  POST   /settings/reset                        settings.configure
   17  GET    /settings/catalogue                    settings.read
   18  GET    /platform/settings                     platform_settings.read
   19  PUT    /platform/settings                     platform_settings.configure

BLOCKED (2 operations) — deliberately absent, blocked by an unresolved contract/schema
identity; inventing one is prohibited:
   14/15  PUT|DELETE /settings/holidays/{id}
          ``core.tenant_holiday_calendar`` has NO surrogate id column (its natural key is
          ``tenant_id + holiday_name + holiday_date``) and ``SettingsService`` exposes only
          ``list_holidays``/``add_holiday``. Binding ``{id}`` would require inventing a
          database identifier, which the approved rule forbids, so these two routes are
          deliberately absent. Adding them requires a contract decision on the holiday
          identity plus ``update_holiday``/``delete_holiday`` service methods.

Also notable, and deliberately NOT invented here:
    * ``edition_minimum`` (``core.tenant_preference``) is carried through the DTOs but
      ``SettingsService`` does not enforce it, and no PF-011 feature constant exists in
      ``app/core/edition_gating.py``, so no ``require_feature`` call is made.
    * ``is_editable = FALSE`` means Platform Admin only (ADR-017 rule 9). The service raises
      ``PermissionError`` for a non-Platform-Admin write; this layer also pre-checks the
      caller's role so the refusal is a 403 rather than a 500.
    * Feature toggles remain in ``core.tenant_settings``; no separate toggle API is exposed.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import (
    AppError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
    http_error_from_app,
)
from app.core.rbac import require_permission
from app.db.session import get_db
from app.schemas.pf.settings import (
    HolidayCreate,
    HolidayListResponse,
    HolidayResponse,
    ModuleDefaultListResponse,
    ModuleDefaultUpdate,
    NotificationPreferenceListResponse,
    NotificationPreferenceUpdate,
    PlatformSettingListResponse,
    PlatformSettingUpsert,
    SettingCatalogueListResponse,
    SettingsResetRequest,
    TenantPreferenceListResponse,
    TenantPreferenceResponse,
    TenantPreferenceUpdate,
    TenantPreferenceUpsert,
    TenantSettingsResponse,
    TenantSettingsUpdate,
)
from app.services.pf.settings_service import SettingsService

router = APIRouter(tags=["PF Settings"])

READ = "settings.read"
CONFIGURE = "settings.configure"
PLATFORM_READ = "platform_settings.read"
PLATFORM_CONFIGURE = "platform_settings.configure"
PLATFORM_ADMIN_ROLE = "PLATFORM_ADMIN"

# Exact error texts the service raises, mapped to transport-level codes (see ``_call``).
_NOT_FOUND_MARKER = "not found"
_FORBIDDEN_MARKERS = ("platform admin required", "locked")


def _actor_id(current: CurrentUser) -> UUID | None:
    """Best-effort actor id for the service's audit payloads."""
    return getattr(current, "user_id", None) or getattr(current, "id", None)


def _call(fn: Any) -> Any:
    """Run a service call, translating its domain errors into ``AppError`` responses.

    ``SettingsService`` raises ``ValueError`` (unknown/missing row, confirmation missing) and
    ``PermissionError`` (locked preference), neither of which is an ``AppError``.
    """
    try:
        return fn()
    except AppError as exc:
        raise http_error_from_app(exc) from exc
    except PermissionError as exc:
        raise http_error_from_app(ForbiddenError(str(exc))) from exc
    except ValueError as exc:
        message = str(exc)
        if _NOT_FOUND_MARKER in message.lower():
            raise http_error_from_app(NotFoundError(message)) from exc
        raise http_error_from_app(ValidationAppError(message)) from exc


def _is_locked(preference: dict[str, Any] | None) -> bool:
    return preference is not None and not bool(preference.get("is_editable", True))


def _guard_locked_preference(db: Session, tenant_id: UUID, key: str, current: CurrentUser) -> None:
    """ADR-017 rule 9: a non-editable preference is Platform Admin only.

    Raises ``ForbiddenError`` through ``_call``'s translation when the caller is not a
    Platform Admin, and lets ``SettingsService.upsert_preference`` remain the final authority.
    """
    existing = _call(lambda: _optional_preference(db, tenant_id, key))
    if _is_locked(existing) and getattr(current, "role_code", None) != PLATFORM_ADMIN_ROLE:
        raise http_error_from_app(
            ForbiddenError(f"Preference '{key}' is not editable by this tenant")
        )


def _optional_preference(db: Session, tenant_id: UUID, key: str) -> dict[str, Any] | None:
    """Read a preference without raising when it does not exist yet."""
    try:
        return SettingsService(db, tenant_id).get_preference(key)
    except ValueError:
        return None


# --------------------------------------------------------------------------------------
# 1-3  Tenant settings
# --------------------------------------------------------------------------------------


@router.get("/settings", response_model=TenantSettingsResponse)
def get_settings(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantSettingsResponse:
    def run() -> Any:
        require_permission(current, READ)
        return SettingsService(db, current.tenant_id).get_settings()

    return _call(run)


@router.put("/settings", response_model=TenantSettingsResponse)
def replace_settings(
    payload: TenantSettingsUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantSettingsResponse:
    def run() -> Any:
        require_permission(current, CONFIGURE)
        return SettingsService(db, current.tenant_id).update_settings(
            payload.model_dump(exclude_unset=True, exclude_none=True),
            actor_id=_actor_id(current),
        )

    return _call(run)


@router.patch("/settings", response_model=TenantSettingsResponse)
def update_settings(
    payload: TenantSettingsUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantSettingsResponse:
    def run() -> Any:
        require_permission(current, CONFIGURE)
        return SettingsService(db, current.tenant_id).update_settings(
            payload.model_dump(exclude_unset=True, exclude_none=True),
            actor_id=_actor_id(current),
        )

    return _call(run)


# --------------------------------------------------------------------------------------
# 4-7  Tenant preferences
# --------------------------------------------------------------------------------------


@router.get("/settings/preferences", response_model=TenantPreferenceListResponse)
def list_preferences(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantPreferenceListResponse:
    def run() -> Any:
        require_permission(current, READ)
        items = SettingsService(db, current.tenant_id).list_preferences()
        return {"items": items, "total": len(items)}

    return _call(run)


@router.put("/settings/preferences", response_model=TenantPreferenceListResponse)
def upsert_preferences(
    payload: list[TenantPreferenceUpsert],
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantPreferenceListResponse:
    def run() -> Any:
        require_permission(current, CONFIGURE)
        service = SettingsService(db, current.tenant_id)
        for item in payload:
            values = item.model_dump(exclude_unset=True, exclude_none=True)
            key = values.pop("preference_key")
            _guard_locked_preference(db, current.tenant_id, key, current)
            service.upsert_preference(
                key,
                values,
                actor_id=_actor_id(current),
                actor_platform_context=current.platform_context,
            )
        items = service.list_preferences()
        return {"items": items, "total": len(items)}

    return _call(run)


@router.get("/settings/preferences/{key}", response_model=TenantPreferenceResponse)
def get_preference(
    key: str,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantPreferenceResponse:
    def run() -> Any:
        require_permission(current, READ)
        return SettingsService(db, current.tenant_id).get_preference(key)

    return _call(run)


@router.put("/settings/preferences/{key}", response_model=TenantPreferenceResponse)
def upsert_preference(
    key: str,
    payload: TenantPreferenceUpdate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantPreferenceResponse:
    def run() -> Any:
        require_permission(current, CONFIGURE)
        _guard_locked_preference(db, current.tenant_id, key, current)
        return SettingsService(db, current.tenant_id).upsert_preference(
            key,
            payload.model_dump(exclude_unset=True, exclude_none=True),
            actor_id=_actor_id(current),
            actor_platform_context=current.platform_context,
        )

    return _call(run)


# --------------------------------------------------------------------------------------
# 8-9  Notification preferences
# --------------------------------------------------------------------------------------


@router.get("/settings/notifications", response_model=NotificationPreferenceListResponse)
def list_notifications(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NotificationPreferenceListResponse:
    def run() -> Any:
        require_permission(current, READ)
        items = SettingsService(db, current.tenant_id).list_notifications()
        return {"items": items, "total": len(items)}

    return _call(run)


@router.put("/settings/notifications", response_model=NotificationPreferenceListResponse)
def upsert_notifications(
    payload: list[NotificationPreferenceUpdate],
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NotificationPreferenceListResponse:
    def run() -> Any:
        require_permission(current, CONFIGURE)
        items = SettingsService(db, current.tenant_id).upsert_notifications(
            [item.model_dump(exclude_unset=True, exclude_none=True) for item in payload],
            actor_id=_actor_id(current),
        )
        return {"items": items, "total": len(items)}

    return _call(run)


# --------------------------------------------------------------------------------------
# 10-11  Module defaults
# --------------------------------------------------------------------------------------


@router.get("/settings/module-defaults", response_model=ModuleDefaultListResponse)
def list_module_defaults(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ModuleDefaultListResponse:
    def run() -> Any:
        require_permission(current, READ)
        items = SettingsService(db, current.tenant_id).list_module_defaults()
        return {"items": items, "total": len(items)}

    return _call(run)


@router.put("/settings/module-defaults", response_model=ModuleDefaultListResponse)
def upsert_module_defaults(
    payload: list[ModuleDefaultUpdate],
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ModuleDefaultListResponse:
    def run() -> Any:
        require_permission(current, CONFIGURE)
        items = SettingsService(db, current.tenant_id).upsert_module_defaults(
            [item.model_dump(exclude_unset=True, exclude_none=True) for item in payload],
            actor_id=_actor_id(current),
        )
        return {"items": items, "total": len(items)}

    return _call(run)


# --------------------------------------------------------------------------------------
# 12-13  Holiday calendar (no id-based operations; see module docstring)
# --------------------------------------------------------------------------------------


@router.get("/settings/holidays", response_model=HolidayListResponse)
def list_holidays(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> HolidayListResponse:
    def run() -> Any:
        require_permission(current, READ)
        items = SettingsService(db, current.tenant_id).list_holidays()
        return {"items": items, "total": len(items)}

    return _call(run)


@router.post("/settings/holidays", response_model=HolidayResponse)
def create_holiday(
    payload: HolidayCreate,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> HolidayResponse:
    def run() -> Any:
        require_permission(current, CONFIGURE)
        return SettingsService(db, current.tenant_id).add_holiday(
            payload.model_dump(exclude_unset=True, exclude_none=True),
            actor_id=_actor_id(current),
        )

    return _call(run)


# --------------------------------------------------------------------------------------
# 16  Reset to defaults (explicit confirmation required)
# --------------------------------------------------------------------------------------


@router.post("/settings/reset", response_model=TenantSettingsResponse)
def reset_settings(
    payload: SettingsResetRequest,
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantSettingsResponse:
    def run() -> Any:
        require_permission(current, CONFIGURE)
        if not payload.confirmed:
            raise ValidationAppError("Explicit confirmation required to reset settings")
        return SettingsService(db, current.tenant_id).reset_defaults(
            actor_id=_actor_id(current),
            confirmed=True,
        )

    return _call(run)


# --------------------------------------------------------------------------------------
# 17  Available settings registry (platform-global catalogue)
# --------------------------------------------------------------------------------------


@router.get("/settings/catalogue", response_model=SettingCatalogueListResponse)
def get_settings_catalogue(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SettingCatalogueListResponse:
    def run() -> Any:
        require_permission(current, READ)
        items = SettingsService(db, current.tenant_id).list_catalogue()
        return {"items": items, "total": len(items)}

    return _call(run)


# --------------------------------------------------------------------------------------
# 18-19  Platform-global settings (no tenant scope, no RLS)
# --------------------------------------------------------------------------------------


@router.get("/platform/settings", response_model=PlatformSettingListResponse)
def list_platform_settings(
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PlatformSettingListResponse:
    def run() -> Any:
        require_permission(current, PLATFORM_READ)
        items = SettingsService(db, current.tenant_id).get_platform_settings()
        return {"items": items, "total": len(items)}

    return _call(run)


@router.put("/platform/settings", response_model=PlatformSettingListResponse)
def update_platform_settings(
    payload: list[PlatformSettingUpsert],
    current: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PlatformSettingListResponse:
    def run() -> Any:
        require_permission(current, PLATFORM_CONFIGURE)
        items = SettingsService(db, current.tenant_id).update_platform_settings(
            [item.model_dump(exclude_unset=True, exclude_none=True) for item in payload],
            actor_id=_actor_id(current),
        )
        return {"items": items, "total": len(items)}

    return _call(run)
