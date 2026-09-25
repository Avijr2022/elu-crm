"""Shared pytest helpers for RLS-aware DB access (PF-003A / ADR-015)."""

from contextlib import contextmanager
from collections.abc import Iterator

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.session import SessionLocal
from app.models.pf import Tenant, User

PLATFORM_TENANT_CODE = "EIIP001"


@contextmanager
def platform_session() -> Iterator[Session]:
    """Open a Session with ``app.platform_context=true`` for setup/assertions."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        yield db
    finally:
        clear_rls_context(db)
        db.close()


def platform_admin_select():
    """Select the seeded platform admin **within the platform tenant** (EIIP001).

    ``core.users`` is unique on ``(tenant_id, email)`` (``uk_users_tenant_email``),
    and tenant provisioning seeds ``settings.seed_admin_email`` into *every* newly
    registered tenant. An email-only lookup can therefore return a foreign tenant's
    row: role/password setup then lands on the wrong tenant while the fixture still
    logs in with ``tenant_code="EIIP001"`` (-> 401 -> fixture error), and the
    resulting failed logins increment that tenant's ``failed_login_count``.
    Every test must resolve the administration account through this selector.
    """
    settings = get_settings()
    return (
        select(User)
        .join(Tenant, Tenant.tenant_id == User.tenant_id)
        .where(
            Tenant.tenant_code == PLATFORM_TENANT_CODE,
            User.email == settings.seed_admin_email.lower(),
        )
    )


def reset_platform_admin_login() -> None:
    """Pin the platform admin's credentials and clear stale lockout state.

    Repeated failed logins increment ``failed_login_count`` and can leave the
    account ``LOCKED`` (BR-PF-055), after which every login fails with 403 even
    with the correct password. A fresh database is unaffected. No-op when the
    database has not been seeded yet (the app lifespan seeds on first TestClient).
    """
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
        if admin is None:
            return
        admin.password_hash = hash_password(settings.seed_admin_password)
        admin.account_status = "ACTIVE"
        admin.failed_login_count = 0
        admin.locked_until = None
        db.commit()


@pytest.fixture(scope="module", autouse=True)
def _platform_admin_login_state() -> None:
    """Normalise the platform admin's login state before each module runs."""
    reset_platform_admin_login()
