"""Shared pytest helpers for RLS-aware DB access (PF-003A / ADR-015)."""

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
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


# NOTE (2026-09-25): a module-scoped autouse fixture that normalised the platform
# admin's login state was DELIBERATELY REMOVED. It opened a platform_session()
# (which issues SET LOCAL ROLE elu_app) during module setup, i.e. BEFORE the app
# lifespan has run the bootstrap DDL that creates the elu_app role on a fresh
# database. In CI that made all 264 tests error with
# `DataError: (psycopg.errors.InvalidParameterValue) role "elu_app" does not exist`
# while passing locally, where the role already exists.
# Rule: keep conftest helpers side-effect free and DB-order-neutral - never touch the
# database outside a TestClient(app) context.
