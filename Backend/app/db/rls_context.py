"""PostgreSQL RLS session binding (ADR-015 / ELU-DEV-001 §6A).

RLS GUCs and ``SET LOCAL ROLE elu_app`` are stored on ``Session.info`` and
re-applied on every ``after_begin`` so they survive ``commit()`` within a
request. ContextVars alone are unsafe with FastAPI sync threadpool hops.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator, Optional
from uuid import UUID

from sqlalchemy import event, text
from sqlalchemy.orm import Session

_app_role_cv: ContextVar[bool] = ContextVar("elu_use_app_role", default=True)
_listener_registered = False

APP_ROLE = "elu_app"
_INFO_TENANT = "elu_tenant_id"
_INFO_PLATFORM = "elu_platform"


def clear_rls_context(db: Session | None = None) -> None:
    _app_role_cv.set(True)
    if db is not None:
        db.info[_INFO_TENANT] = None
        db.info[_INFO_PLATFORM] = False


def set_app_role_enabled(enabled: bool) -> None:
    """When False, sessions stay as login role (superuser/owner) for DDL."""
    _app_role_cv.set(enabled)


def app_role_enabled() -> bool:
    return _app_role_cv.get()


@contextmanager
def owner_role() -> Iterator[None]:
    """Temporarily disable elu_app so DDL/owner ops run as login role."""
    previous = app_role_enabled()
    set_app_role_enabled(False)
    try:
        yield
    finally:
        set_app_role_enabled(previous)


def bind_rls_context(
    db: Session,
    *,
    tenant_id: UUID | str | None = None,
    platform: bool = False,
) -> None:
    """Bind RLS GUC values on this Session for the remainder of the request."""
    db.info[_INFO_TENANT] = str(tenant_id) if tenant_id is not None else None
    db.info[_INFO_PLATFORM] = bool(platform)
    _apply_to_connection(db, db.connection())


def _apply_to_connection(session: Session, connection) -> None:
    if _app_role_cv.get():
        connection.execute(text(f"SET LOCAL ROLE {APP_ROLE}"))
    else:
        connection.execute(text("RESET ROLE"))

    tid = session.info.get(_INFO_TENANT) or ""
    platform = "true" if session.info.get(_INFO_PLATFORM) else ""
    connection.execute(
        text("SELECT set_config('app.tenant_id', :tid, true)"),
        {"tid": tid},
    )
    connection.execute(
        text("SELECT set_config('app.platform_context', :pc, true)"),
        {"pc": platform},
    )


def register_rls_session_listener() -> None:
    """Idempotent registration of Session.after_begin RLS re-bind."""
    global _listener_registered
    if _listener_registered:
        return

    @event.listens_for(Session, "after_begin")
    def _rls_after_begin(session, transaction, connection) -> None:  # noqa: ARG001
        _apply_to_connection(session, connection)

    _listener_registered = True
