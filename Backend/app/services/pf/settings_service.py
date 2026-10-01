"""PF-011 System Configuration service layer."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional
from uuid import UUID, uuid4

import redis
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, ValidationAppError
from app.models.pf import Edition, Tenant
from app.services.pf.audit_service import write_audit_event
from app.utils.redis_rate_limiter import get_redis_client

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 300
CACHE_PREFIX = "pf011:settings"
REQ_ID = "REQ-PF-011"

# Failure modes treated as "cache unavailable": the settings path degrades to the
# database instead of propagating them (BR-PF-082).
_CACHE_ERRORS = (redis.RedisError, OSError, ValueError, TypeError)


class SettingsService:
    """Tenant and platform settings operations for PF-011."""

    def __init__(self, db: Session, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id

    # ----------------------------------------------------------------------------------
    # Redis cache (BR-PF-082): tenant-scoped, TTL 300s, fail-open
    # ----------------------------------------------------------------------------------
    # Every cache operation is best-effort: Redis being unavailable degrades to the
    # database and never fails a settings read or an already-committed write.

    def _cache_key(self) -> str:
        """Tenant-scoped cache key (``CACHE_PREFIX`` plus the tenant id)."""
        return f"{CACHE_PREFIX}:{self.tenant_id}"

    def _redis(self):
        """Return the shared Redis client, or ``None`` when one cannot be built.

        Reuses ``app.utils.redis_rate_limiter.get_redis_client`` and the existing
        ``REDIS_URL`` environment pattern. Connections are lazy, so unreachability
        surfaces on the first command and is handled by each caller.
        """
        try:
            return get_redis_client(os.getenv("REDIS_URL"))
        except _CACHE_ERRORS:
            logger.warning("PF-011 cache client unavailable", exc_info=True)
            return None

    def _cache_read(self) -> Optional[dict[str, Any]]:
        """Return the cached settings mapping, or ``None`` on a miss/unavailability."""
        client = self._redis()
        if client is None:
            return None
        try:
            payload = client.get(self._cache_key())
        except _CACHE_ERRORS:
            logger.warning(
                "PF-011 cache read failed; falling back to the database", exc_info=True
            )
            return None
        if not payload:
            return None
        try:
            cached = json.loads(payload)
        except ValueError:
            logger.warning("PF-011 cache payload is not valid JSON; ignoring it")
            return None
        return cached if isinstance(cached, dict) else None

    def _cache_write(self, settings: dict[str, Any]) -> None:
        """Cache a settings response; never raises into the read path.

        Values are stored through ``default=str`` so UUID/date members stay
        JSON-serialisable; the API DTOs are unchanged because Pydantic coerces those
        ISO strings back to UUID/date on validation.
        """
        client = self._redis()
        if client is None:
            return
        try:
            client.set(
                self._cache_key(),
                json.dumps(settings, default=str),
                ex=CACHE_TTL_SECONDS,
            )
        except _CACHE_ERRORS:
            logger.warning(
                "PF-011 cache write failed; serving from the database", exc_info=True
            )

    def _invalidate_cache(self) -> None:
        """Invalidate this tenant's cached settings after a successful commit.

        Called only after ``self.db.commit()`` and swallowed on error: an already
        committed write must never be reported as failed, and the 300s TTL bounds any
        residual staleness.
        """
        client = self._redis()
        if client is None:
            return
        try:
            client.delete(self._cache_key())
        except _CACHE_ERRORS:
            logger.warning(
                "PF-011 cache invalidation failed; TTL expiry will recover", exc_info=True
            )

    # ----------------------------------------------------------------------------------
    # Edition-minimum enforcement (BR-PF-078) via core.edition.display_order
    # ----------------------------------------------------------------------------------
    # The governed order COMMUNITY(1) < PROFESSIONAL(2) < ENTERPRISE(3) is read from
    # ``Edition.display_order`` through the existing Tenant -> Edition relationship; no
    # rank map is hard-coded. PF-011 has no feature code, so ``require_feature()`` is
    # deliberately not called.

    def _tenant_edition(self) -> tuple[Optional[str], Optional[int]]:
        """Return the tenant's edition ``(code, display_order)``."""
        row = self.db.execute(
            select(Edition.code, Edition.display_order)
            .join(Tenant, Tenant.edition_id == Edition.id)
            .where(Tenant.tenant_id == self.tenant_id)
        ).first()
        if row is None:
            return None, None
        return row[0], row[1]

    def _edition_rank(self, edition_code: Optional[str]) -> Optional[int]:
        """Rank an edition code from the existing edition catalogue."""
        if not edition_code:
            return None
        row = self.db.execute(
            select(Edition.display_order).where(Edition.code == edition_code)
        ).first()
        return row[0] if row is not None else None

    def _assert_preference_edition_allowed(
        self,
        key: str,
        stored_minimum: Optional[str],
        incoming_minimum: Optional[str],
    ) -> None:
        """Fail closed on tenant-preference writes that exceed the tenant's edition.

        * a stored ``edition_minimum`` above the tenant edition rejects the write;
        * an incoming ``edition_minimum`` must exist in the edition catalogue;
        * the resulting minimum must not exceed the tenant's edition.

        No role bypasses this: the approved specification grants Platform Admin no
        edition-enforcement exemption for PF-011 preferences.
        """
        tenant_code, tenant_rank = self._tenant_edition()
        if tenant_rank is None:
            raise ValidationAppError(
                f"Tenant edition could not be resolved for preference '{key}'",
                req_id=REQ_ID,
            )

        if stored_minimum:
            stored_rank = self._edition_rank(stored_minimum)
            if stored_rank is None:
                raise ValidationAppError(
                    f"Preference '{key}' declares unknown edition_minimum "
                    f"'{stored_minimum}'",
                    req_id=REQ_ID,
                )
            if tenant_rank < stored_rank:
                raise ForbiddenError(
                    f"Preference '{key}' requires edition '{stored_minimum}', which is "
                    f"above the tenant edition '{tenant_code}'",
                    req_id=REQ_ID,
                )

        if incoming_minimum:
            incoming_rank = self._edition_rank(incoming_minimum)
            if incoming_rank is None:
                raise ValidationAppError(
                    f"Unknown edition_minimum '{incoming_minimum}'",
                    req_id=REQ_ID,
                )
            if incoming_rank > tenant_rank:
                raise ForbiddenError(
                    f"edition_minimum '{incoming_minimum}' exceeds the tenant edition "
                    f"'{tenant_code}'",
                    req_id=REQ_ID,
                )

    def _select_settings(self) -> dict[str, Any]:
        """Uncached read of ``core.tenant_settings`` for the current tenant."""
        row = self.db.execute(
            text(
                """
                SELECT setting_id, tenant_id, financial_year_start,
                       currency_code, time_zone, date_format, time_format,
                       default_language, notification_enabled, workflow_enabled
                FROM core.tenant_settings
                WHERE tenant_id = :tenant_id
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().first()
        return dict(row) if row else {}

    def get_settings(self) -> dict[str, Any]:
        """Tenant settings, served from the tenant-scoped cache when available."""
        cached = self._cache_read()
        if cached is not None:
            return cached

        settings = self._select_settings()
        if settings:
            self._cache_write(settings)
        return settings

    def update_settings(self, values: dict[str, Any], actor_id: Optional[UUID] = None) -> dict[str, Any]:
        before = self._select_settings()
        if not before:
            raise ValueError("Tenant settings not found")

        allowed = {
            "financial_year_start",
            "currency_code",
            "time_zone",
            "date_format",
            "time_format",
            "default_language",
            "notification_enabled",
            "workflow_enabled",
        }
        changes = {k: v for k, v in values.items() if k in allowed}
        if not changes:
            return before

        assignments = ", ".join(f"{k} = :{k}" for k in changes)
        params = {"tenant_id": self.tenant_id, **changes}

        row = self.db.execute(
            text(
                f"""
                UPDATE core.tenant_settings
                SET {assignments}
                WHERE tenant_id = :tenant_id
                RETURNING setting_id, tenant_id, financial_year_start,
                          currency_code, time_zone, date_format, time_format,
                          default_language, notification_enabled, workflow_enabled
                """
            ),
            params,
        ).mappings().first()

        if row is None:
            raise ValueError("Tenant settings not found")

        after = dict(row)
        write_audit_event(
            self.db,
            event_type="SETTINGS_UPDATED", entity_type="tenant_settings", entity_id=None,
            event_category="SETTINGS",
            actor_id=actor_id,
            tenant_id=self.tenant_id,
            payload={"before": before, "after": after},
        )
        self.db.commit()
        self._invalidate_cache()
        return after

    def list_preferences(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text(
                """
                SELECT tenant_id, preference_key, preference_value,
                       preference_type, preference_group, description,
                       is_editable, edition_minimum
                FROM core.tenant_preference
                WHERE tenant_id = :tenant_id
                ORDER BY preference_key
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def list_notifications(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text(
                """
                SELECT tenant_id, event_type, module_code, email_enabled,
                       sms_enabled, whatsapp_enabled, push_enabled,
                       internal_enabled, notify_actor, notify_manager,
                       notify_admin, custom_recipients
                FROM core.tenant_notification_preference
                WHERE tenant_id = :tenant_id
                ORDER BY event_type, module_code
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def list_module_defaults(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text(
                """
                SELECT tenant_id, module_code, entity_type,
                       field_name, default_value
                FROM core.tenant_module_default
                WHERE tenant_id = :tenant_id
                ORDER BY module_code, entity_type, field_name
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def list_holidays(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text(
                """
                SELECT tenant_id, holiday_name, holiday_date,
                       is_recurring, holiday_type, calendar_year
                FROM core.tenant_holiday_calendar
                WHERE tenant_id = :tenant_id
                ORDER BY holiday_date, holiday_name
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def get_preference(self, key: str) -> dict[str, Any]:
        row = self.db.execute(
            text("""
                SELECT tenant_id, preference_key, preference_value,
                       preference_type, preference_group, description,
                       is_editable, edition_minimum
                FROM core.tenant_preference
                WHERE tenant_id = :tenant_id AND preference_key = :key
            """),
            {"tenant_id": self.tenant_id, "key": key},
        ).mappings().first()
        if row is None:
            raise ValueError("Preference not found")
        return dict(row)

    def upsert_preference(
        self,
        key: str,
        values: dict[str, Any],
        actor_id: Optional[UUID] = None,
        *,
        actor_platform_context: bool = False,
    ) -> dict[str, Any]:
        before = self.db.execute(
            text("""
                SELECT tenant_id, preference_key, preference_value,
                       preference_type, preference_group, description,
                       is_editable, edition_minimum
                FROM core.tenant_preference
                WHERE tenant_id = :tenant_id AND preference_key = :key
            """),
            {"tenant_id": self.tenant_id, "key": key},
        ).mappings().first()

        if (
            before is not None
            and not bool(before["is_editable"])
            and not actor_platform_context
        ):
            raise PermissionError("Platform Admin required for locked preference")

        self._assert_preference_edition_allowed(
            key,
            before["edition_minimum"] if before is not None else None,
            values.get("edition_minimum"),
        )

        allowed = {
            "preference_value",
            "preference_type",
            "preference_group",
            "description",
            "is_editable",
            "edition_minimum",
        }
        changes = {k: v for k, v in values.items() if k in allowed}

        if before is None:
            self.db.execute(
                text("""
                    INSERT INTO core.tenant_preference
                    (tenant_id, preference_key, preference_value,
                     preference_type, preference_group, description,
                     is_editable, edition_minimum)
                    VALUES
                    (:tenant_id, :key, :preference_value,
                     :preference_type, :preference_group, :description,
                     :is_editable, :edition_minimum)
                """),
                {
                    "tenant_id": self.tenant_id,
                    "key": key,
                    "preference_value": changes.get("preference_value"),
                    "preference_type": changes.get("preference_type"),
                    "preference_group": changes.get("preference_group"),
                    "description": changes.get("description"),
                    "is_editable": changes.get("is_editable", True),
                    "edition_minimum": changes.get("edition_minimum"),
                },
            )
        else:
            if changes:
                assignments = ", ".join(f"{k} = :{k}" for k in changes)
                self.db.execute(
                    text(f"""
                        UPDATE core.tenant_preference
                        SET {assignments}
                        WHERE tenant_id = :tenant_id
                          AND preference_key = :key
                    """),
                    {"tenant_id": self.tenant_id, "key": key, **changes},
                )

        after = self.get_preference(key)
        write_audit_event(
            self.db,
            event_type="PREFERENCE_CHANGED", entity_type="tenant_preference", entity_id=None,
            event_category="SETTINGS",
            actor_id=actor_id,
            tenant_id=self.tenant_id,
            payload={
                "before": dict(before) if before else None,
                "after": after,
            },
        )
        self.db.commit()
        self._invalidate_cache()
        return after

    def upsert_notifications(
        self,
        values: list[dict[str, Any]],
        actor_id: Optional[UUID] = None,
    ) -> list[dict[str, Any]]:
        before = self.list_notifications()

        for item in values:
            event_type = item["event_type"]
            module_code = item["module_code"]
            allowed = {
                "email_enabled", "sms_enabled", "whatsapp_enabled",
                "push_enabled", "internal_enabled", "notify_actor",
                "notify_manager", "notify_admin", "custom_recipients",
            }
            changes = {k: v for k, v in item.items() if k in allowed}
            if not changes:
                continue

            exists = self.db.execute(
                text("""
                    SELECT 1
                    FROM core.tenant_notification_preference
                    WHERE tenant_id = :tenant_id
                      AND event_type = :event_type
                      AND module_code = :module_code
                """),
                {
                    "tenant_id": self.tenant_id,
                    "event_type": event_type,
                    "module_code": module_code,
                },
            ).first()

            if exists:
                assignments = ", ".join(f"{k} = :{k}" for k in changes)
                self.db.execute(
                    text(f"""
                        UPDATE core.tenant_notification_preference
                        SET {assignments}
                        WHERE tenant_id = :tenant_id
                          AND event_type = :event_type
                          AND module_code = :module_code
                    """),
                    {
                        "tenant_id": self.tenant_id,
                        "event_type": event_type,
                        "module_code": module_code,
                        **changes,
                    },
                )
            else:
                defaults = {
                    "email_enabled": False,
                    "sms_enabled": False,
                    "whatsapp_enabled": False,
                    "push_enabled": False,
                    "internal_enabled": False,
                    "notify_actor": False,
                    "notify_manager": False,
                    "notify_admin": False,
                    "custom_recipients": None,
                }
                defaults.update(changes)
                self.db.execute(
                    text("""
                        INSERT INTO core.tenant_notification_preference
                        (tenant_id, event_type, module_code,
                         email_enabled, sms_enabled, whatsapp_enabled,
                         push_enabled, internal_enabled, notify_actor,
                         notify_manager, notify_admin, custom_recipients)
                        VALUES
                        (:tenant_id, :event_type, :module_code,
                         :email_enabled, :sms_enabled, :whatsapp_enabled,
                         :push_enabled, :internal_enabled, :notify_actor,
                         :notify_manager, :notify_admin, :custom_recipients)
                    """),
                    {
                        "tenant_id": self.tenant_id,
                        "event_type": event_type,
                        "module_code": module_code,
                        **defaults,
                    },
                )

        after = self.list_notifications()
        write_audit_event(
            self.db,
            event_type="NOTIFICATION_PREFERENCES_CHANGED", entity_type="tenant_notification_preference", entity_id=None,
            event_category="SETTINGS",
            actor_id=actor_id,
            tenant_id=self.tenant_id,
            payload={"before": before, "after": after},
        )
        self.db.commit()
        self._invalidate_cache()
        return after

    def upsert_module_defaults(
        self,
        values: list[dict[str, Any]],
        actor_id: Optional[UUID] = None,
    ) -> list[dict[str, Any]]:
        before = self.list_module_defaults()

        for item in values:
            self.db.execute(
                text("""
                    DELETE FROM core.tenant_module_default
                    WHERE tenant_id = :tenant_id
                      AND module_code = :module_code
                      AND entity_type = :entity_type
                      AND field_name = :field_name
                """),
                {
                    "tenant_id": self.tenant_id,
                    "module_code": item["module_code"],
                    "entity_type": item["entity_type"],
                    "field_name": item["field_name"],
                },
            )
            self.db.execute(
                text("""
                    INSERT INTO core.tenant_module_default
                    (tenant_id, module_code, entity_type, field_name, default_value)
                    VALUES
                    (:tenant_id, :module_code, :entity_type,
                     :field_name, :default_value)
                """),
                {"tenant_id": self.tenant_id, **item},
            )

        after = self.list_module_defaults()
        write_audit_event(
            self.db,
            event_type="MODULE_DEFAULTS_CHANGED", entity_type="tenant_module_default", entity_id=None,
            event_category="SETTINGS",
            actor_id=actor_id,
            tenant_id=self.tenant_id,
            payload={"before": before, "after": after},
        )
        self.db.commit()
        self._invalidate_cache()
        return after

    def add_holiday(
        self,
        values: dict[str, Any],
        actor_id: Optional[UUID] = None,
    ) -> dict[str, Any]:
        self.db.execute(
            text("""
                INSERT INTO core.tenant_holiday_calendar
                (tenant_id, holiday_name, holiday_date,
                 is_recurring, holiday_type, calendar_year)
                VALUES
                (:tenant_id, :holiday_name, :holiday_date,
                 :is_recurring, :holiday_type, :calendar_year)
            """),
            {
                "tenant_id": self.tenant_id,
                "holiday_name": values["holiday_name"],
                "holiday_date": values["holiday_date"],
                "is_recurring": values.get("is_recurring", False),
                "holiday_type": values.get("holiday_type"),
                "calendar_year": values.get("calendar_year"),
            },
        )
        after = dict(
            self.db.execute(
                text("""
                    SELECT tenant_id, holiday_name, holiday_date,
                           is_recurring, holiday_type, calendar_year
                    FROM core.tenant_holiday_calendar
                    WHERE tenant_id = :tenant_id
                      AND holiday_name = :holiday_name
                      AND holiday_date = :holiday_date
                    ORDER BY holiday_name
                    LIMIT 1
                """),
                {
                    "tenant_id": self.tenant_id,
                    "holiday_name": values["holiday_name"],
                    "holiday_date": values["holiday_date"],
                },
            ).mappings().first()
        )
        write_audit_event(
            self.db,
            event_type="HOLIDAY_ADDED", entity_type="tenant_holiday_calendar", entity_id=None,
            event_category="SETTINGS",
            actor_id=actor_id,
            tenant_id=self.tenant_id,
            payload={"before": None, "after": after},
        )
        self.db.commit()
        self._invalidate_cache()
        return after

    def reset_defaults(
        self,
        actor_id: Optional[UUID] = None,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        if not confirmed:
            raise ValueError("Explicit confirmation required")

        before = self._select_settings()
        row = self.db.execute(
            text("""
                UPDATE core.tenant_settings
                SET financial_year_start = DATE_TRUNC('year', CURRENT_DATE)::date,
                    currency_code = 'INR',
                    time_zone = 'Asia/Kolkata',
                    date_format = 'DD/MM/YYYY',
                    time_format = '24 Hour',
                    default_language = 'en',
                    notification_enabled = TRUE,
                    workflow_enabled = TRUE
                WHERE tenant_id = :tenant_id
                RETURNING setting_id, tenant_id, financial_year_start,
                          currency_code, time_zone, date_format, time_format,
                          default_language, notification_enabled, workflow_enabled
            """),
            {"tenant_id": self.tenant_id},
        ).mappings().first()

        if row is None:
            raise ValueError("Tenant settings not found")

        after = dict(row)
        write_audit_event(
            self.db,
            event_type="SETTINGS_RESET", entity_type="tenant_settings", entity_id=None,
            event_category="SETTINGS",
            actor_id=actor_id,
            tenant_id=self.tenant_id,
            payload={"before": before, "after": after},
        )
        self.db.commit()
        self._invalidate_cache()
        return after

    # ----------------------------------------------------------------------------------
    # Platform-global settings and the settings catalogue (PF-011 ops 17-19)
    # ----------------------------------------------------------------------------------

    def list_catalogue(self) -> list[dict[str, Any]]:
        """Read the platform-global settings registry (``core.setting_catalogue``).

        Platform-global: ``setting_catalogue`` carries no ``tenant_id`` and is not filtered
        by the tenant context; it is the registry that validates ``preference_key`` values.
        """
        rows = self.db.execute(
            text(
                """
                SELECT id, setting_key, value_type, default_value, description
                FROM core.setting_catalogue
                ORDER BY setting_key
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def get_platform_settings(self) -> list[dict[str, Any]]:
        """Read platform-global settings (``core.platform_setting``).

        Platform-global by contract: the table has no ``tenant_id`` column and is
        deliberately **not** scoped to ``self.tenant_id``.
        """
        rows = self.db.execute(
            text(
                """
                SELECT id, key, value, description
                FROM core.platform_setting
                ORDER BY key
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def update_platform_settings(
        self,
        values: list[dict[str, Any]],
        actor_id: Optional[UUID] = None,
    ) -> list[dict[str, Any]]:
        """Upsert platform-global settings by ``key`` (``core.platform_setting``).

        Platform-global: no ``tenant_id`` is written or filtered, so the audit event is
        emitted with ``tenant_id=None`` (``audit.audit_event.tenant_id`` is nullable).
        """
        before = self.get_platform_settings()
        allowed = {"value", "description"}

        for item in values:
            key = item["key"]
            changes = {k: v for k, v in item.items() if k in allowed}
            if not changes:
                continue

            exists = self.db.execute(
                text("SELECT 1 FROM core.platform_setting WHERE key = :key"),
                {"key": key},
            ).first()

            if exists:
                assignments = ", ".join(f"{k} = :{k}" for k in changes)
                self.db.execute(
                    text(
                        f"""
                        UPDATE core.platform_setting
                        SET {assignments}
                        WHERE key = :key
                        """
                    ),
                    {"key": key, **changes},
                )
            else:
                self.db.execute(
                    text(
                        """
                        INSERT INTO core.platform_setting (id, key, value, description)
                        VALUES (:id, :key, :value, :description)
                        """
                    ),
                    {
                        "id": uuid4(),
                        "key": key,
                        "value": changes.get("value"),
                        "description": changes.get("description"),
                    },
                )

        after = self.get_platform_settings()
        write_audit_event(
            self.db,
            event_type="PLATFORM_SETTINGS_UPDATED",
            event_category="SETTINGS",
            entity_type="platform_setting",
            entity_id=None,
            actor_id=actor_id,
            tenant_id=None,
            payload={"before": before, "after": after},
        )
        self.db.commit()
        return after
