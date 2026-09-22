"""PF-009 Roles & Permissions (RBAC) — Batch 1 foundation service.

Batch 1 scope (foundation only):
  * custom-role edition limit enforcement — **BR-PF-061**
  * system-role immutability — **BR-PF-062**

Deferred to later authorised batches: the ``/api/v1/rbac`` API surface,
multi-role JWT/auth resolution, permission-grain rollout on released modules,
reports and notifications. Nothing in this module is wired to a router yet.

Design constraints honoured here:
  * **No universal PLATFORM_ADMIN permission bypass** is introduced. These
    guards are role-agnostic and check ``Role.is_system`` only.
  * ``core.users.role_id`` is preserved — this module never reads or writes it.
  * ``core.role_permission`` is never given a ``tenant_id`` column.

Edition-limit convention mirrors ``SubscriptionService._edition_max_users``:
the bound lives on ``edition.limits`` as ``MAX_ROLES`` and the repo-wide
"unlimited" sentinel is ``999999`` (same as ``MAX_USERS`` / ``MAX_BRANCHES``).
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.models.pf import Edition, Role

#: Edition limit code carrying the BR-PF-061 custom-role bound.
LIMIT_CUSTOM_ROLES = "MAX_ROLES"

#: Repo-wide "unlimited" sentinel (MAX_USERS / MAX_BRANCHES / MAX_STORAGE_GB).
UNLIMITED = Decimal("999999")

_REQ_LIMIT = "BR-PF-061"
_REQ_SYSTEM = "BR-PF-062"


def custom_role_limit(edition: Edition) -> int | None:
    """Return the BR-PF-061 custom-role bound for an edition.

    ``None`` means unlimited (Enterprise) or an undefined limit code — in both
    cases no custom-role bound is enforced, matching the MAX_USERS convention.
    """
    for lim in edition.limits:
        if lim.limit_code.upper() != LIMIT_CUSTOM_ROLES:
            continue
        try:
            value = Decimal(str(lim.limit_value))
        except Exception:
            return None
        if value >= UNLIMITED:
            return None
        return int(value)
    return None


def count_custom_roles(db: Session, tenant_id: UUID) -> int:
    """Count a tenant's live *custom* roles (``is_system`` false, not deleted)."""
    return int(
        db.scalar(
            select(func.count())
            .select_from(Role)
            .where(
                Role.tenant_id == tenant_id,
                Role.is_system.is_(False),
                Role.is_deleted.is_(False),
            )
        )
        or 0
    )


def assert_can_add_custom_role(
    db: Session, tenant_id: UUID, edition: Edition
) -> None:
    """Enforce BR-PF-061 before a custom role is created.

    Rejects when the tenant already holds ``MAX_ROLES`` live custom roles for
    its edition (Community=5, Professional=25, Enterprise=unlimited).
    """
    limit = custom_role_limit(edition)
    if limit is None:
        return
    used = count_custom_roles(db, tenant_id)
    if used >= limit:
        raise ValidationAppError(
            f"custom role limit reached for this edition ({used}/{limit})",
            req_id=_REQ_LIMIT,
        )


def assert_role_renamable(role: Role) -> None:
    """BR-PF-062 — a system role (``is_system`` true) cannot be renamed."""
    if role.is_system:
        raise ValidationAppError(
            f"system role '{role.role_code}' cannot be renamed",
            req_id=_REQ_SYSTEM,
        )


def assert_role_deletable(role: Role) -> None:
    """BR-PF-062 — a system role (``is_system`` true) cannot be deleted."""
    if role.is_system:
        raise ValidationAppError(
            f"system role '{role.role_code}' cannot be deleted",
            req_id=_REQ_SYSTEM,
        )


def rename_role(db: Session, role: Role, new_name: str) -> Role:
    """Rename a custom role (foundation helper; no router in Batch 1)."""
    assert_role_renamable(role)
    role.role_name = new_name
    db.flush()
    return role


def deactivate_role(db: Session, role: Role) -> Role:
    """Soft-delete a custom role (foundation helper; no router in Batch 1)."""
    assert_role_deletable(role)
    role.is_deleted = True
    role.is_active = False
    db.flush()
    return role
